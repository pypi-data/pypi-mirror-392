/* Generated code for Python module 'mcp_atlassian$utils$environment'
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

/* The "module_mcp_atlassian$utils$environment" is a Python object pointer of module type.
 *
 * Note: For full compatibility with CPython, every module variable access
 * needs to go through it except for cases where the module cannot possibly
 * have changed in the mean time.
 */

PyObject *module_mcp_atlassian$utils$environment;
PyDictObject *moduledict_mcp_atlassian$utils$environment;

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
        loadConstantsBlob(tstate, &mod_consts[0], UN_TRANSLATE("mcp_atlassian.utils.environment"));
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
void checkModuleConstants_mcp_atlassian$utils$environment(PyThreadState *tstate) {
    // The module may not have been used at all, then ignore this.
    if (constants_created == false) return;

    for (int i = 0; i < 59; i++) {
        assert(mod_consts_hash[i] == DEEP_HASH(tstate, mod_consts[i]));
        CHECK_OBJECT_DEEP(mod_consts[i]);
    }
}
#endif

// Helper to preserving module variables for Python3.11+
#if 4
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
static PyObject *module_var_accessor_mcp_atlassian$$36$utils$$36$environment$__spec__(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_mcp_atlassian$utils$environment->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_mcp_atlassian$utils$environment->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)mod_consts[58]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_mcp_atlassian$utils$environment->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)mod_consts[58]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)mod_consts[58]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[58]);
    }

    return result;
}

static PyObject *module_var_accessor_mcp_atlassian$$36$utils$$36$environment$is_atlassian_cloud_url(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_mcp_atlassian$utils$environment->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_mcp_atlassian$utils$environment->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)mod_consts[8]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_mcp_atlassian$utils$environment->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[8]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[8], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[8]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[8], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)mod_consts[8]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)mod_consts[8]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[8]);
    }

    return result;
}

static PyObject *module_var_accessor_mcp_atlassian$$36$utils$$36$environment$logger(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_mcp_atlassian$utils$environment->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_mcp_atlassian$utils$environment->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)mod_consts[5]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_mcp_atlassian$utils$environment->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)mod_consts[5]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)mod_consts[5]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[5]);
    }

    return result;
}

static PyObject *module_var_accessor_mcp_atlassian$$36$utils$$36$environment$logging(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_mcp_atlassian$utils$environment->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_mcp_atlassian$utils$environment->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)mod_consts[46]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_mcp_atlassian$utils$environment->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[46]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[46], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[46]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[46], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)mod_consts[46]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)mod_consts[46]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[46]);
    }

    return result;
}


#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
// The module code objects.
static PyCodeObject *code_objects_0e427739627123b53bc4e1a4ec018506;
static PyCodeObject *code_objects_6380f0aa092288274df7ae9483b2d393;

static void createModuleCodeObjects(void) {
    module_filename_obj = MAKE_RELATIVE_PATH(mod_consts[54]); CHECK_OBJECT(module_filename_obj);
    code_objects_0e427739627123b53bc4e1a4ec018506 = MAKE_CODE_OBJECT(module_filename_obj, 1, CO_NOFREE, mod_consts[55], mod_consts[55], NULL, NULL, 0, 0, 0);
    code_objects_6380f0aa092288274df7ae9483b2d393 = MAKE_CODE_OBJECT(module_filename_obj, 11, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[53], mod_consts[53], mod_consts[56], NULL, 0, 0, 0);
}
#endif

// The module function declarations.
static PyObject *MAKE_FUNCTION_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services(PyThreadState *tstate, PyObject *annotations);


// The module function definitions.
static PyObject *impl_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *var_confluence_url = NULL;
    nuitka_bool var_confluence_is_setup = NUITKA_BOOL_UNASSIGNED;
    PyObject *var_intsig_url = NULL;
    PyObject *var_intsig_username = NULL;
    PyObject *var_intsig_password = NULL;
    PyObject *var_is_cloud = NULL;
    PyObject *var_jira_url = NULL;
    nuitka_bool var_jira_is_setup = NUITKA_BOOL_UNASSIGNED;
    struct Nuitka_FrameObject *frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    NUITKA_MAY_BE_UNUSED nuitka_void tmp_unused;
    int tmp_res;
    static struct Nuitka_FrameObject *cache_frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;

    // Actual function body.
    // Tried code:
    if (isFrameUnusable(cache_frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services)) {
        Py_XDECREF(cache_frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services = MAKE_FUNCTION_FRAME(tstate, code_objects_6380f0aa092288274df7ae9483b2d393, module_mcp_atlassian$utils$environment, sizeof(nuitka_bool)+sizeof(nuitka_bool)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_type_description == NULL);
    frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services = cache_frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services);
    assert(Py_REFCNT(frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services) == 2);

    // Framed code:
    {
        PyObject *tmp_assign_source_1;
        int tmp_or_left_truth_1;
        PyObject *tmp_or_left_value_1;
        PyObject *tmp_or_right_value_1;
        PyObject *tmp_called_instance_1;
        PyObject *tmp_called_instance_2;
        tmp_called_instance_1 = IMPORT_HARD_OS();
        assert(!(tmp_called_instance_1 == NULL));
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 14;
        tmp_or_left_value_1 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_1,
            mod_consts[0],
            PyTuple_GET_ITEM(mod_consts[1], 0)
        );

        if (tmp_or_left_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 14;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_or_left_truth_1 = CHECK_IF_TRUE(tmp_or_left_value_1);
        if (tmp_or_left_truth_1 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_or_left_value_1);

            exception_lineno = 14;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        if (tmp_or_left_truth_1 == 1) {
            goto or_left_1;
        } else {
            goto or_right_1;
        }
        or_right_1:;
        Py_DECREF(tmp_or_left_value_1);
        tmp_called_instance_2 = IMPORT_HARD_OS();
        assert(!(tmp_called_instance_2 == NULL));
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 14;
        tmp_or_right_value_1 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_2,
            mod_consts[0],
            PyTuple_GET_ITEM(mod_consts[2], 0)
        );

        if (tmp_or_right_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 14;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_assign_source_1 = tmp_or_right_value_1;
        goto or_end_1;
        or_left_1:;
        tmp_assign_source_1 = tmp_or_left_value_1;
        or_end_1:;
        assert(var_confluence_url == NULL);
        var_confluence_url = tmp_assign_source_1;
    }
    {
        nuitka_bool tmp_assign_source_2;
        tmp_assign_source_2 = NUITKA_BOOL_FALSE;
        var_confluence_is_setup = tmp_assign_source_2;
    }
    {
        PyObject *tmp_assign_source_3;
        PyObject *tmp_called_instance_3;
        tmp_called_instance_3 = IMPORT_HARD_OS();
        assert(!(tmp_called_instance_3 == NULL));
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 18;
        tmp_assign_source_3 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_3,
            mod_consts[0],
            PyTuple_GET_ITEM(mod_consts[2], 0)
        );

        if (tmp_assign_source_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 18;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        assert(var_intsig_url == NULL);
        var_intsig_url = tmp_assign_source_3;
    }
    {
        PyObject *tmp_assign_source_4;
        PyObject *tmp_called_instance_4;
        tmp_called_instance_4 = IMPORT_HARD_OS();
        assert(!(tmp_called_instance_4 == NULL));
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 19;
        tmp_assign_source_4 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_4,
            mod_consts[0],
            PyTuple_GET_ITEM(mod_consts[3], 0)
        );

        if (tmp_assign_source_4 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 19;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        assert(var_intsig_username == NULL);
        var_intsig_username = tmp_assign_source_4;
    }
    {
        PyObject *tmp_assign_source_5;
        PyObject *tmp_called_instance_5;
        tmp_called_instance_5 = IMPORT_HARD_OS();
        assert(!(tmp_called_instance_5 == NULL));
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 20;
        tmp_assign_source_5 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_5,
            mod_consts[0],
            PyTuple_GET_ITEM(mod_consts[4], 0)
        );

        if (tmp_assign_source_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 20;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        assert(var_intsig_password == NULL);
        var_intsig_password = tmp_assign_source_5;
    }
    {
        nuitka_bool tmp_condition_result_1;
        int tmp_and_left_truth_1;
        nuitka_bool tmp_and_left_value_1;
        nuitka_bool tmp_and_right_value_1;
        int tmp_truth_name_1;
        int tmp_and_left_truth_2;
        nuitka_bool tmp_and_left_value_2;
        nuitka_bool tmp_and_right_value_2;
        int tmp_truth_name_2;
        int tmp_truth_name_3;
        CHECK_OBJECT(var_intsig_url);
        tmp_truth_name_1 = CHECK_IF_TRUE(var_intsig_url);
        if (tmp_truth_name_1 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 21;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_and_left_value_1 = tmp_truth_name_1 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        tmp_and_left_truth_1 = tmp_and_left_value_1 == NUITKA_BOOL_TRUE ? 1 : 0;
        if (tmp_and_left_truth_1 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 21;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        if (tmp_and_left_truth_1 == 1) {
            goto and_right_1;
        } else {
            goto and_left_1;
        }
        and_right_1:;
        CHECK_OBJECT(var_intsig_username);
        tmp_truth_name_2 = CHECK_IF_TRUE(var_intsig_username);
        if (tmp_truth_name_2 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 21;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_and_left_value_2 = tmp_truth_name_2 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        tmp_and_left_truth_2 = tmp_and_left_value_2 == NUITKA_BOOL_TRUE ? 1 : 0;
        if (tmp_and_left_truth_2 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 21;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        if (tmp_and_left_truth_2 == 1) {
            goto and_right_2;
        } else {
            goto and_left_2;
        }
        and_right_2:;
        CHECK_OBJECT(var_intsig_password);
        tmp_truth_name_3 = CHECK_IF_TRUE(var_intsig_password);
        if (tmp_truth_name_3 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 21;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_and_right_value_2 = tmp_truth_name_3 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        tmp_and_right_value_1 = tmp_and_right_value_2;
        goto and_end_2;
        and_left_2:;
        tmp_and_right_value_1 = tmp_and_left_value_2;
        and_end_2:;
        tmp_condition_result_1 = tmp_and_right_value_1;
        goto and_end_1;
        and_left_1:;
        tmp_condition_result_1 = tmp_and_left_value_1;
        and_end_1:;
        if (tmp_condition_result_1 == NUITKA_BOOL_TRUE) {
            goto branch_yes_1;
        } else {
            goto branch_no_1;
        }
    }
    branch_yes_1:;
    {
        nuitka_bool tmp_assign_source_6;
        tmp_assign_source_6 = NUITKA_BOOL_TRUE;
        var_confluence_is_setup = tmp_assign_source_6;
    }
    {
        PyObject *tmp_called_instance_6;
        PyObject *tmp_call_result_1;
        tmp_called_instance_6 = module_var_accessor_mcp_atlassian$$36$utils$$36$environment$logger(tstate);
        if (unlikely(tmp_called_instance_6 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_called_instance_6 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 23;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 23;
        tmp_call_result_1 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_6,
            mod_consts[6],
            PyTuple_GET_ITEM(mod_consts[7], 0)
        );

        if (tmp_call_result_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 23;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_1);
    }
    goto branch_end_1;
    branch_no_1:;
    {
        nuitka_bool tmp_condition_result_2;
        int tmp_truth_name_4;
        CHECK_OBJECT(var_confluence_url);
        tmp_truth_name_4 = CHECK_IF_TRUE(var_confluence_url);
        if (tmp_truth_name_4 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 24;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_2 = tmp_truth_name_4 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        if (tmp_condition_result_2 == NUITKA_BOOL_TRUE) {
            goto branch_yes_2;
        } else {
            goto branch_no_2;
        }
    }
    branch_yes_2:;
    {
        PyObject *tmp_assign_source_7;
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        tmp_called_value_1 = module_var_accessor_mcp_atlassian$$36$utils$$36$environment$is_atlassian_cloud_url(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[8]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 25;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(var_confluence_url);
        tmp_args_element_value_1 = var_confluence_url;
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 25;
        tmp_assign_source_7 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_1, tmp_args_element_value_1);
        if (tmp_assign_source_7 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 25;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        assert(var_is_cloud == NULL);
        var_is_cloud = tmp_assign_source_7;
    }
    {
        bool tmp_condition_result_3;
        PyObject *tmp_all_arg_1;
        PyObject *tmp_list_element_1;
        PyObject *tmp_called_instance_7;
        PyObject *tmp_capi_result_1;
        tmp_called_instance_7 = IMPORT_HARD_OS();
        assert(!(tmp_called_instance_7 == NULL));
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 30;
        tmp_list_element_1 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_7,
            mod_consts[0],
            PyTuple_GET_ITEM(mod_consts[9], 0)
        );

        if (tmp_list_element_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 30;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_all_arg_1 = MAKE_LIST_EMPTY(tstate, 5);
        {
            PyObject *tmp_called_instance_8;
            PyObject *tmp_called_instance_9;
            PyObject *tmp_called_instance_10;
            PyObject *tmp_called_instance_11;
            PyList_SET_ITEM(tmp_all_arg_1, 0, tmp_list_element_1);
            tmp_called_instance_8 = IMPORT_HARD_OS();
            assert(!(tmp_called_instance_8 == NULL));
            frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 31;
            tmp_list_element_1 = CALL_METHOD_WITH_SINGLE_ARG(
                tstate,
                tmp_called_instance_8,
                mod_consts[0],
                PyTuple_GET_ITEM(mod_consts[10], 0)
            );

            if (tmp_list_element_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 31;
                type_description_1 = "obooooob";
                goto list_build_exception_1;
            }
            PyList_SET_ITEM(tmp_all_arg_1, 1, tmp_list_element_1);
            tmp_called_instance_9 = IMPORT_HARD_OS();
            assert(!(tmp_called_instance_9 == NULL));
            frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 32;
            tmp_list_element_1 = CALL_METHOD_WITH_SINGLE_ARG(
                tstate,
                tmp_called_instance_9,
                mod_consts[0],
                PyTuple_GET_ITEM(mod_consts[11], 0)
            );

            if (tmp_list_element_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 32;
                type_description_1 = "obooooob";
                goto list_build_exception_1;
            }
            PyList_SET_ITEM(tmp_all_arg_1, 2, tmp_list_element_1);
            tmp_called_instance_10 = IMPORT_HARD_OS();
            assert(!(tmp_called_instance_10 == NULL));
            frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 33;
            tmp_list_element_1 = CALL_METHOD_WITH_SINGLE_ARG(
                tstate,
                tmp_called_instance_10,
                mod_consts[0],
                PyTuple_GET_ITEM(mod_consts[12], 0)
            );

            if (tmp_list_element_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 33;
                type_description_1 = "obooooob";
                goto list_build_exception_1;
            }
            PyList_SET_ITEM(tmp_all_arg_1, 3, tmp_list_element_1);
            tmp_called_instance_11 = IMPORT_HARD_OS();
            assert(!(tmp_called_instance_11 == NULL));
            frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 34;
            tmp_list_element_1 = CALL_METHOD_WITH_SINGLE_ARG(
                tstate,
                tmp_called_instance_11,
                mod_consts[0],
                PyTuple_GET_ITEM(mod_consts[13], 0)
            );

            if (tmp_list_element_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 34;
                type_description_1 = "obooooob";
                goto list_build_exception_1;
            }
            PyList_SET_ITEM(tmp_all_arg_1, 4, tmp_list_element_1);
        }
        goto list_build_noexception_1;
        // Exception handling pass through code for list_build:
        list_build_exception_1:;
        Py_DECREF(tmp_all_arg_1);
        goto frame_exception_exit_1;
        // Finished with no exception for list_build:
        list_build_noexception_1:;
        tmp_capi_result_1 = BUILTIN_ALL(tstate, tmp_all_arg_1);
        Py_DECREF(tmp_all_arg_1);
        if (tmp_capi_result_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 28;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_3 = CHECK_IF_TRUE(tmp_capi_result_1) == 1;
        Py_DECREF(tmp_capi_result_1);
        if (tmp_condition_result_3 != false) {
            goto branch_yes_3;
        } else {
            goto branch_no_3;
        }
    }
    branch_yes_3:;
    {
        nuitka_bool tmp_assign_source_8;
        tmp_assign_source_8 = NUITKA_BOOL_TRUE;
        var_confluence_is_setup = tmp_assign_source_8;
    }
    {
        PyObject *tmp_called_instance_12;
        PyObject *tmp_call_result_2;
        tmp_called_instance_12 = module_var_accessor_mcp_atlassian$$36$utils$$36$environment$logger(tstate);
        if (unlikely(tmp_called_instance_12 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_called_instance_12 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 40;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 40;
        tmp_call_result_2 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_12,
            mod_consts[6],
            PyTuple_GET_ITEM(mod_consts[14], 0)
        );

        if (tmp_call_result_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 40;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_2);
    }
    goto branch_end_3;
    branch_no_3:;
    {
        bool tmp_condition_result_4;
        PyObject *tmp_all_arg_2;
        PyObject *tmp_list_element_2;
        PyObject *tmp_called_instance_13;
        PyObject *tmp_capi_result_2;
        tmp_called_instance_13 = IMPORT_HARD_OS();
        assert(!(tmp_called_instance_13 == NULL));
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 45;
        tmp_list_element_2 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_13,
            mod_consts[0],
            PyTuple_GET_ITEM(mod_consts[15], 0)
        );

        if (tmp_list_element_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 45;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_all_arg_2 = MAKE_LIST_EMPTY(tstate, 2);
        {
            PyObject *tmp_called_instance_14;
            PyList_SET_ITEM(tmp_all_arg_2, 0, tmp_list_element_2);
            tmp_called_instance_14 = IMPORT_HARD_OS();
            assert(!(tmp_called_instance_14 == NULL));
            frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 46;
            tmp_list_element_2 = CALL_METHOD_WITH_SINGLE_ARG(
                tstate,
                tmp_called_instance_14,
                mod_consts[0],
                PyTuple_GET_ITEM(mod_consts[13], 0)
            );

            if (tmp_list_element_2 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 46;
                type_description_1 = "obooooob";
                goto list_build_exception_2;
            }
            PyList_SET_ITEM(tmp_all_arg_2, 1, tmp_list_element_2);
        }
        goto list_build_noexception_2;
        // Exception handling pass through code for list_build:
        list_build_exception_2:;
        Py_DECREF(tmp_all_arg_2);
        goto frame_exception_exit_1;
        // Finished with no exception for list_build:
        list_build_noexception_2:;
        tmp_capi_result_2 = BUILTIN_ALL(tstate, tmp_all_arg_2);
        Py_DECREF(tmp_all_arg_2);
        if (tmp_capi_result_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 43;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_4 = CHECK_IF_TRUE(tmp_capi_result_2) == 1;
        Py_DECREF(tmp_capi_result_2);
        if (tmp_condition_result_4 != false) {
            goto branch_yes_4;
        } else {
            goto branch_no_4;
        }
    }
    branch_yes_4:;
    {
        nuitka_bool tmp_assign_source_9;
        tmp_assign_source_9 = NUITKA_BOOL_TRUE;
        var_confluence_is_setup = tmp_assign_source_9;
    }
    {
        PyObject *tmp_called_instance_15;
        PyObject *tmp_call_result_3;
        tmp_called_instance_15 = module_var_accessor_mcp_atlassian$$36$utils$$36$environment$logger(tstate);
        if (unlikely(tmp_called_instance_15 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_called_instance_15 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 50;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 50;
        tmp_call_result_3 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_15,
            mod_consts[6],
            PyTuple_GET_ITEM(mod_consts[16], 0)
        );

        if (tmp_call_result_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 50;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_3);
    }
    goto branch_end_4;
    branch_no_4:;
    {
        nuitka_bool tmp_condition_result_5;
        int tmp_truth_name_5;
        CHECK_OBJECT(var_is_cloud);
        tmp_truth_name_5 = CHECK_IF_TRUE(var_is_cloud);
        if (tmp_truth_name_5 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 54;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_5 = tmp_truth_name_5 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        if (tmp_condition_result_5 == NUITKA_BOOL_TRUE) {
            goto branch_yes_5;
        } else {
            goto branch_no_5;
        }
    }
    branch_yes_5:;
    {
        bool tmp_condition_result_6;
        PyObject *tmp_all_arg_3;
        PyObject *tmp_list_element_3;
        PyObject *tmp_called_instance_16;
        PyObject *tmp_capi_result_3;
        tmp_called_instance_16 = IMPORT_HARD_OS();
        assert(!(tmp_called_instance_16 == NULL));
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 57;
        tmp_list_element_3 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_16,
            mod_consts[0],
            PyTuple_GET_ITEM(mod_consts[17], 0)
        );

        if (tmp_list_element_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 57;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_all_arg_3 = MAKE_LIST_EMPTY(tstate, 2);
        {
            PyObject *tmp_called_instance_17;
            PyList_SET_ITEM(tmp_all_arg_3, 0, tmp_list_element_3);
            tmp_called_instance_17 = IMPORT_HARD_OS();
            assert(!(tmp_called_instance_17 == NULL));
            frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 58;
            tmp_list_element_3 = CALL_METHOD_WITH_SINGLE_ARG(
                tstate,
                tmp_called_instance_17,
                mod_consts[0],
                PyTuple_GET_ITEM(mod_consts[18], 0)
            );

            if (tmp_list_element_3 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 58;
                type_description_1 = "obooooob";
                goto list_build_exception_3;
            }
            PyList_SET_ITEM(tmp_all_arg_3, 1, tmp_list_element_3);
        }
        goto list_build_noexception_3;
        // Exception handling pass through code for list_build:
        list_build_exception_3:;
        Py_DECREF(tmp_all_arg_3);
        goto frame_exception_exit_1;
        // Finished with no exception for list_build:
        list_build_noexception_3:;
        tmp_capi_result_3 = BUILTIN_ALL(tstate, tmp_all_arg_3);
        Py_DECREF(tmp_all_arg_3);
        if (tmp_capi_result_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 55;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_6 = CHECK_IF_TRUE(tmp_capi_result_3) == 1;
        Py_DECREF(tmp_capi_result_3);
        if (tmp_condition_result_6 != false) {
            goto branch_yes_6;
        } else {
            goto branch_no_6;
        }
    }
    branch_yes_6:;
    {
        nuitka_bool tmp_assign_source_10;
        tmp_assign_source_10 = NUITKA_BOOL_TRUE;
        var_confluence_is_setup = tmp_assign_source_10;
    }
    {
        PyObject *tmp_called_instance_18;
        PyObject *tmp_call_result_4;
        tmp_called_instance_18 = module_var_accessor_mcp_atlassian$$36$utils$$36$environment$logger(tstate);
        if (unlikely(tmp_called_instance_18 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_called_instance_18 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 62;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 62;
        tmp_call_result_4 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_18,
            mod_consts[6],
            PyTuple_GET_ITEM(mod_consts[19], 0)
        );

        if (tmp_call_result_4 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 62;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_4);
    }
    branch_no_6:;
    goto branch_end_5;
    branch_no_5:;
    {
        nuitka_bool tmp_condition_result_7;
        int tmp_or_left_truth_2;
        nuitka_bool tmp_or_left_value_2;
        nuitka_bool tmp_or_right_value_2;
        PyObject *tmp_called_instance_19;
        PyObject *tmp_call_result_5;
        int tmp_truth_name_6;
        int tmp_and_left_truth_3;
        nuitka_bool tmp_and_left_value_3;
        nuitka_bool tmp_and_right_value_3;
        PyObject *tmp_called_instance_20;
        PyObject *tmp_call_result_6;
        int tmp_truth_name_7;
        PyObject *tmp_called_instance_21;
        PyObject *tmp_call_result_7;
        int tmp_truth_name_8;
        tmp_called_instance_19 = IMPORT_HARD_OS();
        assert(!(tmp_called_instance_19 == NULL));
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 64;
        tmp_call_result_5 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_19,
            mod_consts[0],
            PyTuple_GET_ITEM(mod_consts[20], 0)
        );

        if (tmp_call_result_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 64;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_truth_name_6 = CHECK_IF_TRUE(tmp_call_result_5);
        if (tmp_truth_name_6 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_call_result_5);

            exception_lineno = 64;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_or_left_value_2 = tmp_truth_name_6 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        Py_DECREF(tmp_call_result_5);
        tmp_or_left_truth_2 = tmp_or_left_value_2 == NUITKA_BOOL_TRUE ? 1 : 0;
        if (tmp_or_left_truth_2 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 64;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        if (tmp_or_left_truth_2 == 1) {
            goto or_left_2;
        } else {
            goto or_right_2;
        }
        or_right_2:;
        tmp_called_instance_20 = IMPORT_HARD_OS();
        assert(!(tmp_called_instance_20 == NULL));
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 65;
        tmp_call_result_6 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_20,
            mod_consts[0],
            PyTuple_GET_ITEM(mod_consts[17], 0)
        );

        if (tmp_call_result_6 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 65;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_truth_name_7 = CHECK_IF_TRUE(tmp_call_result_6);
        if (tmp_truth_name_7 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_call_result_6);

            exception_lineno = 65;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_and_left_value_3 = tmp_truth_name_7 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        Py_DECREF(tmp_call_result_6);
        tmp_and_left_truth_3 = tmp_and_left_value_3 == NUITKA_BOOL_TRUE ? 1 : 0;
        if (tmp_and_left_truth_3 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 65;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        if (tmp_and_left_truth_3 == 1) {
            goto and_right_3;
        } else {
            goto and_left_3;
        }
        and_right_3:;
        tmp_called_instance_21 = IMPORT_HARD_OS();
        assert(!(tmp_called_instance_21 == NULL));
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 65;
        tmp_call_result_7 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_21,
            mod_consts[0],
            PyTuple_GET_ITEM(mod_consts[18], 0)
        );

        if (tmp_call_result_7 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 65;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_truth_name_8 = CHECK_IF_TRUE(tmp_call_result_7);
        if (tmp_truth_name_8 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_call_result_7);

            exception_lineno = 65;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_and_right_value_3 = tmp_truth_name_8 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        Py_DECREF(tmp_call_result_7);
        tmp_or_right_value_2 = tmp_and_right_value_3;
        goto and_end_3;
        and_left_3:;
        tmp_or_right_value_2 = tmp_and_left_value_3;
        and_end_3:;
        tmp_condition_result_7 = tmp_or_right_value_2;
        goto or_end_2;
        or_left_2:;
        tmp_condition_result_7 = tmp_or_left_value_2;
        or_end_2:;
        if (tmp_condition_result_7 == NUITKA_BOOL_TRUE) {
            goto branch_yes_7;
        } else {
            goto branch_no_7;
        }
    }
    branch_yes_7:;
    {
        nuitka_bool tmp_assign_source_11;
        tmp_assign_source_11 = NUITKA_BOOL_TRUE;
        var_confluence_is_setup = tmp_assign_source_11;
    }
    {
        PyObject *tmp_called_instance_22;
        PyObject *tmp_call_result_8;
        tmp_called_instance_22 = module_var_accessor_mcp_atlassian$$36$utils$$36$environment$logger(tstate);
        if (unlikely(tmp_called_instance_22 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_called_instance_22 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 68;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 68;
        tmp_call_result_8 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_22,
            mod_consts[6],
            PyTuple_GET_ITEM(mod_consts[21], 0)
        );

        if (tmp_call_result_8 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 68;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_8);
    }
    branch_no_7:;
    branch_end_5:;
    branch_end_4:;
    branch_end_3:;
    goto branch_end_2;
    branch_no_2:;
    {
        bool tmp_condition_result_8;
        PyObject *tmp_cmp_expr_left_1;
        PyObject *tmp_cmp_expr_right_1;
        PyObject *tmp_called_value_2;
        PyObject *tmp_expression_value_1;
        PyObject *tmp_called_instance_23;
        tmp_called_instance_23 = IMPORT_HARD_OS();
        assert(!(tmp_called_instance_23 == NULL));
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 71;
        tmp_expression_value_1 = CALL_METHOD_WITH_ARGS2(
            tstate,
            tmp_called_instance_23,
            mod_consts[0],
            &PyTuple_GET_ITEM(mod_consts[22], 0)
        );

        if (tmp_expression_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 71;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_called_value_2 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[23]);
        Py_DECREF(tmp_expression_value_1);
        if (tmp_called_value_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 71;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 71;
        tmp_cmp_expr_left_1 = CALL_FUNCTION_NO_ARGS(tstate, tmp_called_value_2);
        Py_DECREF(tmp_called_value_2);
        if (tmp_cmp_expr_left_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 71;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_cmp_expr_right_1 = mod_consts[24];
        tmp_res = PySequence_Contains(tmp_cmp_expr_right_1, tmp_cmp_expr_left_1);
        Py_DECREF(tmp_cmp_expr_left_1);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 71;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_8 = (tmp_res == 1) ? true : false;
        if (tmp_condition_result_8 != false) {
            goto branch_yes_8;
        } else {
            goto branch_no_8;
        }
    }
    branch_yes_8:;
    {
        nuitka_bool tmp_assign_source_12;
        tmp_assign_source_12 = NUITKA_BOOL_TRUE;
        var_confluence_is_setup = tmp_assign_source_12;
    }
    {
        PyObject *tmp_called_instance_24;
        PyObject *tmp_call_result_9;
        tmp_called_instance_24 = module_var_accessor_mcp_atlassian$$36$utils$$36$environment$logger(tstate);
        if (unlikely(tmp_called_instance_24 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_called_instance_24 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 73;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 73;
        tmp_call_result_9 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_24,
            mod_consts[6],
            PyTuple_GET_ITEM(mod_consts[25], 0)
        );

        if (tmp_call_result_9 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 73;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_9);
    }
    branch_no_8:;
    branch_end_2:;
    branch_end_1:;
    {
        PyObject *tmp_assign_source_13;
        PyObject *tmp_called_instance_25;
        tmp_called_instance_25 = IMPORT_HARD_OS();
        assert(!(tmp_called_instance_25 == NULL));
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 77;
        tmp_assign_source_13 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_25,
            mod_consts[0],
            PyTuple_GET_ITEM(mod_consts[26], 0)
        );

        if (tmp_assign_source_13 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 77;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        assert(var_jira_url == NULL);
        var_jira_url = tmp_assign_source_13;
    }
    {
        nuitka_bool tmp_assign_source_14;
        tmp_assign_source_14 = NUITKA_BOOL_FALSE;
        var_jira_is_setup = tmp_assign_source_14;
    }
    {
        nuitka_bool tmp_condition_result_9;
        int tmp_truth_name_9;
        CHECK_OBJECT(var_jira_url);
        tmp_truth_name_9 = CHECK_IF_TRUE(var_jira_url);
        if (tmp_truth_name_9 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 79;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_9 = tmp_truth_name_9 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        if (tmp_condition_result_9 == NUITKA_BOOL_TRUE) {
            goto branch_yes_9;
        } else {
            goto branch_no_9;
        }
    }
    branch_yes_9:;
    {
        PyObject *tmp_assign_source_15;
        PyObject *tmp_called_value_3;
        PyObject *tmp_args_element_value_2;
        tmp_called_value_3 = module_var_accessor_mcp_atlassian$$36$utils$$36$environment$is_atlassian_cloud_url(tstate);
        if (unlikely(tmp_called_value_3 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[8]);
        }

        if (tmp_called_value_3 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 80;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(var_jira_url);
        tmp_args_element_value_2 = var_jira_url;
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 80;
        tmp_assign_source_15 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_3, tmp_args_element_value_2);
        if (tmp_assign_source_15 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 80;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        {
            PyObject *old = var_is_cloud;
            var_is_cloud = tmp_assign_source_15;
            Py_XDECREF(old);
        }

    }
    {
        bool tmp_condition_result_10;
        PyObject *tmp_all_arg_4;
        PyObject *tmp_list_element_4;
        PyObject *tmp_called_instance_26;
        PyObject *tmp_capi_result_4;
        tmp_called_instance_26 = IMPORT_HARD_OS();
        assert(!(tmp_called_instance_26 == NULL));
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 85;
        tmp_list_element_4 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_26,
            mod_consts[0],
            PyTuple_GET_ITEM(mod_consts[9], 0)
        );

        if (tmp_list_element_4 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 85;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_all_arg_4 = MAKE_LIST_EMPTY(tstate, 5);
        {
            PyObject *tmp_called_instance_27;
            PyObject *tmp_called_instance_28;
            PyObject *tmp_called_instance_29;
            PyObject *tmp_called_instance_30;
            PyList_SET_ITEM(tmp_all_arg_4, 0, tmp_list_element_4);
            tmp_called_instance_27 = IMPORT_HARD_OS();
            assert(!(tmp_called_instance_27 == NULL));
            frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 86;
            tmp_list_element_4 = CALL_METHOD_WITH_SINGLE_ARG(
                tstate,
                tmp_called_instance_27,
                mod_consts[0],
                PyTuple_GET_ITEM(mod_consts[10], 0)
            );

            if (tmp_list_element_4 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 86;
                type_description_1 = "obooooob";
                goto list_build_exception_4;
            }
            PyList_SET_ITEM(tmp_all_arg_4, 1, tmp_list_element_4);
            tmp_called_instance_28 = IMPORT_HARD_OS();
            assert(!(tmp_called_instance_28 == NULL));
            frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 87;
            tmp_list_element_4 = CALL_METHOD_WITH_SINGLE_ARG(
                tstate,
                tmp_called_instance_28,
                mod_consts[0],
                PyTuple_GET_ITEM(mod_consts[11], 0)
            );

            if (tmp_list_element_4 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 87;
                type_description_1 = "obooooob";
                goto list_build_exception_4;
            }
            PyList_SET_ITEM(tmp_all_arg_4, 2, tmp_list_element_4);
            tmp_called_instance_29 = IMPORT_HARD_OS();
            assert(!(tmp_called_instance_29 == NULL));
            frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 88;
            tmp_list_element_4 = CALL_METHOD_WITH_SINGLE_ARG(
                tstate,
                tmp_called_instance_29,
                mod_consts[0],
                PyTuple_GET_ITEM(mod_consts[12], 0)
            );

            if (tmp_list_element_4 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 88;
                type_description_1 = "obooooob";
                goto list_build_exception_4;
            }
            PyList_SET_ITEM(tmp_all_arg_4, 3, tmp_list_element_4);
            tmp_called_instance_30 = IMPORT_HARD_OS();
            assert(!(tmp_called_instance_30 == NULL));
            frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 89;
            tmp_list_element_4 = CALL_METHOD_WITH_SINGLE_ARG(
                tstate,
                tmp_called_instance_30,
                mod_consts[0],
                PyTuple_GET_ITEM(mod_consts[13], 0)
            );

            if (tmp_list_element_4 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 89;
                type_description_1 = "obooooob";
                goto list_build_exception_4;
            }
            PyList_SET_ITEM(tmp_all_arg_4, 4, tmp_list_element_4);
        }
        goto list_build_noexception_4;
        // Exception handling pass through code for list_build:
        list_build_exception_4:;
        Py_DECREF(tmp_all_arg_4);
        goto frame_exception_exit_1;
        // Finished with no exception for list_build:
        list_build_noexception_4:;
        tmp_capi_result_4 = BUILTIN_ALL(tstate, tmp_all_arg_4);
        Py_DECREF(tmp_all_arg_4);
        if (tmp_capi_result_4 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 83;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_10 = CHECK_IF_TRUE(tmp_capi_result_4) == 1;
        Py_DECREF(tmp_capi_result_4);
        if (tmp_condition_result_10 != false) {
            goto branch_yes_10;
        } else {
            goto branch_no_10;
        }
    }
    branch_yes_10:;
    {
        nuitka_bool tmp_assign_source_16;
        tmp_assign_source_16 = NUITKA_BOOL_TRUE;
        var_jira_is_setup = tmp_assign_source_16;
    }
    {
        PyObject *tmp_called_instance_31;
        PyObject *tmp_call_result_10;
        tmp_called_instance_31 = module_var_accessor_mcp_atlassian$$36$utils$$36$environment$logger(tstate);
        if (unlikely(tmp_called_instance_31 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_called_instance_31 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 93;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 93;
        tmp_call_result_10 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_31,
            mod_consts[6],
            PyTuple_GET_ITEM(mod_consts[27], 0)
        );

        if (tmp_call_result_10 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 93;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_10);
    }
    goto branch_end_10;
    branch_no_10:;
    {
        bool tmp_condition_result_11;
        PyObject *tmp_all_arg_5;
        PyObject *tmp_list_element_5;
        PyObject *tmp_called_instance_32;
        PyObject *tmp_capi_result_5;
        tmp_called_instance_32 = IMPORT_HARD_OS();
        assert(!(tmp_called_instance_32 == NULL));
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 98;
        tmp_list_element_5 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_32,
            mod_consts[0],
            PyTuple_GET_ITEM(mod_consts[15], 0)
        );

        if (tmp_list_element_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 98;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_all_arg_5 = MAKE_LIST_EMPTY(tstate, 2);
        {
            PyObject *tmp_called_instance_33;
            PyList_SET_ITEM(tmp_all_arg_5, 0, tmp_list_element_5);
            tmp_called_instance_33 = IMPORT_HARD_OS();
            assert(!(tmp_called_instance_33 == NULL));
            frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 99;
            tmp_list_element_5 = CALL_METHOD_WITH_SINGLE_ARG(
                tstate,
                tmp_called_instance_33,
                mod_consts[0],
                PyTuple_GET_ITEM(mod_consts[13], 0)
            );

            if (tmp_list_element_5 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 99;
                type_description_1 = "obooooob";
                goto list_build_exception_5;
            }
            PyList_SET_ITEM(tmp_all_arg_5, 1, tmp_list_element_5);
        }
        goto list_build_noexception_5;
        // Exception handling pass through code for list_build:
        list_build_exception_5:;
        Py_DECREF(tmp_all_arg_5);
        goto frame_exception_exit_1;
        // Finished with no exception for list_build:
        list_build_noexception_5:;
        tmp_capi_result_5 = BUILTIN_ALL(tstate, tmp_all_arg_5);
        Py_DECREF(tmp_all_arg_5);
        if (tmp_capi_result_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 96;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_11 = CHECK_IF_TRUE(tmp_capi_result_5) == 1;
        Py_DECREF(tmp_capi_result_5);
        if (tmp_condition_result_11 != false) {
            goto branch_yes_11;
        } else {
            goto branch_no_11;
        }
    }
    branch_yes_11:;
    {
        nuitka_bool tmp_assign_source_17;
        tmp_assign_source_17 = NUITKA_BOOL_TRUE;
        var_jira_is_setup = tmp_assign_source_17;
    }
    {
        PyObject *tmp_called_instance_34;
        PyObject *tmp_call_result_11;
        tmp_called_instance_34 = module_var_accessor_mcp_atlassian$$36$utils$$36$environment$logger(tstate);
        if (unlikely(tmp_called_instance_34 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_called_instance_34 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 103;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 103;
        tmp_call_result_11 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_34,
            mod_consts[6],
            PyTuple_GET_ITEM(mod_consts[28], 0)
        );

        if (tmp_call_result_11 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 103;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_11);
    }
    goto branch_end_11;
    branch_no_11:;
    {
        nuitka_bool tmp_condition_result_12;
        int tmp_truth_name_10;
        CHECK_OBJECT(var_is_cloud);
        tmp_truth_name_10 = CHECK_IF_TRUE(var_is_cloud);
        if (tmp_truth_name_10 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 107;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_12 = tmp_truth_name_10 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        if (tmp_condition_result_12 == NUITKA_BOOL_TRUE) {
            goto branch_yes_12;
        } else {
            goto branch_no_12;
        }
    }
    branch_yes_12:;
    {
        bool tmp_condition_result_13;
        PyObject *tmp_all_arg_6;
        PyObject *tmp_list_element_6;
        PyObject *tmp_called_instance_35;
        PyObject *tmp_capi_result_6;
        tmp_called_instance_35 = IMPORT_HARD_OS();
        assert(!(tmp_called_instance_35 == NULL));
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 110;
        tmp_list_element_6 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_35,
            mod_consts[0],
            PyTuple_GET_ITEM(mod_consts[29], 0)
        );

        if (tmp_list_element_6 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 110;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_all_arg_6 = MAKE_LIST_EMPTY(tstate, 2);
        {
            PyObject *tmp_called_instance_36;
            PyList_SET_ITEM(tmp_all_arg_6, 0, tmp_list_element_6);
            tmp_called_instance_36 = IMPORT_HARD_OS();
            assert(!(tmp_called_instance_36 == NULL));
            frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 111;
            tmp_list_element_6 = CALL_METHOD_WITH_SINGLE_ARG(
                tstate,
                tmp_called_instance_36,
                mod_consts[0],
                PyTuple_GET_ITEM(mod_consts[30], 0)
            );

            if (tmp_list_element_6 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 111;
                type_description_1 = "obooooob";
                goto list_build_exception_6;
            }
            PyList_SET_ITEM(tmp_all_arg_6, 1, tmp_list_element_6);
        }
        goto list_build_noexception_6;
        // Exception handling pass through code for list_build:
        list_build_exception_6:;
        Py_DECREF(tmp_all_arg_6);
        goto frame_exception_exit_1;
        // Finished with no exception for list_build:
        list_build_noexception_6:;
        tmp_capi_result_6 = BUILTIN_ALL(tstate, tmp_all_arg_6);
        Py_DECREF(tmp_all_arg_6);
        if (tmp_capi_result_6 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 108;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_13 = CHECK_IF_TRUE(tmp_capi_result_6) == 1;
        Py_DECREF(tmp_capi_result_6);
        if (tmp_condition_result_13 != false) {
            goto branch_yes_13;
        } else {
            goto branch_no_13;
        }
    }
    branch_yes_13:;
    {
        nuitka_bool tmp_assign_source_18;
        tmp_assign_source_18 = NUITKA_BOOL_TRUE;
        var_jira_is_setup = tmp_assign_source_18;
    }
    {
        PyObject *tmp_called_instance_37;
        PyObject *tmp_call_result_12;
        tmp_called_instance_37 = module_var_accessor_mcp_atlassian$$36$utils$$36$environment$logger(tstate);
        if (unlikely(tmp_called_instance_37 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_called_instance_37 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 115;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 115;
        tmp_call_result_12 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_37,
            mod_consts[6],
            PyTuple_GET_ITEM(mod_consts[31], 0)
        );

        if (tmp_call_result_12 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 115;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_12);
    }
    branch_no_13:;
    goto branch_end_12;
    branch_no_12:;
    {
        nuitka_bool tmp_condition_result_14;
        int tmp_or_left_truth_3;
        nuitka_bool tmp_or_left_value_3;
        nuitka_bool tmp_or_right_value_3;
        PyObject *tmp_called_instance_38;
        PyObject *tmp_call_result_13;
        int tmp_truth_name_11;
        int tmp_and_left_truth_4;
        nuitka_bool tmp_and_left_value_4;
        nuitka_bool tmp_and_right_value_4;
        PyObject *tmp_called_instance_39;
        PyObject *tmp_call_result_14;
        int tmp_truth_name_12;
        PyObject *tmp_called_instance_40;
        PyObject *tmp_call_result_15;
        int tmp_truth_name_13;
        tmp_called_instance_38 = IMPORT_HARD_OS();
        assert(!(tmp_called_instance_38 == NULL));
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 117;
        tmp_call_result_13 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_38,
            mod_consts[0],
            PyTuple_GET_ITEM(mod_consts[32], 0)
        );

        if (tmp_call_result_13 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 117;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_truth_name_11 = CHECK_IF_TRUE(tmp_call_result_13);
        if (tmp_truth_name_11 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_call_result_13);

            exception_lineno = 117;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_or_left_value_3 = tmp_truth_name_11 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        Py_DECREF(tmp_call_result_13);
        tmp_or_left_truth_3 = tmp_or_left_value_3 == NUITKA_BOOL_TRUE ? 1 : 0;
        if (tmp_or_left_truth_3 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 117;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        if (tmp_or_left_truth_3 == 1) {
            goto or_left_3;
        } else {
            goto or_right_3;
        }
        or_right_3:;
        tmp_called_instance_39 = IMPORT_HARD_OS();
        assert(!(tmp_called_instance_39 == NULL));
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 118;
        tmp_call_result_14 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_39,
            mod_consts[0],
            PyTuple_GET_ITEM(mod_consts[29], 0)
        );

        if (tmp_call_result_14 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 118;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_truth_name_12 = CHECK_IF_TRUE(tmp_call_result_14);
        if (tmp_truth_name_12 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_call_result_14);

            exception_lineno = 118;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_and_left_value_4 = tmp_truth_name_12 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        Py_DECREF(tmp_call_result_14);
        tmp_and_left_truth_4 = tmp_and_left_value_4 == NUITKA_BOOL_TRUE ? 1 : 0;
        if (tmp_and_left_truth_4 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 118;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        if (tmp_and_left_truth_4 == 1) {
            goto and_right_4;
        } else {
            goto and_left_4;
        }
        and_right_4:;
        tmp_called_instance_40 = IMPORT_HARD_OS();
        assert(!(tmp_called_instance_40 == NULL));
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 118;
        tmp_call_result_15 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_40,
            mod_consts[0],
            PyTuple_GET_ITEM(mod_consts[30], 0)
        );

        if (tmp_call_result_15 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 118;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_truth_name_13 = CHECK_IF_TRUE(tmp_call_result_15);
        if (tmp_truth_name_13 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_call_result_15);

            exception_lineno = 118;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_and_right_value_4 = tmp_truth_name_13 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        Py_DECREF(tmp_call_result_15);
        tmp_or_right_value_3 = tmp_and_right_value_4;
        goto and_end_4;
        and_left_4:;
        tmp_or_right_value_3 = tmp_and_left_value_4;
        and_end_4:;
        tmp_condition_result_14 = tmp_or_right_value_3;
        goto or_end_3;
        or_left_3:;
        tmp_condition_result_14 = tmp_or_left_value_3;
        or_end_3:;
        if (tmp_condition_result_14 == NUITKA_BOOL_TRUE) {
            goto branch_yes_14;
        } else {
            goto branch_no_14;
        }
    }
    branch_yes_14:;
    {
        nuitka_bool tmp_assign_source_19;
        tmp_assign_source_19 = NUITKA_BOOL_TRUE;
        var_jira_is_setup = tmp_assign_source_19;
    }
    {
        PyObject *tmp_called_instance_41;
        PyObject *tmp_call_result_16;
        tmp_called_instance_41 = module_var_accessor_mcp_atlassian$$36$utils$$36$environment$logger(tstate);
        if (unlikely(tmp_called_instance_41 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_called_instance_41 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 121;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 121;
        tmp_call_result_16 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_41,
            mod_consts[6],
            PyTuple_GET_ITEM(mod_consts[33], 0)
        );

        if (tmp_call_result_16 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 121;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_16);
    }
    branch_no_14:;
    branch_end_12:;
    branch_end_11:;
    branch_end_10:;
    goto branch_end_9;
    branch_no_9:;
    {
        bool tmp_condition_result_15;
        PyObject *tmp_cmp_expr_left_2;
        PyObject *tmp_cmp_expr_right_2;
        PyObject *tmp_called_value_4;
        PyObject *tmp_expression_value_2;
        PyObject *tmp_called_instance_42;
        tmp_called_instance_42 = IMPORT_HARD_OS();
        assert(!(tmp_called_instance_42 == NULL));
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 124;
        tmp_expression_value_2 = CALL_METHOD_WITH_ARGS2(
            tstate,
            tmp_called_instance_42,
            mod_consts[0],
            &PyTuple_GET_ITEM(mod_consts[22], 0)
        );

        if (tmp_expression_value_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 124;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_called_value_4 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_2, mod_consts[23]);
        Py_DECREF(tmp_expression_value_2);
        if (tmp_called_value_4 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 124;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 124;
        tmp_cmp_expr_left_2 = CALL_FUNCTION_NO_ARGS(tstate, tmp_called_value_4);
        Py_DECREF(tmp_called_value_4);
        if (tmp_cmp_expr_left_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 124;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_cmp_expr_right_2 = mod_consts[24];
        tmp_res = PySequence_Contains(tmp_cmp_expr_right_2, tmp_cmp_expr_left_2);
        Py_DECREF(tmp_cmp_expr_left_2);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 124;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_15 = (tmp_res == 1) ? true : false;
        if (tmp_condition_result_15 != false) {
            goto branch_yes_15;
        } else {
            goto branch_no_15;
        }
    }
    branch_yes_15:;
    {
        nuitka_bool tmp_assign_source_20;
        tmp_assign_source_20 = NUITKA_BOOL_TRUE;
        var_jira_is_setup = tmp_assign_source_20;
    }
    {
        PyObject *tmp_called_instance_43;
        PyObject *tmp_call_result_17;
        tmp_called_instance_43 = module_var_accessor_mcp_atlassian$$36$utils$$36$environment$logger(tstate);
        if (unlikely(tmp_called_instance_43 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_called_instance_43 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 126;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 126;
        tmp_call_result_17 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_43,
            mod_consts[6],
            PyTuple_GET_ITEM(mod_consts[34], 0)
        );

        if (tmp_call_result_17 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 126;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_17);
    }
    branch_no_15:;
    branch_end_9:;
    {
        bool tmp_condition_result_16;
        PyObject *tmp_operand_value_1;
        assert(var_confluence_is_setup != NUITKA_BOOL_UNASSIGNED);
        tmp_operand_value_1 = (var_confluence_is_setup == NUITKA_BOOL_TRUE) ? Py_True : Py_False;
        tmp_res = CHECK_IF_TRUE(tmp_operand_value_1);
        assert(!(tmp_res == -1));
        tmp_condition_result_16 = (tmp_res == 0) ? true : false;
        if (tmp_condition_result_16 != false) {
            goto branch_yes_16;
        } else {
            goto branch_no_16;
        }
    }
    branch_yes_16:;
    {
        PyObject *tmp_called_instance_44;
        PyObject *tmp_call_result_18;
        tmp_called_instance_44 = module_var_accessor_mcp_atlassian$$36$utils$$36$environment$logger(tstate);
        if (unlikely(tmp_called_instance_44 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_called_instance_44 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 131;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 131;
        tmp_call_result_18 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_44,
            mod_consts[6],
            PyTuple_GET_ITEM(mod_consts[35], 0)
        );

        if (tmp_call_result_18 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 131;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_18);
    }
    branch_no_16:;
    {
        bool tmp_condition_result_17;
        PyObject *tmp_operand_value_2;
        assert(var_jira_is_setup != NUITKA_BOOL_UNASSIGNED);
        tmp_operand_value_2 = (var_jira_is_setup == NUITKA_BOOL_TRUE) ? Py_True : Py_False;
        tmp_res = CHECK_IF_TRUE(tmp_operand_value_2);
        assert(!(tmp_res == -1));
        tmp_condition_result_17 = (tmp_res == 0) ? true : false;
        if (tmp_condition_result_17 != false) {
            goto branch_yes_17;
        } else {
            goto branch_no_17;
        }
    }
    branch_yes_17:;
    {
        PyObject *tmp_called_instance_45;
        PyObject *tmp_call_result_19;
        tmp_called_instance_45 = module_var_accessor_mcp_atlassian$$36$utils$$36$environment$logger(tstate);
        if (unlikely(tmp_called_instance_45 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_called_instance_45 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 135;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame.f_lineno = 135;
        tmp_call_result_19 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_45,
            mod_consts[6],
            PyTuple_GET_ITEM(mod_consts[36], 0)
        );

        if (tmp_call_result_19 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 135;
            type_description_1 = "obooooob";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_19);
    }
    branch_no_17:;


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services,
        type_description_1,
        var_confluence_url,
        (int)var_confluence_is_setup,
        var_intsig_url,
        var_intsig_username,
        var_intsig_password,
        var_is_cloud,
        var_jira_url,
        (int)var_jira_is_setup
    );


    // Release cached frame if used for exception.
    if (frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services == cache_frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services);
        cache_frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services = NULL;
    }

    assertFrameObject(frame_frame_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[37];
        assert(var_confluence_is_setup != NUITKA_BOOL_UNASSIGNED);
        tmp_dict_value_1 = (var_confluence_is_setup == NUITKA_BOOL_TRUE) ? Py_True : Py_False;
        tmp_return_value = _PyDict_NewPresized( 2 );
        tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[38];
        assert(var_jira_is_setup != NUITKA_BOOL_UNASSIGNED);
        tmp_dict_value_1 = (var_jira_is_setup == NUITKA_BOOL_TRUE) ? Py_True : Py_False;
        tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        goto try_return_handler_1;
    }
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Return handler code:
    try_return_handler_1:;
    CHECK_OBJECT(var_confluence_url);
    Py_DECREF(var_confluence_url);
    var_confluence_url = NULL;
    assert(var_confluence_is_setup != NUITKA_BOOL_UNASSIGNED);
    var_confluence_is_setup = NUITKA_BOOL_UNASSIGNED;
    CHECK_OBJECT(var_intsig_url);
    Py_DECREF(var_intsig_url);
    var_intsig_url = NULL;
    CHECK_OBJECT(var_intsig_username);
    Py_DECREF(var_intsig_username);
    var_intsig_username = NULL;
    CHECK_OBJECT(var_intsig_password);
    Py_DECREF(var_intsig_password);
    var_intsig_password = NULL;
    Py_XDECREF(var_is_cloud);
    var_is_cloud = NULL;
    CHECK_OBJECT(var_jira_url);
    Py_DECREF(var_jira_url);
    var_jira_url = NULL;
    assert(var_jira_is_setup != NUITKA_BOOL_UNASSIGNED);
    var_jira_is_setup = NUITKA_BOOL_UNASSIGNED;
    goto function_return_exit;
    // Exception handler code:
    try_except_handler_1:;
    exception_keeper_lineno_1 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_1 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    Py_XDECREF(var_confluence_url);
    var_confluence_url = NULL;
    var_confluence_is_setup = NUITKA_BOOL_UNASSIGNED;
    Py_XDECREF(var_intsig_url);
    var_intsig_url = NULL;
    Py_XDECREF(var_intsig_username);
    var_intsig_username = NULL;
    Py_XDECREF(var_intsig_password);
    var_intsig_password = NULL;
    Py_XDECREF(var_is_cloud);
    var_is_cloud = NULL;
    Py_XDECREF(var_jira_url);
    var_jira_url = NULL;
    var_jira_is_setup = NUITKA_BOOL_UNASSIGNED;
    // Re-raise.
    exception_state = exception_keeper_name_1;
    exception_lineno = exception_keeper_lineno_1;

    goto function_exception_exit;
    // End of try:

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:

    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.


   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}



static PyObject *MAKE_FUNCTION_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services(PyThreadState *tstate, PyObject *annotations) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services,
        mod_consts[53],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_6380f0aa092288274df7ae9483b2d393,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_mcp_atlassian$utils$environment,
        mod_consts[39],
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

static function_impl_code const function_table_mcp_atlassian$utils$environment[] = {
    impl_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services,
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

    return Nuitka_Function_GetFunctionState(function, function_table_mcp_atlassian$utils$environment);
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
        module_mcp_atlassian$utils$environment,
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
        function_table_mcp_atlassian$utils$environment,
        sizeof(function_table_mcp_atlassian$utils$environment) / sizeof(function_impl_code)
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
static char const *module_full_name = "mcp_atlassian.utils.environment";
#endif

// Internal entry point for module code.
PyObject *modulecode_mcp_atlassian$utils$environment(PyThreadState *tstate, PyObject *module, struct Nuitka_MetaPathBasedLoaderEntry const *loader_entry) {
    // Report entry to PGO.
    PGO_onModuleEntered("mcp_atlassian$utils$environment");

    // Store the module for future use.
    module_mcp_atlassian$utils$environment = module;

    moduledict_mcp_atlassian$utils$environment = MODULE_DICT(module_mcp_atlassian$utils$environment);

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
        PRINT_STRING("mcp_atlassian$utils$environment: Calling setupMetaPathBasedLoader().\n");
#endif
        setupMetaPathBasedLoader(tstate);
#if 0 >= 0
#ifdef _NUITKA_TRACE
        PRINT_STRING("mcp_atlassian$utils$environment: Calling updateMetaPathBasedLoaderModuleRoot().\n");
#endif
        updateMetaPathBasedLoaderModuleRoot(module_full_name);
#endif


#if PYTHON_VERSION >= 0x300
        patchInspectModule(tstate);
#endif

#endif

        /* The constants only used by this module are created now. */
        NUITKA_PRINT_TRACE("mcp_atlassian$utils$environment: Calling createModuleConstants().\n");
        createModuleConstants(tstate);

#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
        createModuleCodeObjects();
#endif
        init_done = true;
    }

#if _NUITKA_MODULE_MODE && 0
    PyObject *pre_load = IMPORT_EMBEDDED_MODULE(tstate, "mcp_atlassian.utils.environment" "-preLoad");
    if (pre_load == NULL) {
        return NULL;
    }
#endif

    // PRINT_STRING("in initmcp_atlassian$utils$environment\n");

#ifdef _NUITKA_PLUGIN_DILL_ENABLED
    {
        char const *module_name_c;
        if (loader_entry != NULL) {
            module_name_c = loader_entry->name;
        } else {
            PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)const_str_plain___name__);
            module_name_c = Nuitka_String_AsString(module_name);
        }

        registerDillPluginTables(tstate, module_name_c, &_method_def_reduce_compiled_function, &_method_def_create_compiled_function);
    }
#endif

    // Set "__compiled__" to what version information we have.
    UPDATE_STRING_DICT0(
        moduledict_mcp_atlassian$utils$environment,
        (Nuitka_StringObject *)const_str_plain___compiled__,
        Nuitka_dunder_compiled_value
    );

    // Update "__package__" value to what it ought to be.
    {
#if 0
        UPDATE_STRING_DICT0(
            moduledict_mcp_atlassian$utils$environment,
            (Nuitka_StringObject *)const_str_plain___package__,
            mod_consts[57]
        );
#elif 0
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)const_str_plain___name__);

        UPDATE_STRING_DICT0(
            moduledict_mcp_atlassian$utils$environment,
            (Nuitka_StringObject *)const_str_plain___package__,
            module_name
        );
#else

#if PYTHON_VERSION < 0x300
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)const_str_plain___name__);
        char const *module_name_cstr = PyString_AS_STRING(module_name);

        char const *last_dot = strrchr(module_name_cstr, '.');

        if (last_dot != NULL) {
            UPDATE_STRING_DICT1(
                moduledict_mcp_atlassian$utils$environment,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyString_FromStringAndSize(module_name_cstr, last_dot - module_name_cstr)
            );
        }
#else
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)const_str_plain___name__);
        Py_ssize_t dot_index = PyUnicode_Find(module_name, const_str_dot, 0, PyUnicode_GetLength(module_name), -1);

        if (dot_index != -1) {
            UPDATE_STRING_DICT1(
                moduledict_mcp_atlassian$utils$environment,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyUnicode_Substring(module_name, 0, dot_index)
            );
        }
#endif
#endif
    }

    CHECK_OBJECT(module_mcp_atlassian$utils$environment);

    // For deep importing of a module we need to have "__builtins__", so we set
    // it ourselves in the same way than CPython does. Note: This must be done
    // before the frame object is allocated, or else it may fail.

    if (GET_STRING_DICT_VALUE(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)const_str_plain___builtins__) == NULL) {
        PyObject *value = (PyObject *)builtin_module;

        // Check if main module, not a dict then but the module itself.
#if _NUITKA_MODULE_MODE || !0
        value = PyModule_GetDict(value);
#endif

        UPDATE_STRING_DICT0(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)const_str_plain___builtins__, value);
    }

    PyObject *module_loader = Nuitka_Loader_New(loader_entry);
    UPDATE_STRING_DICT0(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)const_str_plain___loader__, module_loader);

#if PYTHON_VERSION >= 0x300
// Set the "__spec__" value

#if 0
    // Main modules just get "None" as spec.
    UPDATE_STRING_DICT0(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)const_str_plain___spec__, Py_None);
#else
    // Other modules get a "ModuleSpec" from the standard mechanism.
    {
        PyObject *bootstrap_module = getImportLibBootstrapModule();
        CHECK_OBJECT(bootstrap_module);

        PyObject *_spec_from_module = PyObject_GetAttrString(bootstrap_module, "_spec_from_module");
        CHECK_OBJECT(_spec_from_module);

        PyObject *spec_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, _spec_from_module, module_mcp_atlassian$utils$environment);
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

        UPDATE_STRING_DICT1(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)const_str_plain___spec__, spec_value);
    }
#endif
#endif

    // Temp variables if any
    struct Nuitka_FrameObject *frame_frame_mcp_atlassian$utils$environment;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    bool tmp_result;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;

    // Module init code if any


    // Module code.
    {
        PyObject *tmp_assign_source_1;
        tmp_assign_source_1 = mod_consts[40];
        UPDATE_STRING_DICT0(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)mod_consts[41], tmp_assign_source_1);
    }
    {
        PyObject *tmp_assign_source_2;
        tmp_assign_source_2 = module_filename_obj;
        UPDATE_STRING_DICT0(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)mod_consts[42], tmp_assign_source_2);
    }
    frame_frame_mcp_atlassian$utils$environment = MAKE_MODULE_FRAME(code_objects_0e427739627123b53bc4e1a4ec018506, module_mcp_atlassian$utils$environment);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_mcp_atlassian$utils$environment);
    assert(Py_REFCNT(frame_frame_mcp_atlassian$utils$environment) == 2);

    // Framed code:
    {
        PyObject *tmp_assattr_value_1;
        PyObject *tmp_assattr_target_1;
        tmp_assattr_value_1 = module_filename_obj;
        tmp_assattr_target_1 = module_var_accessor_mcp_atlassian$$36$utils$$36$environment$__spec__(tstate);
        assert(!(tmp_assattr_target_1 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_1, mod_consts[43], tmp_assattr_value_1);
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
        tmp_assattr_target_2 = module_var_accessor_mcp_atlassian$$36$utils$$36$environment$__spec__(tstate);
        assert(!(tmp_assattr_target_2 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_2, mod_consts[44], tmp_assattr_value_2);
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
        UPDATE_STRING_DICT0(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)mod_consts[45], tmp_assign_source_3);
    }
    {
        PyObject *tmp_assign_source_4;
        PyObject *tmp_name_value_1;
        PyObject *tmp_globals_arg_value_1;
        PyObject *tmp_locals_arg_value_1;
        PyObject *tmp_fromlist_value_1;
        PyObject *tmp_level_value_1;
        tmp_name_value_1 = mod_consts[46];
        tmp_globals_arg_value_1 = (PyObject *)moduledict_mcp_atlassian$utils$environment;
        tmp_locals_arg_value_1 = Py_None;
        tmp_fromlist_value_1 = Py_None;
        tmp_level_value_1 = const_int_0;
        frame_frame_mcp_atlassian$utils$environment->m_frame.f_lineno = 3;
        tmp_assign_source_4 = IMPORT_MODULE5(tstate, tmp_name_value_1, tmp_globals_arg_value_1, tmp_locals_arg_value_1, tmp_fromlist_value_1, tmp_level_value_1);
        if (tmp_assign_source_4 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 3;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)mod_consts[46], tmp_assign_source_4);
    }
    {
        PyObject *tmp_assign_source_5;
        tmp_assign_source_5 = IMPORT_HARD_OS();
        assert(!(tmp_assign_source_5 == NULL));
        UPDATE_STRING_DICT0(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)mod_consts[47], tmp_assign_source_5);
    }
    {
        PyObject *tmp_assign_source_6;
        PyObject *tmp_import_name_from_1;
        PyObject *tmp_name_value_2;
        PyObject *tmp_globals_arg_value_2;
        PyObject *tmp_locals_arg_value_2;
        PyObject *tmp_fromlist_value_2;
        PyObject *tmp_level_value_2;
        tmp_name_value_2 = mod_consts[48];
        tmp_globals_arg_value_2 = (PyObject *)moduledict_mcp_atlassian$utils$environment;
        tmp_locals_arg_value_2 = Py_None;
        tmp_fromlist_value_2 = mod_consts[49];
        tmp_level_value_2 = const_int_pos_1;
        frame_frame_mcp_atlassian$utils$environment->m_frame.f_lineno = 6;
        tmp_import_name_from_1 = IMPORT_MODULE5(tstate, tmp_name_value_2, tmp_globals_arg_value_2, tmp_locals_arg_value_2, tmp_fromlist_value_2, tmp_level_value_2);
        if (tmp_import_name_from_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 6;

            goto frame_exception_exit_1;
        }
        if (PyModule_Check(tmp_import_name_from_1)) {
            tmp_assign_source_6 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_1,
                (PyObject *)moduledict_mcp_atlassian$utils$environment,
                mod_consts[8],
                const_int_0
            );
        } else {
            tmp_assign_source_6 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_1, mod_consts[8]);
        }

        Py_DECREF(tmp_import_name_from_1);
        if (tmp_assign_source_6 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 6;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)mod_consts[8], tmp_assign_source_6);
    }
    {
        PyObject *tmp_assign_source_7;
        PyObject *tmp_called_instance_1;
        tmp_called_instance_1 = module_var_accessor_mcp_atlassian$$36$utils$$36$environment$logging(tstate);
        if (unlikely(tmp_called_instance_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[46]);
        }

        if (tmp_called_instance_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 8;

            goto frame_exception_exit_1;
        }
        frame_frame_mcp_atlassian$utils$environment->m_frame.f_lineno = 8;
        tmp_assign_source_7 = CALL_METHOD_WITH_SINGLE_ARG(
            tstate,
            tmp_called_instance_1,
            mod_consts[50],
            PyTuple_GET_ITEM(mod_consts[51], 0)
        );

        if (tmp_assign_source_7 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 8;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)mod_consts[5], tmp_assign_source_7);
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_mcp_atlassian$utils$environment, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_mcp_atlassian$utils$environment->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_mcp_atlassian$utils$environment, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }



    assertFrameObject(frame_frame_mcp_atlassian$utils$environment);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto module_exception_exit;
    frame_no_exception_1:;
    {
        PyObject *tmp_assign_source_8;
        PyObject *tmp_annotations_1;
        tmp_annotations_1 = DICT_COPY(tstate, mod_consts[52]);


        tmp_assign_source_8 = MAKE_FUNCTION_mcp_atlassian$utils$environment$$36$$$36$$$36$function__1_get_available_services(tstate, tmp_annotations_1);

        UPDATE_STRING_DICT1(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)mod_consts[53], tmp_assign_source_8);
    }

    // Report to PGO about leaving the module without error.
    PGO_onModuleExit("mcp_atlassian$utils$environment", false);

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *post_load = IMPORT_EMBEDDED_MODULE(tstate, "mcp_atlassian.utils.environment" "-postLoad");
        if (post_load == NULL) {
            return NULL;
        }
    }
#endif

    Py_INCREF(module_mcp_atlassian$utils$environment);
    return module_mcp_atlassian$utils$environment;
    module_exception_exit:

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_mcp_atlassian$utils$environment, (Nuitka_StringObject *)const_str_plain___name__);

        if (module_name != NULL) {
            Nuitka_DelModule(tstate, module_name);
        }
    }
#endif
    PGO_onModuleExit("mcp_atlassian$utils$environment", false);

    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);
    return NULL;
}
