import collections

import desugaring
import util

NormalIntegerLiteralPushStatement = collections.namedtuple(
    'NormalIntegerLiteralPushStatement',
    (
        'integer',
    ),
)

NormalLambdaPushStatement = collections.namedtuple(
    'NormalLambdaPushStatement',
    (
        'name',
        'statement_list',
    ),
)

NormalSymbolValuePopStatement = collections.namedtuple(
    'NormalSymbolValuePopStatement',
    (
        'symbol',
    ),
)

NormalSymbolValuePushStatement = collections.namedtuple(
    'NormalSymbolValuePushStatement',
    (
        'symbol',
    ),
)

NormalCallStatement = collections.namedtuple('NormalCallStatement', ())
NormalDropStatement = collections.namedtuple('NormalDropStatement', ())

NormalProgram = collections.namedtuple(
    'NormalProgram',
    [
        'statement_list',
    ],
)

def normalize_function_call_expression(counter, expression):
    prestatements = []

    for argument in expression.argument_list:
        counter, argument_prestatements, argument_statement = normalize_expression(counter, argument)
        
        for p in argument_prestatements:
            prestatements.append(p)

        prestatements.append(argument_statement)

    counter, function_prestatements, function_statement = normalize_expression(counter, expression.function)

    for p in function_prestatements:
        prestatements.append(p)

    prestatements.append(function_statement)
    prestatements.append(NormalIntegerLiteralPushStatement(integer=len(expression.argument_list)))

    return (
        counter,
        tuple(prestatements),
        NormalCallStatement()
    )

def normalize_integer_literal_expression(counter, expression):
    return (
        counter,
        (),
        NormalIntegerLiteralPushStatement(
            integer=expression.integer,
        ),
    )

def normalize_lambda_expression(counter, expression):
    if expression.name is None:
        name = '__lambda__'
    else:
        name = expression.name

    # TODO We are currently dropping the number of arguments the function is called with
    # We should check this instead
    statement_list = [NormalDropStatement()]

    for argument_name in reversed(expression.argument_name_list):
        statement_list.append(NormalSymbolValuePopStatement(symbol=argument_name))

    for statement in expression.statement_list:
        counter, p, s = normalize_statement(counter, statement)
        
        for prestatement in p:
            statement_list.append(prestatement)

        statement_list.append(s)

    counter, p, s = normalize_expression(counter, expression.return_expression)

    for prestatement in p:
        statement_list.append(p)

    statement_list.append(s)

    return (
        counter,
        (),
        NormalLambdaPushStatement(
            name=name,
            statement_list=tuple(statement_list),
        ),
    )

def normalize_symbol_expression(counter, expression):
    return (
        counter,
        (),
        NormalSymbolValuePushStatement(
            symbol=expression.symbol,
        ),
    )

def normalize_expression(counter, expression):
    return {
        desugaring.DesugaredFunctionCallExpression: normalize_function_call_expression,
        desugaring.DesugaredIntegerLiteralExpression: normalize_integer_literal_expression,
        desugaring.DesugaredLambdaExpression: normalize_lambda_expression,
        desugaring.DesugaredSymbolExpression: normalize_symbol_expression,
    }[type(expression)](counter, expression)

def normalize_assignment_statement(counter, statement):
    counter, prestatements, normalized_expression = normalize_expression(counter, statement.expression)
    return (
        counter,
        prestatements + (normalized_expression,),
        NormalSymbolValuePopStatement(
            symbol=statement.target,
        ),
    )

def normalize_expression_statement(counter, statement):
    counter, prestatements, normalized_expression = normalize_expression(counter, statement.expression)
    return (
        counter,
        prestatements + (normalized_expression,),
        NormalDropStatement(),
    )

def normalize_statement(counter, statement):
    return {
        desugaring.DesugaredAssignmentStatement: normalize_assignment_statement,
        desugaring.DesugaredExpressionStatement: normalize_expression_statement,
    }[type(statement)](counter, statement)

@util.force_generator(tuple)
def normalize_statement_list(counter, statement_list, **kwargs):
    assign_result_to = kwargs.pop('assign_result_to', None)

    assert len(kwargs) == 0

    result_statement_list = []

    for statement in statement_list:
        counter, prestatements, normalized = normalize_statement(counter, statement)
        for s in prestatements:
            result_statement_list.append(s)
        result_statement_list.append(normalized)

    return (
        counter,
        tuple(result_statement_list),
    )

def normalize(program):
    _, statement_list = normalize_statement_list(0, program.statement_list)

    return NormalProgram(
        statement_list=statement_list,
    )
