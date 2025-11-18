/* Generated code for Python module 'Crypto$Util$py3compat'
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

/* The "module_Crypto$Util$py3compat" is a Python object pointer of module type.
 *
 * Note: For full compatibility with CPython, every module variable access
 * needs to go through it except for cases where the module cannot possibly
 * have changed in the mean time.
 */

PyObject *module_Crypto$Util$py3compat;
PyDictObject *moduledict_Crypto$Util$py3compat;

/* The declarations of module constants used, if any. */
static PyObject *mod_consts[43];
#ifndef __NUITKA_NO_ASSERT__
static Py_hash_t mod_consts_hash[43];
#endif

static PyObject *module_filename_obj = NULL;

/* Indicator if this modules private constants were created yet. */
static bool constants_created = false;

/* Function to create module private constants. */
static void createModuleConstants(PyThreadState *tstate) {
    if (constants_created == false) {
        loadConstantsBlob(tstate, &mod_consts[0], UN_TRANSLATE("Crypto.Util.py3compat"));
        constants_created = true;

#ifndef __NUITKA_NO_ASSERT__
        for (int i = 0; i < 43; i++) {
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
void checkModuleConstants_Crypto$Util$py3compat(PyThreadState *tstate) {
    // The module may not have been used at all, then ignore this.
    if (constants_created == false) return;

    for (int i = 0; i < 43; i++) {
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
static PyObject *module_var_accessor_Crypto$$36$Util$$36$py3compat$FileNotFoundError(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_Crypto$Util$py3compat->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_Crypto$Util$py3compat->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[31]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_Crypto$Util$py3compat->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[31]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[31], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[31]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[31], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[31]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[31]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[31]);
    }

    return result;
}

static PyObject *module_var_accessor_Crypto$$36$Util$$36$py3compat$__spec__(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_Crypto$Util$py3compat->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_Crypto$Util$py3compat->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[42]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_Crypto$Util$py3compat->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[42]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[42], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[42]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[42], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[42]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[42]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[42]);
    }

    return result;
}


#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
// The module code objects.
static PyCodeObject *code_objects_ebdbe7d9dfcbf31dec3e9e8adf8ae06f;
static PyCodeObject *code_objects_b5c9618f870af0e5f35c61cb2d77eb6d;
static PyCodeObject *code_objects_58db51c911d84d7744816865ba8c9dd7;
static PyCodeObject *code_objects_c178357efee95b3e933e2fe6d42aaf1c;
static PyCodeObject *code_objects_2387738b6e508c25c6a3a6d47675662e;
static PyCodeObject *code_objects_962c168f206e54e7973f793b863a3c47;
static PyCodeObject *code_objects_636682cd90bdb20aa83f95a69d464473;
static PyCodeObject *code_objects_0b6122a5d916a537a3658f908c9f2de1;
static PyCodeObject *code_objects_e5d288375cdfe3cbc573465e5bfe1a83;
static PyCodeObject *code_objects_97e9a039eadc72e26a484720b92cd9e8;
static PyCodeObject *code_objects_3107e85e05c796564e9bbd9ea25c8ed6;
static PyCodeObject *code_objects_3d2faf8c69a5e2a33b8db6ec74f75c46;
static PyCodeObject *code_objects_c809308fe905634056a362d089afc7fc;

static void createModuleCodeObjects(void) {
    module_filename_obj = MAKE_RELATIVE_PATH(mod_consts[33]); CHECK_OBJECT(module_filename_obj);
    code_objects_ebdbe7d9dfcbf31dec3e9e8adf8ae06f = MAKE_CODE_OBJECT(module_filename_obj, 1, CO_NOFREE, mod_consts[34], mod_consts[34], NULL, NULL, 0, 0, 0);
    code_objects_b5c9618f870af0e5f35c61cb2d77eb6d = MAKE_CODE_OBJECT(module_filename_obj, 173, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[32], mod_consts[32], mod_consts[35], NULL, 3, 0, 0);
    code_objects_58db51c911d84d7744816865ba8c9dd7 = MAKE_CODE_OBJECT(module_filename_obj, 121, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[14], mod_consts[14], mod_consts[36], NULL, 1, 0, 0);
    code_objects_c178357efee95b3e933e2fe6d42aaf1c = MAKE_CODE_OBJECT(module_filename_obj, 123, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[15], mod_consts[15], mod_consts[36], NULL, 1, 0, 0);
    code_objects_2387738b6e508c25c6a3a6d47675662e = MAKE_CODE_OBJECT(module_filename_obj, 130, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[17], mod_consts[17], mod_consts[36], NULL, 1, 0, 0);
    code_objects_962c168f206e54e7973f793b863a3c47 = MAKE_CODE_OBJECT(module_filename_obj, 125, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[16], mod_consts[16], mod_consts[36], NULL, 1, 0, 0);
    code_objects_636682cd90bdb20aa83f95a69d464473 = MAKE_CODE_OBJECT(module_filename_obj, 145, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[19], mod_consts[19], mod_consts[36], NULL, 1, 0, 0);
    code_objects_0b6122a5d916a537a3658f908c9f2de1 = MAKE_CODE_OBJECT(module_filename_obj, 148, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[20], mod_consts[20], mod_consts[37], NULL, 2, 0, 0);
    code_objects_e5d288375cdfe3cbc573465e5bfe1a83 = MAKE_CODE_OBJECT(module_filename_obj, 163, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[28], mod_consts[28], mod_consts[38], NULL, 1, 0, 0);
    code_objects_97e9a039eadc72e26a484720b92cd9e8 = MAKE_CODE_OBJECT(module_filename_obj, 157, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[26], mod_consts[26], mod_consts[38], NULL, 1, 0, 0);
    code_objects_3107e85e05c796564e9bbd9ea25c8ed6 = MAKE_CODE_OBJECT(module_filename_obj, 160, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[27], mod_consts[27], mod_consts[38], NULL, 1, 0, 0);
    code_objects_3d2faf8c69a5e2a33b8db6ec74f75c46 = MAKE_CODE_OBJECT(module_filename_obj, 132, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[3], mod_consts[3], mod_consts[39], NULL, 2, 0, 0);
    code_objects_c809308fe905634056a362d089afc7fc = MAKE_CODE_OBJECT(module_filename_obj, 143, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[18], mod_consts[18], mod_consts[40], NULL, 1, 0, 0);
}
#endif

// The module function declarations.
static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__15_bord(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes(PyThreadState *tstate, PyObject *defaults);


static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes(PyThreadState *tstate);


// The module function definitions.
static PyObject *impl_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_s = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b)) {
        Py_XDECREF(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b = MAKE_FUNCTION_FRAME(tstate, code_objects_58db51c911d84d7744816865ba8c9dd7, module_Crypto$Util$py3compat, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b->m_type_description == NULL);
    frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b = cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b);
    assert(Py_REFCNT(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_expression_value_1;
        CHECK_OBJECT(par_s);
        tmp_expression_value_1 = par_s;
        tmp_called_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[0]);
        if (tmp_called_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 122;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b->m_frame.f_lineno = 122;
        tmp_return_value = CALL_FUNCTION_WITH_POS_ARGS1(tstate, tmp_called_value_1, mod_consts[1]);

        Py_DECREF(tmp_called_value_1);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 122;
            type_description_1 = "o";
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
            exception_tb = MAKE_TRACEBACK(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b,
        type_description_1,
        par_s
    );


    // Release cached frame if used for exception.
    if (frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b == cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b);
        cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b = NULL;
    }

    assertFrameObject(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_s);
    Py_DECREF(par_s);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_s);
    Py_DECREF(par_s);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_s = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr)) {
        Py_XDECREF(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr = MAKE_FUNCTION_FRAME(tstate, code_objects_c178357efee95b3e933e2fe6d42aaf1c, module_Crypto$Util$py3compat, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr->m_type_description == NULL);
    frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr = cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr);
    assert(Py_REFCNT(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr) == 2);

    // Framed code:
    {
        PyObject *tmp_bytes_arg_1;
        PyObject *tmp_list_element_1;
        CHECK_OBJECT(par_s);
        tmp_list_element_1 = par_s;
        tmp_bytes_arg_1 = MAKE_LIST_EMPTY(tstate, 1);
        PyList_SET_ITEM0(tmp_bytes_arg_1, 0, tmp_list_element_1);
        tmp_return_value = BUILTIN_BYTES1(tstate, tmp_bytes_arg_1);
        Py_DECREF(tmp_bytes_arg_1);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 124;
            type_description_1 = "o";
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
            exception_tb = MAKE_TRACEBACK(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr,
        type_description_1,
        par_s
    );


    // Release cached frame if used for exception.
    if (frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr == cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr);
        cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr = NULL;
    }

    assertFrameObject(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_s);
    Py_DECREF(par_s);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_s);
    Py_DECREF(par_s);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_s = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    int tmp_res;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    PyObject *tmp_return_value = NULL;
    static struct Nuitka_FrameObject *cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr)) {
        Py_XDECREF(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr = MAKE_FUNCTION_FRAME(tstate, code_objects_962c168f206e54e7973f793b863a3c47, module_Crypto$Util$py3compat, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr->m_type_description == NULL);
    frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr = cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr);
    assert(Py_REFCNT(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr) == 2);

    // Framed code:
    {
        nuitka_bool tmp_condition_result_1;
        PyObject *tmp_isinstance_inst_1;
        PyObject *tmp_isinstance_cls_1;
        CHECK_OBJECT(par_s);
        tmp_isinstance_inst_1 = par_s;
        tmp_isinstance_cls_1 = (PyObject *)&PyUnicode_Type;
        tmp_res = PyObject_IsInstance(tmp_isinstance_inst_1, tmp_isinstance_cls_1);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 126;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_1 = (tmp_res != 0) ? NUITKA_BOOL_TRUE : NUITKA_BOOL_FALSE;
        if (tmp_condition_result_1 == NUITKA_BOOL_TRUE) {
            goto branch_yes_1;
        } else {
            goto branch_no_1;
        }
    }
    branch_yes_1:;
    {
        PyObject *tmp_bytes_arg_1;
        PyObject *tmp_bytes_encoding_1;
        CHECK_OBJECT(par_s);
        tmp_bytes_arg_1 = par_s;
        tmp_bytes_encoding_1 = mod_consts[2];
        tmp_return_value = BUILTIN_BYTES3(tstate, tmp_bytes_arg_1, tmp_bytes_encoding_1, NULL);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 127;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        goto frame_return_exit_1;
    }
    goto branch_end_1;
    branch_no_1:;
    {
        PyObject *tmp_bytes_arg_2;
        CHECK_OBJECT(par_s);
        tmp_bytes_arg_2 = par_s;
        tmp_return_value = BUILTIN_BYTES1(tstate, tmp_bytes_arg_2);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 129;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        goto frame_return_exit_1;
    }
    branch_end_1:;


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
            exception_tb = MAKE_TRACEBACK(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr,
        type_description_1,
        par_s
    );


    // Release cached frame if used for exception.
    if (frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr == cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr);
        cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr = NULL;
    }

    assertFrameObject(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_s);
    Py_DECREF(par_s);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_s);
    Py_DECREF(par_s);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_Crypto$Util$py3compat$$36$$$36$$$36$function__15_bord(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_s = python_pars[0];
    PyObject *tmp_return_value = NULL;

    // Actual function body.
    CHECK_OBJECT(par_s);
    tmp_return_value = par_s;
    Py_INCREF(tmp_return_value);
    goto function_return_exit;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_s);
    Py_DECREF(par_s);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_s = python_pars[0];
    PyObject *par_encoding = python_pars[1];
    struct Nuitka_FrameObject *frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    int tmp_res;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    PyObject *tmp_return_value = NULL;
    static struct Nuitka_FrameObject *cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes)) {
        Py_XDECREF(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes = MAKE_FUNCTION_FRAME(tstate, code_objects_3d2faf8c69a5e2a33b8db6ec74f75c46, module_Crypto$Util$py3compat, sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes->m_type_description == NULL);
    frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes = cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes);
    assert(Py_REFCNT(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes) == 2);

    // Framed code:
    {
        nuitka_bool tmp_condition_result_1;
        PyObject *tmp_isinstance_inst_1;
        PyObject *tmp_isinstance_cls_1;
        CHECK_OBJECT(par_s);
        tmp_isinstance_inst_1 = par_s;
        tmp_isinstance_cls_1 = (PyObject *)&PyBytes_Type;
        tmp_res = PyObject_IsInstance(tmp_isinstance_inst_1, tmp_isinstance_cls_1);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 133;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_1 = (tmp_res != 0) ? NUITKA_BOOL_TRUE : NUITKA_BOOL_FALSE;
        if (tmp_condition_result_1 == NUITKA_BOOL_TRUE) {
            goto branch_yes_1;
        } else {
            goto branch_no_1;
        }
    }
    branch_yes_1:;
    CHECK_OBJECT(par_s);
    tmp_return_value = par_s;
    Py_INCREF(tmp_return_value);
    goto frame_return_exit_1;
    goto branch_end_1;
    branch_no_1:;
    {
        nuitka_bool tmp_condition_result_2;
        PyObject *tmp_isinstance_inst_2;
        PyObject *tmp_isinstance_cls_2;
        CHECK_OBJECT(par_s);
        tmp_isinstance_inst_2 = par_s;
        tmp_isinstance_cls_2 = (PyObject *)&PyByteArray_Type;
        tmp_res = PyObject_IsInstance(tmp_isinstance_inst_2, tmp_isinstance_cls_2);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 135;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_2 = (tmp_res != 0) ? NUITKA_BOOL_TRUE : NUITKA_BOOL_FALSE;
        if (tmp_condition_result_2 == NUITKA_BOOL_TRUE) {
            goto branch_yes_2;
        } else {
            goto branch_no_2;
        }
    }
    branch_yes_2:;
    {
        PyObject *tmp_bytes_arg_1;
        CHECK_OBJECT(par_s);
        tmp_bytes_arg_1 = par_s;
        tmp_return_value = BUILTIN_BYTES1(tstate, tmp_bytes_arg_1);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 136;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        goto frame_return_exit_1;
    }
    goto branch_end_2;
    branch_no_2:;
    {
        nuitka_bool tmp_condition_result_3;
        PyObject *tmp_isinstance_inst_3;
        PyObject *tmp_isinstance_cls_3;
        CHECK_OBJECT(par_s);
        tmp_isinstance_inst_3 = par_s;
        tmp_isinstance_cls_3 = (PyObject *)&PyUnicode_Type;
        tmp_res = PyObject_IsInstance(tmp_isinstance_inst_3, tmp_isinstance_cls_3);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 137;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_3 = (tmp_res != 0) ? NUITKA_BOOL_TRUE : NUITKA_BOOL_FALSE;
        if (tmp_condition_result_3 == NUITKA_BOOL_TRUE) {
            goto branch_yes_3;
        } else {
            goto branch_no_3;
        }
    }
    branch_yes_3:;
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_expression_value_1;
        PyObject *tmp_args_element_value_1;
        CHECK_OBJECT(par_s);
        tmp_expression_value_1 = par_s;
        tmp_called_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[0]);
        if (tmp_called_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 138;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_encoding);
        tmp_args_element_value_1 = par_encoding;
        frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes->m_frame.f_lineno = 138;
        tmp_return_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_1, tmp_args_element_value_1);
        Py_DECREF(tmp_called_value_1);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 138;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        goto frame_return_exit_1;
    }
    goto branch_end_3;
    branch_no_3:;
    {
        nuitka_bool tmp_condition_result_4;
        PyObject *tmp_isinstance_inst_4;
        PyObject *tmp_isinstance_cls_4;
        CHECK_OBJECT(par_s);
        tmp_isinstance_inst_4 = par_s;
        tmp_isinstance_cls_4 = (PyObject *)&PyMemoryView_Type;
        tmp_res = PyObject_IsInstance(tmp_isinstance_inst_4, tmp_isinstance_cls_4);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 139;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_4 = (tmp_res != 0) ? NUITKA_BOOL_TRUE : NUITKA_BOOL_FALSE;
        if (tmp_condition_result_4 == NUITKA_BOOL_TRUE) {
            goto branch_yes_4;
        } else {
            goto branch_no_4;
        }
    }
    branch_yes_4:;
    {
        PyObject *tmp_called_instance_1;
        CHECK_OBJECT(par_s);
        tmp_called_instance_1 = par_s;
        frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes->m_frame.f_lineno = 140;
        tmp_return_value = CALL_METHOD_NO_ARGS(tstate, tmp_called_instance_1, mod_consts[3]);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 140;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        goto frame_return_exit_1;
    }
    goto branch_end_4;
    branch_no_4:;
    {
        PyObject *tmp_bytes_arg_2;
        PyObject *tmp_list_element_1;
        CHECK_OBJECT(par_s);
        tmp_list_element_1 = par_s;
        tmp_bytes_arg_2 = MAKE_LIST_EMPTY(tstate, 1);
        PyList_SET_ITEM0(tmp_bytes_arg_2, 0, tmp_list_element_1);
        tmp_return_value = BUILTIN_BYTES1(tstate, tmp_bytes_arg_2);
        Py_DECREF(tmp_bytes_arg_2);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 142;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        goto frame_return_exit_1;
    }
    branch_end_4:;
    branch_end_3:;
    branch_end_2:;
    branch_end_1:;


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
            exception_tb = MAKE_TRACEBACK(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes,
        type_description_1,
        par_s,
        par_encoding
    );


    // Release cached frame if used for exception.
    if (frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes == cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes);
        cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes = NULL;
    }

    assertFrameObject(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_s);
    Py_DECREF(par_s);
    CHECK_OBJECT(par_encoding);
    Py_DECREF(par_encoding);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_s);
    Py_DECREF(par_s);
    CHECK_OBJECT(par_encoding);
    Py_DECREF(par_encoding);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_bs = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr)) {
        Py_XDECREF(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr = MAKE_FUNCTION_FRAME(tstate, code_objects_c809308fe905634056a362d089afc7fc, module_Crypto$Util$py3compat, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr->m_type_description == NULL);
    frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr = cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr);
    assert(Py_REFCNT(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_expression_value_1;
        CHECK_OBJECT(par_bs);
        tmp_expression_value_1 = par_bs;
        tmp_called_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[4]);
        if (tmp_called_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 144;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr->m_frame.f_lineno = 144;
        tmp_return_value = CALL_FUNCTION_WITH_POS_ARGS1(tstate, tmp_called_value_1, mod_consts[1]);

        Py_DECREF(tmp_called_value_1);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 144;
            type_description_1 = "o";
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
            exception_tb = MAKE_TRACEBACK(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr,
        type_description_1,
        par_bs
    );


    // Release cached frame if used for exception.
    if (frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr == cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr);
        cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr = NULL;
    }

    assertFrameObject(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_bs);
    Py_DECREF(par_bs);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_bs);
    Py_DECREF(par_bs);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_s = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    int tmp_res;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string)) {
        Py_XDECREF(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string = MAKE_FUNCTION_FRAME(tstate, code_objects_636682cd90bdb20aa83f95a69d464473, module_Crypto$Util$py3compat, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string->m_type_description == NULL);
    frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string = cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string);
    assert(Py_REFCNT(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string) == 2);

    // Framed code:
    {
        PyObject *tmp_isinstance_inst_1;
        PyObject *tmp_isinstance_cls_1;
        CHECK_OBJECT(par_s);
        tmp_isinstance_inst_1 = par_s;
        tmp_isinstance_cls_1 = (PyObject *)&PyBytes_Type;
        tmp_res = PyObject_IsInstance(tmp_isinstance_inst_1, tmp_isinstance_cls_1);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 146;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_return_value = (tmp_res != 0) ? Py_True : Py_False;
        Py_INCREF(tmp_return_value);
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
            exception_tb = MAKE_TRACEBACK(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string,
        type_description_1,
        par_s
    );


    // Release cached frame if used for exception.
    if (frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string == cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string);
        cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string = NULL;
    }

    assertFrameObject(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_s);
    Py_DECREF(par_s);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_s);
    Py_DECREF(par_s);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_a = python_pars[0];
    PyObject *par_b = python_pars[1];
    struct Nuitka_FrameObject *frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers)) {
        Py_XDECREF(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers = MAKE_FUNCTION_FRAME(tstate, code_objects_0b6122a5d916a537a3658f908c9f2de1, module_Crypto$Util$py3compat, sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers->m_type_description == NULL);
    frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers = cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers);
    assert(Py_REFCNT(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers) == 2);

    // Framed code:
    {
        PyObject *tmp_add_expr_left_1;
        PyObject *tmp_add_expr_right_1;
        CHECK_OBJECT(par_a);
        tmp_add_expr_left_1 = par_a;
        CHECK_OBJECT(par_b);
        tmp_add_expr_right_1 = par_b;
        tmp_return_value = BINARY_OPERATION_ADD_OBJECT_OBJECT_OBJECT(tmp_add_expr_left_1, tmp_add_expr_right_1);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 149;
            type_description_1 = "oo";
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
            exception_tb = MAKE_TRACEBACK(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers,
        type_description_1,
        par_a,
        par_b
    );


    // Release cached frame if used for exception.
    if (frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers == cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers);
        cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers = NULL;
    }

    assertFrameObject(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_a);
    Py_DECREF(par_a);
    CHECK_OBJECT(par_b);
    Py_DECREF(par_b);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_a);
    Py_DECREF(par_a);
    CHECK_OBJECT(par_b);
    Py_DECREF(par_b);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_x = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    int tmp_res;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int)) {
        Py_XDECREF(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int = MAKE_FUNCTION_FRAME(tstate, code_objects_97e9a039eadc72e26a484720b92cd9e8, module_Crypto$Util$py3compat, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int->m_type_description == NULL);
    frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int = cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int);
    assert(Py_REFCNT(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int) == 2);

    // Framed code:
    {
        PyObject *tmp_isinstance_inst_1;
        PyObject *tmp_isinstance_cls_1;
        CHECK_OBJECT(par_x);
        tmp_isinstance_inst_1 = par_x;
        tmp_isinstance_cls_1 = (PyObject *)&PyLong_Type;
        tmp_res = PyObject_IsInstance(tmp_isinstance_inst_1, tmp_isinstance_cls_1);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 158;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_return_value = (tmp_res != 0) ? Py_True : Py_False;
        Py_INCREF(tmp_return_value);
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
            exception_tb = MAKE_TRACEBACK(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int,
        type_description_1,
        par_x
    );


    // Release cached frame if used for exception.
    if (frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int == cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int);
        cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int = NULL;
    }

    assertFrameObject(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_x);
    Py_DECREF(par_x);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_x);
    Py_DECREF(par_x);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_x = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    int tmp_res;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string)) {
        Py_XDECREF(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string = MAKE_FUNCTION_FRAME(tstate, code_objects_3107e85e05c796564e9bbd9ea25c8ed6, module_Crypto$Util$py3compat, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string->m_type_description == NULL);
    frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string = cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string);
    assert(Py_REFCNT(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string) == 2);

    // Framed code:
    {
        PyObject *tmp_isinstance_inst_1;
        PyObject *tmp_isinstance_cls_1;
        CHECK_OBJECT(par_x);
        tmp_isinstance_inst_1 = par_x;
        tmp_isinstance_cls_1 = (PyObject *)&PyUnicode_Type;
        tmp_res = PyObject_IsInstance(tmp_isinstance_inst_1, tmp_isinstance_cls_1);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 161;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_return_value = (tmp_res != 0) ? Py_True : Py_False;
        Py_INCREF(tmp_return_value);
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
            exception_tb = MAKE_TRACEBACK(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string,
        type_description_1,
        par_x
    );


    // Release cached frame if used for exception.
    if (frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string == cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string);
        cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string = NULL;
    }

    assertFrameObject(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_x);
    Py_DECREF(par_x);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_x);
    Py_DECREF(par_x);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_x = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    int tmp_res;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes)) {
        Py_XDECREF(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes = MAKE_FUNCTION_FRAME(tstate, code_objects_e5d288375cdfe3cbc573465e5bfe1a83, module_Crypto$Util$py3compat, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes->m_type_description == NULL);
    frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes = cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes);
    assert(Py_REFCNT(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes) == 2);

    // Framed code:
    {
        int tmp_or_left_truth_1;
        PyObject *tmp_or_left_value_1;
        PyObject *tmp_or_right_value_1;
        PyObject *tmp_isinstance_inst_1;
        PyObject *tmp_isinstance_cls_1;
        int tmp_or_left_truth_2;
        PyObject *tmp_or_left_value_2;
        PyObject *tmp_or_right_value_2;
        PyObject *tmp_isinstance_inst_2;
        PyObject *tmp_isinstance_cls_2;
        PyObject *tmp_isinstance_inst_3;
        PyObject *tmp_isinstance_cls_3;
        CHECK_OBJECT(par_x);
        tmp_isinstance_inst_1 = par_x;
        tmp_isinstance_cls_1 = (PyObject *)&PyBytes_Type;
        tmp_res = PyObject_IsInstance(tmp_isinstance_inst_1, tmp_isinstance_cls_1);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 164;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_or_left_value_1 = (tmp_res != 0) ? Py_True : Py_False;
        tmp_or_left_truth_1 = CHECK_IF_TRUE(tmp_or_left_value_1);
        if (tmp_or_left_truth_1 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 164;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        if (tmp_or_left_truth_1 == 1) {
            goto or_left_1;
        } else {
            goto or_right_1;
        }
        or_right_1:;
        CHECK_OBJECT(par_x);
        tmp_isinstance_inst_2 = par_x;
        tmp_isinstance_cls_2 = (PyObject *)&PyByteArray_Type;
        tmp_res = PyObject_IsInstance(tmp_isinstance_inst_2, tmp_isinstance_cls_2);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 165;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_or_left_value_2 = (tmp_res != 0) ? Py_True : Py_False;
        tmp_or_left_truth_2 = CHECK_IF_TRUE(tmp_or_left_value_2);
        if (tmp_or_left_truth_2 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 165;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        if (tmp_or_left_truth_2 == 1) {
            goto or_left_2;
        } else {
            goto or_right_2;
        }
        or_right_2:;
        CHECK_OBJECT(par_x);
        tmp_isinstance_inst_3 = par_x;
        tmp_isinstance_cls_3 = (PyObject *)&PyMemoryView_Type;
        tmp_res = PyObject_IsInstance(tmp_isinstance_inst_3, tmp_isinstance_cls_3);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 166;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_or_right_value_2 = (tmp_res != 0) ? Py_True : Py_False;
        tmp_or_right_value_1 = tmp_or_right_value_2;
        goto or_end_2;
        or_left_2:;
        tmp_or_right_value_1 = tmp_or_left_value_2;
        or_end_2:;
        tmp_return_value = tmp_or_right_value_1;
        goto or_end_1;
        or_left_1:;
        tmp_return_value = tmp_or_left_value_1;
        or_end_1:;
        Py_INCREF(tmp_return_value);
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
            exception_tb = MAKE_TRACEBACK(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes,
        type_description_1,
        par_x
    );


    // Release cached frame if used for exception.
    if (frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes == cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes);
        cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes = NULL;
    }

    assertFrameObject(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_x);
    Py_DECREF(par_x);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_x);
    Py_DECREF(par_x);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_start = python_pars[0];
    PyObject *par_end = python_pars[1];
    PyObject *par_seq = python_pars[2];
    struct Nuitka_FrameObject *frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    int tmp_res;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    PyObject *tmp_return_value = NULL;
    static struct Nuitka_FrameObject *cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes)) {
        Py_XDECREF(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes = MAKE_FUNCTION_FRAME(tstate, code_objects_b5c9618f870af0e5f35c61cb2d77eb6d, module_Crypto$Util$py3compat, sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes->m_type_description == NULL);
    frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes = cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes);
    assert(Py_REFCNT(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes) == 2);

    // Framed code:
    {
        nuitka_bool tmp_condition_result_1;
        PyObject *tmp_isinstance_inst_1;
        PyObject *tmp_isinstance_cls_1;
        CHECK_OBJECT(par_seq);
        tmp_isinstance_inst_1 = par_seq;
        tmp_isinstance_cls_1 = (PyObject *)&PyMemoryView_Type;
        tmp_res = PyObject_IsInstance(tmp_isinstance_inst_1, tmp_isinstance_cls_1);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 177;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_1 = (tmp_res != 0) ? NUITKA_BOOL_TRUE : NUITKA_BOOL_FALSE;
        if (tmp_condition_result_1 == NUITKA_BOOL_TRUE) {
            goto branch_yes_1;
        } else {
            goto branch_no_1;
        }
    }
    branch_yes_1:;
    {
        PyObject *tmp_called_instance_1;
        PyObject *tmp_expression_value_1;
        PyObject *tmp_subscript_value_1;
        PyObject *tmp_start_value_1;
        PyObject *tmp_stop_value_1;
        CHECK_OBJECT(par_seq);
        tmp_expression_value_1 = par_seq;
        CHECK_OBJECT(par_start);
        tmp_start_value_1 = par_start;
        CHECK_OBJECT(par_end);
        tmp_stop_value_1 = par_end;
        tmp_subscript_value_1 = MAKE_SLICE_OBJECT2(tstate, tmp_start_value_1, tmp_stop_value_1);
        assert(!(tmp_subscript_value_1 == NULL));
        tmp_called_instance_1 = LOOKUP_SUBSCRIPT(tstate, tmp_expression_value_1, tmp_subscript_value_1);
        Py_DECREF(tmp_subscript_value_1);
        if (tmp_called_instance_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 178;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes->m_frame.f_lineno = 178;
        tmp_return_value = CALL_METHOD_NO_ARGS(tstate, tmp_called_instance_1, mod_consts[3]);
        Py_DECREF(tmp_called_instance_1);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 178;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        goto frame_return_exit_1;
    }
    goto branch_end_1;
    branch_no_1:;
    {
        nuitka_bool tmp_condition_result_2;
        PyObject *tmp_isinstance_inst_2;
        PyObject *tmp_isinstance_cls_2;
        CHECK_OBJECT(par_seq);
        tmp_isinstance_inst_2 = par_seq;
        tmp_isinstance_cls_2 = (PyObject *)&PyByteArray_Type;
        tmp_res = PyObject_IsInstance(tmp_isinstance_inst_2, tmp_isinstance_cls_2);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 179;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_2 = (tmp_res != 0) ? NUITKA_BOOL_TRUE : NUITKA_BOOL_FALSE;
        if (tmp_condition_result_2 == NUITKA_BOOL_TRUE) {
            goto branch_yes_2;
        } else {
            goto branch_no_2;
        }
    }
    branch_yes_2:;
    {
        PyObject *tmp_bytes_arg_1;
        PyObject *tmp_expression_value_2;
        PyObject *tmp_subscript_value_2;
        PyObject *tmp_start_value_2;
        PyObject *tmp_stop_value_2;
        CHECK_OBJECT(par_seq);
        tmp_expression_value_2 = par_seq;
        CHECK_OBJECT(par_start);
        tmp_start_value_2 = par_start;
        CHECK_OBJECT(par_end);
        tmp_stop_value_2 = par_end;
        tmp_subscript_value_2 = MAKE_SLICE_OBJECT2(tstate, tmp_start_value_2, tmp_stop_value_2);
        assert(!(tmp_subscript_value_2 == NULL));
        tmp_bytes_arg_1 = LOOKUP_SUBSCRIPT(tstate, tmp_expression_value_2, tmp_subscript_value_2);
        Py_DECREF(tmp_subscript_value_2);
        if (tmp_bytes_arg_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 180;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        tmp_return_value = BUILTIN_BYTES1(tstate, tmp_bytes_arg_1);
        Py_DECREF(tmp_bytes_arg_1);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 180;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        goto frame_return_exit_1;
    }
    goto branch_end_2;
    branch_no_2:;
    {
        PyObject *tmp_expression_value_3;
        PyObject *tmp_subscript_value_3;
        PyObject *tmp_start_value_3;
        PyObject *tmp_stop_value_3;
        CHECK_OBJECT(par_seq);
        tmp_expression_value_3 = par_seq;
        CHECK_OBJECT(par_start);
        tmp_start_value_3 = par_start;
        CHECK_OBJECT(par_end);
        tmp_stop_value_3 = par_end;
        tmp_subscript_value_3 = MAKE_SLICE_OBJECT2(tstate, tmp_start_value_3, tmp_stop_value_3);
        assert(!(tmp_subscript_value_3 == NULL));
        tmp_return_value = LOOKUP_SUBSCRIPT(tstate, tmp_expression_value_3, tmp_subscript_value_3);
        Py_DECREF(tmp_subscript_value_3);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 182;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        goto frame_return_exit_1;
    }
    branch_end_2:;
    branch_end_1:;


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
            exception_tb = MAKE_TRACEBACK(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes,
        type_description_1,
        par_start,
        par_end,
        par_seq
    );


    // Release cached frame if used for exception.
    if (frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes == cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes);
        cache_frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes = NULL;
    }

    assertFrameObject(frame_frame_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_start);
    Py_DECREF(par_start);
    CHECK_OBJECT(par_end);
    Py_DECREF(par_end);
    CHECK_OBJECT(par_seq);
    Py_DECREF(par_seq);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_start);
    Py_DECREF(par_start);
    CHECK_OBJECT(par_end);
    Py_DECREF(par_end);
    CHECK_OBJECT(par_seq);
    Py_DECREF(par_seq);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}



static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b,
        mod_consts[14],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_58db51c911d84d7744816865ba8c9dd7,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_Crypto$Util$py3compat,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr,
        mod_consts[15],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_c178357efee95b3e933e2fe6d42aaf1c,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_Crypto$Util$py3compat,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr,
        mod_consts[16],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_962c168f206e54e7973f793b863a3c47,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_Crypto$Util$py3compat,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__15_bord(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_Crypto$Util$py3compat$$36$$$36$$$36$function__15_bord,
        mod_consts[17],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_2387738b6e508c25c6a3a6d47675662e,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_Crypto$Util$py3compat,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes(PyThreadState *tstate, PyObject *defaults) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes,
        mod_consts[3],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_3d2faf8c69a5e2a33b8db6ec74f75c46,
        defaults,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_Crypto$Util$py3compat,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr,
        mod_consts[18],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_c809308fe905634056a362d089afc7fc,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_Crypto$Util$py3compat,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string,
        mod_consts[19],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_636682cd90bdb20aa83f95a69d464473,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_Crypto$Util$py3compat,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers,
        mod_consts[20],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_0b6122a5d916a537a3658f908c9f2de1,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_Crypto$Util$py3compat,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int,
        mod_consts[26],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_97e9a039eadc72e26a484720b92cd9e8,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_Crypto$Util$py3compat,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string,
        mod_consts[27],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_3107e85e05c796564e9bbd9ea25c8ed6,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_Crypto$Util$py3compat,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes,
        mod_consts[28],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_e5d288375cdfe3cbc573465e5bfe1a83,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_Crypto$Util$py3compat,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes,
        mod_consts[32],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_b5c9618f870af0e5f35c61cb2d77eb6d,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_Crypto$Util$py3compat,
        mod_consts[5],
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

static function_impl_code const function_table_Crypto$Util$py3compat[] = {
    impl_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b,
    impl_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr,
    impl_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr,
    impl_Crypto$Util$py3compat$$36$$$36$$$36$function__15_bord,
    impl_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes,
    impl_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr,
    impl_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string,
    impl_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers,
    impl_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int,
    impl_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string,
    impl_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes,
    impl_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes,
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

    return Nuitka_Function_GetFunctionState(function, function_table_Crypto$Util$py3compat);
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
        module_Crypto$Util$py3compat,
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
        function_table_Crypto$Util$py3compat,
        sizeof(function_table_Crypto$Util$py3compat) / sizeof(function_impl_code)
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
static char const *module_full_name = "Crypto.Util.py3compat";
#endif

// Internal entry point for module code.
PyObject *modulecode_Crypto$Util$py3compat(PyThreadState *tstate, PyObject *module, struct Nuitka_MetaPathBasedLoaderEntry const *loader_entry) {
    // Report entry to PGO.
    PGO_onModuleEntered("Crypto$Util$py3compat");

    // Store the module for future use.
    module_Crypto$Util$py3compat = module;

    moduledict_Crypto$Util$py3compat = MODULE_DICT(module_Crypto$Util$py3compat);

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
        PRINT_STRING("Crypto$Util$py3compat: Calling setupMetaPathBasedLoader().\n");
#endif
        setupMetaPathBasedLoader(tstate);
#if 0 >= 0
#ifdef _NUITKA_TRACE
        PRINT_STRING("Crypto$Util$py3compat: Calling updateMetaPathBasedLoaderModuleRoot().\n");
#endif
        updateMetaPathBasedLoaderModuleRoot(module_full_name);
#endif


#if PYTHON_VERSION >= 0x300
        patchInspectModule(tstate);
#endif

#endif

        /* The constants only used by this module are created now. */
        NUITKA_PRINT_TRACE("Crypto$Util$py3compat: Calling createModuleConstants().\n");
        createModuleConstants(tstate);

#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
        createModuleCodeObjects();
#endif
        init_done = true;
    }

#if _NUITKA_MODULE_MODE && 0
    PyObject *pre_load = IMPORT_EMBEDDED_MODULE(tstate, "Crypto.Util.py3compat" "-preLoad");
    if (pre_load == NULL) {
        return NULL;
    }
#endif

    // PRINT_STRING("in initCrypto$Util$py3compat\n");

#ifdef _NUITKA_PLUGIN_DILL_ENABLED
    {
        char const *module_name_c;
        if (loader_entry != NULL) {
            module_name_c = loader_entry->name;
        } else {
            PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)const_str_plain___name__);
            module_name_c = Nuitka_String_AsString(module_name);
        }

        registerDillPluginTables(tstate, module_name_c, &_method_def_reduce_compiled_function, &_method_def_create_compiled_function);
    }
#endif

    // Set "__compiled__" to what version information we have.
    UPDATE_STRING_DICT0(
        moduledict_Crypto$Util$py3compat,
        (Nuitka_StringObject *)const_str_plain___compiled__,
        Nuitka_dunder_compiled_value
    );

    // Update "__package__" value to what it ought to be.
    {
#if 0
        UPDATE_STRING_DICT0(
            moduledict_Crypto$Util$py3compat,
            (Nuitka_StringObject *)const_str_plain___package__,
            mod_consts[41]
        );
#elif 0
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)const_str_plain___name__);

        UPDATE_STRING_DICT0(
            moduledict_Crypto$Util$py3compat,
            (Nuitka_StringObject *)const_str_plain___package__,
            module_name
        );
#else

#if PYTHON_VERSION < 0x300
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)const_str_plain___name__);
        char const *module_name_cstr = PyString_AS_STRING(module_name);

        char const *last_dot = strrchr(module_name_cstr, '.');

        if (last_dot != NULL) {
            UPDATE_STRING_DICT1(
                moduledict_Crypto$Util$py3compat,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyString_FromStringAndSize(module_name_cstr, last_dot - module_name_cstr)
            );
        }
#else
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)const_str_plain___name__);
        Py_ssize_t dot_index = PyUnicode_Find(module_name, const_str_dot, 0, PyUnicode_GetLength(module_name), -1);

        if (dot_index != -1) {
            UPDATE_STRING_DICT1(
                moduledict_Crypto$Util$py3compat,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyUnicode_Substring(module_name, 0, dot_index)
            );
        }
#endif
#endif
    }

    CHECK_OBJECT(module_Crypto$Util$py3compat);

    // For deep importing of a module we need to have "__builtins__", so we set
    // it ourselves in the same way than CPython does. Note: This must be done
    // before the frame object is allocated, or else it may fail.

    if (GET_STRING_DICT_VALUE(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)const_str_plain___builtins__) == NULL) {
        PyObject *value = (PyObject *)builtin_module;

        // Check if main module, not a dict then but the module itself.
#if _NUITKA_MODULE_MODE || !0
        value = PyModule_GetDict(value);
#endif

        UPDATE_STRING_DICT0(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)const_str_plain___builtins__, value);
    }

    PyObject *module_loader = Nuitka_Loader_New(loader_entry);
    UPDATE_STRING_DICT0(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)const_str_plain___loader__, module_loader);

#if PYTHON_VERSION >= 0x300
// Set the "__spec__" value

#if 0
    // Main modules just get "None" as spec.
    UPDATE_STRING_DICT0(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)const_str_plain___spec__, Py_None);
#else
    // Other modules get a "ModuleSpec" from the standard mechanism.
    {
        PyObject *bootstrap_module = getImportLibBootstrapModule();
        CHECK_OBJECT(bootstrap_module);

        PyObject *_spec_from_module = PyObject_GetAttrString(bootstrap_module, "_spec_from_module");
        CHECK_OBJECT(_spec_from_module);

        PyObject *spec_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, _spec_from_module, module_Crypto$Util$py3compat);
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

        UPDATE_STRING_DICT1(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)const_str_plain___spec__, spec_value);
    }
#endif
#endif

    // Temp variables if any
    struct Nuitka_FrameObject *frame_frame_Crypto$Util$py3compat;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    bool tmp_result;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;

    // Module init code if any


    // Module code.
    {
        PyObject *tmp_assign_source_1;
        tmp_assign_source_1 = mod_consts[6];
        UPDATE_STRING_DICT0(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[7], tmp_assign_source_1);
    }
    {
        PyObject *tmp_assign_source_2;
        tmp_assign_source_2 = module_filename_obj;
        UPDATE_STRING_DICT0(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[8], tmp_assign_source_2);
    }
    frame_frame_Crypto$Util$py3compat = MAKE_MODULE_FRAME(code_objects_ebdbe7d9dfcbf31dec3e9e8adf8ae06f, module_Crypto$Util$py3compat);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_Crypto$Util$py3compat);
    assert(Py_REFCNT(frame_frame_Crypto$Util$py3compat) == 2);

    // Framed code:
    {
        PyObject *tmp_assattr_value_1;
        PyObject *tmp_assattr_target_1;
        tmp_assattr_value_1 = module_filename_obj;
        tmp_assattr_target_1 = module_var_accessor_Crypto$$36$Util$$36$py3compat$__spec__(tstate);
        assert(!(tmp_assattr_target_1 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_1, mod_consts[9], tmp_assattr_value_1);
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
        tmp_assattr_target_2 = module_var_accessor_Crypto$$36$Util$$36$py3compat$__spec__(tstate);
        assert(!(tmp_assattr_target_2 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_2, mod_consts[10], tmp_assattr_value_2);
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
        UPDATE_STRING_DICT0(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[11], tmp_assign_source_3);
    }
    {
        PyObject *tmp_assign_source_4;
        tmp_assign_source_4 = IMPORT_HARD_SYS();
        assert(!(tmp_assign_source_4 == NULL));
        UPDATE_STRING_DICT0(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[12], tmp_assign_source_4);
    }
    {
        PyObject *tmp_assign_source_5;
        PyObject *tmp_name_value_1;
        PyObject *tmp_globals_arg_value_1;
        PyObject *tmp_locals_arg_value_1;
        PyObject *tmp_fromlist_value_1;
        PyObject *tmp_level_value_1;
        tmp_name_value_1 = mod_consts[13];
        tmp_globals_arg_value_1 = (PyObject *)moduledict_Crypto$Util$py3compat;
        tmp_locals_arg_value_1 = Py_None;
        tmp_fromlist_value_1 = Py_None;
        tmp_level_value_1 = const_int_0;
        frame_frame_Crypto$Util$py3compat->m_frame.f_lineno = 62;
        tmp_assign_source_5 = IMPORT_MODULE5(tstate, tmp_name_value_1, tmp_globals_arg_value_1, tmp_locals_arg_value_1, tmp_fromlist_value_1, tmp_level_value_1);
        if (tmp_assign_source_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 62;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[13], tmp_assign_source_5);
    }
    {
        PyObject *tmp_assign_source_6;


        tmp_assign_source_6 = MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__12_b(tstate);

        UPDATE_STRING_DICT1(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[14], tmp_assign_source_6);
    }
    {
        PyObject *tmp_assign_source_7;


        tmp_assign_source_7 = MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__13_bchr(tstate);

        UPDATE_STRING_DICT1(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[15], tmp_assign_source_7);
    }
    {
        PyObject *tmp_assign_source_8;


        tmp_assign_source_8 = MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__14_bstr(tstate);

        UPDATE_STRING_DICT1(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[16], tmp_assign_source_8);
    }
    {
        PyObject *tmp_assign_source_9;


        tmp_assign_source_9 = MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__15_bord(tstate);

        UPDATE_STRING_DICT1(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[17], tmp_assign_source_9);
    }
    {
        PyObject *tmp_assign_source_10;
        PyObject *tmp_defaults_1;
        tmp_defaults_1 = mod_consts[1];
        Py_INCREF(tmp_defaults_1);


        tmp_assign_source_10 = MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__16_tobytes(tstate, tmp_defaults_1);

        UPDATE_STRING_DICT1(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[3], tmp_assign_source_10);
    }
    {
        PyObject *tmp_assign_source_11;


        tmp_assign_source_11 = MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__17_tostr(tstate);

        UPDATE_STRING_DICT1(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[18], tmp_assign_source_11);
    }
    {
        PyObject *tmp_assign_source_12;


        tmp_assign_source_12 = MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__18_byte_string(tstate);

        UPDATE_STRING_DICT1(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[19], tmp_assign_source_12);
    }
    {
        PyObject *tmp_assign_source_13;


        tmp_assign_source_13 = MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__19_concat_buffers(tstate);

        UPDATE_STRING_DICT1(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[20], tmp_assign_source_13);
    }
    {
        PyObject *tmp_assign_source_14;
        {
            PyObject *hard_module = IMPORT_HARD_IO();
            tmp_assign_source_14 = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[21]);
        }
        assert(!(tmp_assign_source_14 == NULL));
        UPDATE_STRING_DICT1(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[21], tmp_assign_source_14);
    }
    {
        PyObject *tmp_assign_source_15;
        {
            PyObject *hard_module = IMPORT_HARD_IO();
            tmp_assign_source_15 = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[22]);
        }
        assert(!(tmp_assign_source_15 == NULL));
        UPDATE_STRING_DICT1(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[22], tmp_assign_source_15);
    }
    {
        PyObject *tmp_assign_source_16;
        tmp_assign_source_16 = mod_consts[23];
        UPDATE_STRING_DICT0(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[24], tmp_assign_source_16);
    }
    {
        PyObject *tmp_assign_source_17;
        tmp_assign_source_17 = (PyObject *)&PyRange_Type;
        UPDATE_STRING_DICT0(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[25], tmp_assign_source_17);
    }
    {
        PyObject *tmp_assign_source_18;


        tmp_assign_source_18 = MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__20_is_native_int(tstate);

        UPDATE_STRING_DICT1(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[26], tmp_assign_source_18);
    }
    {
        PyObject *tmp_assign_source_19;


        tmp_assign_source_19 = MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__21_is_string(tstate);

        UPDATE_STRING_DICT1(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[27], tmp_assign_source_19);
    }
    {
        PyObject *tmp_assign_source_20;


        tmp_assign_source_20 = MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__22_is_bytes(tstate);

        UPDATE_STRING_DICT1(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[28], tmp_assign_source_20);
    }
    {
        PyObject *tmp_assign_source_21;
        PyObject *tmp_import_name_from_1;
        PyObject *tmp_name_value_2;
        PyObject *tmp_globals_arg_value_2;
        PyObject *tmp_locals_arg_value_2;
        PyObject *tmp_fromlist_value_2;
        PyObject *tmp_level_value_2;
        tmp_name_value_2 = mod_consts[13];
        tmp_globals_arg_value_2 = (PyObject *)moduledict_Crypto$Util$py3compat;
        tmp_locals_arg_value_2 = Py_None;
        tmp_fromlist_value_2 = mod_consts[29];
        tmp_level_value_2 = const_int_0;
        frame_frame_Crypto$Util$py3compat->m_frame.f_lineno = 168;
        tmp_import_name_from_1 = IMPORT_MODULE5(tstate, tmp_name_value_2, tmp_globals_arg_value_2, tmp_locals_arg_value_2, tmp_fromlist_value_2, tmp_level_value_2);
        if (tmp_import_name_from_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 168;

            goto frame_exception_exit_1;
        }
        if (PyModule_Check(tmp_import_name_from_1)) {
            tmp_assign_source_21 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_1,
                (PyObject *)moduledict_Crypto$Util$py3compat,
                mod_consts[30],
                const_int_0
            );
        } else {
            tmp_assign_source_21 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_1, mod_consts[30]);
        }

        Py_DECREF(tmp_import_name_from_1);
        if (tmp_assign_source_21 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 168;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[30], tmp_assign_source_21);
    }
    {
        PyObject *tmp_assign_source_22;
        tmp_assign_source_22 = module_var_accessor_Crypto$$36$Util$$36$py3compat$FileNotFoundError(tstate);
        if (unlikely(tmp_assign_source_22 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[31]);
        }

        if (tmp_assign_source_22 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 170;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT0(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[31], tmp_assign_source_22);
    }
    {
        PyObject *tmp_assign_source_23;


        tmp_assign_source_23 = MAKE_FUNCTION_Crypto$Util$py3compat$$36$$$36$$$36$function__23__copy_bytes(tstate);

        UPDATE_STRING_DICT1(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)mod_consts[32], tmp_assign_source_23);
    }
    if (DICT_REMOVE_ITEM((PyObject *)moduledict_Crypto$Util$py3compat, mod_consts[12]) == false) {
        CLEAR_ERROR_OCCURRED(tstate);
    }

    tmp_result = DICT_REMOVE_ITEM((PyObject *)moduledict_Crypto$Util$py3compat, mod_consts[13]);
    if (tmp_result == false) CLEAR_ERROR_OCCURRED(tstate);

    if (unlikely(tmp_result == false)) {

    RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[13]);

        exception_lineno = 185;

        goto frame_exception_exit_1;
    }



    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_Crypto$Util$py3compat, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_Crypto$Util$py3compat->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_Crypto$Util$py3compat, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }



    assertFrameObject(frame_frame_Crypto$Util$py3compat);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto module_exception_exit;
    frame_no_exception_1:;

    // Report to PGO about leaving the module without error.
    PGO_onModuleExit("Crypto$Util$py3compat", false);

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *post_load = IMPORT_EMBEDDED_MODULE(tstate, "Crypto.Util.py3compat" "-postLoad");
        if (post_load == NULL) {
            return NULL;
        }
    }
#endif

    Py_INCREF(module_Crypto$Util$py3compat);
    return module_Crypto$Util$py3compat;
    module_exception_exit:

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_Crypto$Util$py3compat, (Nuitka_StringObject *)const_str_plain___name__);

        if (module_name != NULL) {
            Nuitka_DelModule(tstate, module_name);
        }
    }
#endif
    PGO_onModuleExit("Crypto$Util$py3compat", false);

    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);
    return NULL;
}
