import collections

import parsing

DesugaredFunctionCallExpression = collections.namedtuple(
    'DesugaredFunctionCallExpression',
    (
        'metadata',
        'function',
        'argument_list',
    ),
)

DesugaredIntegerLiteralExpression = parsing.FurIntegerLiteralExpression
DesugaredSymbolExpression = parsing.FurSymbolExpression

DesugaredExpressionStatement = collections.namedtuple(
    'DesugaredExpressionStatement',
    (
        'expression',
    ),
)

DesugaredProgram = collections.namedtuple(
    'DesugaredProgram',
    (
        'statement_list',
    ),
)

def desugar_function_call_expression(expression):
    return DesugaredFunctionCallExpression(
        metadata=expression.metadata,
        function=desugar_expression(expression.function),
        argument_list=tuple(desugar_expression(e) for e in expression.argument_list),
    )

def desugar_integer_literal_expression(expression):
    return expression

def desugar_symbol_expression(expression):
    return expression

def desugar_expression(expression):
    return {
        parsing.FurFunctionCallExpression: desugar_function_call_expression,
        parsing.FurIntegerLiteralExpression: desugar_integer_literal_expression,
        parsing.FurSymbolExpression: desugar_symbol_expression,
    }[type(expression)](expression)

def desugar_expression_statement(statement):
    return DesugaredExpressionStatement(expression=desugar_expression(statement.expression))

def desugar_statement(statement):
    return {
        parsing.FurExpressionStatement: desugar_expression_statement,
    }[type(statement)](statement)

def desugar(program):
    return DesugaredProgram(
        statement_list=tuple(desugar_statement(s) for s in program.statement_list),
    )
