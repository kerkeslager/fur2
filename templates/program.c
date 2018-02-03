#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

struct Environment;
typedef struct Environment Environment;
void Environment_destruct(Environment*);

struct Object;
typedef struct Object Object;

struct Instruction;
typedef struct Instruction Instruction;

enum Type;
typedef enum Type Type;
enum Type
{
  CLOSURE,
  INTEGER,
  NIL,
  STRING
};

enum Operation;
typedef enum Operation Operation;
enum Operation
{
  CALL,
  HALT,
  POP_VALUE,
  PRINT,
  PUSH,
  PUSH_VALUE,
  RETURN
};

struct Closure;
typedef struct Closure Closure;
struct Closure
{
  Environment* closed;
  Instruction* entry;
};

union Instance;
typedef union Instance Instance;
union Instance
{
  Closure closure;
  int32_t integer;
  char* string;
};

struct Object
{
  Type type;
  Instance instance;
};

struct Instruction
{
  Operation operation;
  Object argument;
};

void Object_destruct(Object* self)
{
  switch(self->type)
  {
    case INTEGER:
    case NIL:
    case STRING:
      break;

    case CLOSURE:
      Environment_destruct(self->instance.closure.closed);
      break;
  }
}

struct Stack;
typedef struct Stack Stack;
struct Stack
{
  Object items[256];
  int16_t top;
};

void Stack_initialize(Stack* self)
{
  self->top = 0;
}

Stack* Stack_construct()
{
  Stack* result = malloc(sizeof(Stack));
  Stack_initialize(result);
  return result;
}

void Stack_destruct(Stack* self)
{
  for(int16_t i = 0; i < self->top; i++)
  {
    Object_destruct(&(self->items[i]));
  }

  free(self);
}

void Stack_push(Stack* self, Object object)
{
  assert(self->top < 256);
  self->items[self->top] = object;
  self->top++;
}

Object Stack_pop(Stack* self)
{
  assert(self->top > 0);
  self->top--;
  return self->items[self->top];
}

struct CallStack;
typedef struct CallStack CallStack;
struct CallStack
{
  Instruction* instructionPointers[256];
  int16_t top;
};

CallStack* CallStack_construct()
{
  CallStack* result = malloc(sizeof(CallStack));
  result->top = 0;
  return result;
}

void CallStack_destruct(CallStack* self)
{
  free(self);
}

void CallStack_push(CallStack* self, Instruction* instruction)
{
  assert(self->top < 256);
  self->instructionPointers[self->top] = instruction;
  self->top++;
}

Instruction* CallStack_pop(CallStack* self)
{
  assert(self->top != 256);
  self->top--;
  return self->instructionPointers[self->top];
}

struct Environment
{
  Object symbols[256];
  Object values[256];
  int16_t top;
};

Environment* Environment_construct()
{
  Environment* result = malloc(sizeof(Environment));
  result->top = 0;
  return result;
}

void Environment_destruct(Environment* self)
{
  if(self == NULL) return;

  for(int16_t i = 0; i < self->top; i++)
  {
    Object_destruct(&(self->symbols[i]));
    Object_destruct(&(self->values[i]));
  }

  free(self);
}

void Environment_set(Environment* self, Object symbol, Object value)
{
  assert(self->top < 256);

  self->symbols[self->top] = symbol;
  self->values[self->top] = value;
  self->top++;
}

Object Environment_get(Environment* self, Object symbol)
{
  for(int16_t i = 0; i < self->top; i++)
  {
    if(self->symbols[i].instance.string == symbol.instance.string)
    {
      return self->values[i];
    }
  }

  printf("Undefined symbol \"%s\"\n", symbol.instance.string);
  fflush(stdout);
  assert(false);
}

struct EnvironmentStack;
typedef struct EnvironmentStack EnvironmentStack;
struct EnvironmentStack
{
  Environment* environments[256];
  int16_t top;
};

EnvironmentStack* EnvironmentStack_construct()
{
  EnvironmentStack* result = malloc(sizeof(EnvironmentStack));
  result->top = 0;
  return result;
}

void EnvironmentStack_push(EnvironmentStack* self, Environment* environment)
{
  assert(self->top < 256);
  self->environments[self->top] = environment;
  self->top++;
}

void EnvironmentStack_destruct(EnvironmentStack* self)
{
  for(int16_t i = 0; i < self->top; i++)
  {
    Environment_destruct(self->environments[i]);
  }

  free(self);
}

Environment* EnvironmentStack_peek(EnvironmentStack* self)
{
  return self->environments[self->top - 1];
}

struct Process;
typedef struct Process Process;
struct Process
{
  bool halted;
  Instruction* instruction;
  Stack* stack;
  CallStack* callStack;
  EnvironmentStack* environmentStack;
};

Process* Process_construct(Instruction* start)
{
  Process* result = malloc(sizeof(Process));
  result->halted = false;
  result->instruction = start;
  result->stack = Stack_construct();
  result->callStack = CallStack_construct();
  result->environmentStack = EnvironmentStack_construct();
  return result;
}

void Process_destruct(Process* self)
{
  assert(self->halted);
  
  Stack_destruct(self->stack);
  CallStack_destruct(self->callStack);
  EnvironmentStack_destruct(self->environmentStack);

  free(self);
}

void executeInstruction(Process* process)
{
  Instruction instruction = *(process->instruction);

  switch(instruction.operation) {
    case CALL:
      {
        CallStack_push(process->callStack, process->instruction);
        Object argumentCount = Stack_pop(process->stack);
        Object function = Stack_pop(process->stack);
        assert(function.type == CLOSURE);
        Stack_push(process->stack, argumentCount);
        process->instruction = function.instance.closure.entry;
      }
      break;

    case HALT:
      process->halted = true;
      break;

    case POP_VALUE:
      Environment_set(
        EnvironmentStack_peek(process->environmentStack),
        instruction.argument,
        Stack_pop(process->stack)
      );
      process->instruction++;
      break;

    case PRINT:
      {
        Object argumentCount = Stack_pop(process->stack);
        assert(argumentCount.type == INTEGER);

        Stack reversed;
        Stack_initialize(&reversed);
        
        for(int32_t i = 0; i < argumentCount.instance.integer; i++)
        {
          Stack_push(&reversed, Stack_pop(process->stack));
        }

        for(int32_t i = 0; i < argumentCount.instance.integer; i++)
        {
          Object o = Stack_pop(&reversed);
          switch(o.type)
          {
            case INTEGER:
              printf("%i", o.instance.integer);
              fflush(stdout);
              break;

            default:
              assert(false);
          }
        }
      }
      process->instruction++;
      break;

    case PUSH:
      Stack_push(process->stack, instruction.argument);
      process->instruction++;
      break;

    case PUSH_VALUE:
      {
        Object o = Environment_get(
          EnvironmentStack_peek(process->environmentStack),
          instruction.argument
        );
        Stack_push(process->stack, o);
      }
      process->instruction++;
      break;

    case RETURN:
      process->instruction = CallStack_pop(process->callStack);
      process->instruction++;
      break;
  }
}

void execute(Process* process)
{
  while(!(process->halted))
  {
    executeInstruction(process);
  }
}

{% for name, body in subprograms %}
Instruction {{name}}[] =
{
  {% for instruction in body %}
  {{ instruction }},
  {% endfor %}

  {% if name == '__main__' %}
  (Instruction){ HALT, (Object){ NIL, (Instance)(int32_t)0 } }
  {% else %}
  (Instruction){ RETURN, (Object){ NIL, (Instance)(int32_t)0 } }
  {% endif %}
};
{% endfor %}

Instruction __print__[] = 
{
  (Instruction){ PRINT, (Object) { NIL, (Instance)(int32_t)0 } },
  (Instruction){ RETURN, (Object){ NIL, (Instance)(int32_t)0 } }
};

int main(int argc, char** argv)
{
  Environment* builtins = Environment_construct();
  Environment_set(
    builtins,
    (Object){ STRING, (Instance)"print" },
    (Object){ CLOSURE, (Instance)(Closure) { NULL, __print__} }
  );
  Process* process = Process_construct(__main__);
  EnvironmentStack_push(process->environmentStack, builtins);

  execute(process);

  Process_destruct(process);
  return EXIT_SUCCESS;
}

