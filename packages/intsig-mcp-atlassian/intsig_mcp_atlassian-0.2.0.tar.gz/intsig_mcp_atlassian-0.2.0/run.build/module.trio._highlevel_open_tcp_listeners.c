/* Generated code for Python module 'trio$_highlevel_open_tcp_listeners'
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

/* The "module_trio$_highlevel_open_tcp_listeners" is a Python object pointer of module type.
 *
 * Note: For full compatibility with CPython, every module variable access
 * needs to go through it except for cases where the module cannot possibly
 * have changed in the mean time.
 */

PyObject *module_trio$_highlevel_open_tcp_listeners;
PyDictObject *moduledict_trio$_highlevel_open_tcp_listeners;

/* The declarations of module constants used, if any. */
static PyObject *mod_consts[65];
#ifndef __NUITKA_NO_ASSERT__
static Py_hash_t mod_consts_hash[65];
#endif

static PyObject *module_filename_obj = NULL;

/* Indicator if this modules private constants were created yet. */
static bool constants_created = false;

/* Function to create module private constants. */
static void createModuleConstants(PyThreadState *tstate) {
    if (constants_created == false) {
        loadConstantsBlob(tstate, &mod_consts[0], UN_TRANSLATE("trio._highlevel_open_tcp_listeners"));
        constants_created = true;

#ifndef __NUITKA_NO_ASSERT__
        for (int i = 0; i < 65; i++) {
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
void checkModuleConstants_trio$_highlevel_open_tcp_listeners(PyThreadState *tstate) {
    // The module may not have been used at all, then ignore this.
    if (constants_created == false) return;

    for (int i = 0; i < 65; i++) {
        assert(mod_consts_hash[i] == DEEP_HASH(tstate, mod_consts[i]));
        CHECK_OBJECT_DEEP(mod_consts[i]);
    }
}
#endif

// Helper to preserving module variables for Python3.11+
#if 6
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
static PyObject *module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$ExceptionGroup(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_trio$_highlevel_open_tcp_listeners->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_trio$_highlevel_open_tcp_listeners->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[31]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_trio$_highlevel_open_tcp_listeners->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[31]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[31]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[31]);
    }

    return result;
}

static PyObject *module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$__spec__(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_trio$_highlevel_open_tcp_listeners->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_trio$_highlevel_open_tcp_listeners->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[64]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_trio$_highlevel_open_tcp_listeners->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[64]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[64], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[64]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[64], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[64]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[64]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[64]);
    }

    return result;
}

static PyObject *module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$_compute_backlog(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_trio$_highlevel_open_tcp_listeners->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_trio$_highlevel_open_tcp_listeners->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[7]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_trio$_highlevel_open_tcp_listeners->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[7]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[7], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[7]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[7], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[7]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[7]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[7]);
    }

    return result;
}

static PyObject *module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$errno(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_trio$_highlevel_open_tcp_listeners->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_trio$_highlevel_open_tcp_listeners->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[16]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_trio$_highlevel_open_tcp_listeners->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[16]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[16]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[16]);
    }

    return result;
}

static PyObject *module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$trio(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_trio$_highlevel_open_tcp_listeners->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_trio$_highlevel_open_tcp_listeners->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[27]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_trio$_highlevel_open_tcp_listeners->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[27]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[27], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[27]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[27], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[27]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[27]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[27]);
    }

    return result;
}

static PyObject *module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$tsocket(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_trio$_highlevel_open_tcp_listeners->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_trio$_highlevel_open_tcp_listeners->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[9]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_trio$_highlevel_open_tcp_listeners->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[9]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[9], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[9]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[9], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[9]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[9]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[9]);
    }

    return result;
}


#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
// The module code objects.
static PyCodeObject *code_objects_d605a67f1ef0ef685be8dc5ba72b7cff;
static PyCodeObject *code_objects_a5c538db960641bfcf6a0f2c68eb3d35;
static PyCodeObject *code_objects_e8c68bf30da4df84e255a3b70495ca70;
static PyCodeObject *code_objects_2fb6da62d72bae8c939c2f4bacd9c5af;

static void createModuleCodeObjects(void) {
    module_filename_obj = MAKE_RELATIVE_PATH(mod_consts[59]); CHECK_OBJECT(module_filename_obj);
    code_objects_d605a67f1ef0ef685be8dc5ba72b7cff = MAKE_CODE_OBJECT(module_filename_obj, 1, CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[60], mod_consts[60], NULL, NULL, 0, 0, 0);
    code_objects_a5c538db960641bfcf6a0f2c68eb3d35 = MAKE_CODE_OBJECT(module_filename_obj, 46, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[7], mod_consts[7], mod_consts[61], NULL, 1, 0, 0);
    code_objects_e8c68bf30da4df84e255a3b70495ca70 = MAKE_CODE_OBJECT(module_filename_obj, 57, CO_COROUTINE | CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[32], mod_consts[32], mod_consts[62], NULL, 1, 2, 0);
    code_objects_2fb6da62d72bae8c939c2f4bacd9c5af = MAKE_CODE_OBJECT(module_filename_obj, 172, CO_COROUTINE | CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[40], mod_consts[40], mod_consts[63], NULL, 2, 4, 0);
}
#endif

// The module function declarations.
static PyObject *MAKE_COROUTINE_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__2_open_tcp_listeners$$36$$$36$$$36$coroutine__1_open_tcp_listeners(PyThreadState *tstate, struct Nuitka_CellObject **closure);


static PyObject *MAKE_COROUTINE_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__3_serve_tcp$$36$$$36$$$36$coroutine__1_serve_tcp(PyThreadState *tstate, struct Nuitka_CellObject **closure);


static PyObject *MAKE_FUNCTION_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog(PyThreadState *tstate, PyObject *annotations);


static PyObject *MAKE_FUNCTION_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__2_open_tcp_listeners(PyThreadState *tstate, PyObject *kw_defaults, PyObject *annotations);


static PyObject *MAKE_FUNCTION_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__3_serve_tcp(PyThreadState *tstate, PyObject *kw_defaults, PyObject *annotations);


// The module function definitions.
static PyObject *impl_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_backlog = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    int tmp_res;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    PyObject *tmp_return_value = NULL;
    static struct Nuitka_FrameObject *cache_frame_frame_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog)) {
        Py_XDECREF(cache_frame_frame_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog = MAKE_FUNCTION_FRAME(tstate, code_objects_a5c538db960641bfcf6a0f2c68eb3d35, module_trio$_highlevel_open_tcp_listeners, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog->m_type_description == NULL);
    frame_frame_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog = cache_frame_frame_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog);
    assert(Py_REFCNT(frame_frame_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog) == 2);

    // Framed code:
    {
        bool tmp_condition_result_1;
        int tmp_and_left_truth_1;
        bool tmp_and_left_value_1;
        bool tmp_and_right_value_1;
        PyObject *tmp_operand_value_1;
        PyObject *tmp_isinstance_inst_1;
        PyObject *tmp_isinstance_cls_1;
        PyObject *tmp_cmp_expr_left_1;
        PyObject *tmp_cmp_expr_right_1;
        CHECK_OBJECT(par_backlog);
        tmp_isinstance_inst_1 = par_backlog;
        tmp_isinstance_cls_1 = (PyObject *)&PyLong_Type;
        tmp_res = PyObject_IsInstance(tmp_isinstance_inst_1, tmp_isinstance_cls_1);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 50;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_operand_value_1 = (tmp_res != 0) ? Py_True : Py_False;
        tmp_res = CHECK_IF_TRUE(tmp_operand_value_1);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 50;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_and_left_value_1 = (tmp_res == 0) ? true : false;
        tmp_and_left_truth_1 = tmp_and_left_value_1 != false ? 1 : 0;
        if (tmp_and_left_truth_1 == 1) {
            goto and_right_1;
        } else {
            goto and_left_1;
        }
        and_right_1:;
        CHECK_OBJECT(par_backlog);
        tmp_cmp_expr_left_1 = par_backlog;
        tmp_cmp_expr_right_1 = Py_None;
        tmp_and_right_value_1 = (tmp_cmp_expr_left_1 != tmp_cmp_expr_right_1) ? true : false;
        tmp_condition_result_1 = tmp_and_right_value_1;
        goto and_end_1;
        and_left_1:;
        tmp_condition_result_1 = tmp_and_left_value_1;
        and_end_1:;
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
        PyObject *tmp_string_concat_values_1;
        PyObject *tmp_tuple_element_1;
        tmp_tuple_element_1 = mod_consts[0];
        tmp_string_concat_values_1 = MAKE_TUPLE_EMPTY(tstate, 2);
        {
            PyObject *tmp_format_value_1;
            PyObject *tmp_operand_value_2;
            PyObject *tmp_format_spec_1;
            PyTuple_SET_ITEM0(tmp_string_concat_values_1, 0, tmp_tuple_element_1);
            CHECK_OBJECT(par_backlog);
            tmp_operand_value_2 = par_backlog;
            tmp_format_value_1 = UNARY_OPERATION(PyObject_Repr, tmp_operand_value_2);
            if (tmp_format_value_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 51;
                type_description_1 = "o";
                goto tuple_build_exception_1;
            }
            tmp_format_spec_1 = mod_consts[1];
            tmp_tuple_element_1 = BUILTIN_FORMAT(tstate, tmp_format_value_1, tmp_format_spec_1);
            Py_DECREF(tmp_format_value_1);
            if (tmp_tuple_element_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 51;
                type_description_1 = "o";
                goto tuple_build_exception_1;
            }
            PyTuple_SET_ITEM(tmp_string_concat_values_1, 1, tmp_tuple_element_1);
        }
        goto tuple_build_noexception_1;
        // Exception handling pass through code for tuple_build:
        tuple_build_exception_1:;
        Py_DECREF(tmp_string_concat_values_1);
        goto frame_exception_exit_1;
        // Finished with no exception for tuple_build:
        tuple_build_noexception_1:;
        tmp_make_exception_arg_1 = PyUnicode_Join(mod_consts[1], tmp_string_concat_values_1);
        Py_DECREF(tmp_string_concat_values_1);
        if (tmp_make_exception_arg_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 51;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        frame_frame_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog->m_frame.f_lineno = 51;
        tmp_raise_type_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_TypeError, tmp_make_exception_arg_1);
        Py_DECREF(tmp_make_exception_arg_1);
        assert(!(tmp_raise_type_1 == NULL));
        exception_state.exception_type = tmp_raise_type_1;
        exception_lineno = 51;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);
        type_description_1 = "o";
        goto frame_exception_exit_1;
    }
    branch_no_1:;
    {
        bool tmp_condition_result_2;
        PyObject *tmp_cmp_expr_left_2;
        PyObject *tmp_cmp_expr_right_2;
        CHECK_OBJECT(par_backlog);
        tmp_cmp_expr_left_2 = par_backlog;
        tmp_cmp_expr_right_2 = Py_None;
        tmp_condition_result_2 = (tmp_cmp_expr_left_2 == tmp_cmp_expr_right_2) ? true : false;
        if (tmp_condition_result_2 != false) {
            goto branch_yes_2;
        } else {
            goto branch_no_2;
        }
    }
    branch_yes_2:;
    tmp_return_value = mod_consts[2];
    Py_INCREF(tmp_return_value);
    goto frame_return_exit_1;
    branch_no_2:;
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_args_element_value_2;
        tmp_called_value_1 = LOOKUP_BUILTIN(mod_consts[3]);
        assert(tmp_called_value_1 != NULL);
        CHECK_OBJECT(par_backlog);
        tmp_args_element_value_1 = par_backlog;
        tmp_args_element_value_2 = mod_consts[2];
        frame_frame_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog->m_frame.f_lineno = 54;
        {
            PyObject *call_args[] = {tmp_args_element_value_1, tmp_args_element_value_2};
            tmp_return_value = CALL_FUNCTION_WITH_ARGS2(tstate, tmp_called_value_1, call_args);
        }

        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 54;
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
            exception_tb = MAKE_TRACEBACK(frame_frame_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog,
        type_description_1,
        par_backlog
    );


    // Release cached frame if used for exception.
    if (frame_frame_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog == cache_frame_frame_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog);
        cache_frame_frame_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog = NULL;
    }

    assertFrameObject(frame_frame_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_backlog);
    Py_DECREF(par_backlog);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_backlog);
    Py_DECREF(par_backlog);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__2_open_tcp_listeners(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    struct Nuitka_CellObject *par_port = Nuitka_Cell_New1(python_pars[0]);
    struct Nuitka_CellObject *par_host = Nuitka_Cell_New1(python_pars[1]);
    struct Nuitka_CellObject *par_backlog = Nuitka_Cell_New1(python_pars[2]);
    PyObject *tmp_return_value = NULL;

    // Actual function body.
    {
        struct Nuitka_CellObject *tmp_closure_1[3];

        tmp_closure_1[0] = par_backlog;
        Py_INCREF(tmp_closure_1[0]);
        tmp_closure_1[1] = par_host;
        Py_INCREF(tmp_closure_1[1]);
        tmp_closure_1[2] = par_port;
        Py_INCREF(tmp_closure_1[2]);

        tmp_return_value = MAKE_COROUTINE_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__2_open_tcp_listeners$$36$$$36$$$36$coroutine__1_open_tcp_listeners(tstate, tmp_closure_1);

        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_port);
    Py_DECREF(par_port);
    CHECK_OBJECT(par_host);
    Py_DECREF(par_host);
    CHECK_OBJECT(par_backlog);
    Py_DECREF(par_backlog);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}



#if 1
struct trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__2_open_tcp_listeners$$36$$$36$$$36$coroutine__1_open_tcp_listeners_locals {
    PyObject *var_computed_backlog;
    PyObject *var_addresses;
    PyObject *var_listeners;
    PyObject *var_unsupported_address_families;
    PyObject *var_family;
    PyObject *var_type_;
    PyObject *var_proto;
    PyObject *var__;
    PyObject *var_sockaddr;
    PyObject *var_sock;
    PyObject *var_ex;
    PyObject *var_listener;
    PyObject *tmp_for_loop_1__for_iterator;
    PyObject *tmp_for_loop_1__iter_value;
    PyObject *tmp_for_loop_2__for_iterator;
    PyObject *tmp_for_loop_2__iter_value;
    PyObject *tmp_tuple_unpack_1__element_1;
    PyObject *tmp_tuple_unpack_1__element_2;
    PyObject *tmp_tuple_unpack_1__element_3;
    PyObject *tmp_tuple_unpack_1__element_4;
    PyObject *tmp_tuple_unpack_1__element_5;
    PyObject *tmp_tuple_unpack_1__source_iter;
    char const *type_description_1;
    struct Nuitka_ExceptionPreservationItem exception_state;
    int exception_lineno;
    int tmp_res;
    char yield_tmps[1024];
    bool tmp_result;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    int exception_keeper_lineno_1;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_2;
    int exception_keeper_lineno_2;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_3;
    int exception_keeper_lineno_3;
    struct Nuitka_ExceptionStackItem exception_preserved_1;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_4;
    int exception_keeper_lineno_4;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_5;
    int exception_keeper_lineno_5;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_6;
    int exception_keeper_lineno_6;
    struct Nuitka_ExceptionStackItem exception_preserved_2;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_7;
    int exception_keeper_lineno_7;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_8;
    int exception_keeper_lineno_8;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_9;
    int exception_keeper_lineno_9;
    struct Nuitka_ExceptionStackItem exception_preserved_3;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_10;
    int exception_keeper_lineno_10;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_11;
    int exception_keeper_lineno_11;
    PyObject *tmp_return_value;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_12;
    int exception_keeper_lineno_12;
};
#endif

static PyObject *trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__2_open_tcp_listeners$$36$$$36$$$36$coroutine__1_open_tcp_listeners_context(PyThreadState *tstate, struct Nuitka_CoroutineObject *coroutine, PyObject *yield_return_value) {
    CHECK_OBJECT(coroutine);
    assert(Nuitka_Coroutine_Check((PyObject *)coroutine));
    CHECK_OBJECT_X(yield_return_value);

#if 1
    // Heap access.
    struct trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__2_open_tcp_listeners$$36$$$36$$$36$coroutine__1_open_tcp_listeners_locals *coroutine_heap = (struct trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__2_open_tcp_listeners$$36$$$36$$$36$coroutine__1_open_tcp_listeners_locals *)coroutine->m_heap_storage;
#endif

    // Dispatch to yield based on return label index:
    switch(coroutine->m_yield_return_index) {
    case 2: goto yield_return_2;
    case 1: goto yield_return_1;
    }

    // Local variable initialization
    NUITKA_MAY_BE_UNUSED nuitka_void tmp_unused;
    static struct Nuitka_FrameObject *cache_m_frame = NULL;
    coroutine_heap->var_computed_backlog = NULL;
    coroutine_heap->var_addresses = NULL;
    coroutine_heap->var_listeners = NULL;
    coroutine_heap->var_unsupported_address_families = NULL;
    coroutine_heap->var_family = NULL;
    coroutine_heap->var_type_ = NULL;
    coroutine_heap->var_proto = NULL;
    coroutine_heap->var__ = NULL;
    coroutine_heap->var_sockaddr = NULL;
    coroutine_heap->var_sock = NULL;
    coroutine_heap->var_ex = NULL;
    coroutine_heap->var_listener = NULL;
    coroutine_heap->tmp_for_loop_1__for_iterator = NULL;
    coroutine_heap->tmp_for_loop_1__iter_value = NULL;
    coroutine_heap->tmp_for_loop_2__for_iterator = NULL;
    coroutine_heap->tmp_for_loop_2__iter_value = NULL;
    coroutine_heap->tmp_tuple_unpack_1__element_1 = NULL;
    coroutine_heap->tmp_tuple_unpack_1__element_2 = NULL;
    coroutine_heap->tmp_tuple_unpack_1__element_3 = NULL;
    coroutine_heap->tmp_tuple_unpack_1__element_4 = NULL;
    coroutine_heap->tmp_tuple_unpack_1__element_5 = NULL;
    coroutine_heap->tmp_tuple_unpack_1__source_iter = NULL;
    coroutine_heap->type_description_1 = NULL;
    coroutine_heap->exception_state = Empty_Nuitka_ExceptionPreservationItem;
    coroutine_heap->exception_lineno = 0;
    coroutine_heap->tmp_return_value = NULL;

    // Actual coroutine body.
    // Tried code:
    if (isFrameUnusable(cache_m_frame)) {
        Py_XDECREF(cache_m_frame);

#if _DEBUG_REFCOUNTS
        if (cache_m_frame == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_m_frame = MAKE_FUNCTION_FRAME(tstate, code_objects_e8c68bf30da4df84e255a3b70495ca70, module_trio$_highlevel_open_tcp_listeners, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_m_frame->m_type_description == NULL);
    coroutine->m_frame = cache_m_frame;
    // Mark the frame object as in use, ref count 1 will be up for reuse.
    Py_INCREF(coroutine->m_frame);
    assert(Py_REFCNT(coroutine->m_frame) == 2); // Frame stack

    Nuitka_SetFrameGenerator(coroutine->m_frame, (PyObject *)coroutine);

    assert(coroutine->m_frame->m_frame.f_back == NULL);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackGeneratorCompiledFrame(tstate, coroutine->m_frame);
    assert(Py_REFCNT(coroutine->m_frame) == 2);

    // Store currently existing exception as the one to publish again when we
    // yield or yield from.
    STORE_COROUTINE_EXCEPTION(tstate, coroutine);

    // Framed code:
    {
        bool tmp_condition_result_1;
        PyObject *tmp_operand_value_1;
        PyObject *tmp_isinstance_inst_1;
        PyObject *tmp_isinstance_cls_1;
        if (Nuitka_Cell_GET(coroutine->m_closure[2]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[5]);
            NORMALIZE_EXCEPTION_STATE(tstate, &coroutine_heap->exception_state);
            CHAIN_EXCEPTION(tstate, coroutine_heap->exception_state.exception_value);

            coroutine_heap->exception_lineno = 109;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }

        tmp_isinstance_inst_1 = Nuitka_Cell_GET(coroutine->m_closure[2]);
        tmp_isinstance_cls_1 = (PyObject *)&PyLong_Type;
        coroutine_heap->tmp_res = PyObject_IsInstance(tmp_isinstance_inst_1, tmp_isinstance_cls_1);
        if (coroutine_heap->tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 109;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }
        tmp_operand_value_1 = (coroutine_heap->tmp_res != 0) ? Py_True : Py_False;
        coroutine_heap->tmp_res = CHECK_IF_TRUE(tmp_operand_value_1);
        if (coroutine_heap->tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 109;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_1 = (coroutine_heap->tmp_res == 0) ? true : false;
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
        PyObject *tmp_string_concat_values_1;
        PyObject *tmp_tuple_element_1;
        tmp_tuple_element_1 = mod_consts[6];
        tmp_string_concat_values_1 = MAKE_TUPLE_EMPTY(tstate, 2);
        {
            PyObject *tmp_format_value_1;
            PyObject *tmp_operand_value_2;
            PyObject *tmp_format_spec_1;
            PyTuple_SET_ITEM0(tmp_string_concat_values_1, 0, tmp_tuple_element_1);
            if (Nuitka_Cell_GET(coroutine->m_closure[2]) == NULL) {

                FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[5]);
                NORMALIZE_EXCEPTION_STATE(tstate, &coroutine_heap->exception_state);
                CHAIN_EXCEPTION(tstate, coroutine_heap->exception_state.exception_value);

                coroutine_heap->exception_lineno = 110;
                coroutine_heap->type_description_1 = "cccooooooooooooN";
                goto tuple_build_exception_1;
            }

            tmp_operand_value_2 = Nuitka_Cell_GET(coroutine->m_closure[2]);
            tmp_format_value_1 = UNARY_OPERATION(PyObject_Repr, tmp_operand_value_2);
            if (tmp_format_value_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


                coroutine_heap->exception_lineno = 110;
                coroutine_heap->type_description_1 = "cccooooooooooooN";
                goto tuple_build_exception_1;
            }
            tmp_format_spec_1 = mod_consts[1];
            tmp_tuple_element_1 = BUILTIN_FORMAT(tstate, tmp_format_value_1, tmp_format_spec_1);
            Py_DECREF(tmp_format_value_1);
            if (tmp_tuple_element_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


                coroutine_heap->exception_lineno = 110;
                coroutine_heap->type_description_1 = "cccooooooooooooN";
                goto tuple_build_exception_1;
            }
            PyTuple_SET_ITEM(tmp_string_concat_values_1, 1, tmp_tuple_element_1);
        }
        goto tuple_build_noexception_1;
        // Exception handling pass through code for tuple_build:
        tuple_build_exception_1:;
        Py_DECREF(tmp_string_concat_values_1);
        goto frame_exception_exit_1;
        // Finished with no exception for tuple_build:
        tuple_build_noexception_1:;
        tmp_make_exception_arg_1 = PyUnicode_Join(mod_consts[1], tmp_string_concat_values_1);
        Py_DECREF(tmp_string_concat_values_1);
        if (tmp_make_exception_arg_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 110;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }
        coroutine->m_frame->m_frame.f_lineno = 110;
        tmp_raise_type_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_TypeError, tmp_make_exception_arg_1);
        Py_DECREF(tmp_make_exception_arg_1);
        assert(!(tmp_raise_type_1 == NULL));
        coroutine_heap->exception_state.exception_type = tmp_raise_type_1;
        coroutine_heap->exception_lineno = 110;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &coroutine_heap->exception_state);
        coroutine_heap->type_description_1 = "cccooooooooooooN";
        goto frame_exception_exit_1;
    }
    branch_no_1:;
    {
        PyObject *tmp_assign_source_1;
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        tmp_called_value_1 = module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$_compute_backlog(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[7]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&coroutine_heap->exception_state));



            coroutine_heap->exception_lineno = 112;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }
        if (Nuitka_Cell_GET(coroutine->m_closure[0]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[8]);
            NORMALIZE_EXCEPTION_STATE(tstate, &coroutine_heap->exception_state);
            CHAIN_EXCEPTION(tstate, coroutine_heap->exception_state.exception_value);

            coroutine_heap->exception_lineno = 112;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }

        tmp_args_element_value_1 = Nuitka_Cell_GET(coroutine->m_closure[0]);
        coroutine->m_frame->m_frame.f_lineno = 112;
        tmp_assign_source_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_1, tmp_args_element_value_1);
        if (tmp_assign_source_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 112;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }
        assert(coroutine_heap->var_computed_backlog == NULL);
        coroutine_heap->var_computed_backlog = tmp_assign_source_1;
    }
    {
        PyObject *tmp_assign_source_2;
        PyObject *tmp_expression_value_1;
        PyObject *tmp_expression_value_2;
        PyObject *tmp_called_value_2;
        PyObject *tmp_expression_value_3;
        PyObject *tmp_kw_call_arg_value_0_1;
        PyObject *tmp_kw_call_arg_value_1_1;
        PyObject *tmp_kw_call_dict_value_0_1;
        PyObject *tmp_expression_value_4;
        PyObject *tmp_kw_call_dict_value_1_1;
        PyObject *tmp_expression_value_5;
        coroutine->m_frame->m_frame.f_lineno = 114;
        tmp_expression_value_3 = module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$tsocket(tstate);
        if (unlikely(tmp_expression_value_3 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[9]);
        }

        if (tmp_expression_value_3 == NULL) {
            assert(HAS_EXCEPTION_STATE(&coroutine_heap->exception_state));



            coroutine_heap->exception_lineno = 114;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }
        tmp_called_value_2 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_3, mod_consts[10]);
        if (tmp_called_value_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 114;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }
        if (Nuitka_Cell_GET(coroutine->m_closure[1]) == NULL) {
            Py_DECREF(tmp_called_value_2);
            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[11]);
            NORMALIZE_EXCEPTION_STATE(tstate, &coroutine_heap->exception_state);
            CHAIN_EXCEPTION(tstate, coroutine_heap->exception_state.exception_value);

            coroutine_heap->exception_lineno = 115;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_arg_value_0_1 = Nuitka_Cell_GET(coroutine->m_closure[1]);
        if (Nuitka_Cell_GET(coroutine->m_closure[2]) == NULL) {
            Py_DECREF(tmp_called_value_2);
            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[5]);
            NORMALIZE_EXCEPTION_STATE(tstate, &coroutine_heap->exception_state);
            CHAIN_EXCEPTION(tstate, coroutine_heap->exception_state.exception_value);

            coroutine_heap->exception_lineno = 116;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_arg_value_1_1 = Nuitka_Cell_GET(coroutine->m_closure[2]);
        tmp_expression_value_4 = module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$tsocket(tstate);
        if (unlikely(tmp_expression_value_4 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[9]);
        }

        if (tmp_expression_value_4 == NULL) {
            assert(HAS_EXCEPTION_STATE(&coroutine_heap->exception_state));

            Py_DECREF(tmp_called_value_2);

            coroutine_heap->exception_lineno = 117;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }
        tmp_kw_call_dict_value_0_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_4, mod_consts[12]);
        if (tmp_kw_call_dict_value_0_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);
            Py_DECREF(tmp_called_value_2);

            coroutine_heap->exception_lineno = 117;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }
        tmp_expression_value_5 = module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$tsocket(tstate);
        if (unlikely(tmp_expression_value_5 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[9]);
        }

        if (tmp_expression_value_5 == NULL) {
            assert(HAS_EXCEPTION_STATE(&coroutine_heap->exception_state));

            Py_DECREF(tmp_called_value_2);
            Py_DECREF(tmp_kw_call_dict_value_0_1);

            coroutine_heap->exception_lineno = 118;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }
        tmp_kw_call_dict_value_1_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_5, mod_consts[13]);
        if (tmp_kw_call_dict_value_1_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);
            Py_DECREF(tmp_called_value_2);
            Py_DECREF(tmp_kw_call_dict_value_0_1);

            coroutine_heap->exception_lineno = 118;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }
        coroutine->m_frame->m_frame.f_lineno = 114;
        {
            PyObject *args[] = {tmp_kw_call_arg_value_0_1, tmp_kw_call_arg_value_1_1};
            PyObject *kw_values[2] = {tmp_kw_call_dict_value_0_1, tmp_kw_call_dict_value_1_1};
            tmp_expression_value_2 = CALL_FUNCTION_WITH_ARGS2_KW_SPLIT(tstate, tmp_called_value_2, args, kw_values, mod_consts[14]);
        }

        Py_DECREF(tmp_called_value_2);
        Py_DECREF(tmp_kw_call_dict_value_0_1);
        Py_DECREF(tmp_kw_call_dict_value_1_1);
        if (tmp_expression_value_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 114;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }
        tmp_expression_value_1 = ASYNC_AWAIT(tstate, tmp_expression_value_2, await_normal);
        Py_DECREF(tmp_expression_value_2);
        if (tmp_expression_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 114;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }
        Nuitka_PreserveHeap(coroutine_heap->yield_tmps, &tmp_expression_value_2, sizeof(PyObject *), &tmp_called_value_2, sizeof(PyObject *), &tmp_expression_value_3, sizeof(PyObject *), &tmp_kw_call_arg_value_0_1, sizeof(PyObject *), &tmp_kw_call_arg_value_1_1, sizeof(PyObject *), &tmp_kw_call_dict_value_0_1, sizeof(PyObject *), &tmp_expression_value_4, sizeof(PyObject *), &tmp_kw_call_dict_value_1_1, sizeof(PyObject *), &tmp_expression_value_5, sizeof(PyObject *), NULL);
        coroutine->m_yield_return_index = 1;
        coroutine->m_yield_from = tmp_expression_value_1;
        coroutine->m_awaiting = true;
        return NULL;

        yield_return_1:
        Nuitka_RestoreHeap(coroutine_heap->yield_tmps, &tmp_expression_value_2, sizeof(PyObject *), &tmp_called_value_2, sizeof(PyObject *), &tmp_expression_value_3, sizeof(PyObject *), &tmp_kw_call_arg_value_0_1, sizeof(PyObject *), &tmp_kw_call_arg_value_1_1, sizeof(PyObject *), &tmp_kw_call_dict_value_0_1, sizeof(PyObject *), &tmp_expression_value_4, sizeof(PyObject *), &tmp_kw_call_dict_value_1_1, sizeof(PyObject *), &tmp_expression_value_5, sizeof(PyObject *), NULL);
        coroutine->m_awaiting = false;

        if (yield_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 114;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }
        tmp_assign_source_2 = yield_return_value;
        assert(coroutine_heap->var_addresses == NULL);
        coroutine_heap->var_addresses = tmp_assign_source_2;
    }
    {
        PyObject *tmp_assign_source_3;
        tmp_assign_source_3 = MAKE_LIST_EMPTY(tstate, 0);
        assert(coroutine_heap->var_listeners == NULL);
        coroutine_heap->var_listeners = tmp_assign_source_3;
    }
    {
        PyObject *tmp_assign_source_4;
        tmp_assign_source_4 = MAKE_LIST_EMPTY(tstate, 0);
        assert(coroutine_heap->var_unsupported_address_families == NULL);
        coroutine_heap->var_unsupported_address_families = tmp_assign_source_4;
    }
    // Tried code:
    {
        PyObject *tmp_assign_source_5;
        PyObject *tmp_iter_arg_1;
        CHECK_OBJECT(coroutine_heap->var_addresses);
        tmp_iter_arg_1 = coroutine_heap->var_addresses;
        tmp_assign_source_5 = MAKE_ITERATOR(tstate, tmp_iter_arg_1);
        if (tmp_assign_source_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 124;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_2;
        }
        assert(coroutine_heap->tmp_for_loop_1__for_iterator == NULL);
        coroutine_heap->tmp_for_loop_1__for_iterator = tmp_assign_source_5;
    }
    // Tried code:
    loop_start_1:;
    {
        PyObject *tmp_next_source_1;
        PyObject *tmp_assign_source_6;
        CHECK_OBJECT(coroutine_heap->tmp_for_loop_1__for_iterator);
        tmp_next_source_1 = coroutine_heap->tmp_for_loop_1__for_iterator;
        tmp_assign_source_6 = ITERATOR_NEXT(tmp_next_source_1);
        if (tmp_assign_source_6 == NULL) {
            if (CHECK_AND_CLEAR_STOP_ITERATION_OCCURRED(tstate)) {

                goto loop_end_1;
            } else {

                FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);
                coroutine_heap->type_description_1 = "cccooooooooooooN";
                coroutine_heap->exception_lineno = 124;
                goto try_except_handler_3;
            }
        }

        {
            PyObject *old = coroutine_heap->tmp_for_loop_1__iter_value;
            coroutine_heap->tmp_for_loop_1__iter_value = tmp_assign_source_6;
            Py_XDECREF(old);
        }

    }
    // Tried code:
    {
        PyObject *tmp_assign_source_7;
        PyObject *tmp_iter_arg_2;
        CHECK_OBJECT(coroutine_heap->tmp_for_loop_1__iter_value);
        tmp_iter_arg_2 = coroutine_heap->tmp_for_loop_1__iter_value;
        tmp_assign_source_7 = MAKE_UNPACK_ITERATOR(tmp_iter_arg_2);
        if (tmp_assign_source_7 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 124;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_4;
        }
        {
            PyObject *old = coroutine_heap->tmp_tuple_unpack_1__source_iter;
            coroutine_heap->tmp_tuple_unpack_1__source_iter = tmp_assign_source_7;
            Py_XDECREF(old);
        }

    }
    // Tried code:
    {
        PyObject *tmp_assign_source_8;
        PyObject *tmp_unpack_1;
        CHECK_OBJECT(coroutine_heap->tmp_tuple_unpack_1__source_iter);
        tmp_unpack_1 = coroutine_heap->tmp_tuple_unpack_1__source_iter;
        tmp_assign_source_8 = UNPACK_NEXT(tstate, &coroutine_heap->exception_state, tmp_unpack_1, 0, 5);
        if (tmp_assign_source_8 == NULL) {
            assert(HAS_EXCEPTION_STATE(&coroutine_heap->exception_state));



            coroutine_heap->exception_lineno = 124;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_5;
        }
        {
            PyObject *old = coroutine_heap->tmp_tuple_unpack_1__element_1;
            coroutine_heap->tmp_tuple_unpack_1__element_1 = tmp_assign_source_8;
            Py_XDECREF(old);
        }

    }
    {
        PyObject *tmp_assign_source_9;
        PyObject *tmp_unpack_2;
        CHECK_OBJECT(coroutine_heap->tmp_tuple_unpack_1__source_iter);
        tmp_unpack_2 = coroutine_heap->tmp_tuple_unpack_1__source_iter;
        tmp_assign_source_9 = UNPACK_NEXT(tstate, &coroutine_heap->exception_state, tmp_unpack_2, 1, 5);
        if (tmp_assign_source_9 == NULL) {
            assert(HAS_EXCEPTION_STATE(&coroutine_heap->exception_state));



            coroutine_heap->exception_lineno = 124;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_5;
        }
        {
            PyObject *old = coroutine_heap->tmp_tuple_unpack_1__element_2;
            coroutine_heap->tmp_tuple_unpack_1__element_2 = tmp_assign_source_9;
            Py_XDECREF(old);
        }

    }
    {
        PyObject *tmp_assign_source_10;
        PyObject *tmp_unpack_3;
        CHECK_OBJECT(coroutine_heap->tmp_tuple_unpack_1__source_iter);
        tmp_unpack_3 = coroutine_heap->tmp_tuple_unpack_1__source_iter;
        tmp_assign_source_10 = UNPACK_NEXT(tstate, &coroutine_heap->exception_state, tmp_unpack_3, 2, 5);
        if (tmp_assign_source_10 == NULL) {
            assert(HAS_EXCEPTION_STATE(&coroutine_heap->exception_state));



            coroutine_heap->exception_lineno = 124;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_5;
        }
        {
            PyObject *old = coroutine_heap->tmp_tuple_unpack_1__element_3;
            coroutine_heap->tmp_tuple_unpack_1__element_3 = tmp_assign_source_10;
            Py_XDECREF(old);
        }

    }
    {
        PyObject *tmp_assign_source_11;
        PyObject *tmp_unpack_4;
        CHECK_OBJECT(coroutine_heap->tmp_tuple_unpack_1__source_iter);
        tmp_unpack_4 = coroutine_heap->tmp_tuple_unpack_1__source_iter;
        tmp_assign_source_11 = UNPACK_NEXT(tstate, &coroutine_heap->exception_state, tmp_unpack_4, 3, 5);
        if (tmp_assign_source_11 == NULL) {
            assert(HAS_EXCEPTION_STATE(&coroutine_heap->exception_state));



            coroutine_heap->exception_lineno = 124;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_5;
        }
        {
            PyObject *old = coroutine_heap->tmp_tuple_unpack_1__element_4;
            coroutine_heap->tmp_tuple_unpack_1__element_4 = tmp_assign_source_11;
            Py_XDECREF(old);
        }

    }
    {
        PyObject *tmp_assign_source_12;
        PyObject *tmp_unpack_5;
        CHECK_OBJECT(coroutine_heap->tmp_tuple_unpack_1__source_iter);
        tmp_unpack_5 = coroutine_heap->tmp_tuple_unpack_1__source_iter;
        tmp_assign_source_12 = UNPACK_NEXT(tstate, &coroutine_heap->exception_state, tmp_unpack_5, 4, 5);
        if (tmp_assign_source_12 == NULL) {
            assert(HAS_EXCEPTION_STATE(&coroutine_heap->exception_state));



            coroutine_heap->exception_lineno = 124;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_5;
        }
        {
            PyObject *old = coroutine_heap->tmp_tuple_unpack_1__element_5;
            coroutine_heap->tmp_tuple_unpack_1__element_5 = tmp_assign_source_12;
            Py_XDECREF(old);
        }

    }
    {
        PyObject *tmp_iterator_name_1;
        CHECK_OBJECT(coroutine_heap->tmp_tuple_unpack_1__source_iter);
        tmp_iterator_name_1 = coroutine_heap->tmp_tuple_unpack_1__source_iter;
        coroutine_heap->tmp_result = UNPACK_ITERATOR_CHECK(tstate, &coroutine_heap->exception_state, tmp_iterator_name_1, 5);
        if (coroutine_heap->tmp_result == false) {
            assert(HAS_EXCEPTION_STATE(&coroutine_heap->exception_state));



            coroutine_heap->exception_lineno = 124;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_5;
        }
    }
    goto try_end_1;
    // Exception handler code:
    try_except_handler_5:;
    coroutine_heap->exception_keeper_lineno_1 = coroutine_heap->exception_lineno;
    coroutine_heap->exception_lineno = 0;
    coroutine_heap->exception_keeper_name_1 = coroutine_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&coroutine_heap->exception_state);

    CHECK_OBJECT(coroutine_heap->tmp_tuple_unpack_1__source_iter);
    Py_DECREF(coroutine_heap->tmp_tuple_unpack_1__source_iter);
    coroutine_heap->tmp_tuple_unpack_1__source_iter = NULL;
    // Re-raise.
    coroutine_heap->exception_state = coroutine_heap->exception_keeper_name_1;
    coroutine_heap->exception_lineno = coroutine_heap->exception_keeper_lineno_1;

    goto try_except_handler_4;
    // End of try:
    try_end_1:;
    goto try_end_2;
    // Exception handler code:
    try_except_handler_4:;
    coroutine_heap->exception_keeper_lineno_2 = coroutine_heap->exception_lineno;
    coroutine_heap->exception_lineno = 0;
    coroutine_heap->exception_keeper_name_2 = coroutine_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&coroutine_heap->exception_state);

    Py_XDECREF(coroutine_heap->tmp_tuple_unpack_1__element_1);
    coroutine_heap->tmp_tuple_unpack_1__element_1 = NULL;
    Py_XDECREF(coroutine_heap->tmp_tuple_unpack_1__element_2);
    coroutine_heap->tmp_tuple_unpack_1__element_2 = NULL;
    Py_XDECREF(coroutine_heap->tmp_tuple_unpack_1__element_3);
    coroutine_heap->tmp_tuple_unpack_1__element_3 = NULL;
    Py_XDECREF(coroutine_heap->tmp_tuple_unpack_1__element_4);
    coroutine_heap->tmp_tuple_unpack_1__element_4 = NULL;
    Py_XDECREF(coroutine_heap->tmp_tuple_unpack_1__element_5);
    coroutine_heap->tmp_tuple_unpack_1__element_5 = NULL;
    // Re-raise.
    coroutine_heap->exception_state = coroutine_heap->exception_keeper_name_2;
    coroutine_heap->exception_lineno = coroutine_heap->exception_keeper_lineno_2;

    goto try_except_handler_3;
    // End of try:
    try_end_2:;
    CHECK_OBJECT(coroutine_heap->tmp_tuple_unpack_1__source_iter);
    Py_DECREF(coroutine_heap->tmp_tuple_unpack_1__source_iter);
    coroutine_heap->tmp_tuple_unpack_1__source_iter = NULL;
    {
        PyObject *tmp_assign_source_13;
        CHECK_OBJECT(coroutine_heap->tmp_tuple_unpack_1__element_1);
        tmp_assign_source_13 = coroutine_heap->tmp_tuple_unpack_1__element_1;
        {
            PyObject *old = coroutine_heap->var_family;
            coroutine_heap->var_family = tmp_assign_source_13;
            Py_INCREF(coroutine_heap->var_family);
            Py_XDECREF(old);
        }

    }
    Py_XDECREF(coroutine_heap->tmp_tuple_unpack_1__element_1);
    coroutine_heap->tmp_tuple_unpack_1__element_1 = NULL;

    {
        PyObject *tmp_assign_source_14;
        CHECK_OBJECT(coroutine_heap->tmp_tuple_unpack_1__element_2);
        tmp_assign_source_14 = coroutine_heap->tmp_tuple_unpack_1__element_2;
        {
            PyObject *old = coroutine_heap->var_type_;
            coroutine_heap->var_type_ = tmp_assign_source_14;
            Py_INCREF(coroutine_heap->var_type_);
            Py_XDECREF(old);
        }

    }
    Py_XDECREF(coroutine_heap->tmp_tuple_unpack_1__element_2);
    coroutine_heap->tmp_tuple_unpack_1__element_2 = NULL;

    {
        PyObject *tmp_assign_source_15;
        CHECK_OBJECT(coroutine_heap->tmp_tuple_unpack_1__element_3);
        tmp_assign_source_15 = coroutine_heap->tmp_tuple_unpack_1__element_3;
        {
            PyObject *old = coroutine_heap->var_proto;
            coroutine_heap->var_proto = tmp_assign_source_15;
            Py_INCREF(coroutine_heap->var_proto);
            Py_XDECREF(old);
        }

    }
    Py_XDECREF(coroutine_heap->tmp_tuple_unpack_1__element_3);
    coroutine_heap->tmp_tuple_unpack_1__element_3 = NULL;

    {
        PyObject *tmp_assign_source_16;
        CHECK_OBJECT(coroutine_heap->tmp_tuple_unpack_1__element_4);
        tmp_assign_source_16 = coroutine_heap->tmp_tuple_unpack_1__element_4;
        {
            PyObject *old = coroutine_heap->var__;
            coroutine_heap->var__ = tmp_assign_source_16;
            Py_INCREF(coroutine_heap->var__);
            Py_XDECREF(old);
        }

    }
    Py_XDECREF(coroutine_heap->tmp_tuple_unpack_1__element_4);
    coroutine_heap->tmp_tuple_unpack_1__element_4 = NULL;

    {
        PyObject *tmp_assign_source_17;
        CHECK_OBJECT(coroutine_heap->tmp_tuple_unpack_1__element_5);
        tmp_assign_source_17 = coroutine_heap->tmp_tuple_unpack_1__element_5;
        {
            PyObject *old = coroutine_heap->var_sockaddr;
            coroutine_heap->var_sockaddr = tmp_assign_source_17;
            Py_INCREF(coroutine_heap->var_sockaddr);
            Py_XDECREF(old);
        }

    }
    Py_XDECREF(coroutine_heap->tmp_tuple_unpack_1__element_5);
    coroutine_heap->tmp_tuple_unpack_1__element_5 = NULL;

    // Tried code:
    {
        PyObject *tmp_assign_source_18;
        PyObject *tmp_called_instance_1;
        PyObject *tmp_args_element_value_2;
        PyObject *tmp_args_element_value_3;
        PyObject *tmp_args_element_value_4;
        tmp_called_instance_1 = module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$tsocket(tstate);
        if (unlikely(tmp_called_instance_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[9]);
        }

        if (tmp_called_instance_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&coroutine_heap->exception_state));



            coroutine_heap->exception_lineno = 126;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_6;
        }
        CHECK_OBJECT(coroutine_heap->var_family);
        tmp_args_element_value_2 = coroutine_heap->var_family;
        CHECK_OBJECT(coroutine_heap->var_type_);
        tmp_args_element_value_3 = coroutine_heap->var_type_;
        CHECK_OBJECT(coroutine_heap->var_proto);
        tmp_args_element_value_4 = coroutine_heap->var_proto;
        coroutine->m_frame->m_frame.f_lineno = 126;
        {
            PyObject *call_args[] = {tmp_args_element_value_2, tmp_args_element_value_3, tmp_args_element_value_4};
            tmp_assign_source_18 = CALL_METHOD_WITH_ARGS3(
                tstate,
                tmp_called_instance_1,
                mod_consts[15],
                call_args
            );
        }

        if (tmp_assign_source_18 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 126;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_6;
        }
        {
            PyObject *old = coroutine_heap->var_sock;
            coroutine_heap->var_sock = tmp_assign_source_18;
            Py_XDECREF(old);
        }

    }
    goto try_end_3;
    // Exception handler code:
    try_except_handler_6:;
    coroutine_heap->exception_keeper_lineno_3 = coroutine_heap->exception_lineno;
    coroutine_heap->exception_lineno = 0;
    coroutine_heap->exception_keeper_name_3 = coroutine_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&coroutine_heap->exception_state);

    // Preserve existing published exception id 1.
    coroutine_heap->exception_preserved_1 = GET_CURRENT_EXCEPTION(tstate);

    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&coroutine_heap->exception_keeper_name_3);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(coroutine->m_frame, coroutine_heap->exception_keeper_lineno_3);
            SET_EXCEPTION_STATE_TRACEBACK(&coroutine_heap->exception_keeper_name_3, exception_tb);
        } else if (coroutine_heap->exception_keeper_lineno_3 != 0) {
            exception_tb = ADD_TRACEBACK(exception_tb, coroutine->m_frame, coroutine_heap->exception_keeper_lineno_3);
            SET_EXCEPTION_STATE_TRACEBACK(&coroutine_heap->exception_keeper_name_3, exception_tb);
        }
    }

    PUBLISH_CURRENT_EXCEPTION(tstate, &coroutine_heap->exception_keeper_name_3);
    // Tried code:
    {
        bool tmp_condition_result_2;
        PyObject *tmp_cmp_expr_left_1;
        PyObject *tmp_cmp_expr_right_1;
        tmp_cmp_expr_left_1 = EXC_TYPE(tstate);
        tmp_cmp_expr_right_1 = PyExc_OSError;
        coroutine_heap->tmp_res = EXCEPTION_MATCH_BOOL(tstate, tmp_cmp_expr_left_1, tmp_cmp_expr_right_1);
        assert(!(coroutine_heap->tmp_res == -1));
        tmp_condition_result_2 = (coroutine_heap->tmp_res != 0) ? true : false;
        if (tmp_condition_result_2 != false) {
            goto branch_yes_2;
        } else {
            goto branch_no_2;
        }
    }
    branch_yes_2:;
    {
        PyObject *tmp_assign_source_19;
        tmp_assign_source_19 = EXC_VALUE(tstate);
        CHECK_OBJECT(tmp_assign_source_19); 
        {
            PyObject *old = coroutine_heap->var_ex;
            coroutine_heap->var_ex = tmp_assign_source_19;
            Py_INCREF(coroutine_heap->var_ex);
            Py_XDECREF(old);
        }

    }
    // Tried code:
    {
        nuitka_bool tmp_condition_result_3;
        PyObject *tmp_cmp_expr_left_2;
        PyObject *tmp_cmp_expr_right_2;
        PyObject *tmp_expression_value_6;
        PyObject *tmp_expression_value_7;
        CHECK_OBJECT(coroutine_heap->var_ex);
        tmp_expression_value_6 = coroutine_heap->var_ex;
        tmp_cmp_expr_left_2 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_6, mod_consts[16]);
        if (tmp_cmp_expr_left_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 128;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_8;
        }
        tmp_expression_value_7 = module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$errno(tstate);
        if (unlikely(tmp_expression_value_7 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[16]);
        }

        if (tmp_expression_value_7 == NULL) {
            assert(HAS_EXCEPTION_STATE(&coroutine_heap->exception_state));

            Py_DECREF(tmp_cmp_expr_left_2);

            coroutine_heap->exception_lineno = 128;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_8;
        }
        tmp_cmp_expr_right_2 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_7, mod_consts[17]);
        if (tmp_cmp_expr_right_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);
            Py_DECREF(tmp_cmp_expr_left_2);

            coroutine_heap->exception_lineno = 128;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_8;
        }
        tmp_condition_result_3 = RICH_COMPARE_EQ_NBOOL_OBJECT_OBJECT(tmp_cmp_expr_left_2, tmp_cmp_expr_right_2);
        Py_DECREF(tmp_cmp_expr_left_2);
        Py_DECREF(tmp_cmp_expr_right_2);
        if (tmp_condition_result_3 == NUITKA_BOOL_EXCEPTION) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 128;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_8;
        }
        if (tmp_condition_result_3 == NUITKA_BOOL_TRUE) {
            goto branch_yes_3;
        } else {
            goto branch_no_3;
        }
    }
    branch_yes_3:;
    {
        PyObject *tmp_list_arg_value_1;
        PyObject *tmp_item_value_1;
        if (coroutine_heap->var_unsupported_address_families == NULL) {

            FORMAT_UNBOUND_LOCAL_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[18]);
            NORMALIZE_EXCEPTION_STATE(tstate, &coroutine_heap->exception_state);
            CHAIN_EXCEPTION(tstate, coroutine_heap->exception_state.exception_value);

            coroutine_heap->exception_lineno = 135;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_8;
        }

        tmp_list_arg_value_1 = coroutine_heap->var_unsupported_address_families;
        CHECK_OBJECT(coroutine_heap->var_ex);
        tmp_item_value_1 = coroutine_heap->var_ex;
        coroutine_heap->tmp_result = LIST_APPEND0(tmp_list_arg_value_1, tmp_item_value_1);
        assert(!(coroutine_heap->tmp_result == false));
    }
    goto try_continue_handler_8;
    goto branch_end_3;
    branch_no_3:;
    coroutine_heap->tmp_result = RERAISE_EXCEPTION(tstate, &coroutine_heap->exception_state);
    if (unlikely(coroutine_heap->tmp_result == false)) {
        coroutine_heap->exception_lineno = 138;
    }

    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&coroutine_heap->exception_state);

        if ((exception_tb != NULL) && (exception_tb->tb_frame == &coroutine->m_frame->m_frame)) {
            coroutine->m_frame->m_frame.f_lineno = exception_tb->tb_lineno;
        }
    }
    coroutine_heap->type_description_1 = "cccooooooooooooN";
    goto try_except_handler_8;
    branch_end_3:;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Exception handler code:
    try_except_handler_8:;
    coroutine_heap->exception_keeper_lineno_4 = coroutine_heap->exception_lineno;
    coroutine_heap->exception_lineno = 0;
    coroutine_heap->exception_keeper_name_4 = coroutine_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&coroutine_heap->exception_state);

    Py_XDECREF(coroutine_heap->var_ex);
    coroutine_heap->var_ex = NULL;

    // Re-raise.
    coroutine_heap->exception_state = coroutine_heap->exception_keeper_name_4;
    coroutine_heap->exception_lineno = coroutine_heap->exception_keeper_lineno_4;

    goto try_except_handler_7;
    // try continue handler code:
    try_continue_handler_8:;
    Py_XDECREF(coroutine_heap->var_ex);
    coroutine_heap->var_ex = NULL;

    goto try_continue_handler_7;
    // End of try:
    goto branch_end_2;
    branch_no_2:;
    coroutine_heap->tmp_result = RERAISE_EXCEPTION(tstate, &coroutine_heap->exception_state);
    if (unlikely(coroutine_heap->tmp_result == false)) {
        coroutine_heap->exception_lineno = 125;
    }

    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&coroutine_heap->exception_state);

        if ((exception_tb != NULL) && (exception_tb->tb_frame == &coroutine->m_frame->m_frame)) {
            coroutine->m_frame->m_frame.f_lineno = exception_tb->tb_lineno;
        }
    }
    coroutine_heap->type_description_1 = "cccooooooooooooN";
    goto try_except_handler_7;
    branch_end_2:;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Exception handler code:
    try_except_handler_7:;
    coroutine_heap->exception_keeper_lineno_5 = coroutine_heap->exception_lineno;
    coroutine_heap->exception_lineno = 0;
    coroutine_heap->exception_keeper_name_5 = coroutine_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&coroutine_heap->exception_state);

    // Restore previous exception id 1.
    SET_CURRENT_EXCEPTION(tstate, &coroutine_heap->exception_preserved_1);

    // Re-raise.
    coroutine_heap->exception_state = coroutine_heap->exception_keeper_name_5;
    coroutine_heap->exception_lineno = coroutine_heap->exception_keeper_lineno_5;

    goto try_except_handler_3;
    // try continue handler code:
    try_continue_handler_7:;
    // Restore previous exception id 1.
    SET_CURRENT_EXCEPTION(tstate, &coroutine_heap->exception_preserved_1);

    goto loop_start_1;
    // End of try:
    // End of try:
    try_end_3:;
    // Tried code:
    {
        nuitka_bool tmp_condition_result_4;
        PyObject *tmp_cmp_expr_left_3;
        PyObject *tmp_cmp_expr_right_3;
        PyObject *tmp_expression_value_8;
        CHECK_OBJECT(coroutine_heap->var_family);
        tmp_cmp_expr_left_3 = coroutine_heap->var_family;
        tmp_expression_value_8 = module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$tsocket(tstate);
        if (unlikely(tmp_expression_value_8 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[9]);
        }

        if (tmp_expression_value_8 == NULL) {
            assert(HAS_EXCEPTION_STATE(&coroutine_heap->exception_state));



            coroutine_heap->exception_lineno = 144;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_9;
        }
        tmp_cmp_expr_right_3 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_8, mod_consts[19]);
        if (tmp_cmp_expr_right_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 144;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_9;
        }
        tmp_condition_result_4 = RICH_COMPARE_EQ_NBOOL_OBJECT_OBJECT(tmp_cmp_expr_left_3, tmp_cmp_expr_right_3);
        Py_DECREF(tmp_cmp_expr_right_3);
        if (tmp_condition_result_4 == NUITKA_BOOL_EXCEPTION) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 144;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_9;
        }
        if (tmp_condition_result_4 == NUITKA_BOOL_TRUE) {
            goto branch_yes_4;
        } else {
            goto branch_no_4;
        }
    }
    branch_yes_4:;
    {
        PyObject *tmp_called_value_3;
        PyObject *tmp_expression_value_9;
        PyObject *tmp_call_result_1;
        PyObject *tmp_args_element_value_5;
        PyObject *tmp_expression_value_10;
        PyObject *tmp_args_element_value_6;
        PyObject *tmp_expression_value_11;
        PyObject *tmp_args_element_value_7;
        CHECK_OBJECT(coroutine_heap->var_sock);
        tmp_expression_value_9 = coroutine_heap->var_sock;
        tmp_called_value_3 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_9, mod_consts[20]);
        if (tmp_called_value_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 145;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_9;
        }
        tmp_expression_value_10 = module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$tsocket(tstate);
        if (unlikely(tmp_expression_value_10 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[9]);
        }

        if (tmp_expression_value_10 == NULL) {
            assert(HAS_EXCEPTION_STATE(&coroutine_heap->exception_state));

            Py_DECREF(tmp_called_value_3);

            coroutine_heap->exception_lineno = 145;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_9;
        }
        tmp_args_element_value_5 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_10, mod_consts[21]);
        if (tmp_args_element_value_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);
            Py_DECREF(tmp_called_value_3);

            coroutine_heap->exception_lineno = 145;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_9;
        }
        tmp_expression_value_11 = module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$tsocket(tstate);
        if (unlikely(tmp_expression_value_11 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[9]);
        }

        if (tmp_expression_value_11 == NULL) {
            assert(HAS_EXCEPTION_STATE(&coroutine_heap->exception_state));

            Py_DECREF(tmp_called_value_3);
            Py_DECREF(tmp_args_element_value_5);

            coroutine_heap->exception_lineno = 145;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_9;
        }
        tmp_args_element_value_6 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_11, mod_consts[22]);
        if (tmp_args_element_value_6 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);
            Py_DECREF(tmp_called_value_3);
            Py_DECREF(tmp_args_element_value_5);

            coroutine_heap->exception_lineno = 145;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_9;
        }
        tmp_args_element_value_7 = const_int_pos_1;
        coroutine->m_frame->m_frame.f_lineno = 145;
        {
            PyObject *call_args[] = {tmp_args_element_value_5, tmp_args_element_value_6, tmp_args_element_value_7};
            tmp_call_result_1 = CALL_FUNCTION_WITH_ARGS3(tstate, tmp_called_value_3, call_args);
        }

        Py_DECREF(tmp_called_value_3);
        Py_DECREF(tmp_args_element_value_5);
        Py_DECREF(tmp_args_element_value_6);
        if (tmp_call_result_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 145;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_9;
        }
        Py_DECREF(tmp_call_result_1);
    }
    branch_no_4:;
    {
        PyObject *tmp_expression_value_12;
        PyObject *tmp_expression_value_13;
        PyObject *tmp_called_instance_2;
        PyObject *tmp_args_element_value_8;
        PyObject *tmp_await_result_1;
        coroutine->m_frame->m_frame.f_lineno = 147;
        CHECK_OBJECT(coroutine_heap->var_sock);
        tmp_called_instance_2 = coroutine_heap->var_sock;
        CHECK_OBJECT(coroutine_heap->var_sockaddr);
        tmp_args_element_value_8 = coroutine_heap->var_sockaddr;
        coroutine->m_frame->m_frame.f_lineno = 147;
        tmp_expression_value_13 = CALL_METHOD_WITH_SINGLE_ARG(tstate, tmp_called_instance_2, mod_consts[23], tmp_args_element_value_8);
        if (tmp_expression_value_13 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 147;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_9;
        }
        tmp_expression_value_12 = ASYNC_AWAIT(tstate, tmp_expression_value_13, await_normal);
        Py_DECREF(tmp_expression_value_13);
        if (tmp_expression_value_12 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 147;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_9;
        }
        Nuitka_PreserveHeap(coroutine_heap->yield_tmps, &tmp_expression_value_13, sizeof(PyObject *), &tmp_called_instance_2, sizeof(PyObject *), &tmp_args_element_value_8, sizeof(PyObject *), NULL);
        coroutine->m_yield_return_index = 2;
        coroutine->m_yield_from = tmp_expression_value_12;
        coroutine->m_awaiting = true;
        return NULL;

        yield_return_2:
        Nuitka_RestoreHeap(coroutine_heap->yield_tmps, &tmp_expression_value_13, sizeof(PyObject *), &tmp_called_instance_2, sizeof(PyObject *), &tmp_args_element_value_8, sizeof(PyObject *), NULL);
        coroutine->m_awaiting = false;

        if (yield_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 147;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_9;
        }
        tmp_await_result_1 = yield_return_value;
        Py_DECREF(tmp_await_result_1);
    }
    {
        PyObject *tmp_called_value_4;
        PyObject *tmp_expression_value_14;
        PyObject *tmp_call_result_2;
        PyObject *tmp_args_element_value_9;
        CHECK_OBJECT(coroutine_heap->var_sock);
        tmp_expression_value_14 = coroutine_heap->var_sock;
        tmp_called_value_4 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_14, mod_consts[24]);
        if (tmp_called_value_4 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 148;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_9;
        }
        if (coroutine_heap->var_computed_backlog == NULL) {
            Py_DECREF(tmp_called_value_4);
            FORMAT_UNBOUND_LOCAL_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[25]);
            NORMALIZE_EXCEPTION_STATE(tstate, &coroutine_heap->exception_state);
            CHAIN_EXCEPTION(tstate, coroutine_heap->exception_state.exception_value);

            coroutine_heap->exception_lineno = 148;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_9;
        }

        tmp_args_element_value_9 = coroutine_heap->var_computed_backlog;
        coroutine->m_frame->m_frame.f_lineno = 148;
        tmp_call_result_2 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_4, tmp_args_element_value_9);
        Py_DECREF(tmp_called_value_4);
        if (tmp_call_result_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 148;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_9;
        }
        Py_DECREF(tmp_call_result_2);
    }
    {
        PyObject *tmp_list_arg_value_2;
        PyObject *tmp_item_value_2;
        PyObject *tmp_called_instance_3;
        PyObject *tmp_args_element_value_10;
        if (coroutine_heap->var_listeners == NULL) {

            FORMAT_UNBOUND_LOCAL_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[26]);
            NORMALIZE_EXCEPTION_STATE(tstate, &coroutine_heap->exception_state);
            CHAIN_EXCEPTION(tstate, coroutine_heap->exception_state.exception_value);

            coroutine_heap->exception_lineno = 150;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_9;
        }

        tmp_list_arg_value_2 = coroutine_heap->var_listeners;
        tmp_called_instance_3 = module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$trio(tstate);
        if (unlikely(tmp_called_instance_3 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[27]);
        }

        if (tmp_called_instance_3 == NULL) {
            assert(HAS_EXCEPTION_STATE(&coroutine_heap->exception_state));



            coroutine_heap->exception_lineno = 150;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_9;
        }
        CHECK_OBJECT(coroutine_heap->var_sock);
        tmp_args_element_value_10 = coroutine_heap->var_sock;
        coroutine->m_frame->m_frame.f_lineno = 150;
        tmp_item_value_2 = CALL_METHOD_WITH_SINGLE_ARG(tstate, tmp_called_instance_3, mod_consts[28], tmp_args_element_value_10);
        if (tmp_item_value_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 150;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_9;
        }
        coroutine_heap->tmp_result = LIST_APPEND1(tmp_list_arg_value_2, tmp_item_value_2);
        assert(!(coroutine_heap->tmp_result == false));
    }
    goto try_end_4;
    // Exception handler code:
    try_except_handler_9:;
    coroutine_heap->exception_keeper_lineno_6 = coroutine_heap->exception_lineno;
    coroutine_heap->exception_lineno = 0;
    coroutine_heap->exception_keeper_name_6 = coroutine_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&coroutine_heap->exception_state);

    // Preserve existing published exception id 2.
    coroutine_heap->exception_preserved_2 = GET_CURRENT_EXCEPTION(tstate);

    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&coroutine_heap->exception_keeper_name_6);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(coroutine->m_frame, coroutine_heap->exception_keeper_lineno_6);
            SET_EXCEPTION_STATE_TRACEBACK(&coroutine_heap->exception_keeper_name_6, exception_tb);
        } else if (coroutine_heap->exception_keeper_lineno_6 != 0) {
            exception_tb = ADD_TRACEBACK(exception_tb, coroutine->m_frame, coroutine_heap->exception_keeper_lineno_6);
            SET_EXCEPTION_STATE_TRACEBACK(&coroutine_heap->exception_keeper_name_6, exception_tb);
        }
    }

    PUBLISH_CURRENT_EXCEPTION(tstate, &coroutine_heap->exception_keeper_name_6);
    // Tried code:
    {
        PyObject *tmp_called_instance_4;
        PyObject *tmp_call_result_3;
        CHECK_OBJECT(coroutine_heap->var_sock);
        tmp_called_instance_4 = coroutine_heap->var_sock;
        coroutine->m_frame->m_frame.f_lineno = 152;
        tmp_call_result_3 = CALL_METHOD_NO_ARGS(tstate, tmp_called_instance_4, mod_consts[29]);
        if (tmp_call_result_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 152;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_10;
        }
        Py_DECREF(tmp_call_result_3);
    }
    coroutine_heap->tmp_result = RERAISE_EXCEPTION(tstate, &coroutine_heap->exception_state);
    if (unlikely(coroutine_heap->tmp_result == false)) {
        coroutine_heap->exception_lineno = 153;
    }

    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&coroutine_heap->exception_state);

        if ((exception_tb != NULL) && (exception_tb->tb_frame == &coroutine->m_frame->m_frame)) {
            coroutine->m_frame->m_frame.f_lineno = exception_tb->tb_lineno;
        }
    }
    coroutine_heap->type_description_1 = "cccooooooooooooN";
    goto try_except_handler_10;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Exception handler code:
    try_except_handler_10:;
    coroutine_heap->exception_keeper_lineno_7 = coroutine_heap->exception_lineno;
    coroutine_heap->exception_lineno = 0;
    coroutine_heap->exception_keeper_name_7 = coroutine_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&coroutine_heap->exception_state);

    // Restore previous exception id 2.
    SET_CURRENT_EXCEPTION(tstate, &coroutine_heap->exception_preserved_2);

    // Re-raise.
    coroutine_heap->exception_state = coroutine_heap->exception_keeper_name_7;
    coroutine_heap->exception_lineno = coroutine_heap->exception_keeper_lineno_7;

    goto try_except_handler_3;
    // End of try:
    // End of try:
    try_end_4:;
    if (CONSIDER_THREADING(tstate) == false) {
        assert(HAS_ERROR_OCCURRED(tstate));

        FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


        coroutine_heap->exception_lineno = 124;
        coroutine_heap->type_description_1 = "cccooooooooooooN";
        goto try_except_handler_3;
    }
    goto loop_start_1;
    loop_end_1:;
    goto try_end_5;
    // Exception handler code:
    try_except_handler_3:;
    coroutine_heap->exception_keeper_lineno_8 = coroutine_heap->exception_lineno;
    coroutine_heap->exception_lineno = 0;
    coroutine_heap->exception_keeper_name_8 = coroutine_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&coroutine_heap->exception_state);

    Py_XDECREF(coroutine_heap->tmp_for_loop_1__iter_value);
    coroutine_heap->tmp_for_loop_1__iter_value = NULL;
    CHECK_OBJECT(coroutine_heap->tmp_for_loop_1__for_iterator);
    Py_DECREF(coroutine_heap->tmp_for_loop_1__for_iterator);
    coroutine_heap->tmp_for_loop_1__for_iterator = NULL;
    // Re-raise.
    coroutine_heap->exception_state = coroutine_heap->exception_keeper_name_8;
    coroutine_heap->exception_lineno = coroutine_heap->exception_keeper_lineno_8;

    goto try_except_handler_2;
    // End of try:
    try_end_5:;
    goto try_end_6;
    // Exception handler code:
    try_except_handler_2:;
    coroutine_heap->exception_keeper_lineno_9 = coroutine_heap->exception_lineno;
    coroutine_heap->exception_lineno = 0;
    coroutine_heap->exception_keeper_name_9 = coroutine_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&coroutine_heap->exception_state);

    // Preserve existing published exception id 3.
    coroutine_heap->exception_preserved_3 = GET_CURRENT_EXCEPTION(tstate);

    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&coroutine_heap->exception_keeper_name_9);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(coroutine->m_frame, coroutine_heap->exception_keeper_lineno_9);
            SET_EXCEPTION_STATE_TRACEBACK(&coroutine_heap->exception_keeper_name_9, exception_tb);
        } else if (coroutine_heap->exception_keeper_lineno_9 != 0) {
            exception_tb = ADD_TRACEBACK(exception_tb, coroutine->m_frame, coroutine_heap->exception_keeper_lineno_9);
            SET_EXCEPTION_STATE_TRACEBACK(&coroutine_heap->exception_keeper_name_9, exception_tb);
        }
    }

    PUBLISH_CURRENT_EXCEPTION(tstate, &coroutine_heap->exception_keeper_name_9);
    // Tried code:
    {
        PyObject *tmp_assign_source_20;
        PyObject *tmp_iter_arg_3;
        if (coroutine_heap->var_listeners == NULL) {

            FORMAT_UNBOUND_LOCAL_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[26]);
            NORMALIZE_EXCEPTION_STATE(tstate, &coroutine_heap->exception_state);
            CHAIN_EXCEPTION(tstate, coroutine_heap->exception_state.exception_value);

            coroutine_heap->exception_lineno = 155;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_11;
        }

        tmp_iter_arg_3 = coroutine_heap->var_listeners;
        tmp_assign_source_20 = MAKE_ITERATOR(tstate, tmp_iter_arg_3);
        if (tmp_assign_source_20 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 155;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_11;
        }
        assert(coroutine_heap->tmp_for_loop_2__for_iterator == NULL);
        coroutine_heap->tmp_for_loop_2__for_iterator = tmp_assign_source_20;
    }
    // Tried code:
    loop_start_2:;
    {
        PyObject *tmp_next_source_2;
        PyObject *tmp_assign_source_21;
        CHECK_OBJECT(coroutine_heap->tmp_for_loop_2__for_iterator);
        tmp_next_source_2 = coroutine_heap->tmp_for_loop_2__for_iterator;
        tmp_assign_source_21 = ITERATOR_NEXT_ITERATOR(tmp_next_source_2);
        if (tmp_assign_source_21 == NULL) {
            if (CHECK_AND_CLEAR_STOP_ITERATION_OCCURRED(tstate)) {

                goto loop_end_2;
            } else {

                FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);
                coroutine_heap->type_description_1 = "cccooooooooooooN";
                coroutine_heap->exception_lineno = 155;
                goto try_except_handler_12;
            }
        }

        {
            PyObject *old = coroutine_heap->tmp_for_loop_2__iter_value;
            coroutine_heap->tmp_for_loop_2__iter_value = tmp_assign_source_21;
            Py_XDECREF(old);
        }

    }
    {
        PyObject *tmp_assign_source_22;
        CHECK_OBJECT(coroutine_heap->tmp_for_loop_2__iter_value);
        tmp_assign_source_22 = coroutine_heap->tmp_for_loop_2__iter_value;
        {
            PyObject *old = coroutine_heap->var_listener;
            coroutine_heap->var_listener = tmp_assign_source_22;
            Py_INCREF(coroutine_heap->var_listener);
            Py_XDECREF(old);
        }

    }
    {
        PyObject *tmp_called_instance_5;
        PyObject *tmp_expression_value_15;
        PyObject *tmp_call_result_4;
        CHECK_OBJECT(coroutine_heap->var_listener);
        tmp_expression_value_15 = coroutine_heap->var_listener;
        tmp_called_instance_5 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_15, mod_consts[15]);
        if (tmp_called_instance_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 156;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_12;
        }
        coroutine->m_frame->m_frame.f_lineno = 156;
        tmp_call_result_4 = CALL_METHOD_NO_ARGS(tstate, tmp_called_instance_5, mod_consts[29]);
        Py_DECREF(tmp_called_instance_5);
        if (tmp_call_result_4 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 156;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto try_except_handler_12;
        }
        Py_DECREF(tmp_call_result_4);
    }
    if (CONSIDER_THREADING(tstate) == false) {
        assert(HAS_ERROR_OCCURRED(tstate));

        FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


        coroutine_heap->exception_lineno = 155;
        coroutine_heap->type_description_1 = "cccooooooooooooN";
        goto try_except_handler_12;
    }
    goto loop_start_2;
    loop_end_2:;
    goto try_end_7;
    // Exception handler code:
    try_except_handler_12:;
    coroutine_heap->exception_keeper_lineno_10 = coroutine_heap->exception_lineno;
    coroutine_heap->exception_lineno = 0;
    coroutine_heap->exception_keeper_name_10 = coroutine_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&coroutine_heap->exception_state);

    Py_XDECREF(coroutine_heap->tmp_for_loop_2__iter_value);
    coroutine_heap->tmp_for_loop_2__iter_value = NULL;
    CHECK_OBJECT(coroutine_heap->tmp_for_loop_2__for_iterator);
    Py_DECREF(coroutine_heap->tmp_for_loop_2__for_iterator);
    coroutine_heap->tmp_for_loop_2__for_iterator = NULL;
    // Re-raise.
    coroutine_heap->exception_state = coroutine_heap->exception_keeper_name_10;
    coroutine_heap->exception_lineno = coroutine_heap->exception_keeper_lineno_10;

    goto try_except_handler_11;
    // End of try:
    try_end_7:;
    Py_XDECREF(coroutine_heap->tmp_for_loop_2__iter_value);
    coroutine_heap->tmp_for_loop_2__iter_value = NULL;
    CHECK_OBJECT(coroutine_heap->tmp_for_loop_2__for_iterator);
    Py_DECREF(coroutine_heap->tmp_for_loop_2__for_iterator);
    coroutine_heap->tmp_for_loop_2__for_iterator = NULL;
    coroutine_heap->tmp_result = RERAISE_EXCEPTION(tstate, &coroutine_heap->exception_state);
    if (unlikely(coroutine_heap->tmp_result == false)) {
        coroutine_heap->exception_lineno = 157;
    }

    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&coroutine_heap->exception_state);

        if ((exception_tb != NULL) && (exception_tb->tb_frame == &coroutine->m_frame->m_frame)) {
            coroutine->m_frame->m_frame.f_lineno = exception_tb->tb_lineno;
        }
    }
    coroutine_heap->type_description_1 = "cccooooooooooooN";
    goto try_except_handler_11;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Exception handler code:
    try_except_handler_11:;
    coroutine_heap->exception_keeper_lineno_11 = coroutine_heap->exception_lineno;
    coroutine_heap->exception_lineno = 0;
    coroutine_heap->exception_keeper_name_11 = coroutine_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&coroutine_heap->exception_state);

    // Restore previous exception id 3.
    SET_CURRENT_EXCEPTION(tstate, &coroutine_heap->exception_preserved_3);

    // Re-raise.
    coroutine_heap->exception_state = coroutine_heap->exception_keeper_name_11;
    coroutine_heap->exception_lineno = coroutine_heap->exception_keeper_lineno_11;

    goto frame_exception_exit_1;
    // End of try:
    // End of try:
    try_end_6:;
    Py_XDECREF(coroutine_heap->tmp_for_loop_1__iter_value);
    coroutine_heap->tmp_for_loop_1__iter_value = NULL;
    CHECK_OBJECT(coroutine_heap->tmp_for_loop_1__for_iterator);
    Py_DECREF(coroutine_heap->tmp_for_loop_1__for_iterator);
    coroutine_heap->tmp_for_loop_1__for_iterator = NULL;
    {
        nuitka_bool tmp_condition_result_5;
        int tmp_and_left_truth_1;
        nuitka_bool tmp_and_left_value_1;
        nuitka_bool tmp_and_right_value_1;
        int tmp_truth_name_1;
        PyObject *tmp_operand_value_3;
        if (coroutine_heap->var_unsupported_address_families == NULL) {

            FORMAT_UNBOUND_LOCAL_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[18]);
            NORMALIZE_EXCEPTION_STATE(tstate, &coroutine_heap->exception_state);
            CHAIN_EXCEPTION(tstate, coroutine_heap->exception_state.exception_value);

            coroutine_heap->exception_lineno = 159;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }

        tmp_truth_name_1 = CHECK_IF_TRUE(coroutine_heap->var_unsupported_address_families);
        if (tmp_truth_name_1 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 159;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }
        tmp_and_left_value_1 = tmp_truth_name_1 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        tmp_and_left_truth_1 = tmp_and_left_value_1 == NUITKA_BOOL_TRUE ? 1 : 0;
        if (tmp_and_left_truth_1 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 159;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }
        if (tmp_and_left_truth_1 == 1) {
            goto and_right_1;
        } else {
            goto and_left_1;
        }
        and_right_1:;
        if (coroutine_heap->var_listeners == NULL) {

            FORMAT_UNBOUND_LOCAL_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[26]);
            NORMALIZE_EXCEPTION_STATE(tstate, &coroutine_heap->exception_state);
            CHAIN_EXCEPTION(tstate, coroutine_heap->exception_state.exception_value);

            coroutine_heap->exception_lineno = 159;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }

        tmp_operand_value_3 = coroutine_heap->var_listeners;
        coroutine_heap->tmp_res = CHECK_IF_TRUE(tmp_operand_value_3);
        if (coroutine_heap->tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 159;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }
        tmp_and_right_value_1 = (coroutine_heap->tmp_res == 0) ? NUITKA_BOOL_TRUE : NUITKA_BOOL_FALSE;
        tmp_condition_result_5 = tmp_and_right_value_1;
        goto and_end_1;
        and_left_1:;
        tmp_condition_result_5 = tmp_and_left_value_1;
        and_end_1:;
        if (tmp_condition_result_5 == NUITKA_BOOL_TRUE) {
            goto branch_yes_5;
        } else {
            goto branch_no_5;
        }
    }
    branch_yes_5:;
    {
        PyObject *tmp_raise_type_2;
        PyObject *tmp_make_exception_arg_2;
        PyObject *tmp_expression_value_16;
        PyObject *tmp_make_exception_arg_3;
        PyObject *tmp_raise_cause_1;
        PyObject *tmp_called_value_5;
        PyObject *tmp_args_element_value_11;
        PyObject *tmp_args_element_value_12;
        tmp_expression_value_16 = module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$errno(tstate);
        if (unlikely(tmp_expression_value_16 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[16]);
        }

        if (tmp_expression_value_16 == NULL) {
            assert(HAS_EXCEPTION_STATE(&coroutine_heap->exception_state));



            coroutine_heap->exception_lineno = 164;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }
        tmp_make_exception_arg_2 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_16, mod_consts[17]);
        if (tmp_make_exception_arg_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 164;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }
        tmp_make_exception_arg_3 = mod_consts[30];
        coroutine->m_frame->m_frame.f_lineno = 164;
        {
            PyObject *call_args[] = {tmp_make_exception_arg_2, tmp_make_exception_arg_3};
            tmp_raise_type_2 = CALL_FUNCTION_WITH_ARGS2(tstate, PyExc_OSError, call_args);
        }

        Py_DECREF(tmp_make_exception_arg_2);
        assert(!(tmp_raise_type_2 == NULL));
        tmp_called_value_5 = module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$ExceptionGroup(tstate);
        if (unlikely(tmp_called_value_5 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[31]);
        }

        if (tmp_called_value_5 == NULL) {
            assert(HAS_EXCEPTION_STATE(&coroutine_heap->exception_state));

            Py_DECREF(tmp_raise_type_2);

            coroutine_heap->exception_lineno = 164;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }
        tmp_args_element_value_11 = mod_consts[30];
        if (coroutine_heap->var_unsupported_address_families == NULL) {
            Py_DECREF(tmp_raise_type_2);
            FORMAT_UNBOUND_LOCAL_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[18]);
            NORMALIZE_EXCEPTION_STATE(tstate, &coroutine_heap->exception_state);
            CHAIN_EXCEPTION(tstate, coroutine_heap->exception_state.exception_value);

            coroutine_heap->exception_lineno = 166;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }

        tmp_args_element_value_12 = coroutine_heap->var_unsupported_address_families;
        coroutine->m_frame->m_frame.f_lineno = 164;
        {
            PyObject *call_args[] = {tmp_args_element_value_11, tmp_args_element_value_12};
            tmp_raise_cause_1 = CALL_FUNCTION_WITH_ARGS2(tstate, tmp_called_value_5, call_args);
        }

        if (tmp_raise_cause_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);
            Py_DECREF(tmp_raise_type_2);

            coroutine_heap->exception_lineno = 164;
            coroutine_heap->type_description_1 = "cccooooooooooooN";
            goto frame_exception_exit_1;
        }
        coroutine_heap->exception_state.exception_type = tmp_raise_type_2;
        coroutine_heap->exception_lineno = 164;
        RAISE_EXCEPTION_WITH_CAUSE(tstate, &coroutine_heap->exception_state, tmp_raise_cause_1);
        coroutine_heap->type_description_1 = "cccooooooooooooN";
        goto frame_exception_exit_1;
    }
    branch_no_5:;
    if (coroutine_heap->var_listeners == NULL) {

        FORMAT_UNBOUND_LOCAL_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[26]);
        NORMALIZE_EXCEPTION_STATE(tstate, &coroutine_heap->exception_state);
        CHAIN_EXCEPTION(tstate, coroutine_heap->exception_state.exception_value);

        coroutine_heap->exception_lineno = 169;
        coroutine_heap->type_description_1 = "cccooooooooooooN";
        goto frame_exception_exit_1;
    }

    coroutine_heap->tmp_return_value = coroutine_heap->var_listeners;
    Py_INCREF(coroutine_heap->tmp_return_value);
    goto frame_return_exit_1;

    // Release exception attached to the frame
    DROP_COROUTINE_EXCEPTION(coroutine);



    goto frame_no_exception_1;
    frame_return_exit_1:;

#if PYTHON_VERSION >= 0x300
#if PYTHON_VERSION < 0x3b0
    Py_CLEAR(EXC_TYPE_F(coroutine));
#endif
    Py_CLEAR(EXC_VALUE_F(coroutine));
#if PYTHON_VERSION < 0x3b0
    Py_CLEAR(EXC_TRACEBACK_F(coroutine));
#endif
#endif

    goto try_return_handler_1;

    frame_exception_exit_1:;

    // If it's not an exit exception, consider and create a traceback for it.
    if (!EXCEPTION_STATE_MATCH_GENERATOR(tstate, &coroutine_heap->exception_state)) {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&coroutine_heap->exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(coroutine->m_frame, coroutine_heap->exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&coroutine_heap->exception_state, exception_tb);
        } else if ((coroutine_heap->exception_lineno != 0) && (exception_tb->tb_frame != &coroutine->m_frame->m_frame)) {
            exception_tb = ADD_TRACEBACK(exception_tb, coroutine->m_frame, coroutine_heap->exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&coroutine_heap->exception_state, exception_tb);
        }

        Nuitka_Frame_AttachLocals(
            coroutine->m_frame,
            coroutine_heap->type_description_1,
            coroutine->m_closure[2],
            coroutine->m_closure[1],
            coroutine->m_closure[0],
            coroutine_heap->var_computed_backlog,
            coroutine_heap->var_addresses,
            coroutine_heap->var_listeners,
            coroutine_heap->var_unsupported_address_families,
            coroutine_heap->var_family,
            coroutine_heap->var_type_,
            coroutine_heap->var_proto,
            coroutine_heap->var__,
            coroutine_heap->var_sockaddr,
            coroutine_heap->var_sock,
            coroutine_heap->var_ex,
            coroutine_heap->var_listener,
            NULL
        );


        // Release cached frame if used for exception.
        if (coroutine->m_frame == cache_m_frame) {
#if _DEBUG_REFCOUNTS
            count_active_frame_cache_instances -= 1;
            count_released_frame_cache_instances += 1;
#endif

            Py_DECREF(cache_m_frame);
            cache_m_frame = NULL;
        }

        assertFrameObject(coroutine->m_frame);
    }

    // Release exception attached to the frame
    DROP_COROUTINE_EXCEPTION(coroutine);


    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Return handler code:
    try_return_handler_1:;
    Py_XDECREF(coroutine_heap->var_computed_backlog);
    coroutine_heap->var_computed_backlog = NULL;
    CHECK_OBJECT(coroutine_heap->var_addresses);
    Py_DECREF(coroutine_heap->var_addresses);
    coroutine_heap->var_addresses = NULL;
    Py_XDECREF(coroutine_heap->var_listeners);
    coroutine_heap->var_listeners = NULL;
    Py_XDECREF(coroutine_heap->var_unsupported_address_families);
    coroutine_heap->var_unsupported_address_families = NULL;
    Py_XDECREF(coroutine_heap->var_family);
    coroutine_heap->var_family = NULL;
    Py_XDECREF(coroutine_heap->var_type_);
    coroutine_heap->var_type_ = NULL;
    Py_XDECREF(coroutine_heap->var_proto);
    coroutine_heap->var_proto = NULL;
    Py_XDECREF(coroutine_heap->var__);
    coroutine_heap->var__ = NULL;
    Py_XDECREF(coroutine_heap->var_sockaddr);
    coroutine_heap->var_sockaddr = NULL;
    Py_XDECREF(coroutine_heap->var_sock);
    coroutine_heap->var_sock = NULL;
    Py_XDECREF(coroutine_heap->var_ex);
    coroutine_heap->var_ex = NULL;
    goto function_return_exit;
    // Exception handler code:
    try_except_handler_1:;
    coroutine_heap->exception_keeper_lineno_12 = coroutine_heap->exception_lineno;
    coroutine_heap->exception_lineno = 0;
    coroutine_heap->exception_keeper_name_12 = coroutine_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&coroutine_heap->exception_state);

    Py_XDECREF(coroutine_heap->var_computed_backlog);
    coroutine_heap->var_computed_backlog = NULL;
    Py_XDECREF(coroutine_heap->var_addresses);
    coroutine_heap->var_addresses = NULL;
    Py_XDECREF(coroutine_heap->var_listeners);
    coroutine_heap->var_listeners = NULL;
    Py_XDECREF(coroutine_heap->var_unsupported_address_families);
    coroutine_heap->var_unsupported_address_families = NULL;
    Py_XDECREF(coroutine_heap->var_family);
    coroutine_heap->var_family = NULL;
    Py_XDECREF(coroutine_heap->var_type_);
    coroutine_heap->var_type_ = NULL;
    Py_XDECREF(coroutine_heap->var_proto);
    coroutine_heap->var_proto = NULL;
    Py_XDECREF(coroutine_heap->var__);
    coroutine_heap->var__ = NULL;
    Py_XDECREF(coroutine_heap->var_sockaddr);
    coroutine_heap->var_sockaddr = NULL;
    Py_XDECREF(coroutine_heap->var_sock);
    coroutine_heap->var_sock = NULL;
    Py_XDECREF(coroutine_heap->var_ex);
    coroutine_heap->var_ex = NULL;
    Py_XDECREF(coroutine_heap->var_listener);
    coroutine_heap->var_listener = NULL;
    // Re-raise.
    coroutine_heap->exception_state = coroutine_heap->exception_keeper_name_12;
    coroutine_heap->exception_lineno = coroutine_heap->exception_keeper_lineno_12;

    goto function_exception_exit;
    // End of try:

    NUITKA_CANNOT_GET_HERE("Return statement must be present");

    function_exception_exit:

    CHECK_EXCEPTION_STATE(&coroutine_heap->exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);
    return NULL;
    function_return_exit:;

    coroutine->m_returned = coroutine_heap->tmp_return_value;

    return NULL;

}

static PyObject *MAKE_COROUTINE_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__2_open_tcp_listeners$$36$$$36$$$36$coroutine__1_open_tcp_listeners(PyThreadState *tstate, struct Nuitka_CellObject **closure) {
    return Nuitka_Coroutine_New(
        tstate,
        trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__2_open_tcp_listeners$$36$$$36$$$36$coroutine__1_open_tcp_listeners_context,
        module_trio$_highlevel_open_tcp_listeners,
        mod_consts[32],
        NULL,
        code_objects_e8c68bf30da4df84e255a3b70495ca70,
        closure,
        3,
#if 1
        sizeof(struct trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__2_open_tcp_listeners$$36$$$36$$$36$coroutine__1_open_tcp_listeners_locals)
#else
        0
#endif
    );
}


static PyObject *impl_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__3_serve_tcp(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    struct Nuitka_CellObject *par_handler = Nuitka_Cell_New1(python_pars[0]);
    struct Nuitka_CellObject *par_port = Nuitka_Cell_New1(python_pars[1]);
    struct Nuitka_CellObject *par_host = Nuitka_Cell_New1(python_pars[2]);
    struct Nuitka_CellObject *par_backlog = Nuitka_Cell_New1(python_pars[3]);
    struct Nuitka_CellObject *par_handler_nursery = Nuitka_Cell_New1(python_pars[4]);
    struct Nuitka_CellObject *par_task_status = Nuitka_Cell_New1(python_pars[5]);
    PyObject *tmp_return_value = NULL;

    // Actual function body.
    {
        struct Nuitka_CellObject *tmp_closure_1[6];

        tmp_closure_1[0] = par_backlog;
        Py_INCREF(tmp_closure_1[0]);
        tmp_closure_1[1] = par_handler;
        Py_INCREF(tmp_closure_1[1]);
        tmp_closure_1[2] = par_handler_nursery;
        Py_INCREF(tmp_closure_1[2]);
        tmp_closure_1[3] = par_host;
        Py_INCREF(tmp_closure_1[3]);
        tmp_closure_1[4] = par_port;
        Py_INCREF(tmp_closure_1[4]);
        tmp_closure_1[5] = par_task_status;
        Py_INCREF(tmp_closure_1[5]);

        tmp_return_value = MAKE_COROUTINE_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__3_serve_tcp$$36$$$36$$$36$coroutine__1_serve_tcp(tstate, tmp_closure_1);

        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_handler);
    Py_DECREF(par_handler);
    CHECK_OBJECT(par_port);
    Py_DECREF(par_port);
    CHECK_OBJECT(par_host);
    Py_DECREF(par_host);
    CHECK_OBJECT(par_backlog);
    Py_DECREF(par_backlog);
    CHECK_OBJECT(par_handler_nursery);
    Py_DECREF(par_handler_nursery);
    CHECK_OBJECT(par_task_status);
    Py_DECREF(par_task_status);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}



#if 1
struct trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__3_serve_tcp$$36$$$36$$$36$coroutine__1_serve_tcp_locals {
    PyObject *var_listeners;
    char const *type_description_1;
    struct Nuitka_ExceptionPreservationItem exception_state;
    int exception_lineno;
    char yield_tmps[1024];
    PyObject *tmp_return_value;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    int exception_keeper_lineno_1;
};
#endif

static PyObject *trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__3_serve_tcp$$36$$$36$$$36$coroutine__1_serve_tcp_context(PyThreadState *tstate, struct Nuitka_CoroutineObject *coroutine, PyObject *yield_return_value) {
    CHECK_OBJECT(coroutine);
    assert(Nuitka_Coroutine_Check((PyObject *)coroutine));
    CHECK_OBJECT_X(yield_return_value);

#if 1
    // Heap access.
    struct trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__3_serve_tcp$$36$$$36$$$36$coroutine__1_serve_tcp_locals *coroutine_heap = (struct trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__3_serve_tcp$$36$$$36$$$36$coroutine__1_serve_tcp_locals *)coroutine->m_heap_storage;
#endif

    // Dispatch to yield based on return label index:
    switch(coroutine->m_yield_return_index) {
    case 2: goto yield_return_2;
    case 1: goto yield_return_1;
    }

    // Local variable initialization
    NUITKA_MAY_BE_UNUSED nuitka_void tmp_unused;
    static struct Nuitka_FrameObject *cache_m_frame = NULL;
    coroutine_heap->var_listeners = NULL;
    coroutine_heap->type_description_1 = NULL;
    coroutine_heap->exception_state = Empty_Nuitka_ExceptionPreservationItem;
    coroutine_heap->exception_lineno = 0;
    coroutine_heap->tmp_return_value = NULL;

    // Actual coroutine body.
    // Tried code:
    if (isFrameUnusable(cache_m_frame)) {
        Py_XDECREF(cache_m_frame);

#if _DEBUG_REFCOUNTS
        if (cache_m_frame == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_m_frame = MAKE_FUNCTION_FRAME(tstate, code_objects_2fb6da62d72bae8c939c2f4bacd9c5af, module_trio$_highlevel_open_tcp_listeners, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_m_frame->m_type_description == NULL);
    coroutine->m_frame = cache_m_frame;
    // Mark the frame object as in use, ref count 1 will be up for reuse.
    Py_INCREF(coroutine->m_frame);
    assert(Py_REFCNT(coroutine->m_frame) == 2); // Frame stack

    Nuitka_SetFrameGenerator(coroutine->m_frame, (PyObject *)coroutine);

    assert(coroutine->m_frame->m_frame.f_back == NULL);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackGeneratorCompiledFrame(tstate, coroutine->m_frame);
    assert(Py_REFCNT(coroutine->m_frame) == 2);

    // Store currently existing exception as the one to publish again when we
    // yield or yield from.
    STORE_COROUTINE_EXCEPTION(tstate, coroutine);

    // Framed code:
    {
        PyObject *tmp_assign_source_1;
        PyObject *tmp_expression_value_1;
        PyObject *tmp_expression_value_2;
        PyObject *tmp_called_value_1;
        PyObject *tmp_expression_value_3;
        PyObject *tmp_kw_call_arg_value_0_1;
        PyObject *tmp_kw_call_dict_value_0_1;
        PyObject *tmp_kw_call_dict_value_1_1;
        coroutine->m_frame->m_frame.f_lineno = 245;
        tmp_expression_value_3 = module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$trio(tstate);
        if (unlikely(tmp_expression_value_3 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[27]);
        }

        if (tmp_expression_value_3 == NULL) {
            assert(HAS_EXCEPTION_STATE(&coroutine_heap->exception_state));



            coroutine_heap->exception_lineno = 245;
            coroutine_heap->type_description_1 = "cccccco";
            goto frame_exception_exit_1;
        }
        tmp_called_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_3, mod_consts[32]);
        if (tmp_called_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 245;
            coroutine_heap->type_description_1 = "cccccco";
            goto frame_exception_exit_1;
        }
        if (Nuitka_Cell_GET(coroutine->m_closure[4]) == NULL) {
            Py_DECREF(tmp_called_value_1);
            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[5]);
            NORMALIZE_EXCEPTION_STATE(tstate, &coroutine_heap->exception_state);
            CHAIN_EXCEPTION(tstate, coroutine_heap->exception_state.exception_value);

            coroutine_heap->exception_lineno = 245;
            coroutine_heap->type_description_1 = "cccccco";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_arg_value_0_1 = Nuitka_Cell_GET(coroutine->m_closure[4]);
        if (Nuitka_Cell_GET(coroutine->m_closure[3]) == NULL) {
            Py_DECREF(tmp_called_value_1);
            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[11]);
            NORMALIZE_EXCEPTION_STATE(tstate, &coroutine_heap->exception_state);
            CHAIN_EXCEPTION(tstate, coroutine_heap->exception_state.exception_value);

            coroutine_heap->exception_lineno = 245;
            coroutine_heap->type_description_1 = "cccccco";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_dict_value_0_1 = Nuitka_Cell_GET(coroutine->m_closure[3]);
        if (Nuitka_Cell_GET(coroutine->m_closure[0]) == NULL) {
            Py_DECREF(tmp_called_value_1);
            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[8]);
            NORMALIZE_EXCEPTION_STATE(tstate, &coroutine_heap->exception_state);
            CHAIN_EXCEPTION(tstate, coroutine_heap->exception_state.exception_value);

            coroutine_heap->exception_lineno = 245;
            coroutine_heap->type_description_1 = "cccccco";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_dict_value_1_1 = Nuitka_Cell_GET(coroutine->m_closure[0]);
        coroutine->m_frame->m_frame.f_lineno = 245;
        {
            PyObject *args[] = {tmp_kw_call_arg_value_0_1};
            PyObject *kw_values[2] = {tmp_kw_call_dict_value_0_1, tmp_kw_call_dict_value_1_1};
            tmp_expression_value_2 = CALL_FUNCTION_WITH_ARGS1_KW_SPLIT(tstate, tmp_called_value_1, args, kw_values, mod_consts[34]);
        }

        Py_DECREF(tmp_called_value_1);
        if (tmp_expression_value_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 245;
            coroutine_heap->type_description_1 = "cccccco";
            goto frame_exception_exit_1;
        }
        tmp_expression_value_1 = ASYNC_AWAIT(tstate, tmp_expression_value_2, await_normal);
        Py_DECREF(tmp_expression_value_2);
        if (tmp_expression_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 245;
            coroutine_heap->type_description_1 = "cccccco";
            goto frame_exception_exit_1;
        }
        Nuitka_PreserveHeap(coroutine_heap->yield_tmps, &tmp_expression_value_2, sizeof(PyObject *), &tmp_called_value_1, sizeof(PyObject *), &tmp_expression_value_3, sizeof(PyObject *), &tmp_kw_call_arg_value_0_1, sizeof(PyObject *), &tmp_kw_call_dict_value_0_1, sizeof(PyObject *), &tmp_kw_call_dict_value_1_1, sizeof(PyObject *), NULL);
        coroutine->m_yield_return_index = 1;
        coroutine->m_yield_from = tmp_expression_value_1;
        coroutine->m_awaiting = true;
        return NULL;

        yield_return_1:
        Nuitka_RestoreHeap(coroutine_heap->yield_tmps, &tmp_expression_value_2, sizeof(PyObject *), &tmp_called_value_1, sizeof(PyObject *), &tmp_expression_value_3, sizeof(PyObject *), &tmp_kw_call_arg_value_0_1, sizeof(PyObject *), &tmp_kw_call_dict_value_0_1, sizeof(PyObject *), &tmp_kw_call_dict_value_1_1, sizeof(PyObject *), NULL);
        coroutine->m_awaiting = false;

        if (yield_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 245;
            coroutine_heap->type_description_1 = "cccccco";
            goto frame_exception_exit_1;
        }
        tmp_assign_source_1 = yield_return_value;
        assert(coroutine_heap->var_listeners == NULL);
        coroutine_heap->var_listeners = tmp_assign_source_1;
    }
    {
        PyObject *tmp_expression_value_4;
        PyObject *tmp_expression_value_5;
        PyObject *tmp_called_value_2;
        PyObject *tmp_expression_value_6;
        PyObject *tmp_kw_call_arg_value_0_2;
        PyObject *tmp_kw_call_arg_value_1_1;
        PyObject *tmp_kw_call_dict_value_0_2;
        PyObject *tmp_kw_call_dict_value_1_2;
        PyObject *tmp_await_result_1;
        coroutine->m_frame->m_frame.f_lineno = 246;
        tmp_expression_value_6 = module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$trio(tstate);
        if (unlikely(tmp_expression_value_6 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[27]);
        }

        if (tmp_expression_value_6 == NULL) {
            assert(HAS_EXCEPTION_STATE(&coroutine_heap->exception_state));



            coroutine_heap->exception_lineno = 246;
            coroutine_heap->type_description_1 = "cccccco";
            goto frame_exception_exit_1;
        }
        tmp_called_value_2 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_6, mod_consts[35]);
        if (tmp_called_value_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 246;
            coroutine_heap->type_description_1 = "cccccco";
            goto frame_exception_exit_1;
        }
        if (Nuitka_Cell_GET(coroutine->m_closure[1]) == NULL) {
            Py_DECREF(tmp_called_value_2);
            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[36]);
            NORMALIZE_EXCEPTION_STATE(tstate, &coroutine_heap->exception_state);
            CHAIN_EXCEPTION(tstate, coroutine_heap->exception_state.exception_value);

            coroutine_heap->exception_lineno = 247;
            coroutine_heap->type_description_1 = "cccccco";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_arg_value_0_2 = Nuitka_Cell_GET(coroutine->m_closure[1]);
        CHECK_OBJECT(coroutine_heap->var_listeners);
        tmp_kw_call_arg_value_1_1 = coroutine_heap->var_listeners;
        if (Nuitka_Cell_GET(coroutine->m_closure[2]) == NULL) {
            Py_DECREF(tmp_called_value_2);
            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[37]);
            NORMALIZE_EXCEPTION_STATE(tstate, &coroutine_heap->exception_state);
            CHAIN_EXCEPTION(tstate, coroutine_heap->exception_state.exception_value);

            coroutine_heap->exception_lineno = 249;
            coroutine_heap->type_description_1 = "cccccco";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_dict_value_0_2 = Nuitka_Cell_GET(coroutine->m_closure[2]);
        if (Nuitka_Cell_GET(coroutine->m_closure[5]) == NULL) {
            Py_DECREF(tmp_called_value_2);
            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &coroutine_heap->exception_state, mod_consts[38]);
            NORMALIZE_EXCEPTION_STATE(tstate, &coroutine_heap->exception_state);
            CHAIN_EXCEPTION(tstate, coroutine_heap->exception_state.exception_value);

            coroutine_heap->exception_lineno = 250;
            coroutine_heap->type_description_1 = "cccccco";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_dict_value_1_2 = Nuitka_Cell_GET(coroutine->m_closure[5]);
        coroutine->m_frame->m_frame.f_lineno = 246;
        {
            PyObject *args[] = {tmp_kw_call_arg_value_0_2, tmp_kw_call_arg_value_1_1};
            PyObject *kw_values[2] = {tmp_kw_call_dict_value_0_2, tmp_kw_call_dict_value_1_2};
            tmp_expression_value_5 = CALL_FUNCTION_WITH_ARGS2_KW_SPLIT(tstate, tmp_called_value_2, args, kw_values, mod_consts[39]);
        }

        Py_DECREF(tmp_called_value_2);
        if (tmp_expression_value_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 246;
            coroutine_heap->type_description_1 = "cccccco";
            goto frame_exception_exit_1;
        }
        tmp_expression_value_4 = ASYNC_AWAIT(tstate, tmp_expression_value_5, await_normal);
        Py_DECREF(tmp_expression_value_5);
        if (tmp_expression_value_4 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 246;
            coroutine_heap->type_description_1 = "cccccco";
            goto frame_exception_exit_1;
        }
        Nuitka_PreserveHeap(coroutine_heap->yield_tmps, &tmp_expression_value_5, sizeof(PyObject *), &tmp_called_value_2, sizeof(PyObject *), &tmp_expression_value_6, sizeof(PyObject *), &tmp_kw_call_arg_value_0_2, sizeof(PyObject *), &tmp_kw_call_arg_value_1_1, sizeof(PyObject *), &tmp_kw_call_dict_value_0_2, sizeof(PyObject *), &tmp_kw_call_dict_value_1_2, sizeof(PyObject *), NULL);
        coroutine->m_yield_return_index = 2;
        coroutine->m_yield_from = tmp_expression_value_4;
        coroutine->m_awaiting = true;
        return NULL;

        yield_return_2:
        Nuitka_RestoreHeap(coroutine_heap->yield_tmps, &tmp_expression_value_5, sizeof(PyObject *), &tmp_called_value_2, sizeof(PyObject *), &tmp_expression_value_6, sizeof(PyObject *), &tmp_kw_call_arg_value_0_2, sizeof(PyObject *), &tmp_kw_call_arg_value_1_1, sizeof(PyObject *), &tmp_kw_call_dict_value_0_2, sizeof(PyObject *), &tmp_kw_call_dict_value_1_2, sizeof(PyObject *), NULL);
        coroutine->m_awaiting = false;

        if (yield_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);


            coroutine_heap->exception_lineno = 246;
            coroutine_heap->type_description_1 = "cccccco";
            goto frame_exception_exit_1;
        }
        tmp_await_result_1 = yield_return_value;
        Py_DECREF(tmp_await_result_1);
    }

    // Release exception attached to the frame
    DROP_COROUTINE_EXCEPTION(coroutine);



    goto frame_no_exception_1;
    frame_exception_exit_1:;

    // If it's not an exit exception, consider and create a traceback for it.
    if (!EXCEPTION_STATE_MATCH_GENERATOR(tstate, &coroutine_heap->exception_state)) {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&coroutine_heap->exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(coroutine->m_frame, coroutine_heap->exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&coroutine_heap->exception_state, exception_tb);
        } else if ((coroutine_heap->exception_lineno != 0) && (exception_tb->tb_frame != &coroutine->m_frame->m_frame)) {
            exception_tb = ADD_TRACEBACK(exception_tb, coroutine->m_frame, coroutine_heap->exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&coroutine_heap->exception_state, exception_tb);
        }

        Nuitka_Frame_AttachLocals(
            coroutine->m_frame,
            coroutine_heap->type_description_1,
            coroutine->m_closure[1],
            coroutine->m_closure[4],
            coroutine->m_closure[3],
            coroutine->m_closure[0],
            coroutine->m_closure[2],
            coroutine->m_closure[5],
            coroutine_heap->var_listeners
        );


        // Release cached frame if used for exception.
        if (coroutine->m_frame == cache_m_frame) {
#if _DEBUG_REFCOUNTS
            count_active_frame_cache_instances -= 1;
            count_released_frame_cache_instances += 1;
#endif

            Py_DECREF(cache_m_frame);
            cache_m_frame = NULL;
        }

        assertFrameObject(coroutine->m_frame);
    }

    // Release exception attached to the frame
    DROP_COROUTINE_EXCEPTION(coroutine);


    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    coroutine_heap->tmp_return_value = Py_None;
    Py_INCREF(coroutine_heap->tmp_return_value);
    goto try_return_handler_1;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Return handler code:
    try_return_handler_1:;
    CHECK_OBJECT(coroutine_heap->var_listeners);
    Py_DECREF(coroutine_heap->var_listeners);
    coroutine_heap->var_listeners = NULL;
    goto function_return_exit;
    // Exception handler code:
    try_except_handler_1:;
    coroutine_heap->exception_keeper_lineno_1 = coroutine_heap->exception_lineno;
    coroutine_heap->exception_lineno = 0;
    coroutine_heap->exception_keeper_name_1 = coroutine_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&coroutine_heap->exception_state);

    Py_XDECREF(coroutine_heap->var_listeners);
    coroutine_heap->var_listeners = NULL;
    // Re-raise.
    coroutine_heap->exception_state = coroutine_heap->exception_keeper_name_1;
    coroutine_heap->exception_lineno = coroutine_heap->exception_keeper_lineno_1;

    goto function_exception_exit;
    // End of try:

    NUITKA_CANNOT_GET_HERE("Return statement must be present");

    function_exception_exit:

    CHECK_EXCEPTION_STATE(&coroutine_heap->exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &coroutine_heap->exception_state);
    return NULL;
    function_return_exit:;

    coroutine->m_returned = coroutine_heap->tmp_return_value;

    return NULL;

}

static PyObject *MAKE_COROUTINE_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__3_serve_tcp$$36$$$36$$$36$coroutine__1_serve_tcp(PyThreadState *tstate, struct Nuitka_CellObject **closure) {
    return Nuitka_Coroutine_New(
        tstate,
        trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__3_serve_tcp$$36$$$36$$$36$coroutine__1_serve_tcp_context,
        module_trio$_highlevel_open_tcp_listeners,
        mod_consts[40],
        NULL,
        code_objects_2fb6da62d72bae8c939c2f4bacd9c5af,
        closure,
        6,
#if 1
        sizeof(struct trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__3_serve_tcp$$36$$$36$$$36$coroutine__1_serve_tcp_locals)
#else
        0
#endif
    );
}



static PyObject *MAKE_FUNCTION_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog(PyThreadState *tstate, PyObject *annotations) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog,
        mod_consts[7],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_a5c538db960641bfcf6a0f2c68eb3d35,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_trio$_highlevel_open_tcp_listeners,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__2_open_tcp_listeners(PyThreadState *tstate, PyObject *kw_defaults, PyObject *annotations) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__2_open_tcp_listeners,
        mod_consts[32],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_e8c68bf30da4df84e255a3b70495ca70,
        NULL,
#if PYTHON_VERSION >= 0x300
        kw_defaults,
        annotations,
#endif
        module_trio$_highlevel_open_tcp_listeners,
        mod_consts[4],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__3_serve_tcp(PyThreadState *tstate, PyObject *kw_defaults, PyObject *annotations) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__3_serve_tcp,
        mod_consts[40],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_2fb6da62d72bae8c939c2f4bacd9c5af,
        NULL,
#if PYTHON_VERSION >= 0x300
        kw_defaults,
        annotations,
#endif
        module_trio$_highlevel_open_tcp_listeners,
        mod_consts[33],
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

static function_impl_code const function_table_trio$_highlevel_open_tcp_listeners[] = {
    impl_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog,
    impl_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__2_open_tcp_listeners,
    impl_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__3_serve_tcp,
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

    return Nuitka_Function_GetFunctionState(function, function_table_trio$_highlevel_open_tcp_listeners);
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
        module_trio$_highlevel_open_tcp_listeners,
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
        function_table_trio$_highlevel_open_tcp_listeners,
        sizeof(function_table_trio$_highlevel_open_tcp_listeners) / sizeof(function_impl_code)
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
static char const *module_full_name = "trio._highlevel_open_tcp_listeners";
#endif

// Internal entry point for module code.
PyObject *modulecode_trio$_highlevel_open_tcp_listeners(PyThreadState *tstate, PyObject *module, struct Nuitka_MetaPathBasedLoaderEntry const *loader_entry) {
    // Report entry to PGO.
    PGO_onModuleEntered("trio$_highlevel_open_tcp_listeners");

    // Store the module for future use.
    module_trio$_highlevel_open_tcp_listeners = module;

    moduledict_trio$_highlevel_open_tcp_listeners = MODULE_DICT(module_trio$_highlevel_open_tcp_listeners);

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
        PRINT_STRING("trio$_highlevel_open_tcp_listeners: Calling setupMetaPathBasedLoader().\n");
#endif
        setupMetaPathBasedLoader(tstate);
#if 0 >= 0
#ifdef _NUITKA_TRACE
        PRINT_STRING("trio$_highlevel_open_tcp_listeners: Calling updateMetaPathBasedLoaderModuleRoot().\n");
#endif
        updateMetaPathBasedLoaderModuleRoot(module_full_name);
#endif


#if PYTHON_VERSION >= 0x300
        patchInspectModule(tstate);
#endif

#endif

        /* The constants only used by this module are created now. */
        NUITKA_PRINT_TRACE("trio$_highlevel_open_tcp_listeners: Calling createModuleConstants().\n");
        createModuleConstants(tstate);

#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
        createModuleCodeObjects();
#endif
        init_done = true;
    }

#if _NUITKA_MODULE_MODE && 0
    PyObject *pre_load = IMPORT_EMBEDDED_MODULE(tstate, "trio._highlevel_open_tcp_listeners" "-preLoad");
    if (pre_load == NULL) {
        return NULL;
    }
#endif

    // PRINT_STRING("in inittrio$_highlevel_open_tcp_listeners\n");

#ifdef _NUITKA_PLUGIN_DILL_ENABLED
    {
        char const *module_name_c;
        if (loader_entry != NULL) {
            module_name_c = loader_entry->name;
        } else {
            PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)const_str_plain___name__);
            module_name_c = Nuitka_String_AsString(module_name);
        }

        registerDillPluginTables(tstate, module_name_c, &_method_def_reduce_compiled_function, &_method_def_create_compiled_function);
    }
#endif

    // Set "__compiled__" to what version information we have.
    UPDATE_STRING_DICT0(
        moduledict_trio$_highlevel_open_tcp_listeners,
        (Nuitka_StringObject *)const_str_plain___compiled__,
        Nuitka_dunder_compiled_value
    );

    // Update "__package__" value to what it ought to be.
    {
#if 0
        UPDATE_STRING_DICT0(
            moduledict_trio$_highlevel_open_tcp_listeners,
            (Nuitka_StringObject *)const_str_plain___package__,
            mod_consts[1]
        );
#elif 0
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)const_str_plain___name__);

        UPDATE_STRING_DICT0(
            moduledict_trio$_highlevel_open_tcp_listeners,
            (Nuitka_StringObject *)const_str_plain___package__,
            module_name
        );
#else

#if PYTHON_VERSION < 0x300
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)const_str_plain___name__);
        char const *module_name_cstr = PyString_AS_STRING(module_name);

        char const *last_dot = strrchr(module_name_cstr, '.');

        if (last_dot != NULL) {
            UPDATE_STRING_DICT1(
                moduledict_trio$_highlevel_open_tcp_listeners,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyString_FromStringAndSize(module_name_cstr, last_dot - module_name_cstr)
            );
        }
#else
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)const_str_plain___name__);
        Py_ssize_t dot_index = PyUnicode_Find(module_name, const_str_dot, 0, PyUnicode_GetLength(module_name), -1);

        if (dot_index != -1) {
            UPDATE_STRING_DICT1(
                moduledict_trio$_highlevel_open_tcp_listeners,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyUnicode_Substring(module_name, 0, dot_index)
            );
        }
#endif
#endif
    }

    CHECK_OBJECT(module_trio$_highlevel_open_tcp_listeners);

    // For deep importing of a module we need to have "__builtins__", so we set
    // it ourselves in the same way than CPython does. Note: This must be done
    // before the frame object is allocated, or else it may fail.

    if (GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)const_str_plain___builtins__) == NULL) {
        PyObject *value = (PyObject *)builtin_module;

        // Check if main module, not a dict then but the module itself.
#if _NUITKA_MODULE_MODE || !0
        value = PyModule_GetDict(value);
#endif

        UPDATE_STRING_DICT0(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)const_str_plain___builtins__, value);
    }

    PyObject *module_loader = Nuitka_Loader_New(loader_entry);
    UPDATE_STRING_DICT0(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)const_str_plain___loader__, module_loader);

#if PYTHON_VERSION >= 0x300
// Set the "__spec__" value

#if 0
    // Main modules just get "None" as spec.
    UPDATE_STRING_DICT0(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)const_str_plain___spec__, Py_None);
#else
    // Other modules get a "ModuleSpec" from the standard mechanism.
    {
        PyObject *bootstrap_module = getImportLibBootstrapModule();
        CHECK_OBJECT(bootstrap_module);

        PyObject *_spec_from_module = PyObject_GetAttrString(bootstrap_module, "_spec_from_module");
        CHECK_OBJECT(_spec_from_module);

        PyObject *spec_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, _spec_from_module, module_trio$_highlevel_open_tcp_listeners);
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

        UPDATE_STRING_DICT1(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)const_str_plain___spec__, spec_value);
    }
#endif
#endif

    // Temp variables if any
    struct Nuitka_FrameObject *frame_frame_trio$_highlevel_open_tcp_listeners;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    bool tmp_result;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    int tmp_res;

    // Module init code if any


    // Module code.
    {
        PyObject *tmp_assign_source_1;
        tmp_assign_source_1 = Py_None;
        UPDATE_STRING_DICT0(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[41], tmp_assign_source_1);
    }
    {
        PyObject *tmp_assign_source_2;
        tmp_assign_source_2 = module_filename_obj;
        UPDATE_STRING_DICT0(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[42], tmp_assign_source_2);
    }
    frame_frame_trio$_highlevel_open_tcp_listeners = MAKE_MODULE_FRAME(code_objects_d605a67f1ef0ef685be8dc5ba72b7cff, module_trio$_highlevel_open_tcp_listeners);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_trio$_highlevel_open_tcp_listeners);
    assert(Py_REFCNT(frame_frame_trio$_highlevel_open_tcp_listeners) == 2);

    // Framed code:
    {
        PyObject *tmp_assattr_value_1;
        PyObject *tmp_assattr_target_1;
        tmp_assattr_value_1 = module_filename_obj;
        tmp_assattr_target_1 = module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$__spec__(tstate);
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
        tmp_assattr_target_2 = module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$__spec__(tstate);
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
        UPDATE_STRING_DICT0(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[45], tmp_assign_source_3);
    }
    {
        PyObject *tmp_assign_source_4;
        {
            PyObject *hard_module = IMPORT_HARD___FUTURE__();
            tmp_assign_source_4 = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[46]);
        }
        assert(!(tmp_assign_source_4 == NULL));
        UPDATE_STRING_DICT1(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[46], tmp_assign_source_4);
    }
    {
        PyObject *tmp_assign_source_5;
        PyObject *tmp_name_value_1;
        PyObject *tmp_globals_arg_value_1;
        PyObject *tmp_locals_arg_value_1;
        PyObject *tmp_fromlist_value_1;
        PyObject *tmp_level_value_1;
        tmp_name_value_1 = mod_consts[16];
        tmp_globals_arg_value_1 = (PyObject *)moduledict_trio$_highlevel_open_tcp_listeners;
        tmp_locals_arg_value_1 = Py_None;
        tmp_fromlist_value_1 = Py_None;
        tmp_level_value_1 = const_int_0;
        frame_frame_trio$_highlevel_open_tcp_listeners->m_frame.f_lineno = 3;
        tmp_assign_source_5 = IMPORT_MODULE5(tstate, tmp_name_value_1, tmp_globals_arg_value_1, tmp_locals_arg_value_1, tmp_fromlist_value_1, tmp_level_value_1);
        if (tmp_assign_source_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 3;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[16], tmp_assign_source_5);
    }
    {
        PyObject *tmp_assign_source_6;
        tmp_assign_source_6 = IMPORT_HARD_SYS();
        assert(!(tmp_assign_source_6 == NULL));
        UPDATE_STRING_DICT0(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[47], tmp_assign_source_6);
    }
    {
        PyObject *tmp_assign_source_7;
        tmp_assign_source_7 = Py_False;
        UPDATE_STRING_DICT0(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[48], tmp_assign_source_7);
    }
    {
        PyObject *tmp_assign_source_8;
        PyObject *tmp_name_value_2;
        PyObject *tmp_globals_arg_value_2;
        PyObject *tmp_locals_arg_value_2;
        PyObject *tmp_fromlist_value_2;
        PyObject *tmp_level_value_2;
        tmp_name_value_2 = mod_consts[27];
        tmp_globals_arg_value_2 = (PyObject *)moduledict_trio$_highlevel_open_tcp_listeners;
        tmp_locals_arg_value_2 = Py_None;
        tmp_fromlist_value_2 = Py_None;
        tmp_level_value_2 = const_int_0;
        frame_frame_trio$_highlevel_open_tcp_listeners->m_frame.f_lineno = 7;
        tmp_assign_source_8 = IMPORT_MODULE5(tstate, tmp_name_value_2, tmp_globals_arg_value_2, tmp_locals_arg_value_2, tmp_fromlist_value_2, tmp_level_value_2);
        if (tmp_assign_source_8 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 7;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[27], tmp_assign_source_8);
    }
    {
        PyObject *tmp_assign_source_9;
        PyObject *tmp_import_name_from_1;
        PyObject *tmp_name_value_3;
        PyObject *tmp_globals_arg_value_3;
        PyObject *tmp_locals_arg_value_3;
        PyObject *tmp_fromlist_value_3;
        PyObject *tmp_level_value_3;
        tmp_name_value_3 = mod_consts[27];
        tmp_globals_arg_value_3 = (PyObject *)moduledict_trio$_highlevel_open_tcp_listeners;
        tmp_locals_arg_value_3 = Py_None;
        tmp_fromlist_value_3 = mod_consts[49];
        tmp_level_value_3 = const_int_0;
        frame_frame_trio$_highlevel_open_tcp_listeners->m_frame.f_lineno = 8;
        tmp_import_name_from_1 = IMPORT_MODULE5(tstate, tmp_name_value_3, tmp_globals_arg_value_3, tmp_locals_arg_value_3, tmp_fromlist_value_3, tmp_level_value_3);
        if (tmp_import_name_from_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 8;

            goto frame_exception_exit_1;
        }
        if (PyModule_Check(tmp_import_name_from_1)) {
            tmp_assign_source_9 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_1,
                (PyObject *)moduledict_trio$_highlevel_open_tcp_listeners,
                mod_consts[50],
                const_int_0
            );
        } else {
            tmp_assign_source_9 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_1, mod_consts[50]);
        }

        Py_DECREF(tmp_import_name_from_1);
        if (tmp_assign_source_9 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 8;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[50], tmp_assign_source_9);
    }
    {
        PyObject *tmp_assign_source_10;
        PyObject *tmp_import_name_from_2;
        PyObject *tmp_name_value_4;
        PyObject *tmp_globals_arg_value_4;
        PyObject *tmp_locals_arg_value_4;
        PyObject *tmp_fromlist_value_4;
        PyObject *tmp_level_value_4;
        tmp_name_value_4 = mod_consts[1];
        tmp_globals_arg_value_4 = (PyObject *)moduledict_trio$_highlevel_open_tcp_listeners;
        tmp_locals_arg_value_4 = Py_None;
        tmp_fromlist_value_4 = mod_consts[51];
        tmp_level_value_4 = const_int_pos_1;
        frame_frame_trio$_highlevel_open_tcp_listeners->m_frame.f_lineno = 10;
        tmp_import_name_from_2 = IMPORT_MODULE5(tstate, tmp_name_value_4, tmp_globals_arg_value_4, tmp_locals_arg_value_4, tmp_fromlist_value_4, tmp_level_value_4);
        if (tmp_import_name_from_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 10;

            goto frame_exception_exit_1;
        }
        if (PyModule_Check(tmp_import_name_from_2)) {
            tmp_assign_source_10 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_2,
                (PyObject *)moduledict_trio$_highlevel_open_tcp_listeners,
                mod_consts[15],
                const_int_0
            );
        } else {
            tmp_assign_source_10 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_2, mod_consts[15]);
        }

        Py_DECREF(tmp_import_name_from_2);
        if (tmp_assign_source_10 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 10;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[9], tmp_assign_source_10);
    }
    {
        PyObject *tmp_assign_source_11;
        PyObject *tmp_import_name_from_3;
        PyObject *tmp_name_value_5;
        PyObject *tmp_globals_arg_value_5;
        PyObject *tmp_locals_arg_value_5;
        PyObject *tmp_fromlist_value_5;
        PyObject *tmp_level_value_5;
        tmp_name_value_5 = mod_consts[52];
        tmp_globals_arg_value_5 = (PyObject *)moduledict_trio$_highlevel_open_tcp_listeners;
        tmp_locals_arg_value_5 = Py_None;
        tmp_fromlist_value_5 = mod_consts[53];
        tmp_level_value_5 = const_int_0;
        frame_frame_trio$_highlevel_open_tcp_listeners->m_frame.f_lineno = 16;
        tmp_import_name_from_3 = IMPORT_MODULE5(tstate, tmp_name_value_5, tmp_globals_arg_value_5, tmp_locals_arg_value_5, tmp_fromlist_value_5, tmp_level_value_5);
        if (tmp_import_name_from_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 16;

            goto frame_exception_exit_1;
        }
        if (PyModule_Check(tmp_import_name_from_3)) {
            tmp_assign_source_11 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_3,
                (PyObject *)moduledict_trio$_highlevel_open_tcp_listeners,
                mod_consts[31],
                const_int_0
            );
        } else {
            tmp_assign_source_11 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_3, mod_consts[31]);
        }

        Py_DECREF(tmp_import_name_from_3);
        if (tmp_assign_source_11 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 16;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[31], tmp_assign_source_11);
    }
    {
        PyObject *tmp_assign_source_12;
        PyObject *tmp_annotations_1;
        tmp_annotations_1 = DICT_COPY(tstate, mod_consts[54]);


        tmp_assign_source_12 = MAKE_FUNCTION_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__1__compute_backlog(tstate, tmp_annotations_1);

        UPDATE_STRING_DICT1(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[7], tmp_assign_source_12);
    }
    {
        PyObject *tmp_assign_source_13;
        PyObject *tmp_kw_defaults_1;
        PyObject *tmp_annotations_2;
        tmp_kw_defaults_1 = DICT_COPY(tstate, mod_consts[55]);
        tmp_annotations_2 = DICT_COPY(tstate, mod_consts[56]);


        tmp_assign_source_13 = MAKE_FUNCTION_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__2_open_tcp_listeners(tstate, tmp_kw_defaults_1, tmp_annotations_2);

        UPDATE_STRING_DICT1(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[32], tmp_assign_source_13);
    }
    {
        PyObject *tmp_assign_source_14;
        PyObject *tmp_kw_defaults_2;
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        PyObject *tmp_annotations_3;
        tmp_dict_key_1 = mod_consts[11];
        tmp_dict_value_1 = Py_None;
        tmp_kw_defaults_2 = _PyDict_NewPresized( 4 );
        {
            PyObject *tmp_expression_value_1;
            tmp_res = PyDict_SetItem(tmp_kw_defaults_2, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[8];
            tmp_dict_value_1 = Py_None;
            tmp_res = PyDict_SetItem(tmp_kw_defaults_2, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[37];
            tmp_dict_value_1 = Py_None;
            tmp_res = PyDict_SetItem(tmp_kw_defaults_2, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[38];
            tmp_expression_value_1 = module_var_accessor_trio$$36$_highlevel_open_tcp_listeners$trio(tstate);
            if (unlikely(tmp_expression_value_1 == NULL)) {
                RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[27]);
            }

            if (tmp_expression_value_1 == NULL) {
                assert(HAS_EXCEPTION_STATE(&exception_state));



                exception_lineno = 179;

                goto dict_build_exception_1;
            }
            tmp_dict_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[57]);
            if (tmp_dict_value_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 179;

                goto dict_build_exception_1;
            }
            tmp_res = PyDict_SetItem(tmp_kw_defaults_2, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
        }
        goto dict_build_noexception_1;
        // Exception handling pass through code for dict_build:
        dict_build_exception_1:;
        Py_DECREF(tmp_kw_defaults_2);
        goto frame_exception_exit_1;
        // Finished with no exception for dict_build:
        dict_build_noexception_1:;
        tmp_annotations_3 = DICT_COPY(tstate, mod_consts[58]);


        tmp_assign_source_14 = MAKE_FUNCTION_trio$_highlevel_open_tcp_listeners$$36$$$36$$$36$function__3_serve_tcp(tstate, tmp_kw_defaults_2, tmp_annotations_3);

        UPDATE_STRING_DICT1(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)mod_consts[40], tmp_assign_source_14);
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_trio$_highlevel_open_tcp_listeners, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_trio$_highlevel_open_tcp_listeners->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_trio$_highlevel_open_tcp_listeners, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }



    assertFrameObject(frame_frame_trio$_highlevel_open_tcp_listeners);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto module_exception_exit;
    frame_no_exception_1:;

    // Report to PGO about leaving the module without error.
    PGO_onModuleExit("trio$_highlevel_open_tcp_listeners", false);

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *post_load = IMPORT_EMBEDDED_MODULE(tstate, "trio._highlevel_open_tcp_listeners" "-postLoad");
        if (post_load == NULL) {
            return NULL;
        }
    }
#endif

    Py_INCREF(module_trio$_highlevel_open_tcp_listeners);
    return module_trio$_highlevel_open_tcp_listeners;
    module_exception_exit:

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_trio$_highlevel_open_tcp_listeners, (Nuitka_StringObject *)const_str_plain___name__);

        if (module_name != NULL) {
            Nuitka_DelModule(tstate, module_name);
        }
    }
#endif
    PGO_onModuleExit("trio$_highlevel_open_tcp_listeners", false);

    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);
    return NULL;
}
