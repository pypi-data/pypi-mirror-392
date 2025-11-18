/* Generated code for Python module 'pydantic$annotated_handlers'
 * created by Nuitka version 2.8.4
 *
 * This code is in part copyright 2025 Kay Hayen.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include "nuitka/prelude.h"

#include "nuitka/unfreezing.h"

#include "__helpers.h"

/* The "module_pydantic$annotated_handlers" is a Python object pointer of module type.
 *
 * Note: For full compatibility with CPython, every module variable access
 * needs to go through it except for cases where the module cannot possibly
 * have changed in the mean time.
 */

PyObject *module_pydantic$annotated_handlers;
PyDictObject *moduledict_pydantic$annotated_handlers;

/* The declarations of module constants used, if any. */
static PyObject *mod_consts[60];
#ifndef __NUITKA_NO_ASSERT__
static Py_hash_t mod_consts_hash[60];
#endif

static PyObject *module_filename_obj = NULL;

/* Indicator if this modules private constants were created yet. */
static bool constants_created = false;

/* Function to create module private constants. */
static void createModuleConstants(PyThreadState *tstate) {
    if (constants_created == false) {
        loadConstantsBlob(tstate, &mod_consts[0], UN_TRANSLATE("pydantic.annotated_handlers"));
        constants_created = true;

#ifndef __NUITKA_NO_ASSERT__
        for (int i = 0; i < 60; i++) {
            mod_consts_hash[i] = DEEP_HASH(tstate, mod_consts[i]);
        }
#endif
    }
}

// We want to be able to initialize the "__main__" constants in any case.
#if 0
void createMainModuleConstants(PyThreadState *tstate) {
    createModuleConstants(tstate);
}
#endif

/* Function to verify module private constants for non-corruption. */
#ifndef __NUITKA_NO_ASSERT__
void checkModuleConstants_pydantic$annotated_handlers(PyThreadState *tstate) {
    // The module may not have been used at all, then ignore this.
    if (constants_created == false) return;

    for (int i = 0; i < 60; i++) {
        assert(mod_consts_hash[i] == DEEP_HASH(tstate, mod_consts[i]));
        CHECK_OBJECT_DEEP(mod_consts[i]);
    }
}
#endif

// Helper to preserving module variables for Python3.11+
#if 1
#if PYTHON_VERSION >= 0x3c0
NUITKA_MAY_BE_UNUSED static uint32_t _Nuitka_PyDictKeys_GetVersionForCurrentState(PyInterpreterState *interp, PyDictKeysObject *dk)
{
    if (dk->dk_version != 0) {
        return dk->dk_version;
    }
    uint32_t result = interp->dict_state.next_keys_version++;
    dk->dk_version = result;
    return result;
}
#elif PYTHON_VERSION >= 0x3b0
static uint32_t _Nuitka_next_dict_keys_version = 2;

NUITKA_MAY_BE_UNUSED static uint32_t _Nuitka_PyDictKeys_GetVersionForCurrentState(PyDictKeysObject *dk)
{
    if (dk->dk_version != 0) {
        return dk->dk_version;
    }
    uint32_t result = _Nuitka_next_dict_keys_version++;
    dk->dk_version = result;
    return result;
}
#endif
#endif

// Accessors to module variables.
static PyObject *module_var_accessor_pydantic$$36$annotated_handlers$__spec__(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_pydantic$annotated_handlers->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_pydantic$annotated_handlers->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)mod_consts[59]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_pydantic$annotated_handlers->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[59]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[59], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[59]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[59], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)mod_consts[59]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)mod_consts[59]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[59]);
    }

    return result;
}


#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
// The module code objects.
static PyCodeObject *code_objects_d81db0ae0b9946400d6e7fec6a683fa5;
static PyCodeObject *code_objects_f4259ffbf1fc4b0da96b8fa3567922fc;
static PyCodeObject *code_objects_a6fbdb7809831a4b3a627c6bde1e565b;
static PyCodeObject *code_objects_f26d514f32254f66cde63b67cee5c2e3;
static PyCodeObject *code_objects_fd0fad0a104eeca544b8f0f04488ab53;
static PyCodeObject *code_objects_9703b3273adacd60dfe80dcb0823378b;
static PyCodeObject *code_objects_3abb596d5c186dda53a1b68ac796fae3;
static PyCodeObject *code_objects_be5b32f380b3caf9680b09f282f865fa;
static PyCodeObject *code_objects_4b38cae7057ace1964e7d228ee0c98d7;
static PyCodeObject *code_objects_93589928529aaca845087fa6eeb974c4;

static void createModuleCodeObjects(void) {
    module_filename_obj = MAKE_RELATIVE_PATH(mod_consts[50]); CHECK_OBJECT(module_filename_obj);
    code_objects_d81db0ae0b9946400d6e7fec6a683fa5 = MAKE_CODE_OBJECT(module_filename_obj, 1, CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[51], mod_consts[51], NULL, NULL, 0, 0, 0);
    code_objects_f4259ffbf1fc4b0da96b8fa3567922fc = MAKE_CODE_OBJECT(module_filename_obj, 66, CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[37], mod_consts[37], mod_consts[52], NULL, 0, 0, 0);
    code_objects_a6fbdb7809831a4b3a627c6bde1e565b = MAKE_CODE_OBJECT(module_filename_obj, 24, CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[25], mod_consts[25], mod_consts[52], NULL, 0, 0, 0);
    code_objects_f26d514f32254f66cde63b67cee5c2e3 = MAKE_CODE_OBJECT(module_filename_obj, 69, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[31], mod_consts[39], mod_consts[53], NULL, 2, 0, 2);
    code_objects_fd0fad0a104eeca544b8f0f04488ab53 = MAKE_CODE_OBJECT(module_filename_obj, 33, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[31], mod_consts[32], mod_consts[54], NULL, 2, 0, 2);
    code_objects_9703b3273adacd60dfe80dcb0823378b = MAKE_CODE_OBJECT(module_filename_obj, 120, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[48], mod_consts[49], mod_consts[55], NULL, 1, 0, 0);
    code_objects_3abb596d5c186dda53a1b68ac796fae3 = MAKE_CODE_OBJECT(module_filename_obj, 116, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[45], mod_consts[46], mod_consts[55], NULL, 1, 0, 0);
    code_objects_be5b32f380b3caf9680b09f282f865fa = MAKE_CODE_OBJECT(module_filename_obj, 84, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[40], mod_consts[41], mod_consts[53], NULL, 2, 0, 2);
    code_objects_4b38cae7057ace1964e7d228ee0c98d7 = MAKE_CODE_OBJECT(module_filename_obj, 99, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[34], mod_consts[43], mod_consts[56], NULL, 2, 0, 2);
    code_objects_93589928529aaca845087fa6eeb974c4 = MAKE_CODE_OBJECT(module_filename_obj, 49, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[34], mod_consts[35], mod_consts[57], NULL, 2, 0, 2);
}
#endif

// The module function declarations.
static PyObject *MAKE_FUNCTION_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__(PyThreadState *tstate, PyObject *annotations);


static PyObject *MAKE_FUNCTION_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema(PyThreadState *tstate, PyObject *annotations);


static PyObject *MAKE_FUNCTION_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__(PyThreadState *tstate, PyObject *annotations);


static PyObject *MAKE_FUNCTION_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema(PyThreadState *tstate, PyObject *annotations);


static PyObject *MAKE_FUNCTION_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema(PyThreadState *tstate, PyObject *annotations);


static PyObject *MAKE_FUNCTION_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name(PyThreadState *tstate, PyObject *annotations);


static PyObject *MAKE_FUNCTION_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace(PyThreadState *tstate, PyObject *annotations);


// The module function definitions.
static PyObject *impl_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_core_schema = python_pars[1];
    struct Nuitka_FrameObject *frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__ = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__)) {
        Py_XDECREF(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__ == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__ = MAKE_FUNCTION_FRAME(tstate, code_objects_fd0fad0a104eeca544b8f0f04488ab53, module_pydantic$annotated_handlers, sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__->m_type_description == NULL);
    frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__ = cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__);
    assert(Py_REFCNT(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__) == 2);

    // Framed code:
    {
        PyObject *tmp_raise_type_1;
        tmp_raise_type_1 = PyExc_NotImplementedError;
        exception_state.exception_type = tmp_raise_type_1;
        Py_INCREF(tmp_raise_type_1);
        exception_lineno = 47;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);
        type_description_1 = "oo";
        goto frame_exception_exit_1;
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__,
        type_description_1,
        par_self,
        par_core_schema
    );


    // Release cached frame if used for exception.
    if (frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__ == cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__);
        cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__ = NULL;
    }

    assertFrameObject(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_OBJECT(par_core_schema);
    Py_DECREF(par_core_schema);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

}


static PyObject *impl_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_maybe_ref_json_schema = python_pars[1];
    struct Nuitka_FrameObject *frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema)) {
        Py_XDECREF(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema = MAKE_FUNCTION_FRAME(tstate, code_objects_93589928529aaca845087fa6eeb974c4, module_pydantic$annotated_handlers, sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema->m_type_description == NULL);
    frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema = cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema);
    assert(Py_REFCNT(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema) == 2);

    // Framed code:
    {
        PyObject *tmp_raise_type_1;
        tmp_raise_type_1 = PyExc_NotImplementedError;
        exception_state.exception_type = tmp_raise_type_1;
        Py_INCREF(tmp_raise_type_1);
        exception_lineno = 63;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);
        type_description_1 = "oo";
        goto frame_exception_exit_1;
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema,
        type_description_1,
        par_self,
        par_maybe_ref_json_schema
    );


    // Release cached frame if used for exception.
    if (frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema == cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema);
        cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema = NULL;
    }

    assertFrameObject(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_OBJECT(par_maybe_ref_json_schema);
    Py_DECREF(par_maybe_ref_json_schema);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

}


static PyObject *impl_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_source_type = python_pars[1];
    struct Nuitka_FrameObject *frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__ = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__)) {
        Py_XDECREF(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__ == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__ = MAKE_FUNCTION_FRAME(tstate, code_objects_f26d514f32254f66cde63b67cee5c2e3, module_pydantic$annotated_handlers, sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__->m_type_description == NULL);
    frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__ = cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__);
    assert(Py_REFCNT(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__) == 2);

    // Framed code:
    {
        PyObject *tmp_raise_type_1;
        tmp_raise_type_1 = PyExc_NotImplementedError;
        exception_state.exception_type = tmp_raise_type_1;
        Py_INCREF(tmp_raise_type_1);
        exception_lineno = 82;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);
        type_description_1 = "oo";
        goto frame_exception_exit_1;
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__,
        type_description_1,
        par_self,
        par_source_type
    );


    // Release cached frame if used for exception.
    if (frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__ == cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__);
        cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__ = NULL;
    }

    assertFrameObject(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_OBJECT(par_source_type);
    Py_DECREF(par_source_type);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

}


static PyObject *impl_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_source_type = python_pars[1];
    struct Nuitka_FrameObject *frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema)) {
        Py_XDECREF(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema = MAKE_FUNCTION_FRAME(tstate, code_objects_be5b32f380b3caf9680b09f282f865fa, module_pydantic$annotated_handlers, sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema->m_type_description == NULL);
    frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema = cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema);
    assert(Py_REFCNT(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema) == 2);

    // Framed code:
    {
        PyObject *tmp_raise_type_1;
        tmp_raise_type_1 = PyExc_NotImplementedError;
        exception_state.exception_type = tmp_raise_type_1;
        Py_INCREF(tmp_raise_type_1);
        exception_lineno = 97;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);
        type_description_1 = "oo";
        goto frame_exception_exit_1;
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema,
        type_description_1,
        par_self,
        par_source_type
    );


    // Release cached frame if used for exception.
    if (frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema == cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema);
        cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema = NULL;
    }

    assertFrameObject(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_OBJECT(par_source_type);
    Py_DECREF(par_source_type);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

}


static PyObject *impl_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_maybe_ref_schema = python_pars[1];
    struct Nuitka_FrameObject *frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema)) {
        Py_XDECREF(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema = MAKE_FUNCTION_FRAME(tstate, code_objects_4b38cae7057ace1964e7d228ee0c98d7, module_pydantic$annotated_handlers, sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema->m_type_description == NULL);
    frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema = cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema);
    assert(Py_REFCNT(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema) == 2);

    // Framed code:
    {
        PyObject *tmp_raise_type_1;
        tmp_raise_type_1 = PyExc_NotImplementedError;
        exception_state.exception_type = tmp_raise_type_1;
        Py_INCREF(tmp_raise_type_1);
        exception_lineno = 113;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);
        type_description_1 = "oo";
        goto frame_exception_exit_1;
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema,
        type_description_1,
        par_self,
        par_maybe_ref_schema
    );


    // Release cached frame if used for exception.
    if (frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema == cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema);
        cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema = NULL;
    }

    assertFrameObject(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_OBJECT(par_maybe_ref_schema);
    Py_DECREF(par_maybe_ref_schema);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

}


static PyObject *impl_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name)) {
        Py_XDECREF(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name = MAKE_FUNCTION_FRAME(tstate, code_objects_3abb596d5c186dda53a1b68ac796fae3, module_pydantic$annotated_handlers, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name->m_type_description == NULL);
    frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name = cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name);
    assert(Py_REFCNT(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name) == 2);

    // Framed code:
    {
        PyObject *tmp_raise_type_1;
        tmp_raise_type_1 = PyExc_NotImplementedError;
        exception_state.exception_type = tmp_raise_type_1;
        Py_INCREF(tmp_raise_type_1);
        exception_lineno = 118;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);
        type_description_1 = "o";
        goto frame_exception_exit_1;
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name,
        type_description_1,
        par_self
    );


    // Release cached frame if used for exception.
    if (frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name == cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name);
        cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name = NULL;
    }

    assertFrameObject(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

}


static PyObject *impl_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace)) {
        Py_XDECREF(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace = MAKE_FUNCTION_FRAME(tstate, code_objects_9703b3273adacd60dfe80dcb0823378b, module_pydantic$annotated_handlers, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace->m_type_description == NULL);
    frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace = cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace);
    assert(Py_REFCNT(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace) == 2);

    // Framed code:
    {
        PyObject *tmp_raise_type_1;
        tmp_raise_type_1 = PyExc_NotImplementedError;
        exception_state.exception_type = tmp_raise_type_1;
        Py_INCREF(tmp_raise_type_1);
        exception_lineno = 122;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);
        type_description_1 = "o";
        goto frame_exception_exit_1;
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace,
        type_description_1,
        par_self
    );


    // Release cached frame if used for exception.
    if (frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace == cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace);
        cache_frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace = NULL;
    }

    assertFrameObject(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

}



static PyObject *MAKE_FUNCTION_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__(PyThreadState *tstate, PyObject *annotations) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__,
        mod_consts[31],
#if PYTHON_VERSION >= 0x300
        mod_consts[32],
#endif
        code_objects_fd0fad0a104eeca544b8f0f04488ab53,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_pydantic$annotated_handlers,
        mod_consts[0],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema(PyThreadState *tstate, PyObject *annotations) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema,
        mod_consts[34],
#if PYTHON_VERSION >= 0x300
        mod_consts[35],
#endif
        code_objects_93589928529aaca845087fa6eeb974c4,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_pydantic$annotated_handlers,
        mod_consts[1],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__(PyThreadState *tstate, PyObject *annotations) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__,
        mod_consts[31],
#if PYTHON_VERSION >= 0x300
        mod_consts[39],
#endif
        code_objects_f26d514f32254f66cde63b67cee5c2e3,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_pydantic$annotated_handlers,
        mod_consts[2],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema(PyThreadState *tstate, PyObject *annotations) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema,
        mod_consts[40],
#if PYTHON_VERSION >= 0x300
        mod_consts[41],
#endif
        code_objects_be5b32f380b3caf9680b09f282f865fa,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_pydantic$annotated_handlers,
        mod_consts[3],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema(PyThreadState *tstate, PyObject *annotations) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema,
        mod_consts[34],
#if PYTHON_VERSION >= 0x300
        mod_consts[43],
#endif
        code_objects_4b38cae7057ace1964e7d228ee0c98d7,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_pydantic$annotated_handlers,
        mod_consts[4],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name(PyThreadState *tstate, PyObject *annotations) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name,
        mod_consts[45],
#if PYTHON_VERSION >= 0x300
        mod_consts[46],
#endif
        code_objects_3abb596d5c186dda53a1b68ac796fae3,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_pydantic$annotated_handlers,
        mod_consts[5],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace(PyThreadState *tstate, PyObject *annotations) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace,
        mod_consts[48],
#if PYTHON_VERSION >= 0x300
        mod_consts[49],
#endif
        code_objects_9703b3273adacd60dfe80dcb0823378b,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_pydantic$annotated_handlers,
        mod_consts[6],
        NULL,
        0
    );


    return (PyObject *)result;
}


extern void _initCompiledCellType();
extern void _initCompiledGeneratorType();
extern void _initCompiledFunctionType();
extern void _initCompiledMethodType();
extern void _initCompiledFrameType();

extern PyTypeObject Nuitka_Loader_Type;

#ifdef _NUITKA_PLUGIN_DILL_ENABLED
// Provide a way to create find a function via its C code and create it back
// in another process, useful for multiprocessing extensions like dill
extern void registerDillPluginTables(PyThreadState *tstate, char const *module_name, PyMethodDef *reduce_compiled_function, PyMethodDef *create_compiled_function);

static function_impl_code const function_table_pydantic$annotated_handlers[] = {
    impl_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__,
    impl_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema,
    impl_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__,
    impl_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema,
    impl_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema,
    impl_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name,
    impl_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace,
    NULL
};

static PyObject *_reduce_compiled_function(PyObject *self, PyObject *args, PyObject *kwds) {
    PyObject *func;

    if (!PyArg_ParseTuple(args, "O:reduce_compiled_function", &func, NULL)) {
        return NULL;
    }

    if (Nuitka_Function_Check(func) == false) {
        PyThreadState *tstate = PyThreadState_GET();

        SET_CURRENT_EXCEPTION_TYPE0_STR(tstate, PyExc_TypeError, "not a compiled function");
        return NULL;
    }

    struct Nuitka_FunctionObject *function = (struct Nuitka_FunctionObject *)func;

    return Nuitka_Function_GetFunctionState(function, function_table_pydantic$annotated_handlers);
}

static PyMethodDef _method_def_reduce_compiled_function = {"reduce_compiled_function", (PyCFunction)_reduce_compiled_function,
                                                           METH_VARARGS, NULL};


static PyObject *_create_compiled_function(PyObject *self, PyObject *args, PyObject *kwds) {
    CHECK_OBJECT_DEEP(args);

    PyObject *function_index;
    PyObject *code_object_desc;
    PyObject *defaults;
    PyObject *kw_defaults;
    PyObject *doc;
    PyObject *constant_return_value;
    PyObject *function_qualname;
    PyObject *closure;
    PyObject *annotations;
    PyObject *func_dict;

    if (!PyArg_ParseTuple(args, "OOOOOOOOOO:create_compiled_function", &function_index, &code_object_desc, &defaults, &kw_defaults, &doc, &constant_return_value, &function_qualname, &closure, &annotations, &func_dict, NULL)) {
        return NULL;
    }

    return (PyObject *)Nuitka_Function_CreateFunctionViaCodeIndex(
        module_pydantic$annotated_handlers,
        function_qualname,
        function_index,
        code_object_desc,
        constant_return_value,
        defaults,
        kw_defaults,
        doc,
        closure,
        annotations,
        func_dict,
        function_table_pydantic$annotated_handlers,
        sizeof(function_table_pydantic$annotated_handlers) / sizeof(function_impl_code)
    );
}

static PyMethodDef _method_def_create_compiled_function = {
    "create_compiled_function",
    (PyCFunction)_create_compiled_function,
    METH_VARARGS, NULL
};


#endif

// Actual name might be different when loaded as a package.
#if _NUITKA_MODULE_MODE && 0
static char const *module_full_name = "pydantic.annotated_handlers";
#endif

// Internal entry point for module code.
PyObject *modulecode_pydantic$annotated_handlers(PyThreadState *tstate, PyObject *module, struct Nuitka_MetaPathBasedLoaderEntry const *loader_entry) {
    // Report entry to PGO.
    PGO_onModuleEntered("pydantic$annotated_handlers");

    // Store the module for future use.
    module_pydantic$annotated_handlers = module;

    moduledict_pydantic$annotated_handlers = MODULE_DICT(module_pydantic$annotated_handlers);

    // Modules can be loaded again in case of errors, avoid the init being done again.
    static bool init_done = false;

    if (init_done == false) {
#if _NUITKA_MODULE_MODE && 0
        // In case of an extension module loaded into a process, we need to call
        // initialization here because that's the first and potentially only time
        // we are going called.
#if PYTHON_VERSION > 0x350 && !defined(_NUITKA_EXPERIMENTAL_DISABLE_ALLOCATORS)
        initNuitkaAllocators();
#endif
        // Initialize the constant values used.
        _initBuiltinModule(tstate);

        PyObject *real_module_name = PyObject_GetAttrString(module, "__name__");
        CHECK_OBJECT(real_module_name);
        module_full_name = strdup(Nuitka_String_AsString(real_module_name));

        createGlobalConstants(tstate, real_module_name);

        /* Initialize the compiled types of Nuitka. */
        _initCompiledCellType();
        _initCompiledGeneratorType();
        _initCompiledFunctionType();
        _initCompiledMethodType();
        _initCompiledFrameType();

        _initSlotCompare();
#if PYTHON_VERSION >= 0x270
        _initSlotIterNext();
#endif

        patchTypeComparison();

        // Enable meta path based loader if not already done.
#ifdef _NUITKA_TRACE
        PRINT_STRING("pydantic$annotated_handlers: Calling setupMetaPathBasedLoader().\n");
#endif
        setupMetaPathBasedLoader(tstate);
#if 0 >= 0
#ifdef _NUITKA_TRACE
        PRINT_STRING("pydantic$annotated_handlers: Calling updateMetaPathBasedLoaderModuleRoot().\n");
#endif
        updateMetaPathBasedLoaderModuleRoot(module_full_name);
#endif


#if PYTHON_VERSION >= 0x300
        patchInspectModule(tstate);
#endif

#endif

        /* The constants only used by this module are created now. */
        NUITKA_PRINT_TRACE("pydantic$annotated_handlers: Calling createModuleConstants().\n");
        createModuleConstants(tstate);

#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
        createModuleCodeObjects();
#endif
        init_done = true;
    }

#if _NUITKA_MODULE_MODE && 0
    PyObject *pre_load = IMPORT_EMBEDDED_MODULE(tstate, "pydantic.annotated_handlers" "-preLoad");
    if (pre_load == NULL) {
        return NULL;
    }
#endif

    // PRINT_STRING("in initpydantic$annotated_handlers\n");

#ifdef _NUITKA_PLUGIN_DILL_ENABLED
    {
        char const *module_name_c;
        if (loader_entry != NULL) {
            module_name_c = loader_entry->name;
        } else {
            PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)const_str_plain___name__);
            module_name_c = Nuitka_String_AsString(module_name);
        }

        registerDillPluginTables(tstate, module_name_c, &_method_def_reduce_compiled_function, &_method_def_create_compiled_function);
    }
#endif

    // Set "__compiled__" to what version information we have.
    UPDATE_STRING_DICT0(
        moduledict_pydantic$annotated_handlers,
        (Nuitka_StringObject *)const_str_plain___compiled__,
        Nuitka_dunder_compiled_value
    );

    // Update "__package__" value to what it ought to be.
    {
#if 0
        UPDATE_STRING_DICT0(
            moduledict_pydantic$annotated_handlers,
            (Nuitka_StringObject *)const_str_plain___package__,
            mod_consts[58]
        );
#elif 0
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)const_str_plain___name__);

        UPDATE_STRING_DICT0(
            moduledict_pydantic$annotated_handlers,
            (Nuitka_StringObject *)const_str_plain___package__,
            module_name
        );
#else

#if PYTHON_VERSION < 0x300
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)const_str_plain___name__);
        char const *module_name_cstr = PyString_AS_STRING(module_name);

        char const *last_dot = strrchr(module_name_cstr, '.');

        if (last_dot != NULL) {
            UPDATE_STRING_DICT1(
                moduledict_pydantic$annotated_handlers,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyString_FromStringAndSize(module_name_cstr, last_dot - module_name_cstr)
            );
        }
#else
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)const_str_plain___name__);
        Py_ssize_t dot_index = PyUnicode_Find(module_name, const_str_dot, 0, PyUnicode_GetLength(module_name), -1);

        if (dot_index != -1) {
            UPDATE_STRING_DICT1(
                moduledict_pydantic$annotated_handlers,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyUnicode_Substring(module_name, 0, dot_index)
            );
        }
#endif
#endif
    }

    CHECK_OBJECT(module_pydantic$annotated_handlers);

    // For deep importing of a module we need to have "__builtins__", so we set
    // it ourselves in the same way than CPython does. Note: This must be done
    // before the frame object is allocated, or else it may fail.

    if (GET_STRING_DICT_VALUE(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)const_str_plain___builtins__) == NULL) {
        PyObject *value = (PyObject *)builtin_module;

        // Check if main module, not a dict then but the module itself.
#if _NUITKA_MODULE_MODE || !0
        value = PyModule_GetDict(value);
#endif

        UPDATE_STRING_DICT0(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)const_str_plain___builtins__, value);
    }

    PyObject *module_loader = Nuitka_Loader_New(loader_entry);
    UPDATE_STRING_DICT0(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)const_str_plain___loader__, module_loader);

#if PYTHON_VERSION >= 0x300
// Set the "__spec__" value

#if 0
    // Main modules just get "None" as spec.
    UPDATE_STRING_DICT0(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)const_str_plain___spec__, Py_None);
#else
    // Other modules get a "ModuleSpec" from the standard mechanism.
    {
        PyObject *bootstrap_module = getImportLibBootstrapModule();
        CHECK_OBJECT(bootstrap_module);

        PyObject *_spec_from_module = PyObject_GetAttrString(bootstrap_module, "_spec_from_module");
        CHECK_OBJECT(_spec_from_module);

        PyObject *spec_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, _spec_from_module, module_pydantic$annotated_handlers);
        Py_DECREF(_spec_from_module);

        // We can assume this to never fail, or else we are in trouble anyway.
        // CHECK_OBJECT(spec_value);

        if (spec_value == NULL) {
            PyErr_PrintEx(0);
            abort();
        }

        // Mark the execution in the "__spec__" value.
        SET_ATTRIBUTE(tstate, spec_value, const_str_plain__initializing, Py_True);

#if _NUITKA_MODULE_MODE && 0 && 0 >= 0
        // Set our loader object in the "__spec__" value.
        SET_ATTRIBUTE(tstate, spec_value, const_str_plain_loader, module_loader);
#endif

        UPDATE_STRING_DICT1(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)const_str_plain___spec__, spec_value);
    }
#endif
#endif

    // Temp variables if any
    PyObject *outline_0_var___class__ = NULL;
    PyObject *outline_1_var___class__ = NULL;
    PyObject *tmp_class_creation_1__class_decl_dict = NULL;
    PyObject *tmp_class_creation_1__prepared = NULL;
    PyObject *tmp_class_creation_2__class_decl_dict = NULL;
    PyObject *tmp_class_creation_2__prepared = NULL;
    PyObject *tmp_import_from_1__module = NULL;
    struct Nuitka_FrameObject *frame_frame_pydantic$annotated_handlers;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    bool tmp_result;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;
    PyObject *locals_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_24 = NULL;
    PyObject *tmp_dictset_value;
    struct Nuitka_FrameObject *frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_2;
    NUITKA_MAY_BE_UNUSED char const *type_description_2 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_2;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_2;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_3;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_3;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_4;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_4;
    PyObject *locals_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_66 = NULL;
    struct Nuitka_FrameObject *frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_3;
    NUITKA_MAY_BE_UNUSED char const *type_description_3 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_5;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_5;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_6;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_6;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_7;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_7;

    // Module init code if any


    // Module code.
    {
        PyObject *tmp_assign_source_1;
        tmp_assign_source_1 = mod_consts[7];
        UPDATE_STRING_DICT0(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)mod_consts[8], tmp_assign_source_1);
    }
    {
        PyObject *tmp_assign_source_2;
        tmp_assign_source_2 = module_filename_obj;
        UPDATE_STRING_DICT0(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)mod_consts[9], tmp_assign_source_2);
    }
    frame_frame_pydantic$annotated_handlers = MAKE_MODULE_FRAME(code_objects_d81db0ae0b9946400d6e7fec6a683fa5, module_pydantic$annotated_handlers);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_pydantic$annotated_handlers);
    assert(Py_REFCNT(frame_frame_pydantic$annotated_handlers) == 2);

    // Framed code:
    {
        PyObject *tmp_assattr_value_1;
        PyObject *tmp_assattr_target_1;
        tmp_assattr_value_1 = module_filename_obj;
        tmp_assattr_target_1 = module_var_accessor_pydantic$$36$annotated_handlers$__spec__(tstate);
        assert(!(tmp_assattr_target_1 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_1, mod_consts[10], tmp_assattr_value_1);
        if (tmp_result == false) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 1;

            goto frame_exception_exit_1;
        }
    }
    {
        PyObject *tmp_assattr_value_2;
        PyObject *tmp_assattr_target_2;
        tmp_assattr_value_2 = Py_True;
        tmp_assattr_target_2 = module_var_accessor_pydantic$$36$annotated_handlers$__spec__(tstate);
        assert(!(tmp_assattr_target_2 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_2, mod_consts[11], tmp_assattr_value_2);
        if (tmp_result == false) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 1;

            goto frame_exception_exit_1;
        }
    }
    {
        PyObject *tmp_assign_source_3;
        tmp_assign_source_3 = Py_None;
        UPDATE_STRING_DICT0(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)mod_consts[12], tmp_assign_source_3);
    }
    {
        PyObject *tmp_assign_source_4;
        {
            PyObject *hard_module = IMPORT_HARD___FUTURE__();
            tmp_assign_source_4 = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[13]);
        }
        assert(!(tmp_assign_source_4 == NULL));
        UPDATE_STRING_DICT1(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)mod_consts[14], tmp_assign_source_4);
    }
    {
        PyObject *tmp_assign_source_5;
        tmp_assign_source_5 = IMPORT_HARD_TYPING();
        assert(!(tmp_assign_source_5 == NULL));
        assert(tmp_import_from_1__module == NULL);
        Py_INCREF(tmp_assign_source_5);
        tmp_import_from_1__module = tmp_assign_source_5;
    }
    {
        PyObject *tmp_assign_source_6;
        tmp_assign_source_6 = Py_False;
        UPDATE_STRING_DICT0(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)mod_consts[15], tmp_assign_source_6);
    }
    // Tried code:
    {
        PyObject *tmp_assign_source_7;
        PyObject *tmp_import_name_from_1;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_1 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_1)) {
            tmp_assign_source_7 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_1,
                (PyObject *)moduledict_pydantic$annotated_handlers,
                mod_consts[16],
                const_int_0
            );
        } else {
            tmp_assign_source_7 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_1, mod_consts[16]);
        }

        if (tmp_assign_source_7 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 5;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)mod_consts[16], tmp_assign_source_7);
    }
    {
        PyObject *tmp_assign_source_8;
        PyObject *tmp_import_name_from_2;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_2 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_2)) {
            tmp_assign_source_8 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_2,
                (PyObject *)moduledict_pydantic$annotated_handlers,
                mod_consts[17],
                const_int_0
            );
        } else {
            tmp_assign_source_8 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_2, mod_consts[17]);
        }

        if (tmp_assign_source_8 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 5;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)mod_consts[17], tmp_assign_source_8);
    }
    goto try_end_1;
    // Exception handler code:
    try_except_handler_1:;
    exception_keeper_lineno_1 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_1 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    CHECK_OBJECT(tmp_import_from_1__module);
    Py_DECREF(tmp_import_from_1__module);
    tmp_import_from_1__module = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_1;
    exception_lineno = exception_keeper_lineno_1;

    goto frame_exception_exit_1;
    // End of try:
    try_end_1:;
    CHECK_OBJECT(tmp_import_from_1__module);
    Py_DECREF(tmp_import_from_1__module);
    tmp_import_from_1__module = NULL;
    {
        PyObject *tmp_assign_source_9;
        frame_frame_pydantic$annotated_handlers->m_frame.f_lineno = 7;
        tmp_assign_source_9 = IMPORT_MODULE_FIXED(tstate, mod_consts[18], mod_consts[18]);
        if (tmp_assign_source_9 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 7;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)mod_consts[19], tmp_assign_source_9);
    }
    {
        PyObject *tmp_assign_source_10;
        tmp_assign_source_10 = mod_consts[20];
        UPDATE_STRING_DICT0(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)mod_consts[21], tmp_assign_source_10);
    }
    {
        PyObject *tmp_assign_source_11;
        tmp_assign_source_11 = MAKE_DICT_EMPTY(tstate);
        assert(tmp_class_creation_1__class_decl_dict == NULL);
        tmp_class_creation_1__class_decl_dict = tmp_assign_source_11;
    }
    {
        PyObject *tmp_assign_source_12;
        tmp_assign_source_12 = MAKE_DICT_EMPTY(tstate);
        assert(tmp_class_creation_1__prepared == NULL);
        tmp_class_creation_1__prepared = tmp_assign_source_12;
    }
    // Tried code:
    {
        PyObject *tmp_assign_source_13;
        {
            PyObject *tmp_set_locals_1;
            CHECK_OBJECT(tmp_class_creation_1__prepared);
            tmp_set_locals_1 = tmp_class_creation_1__prepared;
            locals_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_24 = tmp_set_locals_1;
            Py_INCREF(tmp_set_locals_1);
        }
        tmp_dictset_value = mod_consts[22];
        tmp_result = DICT_SET_ITEM(locals_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_24, mod_consts[23], tmp_dictset_value);
        assert(!(tmp_result == false));
        tmp_dictset_value = mod_consts[24];
        tmp_result = DICT_SET_ITEM(locals_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_24, mod_consts[8], tmp_dictset_value);
        assert(!(tmp_result == false));
        tmp_dictset_value = mod_consts[25];
        tmp_result = DICT_SET_ITEM(locals_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_24, mod_consts[26], tmp_dictset_value);
        assert(!(tmp_result == false));
        tmp_dictset_value = MAKE_DICT_EMPTY(tstate);
        tmp_result = DICT_SET_ITEM(locals_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_24, mod_consts[27], tmp_dictset_value);
        Py_DECREF(tmp_dictset_value);
        assert(!(tmp_result == false));
        // Tried code:
        // Tried code:
        frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_2 = MAKE_CLASS_FRAME(tstate, code_objects_a6fbdb7809831a4b3a627c6bde1e565b, module_pydantic$annotated_handlers, NULL, sizeof(void *));

        // Push the new frame as the currently active one, and we should be exclusively
        // owning it.
        pushFrameStackCompiledFrame(tstate, frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_2);
        assert(Py_REFCNT(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_2) == 2);

        // Framed code:
        {
            PyObject *tmp_ass_subvalue_1;
            PyObject *tmp_ass_subscribed_1;
            PyObject *tmp_ass_subscript_1;
            tmp_ass_subvalue_1 = mod_consts[28];
            tmp_ass_subscribed_1 = DICT_GET_ITEM0(tstate, locals_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_24, mod_consts[27]);

            if (unlikely(tmp_ass_subscribed_1 == NULL && CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate))) {

            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[27]);

                exception_lineno = 31;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }

            if (tmp_ass_subscribed_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 31;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
            tmp_ass_subscript_1 = mod_consts[29];
            tmp_result = SET_SUBSCRIPT(tstate, tmp_ass_subscribed_1, tmp_ass_subscript_1, tmp_ass_subvalue_1);
            if (tmp_result == false) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 31;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
        }


        // Put the previous frame back on top.
        popFrameStack(tstate);

        goto frame_no_exception_1;
        frame_exception_exit_2:


        {
            PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
            if (exception_tb == NULL) {
                exception_tb = MAKE_TRACEBACK(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_2, exception_lineno);
                SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
            } else if (exception_tb->tb_frame != &frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_2->m_frame) {
                exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_2, exception_lineno);
                SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
            }
        }

        // Attaches locals to frame if any.
        Nuitka_Frame_AttachLocals(
            frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_2,
            type_description_2,
            outline_0_var___class__
        );



        assertFrameObject(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_2);

        // Put the previous frame back on top.
        popFrameStack(tstate);

        // Return the error.
        goto nested_frame_exit_1;
        frame_no_exception_1:;
        goto skip_nested_handling_1;
        nested_frame_exit_1:;

        goto try_except_handler_4;
        skip_nested_handling_1:;
        {
            PyObject *tmp_annotations_1;
            tmp_annotations_1 = DICT_COPY(tstate, mod_consts[30]);


            tmp_dictset_value = MAKE_FUNCTION_pydantic$annotated_handlers$$36$$$36$$$36$function__1___call__(tstate, tmp_annotations_1);

            tmp_result = DICT_SET_ITEM(locals_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_24, mod_consts[31], tmp_dictset_value);
            Py_DECREF(tmp_dictset_value);
            assert(!(tmp_result == false));
        }
        {
            PyObject *tmp_annotations_2;
            tmp_annotations_2 = DICT_COPY(tstate, mod_consts[33]);


            tmp_dictset_value = MAKE_FUNCTION_pydantic$annotated_handlers$$36$$$36$$$36$function__2_resolve_ref_schema(tstate, tmp_annotations_2);

            tmp_result = DICT_SET_ITEM(locals_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_24, mod_consts[34], tmp_dictset_value);
            Py_DECREF(tmp_dictset_value);
            assert(!(tmp_result == false));
        }
        {
            PyObject *tmp_assign_source_14;
            PyObject *tmp_called_value_1;
            PyObject *tmp_args_value_1;
            PyObject *tmp_tuple_element_1;
            PyObject *tmp_kwargs_value_1;
            tmp_called_value_1 = (PyObject *)&PyType_Type;
            tmp_tuple_element_1 = mod_consts[25];
            tmp_args_value_1 = MAKE_TUPLE_EMPTY(tstate, 3);
            PyTuple_SET_ITEM0(tmp_args_value_1, 0, tmp_tuple_element_1);
            tmp_tuple_element_1 = const_tuple_empty;
            PyTuple_SET_ITEM0(tmp_args_value_1, 1, tmp_tuple_element_1);
            tmp_tuple_element_1 = locals_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_24;
            PyTuple_SET_ITEM0(tmp_args_value_1, 2, tmp_tuple_element_1);
            CHECK_OBJECT(tmp_class_creation_1__class_decl_dict);
            tmp_kwargs_value_1 = tmp_class_creation_1__class_decl_dict;
            frame_frame_pydantic$annotated_handlers->m_frame.f_lineno = 24;
            tmp_assign_source_14 = CALL_FUNCTION(tstate, tmp_called_value_1, tmp_args_value_1, tmp_kwargs_value_1);
            Py_DECREF(tmp_args_value_1);
            if (tmp_assign_source_14 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 24;

                goto try_except_handler_4;
            }
            assert(outline_0_var___class__ == NULL);
            outline_0_var___class__ = tmp_assign_source_14;
        }
        CHECK_OBJECT(outline_0_var___class__);
        tmp_assign_source_13 = outline_0_var___class__;
        Py_INCREF(tmp_assign_source_13);
        goto try_return_handler_4;
        NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
        return NULL;
        // Return handler code:
        try_return_handler_4:;
        Py_DECREF(locals_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_24);
        locals_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_24 = NULL;
        goto try_return_handler_3;
        // Exception handler code:
        try_except_handler_4:;
        exception_keeper_lineno_2 = exception_lineno;
        exception_lineno = 0;
        exception_keeper_name_2 = exception_state;
        INIT_ERROR_OCCURRED_STATE(&exception_state);

        Py_DECREF(locals_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_24);
        locals_pydantic$annotated_handlers$$36$$$36$$$36$class__1_GetJsonSchemaHandler_24 = NULL;
        // Re-raise.
        exception_state = exception_keeper_name_2;
        exception_lineno = exception_keeper_lineno_2;

        goto try_except_handler_3;
        // End of try:
        NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
        return NULL;
        // Return handler code:
        try_return_handler_3:;
        CHECK_OBJECT(outline_0_var___class__);
        Py_DECREF(outline_0_var___class__);
        outline_0_var___class__ = NULL;
        goto outline_result_1;
        // Exception handler code:
        try_except_handler_3:;
        exception_keeper_lineno_3 = exception_lineno;
        exception_lineno = 0;
        exception_keeper_name_3 = exception_state;
        INIT_ERROR_OCCURRED_STATE(&exception_state);

        // Re-raise.
        exception_state = exception_keeper_name_3;
        exception_lineno = exception_keeper_lineno_3;

        goto outline_exception_1;
        // End of try:
        NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
        return NULL;
        outline_exception_1:;
        exception_lineno = 24;
        goto try_except_handler_2;
        outline_result_1:;
        UPDATE_STRING_DICT1(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)mod_consts[25], tmp_assign_source_13);
    }
    goto try_end_2;
    // Exception handler code:
    try_except_handler_2:;
    exception_keeper_lineno_4 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_4 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    CHECK_OBJECT(tmp_class_creation_1__class_decl_dict);
    Py_DECREF(tmp_class_creation_1__class_decl_dict);
    tmp_class_creation_1__class_decl_dict = NULL;
    CHECK_OBJECT(tmp_class_creation_1__prepared);
    Py_DECREF(tmp_class_creation_1__prepared);
    tmp_class_creation_1__prepared = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_4;
    exception_lineno = exception_keeper_lineno_4;

    goto frame_exception_exit_1;
    // End of try:
    try_end_2:;
    CHECK_OBJECT(tmp_class_creation_1__class_decl_dict);
    Py_DECREF(tmp_class_creation_1__class_decl_dict);
    tmp_class_creation_1__class_decl_dict = NULL;
    CHECK_OBJECT(tmp_class_creation_1__prepared);
    Py_DECREF(tmp_class_creation_1__prepared);
    tmp_class_creation_1__prepared = NULL;
    {
        PyObject *tmp_assign_source_15;
        tmp_assign_source_15 = MAKE_DICT_EMPTY(tstate);
        assert(tmp_class_creation_2__class_decl_dict == NULL);
        tmp_class_creation_2__class_decl_dict = tmp_assign_source_15;
    }
    {
        PyObject *tmp_assign_source_16;
        tmp_assign_source_16 = MAKE_DICT_EMPTY(tstate);
        assert(tmp_class_creation_2__prepared == NULL);
        tmp_class_creation_2__prepared = tmp_assign_source_16;
    }
    // Tried code:
    {
        PyObject *tmp_assign_source_17;
        {
            PyObject *tmp_set_locals_2;
            CHECK_OBJECT(tmp_class_creation_2__prepared);
            tmp_set_locals_2 = tmp_class_creation_2__prepared;
            locals_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_66 = tmp_set_locals_2;
            Py_INCREF(tmp_set_locals_2);
        }
        tmp_dictset_value = mod_consts[22];
        tmp_result = DICT_SET_ITEM(locals_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_66, mod_consts[23], tmp_dictset_value);
        assert(!(tmp_result == false));
        tmp_dictset_value = mod_consts[36];
        tmp_result = DICT_SET_ITEM(locals_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_66, mod_consts[8], tmp_dictset_value);
        assert(!(tmp_result == false));
        tmp_dictset_value = mod_consts[37];
        tmp_result = DICT_SET_ITEM(locals_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_66, mod_consts[26], tmp_dictset_value);
        assert(!(tmp_result == false));
        {
            PyObject *tmp_annotations_3;
            tmp_annotations_3 = DICT_COPY(tstate, mod_consts[38]);


            tmp_dictset_value = MAKE_FUNCTION_pydantic$annotated_handlers$$36$$$36$$$36$function__3___call__(tstate, tmp_annotations_3);

            tmp_result = DICT_SET_ITEM(locals_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_66, mod_consts[31], tmp_dictset_value);
            Py_DECREF(tmp_dictset_value);
            assert(!(tmp_result == false));
        }
        {
            PyObject *tmp_annotations_4;
            tmp_annotations_4 = DICT_COPY(tstate, mod_consts[38]);


            tmp_dictset_value = MAKE_FUNCTION_pydantic$annotated_handlers$$36$$$36$$$36$function__4_generate_schema(tstate, tmp_annotations_4);

            tmp_result = DICT_SET_ITEM(locals_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_66, mod_consts[40], tmp_dictset_value);
            Py_DECREF(tmp_dictset_value);
            assert(!(tmp_result == false));
        }
        {
            PyObject *tmp_annotations_5;
            tmp_annotations_5 = DICT_COPY(tstate, mod_consts[42]);


            tmp_dictset_value = MAKE_FUNCTION_pydantic$annotated_handlers$$36$$$36$$$36$function__5_resolve_ref_schema(tstate, tmp_annotations_5);

            tmp_result = DICT_SET_ITEM(locals_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_66, mod_consts[34], tmp_dictset_value);
            Py_DECREF(tmp_dictset_value);
            assert(!(tmp_result == false));
        }
        // Tried code:
        // Tried code:
        frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_3 = MAKE_CLASS_FRAME(tstate, code_objects_f4259ffbf1fc4b0da96b8fa3567922fc, module_pydantic$annotated_handlers, NULL, sizeof(void *));

        // Push the new frame as the currently active one, and we should be exclusively
        // owning it.
        pushFrameStackCompiledFrame(tstate, frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_3);
        assert(Py_REFCNT(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_3) == 2);

        // Framed code:
        {
            PyObject *tmp_called_value_2;
            PyObject *tmp_args_element_value_1;
            PyObject *tmp_annotations_6;
            tmp_called_value_2 = (PyObject *)&PyProperty_Type;
            tmp_annotations_6 = DICT_COPY(tstate, mod_consts[44]);


            tmp_args_element_value_1 = MAKE_FUNCTION_pydantic$annotated_handlers$$36$$$36$$$36$function__6_field_name(tstate, tmp_annotations_6);

            frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_3->m_frame.f_lineno = 115;
            tmp_dictset_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_2, tmp_args_element_value_1);
            Py_DECREF(tmp_args_element_value_1);
            if (tmp_dictset_value == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 115;
                type_description_2 = "o";
                goto frame_exception_exit_3;
            }
            tmp_result = DICT_SET_ITEM(locals_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_66, mod_consts[45], tmp_dictset_value);
            Py_DECREF(tmp_dictset_value);
            if (tmp_result == false) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 116;
                type_description_2 = "o";
                goto frame_exception_exit_3;
            }
        }


        // Put the previous frame back on top.
        popFrameStack(tstate);

        goto frame_no_exception_2;
        frame_exception_exit_3:


        {
            PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
            if (exception_tb == NULL) {
                exception_tb = MAKE_TRACEBACK(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_3, exception_lineno);
                SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
            } else if (exception_tb->tb_frame != &frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_3->m_frame) {
                exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_3, exception_lineno);
                SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
            }
        }

        // Attaches locals to frame if any.
        Nuitka_Frame_AttachLocals(
            frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_3,
            type_description_2,
            outline_1_var___class__
        );



        assertFrameObject(frame_frame_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_3);

        // Put the previous frame back on top.
        popFrameStack(tstate);

        // Return the error.
        goto nested_frame_exit_2;
        frame_no_exception_2:;
        goto skip_nested_handling_2;
        nested_frame_exit_2:;

        goto try_except_handler_7;
        skip_nested_handling_2:;
        {
            PyObject *tmp_annotations_7;
            tmp_annotations_7 = DICT_COPY(tstate, mod_consts[47]);


            tmp_dictset_value = MAKE_FUNCTION_pydantic$annotated_handlers$$36$$$36$$$36$function__7__get_types_namespace(tstate, tmp_annotations_7);

            tmp_result = DICT_SET_ITEM(locals_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_66, mod_consts[48], tmp_dictset_value);
            Py_DECREF(tmp_dictset_value);
            assert(!(tmp_result == false));
        }
        {
            PyObject *tmp_assign_source_18;
            PyObject *tmp_called_value_3;
            PyObject *tmp_args_value_2;
            PyObject *tmp_tuple_element_2;
            PyObject *tmp_kwargs_value_2;
            tmp_called_value_3 = (PyObject *)&PyType_Type;
            tmp_tuple_element_2 = mod_consts[37];
            tmp_args_value_2 = MAKE_TUPLE_EMPTY(tstate, 3);
            PyTuple_SET_ITEM0(tmp_args_value_2, 0, tmp_tuple_element_2);
            tmp_tuple_element_2 = const_tuple_empty;
            PyTuple_SET_ITEM0(tmp_args_value_2, 1, tmp_tuple_element_2);
            tmp_tuple_element_2 = locals_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_66;
            PyTuple_SET_ITEM0(tmp_args_value_2, 2, tmp_tuple_element_2);
            CHECK_OBJECT(tmp_class_creation_2__class_decl_dict);
            tmp_kwargs_value_2 = tmp_class_creation_2__class_decl_dict;
            frame_frame_pydantic$annotated_handlers->m_frame.f_lineno = 66;
            tmp_assign_source_18 = CALL_FUNCTION(tstate, tmp_called_value_3, tmp_args_value_2, tmp_kwargs_value_2);
            Py_DECREF(tmp_args_value_2);
            if (tmp_assign_source_18 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 66;

                goto try_except_handler_7;
            }
            assert(outline_1_var___class__ == NULL);
            outline_1_var___class__ = tmp_assign_source_18;
        }
        CHECK_OBJECT(outline_1_var___class__);
        tmp_assign_source_17 = outline_1_var___class__;
        Py_INCREF(tmp_assign_source_17);
        goto try_return_handler_7;
        NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
        return NULL;
        // Return handler code:
        try_return_handler_7:;
        Py_DECREF(locals_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_66);
        locals_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_66 = NULL;
        goto try_return_handler_6;
        // Exception handler code:
        try_except_handler_7:;
        exception_keeper_lineno_5 = exception_lineno;
        exception_lineno = 0;
        exception_keeper_name_5 = exception_state;
        INIT_ERROR_OCCURRED_STATE(&exception_state);

        Py_DECREF(locals_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_66);
        locals_pydantic$annotated_handlers$$36$$$36$$$36$class__2_GetCoreSchemaHandler_66 = NULL;
        // Re-raise.
        exception_state = exception_keeper_name_5;
        exception_lineno = exception_keeper_lineno_5;

        goto try_except_handler_6;
        // End of try:
        NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
        return NULL;
        // Return handler code:
        try_return_handler_6:;
        CHECK_OBJECT(outline_1_var___class__);
        Py_DECREF(outline_1_var___class__);
        outline_1_var___class__ = NULL;
        goto outline_result_2;
        // Exception handler code:
        try_except_handler_6:;
        exception_keeper_lineno_6 = exception_lineno;
        exception_lineno = 0;
        exception_keeper_name_6 = exception_state;
        INIT_ERROR_OCCURRED_STATE(&exception_state);

        // Re-raise.
        exception_state = exception_keeper_name_6;
        exception_lineno = exception_keeper_lineno_6;

        goto outline_exception_2;
        // End of try:
        NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
        return NULL;
        outline_exception_2:;
        exception_lineno = 66;
        goto try_except_handler_5;
        outline_result_2:;
        UPDATE_STRING_DICT1(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)mod_consts[37], tmp_assign_source_17);
    }
    goto try_end_3;
    // Exception handler code:
    try_except_handler_5:;
    exception_keeper_lineno_7 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_7 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    CHECK_OBJECT(tmp_class_creation_2__class_decl_dict);
    Py_DECREF(tmp_class_creation_2__class_decl_dict);
    tmp_class_creation_2__class_decl_dict = NULL;
    CHECK_OBJECT(tmp_class_creation_2__prepared);
    Py_DECREF(tmp_class_creation_2__prepared);
    tmp_class_creation_2__prepared = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_7;
    exception_lineno = exception_keeper_lineno_7;

    goto frame_exception_exit_1;
    // End of try:
    try_end_3:;


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_3;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_pydantic$annotated_handlers, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_pydantic$annotated_handlers->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_pydantic$annotated_handlers, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }



    assertFrameObject(frame_frame_pydantic$annotated_handlers);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto module_exception_exit;
    frame_no_exception_3:;
    CHECK_OBJECT(tmp_class_creation_2__class_decl_dict);
    Py_DECREF(tmp_class_creation_2__class_decl_dict);
    tmp_class_creation_2__class_decl_dict = NULL;
    CHECK_OBJECT(tmp_class_creation_2__prepared);
    Py_DECREF(tmp_class_creation_2__prepared);
    tmp_class_creation_2__prepared = NULL;

    // Report to PGO about leaving the module without error.
    PGO_onModuleExit("pydantic$annotated_handlers", false);

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *post_load = IMPORT_EMBEDDED_MODULE(tstate, "pydantic.annotated_handlers" "-postLoad");
        if (post_load == NULL) {
            return NULL;
        }
    }
#endif

    Py_INCREF(module_pydantic$annotated_handlers);
    return module_pydantic$annotated_handlers;
    module_exception_exit:

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_pydantic$annotated_handlers, (Nuitka_StringObject *)const_str_plain___name__);

        if (module_name != NULL) {
            Nuitka_DelModule(tstate, module_name);
        }
    }
#endif
    PGO_onModuleExit("pydantic$annotated_handlers", false);

    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);
    return NULL;
}
