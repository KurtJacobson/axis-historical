// This is an approach I tried and abandoned, to use the interplist
// It is included in case I change my mind.

#include <Python.h>
#include <structmember.h>

#include "rcs.hh"
#include "emc.hh"
#include "rs274ngc.hh"
#include "rs274ngc_return.hh"
#include "canon.hh"
#include "interpl.hh"

#ifndef PyMODINIT_FUNC
#define PyMODINIT_FUNC void
#endif

/* This definition of offsetof avoids the g++ warning
 * 'invalid offsetof from non-POD type'.
 */
#undef offsetof
#define offsetof(T,x) (int)(-1+(char*)&(((T*)1)->x))


static PyObject *pose(const EmcPose &p) {
    PyObject *res = PyTuple_New(6);
    PyTuple_SET_ITEM(res, 0, PyFloat_FromDouble(p.tran.x));
    PyTuple_SET_ITEM(res, 1, PyFloat_FromDouble(p.tran.y));
    PyTuple_SET_ITEM(res, 2, PyFloat_FromDouble(p.tran.z));
    PyTuple_SET_ITEM(res, 3, PyFloat_FromDouble(p.a));
    PyTuple_SET_ITEM(res, 4, PyFloat_FromDouble(p.b));
    PyTuple_SET_ITEM(res, 5, PyFloat_FromDouble(p.c));
    return res;
}

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
    double settings[RS274NGC_ACTIVE_SETTINGS];
    int gcodes[RS274NGC_ACTIVE_G_CODES];
    int mcodes[RS274NGC_ACTIVE_M_CODES];
} LineCode;

typedef struct {
    PyObject_HEAD
    int lineno;
    EMC_TRAJ_DELAY m;
} Delay;

typedef struct {
    PyObject_HEAD
    int lineno;
    EMC_TRAJ_SET_VELOCITY m;
} Velocity;

typedef struct {
    PyObject_HEAD
    int lineno;
    EMC_TRAJ_LINEAR_MOVE m;
} LinearMove;

typedef struct {
    PyObject_HEAD
    int lineno;
    EMC_TRAJ_CIRCULAR_MOVE m;
} CircularMove;

typedef struct {
    PyObject_HEAD
    int lineno;
    int message_type;
} UnknownMessage;

UnknownMessage *UnknownMessageNew(int lineno, int message_type) {
    UnknownMessage *res = PyObject_New(UnknownMessage, &UnknownMessageType);
    res->lineno = lineno;
    res->message_type = message_type;
    return res;
}

PyMemberDef UnknownMessageMembers[] = {
    {"lineno", T_INT, offsetof(UnknownMessage, lineno), READONLY},
    {"message_type", T_INT, offsetof(UnknownMessage, message_type), READONLY},
    {NULL}
};

PyTypeObject UnknownMessageType = {
    PyObject_HEAD_INIT(NULL)
    0,                      /*ob_size*/
    "gcode.unknownmessage", /*tp_name*/
    sizeof(UnknownMessage), /*tp_basicsize*/
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
    UnknownMessageMembers,  /*tp_members*/
    0,                      /*tp_getset*/
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


Delay *DelayNew(int lineno, EMC_TRAJ_DELAY *m) {
    Delay *res = PyObject_New(Delay, &DelayType);
    res->lineno = lineno;
    memcpy(&res->m, m, sizeof(EMC_TRAJ_DELAY));
    return res;
};

PyMemberDef DelayMembers[] = {
    {"lineno", T_INT, offsetof(Delay, lineno), READONLY},
    {"delay", T_DOUBLE, offsetof(Delay, m.delay), READONLY},
    {NULL}
};

PyTypeObject DelayType = {
    PyObject_HEAD_INIT(NULL)
    0,                      /*ob_size*/
    "gcode.delay",          /*tp_name*/
    sizeof(Delay),          /*tp_basicsize*/
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
    DelayMembers,           /*tp_members*/
    0,                      /*tp_getset*/
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


Velocity *VelocityNew(int lineno, EMC_TRAJ_SET_VELOCITY *m, bool metric) {
    Velocity *res = PyObject_New(Velocity, &VelocityType);
    res->lineno = lineno;
    memcpy(&res->m, m, sizeof(EMC_TRAJ_SET_VELOCITY));
    if(metric) { res->m.velocity /= 25.4; }
    return res;
};

PyMemberDef VelocityMembers[] = {
    {"lineno", T_INT, offsetof(Velocity, lineno), READONLY},
    {"velocity", T_DOUBLE, offsetof(Velocity, m.velocity), READONLY},
    {NULL}
};

PyTypeObject VelocityType = {
    PyObject_HEAD_INIT(NULL)
    0,                      /*ob_size*/
    "gcode.velocity",       /*tp_name*/
    sizeof(Velocity),     /*tp_basicsize*/
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
    VelocityMembers,                      /*tp_members*/
    0,                    /*tp_getset*/
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


LinearMove *LinearMoveNew(int lineno, EMC_TRAJ_LINEAR_MOVE *m, bool metric) {
    LinearMove *res = PyObject_New(LinearMove, &LinearMoveType);
    res->lineno = lineno;
    memcpy(&res->m, m, sizeof(EMC_TRAJ_LINEAR_MOVE));
    if(metric) {
        res->m.end.tran.x /= 25.4;
        res->m.end.tran.y /= 25.4;
        res->m.end.tran.z /= 25.4;
    }
    return res;
};

PyMemberDef LinearMoveMembers[] = {
    {"lineno", T_INT, offsetof(LinearMove, lineno), READONLY},
    {"x", T_DOUBLE, offsetof(LinearMove, m.end.tran.x), READONLY},
    {"y", T_DOUBLE, offsetof(LinearMove, m.end.tran.y), READONLY},
    {"z", T_DOUBLE, offsetof(LinearMove, m.end.tran.z), READONLY},
    {"a", T_DOUBLE, offsetof(LinearMove, m.end.a), READONLY},
    {"b", T_DOUBLE, offsetof(LinearMove, m.end.b), READONLY},
    {"c", T_DOUBLE, offsetof(LinearMove, m.end.c), READONLY},
    {NULL}
};

PyTypeObject LinearMoveType = {
    PyObject_HEAD_INIT(NULL)
    0,                      /*ob_size*/
    "gcode.linearmove",     /*tp_name*/
    sizeof(LinearMove),     /*tp_basicsize*/
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
    LinearMoveMembers,      /*tp_members*/
    0,                      /*tp_getset*/
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


CircularMove *CircularMoveNew(int lineno,
                            EMC_TRAJ_CIRCULAR_MOVE *m, bool metric) {
    CircularMove *res = PyObject_New(CircularMove, &CircularMoveType);
    res->lineno = lineno;
    memcpy(&res->m, m, sizeof(EMC_TRAJ_CIRCULAR_MOVE));
    if(metric) {
        res->m.end.tran.x /= 25.4;
        res->m.end.tran.y /= 25.4;
        res->m.end.tran.z /= 25.4;

        res->m.center.x /= 25.4;
        res->m.center.y /= 25.4;
        res->m.center.z /= 25.4;
    }
    return res;
};

PyMemberDef CircularMoveMembers[] = {
    {"lineno", T_INT, offsetof(CircularMove, lineno), READONLY},
    {"x", T_DOUBLE, offsetof(CircularMove, m.end.tran.x), READONLY},
    {"y", T_DOUBLE, offsetof(CircularMove, m.end.tran.y), READONLY},
    {"z", T_DOUBLE, offsetof(CircularMove, m.end.tran.z), READONLY},
    {"a", T_DOUBLE, offsetof(CircularMove, m.end.a), READONLY},
    {"b", T_DOUBLE, offsetof(CircularMove, m.end.b), READONLY},
    {"c", T_DOUBLE, offsetof(CircularMove, m.end.c), READONLY},
    {"center_x", T_DOUBLE, offsetof(CircularMove, m.center.x), READONLY},
    {"center_y", T_DOUBLE, offsetof(CircularMove, m.center.y), READONLY},
    {"center_z", T_DOUBLE, offsetof(CircularMove, m.center.z), READONLY},
    {"normal_x", T_DOUBLE, offsetof(CircularMove, m.normal.x), READONLY},
    {"normal_y", T_DOUBLE, offsetof(CircularMove, m.normal.y), READONLY},
    {"normal_z", T_DOUBLE, offsetof(CircularMove, m.normal.z), READONLY},
    {NULL}
};

PyTypeObject CircularMoveType = {
    PyObject_HEAD_INIT(NULL)
    0,                      /*ob_size*/
    "gcode.circularmove",   /*tp_name*/
    sizeof(CircularMove),   /*tp_basicsize*/
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
    CircularMoveMembers,    /*tp_members*/
    0,                      /*tp_getset*/
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


PyObject *LineCode_gcodes(LineCode *l) {
    return int_array(l->gcodes, RS274NGC_ACTIVE_G_CODES);
}
PyObject *LineCode_mcodes(LineCode *l) {
    return int_array(l->mcodes, RS274NGC_ACTIVE_M_CODES);
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
int last_lineno;
int lineno;
int plane;
bool metric;

void maybe_new_line() {
    if(interp_error) return;
    if(lineno == last_lineno) return;
    last_lineno = lineno;
    LineCode *new_line_code =
        (LineCode*)(PyObject_New(LineCode, &LineCodeType));
    rs274ngc_active_settings(new_line_code->settings);
    rs274ngc_active_g_codes(new_line_code->gcodes);
    rs274ngc_active_m_codes(new_line_code->mcodes);
    PyObject *result = 
        PyObject_CallMethod(callback, "next_line", "O", new_line_code);
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

void SET_LENGTH_UNITS(CANON_UNITS u) {
    metric = u == CANON_UNITS_MM;
}

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

void SET_FEED_REFERENCE(double reference) { }
void SET_CUTTER_RADIUS_COMPENSATION(double radius) {}
void START_CUTTER_RADIUS_COMPENSATION(int direction) {}
void STOP_CUTTER_RADIUS_COMPENSATION(int direction) {}
void START_SPEED_FEED_SYNCH() {}
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
void USE_TOOL_LENGTH_OFFSET(double length) {}
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
void GET_EXTERNAL_PARAMETER_FILE_NAME(char *name, int max_size) {}
int GET_EXTERNAL_LENGTH_UNIT_TYPE() { return CANON_UNITS_INCHES; }
CANON_TOOL_TABLE GET_EXTERNAL_TOOL_TABLE(int tool) {
    CANON_TOOL_TABLE t = {0, 0, 0}; return t;
}
void SET_FEED_REFERENCE(int ref) {}
int GET_EXTERNAL_QUEUE_EMPTY() { return true; }
CANON_DIRECTION GET_EXTERNAL_SPINDLE() { return 0; }
int GET_EXTERNAL_TOOL_SLOT() { return 0; }
double GET_EXTERNAL_FEED_RATE() { return 0; }
double GET_EXTERNAL_TRAVERSE_RATE() { return 0; }
int GET_EXTERNAL_FLOOD() { return 0; }
int GET_EXTERNAL_MIST() { return 0; }
CANON_PLANE GET_EXTERNAL_PLANE() { return 0; }
double GET_EXTERNAL_SPEED() { return 0; }
int GET_EXTERNAL_TOOL_MAX() { return 0; }

USER_DEFINED_FUNCTION_TYPE USER_DEFINED_FUNCTION[USER_DEFINED_FUNCTION_NUM];

CANON_MOTION_MODE motion_mode;
void SET_MOTION_CONTROL_MODE(CANON_MOTION_MODE mode) { motion_mode = mode; }
CANON_MOTION_MODE GET_EXTERNAL_MOTION_CONTROL_MODE() { return motion_mode; }

PyObject *parse_file(PyObject *self, PyObject *args) {
    char *f;
    if(!PyArg_ParseTuple(args, "sO", &f, &callback)) return NULL;

    metric=false;
    lineno=1;
    interp_error = 0;
    last_lineno = -1;

    rs274ngc_init();
    rs274ngc_open(f);
    while(!interp_error) {
        lineno++;
        int result = rs274ngc_read();
        if(result != RS274NGC_OK) break;
        result = rs274ngc_execute();
        if(result != RS274NGC_OK) break;
    }
    if(interp_error) return NULL;
    Py_INCREF(Py_None);
    return Py_None;
}

PyMethodDef gcode_methods[] = {
    {"parse", (PyCFunction)parse_file, METH_VARARGS, "Parse a G-Code file"},
    {NULL}
};

PyMODINIT_FUNC
initgcode(void) {
    PyObject *m = Py_InitModule3("gcode", gcode_methods,
                "Interface to EMC rs274ngc interpreter");
    PyType_Ready(&LineCodeType);
    PyType_Ready(&DelayType);
    PyType_Ready(&VelocityType);
    PyType_Ready(&LinearMoveType);
    PyType_Ready(&CircularMoveType);
    PyType_Ready(&UnknownMessageType);

    PyModule_AddObject(m, "linecode", (PyObject*)&LineCodeType);
    PyModule_AddObject(m, "delay", (PyObject*)&DelayType);
    PyModule_AddObject(m, "velocity", (PyObject*)&VelocityType);
    PyModule_AddObject(m, "linearmove", (PyObject*)&LinearMoveType);
    PyModule_AddObject(m, "circularmove", (PyObject*)&CircularMoveType);
    PyModule_AddObject(m, "unknownmessage", (PyObject*)&UnknownMessageType);
}
