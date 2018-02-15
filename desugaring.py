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

_DesugaredLambdaExpression = collections.namedtuple(
    'DesugaredLambdaExpression',
    (
        'name',
        'argument_name_list',
        'statement_list',
        'return_expression',
    ),
)

class DesugaredLambdaExpression(_DesugaredLambdaExpression):
    def __new__(cls, *args, **kwargs):
        if 'name' not in kwargs:
            kwargs['name'] = None

        return super(DesugaredLambdaExpression, cls).__new__(cls, *args, **kwargs)

DesugaredSymbolExpression = parsing.FurSymbolExpression

DesugaredAssignmentStatement = collections.namedtuple(
    'DesugaredAssignmentStatement',
    (
        'target',
        'expression',
    ),
)

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

def desugar_lambda_expression(expression):
    return DesugaredLambdaExpression(
        argument_name_list=expression.argument_name_list,
        statement_list=tuple(desugar_statement(s) for s in expression.statement_list),
        return_expression=desugar_expression(expression.return_expression),
    )

def desugar_symbol_expression(expression):
    return expression

def desugar_expression(expression):
    return {
        parsing.FurFunctionCallExpression: desugar_function_call_expression,
        parsing.FurIntegerLiteralExpression: desugar_integer_literal_expression,
        parsing.FurLambdaExpression: desugar_lambda_expression,
        parsing.FurSymbolExpression: desugar_symbol_expression,
    }[type(expression)](expression)

def desugar_assignment_statement(statement):
    return DesugaredAssignmentStatement(
        target=statement.target,
        expression=desugar_expression(statement.expression),
    )

def desugar_expression_statement(statement):
    return DesugaredExpressionStatement(expression=desugar_expression(statement.expression))

def desugar_statement(statement):
    return {
        parsing.FurAssignmentStatement: desugar_assignment_statement,
        parsing.FurExpressionStatement: desugar_expression_statement,
    }[type(statement)](statement)

def desugar(program):
    return DesugaredProgram(
        statement_list=tuple(desugar_statement(s) for s in program.statement_list),
    )
