{% macro stack(name, item_type, item_destruct=None) -%}
#include <assert.h>
#include <stdbool.h>
#include <stdlib.h>

struct {{ name }}Node;
typedef struct {{ name }}Node {{ name }}Node;
struct {{ name }}Node
{
  {{ item_type }} item;
  {{ name }}Node* next;
};

struct {{ name }};
typedef struct {{ name }} {{ name }};
struct {{ name }}
{
  {{ name }}Node* top;
};

bool {{ name }}_isEmpty({{ name }}*);
{{ item_type }} {{ name }}_pop({{ name }}*);

void {{ name }}_initialize({{name}}* self)
{
  self->top = NULL;
}

{{ name }}* {{ name }}_construct()
{
  {{ name }}* result = malloc(sizeof({{ name }}));
  {{ name }}_initialize(result);
  return result;
}

void {{ name }}_deinitialize({{ name }}* self)
{
  while(!{{ name }}_isEmpty(self))
  {
    {% if item_destruct %}
    {{ item_destruct }}({{ name }}_pop(self));
    {% else %}
    {{ name }}_pop(self);
    {% endif %}
  }
}

void {{ name }}_destruct({{ name }}* self)
{
  {{ name }}_deinitialize(self);
  free(self);
}

bool {{ name }}_isEmpty({{ name }}* self)
{
  return self->top == NULL;
}

void {{ name }}_push({{ name }}* self, {{ item_type }} item)
{
  {{ name }}Node* node = malloc(sizeof({{ name }}Node));
  node->item = item;
  node->next = self->top;
  self->top = node;
}

{{ item_type }} {{ name }}_peek({{ name }}* self)
{
  assert(self->top != NULL);
  return self->top->item;
}

{{ item_type }} {{ name }}_pop({{ name }}* self)
{
  {{ item_type }} result = {{ name }}_peek(self);
  {{ name }}Node* next = self->top->next;

  free(self->top);

  self->top = next;
  return result;
}
{%- endmacro %}
