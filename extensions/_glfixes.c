#include <Python.h>
#include <GL/gl.h>

#ifndef PyMODINIT_FUNC
#if defined(__cplusplus)
#define PyMODINIT_FUNC extern "C" void
#else /* __cplusplus */
#define PyMODINIT_FUNC void
#endif /* __cplusplus */
#endif

static PyObject *wrap_glInterleavedArrays(PyObject *s, PyObject *o) {
    static void *buf = NULL;
    PyObject *str;
    int format, stride, size;

    if(!PyArg_ParseTuple(o, "iiO", &format, &stride, &str)) {
        return NULL;
    }

    if(!PyString_Check(str)) {
        PyErr_Format( PyExc_TypeError, "Expected string" );
        return NULL;
    }

    // size = min(8192, PyString_GET_SIZE(str));
    size = PyString_GET_SIZE(str);
    if(buf == NULL) buf = malloc(size);
    else buf = realloc(buf, size);
    memcpy(buf, PyString_AS_STRING(str), size);
    glInterleavedArrays(format, stride, buf);

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef glfixes_method[] = {
    {"glInterleavedArrays", wrap_glInterleavedArrays, METH_VARARGS, "glInterleavedArrays()"},
    {NULL},
};

PyMODINIT_FUNC
init_glfixes(void) {
    Py_InitModule3("_glfixes", glfixes_method, "replaces buggy PyOpenGL stuff");
}
