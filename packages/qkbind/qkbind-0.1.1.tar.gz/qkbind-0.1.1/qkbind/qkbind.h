// qkbind.h - Lightweight Python binding macros for C
// A pybind11-inspired binding system for pure C
#ifndef QKBIND_H
#define QKBIND_H

#include <Python.h>

// ============================================================================
// Core Macros
// ============================================================================

// Wrapper struct generator - wraps C struct in Python object
#define QKBIND_WRAP(CType, PyName) \
    typedef struct { \
        PyObject_HEAD \
        CType* obj; \
    } Py##PyName##Object;

// Init function generator - handles __init__
#define QKBIND_INIT(PyName, CType, create_func, ...) \
    static int Py##PyName##_init(Py##PyName##Object* self, PyObject* args) { \
        __VA_ARGS__ \
        self->obj = create_func; \
        return 0; \
    }

// Dealloc generator - handles __del__
#define QKBIND_DEALLOC(PyName, free_func) \
    static void Py##PyName##_dealloc(Py##PyName##Object* self) { \
        if (self->obj) free_func(self->obj); \
        Py_TYPE(self)->tp_free((PyObject*)self); \
    }

// ============================================================================
// Operator Macros
// ============================================================================

// Binary operator generator (for +, *, -, /, etc.)
#define QKBIND_BINOP(PyName, op_name, c_func) \
    static PyObject* Py##PyName##_##op_name(Py##PyName##Object* self, PyObject* other) { \
        if (!PyObject_TypeCheck(other, &Py##PyName##Type)) { \
            PyErr_SetString(PyExc_TypeError, "Type mismatch"); \
            return NULL; \
        } \
        Py##PyName##Object* result = PyObject_New(Py##PyName##Object, &Py##PyName##Type); \
        result->obj = c_func(self->obj, ((Py##PyName##Object*)other)->obj); \
        if (!result->obj) { \
            Py_DECREF(result); \
            PyErr_SetString(PyExc_ValueError, "Operation failed"); \
            return NULL; \
        } \
        return (PyObject*)result; \
    }

// ============================================================================
// Method Macros
// ============================================================================

// Method generator - single argument of same type
#define QKBIND_METHOD(PyName, method_name, c_func) \
    static PyObject* Py##PyName##_##method_name(Py##PyName##Object* self, PyObject* args) { \
        Py##PyName##Object* other; \
        if (!PyArg_ParseTuple(args, "O!", &Py##PyName##Type, &other)) return NULL; \
        Py##PyName##Object* result = PyObject_New(Py##PyName##Object, &Py##PyName##Type); \
        result->obj = c_func(self->obj, other->obj); \
        if (!result->obj) { \
            Py_DECREF(result); \
            PyErr_SetString(PyExc_ValueError, "Method failed"); \
            return NULL; \
        } \
        return (PyObject*)result; \
    }

// Method generator - no arguments
#define QKBIND_METHOD_NOARGS(PyName, method_name, c_func) \
    static PyObject* Py##PyName##_##method_name(Py##PyName##Object* self, PyObject* Py_UNUSED(args)) { \
        Py##PyName##Object* result = PyObject_New(Py##PyName##Object, &Py##PyName##Type); \
        result->obj = c_func(self->obj); \
        if (!result->obj) { \
            Py_DECREF(result); \
            PyErr_SetString(PyExc_ValueError, "Method failed"); \
            return NULL; \
        } \
        return (PyObject*)result; \
    }

// ============================================================================
// Property Macros
// ============================================================================

// Property getter - int array (e.g., shape)
#define QKBIND_PROPERTY_INT_ARRAY(PyName, prop_name, field, size_field) \
    static PyObject* Py##PyName##_get_##prop_name(Py##PyName##Object* self, void* closure) { \
        PyObject* list = PyList_New(self->obj->size_field); \
        for (int i = 0; i < self->obj->size_field; i++) { \
            PyList_SetItem(list, i, PyLong_FromLong(self->obj->field[i])); \
        } \
        return list; \
    }

// Property getter - single int
#define QKBIND_PROPERTY_INT(PyName, prop_name, field) \
    static PyObject* Py##PyName##_get_##prop_name(Py##PyName##Object* self, void* closure) { \
        return PyLong_FromLong(self->obj->field); \
    }

// Property getter - single size_t
#define QKBIND_PROPERTY_SIZE(PyName, prop_name, field) \
    static PyObject* Py##PyName##_get_##prop_name(Py##PyName##Object* self, void* closure) { \
        return PyLong_FromSize_t(self->obj->field); \
    }

// Property getter - single float
#define QKBIND_PROPERTY_FLOAT(PyName, prop_name, field) \
    static PyObject* Py##PyName##_get_##prop_name(Py##PyName##Object* self, void* closure) { \
        return PyFloat_FromDouble(self->obj->field); \
    }

// ============================================================================
// Type Definition Helpers
// ============================================================================

#define QKBIND_TYPE_BEGIN(PyName, module_name) \
    static PyTypeObject Py##PyName##Type = { \
        PyVarObject_HEAD_INIT(NULL, 0) \
        .tp_name = #module_name "." #PyName, \
        .tp_basicsize = sizeof(Py##PyName##Object), \
        .tp_dealloc = (destructor)Py##PyName##_dealloc, \
        .tp_init = (initproc)Py##PyName##_init, \
        .tp_flags = Py_TPFLAGS_DEFAULT, \
        .tp_new = PyType_GenericNew,

#define QKBIND_TYPE_END };

// ============================================================================
// Module Helpers
// ============================================================================

#define QKBIND_MODULE_BEGIN(module_name) \
    static PyModuleDef module_name##_module = { \
        PyModuleDef_HEAD_INIT, \
        .m_name = #module_name, \
        .m_size = -1, \
    }; \
    PyMODINIT_FUNC PyInit_##module_name(void) { \
        PyObject* m = PyModule_Create(&module_name##_module); \
        if (!m) return NULL;

#define QKBIND_MODULE_ADD_TYPE(PyName) \
    if (PyType_Ready(&Py##PyName##Type) < 0) return NULL; \
    Py_INCREF(&Py##PyName##Type); \
    PyModule_AddObject(m, #PyName, (PyObject*)&Py##PyName##Type);

#define QKBIND_MODULE_ADD_INT(name, value) \
    PyModule_AddIntConstant(m, #name, value);

#define QKBIND_MODULE_END \
        return m; \
    }

#endif // QKBIND_H
