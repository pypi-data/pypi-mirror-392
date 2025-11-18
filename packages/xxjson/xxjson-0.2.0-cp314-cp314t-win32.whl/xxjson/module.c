#include "xxjson.h"


static PyObject *xxjson_dumps(PyObject *self, PyObject *arg) {
    if(!PyMapping_Check(arg)) { 
        PyErr_SetString(PyExc_ValueError, "object must be a dictionary-like");
        return NULL;
    }
    yyjson_mut_doc *doc = yyjson_mut_doc_new(NULL);

    struct xxjson_state *st = PyModule_GetState(self);

    yyjson_mut_val *val = conv_object(st, doc, arg);
    if(!val) {
        yyjson_mut_doc_free(doc);
        return NULL;
    }

    yyjson_mut_doc_set_root(doc, val);

    size_t len;
    char *json = yyjson_mut_write(doc, 0, &len);
    PyObject *out = PyBytes_FromStringAndSize(json, len);
    free(json);
    yyjson_mut_doc_free(doc);
    return out;
}

static PyObject *xxjson_loads(PyObject *self, PyObject *arg) {
    Py_buffer view;
    yyjson_read_err err;
    yyjson_doc *doc;
    yyjson_val *val;
    PyObject *ret;

    if(PyObject_GetBuffer(arg, &view, PyBUF_CONTIG_RO) < 0) {
        return NULL;
    }

    doc = yyjson_read_opts(view.buf, view.len, 0, NULL, &err);
    PyBuffer_Release(&view);
    if(!doc) {
        return PyErr_Format(PyExc_ValueError, "JSON parse error at byte %zu: %s (code %u)",
                err.pos, err.msg, err.code);
    }

    val = yyjson_doc_get_root(doc);

    ret = conv_element(val);
    yyjson_doc_free(doc);

    return ret;
}

static int mod_exec(PyObject *module) {
    PyDateTime_IMPORT;

    PyDateTime_CAPI *capi = PyCapsule_Import("datetime.datetime_CAPI", 0);

    if(capi == NULL) {
        PyErr_SetString(PyExc_RuntimeError, "Failed to import datetime");
        return -1;
    }

    struct xxjson_state *st = PyModule_GetState(module);
    st->capi = capi;

    return 0;
}

static PyModuleDef_Slot slots[] = {
    {Py_mod_exec, mod_exec},
#ifdef Py_GIL_DISABLED
    {Py_mod_gil, Py_MOD_GIL_NOT_USED},
#endif
    {0, NULL}
};

static PyMethodDef methods[] = {
    {"loads", xxjson_loads, METH_O, "Load json from bytes"},
    {"dumps", xxjson_dumps, METH_O, "Write json to bytes"},
    { NULL, NULL, 0, NULL }
};


static struct PyModuleDef module = {
    PyModuleDef_HEAD_INIT,
    "cxxjson",
    "xxjson wraps yyjson",
    sizeof(struct xxjson_state),
    methods,
    slots,
    NULL,
    NULL,
    NULL
};

PyMODINIT_FUNC PyInit_cxxjson(void) {
    return PyModuleDef_Init(&module);
}
