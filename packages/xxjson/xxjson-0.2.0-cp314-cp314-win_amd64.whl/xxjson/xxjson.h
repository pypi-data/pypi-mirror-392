#pragma once

#include "pytypedefs.h"
#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <datetime.h>
#include "yyjson.h"


struct xxjson_state {
    PyDateTime_CAPI *capi; 
};

PyObject *conv_element(yyjson_val *val);
yyjson_mut_val *conv_object(struct xxjson_state *st, yyjson_mut_doc *doc, PyObject *obj);

extern struct PyModuleDef *xxjson_def;
