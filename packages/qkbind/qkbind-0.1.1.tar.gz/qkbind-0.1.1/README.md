# qkbind

Lightweight Python bindings for C

## Installation

```bash
pip install qkbind
```

Or include directly in your project:

```c
#include <qkbind/qkbind.h>
```

## Example

```c
#include <qkbind/qkbind.h>

// Your C struct
typedef struct {
    float* data;
    int size;
} Vector;

Vector* vector_create(int size) { /* ... */ }
void vector_free(Vector* v) { /* ... */ }
Vector* vector_add(Vector* a, Vector* b) { /* ... */ }

// Python bindings (just a few lines!)
QKBIND_WRAP(Vector, Vector)
QKBIND_INIT(Vector, Vector, vector_create(size),
    int size;
    if (!PyArg_ParseTuple(args, "i", &size)) return -1;
)
QKBIND_DEALLOC(Vector, vector_free)
QKBIND_BINOP(Vector, add, vector_add)
QKBIND_PROPERTY_INT(Vector, size, size)

// Type definition
static PyNumberMethods PyVector_as_number = {
    .nb_add = (binaryfunc)PyVector_add,
};

QKBIND_TYPE_BEGIN(Vector, vector_c)
    .tp_as_number = &PyVector_as_number,
QKBIND_TYPE_END

// Module
QKBIND_MODULE_BEGIN(vector_c)
    QKBIND_MODULE_ADD_TYPE(Vector)
QKBIND_MODULE_END
```

Use in Python:

```python
import vector_c

v1 = vector_c.Vector(100)
v2 = vector_c.Vector(100)
v3 = v1 + v2  # Calls C code!
print(v3.size)
```

## License

MIT
