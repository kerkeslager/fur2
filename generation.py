import jinja2

import transformation

ENV = jinja2.Environment(
    autoescape=jinja2.select_autoescape([]),
    loader=jinja2.FileSystemLoader('templates'),
    trim_blocks=True,
)

def generate_call_statement(statement):
    return '(Instruction){ CALL, (Object){ NIL, (Instance)(int32_t)0 } }'

def generate_push_statement(statement):
    TYPES = {
        'integer': 'int32_t',
    }

    result = '(Instruction){{ PUSH, (Object){{ {}, (Instance)({}){} }} }}'.format(
        statement.type_.upper(),
        TYPES[statement.type_],
        statement.value,
    )

    return result

def generate_push_value_statement(statement):
    return '(Instruction){{ PUSH_VALUE, (Object){{ STRING, (Instance)(char*)"{}" }} }}'.format(
        statement.symbol,
    )

def generate_instruction(instruction):
    return {
        transformation.CCallStatement: generate_call_statement,
        transformation.CPushStatement: generate_push_statement,
        transformation.CPushValueStatement: generate_push_value_statement,
    }[type(instruction)](instruction)

def generate_subprogram(subprogram):
    return tuple(generate_instruction(i) for i in subprogram)

def generate(program):
    subprograms = tuple((name, generate_subprogram(body)) for name,body in program.subprograms)
    template = ENV.get_template('program.c')
    return template.render(subprograms=subprograms)
