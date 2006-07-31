#include <Python.h>
#define ULAPI
#include "hal.h"

#include "emc.hh"
#include "axisversion.h"

#ifndef Py_RETURN_NONE
#define Py_RETURN_NONE return Py_INCREF(Py_None), Py_None
#endif

union ptrunion {
    void *v;
    hal_bit_t *b;
    hal_u8_t *u8;
    hal_s8_t *s8;
    hal_u16_t *u16;
    hal_s16_t *s16;
    hal_u32_t *u32;
    hal_s32_t *s32;
    hal_float_t *f;
};

typedef struct halpin { 
    char *name;
    hal_type_t type;
    hal_dir_t dir;
    union ptrunion *u; 
} halpin;

typedef struct halobject {
    PyObject_HEAD
    int hal_id;
    char *name;
    int npins, mpins;
    struct halpin *pins;
} halobject;

PyObject *pyhal_error_type = NULL;

static PyObject *pyhal_error(int code) {
    switch(code) {
        case HAL_SUCCESS:
            PyErr_SetString(pyhal_error_type, "Call Successful"); break;
        case HAL_UNSUP:
            PyErr_SetString(pyhal_error_type, "Function not supported"); break;
        case HAL_BADVAR:
            PyErr_SetString(pyhal_error_type, "Duplicate or not-found variable name"); break;
        case HAL_INVAL:
            PyErr_SetString(pyhal_error_type, "Invalid argument"); break;
        case HAL_NOMEM:
            PyErr_SetString(pyhal_error_type, "Not enough memory"); break;
        case HAL_LIMIT:
            PyErr_SetString(pyhal_error_type, "Resource limit reached"); break;
        case HAL_PERM:
            PyErr_SetString(pyhal_error_type, "Permission Denied"); break;
        case HAL_BUSY:
            PyErr_SetString(pyhal_error_type, "Resources is busy or locked");
            break;
        case HAL_NOTFND:
            PyErr_SetString(pyhal_error_type, "Object not found"); break;
        case HAL_FAIL:
            PyErr_SetString(pyhal_error_type, "Operation failed"); break;
        default:
            PyErr_Format(pyhal_error_type, "Unknown error code %d", code);
            break;
    }
    return NULL;
}

static int pyhal_init(halobject *self, PyObject *args, PyObject *kw) {
    char *name;

    if(!PyArg_ParseTuple(args, "s:hal.component", &name)) return -1;
    self->hal_id = hal_init(name);
    if(self->hal_id <= 0) {
        pyhal_error(self->hal_id);
        return -1;
    }
    self->name = strdup(name);
    if(!name) {
        PyErr_SetString(PyExc_MemoryError, "strdup(name) failed");
        return -1;
    }
    self->npins = self->mpins = 0;
    return 0;
}

static void pyhal_delete(halobject *self) {
    if(self->hal_id > 0) 
        hal_exit(self->hal_id);

    if(self->name)
        free(self->name);

    if(self->pins)
        free(self->pins);

    PyObject_Del(self);
}

#define MAX_PIN_SIZE sizeof(hal_float_t)

static int pyhal_write_common(halpin *pin, PyObject *value) {
    int is_int = PyInt_Check(value);
    int intval = is_int ? PyInt_AsLong(value) : -1;
    unsigned int uintval;
    if(!pin) return -1;

    switch(pin->type) {
        case HAL_BIT:
            *pin->u->b = PyObject_IsTrue(value);
            break;
        case HAL_FLOAT:
            if(PyFloat_Check(value)) 
                *pin->u->f = PyFloat_AsDouble(value);
            else if(is_int)
                *pin->u->f = intval;
            else {
                PyErr_Format(PyExc_TypeError,
                        "Integer or float expected, not %s",
                        value->ob_type->tp_name);
                return -1;
            }
            break;
        case HAL_U8:
            if(!is_int) goto typeerr;
            if(intval < 0 || intval > 0xff) goto rangeerr;
            *pin->u->u8 = intval;
            break;
        case HAL_S8:
            if(!is_int) goto typeerr;
            if(intval < -0x80 || intval > 0x7f) goto rangeerr;
            *pin->u->s8 = intval;
            break;
        case HAL_U16:
            if(!is_int) goto typeerr;
            if(intval < 0 || intval > 0xffff) goto rangeerr;
            *pin->u->u16 = intval;
            break;
        case HAL_S16:
            if(!is_int) goto typeerr;
            if(intval < -0x8000 || intval > 0x7fff) goto rangeerr;
            *pin->u->s16 = intval;
            break;
        case HAL_U32:
            if(is_int) {
                if(intval < 0) goto rangeerr;
                *pin->u->u32 = intval;
                break;
            }
            if(!PyLong_Check(value)) {
                PyErr_Format(PyExc_TypeError,
                        "Integer or long expected, not %s",
                        value->ob_type->tp_name);
                return -1;
            }
            uintval = PyLong_AsUnsignedLong(value);
            if(PyErr_Occurred()) return -1;
            *pin->u->u32 = uintval;
            break;
        case HAL_S32:
            if(!is_int) goto typeerr;
            *pin->u->s32 = intval;
            break;
        default:
            PyErr_Format(pyhal_error_type, "Invalid pin type %d", pin->type);
    }
    return 0;
typeerr:
    PyErr_Format(PyExc_TypeError, "Integer expected, not %s",
            value->ob_type->tp_name);
    return -1;
rangeerr:
    PyErr_Format(PyExc_OverflowError, "Value %d out of range for pin", intval);
    return -1;
}

static PyObject *pyhal_read_common(halpin *pin) {
    if(!pin) return NULL;
    switch(pin->type) {
        case HAL_BIT: return PyBool_FromLong(*(pin->u->b));
        case HAL_U8: return PyInt_FromLong(*(pin->u->u8));
        case HAL_S8: return PyInt_FromLong(*(pin->u->s8));
        case HAL_U16: return PyInt_FromLong(*(pin->u->u16));
        case HAL_S16: return PyInt_FromLong(*(pin->u->s16));
        case HAL_U32: return PyLong_FromUnsignedLong(*(pin->u->u32));
        case HAL_S32: return PyInt_FromLong(*(pin->u->s32));
        case HAL_FLOAT: return PyFloat_FromDouble(*(pin->u->f));
    }
    PyErr_Format(pyhal_error_type, "Invalid pin type %d", pin->type);
    return NULL;
}

static halpin *find_pin(halobject *self, char *name) {
    int i;

    if(!name) return NULL;

    for(i=0; i<self->npins; i++) {
        if(strcmp(name, self->pins[i].name) == 0) {
            return &self->pins[i];
        }
    }
    PyErr_Format(PyExc_AttributeError, "Pin '%s' does not exist", name);
    return NULL;
}

static PyObject * pyhal_create_common(halobject *self, char *name, hal_type_t type, hal_dir_t dir) {
    char pin_name[HAL_NAME_LEN];
    int res;
    halpin *pin;

    if(type < HAL_BIT || type > HAL_U32) {
        PyErr_Format(pyhal_error_type, "Invalid pin type %d", type);
        return NULL;
    }
    if(self->npins == self->mpins) {
        halpin *pins;
        self->mpins = 2 * self->mpins + 1;
        pins = (halpin*)realloc(self->pins, sizeof(halpin) * self->mpins);
        if(!pins) {
            PyErr_SetString(PyExc_MemoryError, "realloc(pins) failed");
            return NULL;
        }
        self->pins = pins;
    }

    pin = &self->pins[self->npins];
    
    pin->name = strdup(name);
    if(!pin->name) {
        PyErr_SetString(PyExc_MemoryError, "strdup(name) failed");
        return NULL;
    }

    pin->type = type;
    pin->dir = dir;
    pin->u = (ptrunion*)hal_malloc(MAX_PIN_SIZE);
    if(!pin->u) {
        free(pin->name);
        PyErr_SetString(PyExc_MemoryError, "hal_malloc failed");
        return NULL;
    }

    snprintf(pin_name, HAL_NAME_LEN, "%s.%s", self->name, name);
    res = hal_pin_new(pin_name, type, dir, (void**)pin->u, self->hal_id);
    if(res) return pyhal_error(res);

    self->npins ++;

    Py_RETURN_NONE;
}

static PyObject *pyhal_new_pin(halobject *self, PyObject *o) {
    char *name;
    int type, dir;

    if(!PyArg_ParseTuple(o, "sii", &name, &type, &dir)) 
        return NULL;

    return pyhal_create_common(self, name, (hal_type_t)type, (hal_dir_t)dir);
}

static PyObject *pyhal_ready(halobject *self, PyObject *o) {
#if EMC_VERSION_CHECK(2,1,0)
    // hal_ready did not exist in EMC 2.0.x, make it a no-op
    int res = hal_ready(self->hal_id);
    if(res) return pyhal_error(res);
#endif
    Py_RETURN_NONE;
}

static PyObject *pyhal_exit(halobject *self, PyObject *o) {
    if(self->hal_id > 0) 
        hal_exit(self->hal_id);
    self->hal_id = 0;
    Py_RETURN_NONE;
}

static PyObject *pyhal_repr(halobject *self) {
    return PyString_FromFormat("<hal component %s(%d) with %d pins>",
            self->name, self->hal_id, self->npins);
}

static PyObject *pyhal_getattro(halobject *self, PyObject *attro)  {
    PyObject *result;

    result = PyObject_GenericGetAttr((PyObject*)self, attro);
    if(result) return result;

    PyErr_Clear();
    return pyhal_read_common(find_pin(self, PyString_AsString(attro)));
}

static int pyhal_setattro(halobject *self, PyObject *attro, PyObject *v) {
    return pyhal_write_common(find_pin(self, PyString_AsString(attro)), v);
}

static PyMethodDef hal_methods[] = {
    {"newpin", (PyCFunction)pyhal_new_pin, METH_VARARGS,
        "Create a new pin"},
    {"exit", (PyCFunction)pyhal_exit, METH_NOARGS,
        "Call hal_exit"},
    {"ready", (PyCFunction)pyhal_ready, METH_NOARGS,
        "Call hal_ready"},
    {NULL},
};

static 
PyTypeObject halobject_type = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "hal.component",           /*tp_name*/
    sizeof(halobject),         /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor) pyhal_delete, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    (reprfunc) pyhal_repr,     /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    (getattrofunc)pyhal_getattro,/*tp_getattro*/
    (setattrofunc)pyhal_setattro,/*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    "HAL Component",           /*tp_doc*/
    0,                         /*tp_traverse*/
    0,                         /*tp_clear*/
    0,                         /*tp_richcompare*/
    0,                         /*tp_weaklistoffset*/
    0,                         /*tp_iter*/
    0,                         /*tp_iternext*/
    hal_methods,               /*tp_methods*/
    0,                         /*tp_members*/
    0,                         /*tp_getset*/
    0,                         /*tp_base*/
    0,                         /*tp_dict*/
    0,                         /*tp_descr_get*/
    0,                         /*tp_descr_set*/
    0,                         /*tp_dictoffset*/
    (initproc)pyhal_init,      /*tp_init*/
    0,                         /*tp_alloc*/
    PyType_GenericNew,         /*tp_new*/
    0,                         /*tp_free*/
    0,                         /*tp_is_gc*/
};

PyMethodDef module_methods[] = {
    {NULL},
};

extern "C"
void inithal(void) {
    PyObject *m = Py_InitModule3("hal", module_methods,
            "Interface to emc2's hal");

    pyhal_error_type = PyErr_NewException("hal.error", NULL, NULL);
    PyModule_AddObject(m, "error", pyhal_error_type);

    PyType_Ready(&halobject_type);
    PyModule_AddObject(m, "component", (PyObject*)&halobject_type);

    PyModule_AddIntConstant(m, "HAL_BIT", HAL_BIT);
    PyModule_AddIntConstant(m, "HAL_FLOAT", HAL_FLOAT);
    PyModule_AddIntConstant(m, "HAL_S8", HAL_S8);
    PyModule_AddIntConstant(m, "HAL_U8", HAL_U8);
    PyModule_AddIntConstant(m, "HAL_S16", HAL_S16);
    PyModule_AddIntConstant(m, "HAL_U16", HAL_U16);
    PyModule_AddIntConstant(m, "HAL_S32", HAL_S32);
    PyModule_AddIntConstant(m, "HAL_U32", HAL_U32);

    PyModule_AddIntConstant(m, "HAL_RD", HAL_RD);
    PyModule_AddIntConstant(m, "HAL_WR", HAL_WR);
    PyModule_AddIntConstant(m, "HAL_RD_WR", HAL_RD_WR);
}
