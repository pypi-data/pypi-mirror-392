#include "xxjson.h"

#include <ctype.h>
#include <string.h>


static inline int iso8601(const char *s) {
    if (!s) return 0;                // NULL pointer check

    size_t n = strlen(s);
    if (n < 10) return 0;            // shortest is YYYY-MM-DD

    // YYYY-MM-DD
    if (n >= 10) {
        if (!(isdigit(s[0]) && isdigit(s[1]) &&
              isdigit(s[2]) && isdigit(s[3]) &&
              s[4] == '-' &&
              isdigit(s[5]) && isdigit(s[6]) &&
              s[7] == '-' &&
              isdigit(s[8]) && isdigit(s[9])))
            return 0;
    } else return 0;

    if (n == 10)
        return 1;                    // date only OK

    // Must have at least "T00:00"
    if (n < 16) return 0;

    if (s[10] != 'T') return 0;

    // HH:MM
    if (!(isdigit(s[11]) && isdigit(s[12]) &&
          s[13] == ':' &&
          isdigit(s[14]) && isdigit(s[15])))
        return 0;

    size_t p = 16;

    // Optional seconds
    if (p < n && s[p] == ':') {
        if (n < p + 3) return 0;  // need p, p+1 digits
        if (!(isdigit(s[p+1]) && isdigit(s[p+2])))
            return 0;
        p += 3;  // move past :ss

        // Optional fractional
        if (p < n && s[p] == '.') {
            p++;
            if (p >= n || !isdigit(s[p])) return 0;
            while (p < n && isdigit(s[p])) p++;
        }
    }

    // Ended cleanly
    if (p == n) return 1;

    // Timezone: Z
    if (s[p] == 'Z')
        return p + 1 == n;

    // Timezone: ±HH or ±HH:MM
    if (s[p] == '+' || s[p] == '-') {
        p++;
        if (p + 1 >= n) return 0;
        if (!(isdigit(s[p]) && isdigit(s[p+1])))
            return 0;
        p += 2;

        if (p == n) return 1;  // ±HH form

        if (p + 2 >= n) return 0;
        if (s[p] != ':') return 0;
        if (!(isdigit(s[p+1]) && isdigit(s[p+2])))
            return 0;
        p += 3;

        return p == n;
    }

    return 0;
}



static inline size_t utf8_chars(const char *s, size_t len) {
    size_t count = 0;
    for(size_t i = 0; i < len; i++) {
        if(yyjson_likely(s[i] >> 6 != 2)) {
            count++;
        }
    }
    return count;
}

static inline PyObject *conv_datetime(PyObject *str) {
    PyObject *dt_module = PyImport_ImportModule("datetime");
    if (!dt_module) return NULL;

    PyObject *datetime_cls = PyObject_GetAttrString(dt_module, "datetime");
    Py_DECREF(dt_module);
    if (!datetime_cls) return NULL;

    PyObject *fromiso = PyObject_GetAttrString(datetime_cls, "fromisoformat");
    Py_DECREF(datetime_cls);
    if(!fromiso) return NULL;


    PyObject *result = PyObject_CallOneArg(fromiso, str);
    Py_DECREF(str);
    return result;
}


static inline PyObject *conv_str(const char *s, size_t len) {
    size_t nchars = utf8_chars(s,len);
    if(yyjson_likely(nchars == len)) {
        PyObject *uni = PyUnicode_New(len, 127);
        if(!uni) return NULL;
        PyASCIIObject *asc = (PyASCIIObject *)uni;
        memcpy(asc + 1, s, len);
        if(yyjson_unlikely(iso8601(s))) {
            return conv_datetime(uni);
        } else {
            return uni;
        }
    }
    return PyUnicode_DecodeUTF8(s, len, NULL);
}

PyObject *conv_element(yyjson_val *val) {
    yyjson_type type = yyjson_get_type(val);

    switch(type) {
    case YYJSON_TYPE_NULL:
        Py_RETURN_NONE;
    case YYJSON_TYPE_BOOL:
        if(yyjson_get_subtype(val) == YYJSON_SUBTYPE_TRUE) {
            Py_RETURN_TRUE;
        } else {
            Py_RETURN_FALSE;
        }
    case YYJSON_TYPE_STR:
        return conv_str(yyjson_get_str(val), yyjson_get_len(val));
    case YYJSON_TYPE_NUM:
        switch(yyjson_get_subtype(val)) {
        case YYJSON_SUBTYPE_UINT:
            return PyLong_FromUnsignedLongLong(yyjson_get_uint(val));
        case YYJSON_SUBTYPE_SINT:
            return PyLong_FromLongLong(yyjson_get_sint(val));
        case YYJSON_SUBTYPE_REAL:
            return PyFloat_FromDouble(yyjson_get_real(val));
        }
    case YYJSON_TYPE_ARR: {
        PyObject *arr = PyList_New(yyjson_arr_size(val));
        if(!arr) {
            return NULL;
        }
        yyjson_val *oval;
        PyObject *pval;
        yyjson_arr_iter it = {0};
        yyjson_arr_iter_init(val, &it);
        size_t idx = 0;
        while((oval = yyjson_arr_iter_next(&it))) {
            pval = conv_element(oval);
            if(!pval) {
                return NULL;
            }
            PyList_SET_ITEM(arr, idx++, pval);
        }
        return arr;
    }
    case YYJSON_TYPE_OBJ: {
        PyObject *dict = PyDict_New();
        if(!dict) { return NULL; }
        yyjson_val *okey, *oval;
        PyObject *pkey, *pval;
        yyjson_obj_iter it = {0};
        yyjson_obj_iter_init(val, &it);
        while((okey = yyjson_obj_iter_next(&it))) {
            oval = yyjson_obj_iter_get_val(okey);
            pkey = conv_str(yyjson_get_str(okey), yyjson_get_len(okey));
            if(!pkey) {
                return NULL;
            }
            pval = conv_element(oval);
            if(!pval) {
                Py_DECREF(pkey);
                return NULL;
            }

            if(PyDict_SetItem(dict, pkey, pval) == -1) {
                return NULL;
            }

            Py_DECREF(pkey);
            Py_DECREF(pval);
        }
        return dict;
    }
    }
    PyErr_SetString(PyExc_TypeError, "Unknown type found.");
    return NULL;
}

static yyjson_mut_val *conv_mapping(struct xxjson_state *st, yyjson_mut_doc *doc, PyObject *obj) {
    yyjson_mut_val *val = yyjson_mut_obj(doc);

    PyObject *items = PyMapping_Items(obj);
    if(!items) return NULL;

    Py_ssize_t len = PyList_Size(items);
    
    for(Py_ssize_t i = 0; i < len; i++) {
        PyObject *item = PyList_GetItem(items, i);
        PyObject *k = PyTuple_GetItem(item, 0);
        PyObject *v = PyTuple_GetItem(item, 1);

        if(!PyUnicode_Check(k)) {
            PyErr_SetString(PyExc_TypeError, "all keys must be str");
            Py_DECREF(items);
            return NULL;
        }

        const char *s = PyUnicode_AsUTF8(k);
        if(!s) {
            Py_DECREF(items);
            return NULL;
        }
        yyjson_mut_val *jval = conv_object(st, doc, v);
        if(!val) {
            Py_DECREF(items);
            return NULL;
        }

        yyjson_mut_obj_add(val, yyjson_mut_str(doc, s), jval);
    }
    Py_DECREF(items);
    return val;
}
static yyjson_mut_val *conv_seq(struct xxjson_state *st, yyjson_mut_doc *doc, PyObject *obj) {
    yyjson_mut_val *val = yyjson_mut_arr(doc);
    Py_ssize_t n = PySequence_Length(obj);
    for(Py_ssize_t i = 0; i < n; i++) {
        PyObject *item = PySequence_GetItem(obj, i);
        if(!item) return NULL;
        yyjson_mut_val *jval = conv_object(st, doc, item);
        Py_DECREF(item);
        if(!jval) return NULL;
        yyjson_mut_arr_append(val, jval);
    }
    return val;
}


yyjson_mut_val *conv_object(struct xxjson_state *st, yyjson_mut_doc *doc, PyObject *obj) {

    if(obj == Py_None) {
        return yyjson_mut_null(doc);
    }

    if(PyBool_Check(obj)) {
        return obj == Py_True ? yyjson_mut_true(doc) : yyjson_mut_false(doc);
    }

    if(PyLong_Check(obj)) {
        return yyjson_mut_int(doc, PyLong_AsLongLong(obj));
    }

    if(PyFloat_Check(obj)) {
        return yyjson_mut_real(doc, PyFloat_AsDouble(obj));
    }

    if(PyObject_TypeCheck(obj, st->capi->DateTimeType)) {
        PyObject *iso = PyObject_CallMethod(obj, "isoformat", NULL);
        if (!iso)
            return NULL; // propagate exception

        const char *cstr = PyUnicode_AsUTF8(iso);
        if (!cstr) {
            Py_DECREF(iso);
            return NULL;
        }
        yyjson_mut_val *s = yyjson_mut_str(doc, cstr);
        Py_DECREF(iso);
        return s;
    }

    if(PyUnicode_Check(obj)) {
        const char *s = PyUnicode_AsUTF8(obj);
        return yyjson_mut_str(doc, s);
    }

    if(PyDict_Check(obj)) {
        return conv_mapping(st, doc, obj);
    }

    if(PyList_Check(obj) || PyTuple_Check(obj)) {
        return conv_seq(st, doc, obj);
    }

    if(PyObject_HasAttrString(obj, "items")) {
        return conv_mapping(st, doc, obj);
    }

    if(PySequence_Check(obj)) {
        return conv_seq(st, doc, obj);
    }

    PyErr_SetString(PyExc_TypeError, "Unsupported type for JSON serialization");
    return NULL;
}
