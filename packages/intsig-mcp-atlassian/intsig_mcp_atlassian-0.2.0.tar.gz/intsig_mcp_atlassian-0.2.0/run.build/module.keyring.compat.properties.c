/* Generated code for Python module 'keyring$compat$properties'
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

/* The "module_keyring$compat$properties" is a Python object pointer of module type.
 *
 * Note: For full compatibility with CPython, every module variable access
 * needs to go through it except for cases where the module cannot possibly
 * have changed in the mean time.
 */

PyObject *module_keyring$compat$properties;
PyDictObject *moduledict_keyring$compat$properties;

/* The declarations of module constants used, if any. */
static PyObject *mod_consts[59];
#ifndef __NUITKA_NO_ASSERT__
static Py_hash_t mod_consts_hash[59];
#endif

static PyObject *module_filename_obj = NULL;

/* Indicator if this modules private constants were created yet. */
static bool constants_created = false;

/* Function to create module private constants. */
static void createModuleConstants(PyThreadState *tstate) {
    if (constants_created == false) {
        loadConstantsBlob(tstate, &mod_consts[0], UN_TRANSLATE("keyring.compat.properties"));
        constants_created = true;

#ifndef __NUITKA_NO_ASSERT__
        for (int i = 0; i < 59; i++) {
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
void checkModuleConstants_keyring$compat$properties(PyThreadState *tstate) {
    // The module may not have been used at all, then ignore this.
    if (constants_created == false) return;

    for (int i = 0; i < 59; i++) {
        assert(mod_consts_hash[i] == DEEP_HASH(tstate, mod_consts[i]));
        CHECK_OBJECT_DEEP(mod_consts[i]);
    }
}
#endif

// Helper to preserving module variables for Python3.11+
#if 2
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
static PyObject *module_var_accessor_keyring$$36$compat$$36$properties$__spec__(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_keyring$compat$properties->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_keyring$compat$properties->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_keyring$compat$properties, (Nuitka_StringObject *)mod_consts[58]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_keyring$compat$properties->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[58]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[58], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[58]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[58], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_keyring$compat$properties, (Nuitka_StringObject *)mod_consts[58]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_keyring$compat$properties, (Nuitka_StringObject *)mod_consts[58]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[58]);
    }

    return result;
}

static PyObject *module_var_accessor_keyring$$36$compat$$36$properties$classproperty(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_keyring$compat$properties->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_keyring$compat$properties->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_keyring$compat$properties, (Nuitka_StringObject *)mod_consts[5]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_keyring$compat$properties->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[5]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[5], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[5]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[5], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_keyring$compat$properties, (Nuitka_StringObject *)mod_consts[5]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_keyring$compat$properties, (Nuitka_StringObject *)mod_consts[5]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[5]);
    }

    return result;
}


#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
// The module code objects.
static PyCodeObject *code_objects_af0ed0f3fe635d3316f54240ceb861d8;
static PyCodeObject *code_objects_4f79b28ff871290619a8150704663417;
static PyCodeObject *code_objects_92da0d1eb7f4ca4d5b6f1b5cdf3803f0;
static PyCodeObject *code_objects_5542c59c5218e44ff56b298a5846d397;
static PyCodeObject *code_objects_4fde9e08e32946118eac2bfaa4f7dd53;
static PyCodeObject *code_objects_141a5838a173a6b378f83501274d2076;
static PyCodeObject *code_objects_0e343abd4150458a2bdcb87479f52e6d;
static PyCodeObject *code_objects_cbce1dea3c2a7b6a7668db59f6ee7775;
static PyCodeObject *code_objects_e845ce3226ae1279ca9cfe39835bf794;
static PyCodeObject *code_objects_88f4ba6c2716a1cfb0fdd90977a2f3c2;
static PyCodeObject *code_objects_7e718ecaef63b307d53ffdbe737750e5;

static void createModuleCodeObjects(void) {
    module_filename_obj = MAKE_RELATIVE_PATH(mod_consts[46]); CHECK_OBJECT(module_filename_obj);
    code_objects_af0ed0f3fe635d3316f54240ceb861d8 = MAKE_CODE_OBJECT(module_filename_obj, 1, CO_NOFREE, mod_consts[47], mod_consts[47], NULL, NULL, 0, 0, 0);
    code_objects_4f79b28ff871290619a8150704663417 = MAKE_CODE_OBJECT(module_filename_obj, 137, CO_NOFREE, mod_consts[14], mod_consts[38], mod_consts[48], NULL, 0, 0, 0);
    code_objects_92da0d1eb7f4ca4d5b6f1b5cdf3803f0 = MAKE_CODE_OBJECT(module_filename_obj, 28, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[12], mod_consts[30], mod_consts[49], NULL, 3, 0, 0);
    code_objects_5542c59c5218e44ff56b298a5846d397 = MAKE_CODE_OBJECT(module_filename_obj, 149, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[12], mod_consts[42], mod_consts[50], NULL, 3, 0, 0);
    code_objects_4fde9e08e32946118eac2bfaa4f7dd53 = MAKE_CODE_OBJECT(module_filename_obj, 23, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[27], mod_consts[28], mod_consts[51], NULL, 2, 0, 0);
    code_objects_141a5838a173a6b378f83501274d2076 = MAKE_CODE_OBJECT(module_filename_obj, 144, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[27], mod_consts[41], mod_consts[52], NULL, 3, 0, 0);
    code_objects_0e343abd4150458a2bdcb87479f52e6d = MAKE_CODE_OBJECT(module_filename_obj, 152, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[6], mod_consts[43], mod_consts[53], NULL, 3, 0, 0);
    code_objects_cbce1dea3c2a7b6a7668db59f6ee7775 = MAKE_CODE_OBJECT(module_filename_obj, 138, CO_OPTIMIZED | CO_NEWLOCALS, mod_consts[8], mod_consts[39], mod_consts[54], mod_consts[48], 3, 0, 0);
    code_objects_e845ce3226ae1279ca9cfe39835bf794 = MAKE_CODE_OBJECT(module_filename_obj, 164, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[9], mod_consts[45], mod_consts[55], NULL, 2, 0, 0);
    code_objects_88f4ba6c2716a1cfb0fdd90977a2f3c2 = MAKE_CODE_OBJECT(module_filename_obj, 34, CO_NOFREE, mod_consts[5], mod_consts[5], mod_consts[48], NULL, 0, 0, 0);
    code_objects_7e718ecaef63b307d53ffdbe737750e5 = MAKE_CODE_OBJECT(module_filename_obj, 159, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[11], mod_consts[44], mod_consts[56], NULL, 2, 0, 0);
}
#endif

// The module function declarations.
NUITKA_CROSS_MODULE PyObject *impl___main__$$36$$$36$$$36$helper_function__mro_entries_conversion(PyThreadState *tstate, PyObject **python_pars);


static PyObject *MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__1___init__(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__2___get__(PyThreadState *tstate, PyObject *defaults);


static PyObject *MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__(PyThreadState *tstate, struct Nuitka_CellObject **closure);


static PyObject *MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__4___init__(PyThreadState *tstate, PyObject *defaults);


static PyObject *MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__5___get__(PyThreadState *tstate, PyObject *defaults);


static PyObject *MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__6___set__(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__7_setter(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method(PyThreadState *tstate);


// The module function definitions.
static PyObject *impl_keyring$compat$properties$$36$$$36$$$36$function__1___init__(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_fget = python_pars[1];
    struct Nuitka_FrameObject *frame_frame_keyring$compat$properties$$36$$$36$$$36$function__1___init__;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    int tmp_res;
    bool tmp_result;
    static struct Nuitka_FrameObject *cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__1___init__ = NULL;
    PyObject *tmp_return_value = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__1___init__)) {
        Py_XDECREF(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__1___init__);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__1___init__ == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__1___init__ = MAKE_FUNCTION_FRAME(tstate, code_objects_4fde9e08e32946118eac2bfaa4f7dd53, module_keyring$compat$properties, sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__1___init__->m_type_description == NULL);
    frame_frame_keyring$compat$properties$$36$$$36$$$36$function__1___init__ = cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__1___init__;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_keyring$compat$properties$$36$$$36$$$36$function__1___init__);
    assert(Py_REFCNT(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__1___init__) == 2);

    // Framed code:
    {
        bool tmp_condition_result_1;
        PyObject *tmp_cmp_expr_left_1;
        PyObject *tmp_cmp_expr_right_1;
        CHECK_OBJECT(par_fget);
        tmp_cmp_expr_left_1 = par_fget;
        tmp_cmp_expr_right_1 = Py_None;
        tmp_condition_result_1 = (tmp_cmp_expr_left_1 == tmp_cmp_expr_right_1) ? true : false;
        if (tmp_condition_result_1 != false) {
            goto branch_yes_1;
        } else {
            goto branch_no_1;
        }
    }
    branch_yes_1:;
    {
        PyObject *tmp_raise_type_1;
        PyObject *tmp_raise_value_1;
        tmp_raise_type_1 = PyExc_AssertionError;
        tmp_raise_value_1 = mod_consts[0];
        exception_state.exception_type = tmp_raise_type_1;
        Py_INCREF(tmp_raise_type_1);
        exception_state.exception_value = tmp_raise_value_1;
        Py_INCREF(tmp_raise_value_1);
        exception_lineno = 24;
        RAISE_EXCEPTION_WITH_TYPE_AND_VALUE(tstate, &exception_state);
        type_description_1 = "oo";
        goto frame_exception_exit_1;
    }
    branch_no_1:;
    {
        bool tmp_condition_result_2;
        PyObject *tmp_operand_value_1;
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        tmp_called_value_1 = LOOKUP_BUILTIN(mod_consts[1]);
        assert(tmp_called_value_1 != NULL);
        CHECK_OBJECT(par_fget);
        tmp_args_element_value_1 = par_fget;
        frame_frame_keyring$compat$properties$$36$$$36$$$36$function__1___init__->m_frame.f_lineno = 25;
        tmp_operand_value_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_1, tmp_args_element_value_1);
        if (tmp_operand_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 25;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        tmp_res = CHECK_IF_TRUE(tmp_operand_value_1);
        Py_DECREF(tmp_operand_value_1);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 25;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_2 = (tmp_res == 0) ? true : false;
        if (tmp_condition_result_2 != false) {
            goto branch_yes_2;
        } else {
            goto branch_no_2;
        }
    }
    branch_yes_2:;
    {
        PyObject *tmp_raise_type_2;
        PyObject *tmp_raise_value_2;
        tmp_raise_type_2 = PyExc_AssertionError;
        tmp_raise_value_2 = mod_consts[2];
        exception_state.exception_type = tmp_raise_type_2;
        Py_INCREF(tmp_raise_type_2);
        exception_state.exception_value = tmp_raise_value_2;
        Py_INCREF(tmp_raise_value_2);
        exception_lineno = 25;
        RAISE_EXCEPTION_WITH_TYPE_AND_VALUE(tstate, &exception_state);
        type_description_1 = "oo";
        goto frame_exception_exit_1;
    }
    branch_no_2:;
    {
        PyObject *tmp_assattr_value_1;
        PyObject *tmp_assattr_target_1;
        CHECK_OBJECT(par_fget);
        tmp_assattr_value_1 = par_fget;
        CHECK_OBJECT(par_self);
        tmp_assattr_target_1 = par_self;
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_1, mod_consts[3], tmp_assattr_value_1);
        if (tmp_result == false) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 26;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__1___init__, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_keyring$compat$properties$$36$$$36$$$36$function__1___init__->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_keyring$compat$properties$$36$$$36$$$36$function__1___init__, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_keyring$compat$properties$$36$$$36$$$36$function__1___init__,
        type_description_1,
        par_self,
        par_fget
    );


    // Release cached frame if used for exception.
    if (frame_frame_keyring$compat$properties$$36$$$36$$$36$function__1___init__ == cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__1___init__) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__1___init__);
        cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__1___init__ = NULL;
    }

    assertFrameObject(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__1___init__);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;
    tmp_return_value = Py_None;
    Py_INCREF(tmp_return_value);
    goto function_return_exit;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_OBJECT(par_fget);
    Py_DECREF(par_fget);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_OBJECT(par_fget);
    Py_DECREF(par_fget);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_keyring$compat$properties$$36$$$36$$$36$function__2___get__(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_obj = python_pars[1];
    PyObject *par_objtype = python_pars[2];
    PyObject *tmp_return_value = NULL;
    struct Nuitka_FrameObject *frame_frame_keyring$compat$properties$$36$$$36$$$36$function__2___get__;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__2___get__ = NULL;

    // Actual function body.
    {
        bool tmp_condition_result_1;
        PyObject *tmp_cmp_expr_left_1;
        PyObject *tmp_cmp_expr_right_1;
        CHECK_OBJECT(par_obj);
        tmp_cmp_expr_left_1 = par_obj;
        tmp_cmp_expr_right_1 = Py_None;
        tmp_condition_result_1 = (tmp_cmp_expr_left_1 == tmp_cmp_expr_right_1) ? true : false;
        if (tmp_condition_result_1 != false) {
            goto branch_yes_1;
        } else {
            goto branch_no_1;
        }
    }
    branch_yes_1:;
    CHECK_OBJECT(par_self);
    tmp_return_value = par_self;
    Py_INCREF(tmp_return_value);
    goto function_return_exit;
    branch_no_1:;
    if (isFrameUnusable(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__2___get__)) {
        Py_XDECREF(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__2___get__);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__2___get__ == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__2___get__ = MAKE_FUNCTION_FRAME(tstate, code_objects_92da0d1eb7f4ca4d5b6f1b5cdf3803f0, module_keyring$compat$properties, sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__2___get__->m_type_description == NULL);
    frame_frame_keyring$compat$properties$$36$$$36$$$36$function__2___get__ = cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__2___get__;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_keyring$compat$properties$$36$$$36$$$36$function__2___get__);
    assert(Py_REFCNT(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__2___get__) == 2);

    // Framed code:
    {
        PyObject *tmp_called_instance_1;
        PyObject *tmp_args_element_value_1;
        CHECK_OBJECT(par_self);
        tmp_called_instance_1 = par_self;
        CHECK_OBJECT(par_obj);
        tmp_args_element_value_1 = par_obj;
        frame_frame_keyring$compat$properties$$36$$$36$$$36$function__2___get__->m_frame.f_lineno = 31;
        tmp_return_value = CALL_METHOD_WITH_SINGLE_ARG(tstate, tmp_called_instance_1, mod_consts[3], tmp_args_element_value_1);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 31;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        goto frame_return_exit_1;
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_return_exit_1:

    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto function_return_exit;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__2___get__, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_keyring$compat$properties$$36$$$36$$$36$function__2___get__->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_keyring$compat$properties$$36$$$36$$$36$function__2___get__, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_keyring$compat$properties$$36$$$36$$$36$function__2___get__,
        type_description_1,
        par_self,
        par_obj,
        par_objtype
    );


    // Release cached frame if used for exception.
    if (frame_frame_keyring$compat$properties$$36$$$36$$$36$function__2___get__ == cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__2___get__) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__2___get__);
        cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__2___get__ = NULL;
    }

    assertFrameObject(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__2___get__);

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
    CHECK_OBJECT(par_obj);
    Py_DECREF(par_obj);
    CHECK_OBJECT(par_objtype);
    Py_DECREF(par_objtype);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_OBJECT(par_obj);
    Py_DECREF(par_obj);
    CHECK_OBJECT(par_objtype);
    Py_DECREF(par_objtype);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_key = python_pars[1];
    PyObject *par_value = python_pars[2];
    PyObject *var_obj = NULL;
    struct Nuitka_FrameObject *frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    PyObject *tmp_return_value = NULL;
    static struct Nuitka_FrameObject *cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__ = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;

    // Actual function body.
    // Tried code:
    if (isFrameUnusable(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__)) {
        Py_XDECREF(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__ == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__ = MAKE_FUNCTION_FRAME(tstate, code_objects_cbce1dea3c2a7b6a7668db59f6ee7775, module_keyring$compat$properties, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__->m_type_description == NULL);
    frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__ = cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__);
    assert(Py_REFCNT(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__) == 2);

    // Framed code:
    {
        PyObject *tmp_assign_source_1;
        PyObject *tmp_called_value_1;
        PyObject *tmp_expression_value_1;
        PyObject *tmp_expression_value_2;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_args_element_value_2;
        CHECK_OBJECT(par_self);
        tmp_expression_value_2 = par_self;
        tmp_expression_value_1 = LOOKUP_ATTRIBUTE_DICT_SLOT(tstate, tmp_expression_value_2);
        if (tmp_expression_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 139;
            type_description_1 = "ooooc";
            goto frame_exception_exit_1;
        }
        tmp_called_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[4]);
        Py_DECREF(tmp_expression_value_1);
        if (tmp_called_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 139;
            type_description_1 = "ooooc";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_key);
        tmp_args_element_value_1 = par_key;
        tmp_args_element_value_2 = Py_None;
        frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__->m_frame.f_lineno = 139;
        {
            PyObject *call_args[] = {tmp_args_element_value_1, tmp_args_element_value_2};
            tmp_assign_source_1 = CALL_FUNCTION_WITH_ARGS2(tstate, tmp_called_value_1, call_args);
        }

        Py_DECREF(tmp_called_value_1);
        if (tmp_assign_source_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 139;
            type_description_1 = "ooooc";
            goto frame_exception_exit_1;
        }
        assert(var_obj == NULL);
        var_obj = tmp_assign_source_1;
    }
    {
        bool tmp_condition_result_1;
        PyObject *tmp_cmp_expr_left_1;
        PyObject *tmp_cmp_expr_right_1;
        PyObject *tmp_type_arg_1;
        CHECK_OBJECT(var_obj);
        tmp_type_arg_1 = var_obj;
        tmp_cmp_expr_left_1 = BUILTIN_TYPE1(tmp_type_arg_1);
        assert(!(tmp_cmp_expr_left_1 == NULL));
        tmp_cmp_expr_right_1 = module_var_accessor_keyring$$36$compat$$36$properties$classproperty(tstate);
        if (unlikely(tmp_cmp_expr_right_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_cmp_expr_right_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));

            Py_DECREF(tmp_cmp_expr_left_1);

            exception_lineno = 140;
            type_description_1 = "ooooc";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_1 = (tmp_cmp_expr_left_1 == tmp_cmp_expr_right_1) ? true : false;
        Py_DECREF(tmp_cmp_expr_left_1);
        if (tmp_condition_result_1 != false) {
            goto branch_yes_1;
        } else {
            goto branch_no_1;
        }
    }
    branch_yes_1:;
    {
        PyObject *tmp_called_instance_1;
        PyObject *tmp_args_element_value_3;
        PyObject *tmp_args_element_value_4;
        CHECK_OBJECT(var_obj);
        tmp_called_instance_1 = var_obj;
        CHECK_OBJECT(par_self);
        tmp_args_element_value_3 = par_self;
        CHECK_OBJECT(par_value);
        tmp_args_element_value_4 = par_value;
        frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__->m_frame.f_lineno = 141;
        {
            PyObject *call_args[] = {tmp_args_element_value_3, tmp_args_element_value_4};
            tmp_return_value = CALL_METHOD_WITH_ARGS2(
                tstate,
                tmp_called_instance_1,
                mod_consts[6],
                call_args
            );
        }

        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 141;
            type_description_1 = "ooooc";
            goto frame_exception_exit_1;
        }
        goto frame_return_exit_1;
    }
    branch_no_1:;
    {
        PyObject *tmp_called_instance_2;
        PyObject *tmp_type_arg_value_1;
        PyObject *tmp_object_arg_value_1;
        PyObject *tmp_args_element_value_5;
        PyObject *tmp_args_element_value_6;
        if (Nuitka_Cell_GET(self->m_closure[0]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[7]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 142;
            type_description_1 = "ooooc";
            goto frame_exception_exit_1;
        }

        tmp_type_arg_value_1 = Nuitka_Cell_GET(self->m_closure[0]);
        CHECK_OBJECT(par_self);
        tmp_object_arg_value_1 = par_self;
        tmp_called_instance_2 = BUILTIN_SUPER0(tstate, moduledict_keyring$compat$properties, tmp_type_arg_value_1, tmp_object_arg_value_1);
        if (tmp_called_instance_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 142;
            type_description_1 = "ooooc";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_key);
        tmp_args_element_value_5 = par_key;
        CHECK_OBJECT(par_value);
        tmp_args_element_value_6 = par_value;
        frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__->m_frame.f_lineno = 142;
        {
            PyObject *call_args[] = {tmp_args_element_value_5, tmp_args_element_value_6};
            tmp_return_value = CALL_METHOD_WITH_ARGS2(
                tstate,
                tmp_called_instance_2,
                mod_consts[8],
                call_args
            );
        }

        Py_DECREF(tmp_called_instance_2);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 142;
            type_description_1 = "ooooc";
            goto frame_exception_exit_1;
        }
        goto frame_return_exit_1;
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_return_exit_1:

    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto try_return_handler_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__,
        type_description_1,
        par_self,
        par_key,
        par_value,
        var_obj,
        self->m_closure[0]
    );


    // Release cached frame if used for exception.
    if (frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__ == cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__);
        cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__ = NULL;
    }

    assertFrameObject(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Return handler code:
    try_return_handler_1:;
    CHECK_OBJECT(var_obj);
    Py_DECREF(var_obj);
    var_obj = NULL;
    goto function_return_exit;
    // Exception handler code:
    try_except_handler_1:;
    exception_keeper_lineno_1 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_1 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    Py_XDECREF(var_obj);
    var_obj = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_1;
    exception_lineno = exception_keeper_lineno_1;

    goto function_exception_exit;
    // End of try:

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_OBJECT(par_key);
    Py_DECREF(par_key);
    CHECK_OBJECT(par_value);
    Py_DECREF(par_value);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_OBJECT(par_key);
    Py_DECREF(par_key);
    CHECK_OBJECT(par_value);
    Py_DECREF(par_value);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_keyring$compat$properties$$36$$$36$$$36$function__4___init__(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_fget = python_pars[1];
    PyObject *par_fset = python_pars[2];
    struct Nuitka_FrameObject *frame_frame_keyring$compat$properties$$36$$$36$$$36$function__4___init__;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    bool tmp_result;
    NUITKA_MAY_BE_UNUSED nuitka_void tmp_unused;
    static struct Nuitka_FrameObject *cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__4___init__ = NULL;
    PyObject *tmp_return_value = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__4___init__)) {
        Py_XDECREF(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__4___init__);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__4___init__ == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__4___init__ = MAKE_FUNCTION_FRAME(tstate, code_objects_141a5838a173a6b378f83501274d2076, module_keyring$compat$properties, sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__4___init__->m_type_description == NULL);
    frame_frame_keyring$compat$properties$$36$$$36$$$36$function__4___init__ = cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__4___init__;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_keyring$compat$properties$$36$$$36$$$36$function__4___init__);
    assert(Py_REFCNT(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__4___init__) == 2);

    // Framed code:
    {
        PyObject *tmp_assattr_value_1;
        PyObject *tmp_called_instance_1;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_assattr_target_1;
        CHECK_OBJECT(par_self);
        tmp_called_instance_1 = par_self;
        CHECK_OBJECT(par_fget);
        tmp_args_element_value_1 = par_fget;
        frame_frame_keyring$compat$properties$$36$$$36$$$36$function__4___init__->m_frame.f_lineno = 145;
        tmp_assattr_value_1 = CALL_METHOD_WITH_SINGLE_ARG(tstate, tmp_called_instance_1, mod_consts[9], tmp_args_element_value_1);
        if (tmp_assattr_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 145;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_self);
        tmp_assattr_target_1 = par_self;
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_1, mod_consts[3], tmp_assattr_value_1);
        Py_DECREF(tmp_assattr_value_1);
        if (tmp_result == false) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 145;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
    }
    {
        PyObject *tmp_assattr_value_2;
        PyObject *tmp_assattr_target_2;
        CHECK_OBJECT(par_fset);
        tmp_assattr_value_2 = par_fset;
        CHECK_OBJECT(par_self);
        tmp_assattr_target_2 = par_self;
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_2, mod_consts[10], tmp_assattr_value_2);
        if (tmp_result == false) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 146;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
    }
    {
        nuitka_bool tmp_condition_result_1;
        int tmp_truth_name_1;
        CHECK_OBJECT(par_fset);
        tmp_truth_name_1 = CHECK_IF_TRUE(par_fset);
        if (tmp_truth_name_1 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 147;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_1 = tmp_truth_name_1 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        if (tmp_condition_result_1 == NUITKA_BOOL_TRUE) {
            goto branch_yes_1;
        } else {
            goto branch_no_1;
        }
    }
    branch_yes_1:;
    {
        PyObject *tmp_called_instance_2;
        PyObject *tmp_call_result_1;
        PyObject *tmp_args_element_value_2;
        CHECK_OBJECT(par_self);
        tmp_called_instance_2 = par_self;
        CHECK_OBJECT(par_fset);
        tmp_args_element_value_2 = par_fset;
        frame_frame_keyring$compat$properties$$36$$$36$$$36$function__4___init__->m_frame.f_lineno = 147;
        tmp_call_result_1 = CALL_METHOD_WITH_SINGLE_ARG(tstate, tmp_called_instance_2, mod_consts[11], tmp_args_element_value_2);
        if (tmp_call_result_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 147;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_1);
    }
    branch_no_1:;


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__4___init__, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_keyring$compat$properties$$36$$$36$$$36$function__4___init__->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_keyring$compat$properties$$36$$$36$$$36$function__4___init__, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_keyring$compat$properties$$36$$$36$$$36$function__4___init__,
        type_description_1,
        par_self,
        par_fget,
        par_fset
    );


    // Release cached frame if used for exception.
    if (frame_frame_keyring$compat$properties$$36$$$36$$$36$function__4___init__ == cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__4___init__) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__4___init__);
        cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__4___init__ = NULL;
    }

    assertFrameObject(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__4___init__);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;
    tmp_return_value = Py_None;
    Py_INCREF(tmp_return_value);
    goto function_return_exit;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_OBJECT(par_fget);
    Py_DECREF(par_fget);
    CHECK_OBJECT(par_fset);
    Py_DECREF(par_fset);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_OBJECT(par_fget);
    Py_DECREF(par_fget);
    CHECK_OBJECT(par_fset);
    Py_DECREF(par_fset);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_keyring$compat$properties$$36$$$36$$$36$function__5___get__(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_instance = python_pars[1];
    PyObject *par_owner = python_pars[2];
    struct Nuitka_FrameObject *frame_frame_keyring$compat$properties$$36$$$36$$$36$function__5___get__;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__5___get__ = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__5___get__)) {
        Py_XDECREF(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__5___get__);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__5___get__ == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__5___get__ = MAKE_FUNCTION_FRAME(tstate, code_objects_5542c59c5218e44ff56b298a5846d397, module_keyring$compat$properties, sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__5___get__->m_type_description == NULL);
    frame_frame_keyring$compat$properties$$36$$$36$$$36$function__5___get__ = cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__5___get__;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_keyring$compat$properties$$36$$$36$$$36$function__5___get__);
    assert(Py_REFCNT(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__5___get__) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_called_instance_1;
        PyObject *tmp_expression_value_1;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_args_element_value_2;
        CHECK_OBJECT(par_self);
        tmp_expression_value_1 = par_self;
        tmp_called_instance_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[3]);
        if (tmp_called_instance_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 150;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        tmp_args_element_value_1 = Py_None;
        CHECK_OBJECT(par_owner);
        tmp_args_element_value_2 = par_owner;
        frame_frame_keyring$compat$properties$$36$$$36$$$36$function__5___get__->m_frame.f_lineno = 150;
        {
            PyObject *call_args[] = {tmp_args_element_value_1, tmp_args_element_value_2};
            tmp_called_value_1 = CALL_METHOD_WITH_ARGS2(
                tstate,
                tmp_called_instance_1,
                mod_consts[12],
                call_args
            );
        }

        Py_DECREF(tmp_called_instance_1);
        if (tmp_called_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 150;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        frame_frame_keyring$compat$properties$$36$$$36$$$36$function__5___get__->m_frame.f_lineno = 150;
        tmp_return_value = CALL_FUNCTION_NO_ARGS(tstate, tmp_called_value_1);
        Py_DECREF(tmp_called_value_1);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 150;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        goto frame_return_exit_1;
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_return_exit_1:

    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto function_return_exit;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__5___get__, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_keyring$compat$properties$$36$$$36$$$36$function__5___get__->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_keyring$compat$properties$$36$$$36$$$36$function__5___get__, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_keyring$compat$properties$$36$$$36$$$36$function__5___get__,
        type_description_1,
        par_self,
        par_instance,
        par_owner
    );


    // Release cached frame if used for exception.
    if (frame_frame_keyring$compat$properties$$36$$$36$$$36$function__5___get__ == cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__5___get__) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__5___get__);
        cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__5___get__ = NULL;
    }

    assertFrameObject(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__5___get__);

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
    CHECK_OBJECT(par_instance);
    Py_DECREF(par_instance);
    CHECK_OBJECT(par_owner);
    Py_DECREF(par_owner);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_OBJECT(par_instance);
    Py_DECREF(par_instance);
    CHECK_OBJECT(par_owner);
    Py_DECREF(par_owner);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_keyring$compat$properties$$36$$$36$$$36$function__6___set__(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_owner = python_pars[1];
    PyObject *par_value = python_pars[2];
    struct Nuitka_FrameObject *frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    int tmp_res;
    PyObject *tmp_return_value = NULL;
    static struct Nuitka_FrameObject *cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__ = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;

    // Actual function body.
    // Tried code:
    if (isFrameUnusable(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__)) {
        Py_XDECREF(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__ == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__ = MAKE_FUNCTION_FRAME(tstate, code_objects_0e343abd4150458a2bdcb87479f52e6d, module_keyring$compat$properties, sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__->m_type_description == NULL);
    frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__ = cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__);
    assert(Py_REFCNT(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__) == 2);

    // Framed code:
    {
        bool tmp_condition_result_1;
        PyObject *tmp_operand_value_1;
        PyObject *tmp_expression_value_1;
        CHECK_OBJECT(par_self);
        tmp_expression_value_1 = par_self;
        tmp_operand_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[10]);
        if (tmp_operand_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 153;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        tmp_res = CHECK_IF_TRUE(tmp_operand_value_1);
        Py_DECREF(tmp_operand_value_1);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 153;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_1 = (tmp_res == 0) ? true : false;
        if (tmp_condition_result_1 != false) {
            goto branch_yes_1;
        } else {
            goto branch_no_1;
        }
    }
    branch_yes_1:;
    {
        PyObject *tmp_raise_type_1;
        PyObject *tmp_make_exception_arg_1;
        tmp_make_exception_arg_1 = mod_consts[13];
        frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__->m_frame.f_lineno = 154;
        tmp_raise_type_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_AttributeError, tmp_make_exception_arg_1);
        assert(!(tmp_raise_type_1 == NULL));
        exception_state.exception_type = tmp_raise_type_1;
        exception_lineno = 154;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);
        type_description_1 = "ooo";
        goto frame_exception_exit_1;
    }
    branch_no_1:;
    {
        bool tmp_condition_result_2;
        PyObject *tmp_cmp_expr_left_1;
        PyObject *tmp_cmp_expr_right_1;
        PyObject *tmp_type_arg_1;
        PyObject *tmp_expression_value_2;
        CHECK_OBJECT(par_owner);
        tmp_type_arg_1 = par_owner;
        tmp_cmp_expr_left_1 = BUILTIN_TYPE1(tmp_type_arg_1);
        assert(!(tmp_cmp_expr_left_1 == NULL));
        tmp_expression_value_2 = module_var_accessor_keyring$$36$compat$$36$properties$classproperty(tstate);
        if (unlikely(tmp_expression_value_2 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_expression_value_2 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));

            Py_DECREF(tmp_cmp_expr_left_1);

            exception_lineno = 155;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        tmp_cmp_expr_right_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_2, mod_consts[14]);
        if (tmp_cmp_expr_right_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_cmp_expr_left_1);

            exception_lineno = 155;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_2 = (tmp_cmp_expr_left_1 != tmp_cmp_expr_right_1) ? true : false;
        Py_DECREF(tmp_cmp_expr_left_1);
        Py_DECREF(tmp_cmp_expr_right_1);
        if (tmp_condition_result_2 != false) {
            goto branch_yes_2;
        } else {
            goto branch_no_2;
        }
    }
    branch_yes_2:;
    {
        PyObject *tmp_assign_source_1;
        PyObject *tmp_type_arg_2;
        CHECK_OBJECT(par_owner);
        tmp_type_arg_2 = par_owner;
        tmp_assign_source_1 = BUILTIN_TYPE1(tmp_type_arg_2);
        assert(!(tmp_assign_source_1 == NULL));
        {
            PyObject *old = par_owner;
            assert(old != NULL);
            par_owner = tmp_assign_source_1;
            Py_DECREF(old);
        }

    }
    branch_no_2:;
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_called_instance_1;
        PyObject *tmp_expression_value_3;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_args_element_value_2;
        PyObject *tmp_args_element_value_3;
        CHECK_OBJECT(par_self);
        tmp_expression_value_3 = par_self;
        tmp_called_instance_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_3, mod_consts[10]);
        if (tmp_called_instance_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 157;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        tmp_args_element_value_1 = Py_None;
        CHECK_OBJECT(par_owner);
        tmp_args_element_value_2 = par_owner;
        frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__->m_frame.f_lineno = 157;
        {
            PyObject *call_args[] = {tmp_args_element_value_1, tmp_args_element_value_2};
            tmp_called_value_1 = CALL_METHOD_WITH_ARGS2(
                tstate,
                tmp_called_instance_1,
                mod_consts[12],
                call_args
            );
        }

        Py_DECREF(tmp_called_instance_1);
        if (tmp_called_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 157;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_value);
        tmp_args_element_value_3 = par_value;
        frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__->m_frame.f_lineno = 157;
        tmp_return_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_1, tmp_args_element_value_3);
        Py_DECREF(tmp_called_value_1);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 157;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        goto frame_return_exit_1;
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_return_exit_1:

    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto try_return_handler_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__,
        type_description_1,
        par_self,
        par_owner,
        par_value
    );


    // Release cached frame if used for exception.
    if (frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__ == cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__);
        cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__ = NULL;
    }

    assertFrameObject(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__6___set__);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Return handler code:
    try_return_handler_1:;
    CHECK_OBJECT(par_owner);
    Py_DECREF(par_owner);
    par_owner = NULL;
    goto function_return_exit;
    // Exception handler code:
    try_except_handler_1:;
    exception_keeper_lineno_1 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_1 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    Py_XDECREF(par_owner);
    par_owner = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_1;
    exception_lineno = exception_keeper_lineno_1;

    goto function_exception_exit;
    // End of try:

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_OBJECT(par_value);
    Py_DECREF(par_value);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_OBJECT(par_value);
    Py_DECREF(par_value);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_keyring$compat$properties$$36$$$36$$$36$function__7_setter(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_fset = python_pars[1];
    struct Nuitka_FrameObject *frame_frame_keyring$compat$properties$$36$$$36$$$36$function__7_setter;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    bool tmp_result;
    static struct Nuitka_FrameObject *cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__7_setter = NULL;
    PyObject *tmp_return_value = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__7_setter)) {
        Py_XDECREF(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__7_setter);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__7_setter == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__7_setter = MAKE_FUNCTION_FRAME(tstate, code_objects_7e718ecaef63b307d53ffdbe737750e5, module_keyring$compat$properties, sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__7_setter->m_type_description == NULL);
    frame_frame_keyring$compat$properties$$36$$$36$$$36$function__7_setter = cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__7_setter;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_keyring$compat$properties$$36$$$36$$$36$function__7_setter);
    assert(Py_REFCNT(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__7_setter) == 2);

    // Framed code:
    {
        PyObject *tmp_assattr_value_1;
        PyObject *tmp_called_instance_1;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_assattr_target_1;
        CHECK_OBJECT(par_self);
        tmp_called_instance_1 = par_self;
        CHECK_OBJECT(par_fset);
        tmp_args_element_value_1 = par_fset;
        frame_frame_keyring$compat$properties$$36$$$36$$$36$function__7_setter->m_frame.f_lineno = 160;
        tmp_assattr_value_1 = CALL_METHOD_WITH_SINGLE_ARG(tstate, tmp_called_instance_1, mod_consts[9], tmp_args_element_value_1);
        if (tmp_assattr_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 160;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_self);
        tmp_assattr_target_1 = par_self;
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_1, mod_consts[10], tmp_assattr_value_1);
        Py_DECREF(tmp_assattr_value_1);
        if (tmp_result == false) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 160;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__7_setter, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_keyring$compat$properties$$36$$$36$$$36$function__7_setter->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_keyring$compat$properties$$36$$$36$$$36$function__7_setter, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_keyring$compat$properties$$36$$$36$$$36$function__7_setter,
        type_description_1,
        par_self,
        par_fset
    );


    // Release cached frame if used for exception.
    if (frame_frame_keyring$compat$properties$$36$$$36$$$36$function__7_setter == cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__7_setter) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__7_setter);
        cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__7_setter = NULL;
    }

    assertFrameObject(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__7_setter);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;
    CHECK_OBJECT(par_self);
    tmp_return_value = par_self;
    Py_INCREF(tmp_return_value);
    goto function_return_exit;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_OBJECT(par_fset);
    Py_DECREF(par_fset);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_OBJECT(par_fset);
    Py_DECREF(par_fset);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_cls = python_pars[0];
    PyObject *par_fn = python_pars[1];
    nuitka_bool var_needs_method = NUITKA_BOOL_UNASSIGNED;
    struct Nuitka_FrameObject *frame_frame_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    int tmp_res;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;

    // Actual function body.
    // Tried code:
    if (isFrameUnusable(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method)) {
        Py_XDECREF(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method = MAKE_FUNCTION_FRAME(tstate, code_objects_e845ce3226ae1279ca9cfe39835bf794, module_keyring$compat$properties, sizeof(nuitka_bool)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method->m_type_description == NULL);
    frame_frame_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method = cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method);
    assert(Py_REFCNT(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method) == 2);

    // Framed code:
    {
        nuitka_bool tmp_assign_source_1;
        PyObject *tmp_operand_value_1;
        PyObject *tmp_isinstance_inst_1;
        PyObject *tmp_isinstance_cls_1;
        CHECK_OBJECT(par_fn);
        tmp_isinstance_inst_1 = par_fn;
        tmp_isinstance_cls_1 = mod_consts[15];
        tmp_res = PyObject_IsInstance(tmp_isinstance_inst_1, tmp_isinstance_cls_1);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 168;
            type_description_1 = "oob";
            goto frame_exception_exit_1;
        }
        tmp_operand_value_1 = (tmp_res != 0) ? Py_True : Py_False;
        tmp_res = CHECK_IF_TRUE(tmp_operand_value_1);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 168;
            type_description_1 = "oob";
            goto frame_exception_exit_1;
        }
        tmp_assign_source_1 = (tmp_res == 0) ? NUITKA_BOOL_TRUE : NUITKA_BOOL_FALSE;
        var_needs_method = tmp_assign_source_1;
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method,
        type_description_1,
        par_cls,
        par_fn,
        (int)var_needs_method
    );


    // Release cached frame if used for exception.
    if (frame_frame_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method == cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method);
        cache_frame_frame_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method = NULL;
    }

    assertFrameObject(frame_frame_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    {
        bool tmp_condition_result_1;
        PyObject *tmp_classmethod_arg_1;
        assert(var_needs_method != NUITKA_BOOL_UNASSIGNED);
        tmp_condition_result_1 = var_needs_method == NUITKA_BOOL_TRUE;
        if (tmp_condition_result_1 != false) {
            goto condexpr_true_1;
        } else {
            goto condexpr_false_1;
        }
        condexpr_true_1:;
        CHECK_OBJECT(par_fn);
        tmp_classmethod_arg_1 = par_fn;
        tmp_return_value = BUILTIN_CLASSMETHOD(tstate, tmp_classmethod_arg_1);
        assert(!(tmp_return_value == NULL));
        goto condexpr_end_1;
        condexpr_false_1:;
        CHECK_OBJECT(par_fn);
        tmp_return_value = par_fn;
        Py_INCREF(tmp_return_value);
        condexpr_end_1:;
        goto try_return_handler_1;
    }
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Return handler code:
    try_return_handler_1:;
    assert(var_needs_method != NUITKA_BOOL_UNASSIGNED);
    var_needs_method = NUITKA_BOOL_UNASSIGNED;
    goto function_return_exit;
    // Exception handler code:
    try_except_handler_1:;
    exception_keeper_lineno_1 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_1 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    // Re-raise.
    exception_state = exception_keeper_name_1;
    exception_lineno = exception_keeper_lineno_1;

    goto function_exception_exit;
    // End of try:

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_cls);
    Py_DECREF(par_cls);
    CHECK_OBJECT(par_fn);
    Py_DECREF(par_fn);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_cls);
    Py_DECREF(par_cls);
    CHECK_OBJECT(par_fn);
    Py_DECREF(par_fn);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}



static PyObject *MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__1___init__(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_keyring$compat$properties$$36$$$36$$$36$function__1___init__,
        mod_consts[27],
#if PYTHON_VERSION >= 0x300
        mod_consts[28],
#endif
        code_objects_4fde9e08e32946118eac2bfaa4f7dd53,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_keyring$compat$properties,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__2___get__(PyThreadState *tstate, PyObject *defaults) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_keyring$compat$properties$$36$$$36$$$36$function__2___get__,
        mod_consts[12],
#if PYTHON_VERSION >= 0x300
        mod_consts[30],
#endif
        code_objects_92da0d1eb7f4ca4d5b6f1b5cdf3803f0,
        defaults,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_keyring$compat$properties,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__(PyThreadState *tstate, struct Nuitka_CellObject **closure) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__,
        mod_consts[8],
#if PYTHON_VERSION >= 0x300
        mod_consts[39],
#endif
        code_objects_cbce1dea3c2a7b6a7668db59f6ee7775,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_keyring$compat$properties,
        NULL,
        closure,
        1
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__4___init__(PyThreadState *tstate, PyObject *defaults) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_keyring$compat$properties$$36$$$36$$$36$function__4___init__,
        mod_consts[27],
#if PYTHON_VERSION >= 0x300
        mod_consts[41],
#endif
        code_objects_141a5838a173a6b378f83501274d2076,
        defaults,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_keyring$compat$properties,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__5___get__(PyThreadState *tstate, PyObject *defaults) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_keyring$compat$properties$$36$$$36$$$36$function__5___get__,
        mod_consts[12],
#if PYTHON_VERSION >= 0x300
        mod_consts[42],
#endif
        code_objects_5542c59c5218e44ff56b298a5846d397,
        defaults,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_keyring$compat$properties,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__6___set__(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_keyring$compat$properties$$36$$$36$$$36$function__6___set__,
        mod_consts[6],
#if PYTHON_VERSION >= 0x300
        mod_consts[43],
#endif
        code_objects_0e343abd4150458a2bdcb87479f52e6d,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_keyring$compat$properties,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__7_setter(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_keyring$compat$properties$$36$$$36$$$36$function__7_setter,
        mod_consts[11],
#if PYTHON_VERSION >= 0x300
        mod_consts[44],
#endif
        code_objects_7e718ecaef63b307d53ffdbe737750e5,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_keyring$compat$properties,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method,
        mod_consts[9],
#if PYTHON_VERSION >= 0x300
        mod_consts[45],
#endif
        code_objects_e845ce3226ae1279ca9cfe39835bf794,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_keyring$compat$properties,
        mod_consts[16],
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

static function_impl_code const function_table_keyring$compat$properties[] = {
    impl_keyring$compat$properties$$36$$$36$$$36$function__1___init__,
    impl_keyring$compat$properties$$36$$$36$$$36$function__2___get__,
    impl_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__,
    impl_keyring$compat$properties$$36$$$36$$$36$function__4___init__,
    impl_keyring$compat$properties$$36$$$36$$$36$function__5___get__,
    impl_keyring$compat$properties$$36$$$36$$$36$function__6___set__,
    impl_keyring$compat$properties$$36$$$36$$$36$function__7_setter,
    impl_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method,
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

    return Nuitka_Function_GetFunctionState(function, function_table_keyring$compat$properties);
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
        module_keyring$compat$properties,
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
        function_table_keyring$compat$properties,
        sizeof(function_table_keyring$compat$properties) / sizeof(function_impl_code)
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
static char const *module_full_name = "keyring.compat.properties";
#endif

// Internal entry point for module code.
PyObject *modulecode_keyring$compat$properties(PyThreadState *tstate, PyObject *module, struct Nuitka_MetaPathBasedLoaderEntry const *loader_entry) {
    // Report entry to PGO.
    PGO_onModuleEntered("keyring$compat$properties");

    // Store the module for future use.
    module_keyring$compat$properties = module;

    moduledict_keyring$compat$properties = MODULE_DICT(module_keyring$compat$properties);

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
        PRINT_STRING("keyring$compat$properties: Calling setupMetaPathBasedLoader().\n");
#endif
        setupMetaPathBasedLoader(tstate);
#if 0 >= 0
#ifdef _NUITKA_TRACE
        PRINT_STRING("keyring$compat$properties: Calling updateMetaPathBasedLoaderModuleRoot().\n");
#endif
        updateMetaPathBasedLoaderModuleRoot(module_full_name);
#endif


#if PYTHON_VERSION >= 0x300
        patchInspectModule(tstate);
#endif

#endif

        /* The constants only used by this module are created now. */
        NUITKA_PRINT_TRACE("keyring$compat$properties: Calling createModuleConstants().\n");
        createModuleConstants(tstate);

#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
        createModuleCodeObjects();
#endif
        init_done = true;
    }

#if _NUITKA_MODULE_MODE && 0
    PyObject *pre_load = IMPORT_EMBEDDED_MODULE(tstate, "keyring.compat.properties" "-preLoad");
    if (pre_load == NULL) {
        return NULL;
    }
#endif

    // PRINT_STRING("in initkeyring$compat$properties\n");

#ifdef _NUITKA_PLUGIN_DILL_ENABLED
    {
        char const *module_name_c;
        if (loader_entry != NULL) {
            module_name_c = loader_entry->name;
        } else {
            PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_keyring$compat$properties, (Nuitka_StringObject *)const_str_plain___name__);
            module_name_c = Nuitka_String_AsString(module_name);
        }

        registerDillPluginTables(tstate, module_name_c, &_method_def_reduce_compiled_function, &_method_def_create_compiled_function);
    }
#endif

    // Set "__compiled__" to what version information we have.
    UPDATE_STRING_DICT0(
        moduledict_keyring$compat$properties,
        (Nuitka_StringObject *)const_str_plain___compiled__,
        Nuitka_dunder_compiled_value
    );

    // Update "__package__" value to what it ought to be.
    {
#if 0
        UPDATE_STRING_DICT0(
            moduledict_keyring$compat$properties,
            (Nuitka_StringObject *)const_str_plain___package__,
            mod_consts[57]
        );
#elif 0
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_keyring$compat$properties, (Nuitka_StringObject *)const_str_plain___name__);

        UPDATE_STRING_DICT0(
            moduledict_keyring$compat$properties,
            (Nuitka_StringObject *)const_str_plain___package__,
            module_name
        );
#else

#if PYTHON_VERSION < 0x300
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_keyring$compat$properties, (Nuitka_StringObject *)const_str_plain___name__);
        char const *module_name_cstr = PyString_AS_STRING(module_name);

        char const *last_dot = strrchr(module_name_cstr, '.');

        if (last_dot != NULL) {
            UPDATE_STRING_DICT1(
                moduledict_keyring$compat$properties,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyString_FromStringAndSize(module_name_cstr, last_dot - module_name_cstr)
            );
        }
#else
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_keyring$compat$properties, (Nuitka_StringObject *)const_str_plain___name__);
        Py_ssize_t dot_index = PyUnicode_Find(module_name, const_str_dot, 0, PyUnicode_GetLength(module_name), -1);

        if (dot_index != -1) {
            UPDATE_STRING_DICT1(
                moduledict_keyring$compat$properties,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyUnicode_Substring(module_name, 0, dot_index)
            );
        }
#endif
#endif
    }

    CHECK_OBJECT(module_keyring$compat$properties);

    // For deep importing of a module we need to have "__builtins__", so we set
    // it ourselves in the same way than CPython does. Note: This must be done
    // before the frame object is allocated, or else it may fail.

    if (GET_STRING_DICT_VALUE(moduledict_keyring$compat$properties, (Nuitka_StringObject *)const_str_plain___builtins__) == NULL) {
        PyObject *value = (PyObject *)builtin_module;

        // Check if main module, not a dict then but the module itself.
#if _NUITKA_MODULE_MODE || !0
        value = PyModule_GetDict(value);
#endif

        UPDATE_STRING_DICT0(moduledict_keyring$compat$properties, (Nuitka_StringObject *)const_str_plain___builtins__, value);
    }

    PyObject *module_loader = Nuitka_Loader_New(loader_entry);
    UPDATE_STRING_DICT0(moduledict_keyring$compat$properties, (Nuitka_StringObject *)const_str_plain___loader__, module_loader);

#if PYTHON_VERSION >= 0x300
// Set the "__spec__" value

#if 0
    // Main modules just get "None" as spec.
    UPDATE_STRING_DICT0(moduledict_keyring$compat$properties, (Nuitka_StringObject *)const_str_plain___spec__, Py_None);
#else
    // Other modules get a "ModuleSpec" from the standard mechanism.
    {
        PyObject *bootstrap_module = getImportLibBootstrapModule();
        CHECK_OBJECT(bootstrap_module);

        PyObject *_spec_from_module = PyObject_GetAttrString(bootstrap_module, "_spec_from_module");
        CHECK_OBJECT(_spec_from_module);

        PyObject *spec_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, _spec_from_module, module_keyring$compat$properties);
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

        UPDATE_STRING_DICT1(moduledict_keyring$compat$properties, (Nuitka_StringObject *)const_str_plain___spec__, spec_value);
    }
#endif
#endif

    // Temp variables if any
    PyObject *outline_0_var___class__ = NULL;
    PyObject *outline_1_var___class__ = NULL;
    struct Nuitka_CellObject *outline_2_var___class__ = NULL;
    PyObject *tmp_class_creation_1__class_decl_dict = NULL;
    PyObject *tmp_class_creation_1__prepared = NULL;
    PyObject *tmp_class_creation_2__class_decl_dict = NULL;
    PyObject *tmp_class_creation_2__prepared = NULL;
    PyObject *tmp_classproperty$$36$class_creation_1__bases = NULL;
    PyObject *tmp_classproperty$$36$class_creation_1__class_decl_dict = NULL;
    PyObject *tmp_classproperty$$36$class_creation_1__metaclass = NULL;
    PyObject *tmp_classproperty$$36$class_creation_1__prepared = NULL;
    struct Nuitka_FrameObject *frame_frame_keyring$compat$properties;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    bool tmp_result;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    PyObject *locals_keyring$compat$properties$$36$$$36$$$36$class__1_NonDataProperty_4 = NULL;
    PyObject *tmp_dictset_value;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_2;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_2;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_3;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_3;
    PyObject *locals_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_34 = NULL;
    struct Nuitka_FrameObject *frame_frame_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_2;
    NUITKA_MAY_BE_UNUSED char const *type_description_2 = NULL;
    int tmp_res;
    PyObject *locals_keyring$compat$properties$$36$$$36$$$36$class__3_Meta_137 = NULL;
    struct Nuitka_FrameObject *frame_frame_keyring$compat$properties$$36$$$36$$$36$class__3_Meta_3;
    NUITKA_MAY_BE_UNUSED char const *type_description_3 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_4;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_4;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_5;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_5;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_6;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_6;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_7;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_7;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_8;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_8;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_9;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_9;

    // Module init code if any


    // Module code.
    {
        PyObject *tmp_assign_source_1;
        tmp_assign_source_1 = Py_None;
        UPDATE_STRING_DICT0(moduledict_keyring$compat$properties, (Nuitka_StringObject *)mod_consts[17], tmp_assign_source_1);
    }
    {
        PyObject *tmp_assign_source_2;
        tmp_assign_source_2 = module_filename_obj;
        UPDATE_STRING_DICT0(moduledict_keyring$compat$properties, (Nuitka_StringObject *)mod_consts[18], tmp_assign_source_2);
    }
    frame_frame_keyring$compat$properties = MAKE_MODULE_FRAME(code_objects_af0ed0f3fe635d3316f54240ceb861d8, module_keyring$compat$properties);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_keyring$compat$properties);
    assert(Py_REFCNT(frame_frame_keyring$compat$properties) == 2);

    // Framed code:
    {
        PyObject *tmp_assattr_value_1;
        PyObject *tmp_assattr_target_1;
        tmp_assattr_value_1 = module_filename_obj;
        tmp_assattr_target_1 = module_var_accessor_keyring$$36$compat$$36$properties$__spec__(tstate);
        assert(!(tmp_assattr_target_1 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_1, mod_consts[19], tmp_assattr_value_1);
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
        tmp_assattr_target_2 = module_var_accessor_keyring$$36$compat$$36$properties$__spec__(tstate);
        assert(!(tmp_assattr_target_2 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_2, mod_consts[20], tmp_assattr_value_2);
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
        UPDATE_STRING_DICT0(moduledict_keyring$compat$properties, (Nuitka_StringObject *)mod_consts[21], tmp_assign_source_3);
    }
    {
        PyObject *tmp_assign_source_4;
        tmp_assign_source_4 = MAKE_DICT_EMPTY(tstate);
        assert(tmp_class_creation_1__class_decl_dict == NULL);
        tmp_class_creation_1__class_decl_dict = tmp_assign_source_4;
    }
    {
        PyObject *tmp_assign_source_5;
        tmp_assign_source_5 = MAKE_DICT_EMPTY(tstate);
        assert(tmp_class_creation_1__prepared == NULL);
        tmp_class_creation_1__prepared = tmp_assign_source_5;
    }
    // Tried code:
    {
        PyObject *tmp_assign_source_6;
        {
            PyObject *tmp_set_locals_1;
            CHECK_OBJECT(tmp_class_creation_1__prepared);
            tmp_set_locals_1 = tmp_class_creation_1__prepared;
            locals_keyring$compat$properties$$36$$$36$$$36$class__1_NonDataProperty_4 = tmp_set_locals_1;
            Py_INCREF(tmp_set_locals_1);
        }
        tmp_dictset_value = mod_consts[22];
        tmp_result = DICT_SET_ITEM(locals_keyring$compat$properties$$36$$$36$$$36$class__1_NonDataProperty_4, mod_consts[23], tmp_dictset_value);
        assert(!(tmp_result == false));
        tmp_dictset_value = mod_consts[24];
        tmp_result = DICT_SET_ITEM(locals_keyring$compat$properties$$36$$$36$$$36$class__1_NonDataProperty_4, mod_consts[17], tmp_dictset_value);
        assert(!(tmp_result == false));
        tmp_dictset_value = mod_consts[25];
        tmp_result = DICT_SET_ITEM(locals_keyring$compat$properties$$36$$$36$$$36$class__1_NonDataProperty_4, mod_consts[26], tmp_dictset_value);
        assert(!(tmp_result == false));


        tmp_dictset_value = MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__1___init__(tstate);

        tmp_result = DICT_SET_ITEM(locals_keyring$compat$properties$$36$$$36$$$36$class__1_NonDataProperty_4, mod_consts[27], tmp_dictset_value);
        Py_DECREF(tmp_dictset_value);
        assert(!(tmp_result == false));
        {
            PyObject *tmp_defaults_1;
            tmp_defaults_1 = mod_consts[29];
            Py_INCREF(tmp_defaults_1);


            tmp_dictset_value = MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__2___get__(tstate, tmp_defaults_1);

            tmp_result = DICT_SET_ITEM(locals_keyring$compat$properties$$36$$$36$$$36$class__1_NonDataProperty_4, mod_consts[12], tmp_dictset_value);
            Py_DECREF(tmp_dictset_value);
            assert(!(tmp_result == false));
        }
        // Tried code:
        // Tried code:
        {
            PyObject *tmp_assign_source_7;
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
            tmp_tuple_element_1 = locals_keyring$compat$properties$$36$$$36$$$36$class__1_NonDataProperty_4;
            PyTuple_SET_ITEM0(tmp_args_value_1, 2, tmp_tuple_element_1);
            CHECK_OBJECT(tmp_class_creation_1__class_decl_dict);
            tmp_kwargs_value_1 = tmp_class_creation_1__class_decl_dict;
            frame_frame_keyring$compat$properties->m_frame.f_lineno = 4;
            tmp_assign_source_7 = CALL_FUNCTION(tstate, tmp_called_value_1, tmp_args_value_1, tmp_kwargs_value_1);
            Py_DECREF(tmp_args_value_1);
            if (tmp_assign_source_7 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 4;

                goto try_except_handler_3;
            }
            assert(outline_0_var___class__ == NULL);
            outline_0_var___class__ = tmp_assign_source_7;
        }
        CHECK_OBJECT(outline_0_var___class__);
        tmp_assign_source_6 = outline_0_var___class__;
        Py_INCREF(tmp_assign_source_6);
        goto try_return_handler_3;
        NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
        return NULL;
        // Return handler code:
        try_return_handler_3:;
        Py_DECREF(locals_keyring$compat$properties$$36$$$36$$$36$class__1_NonDataProperty_4);
        locals_keyring$compat$properties$$36$$$36$$$36$class__1_NonDataProperty_4 = NULL;
        goto try_return_handler_2;
        // Exception handler code:
        try_except_handler_3:;
        exception_keeper_lineno_1 = exception_lineno;
        exception_lineno = 0;
        exception_keeper_name_1 = exception_state;
        INIT_ERROR_OCCURRED_STATE(&exception_state);

        Py_DECREF(locals_keyring$compat$properties$$36$$$36$$$36$class__1_NonDataProperty_4);
        locals_keyring$compat$properties$$36$$$36$$$36$class__1_NonDataProperty_4 = NULL;
        // Re-raise.
        exception_state = exception_keeper_name_1;
        exception_lineno = exception_keeper_lineno_1;

        goto try_except_handler_2;
        // End of try:
        NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
        return NULL;
        // Return handler code:
        try_return_handler_2:;
        CHECK_OBJECT(outline_0_var___class__);
        Py_DECREF(outline_0_var___class__);
        outline_0_var___class__ = NULL;
        goto outline_result_1;
        // Exception handler code:
        try_except_handler_2:;
        exception_keeper_lineno_2 = exception_lineno;
        exception_lineno = 0;
        exception_keeper_name_2 = exception_state;
        INIT_ERROR_OCCURRED_STATE(&exception_state);

        // Re-raise.
        exception_state = exception_keeper_name_2;
        exception_lineno = exception_keeper_lineno_2;

        goto outline_exception_1;
        // End of try:
        NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
        return NULL;
        outline_exception_1:;
        exception_lineno = 4;
        goto try_except_handler_1;
        outline_result_1:;
        UPDATE_STRING_DICT1(moduledict_keyring$compat$properties, (Nuitka_StringObject *)mod_consts[25], tmp_assign_source_6);
    }
    goto try_end_1;
    // Exception handler code:
    try_except_handler_1:;
    exception_keeper_lineno_3 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_3 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    CHECK_OBJECT(tmp_class_creation_1__class_decl_dict);
    Py_DECREF(tmp_class_creation_1__class_decl_dict);
    tmp_class_creation_1__class_decl_dict = NULL;
    CHECK_OBJECT(tmp_class_creation_1__prepared);
    Py_DECREF(tmp_class_creation_1__prepared);
    tmp_class_creation_1__prepared = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_3;
    exception_lineno = exception_keeper_lineno_3;

    goto frame_exception_exit_1;
    // End of try:
    try_end_1:;
    CHECK_OBJECT(tmp_class_creation_1__class_decl_dict);
    Py_DECREF(tmp_class_creation_1__class_decl_dict);
    tmp_class_creation_1__class_decl_dict = NULL;
    CHECK_OBJECT(tmp_class_creation_1__prepared);
    Py_DECREF(tmp_class_creation_1__prepared);
    tmp_class_creation_1__prepared = NULL;
    {
        PyObject *tmp_assign_source_8;
        tmp_assign_source_8 = MAKE_DICT_EMPTY(tstate);
        assert(tmp_class_creation_2__class_decl_dict == NULL);
        tmp_class_creation_2__class_decl_dict = tmp_assign_source_8;
    }
    {
        PyObject *tmp_assign_source_9;
        tmp_assign_source_9 = MAKE_DICT_EMPTY(tstate);
        assert(tmp_class_creation_2__prepared == NULL);
        tmp_class_creation_2__prepared = tmp_assign_source_9;
    }
    // Tried code:
    {
        PyObject *tmp_assign_source_10;
        {
            PyObject *tmp_set_locals_2;
            CHECK_OBJECT(tmp_class_creation_2__prepared);
            tmp_set_locals_2 = tmp_class_creation_2__prepared;
            locals_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_34 = tmp_set_locals_2;
            Py_INCREF(tmp_set_locals_2);
        }
        tmp_dictset_value = mod_consts[22];
        tmp_result = DICT_SET_ITEM(locals_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_34, mod_consts[23], tmp_dictset_value);
        assert(!(tmp_result == false));
        tmp_dictset_value = mod_consts[31];
        tmp_result = DICT_SET_ITEM(locals_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_34, mod_consts[17], tmp_dictset_value);
        assert(!(tmp_result == false));
        tmp_dictset_value = mod_consts[5];
        tmp_result = DICT_SET_ITEM(locals_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_34, mod_consts[26], tmp_dictset_value);
        assert(!(tmp_result == false));
        // Tried code:
        // Tried code:
        frame_frame_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_2 = MAKE_CLASS_FRAME(tstate, code_objects_88f4ba6c2716a1cfb0fdd90977a2f3c2, module_keyring$compat$properties, NULL, sizeof(void *));

        // Push the new frame as the currently active one, and we should be exclusively
        // owning it.
        pushFrameStackCompiledFrame(tstate, frame_frame_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_2);
        assert(Py_REFCNT(frame_frame_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_2) == 2);

        // Framed code:
        // Tried code:
        {
            PyObject *tmp_assign_source_11;
            PyObject *tmp_direct_call_arg1_1;
            tmp_direct_call_arg1_1 = mod_consts[32];
            Py_INCREF(tmp_direct_call_arg1_1);

            {
                PyObject *dir_call_args[] = {tmp_direct_call_arg1_1};
                tmp_assign_source_11 = impl___main__$$36$$$36$$$36$helper_function__mro_entries_conversion(tstate, dir_call_args);
            }
            if (tmp_assign_source_11 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 137;
                type_description_2 = "o";
                goto try_except_handler_7;
            }
            assert(tmp_classproperty$$36$class_creation_1__bases == NULL);
            tmp_classproperty$$36$class_creation_1__bases = tmp_assign_source_11;
        }
        {
            PyObject *tmp_assign_source_12;
            tmp_assign_source_12 = MAKE_DICT_EMPTY(tstate);
            assert(tmp_classproperty$$36$class_creation_1__class_decl_dict == NULL);
            tmp_classproperty$$36$class_creation_1__class_decl_dict = tmp_assign_source_12;
        }
        {
            PyObject *tmp_assign_source_13;
            PyObject *tmp_metaclass_value_1;
            nuitka_bool tmp_condition_result_1;
            int tmp_truth_name_1;
            PyObject *tmp_type_arg_1;
            PyObject *tmp_expression_value_1;
            PyObject *tmp_subscript_value_1;
            PyObject *tmp_bases_value_1;
            CHECK_OBJECT(tmp_classproperty$$36$class_creation_1__bases);
            tmp_truth_name_1 = CHECK_IF_TRUE(tmp_classproperty$$36$class_creation_1__bases);
            if (tmp_truth_name_1 == -1) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 137;
                type_description_2 = "o";
                goto try_except_handler_7;
            }
            tmp_condition_result_1 = tmp_truth_name_1 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
            if (tmp_condition_result_1 == NUITKA_BOOL_TRUE) {
                goto condexpr_true_1;
            } else {
                goto condexpr_false_1;
            }
            condexpr_true_1:;
            CHECK_OBJECT(tmp_classproperty$$36$class_creation_1__bases);
            tmp_expression_value_1 = tmp_classproperty$$36$class_creation_1__bases;
            tmp_subscript_value_1 = const_int_0;
            tmp_type_arg_1 = LOOKUP_SUBSCRIPT_CONST(tstate, tmp_expression_value_1, tmp_subscript_value_1, 0);
            if (tmp_type_arg_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 137;
                type_description_2 = "o";
                goto try_except_handler_7;
            }
            tmp_metaclass_value_1 = BUILTIN_TYPE1(tmp_type_arg_1);
            Py_DECREF(tmp_type_arg_1);
            if (tmp_metaclass_value_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 137;
                type_description_2 = "o";
                goto try_except_handler_7;
            }
            goto condexpr_end_1;
            condexpr_false_1:;
            tmp_metaclass_value_1 = (PyObject *)&PyType_Type;
            Py_INCREF(tmp_metaclass_value_1);
            condexpr_end_1:;
            CHECK_OBJECT(tmp_classproperty$$36$class_creation_1__bases);
            tmp_bases_value_1 = tmp_classproperty$$36$class_creation_1__bases;
            tmp_assign_source_13 = SELECT_METACLASS(tstate, tmp_metaclass_value_1, tmp_bases_value_1);
            Py_DECREF(tmp_metaclass_value_1);
            if (tmp_assign_source_13 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 137;
                type_description_2 = "o";
                goto try_except_handler_7;
            }
            assert(tmp_classproperty$$36$class_creation_1__metaclass == NULL);
            tmp_classproperty$$36$class_creation_1__metaclass = tmp_assign_source_13;
        }
        {
            bool tmp_condition_result_2;
            PyObject *tmp_expression_value_2;
            CHECK_OBJECT(tmp_classproperty$$36$class_creation_1__metaclass);
            tmp_expression_value_2 = tmp_classproperty$$36$class_creation_1__metaclass;
            tmp_res = HAS_ATTR_BOOL2(tstate, tmp_expression_value_2, mod_consts[33]);
            if (tmp_res == -1) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 137;
                type_description_2 = "o";
                goto try_except_handler_7;
            }
            tmp_condition_result_2 = (tmp_res != 0) ? true : false;
            if (tmp_condition_result_2 != false) {
                goto branch_yes_1;
            } else {
                goto branch_no_1;
            }
        }
        branch_yes_1:;
        {
            PyObject *tmp_assign_source_14;
            PyObject *tmp_called_value_2;
            PyObject *tmp_expression_value_3;
            PyObject *tmp_args_value_2;
            PyObject *tmp_tuple_element_2;
            PyObject *tmp_kwargs_value_2;
            CHECK_OBJECT(tmp_classproperty$$36$class_creation_1__metaclass);
            tmp_expression_value_3 = tmp_classproperty$$36$class_creation_1__metaclass;
            tmp_called_value_2 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_3, mod_consts[33]);
            if (tmp_called_value_2 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 137;
                type_description_2 = "o";
                goto try_except_handler_7;
            }
            tmp_tuple_element_2 = mod_consts[14];
            tmp_args_value_2 = MAKE_TUPLE_EMPTY(tstate, 2);
            PyTuple_SET_ITEM0(tmp_args_value_2, 0, tmp_tuple_element_2);
            CHECK_OBJECT(tmp_classproperty$$36$class_creation_1__bases);
            tmp_tuple_element_2 = tmp_classproperty$$36$class_creation_1__bases;
            PyTuple_SET_ITEM0(tmp_args_value_2, 1, tmp_tuple_element_2);
            CHECK_OBJECT(tmp_classproperty$$36$class_creation_1__class_decl_dict);
            tmp_kwargs_value_2 = tmp_classproperty$$36$class_creation_1__class_decl_dict;
            frame_frame_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_2->m_frame.f_lineno = 137;
            tmp_assign_source_14 = CALL_FUNCTION(tstate, tmp_called_value_2, tmp_args_value_2, tmp_kwargs_value_2);
            Py_DECREF(tmp_called_value_2);
            Py_DECREF(tmp_args_value_2);
            if (tmp_assign_source_14 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 137;
                type_description_2 = "o";
                goto try_except_handler_7;
            }
            assert(tmp_classproperty$$36$class_creation_1__prepared == NULL);
            tmp_classproperty$$36$class_creation_1__prepared = tmp_assign_source_14;
        }
        {
            bool tmp_condition_result_3;
            PyObject *tmp_operand_value_1;
            PyObject *tmp_expression_value_4;
            CHECK_OBJECT(tmp_classproperty$$36$class_creation_1__prepared);
            tmp_expression_value_4 = tmp_classproperty$$36$class_creation_1__prepared;
            tmp_res = HAS_ATTR_BOOL2(tstate, tmp_expression_value_4, mod_consts[34]);
            if (tmp_res == -1) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 137;
                type_description_2 = "o";
                goto try_except_handler_7;
            }
            tmp_operand_value_1 = (tmp_res != 0) ? Py_True : Py_False;
            tmp_res = CHECK_IF_TRUE(tmp_operand_value_1);
            assert(!(tmp_res == -1));
            tmp_condition_result_3 = (tmp_res == 0) ? true : false;
            if (tmp_condition_result_3 != false) {
                goto branch_yes_2;
            } else {
                goto branch_no_2;
            }
        }
        branch_yes_2:;
        {
            PyObject *tmp_raise_type_1;
            PyObject *tmp_make_exception_arg_1;
            PyObject *tmp_mod_expr_left_1;
            PyObject *tmp_mod_expr_right_1;
            PyObject *tmp_tuple_element_3;
            PyObject *tmp_expression_value_5;
            PyObject *tmp_name_value_1;
            PyObject *tmp_default_value_1;
            tmp_mod_expr_left_1 = mod_consts[35];
            CHECK_OBJECT(tmp_classproperty$$36$class_creation_1__metaclass);
            tmp_expression_value_5 = tmp_classproperty$$36$class_creation_1__metaclass;
            tmp_name_value_1 = mod_consts[36];
            tmp_default_value_1 = mod_consts[37];
            tmp_tuple_element_3 = BUILTIN_GETATTR(tstate, tmp_expression_value_5, tmp_name_value_1, tmp_default_value_1);
            if (tmp_tuple_element_3 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 137;
                type_description_2 = "o";
                goto try_except_handler_7;
            }
            tmp_mod_expr_right_1 = MAKE_TUPLE_EMPTY(tstate, 2);
            {
                PyObject *tmp_expression_value_6;
                PyObject *tmp_type_arg_2;
                PyTuple_SET_ITEM(tmp_mod_expr_right_1, 0, tmp_tuple_element_3);
                CHECK_OBJECT(tmp_classproperty$$36$class_creation_1__prepared);
                tmp_type_arg_2 = tmp_classproperty$$36$class_creation_1__prepared;
                tmp_expression_value_6 = BUILTIN_TYPE1(tmp_type_arg_2);
                assert(!(tmp_expression_value_6 == NULL));
                tmp_tuple_element_3 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_6, mod_consts[36]);
                Py_DECREF(tmp_expression_value_6);
                if (tmp_tuple_element_3 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                    exception_lineno = 137;
                    type_description_2 = "o";
                    goto tuple_build_exception_1;
                }
                PyTuple_SET_ITEM(tmp_mod_expr_right_1, 1, tmp_tuple_element_3);
            }
            goto tuple_build_noexception_1;
            // Exception handling pass through code for tuple_build:
            tuple_build_exception_1:;
            Py_DECREF(tmp_mod_expr_right_1);
            goto try_except_handler_7;
            // Finished with no exception for tuple_build:
            tuple_build_noexception_1:;
            tmp_make_exception_arg_1 = BINARY_OPERATION_MOD_OBJECT_UNICODE_TUPLE(tmp_mod_expr_left_1, tmp_mod_expr_right_1);
            Py_DECREF(tmp_mod_expr_right_1);
            if (tmp_make_exception_arg_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 137;
                type_description_2 = "o";
                goto try_except_handler_7;
            }
            frame_frame_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_2->m_frame.f_lineno = 137;
            tmp_raise_type_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_TypeError, tmp_make_exception_arg_1);
            Py_DECREF(tmp_make_exception_arg_1);
            assert(!(tmp_raise_type_1 == NULL));
            exception_state.exception_type = tmp_raise_type_1;
            exception_lineno = 137;
            RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);
            type_description_2 = "o";
            goto try_except_handler_7;
        }
        branch_no_2:;
        goto branch_end_1;
        branch_no_1:;
        {
            PyObject *tmp_assign_source_15;
            tmp_assign_source_15 = MAKE_DICT_EMPTY(tstate);
            assert(tmp_classproperty$$36$class_creation_1__prepared == NULL);
            tmp_classproperty$$36$class_creation_1__prepared = tmp_assign_source_15;
        }
        branch_end_1:;
        outline_2_var___class__ = Nuitka_Cell_NewEmpty();
        {
            PyObject *tmp_set_locals_3;
            CHECK_OBJECT(tmp_classproperty$$36$class_creation_1__prepared);
            tmp_set_locals_3 = tmp_classproperty$$36$class_creation_1__prepared;
            locals_keyring$compat$properties$$36$$$36$$$36$class__3_Meta_137 = tmp_set_locals_3;
            Py_INCREF(tmp_set_locals_3);
        }
        // Tried code:
        // Tried code:
        tmp_dictset_value = mod_consts[22];
        tmp_res = PyObject_SetItem(locals_keyring$compat$properties$$36$$$36$$$36$class__3_Meta_137, mod_consts[23], tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 137;
            type_description_2 = "o";
            goto try_except_handler_9;
        }
        tmp_dictset_value = mod_consts[38];
        tmp_res = PyObject_SetItem(locals_keyring$compat$properties$$36$$$36$$$36$class__3_Meta_137, mod_consts[26], tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 137;
            type_description_2 = "o";
            goto try_except_handler_9;
        }
        frame_frame_keyring$compat$properties$$36$$$36$$$36$class__3_Meta_3 = MAKE_CLASS_FRAME(tstate, code_objects_4f79b28ff871290619a8150704663417, module_keyring$compat$properties, NULL, sizeof(void *));

        // Push the new frame as the currently active one, and we should be exclusively
        // owning it.
        pushFrameStackCompiledFrame(tstate, frame_frame_keyring$compat$properties$$36$$$36$$$36$class__3_Meta_3);
        assert(Py_REFCNT(frame_frame_keyring$compat$properties$$36$$$36$$$36$class__3_Meta_3) == 2);

        // Framed code:
        {
            struct Nuitka_CellObject *tmp_closure_1[1];

            tmp_closure_1[0] = outline_2_var___class__;
            Py_INCREF(tmp_closure_1[0]);

            tmp_dictset_value = MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__3___setattr__(tstate, tmp_closure_1);

            tmp_res = PyObject_SetItem(locals_keyring$compat$properties$$36$$$36$$$36$class__3_Meta_137, mod_consts[8], tmp_dictset_value);
            Py_DECREF(tmp_dictset_value);
            if (tmp_res != 0) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 138;
                type_description_3 = "c";
                goto frame_exception_exit_3;
            }
        }


        // Put the previous frame back on top.
        popFrameStack(tstate);

        goto frame_no_exception_1;
        frame_exception_exit_3:


        {
            PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
            if (exception_tb == NULL) {
                exception_tb = MAKE_TRACEBACK(frame_frame_keyring$compat$properties$$36$$$36$$$36$class__3_Meta_3, exception_lineno);
                SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
            } else if (exception_tb->tb_frame != &frame_frame_keyring$compat$properties$$36$$$36$$$36$class__3_Meta_3->m_frame) {
                exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_keyring$compat$properties$$36$$$36$$$36$class__3_Meta_3, exception_lineno);
                SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
            }
        }

        // Attaches locals to frame if any.
        Nuitka_Frame_AttachLocals(
            frame_frame_keyring$compat$properties$$36$$$36$$$36$class__3_Meta_3,
            type_description_3,
            outline_2_var___class__
        );



        assertFrameObject(frame_frame_keyring$compat$properties$$36$$$36$$$36$class__3_Meta_3);

        // Put the previous frame back on top.
        popFrameStack(tstate);

        // Return the error.
        goto nested_frame_exit_2;
        frame_no_exception_1:;
        goto skip_nested_handling_1;
        nested_frame_exit_2:;
        type_description_2 = "o";
        goto try_except_handler_9;
        skip_nested_handling_1:;
        {
            nuitka_bool tmp_condition_result_4;
            PyObject *tmp_cmp_expr_left_1;
            PyObject *tmp_cmp_expr_right_1;
            CHECK_OBJECT(tmp_classproperty$$36$class_creation_1__bases);
            tmp_cmp_expr_left_1 = tmp_classproperty$$36$class_creation_1__bases;
            tmp_cmp_expr_right_1 = mod_consts[32];
            tmp_condition_result_4 = RICH_COMPARE_NE_NBOOL_OBJECT_TUPLE(tmp_cmp_expr_left_1, tmp_cmp_expr_right_1);
            if (tmp_condition_result_4 == NUITKA_BOOL_EXCEPTION) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 137;
                type_description_2 = "o";
                goto try_except_handler_9;
            }
            if (tmp_condition_result_4 == NUITKA_BOOL_TRUE) {
                goto branch_yes_3;
            } else {
                goto branch_no_3;
            }
        }
        branch_yes_3:;
        tmp_dictset_value = mod_consts[32];
        tmp_res = PyObject_SetItem(locals_keyring$compat$properties$$36$$$36$$$36$class__3_Meta_137, mod_consts[40], tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 137;
            type_description_2 = "o";
            goto try_except_handler_9;
        }
        branch_no_3:;
        {
            PyObject *tmp_assign_source_16;
            PyObject *tmp_called_value_3;
            PyObject *tmp_args_value_3;
            PyObject *tmp_tuple_element_4;
            PyObject *tmp_kwargs_value_3;
            CHECK_OBJECT(tmp_classproperty$$36$class_creation_1__metaclass);
            tmp_called_value_3 = tmp_classproperty$$36$class_creation_1__metaclass;
            tmp_tuple_element_4 = mod_consts[14];
            tmp_args_value_3 = MAKE_TUPLE_EMPTY(tstate, 3);
            PyTuple_SET_ITEM0(tmp_args_value_3, 0, tmp_tuple_element_4);
            CHECK_OBJECT(tmp_classproperty$$36$class_creation_1__bases);
            tmp_tuple_element_4 = tmp_classproperty$$36$class_creation_1__bases;
            PyTuple_SET_ITEM0(tmp_args_value_3, 1, tmp_tuple_element_4);
            tmp_tuple_element_4 = locals_keyring$compat$properties$$36$$$36$$$36$class__3_Meta_137;
            PyTuple_SET_ITEM0(tmp_args_value_3, 2, tmp_tuple_element_4);
            CHECK_OBJECT(tmp_classproperty$$36$class_creation_1__class_decl_dict);
            tmp_kwargs_value_3 = tmp_classproperty$$36$class_creation_1__class_decl_dict;
            frame_frame_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_2->m_frame.f_lineno = 137;
            tmp_assign_source_16 = CALL_FUNCTION(tstate, tmp_called_value_3, tmp_args_value_3, tmp_kwargs_value_3);
            Py_DECREF(tmp_args_value_3);
            if (tmp_assign_source_16 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 137;
                type_description_2 = "o";
                goto try_except_handler_9;
            }
            assert(Nuitka_Cell_GET(outline_2_var___class__) == NULL);
            Nuitka_Cell_SET(outline_2_var___class__, tmp_assign_source_16);

        }
        CHECK_OBJECT(Nuitka_Cell_GET(outline_2_var___class__));
        tmp_dictset_value = Nuitka_Cell_GET(outline_2_var___class__);
        Py_INCREF(tmp_dictset_value);
        goto try_return_handler_9;
        NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
        return NULL;
        // Return handler code:
        try_return_handler_9:;
        Py_DECREF(locals_keyring$compat$properties$$36$$$36$$$36$class__3_Meta_137);
        locals_keyring$compat$properties$$36$$$36$$$36$class__3_Meta_137 = NULL;
        goto try_return_handler_8;
        // Exception handler code:
        try_except_handler_9:;
        exception_keeper_lineno_4 = exception_lineno;
        exception_lineno = 0;
        exception_keeper_name_4 = exception_state;
        INIT_ERROR_OCCURRED_STATE(&exception_state);

        Py_DECREF(locals_keyring$compat$properties$$36$$$36$$$36$class__3_Meta_137);
        locals_keyring$compat$properties$$36$$$36$$$36$class__3_Meta_137 = NULL;
        // Re-raise.
        exception_state = exception_keeper_name_4;
        exception_lineno = exception_keeper_lineno_4;

        goto try_except_handler_8;
        // End of try:
        NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
        return NULL;
        // Return handler code:
        try_return_handler_8:;
        CHECK_OBJECT(outline_2_var___class__);
        Py_DECREF(outline_2_var___class__);
        outline_2_var___class__ = NULL;
        goto outline_result_3;
        // Exception handler code:
        try_except_handler_8:;
        exception_keeper_lineno_5 = exception_lineno;
        exception_lineno = 0;
        exception_keeper_name_5 = exception_state;
        INIT_ERROR_OCCURRED_STATE(&exception_state);

        // Re-raise.
        exception_state = exception_keeper_name_5;
        exception_lineno = exception_keeper_lineno_5;

        goto outline_exception_3;
        // End of try:
        NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
        return NULL;
        outline_exception_3:;
        exception_lineno = 137;
        goto try_except_handler_7;
        outline_result_3:;
        tmp_result = DICT_SET_ITEM(locals_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_34, mod_consts[14], tmp_dictset_value);
        Py_DECREF(tmp_dictset_value);
        if (tmp_result == false) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 137;
            type_description_2 = "o";
            goto try_except_handler_7;
        }
        goto try_end_2;
        // Exception handler code:
        try_except_handler_7:;
        exception_keeper_lineno_6 = exception_lineno;
        exception_lineno = 0;
        exception_keeper_name_6 = exception_state;
        INIT_ERROR_OCCURRED_STATE(&exception_state);

        Py_XDECREF(tmp_classproperty$$36$class_creation_1__bases);
        tmp_classproperty$$36$class_creation_1__bases = NULL;
        Py_XDECREF(tmp_classproperty$$36$class_creation_1__class_decl_dict);
        tmp_classproperty$$36$class_creation_1__class_decl_dict = NULL;
        Py_XDECREF(tmp_classproperty$$36$class_creation_1__metaclass);
        tmp_classproperty$$36$class_creation_1__metaclass = NULL;
        Py_XDECREF(tmp_classproperty$$36$class_creation_1__prepared);
        tmp_classproperty$$36$class_creation_1__prepared = NULL;
        // Re-raise.
        exception_state = exception_keeper_name_6;
        exception_lineno = exception_keeper_lineno_6;

        goto frame_exception_exit_2;
        // End of try:
        try_end_2:;


        // Put the previous frame back on top.
        popFrameStack(tstate);

        goto frame_no_exception_2;
        frame_exception_exit_2:


        {
            PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
            if (exception_tb == NULL) {
                exception_tb = MAKE_TRACEBACK(frame_frame_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_2, exception_lineno);
                SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
            } else if (exception_tb->tb_frame != &frame_frame_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_2->m_frame) {
                exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_2, exception_lineno);
                SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
            }
        }

        // Attaches locals to frame if any.
        Nuitka_Frame_AttachLocals(
            frame_frame_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_2,
            type_description_2,
            outline_1_var___class__
        );



        assertFrameObject(frame_frame_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_2);

        // Put the previous frame back on top.
        popFrameStack(tstate);

        // Return the error.
        goto nested_frame_exit_1;
        frame_no_exception_2:;
        goto skip_nested_handling_2;
        nested_frame_exit_1:;

        goto try_except_handler_6;
        skip_nested_handling_2:;
        CHECK_OBJECT(tmp_classproperty$$36$class_creation_1__bases);
        Py_DECREF(tmp_classproperty$$36$class_creation_1__bases);
        tmp_classproperty$$36$class_creation_1__bases = NULL;
        CHECK_OBJECT(tmp_classproperty$$36$class_creation_1__class_decl_dict);
        Py_DECREF(tmp_classproperty$$36$class_creation_1__class_decl_dict);
        tmp_classproperty$$36$class_creation_1__class_decl_dict = NULL;
        CHECK_OBJECT(tmp_classproperty$$36$class_creation_1__metaclass);
        Py_DECREF(tmp_classproperty$$36$class_creation_1__metaclass);
        tmp_classproperty$$36$class_creation_1__metaclass = NULL;
        CHECK_OBJECT(tmp_classproperty$$36$class_creation_1__prepared);
        Py_DECREF(tmp_classproperty$$36$class_creation_1__prepared);
        tmp_classproperty$$36$class_creation_1__prepared = NULL;
        {
            PyObject *tmp_defaults_2;
            tmp_defaults_2 = mod_consts[29];
            Py_INCREF(tmp_defaults_2);


            tmp_dictset_value = MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__4___init__(tstate, tmp_defaults_2);

            tmp_result = DICT_SET_ITEM(locals_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_34, mod_consts[27], tmp_dictset_value);
            Py_DECREF(tmp_dictset_value);
            assert(!(tmp_result == false));
        }
        {
            PyObject *tmp_defaults_3;
            tmp_defaults_3 = mod_consts[29];
            Py_INCREF(tmp_defaults_3);


            tmp_dictset_value = MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__5___get__(tstate, tmp_defaults_3);

            tmp_result = DICT_SET_ITEM(locals_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_34, mod_consts[12], tmp_dictset_value);
            Py_DECREF(tmp_dictset_value);
            assert(!(tmp_result == false));
        }


        tmp_dictset_value = MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__6___set__(tstate);

        tmp_result = DICT_SET_ITEM(locals_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_34, mod_consts[6], tmp_dictset_value);
        Py_DECREF(tmp_dictset_value);
        assert(!(tmp_result == false));


        tmp_dictset_value = MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__7_setter(tstate);

        tmp_result = DICT_SET_ITEM(locals_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_34, mod_consts[11], tmp_dictset_value);
        Py_DECREF(tmp_dictset_value);
        assert(!(tmp_result == false));
        {
            PyObject *tmp_classmethod_arg_1;


            tmp_classmethod_arg_1 = MAKE_FUNCTION_keyring$compat$properties$$36$$$36$$$36$function__8__ensure_method(tstate);

            tmp_dictset_value = BUILTIN_CLASSMETHOD(tstate, tmp_classmethod_arg_1);
            Py_DECREF(tmp_classmethod_arg_1);
            assert(!(tmp_dictset_value == NULL));
            tmp_result = DICT_SET_ITEM(locals_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_34, mod_consts[9], tmp_dictset_value);
            Py_DECREF(tmp_dictset_value);
            assert(!(tmp_result == false));
        }
        {
            PyObject *tmp_assign_source_17;
            PyObject *tmp_called_value_4;
            PyObject *tmp_args_value_4;
            PyObject *tmp_tuple_element_5;
            PyObject *tmp_kwargs_value_4;
            tmp_called_value_4 = (PyObject *)&PyType_Type;
            tmp_tuple_element_5 = mod_consts[5];
            tmp_args_value_4 = MAKE_TUPLE_EMPTY(tstate, 3);
            PyTuple_SET_ITEM0(tmp_args_value_4, 0, tmp_tuple_element_5);
            tmp_tuple_element_5 = const_tuple_empty;
            PyTuple_SET_ITEM0(tmp_args_value_4, 1, tmp_tuple_element_5);
            tmp_tuple_element_5 = locals_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_34;
            PyTuple_SET_ITEM0(tmp_args_value_4, 2, tmp_tuple_element_5);
            CHECK_OBJECT(tmp_class_creation_2__class_decl_dict);
            tmp_kwargs_value_4 = tmp_class_creation_2__class_decl_dict;
            frame_frame_keyring$compat$properties->m_frame.f_lineno = 34;
            tmp_assign_source_17 = CALL_FUNCTION(tstate, tmp_called_value_4, tmp_args_value_4, tmp_kwargs_value_4);
            Py_DECREF(tmp_args_value_4);
            if (tmp_assign_source_17 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 34;

                goto try_except_handler_6;
            }
            assert(outline_1_var___class__ == NULL);
            outline_1_var___class__ = tmp_assign_source_17;
        }
        CHECK_OBJECT(outline_1_var___class__);
        tmp_assign_source_10 = outline_1_var___class__;
        Py_INCREF(tmp_assign_source_10);
        goto try_return_handler_6;
        NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
        return NULL;
        // Return handler code:
        try_return_handler_6:;
        Py_DECREF(locals_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_34);
        locals_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_34 = NULL;
        goto try_return_handler_5;
        // Exception handler code:
        try_except_handler_6:;
        exception_keeper_lineno_7 = exception_lineno;
        exception_lineno = 0;
        exception_keeper_name_7 = exception_state;
        INIT_ERROR_OCCURRED_STATE(&exception_state);

        Py_DECREF(locals_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_34);
        locals_keyring$compat$properties$$36$$$36$$$36$class__2_classproperty_34 = NULL;
        // Re-raise.
        exception_state = exception_keeper_name_7;
        exception_lineno = exception_keeper_lineno_7;

        goto try_except_handler_5;
        // End of try:
        NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
        return NULL;
        // Return handler code:
        try_return_handler_5:;
        CHECK_OBJECT(outline_1_var___class__);
        Py_DECREF(outline_1_var___class__);
        outline_1_var___class__ = NULL;
        goto outline_result_2;
        // Exception handler code:
        try_except_handler_5:;
        exception_keeper_lineno_8 = exception_lineno;
        exception_lineno = 0;
        exception_keeper_name_8 = exception_state;
        INIT_ERROR_OCCURRED_STATE(&exception_state);

        // Re-raise.
        exception_state = exception_keeper_name_8;
        exception_lineno = exception_keeper_lineno_8;

        goto outline_exception_2;
        // End of try:
        NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
        return NULL;
        outline_exception_2:;
        exception_lineno = 34;
        goto try_except_handler_4;
        outline_result_2:;
        UPDATE_STRING_DICT1(moduledict_keyring$compat$properties, (Nuitka_StringObject *)mod_consts[5], tmp_assign_source_10);
    }
    goto try_end_3;
    // Exception handler code:
    try_except_handler_4:;
    exception_keeper_lineno_9 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_9 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    CHECK_OBJECT(tmp_class_creation_2__class_decl_dict);
    Py_DECREF(tmp_class_creation_2__class_decl_dict);
    tmp_class_creation_2__class_decl_dict = NULL;
    CHECK_OBJECT(tmp_class_creation_2__prepared);
    Py_DECREF(tmp_class_creation_2__prepared);
    tmp_class_creation_2__prepared = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_9;
    exception_lineno = exception_keeper_lineno_9;

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
            exception_tb = MAKE_TRACEBACK(frame_frame_keyring$compat$properties, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_keyring$compat$properties->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_keyring$compat$properties, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }



    assertFrameObject(frame_frame_keyring$compat$properties);

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
    PGO_onModuleExit("keyring$compat$properties", false);

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *post_load = IMPORT_EMBEDDED_MODULE(tstate, "keyring.compat.properties" "-postLoad");
        if (post_load == NULL) {
            return NULL;
        }
    }
#endif

    Py_INCREF(module_keyring$compat$properties);
    return module_keyring$compat$properties;
    module_exception_exit:

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_keyring$compat$properties, (Nuitka_StringObject *)const_str_plain___name__);

        if (module_name != NULL) {
            Nuitka_DelModule(tstate, module_name);
        }
    }
#endif
    PGO_onModuleExit("keyring$compat$properties", false);

    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);
    return NULL;
}
