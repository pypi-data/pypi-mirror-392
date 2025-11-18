/* Generated code for Python module 'oauthlib$openid$connect$core$request_validator'
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

/* The "module_oauthlib$openid$connect$core$request_validator" is a Python object pointer of module type.
 *
 * Note: For full compatibility with CPython, every module variable access
 * needs to go through it except for cases where the module cannot possibly
 * have changed in the mean time.
 */

PyObject *module_oauthlib$openid$connect$core$request_validator;
PyDictObject *moduledict_oauthlib$openid$connect$core$request_validator;

/* The declarations of module constants used, if any. */
static PyObject *mod_consts[71];
#ifndef __NUITKA_NO_ASSERT__
static Py_hash_t mod_consts_hash[71];
#endif

static PyObject *module_filename_obj = NULL;

/* Indicator if this modules private constants were created yet. */
static bool constants_created = false;

/* Function to create module private constants. */
static void createModuleConstants(PyThreadState *tstate) {
    if (constants_created == false) {
        loadConstantsBlob(tstate, &mod_consts[0], UN_TRANSLATE("oauthlib.openid.connect.core.request_validator"));
        constants_created = true;

#ifndef __NUITKA_NO_ASSERT__
        for (int i = 0; i < 71; i++) {
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
void checkModuleConstants_oauthlib$openid$connect$core$request_validator(PyThreadState *tstate) {
    // The module may not have been used at all, then ignore this.
    if (constants_created == false) return;

    for (int i = 0; i < 71; i++) {
        assert(mod_consts_hash[i] == DEEP_HASH(tstate, mod_consts[i]));
        CHECK_OBJECT_DEEP(mod_consts[i]);
    }
}
#endif

// Helper to preserving module variables for Python3.11+
#if 3
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
static PyObject *module_var_accessor_oauthlib$$36$openid$$36$connect$$36$core$$36$request_validator$OAuth2RequestValidator(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_oauthlib$openid$connect$core$request_validator->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_oauthlib$openid$connect$core$request_validator->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)mod_consts[20]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_oauthlib$openid$connect$core$request_validator->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[20]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[20], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[20]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[20], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)mod_consts[20]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)mod_consts[20]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[20]);
    }

    return result;
}

static PyObject *module_var_accessor_oauthlib$$36$openid$$36$connect$$36$core$$36$request_validator$__spec__(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_oauthlib$openid$connect$core$request_validator->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_oauthlib$openid$connect$core$request_validator->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)mod_consts[70]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_oauthlib$openid$connect$core$request_validator->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[70]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[70], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[70]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[70], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)mod_consts[70]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)mod_consts[70]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[70]);
    }

    return result;
}

static PyObject *module_var_accessor_oauthlib$$36$openid$$36$connect$$36$core$$36$request_validator$logging(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_oauthlib$openid$connect$core$request_validator->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_oauthlib$openid$connect$core$request_validator->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)mod_consts[16]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_oauthlib$openid$connect$core$request_validator->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[16]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[16], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[16]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[16], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)mod_consts[16]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)mod_consts[16]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[16]);
    }

    return result;
}


#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
// The module code objects.
static PyCodeObject *code_objects_862a6e86879ab6dbcea3ab916f74c4b8;
static PyCodeObject *code_objects_2940e4c6965bb30bb3703c5d3195d93e;
static PyCodeObject *code_objects_a559dbb41441742ebbfb3257bb12136f;
static PyCodeObject *code_objects_2b5b4775c1b881dbd1f4cbfb9aed13a0;
static PyCodeObject *code_objects_7ff29d7c5f8372a788bd3e8e573516a1;
static PyCodeObject *code_objects_acd65de89031090bfa3b29e4c122bf20;
static PyCodeObject *code_objects_53c55c1ad69a8660add90f7f1ac4703f;
static PyCodeObject *code_objects_f1246e39074db2b0b2ba838fb6626612;
static PyCodeObject *code_objects_c4fb5e295089e719c08c31d0cc7a5747;
static PyCodeObject *code_objects_06a467eff7c3f17b779d106621eb7fe9;
static PyCodeObject *code_objects_74bdfa392711ebc8bf05f5fcfcf62be5;
static PyCodeObject *code_objects_30b6ae8af35e345b28621a996a5d548d;
static PyCodeObject *code_objects_c621f50285b0d6eeb9275a6bc2d28cbb;
static PyCodeObject *code_objects_fe4fcc65943cd104abcad1d5fb552d87;

static void createModuleCodeObjects(void) {
    module_filename_obj = MAKE_RELATIVE_PATH(mod_consts[60]); CHECK_OBJECT(module_filename_obj);
    code_objects_862a6e86879ab6dbcea3ab916f74c4b8 = MAKE_CODE_OBJECT(module_filename_obj, 1, CO_NOFREE, mod_consts[61], mod_consts[61], NULL, NULL, 0, 0, 0);
    code_objects_2940e4c6965bb30bb3703c5d3195d93e = MAKE_CODE_OBJECT(module_filename_obj, 14, CO_NOFREE, mod_consts[19], mod_consts[19], mod_consts[62], NULL, 0, 0, 0);
    code_objects_a559dbb41441742ebbfb3257bb12136f = MAKE_CODE_OBJECT(module_filename_obj, 119, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[41], mod_consts[42], mod_consts[63], NULL, 5, 0, 0);
    code_objects_2b5b4775c1b881dbd1f4cbfb9aed13a0 = MAKE_CODE_OBJECT(module_filename_obj, 40, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[34], mod_consts[35], mod_consts[64], NULL, 5, 0, 0);
    code_objects_7ff29d7c5f8372a788bd3e8e573516a1 = MAKE_CODE_OBJECT(module_filename_obj, 16, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[32], mod_consts[33], mod_consts[64], NULL, 5, 0, 0);
    code_objects_acd65de89031090bfa3b29e4c122bf20 = MAKE_CODE_OBJECT(module_filename_obj, 80, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[39], mod_consts[40], mod_consts[65], NULL, 4, 0, 0);
    code_objects_53c55c1ad69a8660add90f7f1ac4703f = MAKE_CODE_OBJECT(module_filename_obj, 64, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[36], mod_consts[37], mod_consts[65], NULL, 4, 0, 0);
    code_objects_f1246e39074db2b0b2ba838fb6626612 = MAKE_CODE_OBJECT(module_filename_obj, 268, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[54], mod_consts[55], mod_consts[66], NULL, 2, 0, 0);
    code_objects_c4fb5e295089e719c08c31d0cc7a5747 = MAKE_CODE_OBJECT(module_filename_obj, 310, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[57], mod_consts[58], mod_consts[66], NULL, 2, 0, 0);
    code_objects_06a467eff7c3f17b779d106621eb7fe9 = MAKE_CODE_OBJECT(module_filename_obj, 188, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[45], mod_consts[46], mod_consts[67], NULL, 4, 0, 0);
    code_objects_74bdfa392711ebc8bf05f5fcfcf62be5 = MAKE_CODE_OBJECT(module_filename_obj, 162, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[43], mod_consts[44], mod_consts[67], NULL, 4, 0, 0);
    code_objects_30b6ae8af35e345b28621a996a5d548d = MAKE_CODE_OBJECT(module_filename_obj, 210, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[47], mod_consts[48], mod_consts[66], NULL, 2, 0, 0);
    code_objects_c621f50285b0d6eeb9275a6bc2d28cbb = MAKE_CODE_OBJECT(module_filename_obj, 227, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[49], mod_consts[50], mod_consts[66], NULL, 2, 0, 0);
    code_objects_fe4fcc65943cd104abcad1d5fb552d87 = MAKE_CODE_OBJECT(module_filename_obj, 248, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[51], mod_consts[52], mod_consts[68], NULL, 5, 0, 0);
}
#endif

// The module function declarations.
NUITKA_CROSS_MODULE PyObject *impl___main__$$36$$$36$$$36$helper_function__mro_entries_conversion(PyThreadState *tstate, PyObject **python_pars);


static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__11_get_userinfo_claims(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__12_refresh_id_token(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__4_get_id_token(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login(PyThreadState *tstate);


// The module function definitions.
static PyObject *impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_client_id = python_pars[1];
    PyObject *par_code = python_pars[2];
    PyObject *par_redirect_uri = python_pars[3];
    PyObject *par_request = python_pars[4];
    struct Nuitka_FrameObject *frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes)) {
        Py_XDECREF(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes = MAKE_FUNCTION_FRAME(tstate, code_objects_7ff29d7c5f8372a788bd3e8e573516a1, module_oauthlib$openid$connect$core$request_validator, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes->m_type_description == NULL);
    frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes = cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes);
    assert(Py_REFCNT(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes) == 2);

    // Framed code:
    {
        PyObject *tmp_raise_type_1;
        PyObject *tmp_make_exception_arg_1;
        tmp_make_exception_arg_1 = mod_consts[0];
        frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes->m_frame.f_lineno = 38;
        tmp_raise_type_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_NotImplementedError, tmp_make_exception_arg_1);
        assert(!(tmp_raise_type_1 == NULL));
        exception_state.exception_type = tmp_raise_type_1;
        exception_lineno = 38;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);
        type_description_1 = "ooooo";
        goto frame_exception_exit_1;
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes,
        type_description_1,
        par_self,
        par_client_id,
        par_code,
        par_redirect_uri,
        par_request
    );


    // Release cached frame if used for exception.
    if (frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes == cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes);
        cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes = NULL;
    }

    assertFrameObject(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes);

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
    CHECK_OBJECT(par_client_id);
    Py_DECREF(par_client_id);
    CHECK_OBJECT(par_code);
    Py_DECREF(par_code);
    CHECK_OBJECT(par_redirect_uri);
    Py_DECREF(par_redirect_uri);
    CHECK_OBJECT(par_request);
    Py_DECREF(par_request);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

}


static PyObject *impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_client_id = python_pars[1];
    PyObject *par_code = python_pars[2];
    PyObject *par_redirect_uri = python_pars[3];
    PyObject *par_request = python_pars[4];
    struct Nuitka_FrameObject *frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce)) {
        Py_XDECREF(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce = MAKE_FUNCTION_FRAME(tstate, code_objects_2b5b4775c1b881dbd1f4cbfb9aed13a0, module_oauthlib$openid$connect$core$request_validator, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce->m_type_description == NULL);
    frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce = cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce);
    assert(Py_REFCNT(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce) == 2);

    // Framed code:
    {
        PyObject *tmp_raise_type_1;
        PyObject *tmp_make_exception_arg_1;
        tmp_make_exception_arg_1 = mod_consts[0];
        frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce->m_frame.f_lineno = 62;
        tmp_raise_type_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_NotImplementedError, tmp_make_exception_arg_1);
        assert(!(tmp_raise_type_1 == NULL));
        exception_state.exception_type = tmp_raise_type_1;
        exception_lineno = 62;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);
        type_description_1 = "ooooo";
        goto frame_exception_exit_1;
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce,
        type_description_1,
        par_self,
        par_client_id,
        par_code,
        par_redirect_uri,
        par_request
    );


    // Release cached frame if used for exception.
    if (frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce == cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce);
        cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce = NULL;
    }

    assertFrameObject(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce);

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
    CHECK_OBJECT(par_client_id);
    Py_DECREF(par_client_id);
    CHECK_OBJECT(par_code);
    Py_DECREF(par_code);
    CHECK_OBJECT(par_redirect_uri);
    Py_DECREF(par_redirect_uri);
    CHECK_OBJECT(par_request);
    Py_DECREF(par_request);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

}


static PyObject *impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_token = python_pars[1];
    PyObject *par_token_handler = python_pars[2];
    PyObject *par_request = python_pars[3];
    struct Nuitka_FrameObject *frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token)) {
        Py_XDECREF(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token = MAKE_FUNCTION_FRAME(tstate, code_objects_53c55c1ad69a8660add90f7f1ac4703f, module_oauthlib$openid$connect$core$request_validator, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token->m_type_description == NULL);
    frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token = cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token);
    assert(Py_REFCNT(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token) == 2);

    // Framed code:
    {
        PyObject *tmp_raise_type_1;
        PyObject *tmp_make_exception_arg_1;
        tmp_make_exception_arg_1 = mod_consts[0];
        frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token->m_frame.f_lineno = 78;
        tmp_raise_type_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_NotImplementedError, tmp_make_exception_arg_1);
        assert(!(tmp_raise_type_1 == NULL));
        exception_state.exception_type = tmp_raise_type_1;
        exception_lineno = 78;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);
        type_description_1 = "oooo";
        goto frame_exception_exit_1;
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token,
        type_description_1,
        par_self,
        par_token,
        par_token_handler,
        par_request
    );


    // Release cached frame if used for exception.
    if (frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token == cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token);
        cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token = NULL;
    }

    assertFrameObject(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token);

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
    CHECK_OBJECT(par_token);
    Py_DECREF(par_token);
    CHECK_OBJECT(par_token_handler);
    Py_DECREF(par_token_handler);
    CHECK_OBJECT(par_request);
    Py_DECREF(par_request);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

}


static PyObject *impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_id_token = python_pars[1];
    PyObject *par_token = python_pars[2];
    PyObject *par_token_handler = python_pars[3];
    PyObject *par_request = python_pars[4];
    struct Nuitka_FrameObject *frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token)) {
        Py_XDECREF(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token = MAKE_FUNCTION_FRAME(tstate, code_objects_a559dbb41441742ebbfb3257bb12136f, module_oauthlib$openid$connect$core$request_validator, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token->m_type_description == NULL);
    frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token = cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token);
    assert(Py_REFCNT(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token) == 2);

    // Framed code:
    {
        PyObject *tmp_raise_type_1;
        PyObject *tmp_make_exception_arg_1;
        tmp_make_exception_arg_1 = mod_consts[0];
        frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token->m_frame.f_lineno = 160;
        tmp_raise_type_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_NotImplementedError, tmp_make_exception_arg_1);
        assert(!(tmp_raise_type_1 == NULL));
        exception_state.exception_type = tmp_raise_type_1;
        exception_lineno = 160;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);
        type_description_1 = "ooooo";
        goto frame_exception_exit_1;
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token,
        type_description_1,
        par_self,
        par_id_token,
        par_token,
        par_token_handler,
        par_request
    );


    // Release cached frame if used for exception.
    if (frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token == cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token);
        cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token = NULL;
    }

    assertFrameObject(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token);

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
    CHECK_OBJECT(par_id_token);
    Py_DECREF(par_id_token);
    CHECK_OBJECT(par_token);
    Py_DECREF(par_token);
    CHECK_OBJECT(par_token_handler);
    Py_DECREF(par_token_handler);
    CHECK_OBJECT(par_request);
    Py_DECREF(par_request);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

}


static PyObject *impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_token = python_pars[1];
    PyObject *par_scopes = python_pars[2];
    PyObject *par_request = python_pars[3];
    struct Nuitka_FrameObject *frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token)) {
        Py_XDECREF(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token = MAKE_FUNCTION_FRAME(tstate, code_objects_74bdfa392711ebc8bf05f5fcfcf62be5, module_oauthlib$openid$connect$core$request_validator, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token->m_type_description == NULL);
    frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token = cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token);
    assert(Py_REFCNT(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token) == 2);

    // Framed code:
    {
        PyObject *tmp_raise_type_1;
        PyObject *tmp_make_exception_arg_1;
        tmp_make_exception_arg_1 = mod_consts[0];
        frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token->m_frame.f_lineno = 186;
        tmp_raise_type_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_NotImplementedError, tmp_make_exception_arg_1);
        assert(!(tmp_raise_type_1 == NULL));
        exception_state.exception_type = tmp_raise_type_1;
        exception_lineno = 186;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);
        type_description_1 = "oooo";
        goto frame_exception_exit_1;
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token,
        type_description_1,
        par_self,
        par_token,
        par_scopes,
        par_request
    );


    // Release cached frame if used for exception.
    if (frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token == cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token);
        cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token = NULL;
    }

    assertFrameObject(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token);

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
    CHECK_OBJECT(par_token);
    Py_DECREF(par_token);
    CHECK_OBJECT(par_scopes);
    Py_DECREF(par_scopes);
    CHECK_OBJECT(par_request);
    Py_DECREF(par_request);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

}


static PyObject *impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_token = python_pars[1];
    PyObject *par_scopes = python_pars[2];
    PyObject *par_request = python_pars[3];
    struct Nuitka_FrameObject *frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token)) {
        Py_XDECREF(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token = MAKE_FUNCTION_FRAME(tstate, code_objects_06a467eff7c3f17b779d106621eb7fe9, module_oauthlib$openid$connect$core$request_validator, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token->m_type_description == NULL);
    frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token = cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token);
    assert(Py_REFCNT(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token) == 2);

    // Framed code:
    {
        PyObject *tmp_raise_type_1;
        PyObject *tmp_make_exception_arg_1;
        tmp_make_exception_arg_1 = mod_consts[0];
        frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token->m_frame.f_lineno = 208;
        tmp_raise_type_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_NotImplementedError, tmp_make_exception_arg_1);
        assert(!(tmp_raise_type_1 == NULL));
        exception_state.exception_type = tmp_raise_type_1;
        exception_lineno = 208;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);
        type_description_1 = "oooo";
        goto frame_exception_exit_1;
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token,
        type_description_1,
        par_self,
        par_token,
        par_scopes,
        par_request
    );


    // Release cached frame if used for exception.
    if (frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token == cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token);
        cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token = NULL;
    }

    assertFrameObject(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token);

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
    CHECK_OBJECT(par_token);
    Py_DECREF(par_token);
    CHECK_OBJECT(par_scopes);
    Py_DECREF(par_scopes);
    CHECK_OBJECT(par_request);
    Py_DECREF(par_request);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

}


static PyObject *impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_request = python_pars[1];
    struct Nuitka_FrameObject *frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization)) {
        Py_XDECREF(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization = MAKE_FUNCTION_FRAME(tstate, code_objects_30b6ae8af35e345b28621a996a5d548d, module_oauthlib$openid$connect$core$request_validator, sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization->m_type_description == NULL);
    frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization = cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization);
    assert(Py_REFCNT(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization) == 2);

    // Framed code:
    {
        PyObject *tmp_raise_type_1;
        PyObject *tmp_make_exception_arg_1;
        tmp_make_exception_arg_1 = mod_consts[0];
        frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization->m_frame.f_lineno = 225;
        tmp_raise_type_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_NotImplementedError, tmp_make_exception_arg_1);
        assert(!(tmp_raise_type_1 == NULL));
        exception_state.exception_type = tmp_raise_type_1;
        exception_lineno = 225;
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
            exception_tb = MAKE_TRACEBACK(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization,
        type_description_1,
        par_self,
        par_request
    );


    // Release cached frame if used for exception.
    if (frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization == cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization);
        cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization = NULL;
    }

    assertFrameObject(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization);

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
    CHECK_OBJECT(par_request);
    Py_DECREF(par_request);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

}


static PyObject *impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_request = python_pars[1];
    struct Nuitka_FrameObject *frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login)) {
        Py_XDECREF(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login = MAKE_FUNCTION_FRAME(tstate, code_objects_c621f50285b0d6eeb9275a6bc2d28cbb, module_oauthlib$openid$connect$core$request_validator, sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login->m_type_description == NULL);
    frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login = cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login);
    assert(Py_REFCNT(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login) == 2);

    // Framed code:
    {
        PyObject *tmp_raise_type_1;
        PyObject *tmp_make_exception_arg_1;
        tmp_make_exception_arg_1 = mod_consts[0];
        frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login->m_frame.f_lineno = 246;
        tmp_raise_type_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_NotImplementedError, tmp_make_exception_arg_1);
        assert(!(tmp_raise_type_1 == NULL));
        exception_state.exception_type = tmp_raise_type_1;
        exception_lineno = 246;
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
            exception_tb = MAKE_TRACEBACK(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login,
        type_description_1,
        par_self,
        par_request
    );


    // Release cached frame if used for exception.
    if (frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login == cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login);
        cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login = NULL;
    }

    assertFrameObject(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login);

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
    CHECK_OBJECT(par_request);
    Py_DECREF(par_request);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

}


static PyObject *impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_id_token_hint = python_pars[1];
    PyObject *par_scopes = python_pars[2];
    PyObject *par_claims = python_pars[3];
    PyObject *par_request = python_pars[4];
    struct Nuitka_FrameObject *frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match)) {
        Py_XDECREF(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match = MAKE_FUNCTION_FRAME(tstate, code_objects_fe4fcc65943cd104abcad1d5fb552d87, module_oauthlib$openid$connect$core$request_validator, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match->m_type_description == NULL);
    frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match = cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match);
    assert(Py_REFCNT(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match) == 2);

    // Framed code:
    {
        PyObject *tmp_raise_type_1;
        PyObject *tmp_make_exception_arg_1;
        tmp_make_exception_arg_1 = mod_consts[0];
        frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match->m_frame.f_lineno = 266;
        tmp_raise_type_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_NotImplementedError, tmp_make_exception_arg_1);
        assert(!(tmp_raise_type_1 == NULL));
        exception_state.exception_type = tmp_raise_type_1;
        exception_lineno = 266;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);
        type_description_1 = "ooooo";
        goto frame_exception_exit_1;
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match,
        type_description_1,
        par_self,
        par_id_token_hint,
        par_scopes,
        par_claims,
        par_request
    );


    // Release cached frame if used for exception.
    if (frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match == cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match);
        cache_frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match = NULL;
    }

    assertFrameObject(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match);

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
    CHECK_OBJECT(par_id_token_hint);
    Py_DECREF(par_id_token_hint);
    CHECK_OBJECT(par_scopes);
    Py_DECREF(par_scopes);
    CHECK_OBJECT(par_claims);
    Py_DECREF(par_claims);
    CHECK_OBJECT(par_request);
    Py_DECREF(par_request);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

}



static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match,
        mod_consts[51],
#if PYTHON_VERSION >= 0x300
        mod_consts[52],
#endif
        code_objects_fe4fcc65943cd104abcad1d5fb552d87,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_oauthlib$openid$connect$core$request_validator,
        mod_consts[9],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__11_get_userinfo_claims(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        NULL,
        mod_consts[54],
#if PYTHON_VERSION >= 0x300
        mod_consts[55],
#endif
        code_objects_f1246e39074db2b0b2ba838fb6626612,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_oauthlib$openid$connect$core$request_validator,
        mod_consts[53],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__12_refresh_id_token(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        NULL,
        mod_consts[57],
#if PYTHON_VERSION >= 0x300
        mod_consts[58],
#endif
        code_objects_c4fb5e295089e719c08c31d0cc7a5747,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_oauthlib$openid$connect$core$request_validator,
        mod_consts[56],
        NULL,
        0
    );
    Nuitka_Function_EnableConstReturnTrue(result);

    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes,
        mod_consts[32],
#if PYTHON_VERSION >= 0x300
        mod_consts[33],
#endif
        code_objects_7ff29d7c5f8372a788bd3e8e573516a1,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_oauthlib$openid$connect$core$request_validator,
        mod_consts[1],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce,
        mod_consts[34],
#if PYTHON_VERSION >= 0x300
        mod_consts[35],
#endif
        code_objects_2b5b4775c1b881dbd1f4cbfb9aed13a0,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_oauthlib$openid$connect$core$request_validator,
        mod_consts[2],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token,
        mod_consts[36],
#if PYTHON_VERSION >= 0x300
        mod_consts[37],
#endif
        code_objects_53c55c1ad69a8660add90f7f1ac4703f,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_oauthlib$openid$connect$core$request_validator,
        mod_consts[3],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__4_get_id_token(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        NULL,
        mod_consts[39],
#if PYTHON_VERSION >= 0x300
        mod_consts[40],
#endif
        code_objects_acd65de89031090bfa3b29e4c122bf20,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_oauthlib$openid$connect$core$request_validator,
        mod_consts[38],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token,
        mod_consts[41],
#if PYTHON_VERSION >= 0x300
        mod_consts[42],
#endif
        code_objects_a559dbb41441742ebbfb3257bb12136f,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_oauthlib$openid$connect$core$request_validator,
        mod_consts[4],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token,
        mod_consts[43],
#if PYTHON_VERSION >= 0x300
        mod_consts[44],
#endif
        code_objects_74bdfa392711ebc8bf05f5fcfcf62be5,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_oauthlib$openid$connect$core$request_validator,
        mod_consts[5],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token,
        mod_consts[45],
#if PYTHON_VERSION >= 0x300
        mod_consts[46],
#endif
        code_objects_06a467eff7c3f17b779d106621eb7fe9,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_oauthlib$openid$connect$core$request_validator,
        mod_consts[6],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization,
        mod_consts[47],
#if PYTHON_VERSION >= 0x300
        mod_consts[48],
#endif
        code_objects_30b6ae8af35e345b28621a996a5d548d,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_oauthlib$openid$connect$core$request_validator,
        mod_consts[7],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login,
        mod_consts[49],
#if PYTHON_VERSION >= 0x300
        mod_consts[50],
#endif
        code_objects_c621f50285b0d6eeb9275a6bc2d28cbb,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_oauthlib$openid$connect$core$request_validator,
        mod_consts[8],
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

static function_impl_code const function_table_oauthlib$openid$connect$core$request_validator[] = {
    impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes,
    impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce,
    impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token,
    impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token,
    impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token,
    impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token,
    impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization,
    impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login,
    impl_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match,
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

    return Nuitka_Function_GetFunctionState(function, function_table_oauthlib$openid$connect$core$request_validator);
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
        module_oauthlib$openid$connect$core$request_validator,
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
        function_table_oauthlib$openid$connect$core$request_validator,
        sizeof(function_table_oauthlib$openid$connect$core$request_validator) / sizeof(function_impl_code)
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
static char const *module_full_name = "oauthlib.openid.connect.core.request_validator";
#endif

// Internal entry point for module code.
PyObject *modulecode_oauthlib$openid$connect$core$request_validator(PyThreadState *tstate, PyObject *module, struct Nuitka_MetaPathBasedLoaderEntry const *loader_entry) {
    // Report entry to PGO.
    PGO_onModuleEntered("oauthlib$openid$connect$core$request_validator");

    // Store the module for future use.
    module_oauthlib$openid$connect$core$request_validator = module;

    moduledict_oauthlib$openid$connect$core$request_validator = MODULE_DICT(module_oauthlib$openid$connect$core$request_validator);

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
        PRINT_STRING("oauthlib$openid$connect$core$request_validator: Calling setupMetaPathBasedLoader().\n");
#endif
        setupMetaPathBasedLoader(tstate);
#if 0 >= 0
#ifdef _NUITKA_TRACE
        PRINT_STRING("oauthlib$openid$connect$core$request_validator: Calling updateMetaPathBasedLoaderModuleRoot().\n");
#endif
        updateMetaPathBasedLoaderModuleRoot(module_full_name);
#endif


#if PYTHON_VERSION >= 0x300
        patchInspectModule(tstate);
#endif

#endif

        /* The constants only used by this module are created now. */
        NUITKA_PRINT_TRACE("oauthlib$openid$connect$core$request_validator: Calling createModuleConstants().\n");
        createModuleConstants(tstate);

#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
        createModuleCodeObjects();
#endif
        init_done = true;
    }

#if _NUITKA_MODULE_MODE && 0
    PyObject *pre_load = IMPORT_EMBEDDED_MODULE(tstate, "oauthlib.openid.connect.core.request_validator" "-preLoad");
    if (pre_load == NULL) {
        return NULL;
    }
#endif

    // PRINT_STRING("in initoauthlib$openid$connect$core$request_validator\n");

#ifdef _NUITKA_PLUGIN_DILL_ENABLED
    {
        char const *module_name_c;
        if (loader_entry != NULL) {
            module_name_c = loader_entry->name;
        } else {
            PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)const_str_plain___name__);
            module_name_c = Nuitka_String_AsString(module_name);
        }

        registerDillPluginTables(tstate, module_name_c, &_method_def_reduce_compiled_function, &_method_def_create_compiled_function);
    }
#endif

    // Set "__compiled__" to what version information we have.
    UPDATE_STRING_DICT0(
        moduledict_oauthlib$openid$connect$core$request_validator,
        (Nuitka_StringObject *)const_str_plain___compiled__,
        Nuitka_dunder_compiled_value
    );

    // Update "__package__" value to what it ought to be.
    {
#if 0
        UPDATE_STRING_DICT0(
            moduledict_oauthlib$openid$connect$core$request_validator,
            (Nuitka_StringObject *)const_str_plain___package__,
            mod_consts[69]
        );
#elif 0
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)const_str_plain___name__);

        UPDATE_STRING_DICT0(
            moduledict_oauthlib$openid$connect$core$request_validator,
            (Nuitka_StringObject *)const_str_plain___package__,
            module_name
        );
#else

#if PYTHON_VERSION < 0x300
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)const_str_plain___name__);
        char const *module_name_cstr = PyString_AS_STRING(module_name);

        char const *last_dot = strrchr(module_name_cstr, '.');

        if (last_dot != NULL) {
            UPDATE_STRING_DICT1(
                moduledict_oauthlib$openid$connect$core$request_validator,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyString_FromStringAndSize(module_name_cstr, last_dot - module_name_cstr)
            );
        }
#else
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)const_str_plain___name__);
        Py_ssize_t dot_index = PyUnicode_Find(module_name, const_str_dot, 0, PyUnicode_GetLength(module_name), -1);

        if (dot_index != -1) {
            UPDATE_STRING_DICT1(
                moduledict_oauthlib$openid$connect$core$request_validator,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyUnicode_Substring(module_name, 0, dot_index)
            );
        }
#endif
#endif
    }

    CHECK_OBJECT(module_oauthlib$openid$connect$core$request_validator);

    // For deep importing of a module we need to have "__builtins__", so we set
    // it ourselves in the same way than CPython does. Note: This must be done
    // before the frame object is allocated, or else it may fail.

    if (GET_STRING_DICT_VALUE(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)const_str_plain___builtins__) == NULL) {
        PyObject *value = (PyObject *)builtin_module;

        // Check if main module, not a dict then but the module itself.
#if _NUITKA_MODULE_MODE || !0
        value = PyModule_GetDict(value);
#endif

        UPDATE_STRING_DICT0(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)const_str_plain___builtins__, value);
    }

    PyObject *module_loader = Nuitka_Loader_New(loader_entry);
    UPDATE_STRING_DICT0(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)const_str_plain___loader__, module_loader);

#if PYTHON_VERSION >= 0x300
// Set the "__spec__" value

#if 0
    // Main modules just get "None" as spec.
    UPDATE_STRING_DICT0(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)const_str_plain___spec__, Py_None);
#else
    // Other modules get a "ModuleSpec" from the standard mechanism.
    {
        PyObject *bootstrap_module = getImportLibBootstrapModule();
        CHECK_OBJECT(bootstrap_module);

        PyObject *_spec_from_module = PyObject_GetAttrString(bootstrap_module, "_spec_from_module");
        CHECK_OBJECT(_spec_from_module);

        PyObject *spec_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, _spec_from_module, module_oauthlib$openid$connect$core$request_validator);
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

        UPDATE_STRING_DICT1(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)const_str_plain___spec__, spec_value);
    }
#endif
#endif

    // Temp variables if any
    PyObject *outline_0_var___class__ = NULL;
    PyObject *tmp_class_creation_1__bases = NULL;
    PyObject *tmp_class_creation_1__bases_orig = NULL;
    PyObject *tmp_class_creation_1__class_decl_dict = NULL;
    PyObject *tmp_class_creation_1__metaclass = NULL;
    PyObject *tmp_class_creation_1__prepared = NULL;
    struct Nuitka_FrameObject *frame_frame_oauthlib$openid$connect$core$request_validator;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    bool tmp_result;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    int tmp_res;
    PyObject *locals_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_14 = NULL;
    PyObject *tmp_dictset_value;
    struct Nuitka_FrameObject *frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_2;
    NUITKA_MAY_BE_UNUSED char const *type_description_2 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_2;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_2;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_3;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_3;

    // Module init code if any


    // Module code.
    {
        PyObject *tmp_assign_source_1;
        tmp_assign_source_1 = mod_consts[10];
        UPDATE_STRING_DICT0(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)mod_consts[11], tmp_assign_source_1);
    }
    {
        PyObject *tmp_assign_source_2;
        tmp_assign_source_2 = module_filename_obj;
        UPDATE_STRING_DICT0(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)mod_consts[12], tmp_assign_source_2);
    }
    frame_frame_oauthlib$openid$connect$core$request_validator = MAKE_MODULE_FRAME(code_objects_862a6e86879ab6dbcea3ab916f74c4b8, module_oauthlib$openid$connect$core$request_validator);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_oauthlib$openid$connect$core$request_validator);
    assert(Py_REFCNT(frame_frame_oauthlib$openid$connect$core$request_validator) == 2);

    // Framed code:
    {
        PyObject *tmp_assattr_value_1;
        PyObject *tmp_assattr_target_1;
        tmp_assattr_value_1 = module_filename_obj;
        tmp_assattr_target_1 = module_var_accessor_oauthlib$$36$openid$$36$connect$$36$core$$36$request_validator$__spec__(tstate);
        assert(!(tmp_assattr_target_1 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_1, mod_consts[13], tmp_assattr_value_1);
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
        tmp_assattr_target_2 = module_var_accessor_oauthlib$$36$openid$$36$connect$$36$core$$36$request_validator$__spec__(tstate);
        assert(!(tmp_assattr_target_2 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_2, mod_consts[14], tmp_assattr_value_2);
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
        UPDATE_STRING_DICT0(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)mod_consts[15], tmp_assign_source_3);
    }
    {
        PyObject *tmp_assign_source_4;
        PyObject *tmp_name_value_1;
        PyObject *tmp_globals_arg_value_1;
        PyObject *tmp_locals_arg_value_1;
        PyObject *tmp_fromlist_value_1;
        PyObject *tmp_level_value_1;
        tmp_name_value_1 = mod_consts[16];
        tmp_globals_arg_value_1 = (PyObject *)moduledict_oauthlib$openid$connect$core$request_validator;
        tmp_locals_arg_value_1 = Py_None;
        tmp_fromlist_value_1 = Py_None;
        tmp_level_value_1 = const_int_0;
        frame_frame_oauthlib$openid$connect$core$request_validator->m_frame.f_lineno = 5;
        tmp_assign_source_4 = IMPORT_MODULE5(tstate, tmp_name_value_1, tmp_globals_arg_value_1, tmp_locals_arg_value_1, tmp_fromlist_value_1, tmp_level_value_1);
        if (tmp_assign_source_4 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 5;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)mod_consts[16], tmp_assign_source_4);
    }
    {
        PyObject *tmp_assign_source_5;
        PyObject *tmp_import_name_from_1;
        PyObject *tmp_name_value_2;
        PyObject *tmp_globals_arg_value_2;
        PyObject *tmp_locals_arg_value_2;
        PyObject *tmp_fromlist_value_2;
        PyObject *tmp_level_value_2;
        tmp_name_value_2 = mod_consts[17];
        tmp_globals_arg_value_2 = (PyObject *)moduledict_oauthlib$openid$connect$core$request_validator;
        tmp_locals_arg_value_2 = Py_None;
        tmp_fromlist_value_2 = mod_consts[18];
        tmp_level_value_2 = const_int_0;
        frame_frame_oauthlib$openid$connect$core$request_validator->m_frame.f_lineno = 7;
        tmp_import_name_from_1 = IMPORT_MODULE5(tstate, tmp_name_value_2, tmp_globals_arg_value_2, tmp_locals_arg_value_2, tmp_fromlist_value_2, tmp_level_value_2);
        if (tmp_import_name_from_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 7;

            goto frame_exception_exit_1;
        }
        if (PyModule_Check(tmp_import_name_from_1)) {
            tmp_assign_source_5 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_1,
                (PyObject *)moduledict_oauthlib$openid$connect$core$request_validator,
                mod_consts[19],
                const_int_0
            );
        } else {
            tmp_assign_source_5 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_1, mod_consts[19]);
        }

        Py_DECREF(tmp_import_name_from_1);
        if (tmp_assign_source_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 7;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)mod_consts[20], tmp_assign_source_5);
    }
    {
        PyObject *tmp_assign_source_6;
        PyObject *tmp_called_instance_1;
        tmp_called_instance_1 = module_var_accessor_oauthlib$$36$openid$$36$connect$$36$core$$36$request_validator$logging(tstate);
        if (unlikely(tmp_called_instance_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[16]);
        }

        if (tmp_called_instance_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 11;

            goto frame_exception_exit_1;
        }
        frame_frame_oauthlib$openid$connect$core$request_validator->m_frame.f_lineno = 11;
        tmp_assign_source_6 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_1,
            mod_consts[21],
            PyTuple_GET_ITEM(mod_consts[22], 0)
        );

        if (tmp_assign_source_6 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 11;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)mod_consts[23], tmp_assign_source_6);
    }
    // Tried code:
    {
        PyObject *tmp_assign_source_7;
        PyObject *tmp_tuple_element_1;
        tmp_tuple_element_1 = module_var_accessor_oauthlib$$36$openid$$36$connect$$36$core$$36$request_validator$OAuth2RequestValidator(tstate);
        if (unlikely(tmp_tuple_element_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[20]);
        }

        if (tmp_tuple_element_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 14;

            goto try_except_handler_1;
        }
        tmp_assign_source_7 = MAKE_TUPLE_EMPTY(tstate, 1);
        PyTuple_SET_ITEM0(tmp_assign_source_7, 0, tmp_tuple_element_1);
        assert(tmp_class_creation_1__bases_orig == NULL);
        tmp_class_creation_1__bases_orig = tmp_assign_source_7;
    }
    {
        PyObject *tmp_assign_source_8;
        PyObject *tmp_direct_call_arg1_1;
        CHECK_OBJECT(tmp_class_creation_1__bases_orig);
        tmp_direct_call_arg1_1 = tmp_class_creation_1__bases_orig;
        Py_INCREF(tmp_direct_call_arg1_1);

        {
            PyObject *dir_call_args[] = {tmp_direct_call_arg1_1};
            tmp_assign_source_8 = impl___main__$$36$$$36$$$36$helper_function__mro_entries_conversion(tstate, dir_call_args);
        }
        if (tmp_assign_source_8 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 14;

            goto try_except_handler_1;
        }
        assert(tmp_class_creation_1__bases == NULL);
        tmp_class_creation_1__bases = tmp_assign_source_8;
    }
    {
        PyObject *tmp_assign_source_9;
        tmp_assign_source_9 = MAKE_DICT_EMPTY(tstate);
        assert(tmp_class_creation_1__class_decl_dict == NULL);
        tmp_class_creation_1__class_decl_dict = tmp_assign_source_9;
    }
    {
        PyObject *tmp_assign_source_10;
        PyObject *tmp_metaclass_value_1;
        nuitka_bool tmp_condition_result_1;
        int tmp_truth_name_1;
        PyObject *tmp_type_arg_1;
        PyObject *tmp_expression_value_1;
        PyObject *tmp_subscript_value_1;
        PyObject *tmp_bases_value_1;
        CHECK_OBJECT(tmp_class_creation_1__bases);
        tmp_truth_name_1 = CHECK_IF_TRUE(tmp_class_creation_1__bases);
        if (tmp_truth_name_1 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 14;

            goto try_except_handler_1;
        }
        tmp_condition_result_1 = tmp_truth_name_1 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        if (tmp_condition_result_1 == NUITKA_BOOL_TRUE) {
            goto condexpr_true_1;
        } else {
            goto condexpr_false_1;
        }
        condexpr_true_1:;
        CHECK_OBJECT(tmp_class_creation_1__bases);
        tmp_expression_value_1 = tmp_class_creation_1__bases;
        tmp_subscript_value_1 = const_int_0;
        tmp_type_arg_1 = LOOKUP_SUBSCRIPT_CONST(tstate, tmp_expression_value_1, tmp_subscript_value_1, 0);
        if (tmp_type_arg_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 14;

            goto try_except_handler_1;
        }
        tmp_metaclass_value_1 = BUILTIN_TYPE1(tmp_type_arg_1);
        Py_DECREF(tmp_type_arg_1);
        if (tmp_metaclass_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 14;

            goto try_except_handler_1;
        }
        goto condexpr_end_1;
        condexpr_false_1:;
        tmp_metaclass_value_1 = (PyObject *)&PyType_Type;
        Py_INCREF(tmp_metaclass_value_1);
        condexpr_end_1:;
        CHECK_OBJECT(tmp_class_creation_1__bases);
        tmp_bases_value_1 = tmp_class_creation_1__bases;
        tmp_assign_source_10 = SELECT_METACLASS(tstate, tmp_metaclass_value_1, tmp_bases_value_1);
        Py_DECREF(tmp_metaclass_value_1);
        if (tmp_assign_source_10 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 14;

            goto try_except_handler_1;
        }
        assert(tmp_class_creation_1__metaclass == NULL);
        tmp_class_creation_1__metaclass = tmp_assign_source_10;
    }
    {
        bool tmp_condition_result_2;
        PyObject *tmp_expression_value_2;
        CHECK_OBJECT(tmp_class_creation_1__metaclass);
        tmp_expression_value_2 = tmp_class_creation_1__metaclass;
        tmp_res = HAS_ATTR_BOOL2(tstate, tmp_expression_value_2, mod_consts[24]);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 14;

            goto try_except_handler_1;
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
        PyObject *tmp_assign_source_11;
        PyObject *tmp_called_value_1;
        PyObject *tmp_expression_value_3;
        PyObject *tmp_args_value_1;
        PyObject *tmp_tuple_element_2;
        PyObject *tmp_kwargs_value_1;
        CHECK_OBJECT(tmp_class_creation_1__metaclass);
        tmp_expression_value_3 = tmp_class_creation_1__metaclass;
        tmp_called_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_3, mod_consts[24]);
        if (tmp_called_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 14;

            goto try_except_handler_1;
        }
        tmp_tuple_element_2 = mod_consts[19];
        tmp_args_value_1 = MAKE_TUPLE_EMPTY(tstate, 2);
        PyTuple_SET_ITEM0(tmp_args_value_1, 0, tmp_tuple_element_2);
        CHECK_OBJECT(tmp_class_creation_1__bases);
        tmp_tuple_element_2 = tmp_class_creation_1__bases;
        PyTuple_SET_ITEM0(tmp_args_value_1, 1, tmp_tuple_element_2);
        CHECK_OBJECT(tmp_class_creation_1__class_decl_dict);
        tmp_kwargs_value_1 = tmp_class_creation_1__class_decl_dict;
        frame_frame_oauthlib$openid$connect$core$request_validator->m_frame.f_lineno = 14;
        tmp_assign_source_11 = CALL_FUNCTION(tstate, tmp_called_value_1, tmp_args_value_1, tmp_kwargs_value_1);
        Py_DECREF(tmp_called_value_1);
        Py_DECREF(tmp_args_value_1);
        if (tmp_assign_source_11 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 14;

            goto try_except_handler_1;
        }
        assert(tmp_class_creation_1__prepared == NULL);
        tmp_class_creation_1__prepared = tmp_assign_source_11;
    }
    {
        bool tmp_condition_result_3;
        PyObject *tmp_operand_value_1;
        PyObject *tmp_expression_value_4;
        CHECK_OBJECT(tmp_class_creation_1__prepared);
        tmp_expression_value_4 = tmp_class_creation_1__prepared;
        tmp_res = HAS_ATTR_BOOL2(tstate, tmp_expression_value_4, mod_consts[25]);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 14;

            goto try_except_handler_1;
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
        PyObject *tmp_name_value_3;
        PyObject *tmp_default_value_1;
        tmp_mod_expr_left_1 = mod_consts[26];
        CHECK_OBJECT(tmp_class_creation_1__metaclass);
        tmp_expression_value_5 = tmp_class_creation_1__metaclass;
        tmp_name_value_3 = mod_consts[27];
        tmp_default_value_1 = mod_consts[28];
        tmp_tuple_element_3 = BUILTIN_GETATTR(tstate, tmp_expression_value_5, tmp_name_value_3, tmp_default_value_1);
        if (tmp_tuple_element_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 14;

            goto try_except_handler_1;
        }
        tmp_mod_expr_right_1 = MAKE_TUPLE_EMPTY(tstate, 2);
        {
            PyObject *tmp_expression_value_6;
            PyObject *tmp_type_arg_2;
            PyTuple_SET_ITEM(tmp_mod_expr_right_1, 0, tmp_tuple_element_3);
            CHECK_OBJECT(tmp_class_creation_1__prepared);
            tmp_type_arg_2 = tmp_class_creation_1__prepared;
            tmp_expression_value_6 = BUILTIN_TYPE1(tmp_type_arg_2);
            assert(!(tmp_expression_value_6 == NULL));
            tmp_tuple_element_3 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_6, mod_consts[27]);
            Py_DECREF(tmp_expression_value_6);
            if (tmp_tuple_element_3 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 14;

                goto tuple_build_exception_1;
            }
            PyTuple_SET_ITEM(tmp_mod_expr_right_1, 1, tmp_tuple_element_3);
        }
        goto tuple_build_noexception_1;
        // Exception handling pass through code for tuple_build:
        tuple_build_exception_1:;
        Py_DECREF(tmp_mod_expr_right_1);
        goto try_except_handler_1;
        // Finished with no exception for tuple_build:
        tuple_build_noexception_1:;
        tmp_make_exception_arg_1 = BINARY_OPERATION_MOD_OBJECT_UNICODE_TUPLE(tmp_mod_expr_left_1, tmp_mod_expr_right_1);
        Py_DECREF(tmp_mod_expr_right_1);
        if (tmp_make_exception_arg_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 14;

            goto try_except_handler_1;
        }
        frame_frame_oauthlib$openid$connect$core$request_validator->m_frame.f_lineno = 14;
        tmp_raise_type_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_TypeError, tmp_make_exception_arg_1);
        Py_DECREF(tmp_make_exception_arg_1);
        assert(!(tmp_raise_type_1 == NULL));
        exception_state.exception_type = tmp_raise_type_1;
        exception_lineno = 14;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);

        goto try_except_handler_1;
    }
    branch_no_2:;
    goto branch_end_1;
    branch_no_1:;
    {
        PyObject *tmp_assign_source_12;
        tmp_assign_source_12 = MAKE_DICT_EMPTY(tstate);
        assert(tmp_class_creation_1__prepared == NULL);
        tmp_class_creation_1__prepared = tmp_assign_source_12;
    }
    branch_end_1:;
    {
        PyObject *tmp_assign_source_13;
        {
            PyObject *tmp_set_locals_1;
            CHECK_OBJECT(tmp_class_creation_1__prepared);
            tmp_set_locals_1 = tmp_class_creation_1__prepared;
            locals_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_14 = tmp_set_locals_1;
            Py_INCREF(tmp_set_locals_1);
        }
        // Tried code:
        // Tried code:
        tmp_dictset_value = mod_consts[29];
        tmp_res = PyObject_SetItem(locals_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_14, mod_consts[30], tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 14;

            goto try_except_handler_3;
        }
        tmp_dictset_value = mod_consts[19];
        tmp_res = PyObject_SetItem(locals_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_14, mod_consts[31], tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 14;

            goto try_except_handler_3;
        }
        frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_2 = MAKE_CLASS_FRAME(tstate, code_objects_2940e4c6965bb30bb3703c5d3195d93e, module_oauthlib$openid$connect$core$request_validator, NULL, sizeof(void *));

        // Push the new frame as the currently active one, and we should be exclusively
        // owning it.
        pushFrameStackCompiledFrame(tstate, frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_2);
        assert(Py_REFCNT(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_2) == 2);

        // Framed code:


        tmp_dictset_value = MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__1_get_authorization_code_scopes(tstate);

        tmp_res = PyObject_SetItem(locals_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_14, mod_consts[32], tmp_dictset_value);
        Py_DECREF(tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 16;
            type_description_2 = "o";
            goto frame_exception_exit_2;
        }


        tmp_dictset_value = MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__2_get_authorization_code_nonce(tstate);

        tmp_res = PyObject_SetItem(locals_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_14, mod_consts[34], tmp_dictset_value);
        Py_DECREF(tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 40;
            type_description_2 = "o";
            goto frame_exception_exit_2;
        }


        tmp_dictset_value = MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__3_get_jwt_bearer_token(tstate);

        tmp_res = PyObject_SetItem(locals_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_14, mod_consts[36], tmp_dictset_value);
        Py_DECREF(tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 64;
            type_description_2 = "o";
            goto frame_exception_exit_2;
        }


        tmp_dictset_value = MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__4_get_id_token(tstate);

        tmp_res = PyObject_SetItem(locals_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_14, mod_consts[39], tmp_dictset_value);
        Py_DECREF(tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 80;
            type_description_2 = "o";
            goto frame_exception_exit_2;
        }


        tmp_dictset_value = MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__5_finalize_id_token(tstate);

        tmp_res = PyObject_SetItem(locals_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_14, mod_consts[41], tmp_dictset_value);
        Py_DECREF(tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 119;
            type_description_2 = "o";
            goto frame_exception_exit_2;
        }


        tmp_dictset_value = MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__6_validate_jwt_bearer_token(tstate);

        tmp_res = PyObject_SetItem(locals_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_14, mod_consts[43], tmp_dictset_value);
        Py_DECREF(tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 162;
            type_description_2 = "o";
            goto frame_exception_exit_2;
        }


        tmp_dictset_value = MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__7_validate_id_token(tstate);

        tmp_res = PyObject_SetItem(locals_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_14, mod_consts[45], tmp_dictset_value);
        Py_DECREF(tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 188;
            type_description_2 = "o";
            goto frame_exception_exit_2;
        }


        tmp_dictset_value = MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__8_validate_silent_authorization(tstate);

        tmp_res = PyObject_SetItem(locals_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_14, mod_consts[47], tmp_dictset_value);
        Py_DECREF(tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 210;
            type_description_2 = "o";
            goto frame_exception_exit_2;
        }


        tmp_dictset_value = MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__9_validate_silent_login(tstate);

        tmp_res = PyObject_SetItem(locals_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_14, mod_consts[49], tmp_dictset_value);
        Py_DECREF(tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 227;
            type_description_2 = "o";
            goto frame_exception_exit_2;
        }


        tmp_dictset_value = MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__10_validate_user_match(tstate);

        tmp_res = PyObject_SetItem(locals_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_14, mod_consts[51], tmp_dictset_value);
        Py_DECREF(tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 248;
            type_description_2 = "o";
            goto frame_exception_exit_2;
        }


        tmp_dictset_value = MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__11_get_userinfo_claims(tstate);

        tmp_res = PyObject_SetItem(locals_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_14, mod_consts[54], tmp_dictset_value);
        Py_DECREF(tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 268;
            type_description_2 = "o";
            goto frame_exception_exit_2;
        }


        tmp_dictset_value = MAKE_FUNCTION_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$function__12_refresh_id_token(tstate);

        tmp_res = PyObject_SetItem(locals_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_14, mod_consts[57], tmp_dictset_value);
        Py_DECREF(tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 310;
            type_description_2 = "o";
            goto frame_exception_exit_2;
        }


        // Put the previous frame back on top.
        popFrameStack(tstate);

        goto frame_no_exception_1;
        frame_exception_exit_2:


        {
            PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
            if (exception_tb == NULL) {
                exception_tb = MAKE_TRACEBACK(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_2, exception_lineno);
                SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
            } else if (exception_tb->tb_frame != &frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_2->m_frame) {
                exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_2, exception_lineno);
                SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
            }
        }

        // Attaches locals to frame if any.
        Nuitka_Frame_AttachLocals(
            frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_2,
            type_description_2,
            outline_0_var___class__
        );



        assertFrameObject(frame_frame_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_2);

        // Put the previous frame back on top.
        popFrameStack(tstate);

        // Return the error.
        goto nested_frame_exit_1;
        frame_no_exception_1:;
        goto skip_nested_handling_1;
        nested_frame_exit_1:;

        goto try_except_handler_3;
        skip_nested_handling_1:;
        {
            nuitka_bool tmp_condition_result_4;
            PyObject *tmp_cmp_expr_left_1;
            PyObject *tmp_cmp_expr_right_1;
            CHECK_OBJECT(tmp_class_creation_1__bases);
            tmp_cmp_expr_left_1 = tmp_class_creation_1__bases;
            CHECK_OBJECT(tmp_class_creation_1__bases_orig);
            tmp_cmp_expr_right_1 = tmp_class_creation_1__bases_orig;
            tmp_condition_result_4 = RICH_COMPARE_NE_NBOOL_OBJECT_TUPLE(tmp_cmp_expr_left_1, tmp_cmp_expr_right_1);
            if (tmp_condition_result_4 == NUITKA_BOOL_EXCEPTION) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 14;

                goto try_except_handler_3;
            }
            if (tmp_condition_result_4 == NUITKA_BOOL_TRUE) {
                goto branch_yes_3;
            } else {
                goto branch_no_3;
            }
        }
        branch_yes_3:;
        CHECK_OBJECT(tmp_class_creation_1__bases_orig);
        tmp_dictset_value = tmp_class_creation_1__bases_orig;
        tmp_res = PyObject_SetItem(locals_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_14, mod_consts[59], tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 14;

            goto try_except_handler_3;
        }
        branch_no_3:;
        {
            PyObject *tmp_assign_source_14;
            PyObject *tmp_called_value_2;
            PyObject *tmp_args_value_2;
            PyObject *tmp_tuple_element_4;
            PyObject *tmp_kwargs_value_2;
            CHECK_OBJECT(tmp_class_creation_1__metaclass);
            tmp_called_value_2 = tmp_class_creation_1__metaclass;
            tmp_tuple_element_4 = mod_consts[19];
            tmp_args_value_2 = MAKE_TUPLE_EMPTY(tstate, 3);
            PyTuple_SET_ITEM0(tmp_args_value_2, 0, tmp_tuple_element_4);
            CHECK_OBJECT(tmp_class_creation_1__bases);
            tmp_tuple_element_4 = tmp_class_creation_1__bases;
            PyTuple_SET_ITEM0(tmp_args_value_2, 1, tmp_tuple_element_4);
            tmp_tuple_element_4 = locals_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_14;
            PyTuple_SET_ITEM0(tmp_args_value_2, 2, tmp_tuple_element_4);
            CHECK_OBJECT(tmp_class_creation_1__class_decl_dict);
            tmp_kwargs_value_2 = tmp_class_creation_1__class_decl_dict;
            frame_frame_oauthlib$openid$connect$core$request_validator->m_frame.f_lineno = 14;
            tmp_assign_source_14 = CALL_FUNCTION(tstate, tmp_called_value_2, tmp_args_value_2, tmp_kwargs_value_2);
            Py_DECREF(tmp_args_value_2);
            if (tmp_assign_source_14 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 14;

                goto try_except_handler_3;
            }
            assert(outline_0_var___class__ == NULL);
            outline_0_var___class__ = tmp_assign_source_14;
        }
        CHECK_OBJECT(outline_0_var___class__);
        tmp_assign_source_13 = outline_0_var___class__;
        Py_INCREF(tmp_assign_source_13);
        goto try_return_handler_3;
        NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
        return NULL;
        // Return handler code:
        try_return_handler_3:;
        Py_DECREF(locals_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_14);
        locals_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_14 = NULL;
        goto try_return_handler_2;
        // Exception handler code:
        try_except_handler_3:;
        exception_keeper_lineno_1 = exception_lineno;
        exception_lineno = 0;
        exception_keeper_name_1 = exception_state;
        INIT_ERROR_OCCURRED_STATE(&exception_state);

        Py_DECREF(locals_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_14);
        locals_oauthlib$openid$connect$core$request_validator$$36$$$36$$$36$class__1_RequestValidator_14 = NULL;
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
        exception_lineno = 14;
        goto try_except_handler_1;
        outline_result_1:;
        UPDATE_STRING_DICT1(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)mod_consts[19], tmp_assign_source_13);
    }
    goto try_end_1;
    // Exception handler code:
    try_except_handler_1:;
    exception_keeper_lineno_3 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_3 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    Py_XDECREF(tmp_class_creation_1__bases_orig);
    tmp_class_creation_1__bases_orig = NULL;
    Py_XDECREF(tmp_class_creation_1__bases);
    tmp_class_creation_1__bases = NULL;
    Py_XDECREF(tmp_class_creation_1__class_decl_dict);
    tmp_class_creation_1__class_decl_dict = NULL;
    Py_XDECREF(tmp_class_creation_1__metaclass);
    tmp_class_creation_1__metaclass = NULL;
    Py_XDECREF(tmp_class_creation_1__prepared);
    tmp_class_creation_1__prepared = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_3;
    exception_lineno = exception_keeper_lineno_3;

    goto frame_exception_exit_1;
    // End of try:
    try_end_1:;


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_2;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_oauthlib$openid$connect$core$request_validator, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_oauthlib$openid$connect$core$request_validator->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_oauthlib$openid$connect$core$request_validator, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }



    assertFrameObject(frame_frame_oauthlib$openid$connect$core$request_validator);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto module_exception_exit;
    frame_no_exception_2:;
    CHECK_OBJECT(tmp_class_creation_1__bases_orig);
    Py_DECREF(tmp_class_creation_1__bases_orig);
    tmp_class_creation_1__bases_orig = NULL;
    CHECK_OBJECT(tmp_class_creation_1__bases);
    Py_DECREF(tmp_class_creation_1__bases);
    tmp_class_creation_1__bases = NULL;
    CHECK_OBJECT(tmp_class_creation_1__class_decl_dict);
    Py_DECREF(tmp_class_creation_1__class_decl_dict);
    tmp_class_creation_1__class_decl_dict = NULL;
    CHECK_OBJECT(tmp_class_creation_1__metaclass);
    Py_DECREF(tmp_class_creation_1__metaclass);
    tmp_class_creation_1__metaclass = NULL;
    CHECK_OBJECT(tmp_class_creation_1__prepared);
    Py_DECREF(tmp_class_creation_1__prepared);
    tmp_class_creation_1__prepared = NULL;

    // Report to PGO about leaving the module without error.
    PGO_onModuleExit("oauthlib$openid$connect$core$request_validator", false);

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *post_load = IMPORT_EMBEDDED_MODULE(tstate, "oauthlib.openid.connect.core.request_validator" "-postLoad");
        if (post_load == NULL) {
            return NULL;
        }
    }
#endif

    Py_INCREF(module_oauthlib$openid$connect$core$request_validator);
    return module_oauthlib$openid$connect$core$request_validator;
    module_exception_exit:

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_oauthlib$openid$connect$core$request_validator, (Nuitka_StringObject *)const_str_plain___name__);

        if (module_name != NULL) {
            Nuitka_DelModule(tstate, module_name);
        }
    }
#endif
    PGO_onModuleExit("oauthlib$openid$connect$core$request_validator", false);

    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);
    return NULL;
}
