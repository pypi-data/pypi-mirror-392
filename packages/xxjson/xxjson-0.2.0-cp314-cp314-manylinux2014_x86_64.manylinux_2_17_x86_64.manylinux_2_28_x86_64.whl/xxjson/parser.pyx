# cython: freethreading_compatible = True
from libc.stdint cimport uint32_t, uint8_t, int64_t, uint64_t
from libc.stddef cimport size_t
from cpython.object cimport PyObject
from cpython.list cimport PyList_Append, PyList_New
from cpython.dict cimport PyDict_SetItem, PyDict_New
from cpython.mem cimport PyMem_Malloc, PyMem_Free, PyMem_Realloc
from cpython.unicode cimport PyUnicode_FromStringAndSize
from cpython.ref cimport Py_DECREF, Py_ssize_t
from decimal import Decimal


cdef extern from "yyjson.h":
    ctypedef union yyjson_val_uni:
        uint64_t u64
        int64_t i64
        double f64
        const char *str
        void *ptr
        size_t ofs

    ctypedef struct yyjson_doc

    ctypedef struct yyjson_val:
        uint64_t tag
        yyjson_val_uni uni

    ctypedef struct yyjson_arr_iter:
        size_t idx
        size_t max
        yyjson_val *cur

    ctypedef struct yyjson_obj_iter:
        size_t idx
        size_t max
        yyjson_val *cur
        yyjson_val *obj

    ctypedef struct yyjson_alc:
        void *(*malloc)(void *ctx, size_t size)
        void *(*realloc)(void *ctx, void *ptr, size_t old_size, size_t size)
        void (*free)(void *ctx, void *ptr)

    ctypedef struct yyjson_read_err:
        unsigned int code
        unsigned int line
        unsigned int column
        const char *msg

    # none type invalid
    cdef const uint8_t YYJSON_TYPE_NONE = 0
    # Raw string type, no subtype.
    cdef const uint8_t YYJSON_TYPE_RAW = 1
    # Null type: `null` literal, no subtype.
    cdef const uint8_t YYJSON_TYPE_NULL = 2
    # Boolean type, subtype: TRUE, FALSE. */
    cdef const uint8_t YYJSON_TYPE_BOOL = 3
    # Number type, subtype: UINT, SINT, REAL. */
    cdef const uint8_t YYJSON_TYPE_NUM = 4
    # String type, subtype: NONE, NOESC. */
    cdef const uint8_t YYJSON_TYPE_STR = 5
    # Array type, no subtype. */
    cdef const uint8_t YYJSON_TYPE_ARR = 6
    # Object type, no subtype. */
    cdef const uint8_t YYJSON_TYPE_OBJ = 7

    # No subtype.
    cdef const uint8_t YYJSON_SUBTYPE_NONE = (0 << 3)
    # False subtype: `false` literal. */
    cdef const uint8_t YYJSON_SUBTYPE_FALSE = (0 << 3)
    # True subtype: `true` literal. */
    cdef const uint8_t YYJSON_SUBTYPE_TRUE = (1 << 3)
    # Unsigned integer subtype: `uint64_t`. */
    cdef const uint8_t YYJSON_SUBTYPE_UINT = (0 << 3)
    # Signed integer subtype: `int64_t`. */
    cdef const uint8_t YYJSON_SUBTYPE_SINT = (1 << 3)
    # Real number subtype: `double`. */
    cdef const uint8_t YYJSON_SUBTYPE_REAL = (2 << 3)

    cdef const uint8_t YYJSON_TYPE_MASK = 0x07
    cdef const uint8_t YYJSON_SUBTYPE_MASK = 0x18

    yyjson_doc *yyjson_read_opts(char *dat, size_t len, uint32_t flg, const yyjson_alc *alc_ptr, yyjson_read_err *err)
    yyjson_val *yyjson_doc_get_root(yyjson_doc *doc)
    void yyjson_doc_free(yyjson_doc *doc)

    yyjson_arr_iter yyjson_arr_iter_with(yyjson_val *arr)
    yyjson_val *yyjson_arr_iter_next(yyjson_arr_iter *iter)	

    yyjson_obj_iter yyjson_obj_iter_with(yyjson_val *obj)
    yyjson_val *yyjson_obj_iter_next(yyjson_obj_iter *iter)
    yyjson_val *yyjson_obj_iter_get_val(yyjson_val *key)

    int64_t yyjson_get_sint(yyjson_val *val)
    uint64_t yyjson_get_uint(yyjson_val *val)
    double yyjson_get_real(yyjson_val *val)
    const char *yyjson_get_str(yyjson_val *val)
    size_t yyjson_get_len(yyjson_val *val)

cdef object conv_scalar(yyjson_val *v):
    cdef int t = v.tag & YYJSON_TYPE_MASK
    cdef int st = v.tag & YYJSON_SUBTYPE_MASK
    
    if t == YYJSON_TYPE_BOOL:
        if st == YYJSON_SUBTYPE_FALSE:
            return False
        elif st == YYJSON_SUBTYPE_TRUE:
            return True
    elif t == YYJSON_TYPE_NULL:
        return None
    elif t == YYJSON_TYPE_NUM:
        if st == YYJSON_SUBTYPE_REAL:
            return yyjson_get_real(v)
        elif st == YYJSON_SUBTYPE_SINT:
            return yyjson_get_sint(v)
        elif st == YYJSON_SUBTYPE_UINT:
            return yyjson_get_uint(v)
    elif t == YYJSON_TYPE_STR:
        return yyjson_get_str(v)
    return None
            
cdef struct Frame:
    unsigned char kind
    yyjson_val *v
    yyjson_arr_iter arr_iter
    yyjson_obj_iter obj_iter
    object out
    
cpdef object loads(bytes data, int flags = 0):
    cdef yyjson_doc *doc
    cdef yyjson_read_err err
    cdef yyjson_val *root
    cdef Frame *stack
    cdef Frame *new_stack
    cdef object py_val
    cdef object child_obj
    cdef object result_obj
    cdef ssize_t sp = -1
    cdef ssize_t cap = 256
    cdef int t
    cdef size_t key_len
    cdef object key_obj

    doc = yyjson_read_opts(data, len(data), flags & ~(1<<0), NULL, &err)
    if doc == NULL:
        raise ValueError(f"yyjson error {err.code}: {err.msg.decode()}")

    stack = <Frame *>PyMem_Malloc(cap * sizeof(Frame))
    if stack == NULL:
        raise MemoryError()
    
    root = yyjson_doc_get_root(doc)

    t = root.tag & YYJSON_TYPE_MASK
    if t == YYJSON_TYPE_OBJ:
        result_obj = PyDict_New()
        if result_obj is None:
            PyMem_Free(stack)
            yyjson_doc_free(doc)
            raise MemoryError()
        sp += 1
        stack[sp].kind = YYJSON_TYPE_OBJ
        stack[sp].v = root
        stack[sp].obj_iter = yyjson_obj_iter_with(root)
        stack[sp].out = <PyObject *>result_obj
    elif t == YYJSON_TYPE_ARR:
        result_obj = PyList_New(0)
        if result_obj is None:
            PyMem_Free(stack)
            yyjson_doc_free(doc)
            raise MemoryError()
        sp += 1
        stack[sp].kind = YYJSON_TYPE_ARR
        stack[sp].v = root
        stack[sp].arr_iter = yyjson_arr_iter_with(root)
        stack[sp].out = <PyObject *>result_obj
    else:
        PyMem_Free(stack)
        yyjson_doc_free(doc)
        raise ValueError("JSON should begin with an array or object")

    cdef Frame *f
    cdef yyjson_val *k
    cdef yyjson_val *v

    try:
        while sp >= 0:
            f = &stack[sp]
            if f.kind == YYJSON_TYPE_ARR:
                v = yyjson_arr_iter_next(&f.arr_iter)
                if v == NULL:
                    sp -= 1
                    continue
                if (v.tag & YYJSON_TYPE_MASK) < YYJSON_TYPE_ARR:
                    py_val = conv_scalar(v)
                    PyList_Append(<object>f.out, py_val)
                    continue
                if sp + 1 >= cap:
                    cap *= 2
                    new_stack = <Frame *>PyMem_Realloc(stack, cap * sizeof(Frame))
                    if new_stack == NULL:
                        raise MemoryError()
                    stack = new_stack
                    f = &stack[sp]
                sp += 1
                if (v.tag & YYJSON_TYPE_MASK) == YYJSON_TYPE_ARR:
                    child_obj = PyList_New(0)
                    if child_obj is None:
                        raise MemoryError()
                    stack[sp].kind = YYJSON_TYPE_ARR
                    stack[sp].arr_iter = yyjson_arr_iter_with(v)
                else:
                    child_obj = PyDict_New()
                    if child_obj is None:
                        raise MemoryError()
                    stack[sp].kind = YYJSON_TYPE_OBJ
                    stack[sp].obj_iter = yyjson_obj_iter_with(v)
                PyList_Append(<object>f.out, child_obj)
                stack[sp].v = v
                stack[sp].out = <PyObject *>child_obj
            else:
                k = yyjson_obj_iter_next(&f.obj_iter)
                if k == NULL:
                    sp -= 1
                    continue
                key_len = yyjson_get_len(k)
                key_obj = PyUnicode_FromStringAndSize(yyjson_get_str(k), <Py_ssize_t>key_len)
                if key_obj is None:
                    raise MemoryError()
                v = yyjson_obj_iter_get_val(k)
                if (v.tag & YYJSON_TYPE_MASK) < YYJSON_TYPE_ARR:
                    py_val = conv_scalar(v)
                    PyDict_SetItem(<object>f.out, key_obj, py_val)
                    Py_DECREF(<PyObject *>key_obj)
                    continue
                if sp + 1 >= cap:
                    cap *= 2
                    new_stack = <Frame *>PyMem_Realloc(stack, cap * sizeof(Frame))
                    if new_stack == NULL:
                        Py_DECREF(<PyObject *>key_obj)
                        raise MemoryError()
                    stack = new_stack
                    f = &stack[sp]
                sp += 1
                if (v.tag & YYJSON_TYPE_MASK) == YYJSON_TYPE_ARR:
                    child_obj = PyList_New(0)
                    if child_obj is None:
                        Py_DECREF(<PyObject *>key_obj)
                        raise MemoryError()
                    stack[sp].kind = YYJSON_TYPE_ARR
                    stack[sp].arr_iter = yyjson_arr_iter_with(v)
                else:
                    child_obj = PyDict_New()
                    if child_obj is None:
                        Py_DECREF(<PyObject *>key_obj)
                        raise MemoryError()
                    stack[sp].kind = YYJSON_TYPE_OBJ
                    stack[sp].obj_iter = yyjson_obj_iter_with(v)
                PyDict_SetItem(<object>f.out, key_obj, child_obj)
                Py_DECREF(<PyObject *>key_obj)
                stack[sp].v = v
                stack[sp].out = <PyObject *>child_obj
        return result_obj
    finally:
        if stack != NULL:
            PyMem_Free(stack)
        if doc != NULL:
            yyjson_doc_free(doc)
