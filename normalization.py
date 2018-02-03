import collections

import desugaring
import util

NormalIntegerLiteralPushStatement = collections.namedtuple(
    'NormalIntegerLiteralPushStatement',
    (
        'integer',
    ),
)

NormalSymbolValuePushStatement = collections.namedtuple(
    'NormalSymbolValuePushStatement',
    (
        'symbol',
    ),
)

NormalCallStatement = collections.namedtuple('NormalCallStatement', ())

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
        prestatements,
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
        desugaring.DesugaredSymbolExpression: normalize_symbol_expression,
    }[type(expression)](counter, expression)

def normalize_expression_statement(counter, statement):
    return normalize_expression(counter, statement.expression)

def normalize_statement(counter, statement):
    return {
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
