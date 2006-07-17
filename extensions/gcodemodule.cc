//    This is a component of AXIS, a front-end for emc
//    Copyright 2004, 2005, 2006 Jeff Epler <jepler@unpythonic.net> and 
//    Chris Radek <chris@timeguy.com>
//
//    This program is free software; you can redistribute it and/or modify
//    it under the terms of the GNU General Public License as published by
//    the Free Software Foundation; either version 2 of the License, or
//    (at your option) any later version.
//
//    This program is distributed in the hope that it will be useful,
//    but WITHOUT ANY WARRANTY; without even the implied warranty of
//    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
//    GNU General Public License for more details.
//
//    You should have received a copy of the GNU General Public License
//    along with this program; if not, write to the Free Software
//    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#include <Python.h>
#include <structmember.h>

#include "rcs.hh"
#include "emc.hh"
#include "rs274ngc.hh"
#include "axisversion.h"

#if defined(AXIS_USE_EMC2) || defined(AXIS_USE_BDI4)
#if defined(AXIS_USE_EMC2)
#include "interp_return.hh"
#else
#include "rs274ngc_return.hh"
#endif
#define active_settings  interp_new.active_settings
#define active_g_codes   interp_new.active_g_codes
#define active_m_codes   interp_new.active_m_codes
#define interp_init	 interp_new.init
#define interp_open      interp_new.open
#define interp_read	 interp_new.read
#define interp_execute	 interp_new.execute
char _parameter_file_name[LINELEN];
#else
#include "rs274ngc_return.hh"
#define INTERP_OK        RS274NGC_OK
#define INTERP_MIN_ERROR RS274NGC_MIN_ERROR
#define ACTIVE_SETTINGS  RS274NGC_ACTIVE_SETTINGS
#define ACTIVE_G_CODES   RS274NGC_ACTIVE_G_CODES 
#define ACTIVE_M_CODES   RS274NGC_ACTIVE_M_CODES 
#define active_settings  rs274ngc_active_settings
#define active_g_codes   rs274ngc_active_g_codes
#define active_m_codes   rs274ngc_active_m_codes
#define interp_init	 rs274ngc_init
#define interp_open      rs274ngc_open
#define interp_read	 rs274ngc_read
#define interp_execute   rs274ngc_execute
#endif
#include "canon.hh"
#include "interpl.hh"

#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC extern "C" void
#endif

/* This definition of offsetof avoids the g++ warning
 * 'invalid offsetof from non-POD type'.
 */
#undef offsetof
#define offsetof(T,x) (size_t)(-1+(char*)&(((T*)1)->x))

extern char *_rs274ngc_errors[];

#define iserror(x) ((x) < 0 || (x) >= RS274NGC_MIN_ERROR)

static PyObject *int_array(int *arr, int sz) {
    PyObject *res = PyTuple_New(sz);
    for(int i = 0; i < sz; i++) {
        PyTuple_SET_ITEM(res, i, PyInt_FromLong(arr[i]));
    }
    return res;
}

extern PyTypeObject LineCodeType, DelayType, VelocityType;
extern PyTypeObject LinearMoveType, CircularMoveType, UnknownMessageType;

typedef struct {
    PyObject_HEAD
    double settings[ACTIVE_SETTINGS];
    int gcodes[ACTIVE_G_CODES];
    int mcodes[ACTIVE_M_CODES];
} LineCode;

PyObject *LineCode_gcodes(LineCode *l) {
    return int_array(l->gcodes, ACTIVE_G_CODES);
}
PyObject *LineCode_mcodes(LineCode *l) {
    return int_array(l->mcodes, ACTIVE_M_CODES);
}

PyGetSetDef LineCodeGetSet[] = {
    {"gcodes", (getter)LineCode_gcodes},
    {"mcodes", (getter)LineCode_mcodes},
};

PyMemberDef LineCodeMembers[] = {
    {"sequence_number", T_INT, offsetof(LineCode, gcodes[0]), READONLY},

    {"feed_rate", T_DOUBLE, offsetof(LineCode, settings[1]), READONLY},
    {"speed", T_DOUBLE, offsetof(LineCode, settings[2]), READONLY},
    {"motion_mode", T_INT, offsetof(LineCode, gcodes[1]), READONLY},
    {"block", T_INT, offsetof(LineCode, gcodes[2]), READONLY},
    {"plane", T_INT, offsetof(LineCode, gcodes[3]), READONLY},
    {"cutter_side", T_INT, offsetof(LineCode, gcodes[4]), READONLY},
    {"units", T_INT, offsetof(LineCode, gcodes[5]), READONLY},
    {"distance_mode", T_INT, offsetof(LineCode, gcodes[6]), READONLY},
    {"feed_mode", T_INT, offsetof(LineCode, gcodes[7]), READONLY},
    {"origin", T_INT, offsetof(LineCode, gcodes[8]), READONLY},
    {"tool_length_offset", T_INT, offsetof(LineCode, gcodes[9]), READONLY},
    {"retract_mode", T_INT, offsetof(LineCode, gcodes[10]), READONLY},
    {"path_mode", T_INT, offsetof(LineCode, gcodes[11]), READONLY},

    {"stopping", T_INT, offsetof(LineCode, mcodes[1]), READONLY},
    {"spindle", T_INT, offsetof(LineCode, mcodes[2]), READONLY},
    {"toolchange", T_INT, offsetof(LineCode, mcodes[3]), READONLY},
    {"mist", T_INT, offsetof(LineCode, mcodes[4]), READONLY},
    {"flood", T_INT, offsetof(LineCode, mcodes[5]), READONLY},
    {"overrides", T_INT, offsetof(LineCode, mcodes[6]), READONLY},
    {NULL}
};

PyTypeObject LineCodeType = {
    PyObject_HEAD_INIT(NULL)
    0,                      /*ob_size*/
    "gcode.linecode",       /*tp_name*/
    sizeof(LineCode),    /*tp_basicsize*/
    0,                      /*tp_itemsize*/
    /* methods */
    0,                      /*tp_dealloc*/
    0,                      /*tp_print*/
    0,                      /*tp_getattr*/
    0,                      /*tp_setattr*/
    0,                      /*tp_compare*/
    0,                      /*tp_repr*/
    0,                      /*tp_as_number*/
    0,                      /*tp_as_sequence*/
    0,                      /*tp_as_mapping*/
    0,                      /*tp_hash*/
    0,                      /*tp_call*/
    0,                      /*tp_str*/
    0,                      /*tp_getattro*/
    0,                      /*tp_setattro*/
    0,                      /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT,     /*tp_flags*/
    0,                      /*tp_doc*/
    0,                      /*tp_traverse*/
    0,                      /*tp_clear*/
    0,                      /*tp_richcompare*/
    0,                      /*tp_weaklistoffset*/
    0,                      /*tp_iter*/
    0,                      /*tp_iternext*/
    0,                      /*tp_methods*/
    LineCodeMembers,     /*tp_members*/
    LineCodeGetSet,      /*tp_getset*/
    0,                      /*tp_base*/
    0,                      /*tp_dict*/
    0,                      /*tp_descr_get*/
    0,                      /*tp_descr_set*/
    0,                      /*tp_dictoffset*/
    0,                      /*tp_init*/
    0,                      /*tp_alloc*/
    PyType_GenericNew,      /*tp_new*/
    0,                      /*tp_free*/
    0,                      /*tp_is_gc*/
};

PyObject *callback;
int interp_error;
int last_sequence_number;
int plane;
bool metric;

#if defined(AXIS_USE_EMC2) || defined(AXIS_USE_BDI4)
Interp interp_new;
#endif

void maybe_new_line() {
    if(interp_error) return;
    LineCode *new_line_code =
        (LineCode*)(PyObject_New(LineCode, &LineCodeType));
    active_settings(new_line_code->settings);
    active_g_codes(new_line_code->gcodes);
    active_m_codes(new_line_code->mcodes);
    int sequence_number = new_line_code->gcodes[0];
    if(sequence_number == last_sequence_number) {
        Py_DECREF(new_line_code);
        return;
    }
    last_sequence_number = sequence_number;
    PyObject *result = 
        PyObject_CallMethod(callback, "next_line", "O", new_line_code);
    Py_DECREF(new_line_code);
    if(result == NULL) interp_error ++;
    Py_XDECREF(result);
}

void ARC_FEED(double first_end, double second_end, double first_axis,
        double second_axis, int rotation, double axis_end_point,
        double a_position, double b_position, double c_position) {
    if(metric) {
        first_end /= 25.4;
        second_end /= 25.4;
        first_axis /= 25.4;
        second_axis /= 25.4;
        axis_end_point /= 25.4;
    }
    maybe_new_line();
    if(interp_error) return;
    PyObject *result =
        PyObject_CallMethod(callback, "arc_feed", "ffffiffff",
            first_end, second_end, first_axis, second_axis,
            rotation, axis_end_point, a_position, b_position, c_position);
    if(result == NULL) interp_error ++;
    Py_XDECREF(result);
}

void STRAIGHT_FEED(double x, double y, double z, double a, double b, double c) {
    if(metric) { x /= 25.4; y /= 25.4; z /= 25.4; }
    maybe_new_line();
    if(interp_error) return;
    PyObject *result =
        PyObject_CallMethod(callback, "straight_feed", "ffffff",
            x, y, z, a, b, c);
    if(result == NULL) interp_error ++;
    Py_XDECREF(result);
}

void STRAIGHT_TRAVERSE(double x, double y, double z, double a, double b, double c) {
    if(metric) { x /= 25.4; y /= 25.4; z /= 25.4; }
    maybe_new_line();
    if(interp_error) return;
    PyObject *result =
        PyObject_CallMethod(callback, "straight_traverse", "ffffff",
            x, y, z, a, b, c);
    if(result == NULL) interp_error ++;
    Py_XDECREF(result);
}

void SET_ORIGIN_OFFSETS(double x, double y, double z, double a, double b, double c) {
    if(metric) { x /= 25.4; y /= 25.4; z /= 25.4; }
    maybe_new_line();
    if(interp_error) return;
    PyObject *result =
        PyObject_CallMethod(callback, "set_origin_offsets", "ffffff",
            x, y, z, a, b, c);
    if(result == NULL) interp_error ++;
    Py_XDECREF(result);
}

void USE_LENGTH_UNITS(CANON_UNITS u) { metric = u == CANON_UNITS_MM; }
void SET_LENGTH_UNITS(CANON_UNITS u) { metric = u == CANON_UNITS_MM; }

void SELECT_PLANE(CANON_PLANE pl) {
    maybe_new_line();   
    if(interp_error) return;
    PyObject *result =
        PyObject_CallMethod(callback, "set_plane", "i", pl);
    if(result == NULL) interp_error ++;
    Py_XDECREF(result);
}

void SET_TRAVERSE_RATE(double rate) {
    maybe_new_line();   
    if(interp_error) return;
    PyObject *result =
        PyObject_CallMethod(callback, "set_traverse_rate", "f", rate);
    if(result == NULL) interp_error ++;
    Py_XDECREF(result);
}

void SET_FEED_RATE(double rate) {
    maybe_new_line();   
    if(interp_error) return;
    PyObject *result =
        PyObject_CallMethod(callback, "set_feed_rate", "f", rate);
    if(result == NULL) interp_error ++;
    Py_XDECREF(result);
}

void DWELL(double time) {
    maybe_new_line();   
    if(interp_error) return;
    PyObject *result =
        PyObject_CallMethod(callback, "dwell", "f", time);
    if(result == NULL) interp_error ++;
    Py_XDECREF(result);
}

void MESSAGE(char *comment) {
    maybe_new_line();   
    if(interp_error) return;
    PyObject *result =
        PyObject_CallMethod(callback, "message", "s", comment);
    if(result == NULL) interp_error ++;
    Py_XDECREF(result);
}

void SYSTEM(char *comment) {
    maybe_new_line();   
    if(interp_error) return;
    PyObject *result =
        PyObject_CallMethod(callback, "system", "s", comment);
    if(result == NULL) interp_error ++;
    Py_XDECREF(result);
}

void COMMENT(char *comment) {
    maybe_new_line();   
    if(interp_error) return;
    PyObject *result =
        PyObject_CallMethod(callback, "comment", "s", comment);
    if(result == NULL) interp_error ++;
    Py_XDECREF(result);
}

void USE_TOOL_LENGTH_OFFSET(double xoffset, double zoffset) {
    maybe_new_line();
    if(interp_error) return;
    PyObject *result = PyObject_CallMethod(callback, "tool_offset", "dd",
            zoffset, xoffset);
    if(result == NULL) interp_error ++;
    Py_XDECREF(result);
}
void USE_TOOL_LENGTH_OFFSET(double offset) {
    maybe_new_line();
    if(interp_error) return;
    PyObject *result = PyObject_CallMethod(callback, "tool_offset", "dd",
            offset, 0);
    if(result == NULL) interp_error ++;
}

void SET_FEED_REFERENCE(double reference) { }
void SET_CUTTER_RADIUS_COMPENSATION(double radius) {}
void START_CUTTER_RADIUS_COMPENSATION(int direction) {}
void STOP_CUTTER_RADIUS_COMPENSATION(int direction) {}
void START_SPEED_FEED_SYNCH() {}
void START_SPEED_FEED_SYNCH(double sync) {}
void STOP_SPEED_FEED_SYNCH() {}
void START_SPINDLE_COUNTERCLOCKWISE() {}
void START_SPINDLE_CLOCKWISE() {}
void STOP_SPINDLE_TURNING() {}
void SET_SPINDLE_SPEED(double rpm) {}
void ORIENT_SPINDLE(double d, int i) {}
void PROGRAM_STOP() {}
void PROGRAM_END() {}
void PALLET_SHUTTLE() {}
void CHANGE_TOOL(int tool) {}
void SELECT_TOOL(int tool) {}
void OPTIONAL_PROGRAM_STOP() {}
void DISABLE_FEED_OVERRIDE() {}
void DISABLE_SPEED_OVERRIDE() {}
void ENABLE_FEED_OVERRIDE() {}
void ENABLE_SPEED_OVERRIDE() {}
void MIST_OFF() {}
void FLOOD_OFF() {}
void MIST_ON() {}
void FLOOD_ON() {}
void CLEAR_AUX_OUTPUT_BIT(int bit) {}
void SET_AUX_OUTPUT_BIT(int bit) {}
void SET_AUX_OUTPUT_VALUE(int index, double value) {}
void CLEAR_MOTION_OUTPUT_BIT(int bit) {}
void SET_MOTION_OUTPUT_BIT(int bit) {}
void SET_MOTION_OUTPUT_VALUE(int index, double value) {}
void TURN_PROBE_ON() {}
void TURN_PROBE_OFF() {}
void STRAIGHT_PROBE(double x, double y, double z, double a, double b, double c) {}
double GET_EXTERNAL_MOTION_CONTROL_TOLERANCE() { return 0.1; }
double GET_EXTERNAL_PROBE_POSITION_X() { return 0.0; }
double GET_EXTERNAL_PROBE_POSITION_Y() { return 0.0; }
double GET_EXTERNAL_PROBE_POSITION_Z() { return 0.0; }
double GET_EXTERNAL_PROBE_POSITION_A() { return 0.0; }
double GET_EXTERNAL_PROBE_POSITION_B() { return 0.0; }
double GET_EXTERNAL_PROBE_POSITION_C() { return 0.0; }
double GET_EXTERNAL_PROBE_VALUE() { return 0.0; }
double GET_EXTERNAL_POSITION_X() { return 0.0; }
double GET_EXTERNAL_POSITION_Y() { return 0.0; }
double GET_EXTERNAL_POSITION_Z() { return 0.0; }
double GET_EXTERNAL_POSITION_A() { return 0.0; }
double GET_EXTERNAL_POSITION_B() { return 0.0; }
double GET_EXTERNAL_POSITION_C() { return 0.0; }
void INIT_CANON() {}
void GET_EXTERNAL_PARAMETER_FILE_NAME(char *name, int max_size) {
    PyObject *result = PyObject_GetAttrString(callback, "parameter_file");
    if(!result) { name[0] = 0; return; }
    char *s = PyString_AsString(result);    
    if(!s) { name[0] = 0; return; }
    memset(name, 0, max_size);
    strncpy(name, s, max_size - 1);
}
int GET_EXTERNAL_LENGTH_UNIT_TYPE() { return CANON_UNITS_INCHES; }
CANON_TOOL_TABLE GET_EXTERNAL_TOOL_TABLE(int tool) {
#if EMC_VERSION_CHECK(2,1,0)
    CANON_TOOL_TABLE t = {0,0,0,0,0,0,0};
    if(interp_error) return t;
    PyObject *result =
        PyObject_CallMethod(callback, "get_tool", "i", tool);
    if(result == NULL ||
        !PyArg_ParseTuple(result, "idddddi", &t.id, &t.zoffset, &t.xoffset, 
                          &t.diameter, &t.frontangle, &t.backangle, 
                          &t.orientation))
            interp_error ++;
#else
    CANON_TOOL_TABLE t = {0,0,0};
    double dummy1, dummy2, dummy3;
    int dummy4;
    if(interp_error) return t;
    PyObject *result =
        PyObject_CallMethod(callback, "get_tool", "i", tool);
    if(result == NULL ||
        !PyArg_ParseTuple(result, "idd|dddi", &t.id, &t.length, &t.diameter,
                &dummy1, &dummy2, &dummy3, &dummy4))
            interp_error ++;
#endif

    Py_XDECREF(result);
    return t;
}
void user_defined_function(int num, double arg1, double arg2) {
    if(interp_error) return;
    maybe_new_line();
    PyObject *result =
        PyObject_CallMethod(callback, "user_defined_function",
                            "idd", num, arg1, arg2);
    if(result == NULL) interp_error++;
    Py_XDECREF(result);
}

void SET_FEED_REFERENCE(int ref) {}
int GET_EXTERNAL_QUEUE_EMPTY() { return true; }
CANON_DIRECTION GET_EXTERNAL_SPINDLE() { return 0; }
int GET_EXTERNAL_TOOL_SLOT() { return 0; }
int GET_EXTERNAL_SELECTED_TOOL_SLOT() { return 0; }
double GET_EXTERNAL_FEED_RATE() { return 0; }
double GET_EXTERNAL_TRAVERSE_RATE() { return 0; }
int GET_EXTERNAL_FLOOD() { return 0; }
int GET_EXTERNAL_MIST() { return 0; }
CANON_PLANE GET_EXTERNAL_PLANE() { return 1; }
double GET_EXTERNAL_SPEED() { return 0; }
int GET_EXTERNAL_TOOL_MAX() { return CANON_TOOL_MAX; }
void STOP_ADAPTIVE_FEED() {} 
void START_ADAPTIVE_FEED() {} 

bool PyFloat_CheckAndError(const char *func, PyObject *p)  {
    if(PyFloat_Check(p)) return true;
    PyErr_Format(PyExc_TypeError,
            "%s: Expected double, got %s", func, p->ob_type->tp_name);
    return false;
}

double GET_EXTERNAL_ANGLE_UNITS() {
    PyObject *result =
        PyObject_CallMethod(callback, "get_external_angular_units", "");
    if(result == NULL) interp_error++;

    double dresult = 1.0;
    if(!result || !PyFloat_CheckAndError("get_external_angle_units", result)) {
        interp_error++;
    } else {
        dresult = PyFloat_AsDouble(result);
    }
    Py_XDECREF(result);
    return dresult;
}

double GET_EXTERNAL_LENGTH_UNITS() {
    PyObject *result =
        PyObject_CallMethod(callback, "get_external_length_units", "");
    if(result == NULL) interp_error++;

    double dresult = 0.03937007874016;
    if(!result || !PyFloat_CheckAndError("get_external_length_units", result)) {
        interp_error++;
    } else {
        dresult = PyFloat_AsDouble(result);
    }
    Py_XDECREF(result);
    return dresult;
}

bool check_abort() {
    PyObject *result =
        PyObject_CallMethod(callback, "check_abort", "");
    if(!result) return 1;
    if(PyObject_IsTrue(result)) {
        Py_DECREF(result);
        PyErr_Format(PyExc_KeyboardInterrupt, "Load aborted");
        return 1;
    }
    Py_DECREF(result);
    return 0;
}

USER_DEFINED_FUNCTION_TYPE USER_DEFINED_FUNCTION[USER_DEFINED_FUNCTION_NUM];

CANON_MOTION_MODE motion_mode;
void SET_MOTION_CONTROL_MODE(CANON_MOTION_MODE mode, double tolerance) { motion_mode = mode; }
void SET_MOTION_CONTROL_MODE(double tolerance) { }
void SET_MOTION_CONTROL_MODE(CANON_MOTION_MODE mode) { motion_mode = mode; }
CANON_MOTION_MODE GET_EXTERNAL_MOTION_CONTROL_MODE() { return motion_mode; }

PyObject *parse_file(PyObject *self, PyObject *args) {
    char *f;
    char *unitcode=0, *initcode=0;
    struct timeval t0, t1;
    int wait = 1;
    if(!PyArg_ParseTuple(args, "sO|ss", &f, &callback, &unitcode, &initcode))
        return NULL;

    for(int i=0; i<USER_DEFINED_FUNCTION_NUM; i++) 
        USER_DEFINED_FUNCTION[i] = user_defined_function;

    gettimeofday(&t0, NULL);

    metric=false;
    interp_error = 0;
    last_sequence_number = -1;

    interp_init();
    interp_open(f);
    int result = INTERP_OK;
    if(unitcode) {
        result = interp_read(unitcode);
        if(result != INTERP_OK) goto out_error;
        result = interp_execute();
    }
    if(initcode && result == INTERP_OK) {
        result = interp_read(initcode);
        if(result != INTERP_OK) goto out_error;
        result = interp_execute();
    }
    while(!interp_error && result == INTERP_OK) {
        result = interp_read();
        gettimeofday(&t1, NULL);
        if(t1.tv_sec > t0.tv_sec + wait) {
            if(check_abort()) return NULL;
            t0 = t1;
        }
        if(result != INTERP_OK) break;
        result = interp_execute();
    }
out_error:
    if(interp_error) {
        if(!PyErr_Occurred()) {
            PyErr_Format(PyExc_RuntimeError,
                    "interp_error > 0 but no Python exception set");
        }
        return NULL;
    }
    PyErr_Clear();
    PyObject *retval = PyTuple_New(2);
    PyTuple_SetItem(retval, 0, PyInt_FromLong(result));
    PyTuple_SetItem(retval, 1, PyInt_FromLong(last_sequence_number));
    return retval;
}


static int maxerror = -1;

static int find_maxerror(void) {
    int i=0;
    for(;;i++) {
        if(!_rs274ngc_errors[i] || !strcmp(_rs274ngc_errors[i], "The End"))
            return i;
    }
}

static PyObject *rs274_strerror(PyObject *s, PyObject *o) {
    int err;
    if(!PyArg_ParseTuple(o, "i", &err)) return NULL;
    if(err < 0 || err >= maxerror) {
        return PyString_FromString("Error number out of range");
    }
    return PyString_FromString(_rs274ngc_errors[err]);
}

PyMethodDef gcode_methods[] = {
    {"parse", (PyCFunction)parse_file, METH_VARARGS, "Parse a G-Code file"},
    {"strerror", (PyCFunction)rs274_strerror, METH_VARARGS, "Convert a numeric error to a string"},
    {NULL}
};

PyMODINIT_FUNC
initgcode(void) {
    PyObject *m = Py_InitModule3("gcode", gcode_methods,
                "Interface to EMC rs274ngc interpreter");
    PyType_Ready(&LineCodeType);
    PyModule_AddObject(m, "linecode", (PyObject*)&LineCodeType);
    maxerror = find_maxerror();
    PyObject_SetAttrString(m, "MAX_ERROR", PyInt_FromLong(maxerror));
    PyObject_SetAttrString(m, "MIN_ERROR",
            PyInt_FromLong(INTERP_MIN_ERROR));
}
