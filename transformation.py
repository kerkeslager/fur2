import collections

import normalization

CCallStatement = collections.namedtuple('CCallStatement', ())

CPushStatement = collections.namedtuple(
    'CPushStatement',
    (
        'type_',
        'value',
    ),
)

CPopValueStatement = collections.namedtuple(
    'CPopValueStatement',
    (
        'symbol',
    ),
)

CPushValueStatement = collections.namedtuple(
    'CPushValueStatement',
    (
        'symbol',
    ),
)

CLambda = collections.namedtuple(
    'CLambda',
    (
        'instruction_list',
    )
)

CProgram = collections.namedtuple(
    'CProgram',
    (
        'subprograms',
    ),
)

class Accumulators(object):
    def __init__(self):
        self.subprograms = {}

def transform_call_statement(statement):
    return CCallStatement()

def transform_integer_literal_push_statement(statement):
    return CPushStatement(
        type_='integer',
        value=statement.integer,
    )

def transform_symbol_value_pop_statement(statement):
    return CPopValueStatement(
        symbol=statement.symbol,
    )

def transform_symbol_value_push_statement(statement):
    return CPushValueStatement(
        symbol=statement.symbol,
    )

def transform_statement(statement, accumulators):
    return {
        normalization.NormalCallStatement: transform_call_statement,
        normalization.NormalIntegerLiteralPushStatement: transform_integer_literal_push_statement,
        normalization.NormalSymbolValuePopStatement: transform_symbol_value_pop_statement,
        normalization.NormalSymbolValuePushStatement: transform_symbol_value_push_statement,
    }[type(statement)](statement)

def transform(program):
    accumulators = Accumulators()

    entry_subprogram = tuple(transform_statement(s, accumulators) for s in program.statement_list)
    accumulators.subprograms['__main__'] = entry_subprogram

    return CProgram(
        subprograms=tuple(accumulators.subprograms.items()),
    )
