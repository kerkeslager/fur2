
#include <assert.h>
#include <stdbool.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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
  CLOSE,
  DROP,
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

void Object_deinitialize(Object* self)
{
  switch(self->type)
  {
    case CLOSURE:
    case INTEGER:
    case NIL:
    case STRING:
      break;
  }
}

void Object_destruct(Object* self)
{
  Object_deinitialize(self);
  free(self);
}

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>

struct StackNode;
typedef struct StackNode StackNode;
struct StackNode
{
  Object item;
  StackNode* next;
};

struct Stack;
typedef struct Stack Stack;
struct Stack
{
  StackNode* top;
};

bool Stack_isEmpty(Stack*);
Object Stack_pop(Stack*);

void Stack_initialize(Stack* self)
{
  self->top = NULL;
}

Stack* Stack_construct()
{
  Stack* result = malloc(sizeof(Stack));
  Stack_initialize(result);
  return result;
}

void Stack_deinitialize(Stack* self)
{
  while(!Stack_isEmpty(self))
  {
        Stack_pop(self);
      }
}

void Stack_destruct(Stack* self)
{
  Stack_deinitialize(self);
  free(self);
}

bool Stack_isEmpty(Stack* self)
{
  return self->top == NULL;
}

void Stack_push(Stack* self, Object item)
{
  StackNode* node = malloc(sizeof(StackNode));
  node->item = item;
  node->next = self->top;
  self->top = node;
}

Object Stack_peek(Stack* self)
{
  assert(self->top != NULL);
  return self->top->item;
}

Object Stack_pop(Stack* self)
{
  Object result = Stack_peek(self);
  StackNode* next = self->top->next;

  free(self->top);

  self->top = next;
  return result;
}

#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>

struct CallStackNode;
typedef struct CallStackNode CallStackNode;
struct CallStackNode
{
  Instruction* item;
  CallStackNode* next;
};

struct CallStack;
typedef struct CallStack CallStack;
struct CallStack
{
  CallStackNode* top;
};

bool CallStack_isEmpty(CallStack*);
Instruction* CallStack_pop(CallStack*);

void CallStack_initialize(CallStack* self)
{
  self->top = NULL;
}

CallStack* CallStack_construct()
{
  CallStack* result = malloc(sizeof(CallStack));
  CallStack_initialize(result);
  return result;
}

void CallStack_deinitialize(CallStack* self)
{
  while(!CallStack_isEmpty(self))
  {
        CallStack_pop(self);
      }
}

void CallStack_destruct(CallStack* self)
{
  CallStack_deinitialize(self);
  free(self);
}

bool CallStack_isEmpty(CallStack* self)
{
  return self->top == NULL;
}

void CallStack_push(CallStack* self, Instruction* item)
{
  CallStackNode* node = malloc(sizeof(CallStackNode));
  node->item = item;
  node->next = self->top;
  self->top = node;
}

Instruction* CallStack_peek(CallStack* self)
{
  assert(self->top != NULL);
  return self->top->item;
}

Instruction* CallStack_pop(CallStack* self)
{
  Instruction* result = CallStack_peek(self);
  CallStackNode* next = self->top->next;

  free(self->top);

  self->top = next;
  return result;
}

struct EnvironmentNode;
typedef struct EnvironmentNode EnvironmentNode;
struct EnvironmentNode
{
  Object symbol;
  Object value;
  EnvironmentNode* left;
  EnvironmentNode* right;
};

EnvironmentNode* EnvironmentNode_construct(Object symbol, Object value)
{
  EnvironmentNode* result = malloc(sizeof(EnvironmentNode));
  result->symbol = symbol;
  result->value = value;
  result->left = NULL;
  result->right = NULL;
  return result;
}

void EnvironmentNode_deinitialize(EnvironmentNode*);
void EnvironmentNode_destruct(EnvironmentNode*);

void EnvironmentNode_deinitialize(EnvironmentNode* self)
{
  if(self == NULL) return;

  Object_deinitialize(&(self->symbol));
  Object_deinitialize(&(self->value));

  EnvironmentNode_destruct(self->left);
  EnvironmentNode_destruct(self->right);
}

void EnvironmentNode_destruct(EnvironmentNode* self)
{
  EnvironmentNode_deinitialize(self);
  free(self);
}

struct Environment
{
  EnvironmentNode* top;
};

void Environment_initialize(Environment* self)
{
  self->top = NULL;
}

Environment* Environment_construct()
{
  Environment* result = malloc(sizeof(Environment));
  Environment_initialize(result);
  return result;
}

void Environment_deinitialize(Environment* self)
{
  EnvironmentNode_destruct(self->top);
}

void Environment_destruct(Environment* self)
{
  Environment_deinitialize(self);
  free(self);
}

int Object_compare(Object left, Object right)
{
  switch(left.type)
  {
    case STRING:
      assert(right.type == STRING);
      return strcmp(left.instance.string, right.instance.string);

    default:
      assert(false);
  }
}

void EnvironmentNode_insert(EnvironmentNode* self, Object symbol, Object value)
{
  int comparisonResult = Object_compare(symbol, self->symbol);

  if(comparisonResult == 0)
  {
    assert(false);
  }
  else if(comparisonResult < 0)
  {
    if(self->left == NULL)
    {
      self->left = EnvironmentNode_construct(symbol, value);
    }
    else
    {
      EnvironmentNode_insert(self->left, symbol, value);
    }
  }
  else
  {
    if(self->right == NULL)
    {
      self->right = EnvironmentNode_construct(symbol, value);
    }
    else
    {
      EnvironmentNode_insert(self->right, symbol, value);
    }
  }
}

void Environment_set(Environment* self, Object symbol, Object value)
{

  EnvironmentNode* node = self->top;

  if(node == NULL)
  {
    self->top = EnvironmentNode_construct(symbol, value);
  }
  else
  {
    EnvironmentNode_insert(self->top, symbol, value);
  }
}

Object EnvironmentNode_get(EnvironmentNode* self, Object symbol)
{
  if(self == NULL) {
    printf("Undefined symbol \"%s\"\n", symbol.instance.string);
    fflush(stdout);
    assert(false);
  }

  int comparisonResult = Object_compare(symbol, self->symbol);

  if(comparisonResult == 0)
  {
    return self->value;
  }
  else if(comparisonResult < 0)
  {
    return EnvironmentNode_get(self->left, symbol);
  }
  else
  {
    return EnvironmentNode_get(self->right, symbol);
  }
}

Object Environment_get(Environment* self, Object symbol)
{
  return EnvironmentNode_get(self->top, symbol);
}

struct Process;
typedef struct Process Process;
struct Process
{
  bool halted;
  Instruction* instruction;
  Stack* stack;
  CallStack* callStack;
  Environment* environment;
};

Process* Process_construct(Instruction* start)
{
  Process* result = malloc(sizeof(Process));
  result->halted = false;
  result->instruction = start;
  result->stack = Stack_construct();
  result->callStack = CallStack_construct();
  result->environment = Environment_construct();
  return result;
}

void Process_destruct(Process* self)
{
  assert(self->halted);
  
  Stack_destruct(self->stack);
  CallStack_destruct(self->callStack);
  Environment_destruct(self->environment);

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

    case CLOSE:
      {
        Object lambda = instruction.argument;
        lambda.instance.closure.closed = process->environment;
        Stack_push(process->stack, lambda);
      }
      process->instruction++;
      break;

    case DROP:
      {
        Object o = Stack_pop(process->stack);
        Object_deinitialize(&o);
      }
      process->instruction++;
      break;

    case HALT:
      process->halted = true;
      break;

    case POP_VALUE:
      Environment_set(
        process->environment,
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
          process->environment,
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

Instruction __lambda__$1[] =
{
    (Instruction){ PUSH_VALUE, (Object){ STRING, (Instance)(char*)"answer" } },
  
    (Instruction){ RETURN, (Object){ NIL, (Instance)(int32_t)0 } }
  };
Instruction __lambda__$0[] =
{
    (Instruction){ PUSH, (Object){ INTEGER, (Instance)(int32_t)42 } },
    (Instruction){ POP_VALUE, (Object){ STRING, (Instance)(char*)"answer" } },
    (Instruction){ CLOSE, (Object){ CLOSURE, (Instance)(Closure){ NULL, __lambda__$1 } } },
  
    (Instruction){ RETURN, (Object){ NIL, (Instance)(int32_t)0 } }
  };
Instruction __main__[] =
{
    (Instruction){ CLOSE, (Object){ CLOSURE, (Instance)(Closure){ NULL, __lambda__$0 } } },
    (Instruction){ POP_VALUE, (Object){ STRING, (Instance)(char*)"get_get_answer" } },
    (Instruction){ PUSH_VALUE, (Object){ STRING, (Instance)(char*)"get_get_answer" } },
    (Instruction){ PUSH, (Object){ INTEGER, (Instance)(int32_t)0 } },
    (Instruction){ CALL, (Object){ NIL, (Instance)(int32_t)0 } },
    (Instruction){ POP_VALUE, (Object){ STRING, (Instance)(char*)"get_answer" } },
    (Instruction){ PUSH_VALUE, (Object){ STRING, (Instance)(char*)"get_answer" } },
    (Instruction){ PUSH, (Object){ INTEGER, (Instance)(int32_t)0 } },
    (Instruction){ CALL, (Object){ NIL, (Instance)(int32_t)0 } },
    (Instruction){ PUSH_VALUE, (Object){ STRING, (Instance)(char*)"print" } },
    (Instruction){ PUSH, (Object){ INTEGER, (Instance)(int32_t)1 } },
    (Instruction){ CALL, (Object){ NIL, (Instance)(int32_t)0 } },
    (Instruction){ DROP, (Object){ NIL, (Instance)(int32_t)0 } },
  
    (Instruction){ HALT, (Object){ NIL, (Instance)(int32_t)0 } }
  };

Instruction __print__[] = 
{
  (Instruction){ PRINT, (Object) { NIL, (Instance)(int32_t)0 } },
  (Instruction){ PUSH, (Object) { NIL, (Instance)(int32_t)0 } },
  (Instruction){ RETURN, (Object){ NIL, (Instance)(int32_t)0 } }
};

int main(int argc, char** argv)
{
  Process* process = Process_construct(__main__);
  Environment_set(
    process->environment,
    (Object){ STRING, (Instance)"print" },
    (Object){ CLOSURE, (Instance)(Closure) { NULL, __print__} }
  );

  execute(process);

  Process_destruct(process);
  return EXIT_SUCCESS;
}
