import collections

import normalization

CCallStatement = collections.namedtuple('CCallStatement', ())
CDropStatement = collections.namedtuple('CDropStatement', ())

CCloseStatement = collections.namedtuple(
    'CCloseStatement',
    (
        'name',
    ),
)

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
        self.subprogram_counters = {}
        self.subprograms = {}

def transform_call_statement(statement, accumulators):
    return CCallStatement()

def transform_drop_statement(statement, accumulators):
    return CDropStatement()

def transform_integer_literal_push_statement(statement, accumulators):
    return CPushStatement(
        type_='integer',
        value=statement.integer,
    )

def transform_lambda_push_statement(statement, accumulators):
    subprogram_counter = accumulators.subprogram_counters.get(statement.name, 0)
    accumulators.subprogram_counters[statement.name] = subprogram_counter + 1
    subprogram_name = '{}${}'.format(statement.name, subprogram_counter)
    
    accumulators.subprograms[subprogram_name] = tuple(
        transform_statement(s, accumulators) for s in statement.statement_list
    )

    return CCloseStatement(
        name=subprogram_name,
    )

def transform_symbol_value_pop_statement(statement, accumulators):
    return CPopValueStatement(
        symbol=statement.symbol,
    )

def transform_symbol_value_push_statement(statement, accumulators):
    return CPushValueStatement(
        symbol=statement.symbol,
    )

def transform_statement(statement, accumulators):
    return {
        normalization.NormalCallStatement: transform_call_statement,
        normalization.NormalDropStatement: transform_drop_statement,
        normalization.NormalIntegerLiteralPushStatement: transform_integer_literal_push_statement,
        normalization.NormalLambdaPushStatement: transform_lambda_push_statement,
        normalization.NormalSymbolValuePopStatement: transform_symbol_value_pop_statement,
        normalization.NormalSymbolValuePushStatement: transform_symbol_value_push_statement,
    }[type(statement)](statement, accumulators)

def transform(program):
    accumulators = Accumulators()

    entry_subprogram = tuple(transform_statement(s, accumulators) for s in program.statement_list)
    accumulators.subprograms['__main__'] = entry_subprogram

    return CProgram(
        subprograms=tuple(accumulators.subprograms.items()),
    )
