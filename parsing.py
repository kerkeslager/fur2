import collections

FurFunctionCallExpression = collections.namedtuple(
    'FurFunctionCallExpression',
    [
        'metadata',
        'function',
        'argument_list',
    ],
)

FurSymbolExpression = collections.namedtuple(
    'FurSymbolExpression',
    [
        'metadata',
        'symbol',
    ],
)

FurIntegerLiteralExpression = collections.namedtuple(
    'FurIntegerLiteralExpression',
    [
        'integer',
    ],
)

FurAssignmentStatement = collections.namedtuple(
    'FurAssignmentStatement',
    [
        'target',
        'expression',
    ],
)

FurExpressionStatement = collections.namedtuple(
    'FurExpressionStatement',
    [
        'expression',
    ],
)

FurProgram = collections.namedtuple(
    'FurProgram',
    (
        'statement_list',
    ),
)

def consume_newlines(index, tokens):
    while index < len(tokens) and tokens[index].type == 'newline':
        index += 1

    return True, index, None

def wrapped_parser(open_token, close_token, internal_parser):
    def result_parser(index, tokens):
        failure = (False, index, None)

        if tokens[index].type == open_token:
            index += 1
        else:
            return failure

        success, index, internal = internal_parser(index, tokens)
        if not success:
            return failure

        if tokens[index].type == close_token:
            index += 1
        else:
            # TODO Put the actual expected character in the error message
            raise Exception('Expected closing token on line {}, found "{}"'.format(
                tokens[index].line,
                tokens[index].match,
            ))

        return True, index, internal

    return result_parser

def parenthese_wrapped_parser(internal_parser):
    return wrapped_parser('open_parenthese', 'close_parenthese', internal_parser)

def or_parser(*parsers):
    def result_parser(index, tokens):
        failure = (False, index, None)

        for parser in parsers:
            success, index, value = parser(index, tokens)

            if success:
                return (success, index, value)

        return failure

    return result_parser

def zero_or_more_parser(formatter, parser):
    def result_parser(index, tokens):
        values = []

        while index < len(tokens):
            success, index, value = parser(index, tokens)

            if success:
                values.append(value)
            else:
                break

        return (True, index, formatter(tuple(values)))

    return result_parser

def comma_separated_expression_list_parser(index, tokens):
    return comma_separated_list_parser(expression_parser)(index, tokens)

def comma_separated_list_parser(subparser):
    def result_parser(index, tokens):
        start_index = index

        items = []

        _, index, _ = consume_newlines(index, tokens)

        success, index, item = subparser(index, tokens)

        if success:
            items.append(item)
        else:
            return (True, start_index, ())

        while success and index < len(tokens) and tokens[index].type == 'comma':
            index += 1
            success = False

            _, index, _ = consume_newlines(index, tokens)

            if index < len(tokens):
                success, try_index, item = subparser(index, tokens)

            if success:
                items.append(item)
                index = try_index

        return True, index, tuple(items)

    return result_parser

def function_call_expression_parser(index, tokens):
    failure = (False, index, None)

    # We have to be careful what expressions we add here. Otherwise expressions
    # like "a + b()" become ambiguous to the parser.
    success, index, function = or_parser(
        symbol_expression_parser,
    )(index, tokens)

    if not success:
        return failure

    metadata = tokens[index].metadata

    success, index, argument_list = parenthese_wrapped_parser(comma_separated_expression_list_parser)(
        index,
        tokens,
    )

    if not success:
        return failure

    while success and index < len(tokens):
        # "function" is actually the full function call if the next parse attempt doesn't succeed
        # We can't give this a better name without a bunch of checks, however.
        function = FurFunctionCallExpression(
            metadata=metadata,
            function=function,
            argument_list=argument_list,
        )

        metadata = tokens[index].metadata

        success, index, arguments = parenthese_wrapped_parser(comma_separated_expression_list_parser)(
            index,
            tokens,
        )

    return True, index, function

def integer_literal_expression_parser(index, tokens):
    failure = (False, index, None)

    if tokens[index].type != 'integer_literal':
        return failure
    value = int(tokens[index].match)
    index += 1

    return True, index, FurIntegerLiteralExpression(integer=value)

def symbol_expression_parser(index, tokens):
    if tokens[index].type == 'symbol':
        return (
            True,
            index + 1,
            FurSymbolExpression(
                metadata=tokens[index].metadata,
                symbol=tokens[index].match,
            ),
        )

    return (False, index, None)

expression_parser = or_parser(
    function_call_expression_parser,
    symbol_expression_parser,
    integer_literal_expression_parser,
)

BUILTINS = {'print', 'pow'}

def assignment_statement_parser(index, tokens):
    failure = (False, index, None)

    if tokens[index].type == 'symbol':
        target = tokens[index].match
        target_assignment_line = tokens[index].metadata.line

        index += 1
    else:
        return failure


    if tokens[index].type == 'assignment_operator':
        if target in BUILTINS:
            raise Exception(
                'Trying to assign to builtin "{}" on line {}'.format(target, target_assignment_line),
            )
        assignment_operator_index = index
    else:
        return failure

    success, index, expression = expression_parser(index + 1, tokens)

    if not success:
        raise Exception(
            'Expected expression after assignment operator on line {}'.format(
                tokens[assignment_operator_index].line
            )
        )

    return (True, index, FurAssignmentStatement(target=target, expression=expression))

def expression_statement_parser(index, tokens):
    failure = (False, index, None)

    success, index, expression = expression_parser(index, tokens)

    if not success:
        return failure

    return (True, index, FurExpressionStatement(expression=expression))

def program_formatter(statement_list):
    return FurProgram(statement_list=statement_list)

def statement_parser(index, tokens):
    _, index, _ = consume_newlines(index, tokens)

    if index == len(tokens):
        return (False, index, None)

    return or_parser(
        assignment_statement_parser,
        expression_statement_parser,
    )(index, tokens)

program_parser = zero_or_more_parser(program_formatter, statement_parser)

def execute_parser(parser, tokens):
    success, index, result = parser(0, tokens)

    if index < len(tokens):
        raise Exception('Unable to parse token {}'.format(tokens[index]))

    if success:
        return result

    raise Exception('Unable to parse')

def parse(tokens):
    return execute_parser(program_parser, tokens)
