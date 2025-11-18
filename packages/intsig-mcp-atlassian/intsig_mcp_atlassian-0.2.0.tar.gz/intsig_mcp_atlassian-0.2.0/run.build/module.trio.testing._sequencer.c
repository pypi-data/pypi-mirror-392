/* Generated code for Python module 'trio$testing$_sequencer'
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

/* The "module_trio$testing$_sequencer" is a Python object pointer of module type.
 *
 * Note: For full compatibility with CPython, every module variable access
 * needs to go through it except for cases where the module cannot possibly
 * have changed in the mean time.
 */

PyObject *module_trio$testing$_sequencer;
PyDictObject *moduledict_trio$testing$_sequencer;

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
        loadConstantsBlob(tstate, &mod_consts[0], UN_TRANSLATE("trio.testing._sequencer"));
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
void checkModuleConstants_trio$testing$_sequencer(PyThreadState *tstate) {
    // The module may not have been used at all, then ignore this.
    if (constants_created == false) return;

    for (int i = 0; i < 60; i++) {
        assert(mod_consts_hash[i] == DEEP_HASH(tstate, mod_consts[i]));
        CHECK_OBJECT_DEEP(mod_consts[i]);
    }
}
#endif

// Helper to preserving module variables for Python3.11+
#if 7
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
static PyObject *module_var_accessor_trio$$36$testing$$36$_sequencer$Event(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_trio$testing$_sequencer->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_trio$testing$_sequencer->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[1]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_trio$testing$_sequencer->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[1]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[1], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[1]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[1], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[1]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[1]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[1]);
    }

    return result;
}

static PyObject *module_var_accessor_trio$$36$testing$$36$_sequencer$__spec__(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_trio$testing$_sequencer->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_trio$testing$_sequencer->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[59]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_trio$testing$_sequencer->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[59]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[59]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[59]);
    }

    return result;
}

static PyObject *module_var_accessor_trio$$36$testing$$36$_sequencer$_core(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_trio$testing$_sequencer->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_trio$testing$_sequencer->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[12]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_trio$testing$_sequencer->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[12]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[12], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[12]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[12], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[12]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[12]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[12]);
    }

    return result;
}

static PyObject *module_var_accessor_trio$$36$testing$$36$_sequencer$_util(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_trio$testing$_sequencer->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_trio$testing$_sequencer->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[34]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_trio$testing$_sequencer->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[34]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[34], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[34]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[34], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[34]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[34]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[34]);
    }

    return result;
}

static PyObject *module_var_accessor_trio$$36$testing$$36$_sequencer$asynccontextmanager(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_trio$testing$_sequencer->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_trio$testing$_sequencer->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[29]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_trio$testing$_sequencer->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[29]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[29], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[29]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[29], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[29]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[29]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[29]);
    }

    return result;
}

static PyObject *module_var_accessor_trio$$36$testing$$36$_sequencer$attrs(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_trio$testing$_sequencer->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_trio$testing$_sequencer->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[31]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_trio$testing$_sequencer->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[31]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[31]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[31]);
    }

    return result;
}

static PyObject *module_var_accessor_trio$$36$testing$$36$_sequencer$defaultdict(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_trio$testing$_sequencer->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_trio$testing$_sequencer->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[0]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_trio$testing$_sequencer->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[0]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[0], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[0]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[0], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[0]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[0]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[0]);
    }

    return result;
}


#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
// The module code objects.
static PyCodeObject *code_objects_63ca4e1d511490d410b8a90b722f3b19;
static PyCodeObject *code_objects_09fbf08013f985798a450601ba78f3c5;
static PyCodeObject *code_objects_67714a9ecd1b6f78db6bfd493b6bcfc5;
static PyCodeObject *code_objects_836958794e8a5c7f9da729db0f83a408;

static void createModuleCodeObjects(void) {
    module_filename_obj = MAKE_RELATIVE_PATH(mod_consts[55]); CHECK_OBJECT(module_filename_obj);
    code_objects_63ca4e1d511490d410b8a90b722f3b19 = MAKE_CODE_OBJECT(module_filename_obj, 58, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[46], mod_consts[47], NULL, NULL, 0, 0, 0);
    code_objects_09fbf08013f985798a450601ba78f3c5 = MAKE_CODE_OBJECT(module_filename_obj, 1, CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[56], mod_consts[56], NULL, NULL, 0, 0, 0);
    code_objects_67714a9ecd1b6f78db6bfd493b6bcfc5 = MAKE_CODE_OBJECT(module_filename_obj, 17, CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[42], mod_consts[42], mod_consts[57], NULL, 0, 0, 0);
    code_objects_836958794e8a5c7f9da729db0f83a408 = MAKE_CODE_OBJECT(module_filename_obj, 65, CO_ASYNC_GENERATOR | CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[17], mod_consts[18], mod_consts[58], NULL, 2, 0, 0);
}
#endif

// The module function declarations.
static PyObject *MAKE_ASYNCGEN_trio$testing$_sequencer$$36$$$36$$$36$function__2___call__$$36$$$36$$$36$asyncgen__1___call__(PyThreadState *tstate, struct Nuitka_CellObject **closure);


static PyObject *MAKE_FUNCTION_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_trio$testing$_sequencer$$36$$$36$$$36$function__2___call__(PyThreadState *tstate, PyObject *annotations);


// The module function definitions.
static PyObject *impl_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    struct Nuitka_FrameObject *frame_frame_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda)) {
        Py_XDECREF(cache_frame_frame_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda = MAKE_FUNCTION_FRAME(tstate, code_objects_63ca4e1d511490d410b8a90b722f3b19, module_trio$testing$_sequencer, 0);
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda->m_type_description == NULL);
    frame_frame_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda = cache_frame_frame_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda);
    assert(Py_REFCNT(frame_frame_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        tmp_called_value_1 = module_var_accessor_trio$$36$testing$$36$_sequencer$defaultdict(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[0]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 58;

            goto frame_exception_exit_1;
        }
        tmp_args_element_value_1 = module_var_accessor_trio$$36$testing$$36$_sequencer$Event(tstate);
        if (unlikely(tmp_args_element_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[1]);
        }

        if (tmp_args_element_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 58;

            goto frame_exception_exit_1;
        }
        frame_frame_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda->m_frame.f_lineno = 58;
        tmp_return_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_1, tmp_args_element_value_1);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 58;

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
            exception_tb = MAKE_TRACEBACK(frame_frame_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda,
        type_description_1
    );


    // Release cached frame if used for exception.
    if (frame_frame_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda == cache_frame_frame_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda);
        cache_frame_frame_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda = NULL;
    }

    assertFrameObject(frame_frame_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

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


static PyObject *impl_trio$testing$_sequencer$$36$$$36$$$36$function__2___call__(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    struct Nuitka_CellObject *par_self = Nuitka_Cell_New1(python_pars[0]);
    struct Nuitka_CellObject *par_position = Nuitka_Cell_New1(python_pars[1]);
    PyObject *tmp_return_value = NULL;

    // Actual function body.
    {
        struct Nuitka_CellObject *tmp_closure_1[2];

        tmp_closure_1[0] = par_position;
        Py_INCREF(tmp_closure_1[0]);
        tmp_closure_1[1] = par_self;
        Py_INCREF(tmp_closure_1[1]);

        tmp_return_value = MAKE_ASYNCGEN_trio$testing$_sequencer$$36$$$36$$$36$function__2___call__$$36$$$36$$$36$asyncgen__1___call__(tstate, tmp_closure_1);

        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_OBJECT(par_position);
    Py_DECREF(par_position);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}



#if 1
struct trio$testing$_sequencer$$36$$$36$$$36$function__2___call__$$36$$$36$$$36$asyncgen__1___call___locals {
    PyObject *var_event;
    PyObject *tmp_for_loop_1__for_iterator;
    PyObject *tmp_for_loop_1__iter_value;
    char const *type_description_1;
    struct Nuitka_ExceptionPreservationItem exception_state;
    int exception_lineno;
    int tmp_res;
    char yield_tmps[1024];
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    int exception_keeper_lineno_1;
    struct Nuitka_ExceptionStackItem exception_preserved_1;
    bool tmp_result;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_2;
    int exception_keeper_lineno_2;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_3;
    int exception_keeper_lineno_3;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_4;
    int exception_keeper_lineno_4;
    struct Nuitka_ExceptionStackItem exception_preserved_2;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_5;
    int exception_keeper_lineno_5;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_6;
    int exception_keeper_lineno_6;
};
#endif

static PyObject *trio$testing$_sequencer$$36$$$36$$$36$function__2___call__$$36$$$36$$$36$asyncgen__1___call___context(PyThreadState *tstate, struct Nuitka_AsyncgenObject *asyncgen, PyObject *yield_return_value) {
    CHECK_OBJECT(asyncgen);
    assert(Nuitka_Asyncgen_Check((PyObject *)asyncgen));
    CHECK_OBJECT_X(yield_return_value);

#if 1
    // Heap access.
    struct trio$testing$_sequencer$$36$$$36$$$36$function__2___call__$$36$$$36$$$36$asyncgen__1___call___locals *asyncgen_heap = (struct trio$testing$_sequencer$$36$$$36$$$36$function__2___call__$$36$$$36$$$36$asyncgen__1___call___locals *)asyncgen->m_heap_storage;
#endif

    // Dispatch to yield based on return label index:
    switch(asyncgen->m_yield_return_index) {
    case 2: goto yield_return_2;
    case 1: goto yield_return_1;
    }

    // Local variable initialization
    NUITKA_MAY_BE_UNUSED nuitka_void tmp_unused;
    static struct Nuitka_FrameObject *cache_m_frame = NULL;
    asyncgen_heap->var_event = NULL;
    asyncgen_heap->tmp_for_loop_1__for_iterator = NULL;
    asyncgen_heap->tmp_for_loop_1__iter_value = NULL;
    asyncgen_heap->type_description_1 = NULL;
    asyncgen_heap->exception_state = Empty_Nuitka_ExceptionPreservationItem;
    asyncgen_heap->exception_lineno = 0;

    // Actual asyncgen body.
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
        cache_m_frame = MAKE_FUNCTION_FRAME(tstate, code_objects_836958794e8a5c7f9da729db0f83a408, module_trio$testing$_sequencer, sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_m_frame->m_type_description == NULL);
    asyncgen->m_frame = cache_m_frame;
    // Mark the frame object as in use, ref count 1 will be up for reuse.
    Py_INCREF(asyncgen->m_frame);
    assert(Py_REFCNT(asyncgen->m_frame) == 2); // Frame stack

    Nuitka_SetFrameGenerator(asyncgen->m_frame, (PyObject *)asyncgen);

    assert(asyncgen->m_frame->m_frame.f_back == NULL);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackGeneratorCompiledFrame(tstate, asyncgen->m_frame);
    assert(Py_REFCNT(asyncgen->m_frame) == 2);

    // Store currently existing exception as the one to publish again when we
    // yield or yield from.
    STORE_ASYNCGEN_EXCEPTION(tstate, asyncgen);

    // Framed code:
    {
        bool tmp_condition_result_1;
        PyObject *tmp_cmp_expr_left_1;
        PyObject *tmp_cmp_expr_right_1;
        PyObject *tmp_expression_value_1;
        if (Nuitka_Cell_GET(asyncgen->m_closure[0]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &asyncgen_heap->exception_state, mod_consts[2]);
            NORMALIZE_EXCEPTION_STATE(tstate, &asyncgen_heap->exception_state);
            CHAIN_EXCEPTION(tstate, asyncgen_heap->exception_state.exception_value);

            asyncgen_heap->exception_lineno = 66;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }

        tmp_cmp_expr_left_1 = Nuitka_Cell_GET(asyncgen->m_closure[0]);
        if (Nuitka_Cell_GET(asyncgen->m_closure[1]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &asyncgen_heap->exception_state, mod_consts[3]);
            NORMALIZE_EXCEPTION_STATE(tstate, &asyncgen_heap->exception_state);
            CHAIN_EXCEPTION(tstate, asyncgen_heap->exception_state.exception_value);

            asyncgen_heap->exception_lineno = 66;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }

        tmp_expression_value_1 = Nuitka_Cell_GET(asyncgen->m_closure[1]);
        tmp_cmp_expr_right_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[4]);
        if (tmp_cmp_expr_right_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 66;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }
        asyncgen_heap->tmp_res = PySequence_Contains(tmp_cmp_expr_right_1, tmp_cmp_expr_left_1);
        Py_DECREF(tmp_cmp_expr_right_1);
        if (asyncgen_heap->tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 66;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_1 = (asyncgen_heap->tmp_res == 1) ? true : false;
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
        tmp_tuple_element_1 = mod_consts[5];
        tmp_string_concat_values_1 = MAKE_TUPLE_EMPTY(tstate, 2);
        {
            PyObject *tmp_format_value_1;
            PyObject *tmp_format_spec_1;
            PyTuple_SET_ITEM0(tmp_string_concat_values_1, 0, tmp_tuple_element_1);
            if (Nuitka_Cell_GET(asyncgen->m_closure[0]) == NULL) {

                FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &asyncgen_heap->exception_state, mod_consts[2]);
                NORMALIZE_EXCEPTION_STATE(tstate, &asyncgen_heap->exception_state);
                CHAIN_EXCEPTION(tstate, asyncgen_heap->exception_state.exception_value);

                asyncgen_heap->exception_lineno = 67;
                asyncgen_heap->type_description_1 = "cco";
                goto tuple_build_exception_1;
            }

            tmp_format_value_1 = Nuitka_Cell_GET(asyncgen->m_closure[0]);
            tmp_format_spec_1 = mod_consts[6];
            tmp_tuple_element_1 = BUILTIN_FORMAT(tstate, tmp_format_value_1, tmp_format_spec_1);
            if (tmp_tuple_element_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


                asyncgen_heap->exception_lineno = 67;
                asyncgen_heap->type_description_1 = "cco";
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
        tmp_make_exception_arg_1 = PyUnicode_Join(mod_consts[6], tmp_string_concat_values_1);
        Py_DECREF(tmp_string_concat_values_1);
        if (tmp_make_exception_arg_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 67;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }
        asyncgen->m_frame->m_frame.f_lineno = 67;
        tmp_raise_type_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_RuntimeError, tmp_make_exception_arg_1);
        Py_DECREF(tmp_make_exception_arg_1);
        assert(!(tmp_raise_type_1 == NULL));
        asyncgen_heap->exception_state.exception_type = tmp_raise_type_1;
        asyncgen_heap->exception_lineno = 67;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &asyncgen_heap->exception_state);
        asyncgen_heap->type_description_1 = "cco";
        goto frame_exception_exit_1;
    }
    branch_no_1:;
    {
        nuitka_bool tmp_condition_result_2;
        PyObject *tmp_expression_value_2;
        PyObject *tmp_attribute_value_1;
        int tmp_truth_name_1;
        if (Nuitka_Cell_GET(asyncgen->m_closure[1]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &asyncgen_heap->exception_state, mod_consts[3]);
            NORMALIZE_EXCEPTION_STATE(tstate, &asyncgen_heap->exception_state);
            CHAIN_EXCEPTION(tstate, asyncgen_heap->exception_state.exception_value);

            asyncgen_heap->exception_lineno = 68;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }

        tmp_expression_value_2 = Nuitka_Cell_GET(asyncgen->m_closure[1]);
        tmp_attribute_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_2, mod_consts[7]);
        if (tmp_attribute_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 68;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }
        tmp_truth_name_1 = CHECK_IF_TRUE(tmp_attribute_value_1);
        if (tmp_truth_name_1 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);
            Py_DECREF(tmp_attribute_value_1);

            asyncgen_heap->exception_lineno = 68;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_2 = tmp_truth_name_1 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        Py_DECREF(tmp_attribute_value_1);
        if (tmp_condition_result_2 == NUITKA_BOOL_TRUE) {
            goto branch_yes_2;
        } else {
            goto branch_no_2;
        }
    }
    branch_yes_2:;
    {
        PyObject *tmp_raise_type_2;
        PyObject *tmp_make_exception_arg_2;
        tmp_make_exception_arg_2 = mod_consts[8];
        asyncgen->m_frame->m_frame.f_lineno = 69;
        tmp_raise_type_2 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_RuntimeError, tmp_make_exception_arg_2);
        assert(!(tmp_raise_type_2 == NULL));
        asyncgen_heap->exception_state.exception_type = tmp_raise_type_2;
        asyncgen_heap->exception_lineno = 69;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &asyncgen_heap->exception_state);
        asyncgen_heap->type_description_1 = "cco";
        goto frame_exception_exit_1;
    }
    branch_no_2:;
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_expression_value_3;
        PyObject *tmp_expression_value_4;
        PyObject *tmp_call_result_1;
        PyObject *tmp_args_element_value_1;
        if (Nuitka_Cell_GET(asyncgen->m_closure[1]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &asyncgen_heap->exception_state, mod_consts[3]);
            NORMALIZE_EXCEPTION_STATE(tstate, &asyncgen_heap->exception_state);
            CHAIN_EXCEPTION(tstate, asyncgen_heap->exception_state.exception_value);

            asyncgen_heap->exception_lineno = 70;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }

        tmp_expression_value_4 = Nuitka_Cell_GET(asyncgen->m_closure[1]);
        tmp_expression_value_3 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_4, mod_consts[4]);
        if (tmp_expression_value_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 70;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }
        tmp_called_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_3, mod_consts[9]);
        Py_DECREF(tmp_expression_value_3);
        if (tmp_called_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 70;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }
        if (Nuitka_Cell_GET(asyncgen->m_closure[0]) == NULL) {
            Py_DECREF(tmp_called_value_1);
            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &asyncgen_heap->exception_state, mod_consts[2]);
            NORMALIZE_EXCEPTION_STATE(tstate, &asyncgen_heap->exception_state);
            CHAIN_EXCEPTION(tstate, asyncgen_heap->exception_state.exception_value);

            asyncgen_heap->exception_lineno = 70;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }

        tmp_args_element_value_1 = Nuitka_Cell_GET(asyncgen->m_closure[0]);
        asyncgen->m_frame->m_frame.f_lineno = 70;
        tmp_call_result_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_1, tmp_args_element_value_1);
        Py_DECREF(tmp_called_value_1);
        if (tmp_call_result_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 70;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_1);
    }
    {
        nuitka_bool tmp_condition_result_3;
        PyObject *tmp_cmp_expr_left_2;
        PyObject *tmp_cmp_expr_right_2;
        if (Nuitka_Cell_GET(asyncgen->m_closure[0]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &asyncgen_heap->exception_state, mod_consts[2]);
            NORMALIZE_EXCEPTION_STATE(tstate, &asyncgen_heap->exception_state);
            CHAIN_EXCEPTION(tstate, asyncgen_heap->exception_state.exception_value);

            asyncgen_heap->exception_lineno = 71;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }

        tmp_cmp_expr_left_2 = Nuitka_Cell_GET(asyncgen->m_closure[0]);
        tmp_cmp_expr_right_2 = const_int_0;
        tmp_condition_result_3 = RICH_COMPARE_NE_NBOOL_OBJECT_LONG(tmp_cmp_expr_left_2, tmp_cmp_expr_right_2);
        if (tmp_condition_result_3 == NUITKA_BOOL_EXCEPTION) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 71;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }
        if (tmp_condition_result_3 == NUITKA_BOOL_TRUE) {
            goto branch_yes_3;
        } else {
            goto branch_no_3;
        }
    }
    branch_yes_3:;
    // Tried code:
    {
        PyObject *tmp_expression_value_5;
        PyObject *tmp_expression_value_6;
        PyObject *tmp_called_instance_1;
        PyObject *tmp_expression_value_7;
        PyObject *tmp_expression_value_8;
        PyObject *tmp_subscript_value_1;
        PyObject *tmp_await_result_1;
        asyncgen->m_frame->m_frame.f_lineno = 73;
        if (Nuitka_Cell_GET(asyncgen->m_closure[1]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &asyncgen_heap->exception_state, mod_consts[3]);
            NORMALIZE_EXCEPTION_STATE(tstate, &asyncgen_heap->exception_state);
            CHAIN_EXCEPTION(tstate, asyncgen_heap->exception_state.exception_value);

            asyncgen_heap->exception_lineno = 73;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_2;
        }

        tmp_expression_value_8 = Nuitka_Cell_GET(asyncgen->m_closure[1]);
        tmp_expression_value_7 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_8, mod_consts[10]);
        if (tmp_expression_value_7 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 73;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_2;
        }
        if (Nuitka_Cell_GET(asyncgen->m_closure[0]) == NULL) {
            Py_DECREF(tmp_expression_value_7);
            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &asyncgen_heap->exception_state, mod_consts[2]);
            NORMALIZE_EXCEPTION_STATE(tstate, &asyncgen_heap->exception_state);
            CHAIN_EXCEPTION(tstate, asyncgen_heap->exception_state.exception_value);

            asyncgen_heap->exception_lineno = 73;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_2;
        }

        tmp_subscript_value_1 = Nuitka_Cell_GET(asyncgen->m_closure[0]);
        tmp_called_instance_1 = LOOKUP_SUBSCRIPT(tstate, tmp_expression_value_7, tmp_subscript_value_1);
        Py_DECREF(tmp_expression_value_7);
        if (tmp_called_instance_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 73;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_2;
        }
        asyncgen->m_frame->m_frame.f_lineno = 73;
        tmp_expression_value_6 = CALL_METHOD_NO_ARGS(tstate, tmp_called_instance_1, mod_consts[11]);
        Py_DECREF(tmp_called_instance_1);
        if (tmp_expression_value_6 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 73;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_2;
        }
        tmp_expression_value_5 = ASYNC_AWAIT(tstate, tmp_expression_value_6, await_normal);
        Py_DECREF(tmp_expression_value_6);
        if (tmp_expression_value_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 73;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_2;
        }
        Nuitka_PreserveHeap(asyncgen_heap->yield_tmps, &tmp_expression_value_6, sizeof(PyObject *), &tmp_called_instance_1, sizeof(PyObject *), &tmp_expression_value_7, sizeof(PyObject *), &tmp_expression_value_8, sizeof(PyObject *), &tmp_subscript_value_1, sizeof(PyObject *), NULL);
        asyncgen->m_yield_return_index = 1;
        asyncgen->m_yield_from = tmp_expression_value_5;
        asyncgen->m_awaiting = true;
        return NULL;

        yield_return_1:
        Nuitka_RestoreHeap(asyncgen_heap->yield_tmps, &tmp_expression_value_6, sizeof(PyObject *), &tmp_called_instance_1, sizeof(PyObject *), &tmp_expression_value_7, sizeof(PyObject *), &tmp_expression_value_8, sizeof(PyObject *), &tmp_subscript_value_1, sizeof(PyObject *), NULL);
        asyncgen->m_awaiting = false;

        if (yield_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 73;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_2;
        }
        tmp_await_result_1 = yield_return_value;
        Py_DECREF(tmp_await_result_1);
    }
    goto try_end_1;
    // Exception handler code:
    try_except_handler_2:;
    asyncgen_heap->exception_keeper_lineno_1 = asyncgen_heap->exception_lineno;
    asyncgen_heap->exception_lineno = 0;
    asyncgen_heap->exception_keeper_name_1 = asyncgen_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&asyncgen_heap->exception_state);

    // Preserve existing published exception id 1.
    asyncgen_heap->exception_preserved_1 = GET_CURRENT_EXCEPTION(tstate);

    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&asyncgen_heap->exception_keeper_name_1);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(asyncgen->m_frame, asyncgen_heap->exception_keeper_lineno_1);
            SET_EXCEPTION_STATE_TRACEBACK(&asyncgen_heap->exception_keeper_name_1, exception_tb);
        } else if (asyncgen_heap->exception_keeper_lineno_1 != 0) {
            exception_tb = ADD_TRACEBACK(exception_tb, asyncgen->m_frame, asyncgen_heap->exception_keeper_lineno_1);
            SET_EXCEPTION_STATE_TRACEBACK(&asyncgen_heap->exception_keeper_name_1, exception_tb);
        }
    }

    PUBLISH_CURRENT_EXCEPTION(tstate, &asyncgen_heap->exception_keeper_name_1);
    // Tried code:
    {
        bool tmp_condition_result_4;
        PyObject *tmp_cmp_expr_left_3;
        PyObject *tmp_cmp_expr_right_3;
        PyObject *tmp_expression_value_9;
        tmp_cmp_expr_left_3 = EXC_TYPE(tstate);
        tmp_expression_value_9 = module_var_accessor_trio$$36$testing$$36$_sequencer$_core(tstate);
        if (unlikely(tmp_expression_value_9 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &asyncgen_heap->exception_state, mod_consts[12]);
        }

        if (tmp_expression_value_9 == NULL) {
            assert(HAS_EXCEPTION_STATE(&asyncgen_heap->exception_state));



            asyncgen_heap->exception_lineno = 74;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_3;
        }
        tmp_cmp_expr_right_3 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_9, mod_consts[13]);
        if (tmp_cmp_expr_right_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 74;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_3;
        }
        asyncgen_heap->tmp_res = EXCEPTION_MATCH_BOOL(tstate, tmp_cmp_expr_left_3, tmp_cmp_expr_right_3);
        Py_DECREF(tmp_cmp_expr_right_3);
        if (asyncgen_heap->tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 74;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_3;
        }
        tmp_condition_result_4 = (asyncgen_heap->tmp_res != 0) ? true : false;
        if (tmp_condition_result_4 != false) {
            goto branch_yes_4;
        } else {
            goto branch_no_4;
        }
    }
    branch_yes_4:;
    {
        PyObject *tmp_assattr_value_1;
        PyObject *tmp_assattr_target_1;
        tmp_assattr_value_1 = Py_True;
        if (Nuitka_Cell_GET(asyncgen->m_closure[1]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &asyncgen_heap->exception_state, mod_consts[3]);
            NORMALIZE_EXCEPTION_STATE(tstate, &asyncgen_heap->exception_state);
            CHAIN_EXCEPTION(tstate, asyncgen_heap->exception_state.exception_value);

            asyncgen_heap->exception_lineno = 75;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_3;
        }

        tmp_assattr_target_1 = Nuitka_Cell_GET(asyncgen->m_closure[1]);
        asyncgen_heap->tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_1, mod_consts[7], tmp_assattr_value_1);
        if (asyncgen_heap->tmp_result == false) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 75;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_3;
        }
    }
    {
        PyObject *tmp_assign_source_1;
        PyObject *tmp_iter_arg_1;
        PyObject *tmp_called_value_2;
        PyObject *tmp_expression_value_10;
        PyObject *tmp_expression_value_11;
        if (Nuitka_Cell_GET(asyncgen->m_closure[1]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &asyncgen_heap->exception_state, mod_consts[3]);
            NORMALIZE_EXCEPTION_STATE(tstate, &asyncgen_heap->exception_state);
            CHAIN_EXCEPTION(tstate, asyncgen_heap->exception_state.exception_value);

            asyncgen_heap->exception_lineno = 76;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_3;
        }

        tmp_expression_value_11 = Nuitka_Cell_GET(asyncgen->m_closure[1]);
        tmp_expression_value_10 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_11, mod_consts[10]);
        if (tmp_expression_value_10 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 76;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_3;
        }
        tmp_called_value_2 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_10, mod_consts[14]);
        Py_DECREF(tmp_expression_value_10);
        if (tmp_called_value_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 76;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_3;
        }
        asyncgen->m_frame->m_frame.f_lineno = 76;
        tmp_iter_arg_1 = CALL_FUNCTION_NO_ARGS(tstate, tmp_called_value_2);
        Py_DECREF(tmp_called_value_2);
        if (tmp_iter_arg_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 76;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_3;
        }
        tmp_assign_source_1 = MAKE_ITERATOR(tstate, tmp_iter_arg_1);
        Py_DECREF(tmp_iter_arg_1);
        if (tmp_assign_source_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 76;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_3;
        }
        assert(asyncgen_heap->tmp_for_loop_1__for_iterator == NULL);
        asyncgen_heap->tmp_for_loop_1__for_iterator = tmp_assign_source_1;
    }
    // Tried code:
    loop_start_1:;
    {
        PyObject *tmp_next_source_1;
        PyObject *tmp_assign_source_2;
        CHECK_OBJECT(asyncgen_heap->tmp_for_loop_1__for_iterator);
        tmp_next_source_1 = asyncgen_heap->tmp_for_loop_1__for_iterator;
        tmp_assign_source_2 = ITERATOR_NEXT(tmp_next_source_1);
        if (tmp_assign_source_2 == NULL) {
            if (CHECK_AND_CLEAR_STOP_ITERATION_OCCURRED(tstate)) {

                goto loop_end_1;
            } else {

                FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);
                asyncgen_heap->type_description_1 = "cco";
                asyncgen_heap->exception_lineno = 76;
                goto try_except_handler_4;
            }
        }

        {
            PyObject *old = asyncgen_heap->tmp_for_loop_1__iter_value;
            asyncgen_heap->tmp_for_loop_1__iter_value = tmp_assign_source_2;
            Py_XDECREF(old);
        }

    }
    {
        PyObject *tmp_assign_source_3;
        CHECK_OBJECT(asyncgen_heap->tmp_for_loop_1__iter_value);
        tmp_assign_source_3 = asyncgen_heap->tmp_for_loop_1__iter_value;
        {
            PyObject *old = asyncgen_heap->var_event;
            asyncgen_heap->var_event = tmp_assign_source_3;
            Py_INCREF(asyncgen_heap->var_event);
            Py_XDECREF(old);
        }

    }
    {
        PyObject *tmp_called_instance_2;
        PyObject *tmp_call_result_2;
        CHECK_OBJECT(asyncgen_heap->var_event);
        tmp_called_instance_2 = asyncgen_heap->var_event;
        asyncgen->m_frame->m_frame.f_lineno = 77;
        tmp_call_result_2 = CALL_METHOD_NO_ARGS(tstate, tmp_called_instance_2, mod_consts[15]);
        if (tmp_call_result_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 77;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_4;
        }
        Py_DECREF(tmp_call_result_2);
    }
    if (CONSIDER_THREADING(tstate) == false) {
        assert(HAS_ERROR_OCCURRED(tstate));

        FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


        asyncgen_heap->exception_lineno = 76;
        asyncgen_heap->type_description_1 = "cco";
        goto try_except_handler_4;
    }
    goto loop_start_1;
    loop_end_1:;
    goto try_end_2;
    // Exception handler code:
    try_except_handler_4:;
    asyncgen_heap->exception_keeper_lineno_2 = asyncgen_heap->exception_lineno;
    asyncgen_heap->exception_lineno = 0;
    asyncgen_heap->exception_keeper_name_2 = asyncgen_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&asyncgen_heap->exception_state);

    Py_XDECREF(asyncgen_heap->tmp_for_loop_1__iter_value);
    asyncgen_heap->tmp_for_loop_1__iter_value = NULL;
    CHECK_OBJECT(asyncgen_heap->tmp_for_loop_1__for_iterator);
    Py_DECREF(asyncgen_heap->tmp_for_loop_1__for_iterator);
    asyncgen_heap->tmp_for_loop_1__for_iterator = NULL;
    // Re-raise.
    asyncgen_heap->exception_state = asyncgen_heap->exception_keeper_name_2;
    asyncgen_heap->exception_lineno = asyncgen_heap->exception_keeper_lineno_2;

    goto try_except_handler_3;
    // End of try:
    try_end_2:;
    Py_XDECREF(asyncgen_heap->tmp_for_loop_1__iter_value);
    asyncgen_heap->tmp_for_loop_1__iter_value = NULL;
    CHECK_OBJECT(asyncgen_heap->tmp_for_loop_1__for_iterator);
    Py_DECREF(asyncgen_heap->tmp_for_loop_1__for_iterator);
    asyncgen_heap->tmp_for_loop_1__for_iterator = NULL;
    {
        PyObject *tmp_raise_type_3;
        PyObject *tmp_make_exception_arg_3;
        PyObject *tmp_raise_cause_1;
        tmp_make_exception_arg_3 = mod_consts[16];
        asyncgen->m_frame->m_frame.f_lineno = 78;
        tmp_raise_type_3 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_RuntimeError, tmp_make_exception_arg_3);
        assert(!(tmp_raise_type_3 == NULL));
        tmp_raise_cause_1 = Py_None;
        asyncgen_heap->exception_state.exception_type = tmp_raise_type_3;
        Py_INCREF(tmp_raise_cause_1);
        asyncgen_heap->exception_lineno = 80;
        RAISE_EXCEPTION_WITH_CAUSE(tstate, &asyncgen_heap->exception_state, tmp_raise_cause_1);
        asyncgen_heap->type_description_1 = "cco";
        goto try_except_handler_3;
    }
    goto branch_end_4;
    branch_no_4:;
    asyncgen_heap->tmp_result = RERAISE_EXCEPTION(tstate, &asyncgen_heap->exception_state);
    if (unlikely(asyncgen_heap->tmp_result == false)) {
        asyncgen_heap->exception_lineno = 72;
    }

    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&asyncgen_heap->exception_state);

        if ((exception_tb != NULL) && (exception_tb->tb_frame == &asyncgen->m_frame->m_frame)) {
            asyncgen->m_frame->m_frame.f_lineno = exception_tb->tb_lineno;
        }
    }
    asyncgen_heap->type_description_1 = "cco";
    goto try_except_handler_3;
    branch_end_4:;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Exception handler code:
    try_except_handler_3:;
    asyncgen_heap->exception_keeper_lineno_3 = asyncgen_heap->exception_lineno;
    asyncgen_heap->exception_lineno = 0;
    asyncgen_heap->exception_keeper_name_3 = asyncgen_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&asyncgen_heap->exception_state);

    // Restore previous exception id 1.
    SET_CURRENT_EXCEPTION(tstate, &asyncgen_heap->exception_preserved_1);

    // Re-raise.
    asyncgen_heap->exception_state = asyncgen_heap->exception_keeper_name_3;
    asyncgen_heap->exception_lineno = asyncgen_heap->exception_keeper_lineno_3;

    goto frame_exception_exit_1;
    // End of try:
    // End of try:
    try_end_1:;
    {
        nuitka_bool tmp_condition_result_5;
        PyObject *tmp_expression_value_12;
        PyObject *tmp_attribute_value_2;
        int tmp_truth_name_2;
        if (Nuitka_Cell_GET(asyncgen->m_closure[1]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &asyncgen_heap->exception_state, mod_consts[3]);
            NORMALIZE_EXCEPTION_STATE(tstate, &asyncgen_heap->exception_state);
            CHAIN_EXCEPTION(tstate, asyncgen_heap->exception_state.exception_value);

            asyncgen_heap->exception_lineno = 82;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }

        tmp_expression_value_12 = Nuitka_Cell_GET(asyncgen->m_closure[1]);
        tmp_attribute_value_2 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_12, mod_consts[7]);
        if (tmp_attribute_value_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 82;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }
        tmp_truth_name_2 = CHECK_IF_TRUE(tmp_attribute_value_2);
        if (tmp_truth_name_2 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);
            Py_DECREF(tmp_attribute_value_2);

            asyncgen_heap->exception_lineno = 82;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_5 = tmp_truth_name_2 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        Py_DECREF(tmp_attribute_value_2);
        if (tmp_condition_result_5 == NUITKA_BOOL_TRUE) {
            goto branch_yes_5;
        } else {
            goto branch_no_5;
        }
    }
    branch_yes_5:;
    {
        PyObject *tmp_raise_type_4;
        PyObject *tmp_make_exception_arg_4;
        tmp_make_exception_arg_4 = mod_consts[8];
        asyncgen->m_frame->m_frame.f_lineno = 83;
        tmp_raise_type_4 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_RuntimeError, tmp_make_exception_arg_4);
        assert(!(tmp_raise_type_4 == NULL));
        asyncgen_heap->exception_state.exception_type = tmp_raise_type_4;
        asyncgen_heap->exception_lineno = 83;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &asyncgen_heap->exception_state);
        asyncgen_heap->type_description_1 = "cco";
        goto frame_exception_exit_1;
    }
    branch_no_5:;
    branch_no_3:;
    // Tried code:
    {
        PyObject *tmp_expression_value_13;
        NUITKA_MAY_BE_UNUSED PyObject *tmp_yield_result_1;
        tmp_expression_value_13 = Py_None;
        Py_INCREF(tmp_expression_value_13);
        asyncgen->m_yield_return_index = 2;
        return tmp_expression_value_13;
        yield_return_2:
        if (yield_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 85;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_5;
        }
        tmp_yield_result_1 = yield_return_value;
        Py_DECREF(tmp_yield_result_1);
    }
    goto try_end_3;
    // Exception handler code:
    try_except_handler_5:;
    asyncgen_heap->exception_keeper_lineno_4 = asyncgen_heap->exception_lineno;
    asyncgen_heap->exception_lineno = 0;
    asyncgen_heap->exception_keeper_name_4 = asyncgen_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&asyncgen_heap->exception_state);

    // Preserve existing published exception id 2.
    asyncgen_heap->exception_preserved_2 = GET_CURRENT_EXCEPTION(tstate);

    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&asyncgen_heap->exception_keeper_name_4);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(asyncgen->m_frame, asyncgen_heap->exception_keeper_lineno_4);
            SET_EXCEPTION_STATE_TRACEBACK(&asyncgen_heap->exception_keeper_name_4, exception_tb);
        } else if (asyncgen_heap->exception_keeper_lineno_4 != 0) {
            exception_tb = ADD_TRACEBACK(exception_tb, asyncgen->m_frame, asyncgen_heap->exception_keeper_lineno_4);
            SET_EXCEPTION_STATE_TRACEBACK(&asyncgen_heap->exception_keeper_name_4, exception_tb);
        }
    }

    PUBLISH_CURRENT_EXCEPTION(tstate, &asyncgen_heap->exception_keeper_name_4);
    // Tried code:
    {
        PyObject *tmp_called_instance_3;
        PyObject *tmp_expression_value_14;
        PyObject *tmp_expression_value_15;
        PyObject *tmp_subscript_value_2;
        PyObject *tmp_add_expr_left_1;
        PyObject *tmp_add_expr_right_1;
        PyObject *tmp_call_result_3;
        if (Nuitka_Cell_GET(asyncgen->m_closure[1]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &asyncgen_heap->exception_state, mod_consts[3]);
            NORMALIZE_EXCEPTION_STATE(tstate, &asyncgen_heap->exception_state);
            CHAIN_EXCEPTION(tstate, asyncgen_heap->exception_state.exception_value);

            asyncgen_heap->exception_lineno = 87;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_6;
        }

        tmp_expression_value_15 = Nuitka_Cell_GET(asyncgen->m_closure[1]);
        tmp_expression_value_14 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_15, mod_consts[10]);
        if (tmp_expression_value_14 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 87;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_6;
        }
        if (Nuitka_Cell_GET(asyncgen->m_closure[0]) == NULL) {
            Py_DECREF(tmp_expression_value_14);
            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &asyncgen_heap->exception_state, mod_consts[2]);
            NORMALIZE_EXCEPTION_STATE(tstate, &asyncgen_heap->exception_state);
            CHAIN_EXCEPTION(tstate, asyncgen_heap->exception_state.exception_value);

            asyncgen_heap->exception_lineno = 87;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_6;
        }

        tmp_add_expr_left_1 = Nuitka_Cell_GET(asyncgen->m_closure[0]);
        tmp_add_expr_right_1 = const_int_pos_1;
        tmp_subscript_value_2 = BINARY_OPERATION_ADD_OBJECT_OBJECT_LONG(tmp_add_expr_left_1, tmp_add_expr_right_1);
        if (tmp_subscript_value_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);
            Py_DECREF(tmp_expression_value_14);

            asyncgen_heap->exception_lineno = 87;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_6;
        }
        tmp_called_instance_3 = LOOKUP_SUBSCRIPT(tstate, tmp_expression_value_14, tmp_subscript_value_2);
        Py_DECREF(tmp_expression_value_14);
        Py_DECREF(tmp_subscript_value_2);
        if (tmp_called_instance_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 87;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_6;
        }
        asyncgen->m_frame->m_frame.f_lineno = 87;
        tmp_call_result_3 = CALL_METHOD_NO_ARGS(tstate, tmp_called_instance_3, mod_consts[15]);
        Py_DECREF(tmp_called_instance_3);
        if (tmp_call_result_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 87;
            asyncgen_heap->type_description_1 = "cco";
            goto try_except_handler_6;
        }
        Py_DECREF(tmp_call_result_3);
    }
    asyncgen_heap->tmp_result = RERAISE_EXCEPTION(tstate, &asyncgen_heap->exception_state);
    if (unlikely(asyncgen_heap->tmp_result == false)) {
        asyncgen_heap->exception_lineno = 84;
    }

    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&asyncgen_heap->exception_state);

        if ((exception_tb != NULL) && (exception_tb->tb_frame == &asyncgen->m_frame->m_frame)) {
            asyncgen->m_frame->m_frame.f_lineno = exception_tb->tb_lineno;
        }
    }
    asyncgen_heap->type_description_1 = "cco";
    goto try_except_handler_6;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Exception handler code:
    try_except_handler_6:;
    asyncgen_heap->exception_keeper_lineno_5 = asyncgen_heap->exception_lineno;
    asyncgen_heap->exception_lineno = 0;
    asyncgen_heap->exception_keeper_name_5 = asyncgen_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&asyncgen_heap->exception_state);

    // Restore previous exception id 2.
    SET_CURRENT_EXCEPTION(tstate, &asyncgen_heap->exception_preserved_2);

    // Re-raise.
    asyncgen_heap->exception_state = asyncgen_heap->exception_keeper_name_5;
    asyncgen_heap->exception_lineno = asyncgen_heap->exception_keeper_lineno_5;

    goto frame_exception_exit_1;
    // End of try:
    // End of try:
    try_end_3:;
    {
        PyObject *tmp_called_instance_4;
        PyObject *tmp_expression_value_16;
        PyObject *tmp_expression_value_17;
        PyObject *tmp_subscript_value_3;
        PyObject *tmp_add_expr_left_2;
        PyObject *tmp_add_expr_right_2;
        PyObject *tmp_call_result_4;
        if (Nuitka_Cell_GET(asyncgen->m_closure[1]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &asyncgen_heap->exception_state, mod_consts[3]);
            NORMALIZE_EXCEPTION_STATE(tstate, &asyncgen_heap->exception_state);
            CHAIN_EXCEPTION(tstate, asyncgen_heap->exception_state.exception_value);

            asyncgen_heap->exception_lineno = 87;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }

        tmp_expression_value_17 = Nuitka_Cell_GET(asyncgen->m_closure[1]);
        tmp_expression_value_16 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_17, mod_consts[10]);
        if (tmp_expression_value_16 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 87;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }
        if (Nuitka_Cell_GET(asyncgen->m_closure[0]) == NULL) {
            Py_DECREF(tmp_expression_value_16);
            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &asyncgen_heap->exception_state, mod_consts[2]);
            NORMALIZE_EXCEPTION_STATE(tstate, &asyncgen_heap->exception_state);
            CHAIN_EXCEPTION(tstate, asyncgen_heap->exception_state.exception_value);

            asyncgen_heap->exception_lineno = 87;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }

        tmp_add_expr_left_2 = Nuitka_Cell_GET(asyncgen->m_closure[0]);
        tmp_add_expr_right_2 = const_int_pos_1;
        tmp_subscript_value_3 = BINARY_OPERATION_ADD_OBJECT_OBJECT_LONG(tmp_add_expr_left_2, tmp_add_expr_right_2);
        if (tmp_subscript_value_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);
            Py_DECREF(tmp_expression_value_16);

            asyncgen_heap->exception_lineno = 87;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }
        tmp_called_instance_4 = LOOKUP_SUBSCRIPT(tstate, tmp_expression_value_16, tmp_subscript_value_3);
        Py_DECREF(tmp_expression_value_16);
        Py_DECREF(tmp_subscript_value_3);
        if (tmp_called_instance_4 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 87;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }
        asyncgen->m_frame->m_frame.f_lineno = 87;
        tmp_call_result_4 = CALL_METHOD_NO_ARGS(tstate, tmp_called_instance_4, mod_consts[15]);
        Py_DECREF(tmp_called_instance_4);
        if (tmp_call_result_4 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);


            asyncgen_heap->exception_lineno = 87;
            asyncgen_heap->type_description_1 = "cco";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_4);
    }

    // Release exception attached to the frame
    DROP_ASYNCGEN_EXCEPTION(asyncgen);



    goto frame_no_exception_1;
    frame_exception_exit_1:;

    // If it's not an exit exception, consider and create a traceback for it.
    if (!EXCEPTION_STATE_MATCH_GENERATOR(tstate, &asyncgen_heap->exception_state)) {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&asyncgen_heap->exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(asyncgen->m_frame, asyncgen_heap->exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&asyncgen_heap->exception_state, exception_tb);
        } else if ((asyncgen_heap->exception_lineno != 0) && (exception_tb->tb_frame != &asyncgen->m_frame->m_frame)) {
            exception_tb = ADD_TRACEBACK(exception_tb, asyncgen->m_frame, asyncgen_heap->exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&asyncgen_heap->exception_state, exception_tb);
        }

        Nuitka_Frame_AttachLocals(
            asyncgen->m_frame,
            asyncgen_heap->type_description_1,
            asyncgen->m_closure[1],
            asyncgen->m_closure[0],
            asyncgen_heap->var_event
        );


        // Release cached frame if used for exception.
        if (asyncgen->m_frame == cache_m_frame) {
#if _DEBUG_REFCOUNTS
            count_active_frame_cache_instances -= 1;
            count_released_frame_cache_instances += 1;
#endif

            Py_DECREF(cache_m_frame);
            cache_m_frame = NULL;
        }

        assertFrameObject(asyncgen->m_frame);
    }

    // Release exception attached to the frame
    DROP_ASYNCGEN_EXCEPTION(asyncgen);


    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    goto try_end_4;
    // Exception handler code:
    try_except_handler_1:;
    asyncgen_heap->exception_keeper_lineno_6 = asyncgen_heap->exception_lineno;
    asyncgen_heap->exception_lineno = 0;
    asyncgen_heap->exception_keeper_name_6 = asyncgen_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&asyncgen_heap->exception_state);

    Py_XDECREF(asyncgen_heap->var_event);
    asyncgen_heap->var_event = NULL;
    // Re-raise.
    asyncgen_heap->exception_state = asyncgen_heap->exception_keeper_name_6;
    asyncgen_heap->exception_lineno = asyncgen_heap->exception_keeper_lineno_6;

    goto function_exception_exit;
    // End of try:
    try_end_4:;
    goto function_return_exit;

    NUITKA_CANNOT_GET_HERE("return must be present");

    function_exception_exit:

    CHECK_EXCEPTION_STATE(&asyncgen_heap->exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &asyncgen_heap->exception_state);
    return NULL;
    function_return_exit:;

    return NULL;

}

static PyObject *MAKE_ASYNCGEN_trio$testing$_sequencer$$36$$$36$$$36$function__2___call__$$36$$$36$$$36$asyncgen__1___call__(PyThreadState *tstate, struct Nuitka_CellObject **closure) {
    return Nuitka_Asyncgen_New(
        trio$testing$_sequencer$$36$$$36$$$36$function__2___call__$$36$$$36$$$36$asyncgen__1___call___context,
        module_trio$testing$_sequencer,
        mod_consts[17],
        mod_consts[18],
        code_objects_836958794e8a5c7f9da729db0f83a408,
        closure,
        2,
#if 1
        sizeof(struct trio$testing$_sequencer$$36$$$36$$$36$function__2___call__$$36$$$36$$$36$asyncgen__1___call___locals)
#else
        0
#endif
    );
}



static PyObject *MAKE_FUNCTION_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda,
        mod_consts[46],
#if PYTHON_VERSION >= 0x300
        mod_consts[47],
#endif
        code_objects_63ca4e1d511490d410b8a90b722f3b19,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_trio$testing$_sequencer,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_trio$testing$_sequencer$$36$$$36$$$36$function__2___call__(PyThreadState *tstate, PyObject *annotations) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_trio$testing$_sequencer$$36$$$36$$$36$function__2___call__,
        mod_consts[17],
#if PYTHON_VERSION >= 0x300
        mod_consts[18],
#endif
        code_objects_836958794e8a5c7f9da729db0f83a408,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_trio$testing$_sequencer,
        NULL,
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

static function_impl_code const function_table_trio$testing$_sequencer[] = {
    impl_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda,
    impl_trio$testing$_sequencer$$36$$$36$$$36$function__2___call__,
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

    return Nuitka_Function_GetFunctionState(function, function_table_trio$testing$_sequencer);
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
        module_trio$testing$_sequencer,
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
        function_table_trio$testing$_sequencer,
        sizeof(function_table_trio$testing$_sequencer) / sizeof(function_impl_code)
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
static char const *module_full_name = "trio.testing._sequencer";
#endif

// Internal entry point for module code.
PyObject *modulecode_trio$testing$_sequencer(PyThreadState *tstate, PyObject *module, struct Nuitka_MetaPathBasedLoaderEntry const *loader_entry) {
    // Report entry to PGO.
    PGO_onModuleEntered("trio$testing$_sequencer");

    // Store the module for future use.
    module_trio$testing$_sequencer = module;

    moduledict_trio$testing$_sequencer = MODULE_DICT(module_trio$testing$_sequencer);

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
        PRINT_STRING("trio$testing$_sequencer: Calling setupMetaPathBasedLoader().\n");
#endif
        setupMetaPathBasedLoader(tstate);
#if 0 >= 0
#ifdef _NUITKA_TRACE
        PRINT_STRING("trio$testing$_sequencer: Calling updateMetaPathBasedLoaderModuleRoot().\n");
#endif
        updateMetaPathBasedLoaderModuleRoot(module_full_name);
#endif


#if PYTHON_VERSION >= 0x300
        patchInspectModule(tstate);
#endif

#endif

        /* The constants only used by this module are created now. */
        NUITKA_PRINT_TRACE("trio$testing$_sequencer: Calling createModuleConstants().\n");
        createModuleConstants(tstate);

#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
        createModuleCodeObjects();
#endif
        init_done = true;
    }

#if _NUITKA_MODULE_MODE && 0
    PyObject *pre_load = IMPORT_EMBEDDED_MODULE(tstate, "trio.testing._sequencer" "-preLoad");
    if (pre_load == NULL) {
        return NULL;
    }
#endif

    // PRINT_STRING("in inittrio$testing$_sequencer\n");

#ifdef _NUITKA_PLUGIN_DILL_ENABLED
    {
        char const *module_name_c;
        if (loader_entry != NULL) {
            module_name_c = loader_entry->name;
        } else {
            PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)const_str_plain___name__);
            module_name_c = Nuitka_String_AsString(module_name);
        }

        registerDillPluginTables(tstate, module_name_c, &_method_def_reduce_compiled_function, &_method_def_create_compiled_function);
    }
#endif

    // Set "__compiled__" to what version information we have.
    UPDATE_STRING_DICT0(
        moduledict_trio$testing$_sequencer,
        (Nuitka_StringObject *)const_str_plain___compiled__,
        Nuitka_dunder_compiled_value
    );

    // Update "__package__" value to what it ought to be.
    {
#if 0
        UPDATE_STRING_DICT0(
            moduledict_trio$testing$_sequencer,
            (Nuitka_StringObject *)const_str_plain___package__,
            mod_consts[6]
        );
#elif 0
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)const_str_plain___name__);

        UPDATE_STRING_DICT0(
            moduledict_trio$testing$_sequencer,
            (Nuitka_StringObject *)const_str_plain___package__,
            module_name
        );
#else

#if PYTHON_VERSION < 0x300
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)const_str_plain___name__);
        char const *module_name_cstr = PyString_AS_STRING(module_name);

        char const *last_dot = strrchr(module_name_cstr, '.');

        if (last_dot != NULL) {
            UPDATE_STRING_DICT1(
                moduledict_trio$testing$_sequencer,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyString_FromStringAndSize(module_name_cstr, last_dot - module_name_cstr)
            );
        }
#else
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)const_str_plain___name__);
        Py_ssize_t dot_index = PyUnicode_Find(module_name, const_str_dot, 0, PyUnicode_GetLength(module_name), -1);

        if (dot_index != -1) {
            UPDATE_STRING_DICT1(
                moduledict_trio$testing$_sequencer,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyUnicode_Substring(module_name, 0, dot_index)
            );
        }
#endif
#endif
    }

    CHECK_OBJECT(module_trio$testing$_sequencer);

    // For deep importing of a module we need to have "__builtins__", so we set
    // it ourselves in the same way than CPython does. Note: This must be done
    // before the frame object is allocated, or else it may fail.

    if (GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)const_str_plain___builtins__) == NULL) {
        PyObject *value = (PyObject *)builtin_module;

        // Check if main module, not a dict then but the module itself.
#if _NUITKA_MODULE_MODE || !0
        value = PyModule_GetDict(value);
#endif

        UPDATE_STRING_DICT0(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)const_str_plain___builtins__, value);
    }

    PyObject *module_loader = Nuitka_Loader_New(loader_entry);
    UPDATE_STRING_DICT0(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)const_str_plain___loader__, module_loader);

#if PYTHON_VERSION >= 0x300
// Set the "__spec__" value

#if 0
    // Main modules just get "None" as spec.
    UPDATE_STRING_DICT0(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)const_str_plain___spec__, Py_None);
#else
    // Other modules get a "ModuleSpec" from the standard mechanism.
    {
        PyObject *bootstrap_module = getImportLibBootstrapModule();
        CHECK_OBJECT(bootstrap_module);

        PyObject *_spec_from_module = PyObject_GetAttrString(bootstrap_module, "_spec_from_module");
        CHECK_OBJECT(_spec_from_module);

        PyObject *spec_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, _spec_from_module, module_trio$testing$_sequencer);
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

        UPDATE_STRING_DICT1(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)const_str_plain___spec__, spec_value);
    }
#endif
#endif

    // Temp variables if any
    PyObject *outline_0_var___class__ = NULL;
    PyObject *tmp_class_creation_1__class_decl_dict = NULL;
    PyObject *tmp_class_creation_1__prepared = NULL;
    PyObject *tmp_import_from_1__module = NULL;
    struct Nuitka_FrameObject *frame_frame_trio$testing$_sequencer;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    bool tmp_result;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;
    PyObject *locals_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_17 = NULL;
    PyObject *tmp_dictset_value;
    struct Nuitka_FrameObject *frame_frame_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_2;
    NUITKA_MAY_BE_UNUSED char const *type_description_2 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_2;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_2;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_3;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_3;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_4;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_4;

    // Module init code if any


    // Module code.
    {
        PyObject *tmp_assign_source_1;
        tmp_assign_source_1 = Py_None;
        UPDATE_STRING_DICT0(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[19], tmp_assign_source_1);
    }
    {
        PyObject *tmp_assign_source_2;
        tmp_assign_source_2 = module_filename_obj;
        UPDATE_STRING_DICT0(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[20], tmp_assign_source_2);
    }
    frame_frame_trio$testing$_sequencer = MAKE_MODULE_FRAME(code_objects_09fbf08013f985798a450601ba78f3c5, module_trio$testing$_sequencer);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_trio$testing$_sequencer);
    assert(Py_REFCNT(frame_frame_trio$testing$_sequencer) == 2);

    // Framed code:
    {
        PyObject *tmp_assattr_value_1;
        PyObject *tmp_assattr_target_1;
        tmp_assattr_value_1 = module_filename_obj;
        tmp_assattr_target_1 = module_var_accessor_trio$$36$testing$$36$_sequencer$__spec__(tstate);
        assert(!(tmp_assattr_target_1 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_1, mod_consts[21], tmp_assattr_value_1);
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
        tmp_assattr_target_2 = module_var_accessor_trio$$36$testing$$36$_sequencer$__spec__(tstate);
        assert(!(tmp_assattr_target_2 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_2, mod_consts[22], tmp_assattr_value_2);
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
        UPDATE_STRING_DICT0(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[23], tmp_assign_source_3);
    }
    {
        PyObject *tmp_assign_source_4;
        {
            PyObject *hard_module = IMPORT_HARD___FUTURE__();
            tmp_assign_source_4 = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[24]);
        }
        assert(!(tmp_assign_source_4 == NULL));
        UPDATE_STRING_DICT1(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[24], tmp_assign_source_4);
    }
    {
        PyObject *tmp_assign_source_5;
        PyObject *tmp_import_name_from_1;
        PyObject *tmp_name_value_1;
        PyObject *tmp_globals_arg_value_1;
        PyObject *tmp_locals_arg_value_1;
        PyObject *tmp_fromlist_value_1;
        PyObject *tmp_level_value_1;
        tmp_name_value_1 = mod_consts[25];
        tmp_globals_arg_value_1 = (PyObject *)moduledict_trio$testing$_sequencer;
        tmp_locals_arg_value_1 = Py_None;
        tmp_fromlist_value_1 = mod_consts[26];
        tmp_level_value_1 = const_int_0;
        frame_frame_trio$testing$_sequencer->m_frame.f_lineno = 3;
        tmp_import_name_from_1 = IMPORT_MODULE5(tstate, tmp_name_value_1, tmp_globals_arg_value_1, tmp_locals_arg_value_1, tmp_fromlist_value_1, tmp_level_value_1);
        if (tmp_import_name_from_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 3;

            goto frame_exception_exit_1;
        }
        if (PyModule_Check(tmp_import_name_from_1)) {
            tmp_assign_source_5 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_1,
                (PyObject *)moduledict_trio$testing$_sequencer,
                mod_consts[0],
                const_int_0
            );
        } else {
            tmp_assign_source_5 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_1, mod_consts[0]);
        }

        Py_DECREF(tmp_import_name_from_1);
        if (tmp_assign_source_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 3;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[0], tmp_assign_source_5);
    }
    {
        PyObject *tmp_assign_source_6;
        PyObject *tmp_import_name_from_2;
        PyObject *tmp_name_value_2;
        PyObject *tmp_globals_arg_value_2;
        PyObject *tmp_locals_arg_value_2;
        PyObject *tmp_fromlist_value_2;
        PyObject *tmp_level_value_2;
        tmp_name_value_2 = mod_consts[27];
        tmp_globals_arg_value_2 = (PyObject *)moduledict_trio$testing$_sequencer;
        tmp_locals_arg_value_2 = Py_None;
        tmp_fromlist_value_2 = mod_consts[28];
        tmp_level_value_2 = const_int_0;
        frame_frame_trio$testing$_sequencer->m_frame.f_lineno = 4;
        tmp_import_name_from_2 = IMPORT_MODULE5(tstate, tmp_name_value_2, tmp_globals_arg_value_2, tmp_locals_arg_value_2, tmp_fromlist_value_2, tmp_level_value_2);
        if (tmp_import_name_from_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 4;

            goto frame_exception_exit_1;
        }
        if (PyModule_Check(tmp_import_name_from_2)) {
            tmp_assign_source_6 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_2,
                (PyObject *)moduledict_trio$testing$_sequencer,
                mod_consts[29],
                const_int_0
            );
        } else {
            tmp_assign_source_6 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_2, mod_consts[29]);
        }

        Py_DECREF(tmp_import_name_from_2);
        if (tmp_assign_source_6 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 4;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[29], tmp_assign_source_6);
    }
    {
        PyObject *tmp_assign_source_7;
        tmp_assign_source_7 = Py_False;
        UPDATE_STRING_DICT0(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[30], tmp_assign_source_7);
    }
    {
        PyObject *tmp_assign_source_8;
        PyObject *tmp_name_value_3;
        PyObject *tmp_globals_arg_value_3;
        PyObject *tmp_locals_arg_value_3;
        PyObject *tmp_fromlist_value_3;
        PyObject *tmp_level_value_3;
        tmp_name_value_3 = mod_consts[31];
        tmp_globals_arg_value_3 = (PyObject *)moduledict_trio$testing$_sequencer;
        tmp_locals_arg_value_3 = Py_None;
        tmp_fromlist_value_3 = Py_None;
        tmp_level_value_3 = const_int_0;
        frame_frame_trio$testing$_sequencer->m_frame.f_lineno = 7;
        tmp_assign_source_8 = IMPORT_MODULE5(tstate, tmp_name_value_3, tmp_globals_arg_value_3, tmp_locals_arg_value_3, tmp_fromlist_value_3, tmp_level_value_3);
        if (tmp_assign_source_8 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 7;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[31], tmp_assign_source_8);
    }
    {
        PyObject *tmp_assign_source_9;
        PyObject *tmp_name_value_4;
        PyObject *tmp_globals_arg_value_4;
        PyObject *tmp_locals_arg_value_4;
        PyObject *tmp_fromlist_value_4;
        PyObject *tmp_level_value_4;
        tmp_name_value_4 = mod_consts[6];
        tmp_globals_arg_value_4 = (PyObject *)moduledict_trio$testing$_sequencer;
        tmp_locals_arg_value_4 = Py_None;
        tmp_fromlist_value_4 = mod_consts[32];
        tmp_level_value_4 = mod_consts[33];
        frame_frame_trio$testing$_sequencer->m_frame.f_lineno = 9;
        tmp_assign_source_9 = IMPORT_MODULE5(tstate, tmp_name_value_4, tmp_globals_arg_value_4, tmp_locals_arg_value_4, tmp_fromlist_value_4, tmp_level_value_4);
        if (tmp_assign_source_9 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 9;

            goto frame_exception_exit_1;
        }
        assert(tmp_import_from_1__module == NULL);
        tmp_import_from_1__module = tmp_assign_source_9;
    }
    // Tried code:
    {
        PyObject *tmp_assign_source_10;
        PyObject *tmp_import_name_from_3;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_3 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_3)) {
            tmp_assign_source_10 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_3,
                (PyObject *)moduledict_trio$testing$_sequencer,
                mod_consts[1],
                const_int_0
            );
        } else {
            tmp_assign_source_10 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_3, mod_consts[1]);
        }

        if (tmp_assign_source_10 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 9;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[1], tmp_assign_source_10);
    }
    {
        PyObject *tmp_assign_source_11;
        PyObject *tmp_import_name_from_4;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_4 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_4)) {
            tmp_assign_source_11 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_4,
                (PyObject *)moduledict_trio$testing$_sequencer,
                mod_consts[12],
                const_int_0
            );
        } else {
            tmp_assign_source_11 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_4, mod_consts[12]);
        }

        if (tmp_assign_source_11 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 9;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[12], tmp_assign_source_11);
    }
    {
        PyObject *tmp_assign_source_12;
        PyObject *tmp_import_name_from_5;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_5 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_5)) {
            tmp_assign_source_12 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_5,
                (PyObject *)moduledict_trio$testing$_sequencer,
                mod_consts[34],
                const_int_0
            );
        } else {
            tmp_assign_source_12 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_5, mod_consts[34]);
        }

        if (tmp_assign_source_12 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 9;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[34], tmp_assign_source_12);
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
        PyObject *tmp_assign_source_13;
        tmp_assign_source_13 = MAKE_DICT_EMPTY(tstate);
        assert(tmp_class_creation_1__class_decl_dict == NULL);
        tmp_class_creation_1__class_decl_dict = tmp_assign_source_13;
    }
    {
        PyObject *tmp_assign_source_14;
        tmp_assign_source_14 = MAKE_DICT_EMPTY(tstate);
        assert(tmp_class_creation_1__prepared == NULL);
        tmp_class_creation_1__prepared = tmp_assign_source_14;
    }
    // Tried code:
    {
        PyObject *tmp_assign_source_15;
        PyObject *tmp_called_value_1;
        PyObject *tmp_expression_value_1;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_called_value_2;
        PyObject *tmp_called_value_3;
        PyObject *tmp_expression_value_2;
        PyObject *tmp_args_element_value_2;
        tmp_expression_value_1 = module_var_accessor_trio$$36$testing$$36$_sequencer$_util(tstate);
        if (unlikely(tmp_expression_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[34]);
        }

        if (tmp_expression_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 15;

            goto try_except_handler_2;
        }
        tmp_called_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[35]);
        if (tmp_called_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 15;

            goto try_except_handler_2;
        }
        tmp_expression_value_2 = module_var_accessor_trio$$36$testing$$36$_sequencer$attrs(tstate);
        if (unlikely(tmp_expression_value_2 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[31]);
        }

        if (tmp_expression_value_2 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));

            Py_DECREF(tmp_called_value_1);

            exception_lineno = 16;

            goto try_except_handler_2;
        }
        tmp_called_value_3 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_2, mod_consts[36]);
        if (tmp_called_value_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_called_value_1);

            exception_lineno = 16;

            goto try_except_handler_2;
        }
        frame_frame_trio$testing$_sequencer->m_frame.f_lineno = 16;
        tmp_called_value_2 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_called_value_3, &PyTuple_GET_ITEM(mod_consts[37], 0), mod_consts[38]);
        Py_DECREF(tmp_called_value_3);
        if (tmp_called_value_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_called_value_1);

            exception_lineno = 16;

            goto try_except_handler_2;
        }
        {
            PyObject *tmp_set_locals_1;
            CHECK_OBJECT(tmp_class_creation_1__prepared);
            tmp_set_locals_1 = tmp_class_creation_1__prepared;
            locals_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_17 = tmp_set_locals_1;
            Py_INCREF(tmp_set_locals_1);
        }
        tmp_dictset_value = mod_consts[39];
        tmp_result = DICT_SET_ITEM(locals_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_17, mod_consts[40], tmp_dictset_value);
        assert(!(tmp_result == false));
        tmp_dictset_value = mod_consts[41];
        tmp_result = DICT_SET_ITEM(locals_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_17, mod_consts[19], tmp_dictset_value);
        assert(!(tmp_result == false));
        tmp_dictset_value = mod_consts[42];
        tmp_result = DICT_SET_ITEM(locals_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_17, mod_consts[43], tmp_dictset_value);
        assert(!(tmp_result == false));
        tmp_dictset_value = MAKE_DICT_EMPTY(tstate);
        tmp_result = DICT_SET_ITEM(locals_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_17, mod_consts[44], tmp_dictset_value);
        Py_DECREF(tmp_dictset_value);
        assert(!(tmp_result == false));
        // Tried code:
        // Tried code:
        frame_frame_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_2 = MAKE_CLASS_FRAME(tstate, code_objects_67714a9ecd1b6f78db6bfd493b6bcfc5, module_trio$testing$_sequencer, NULL, sizeof(void *));

        // Push the new frame as the currently active one, and we should be exclusively
        // owning it.
        pushFrameStackCompiledFrame(tstate, frame_frame_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_2);
        assert(Py_REFCNT(frame_frame_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_2) == 2);

        // Framed code:
        {
            PyObject *tmp_called_value_4;
            PyObject *tmp_expression_value_3;
            PyObject *tmp_kw_call_value_0_1;
            PyObject *tmp_kw_call_value_1_1;
            tmp_expression_value_3 = module_var_accessor_trio$$36$testing$$36$_sequencer$attrs(tstate);
            if (unlikely(tmp_expression_value_3 == NULL)) {
                RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[31]);
            }

            if (tmp_expression_value_3 == NULL) {
                assert(HAS_EXCEPTION_STATE(&exception_state));



                exception_lineno = 57;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
            tmp_called_value_4 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_3, mod_consts[45]);
            if (tmp_called_value_4 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 57;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }


            tmp_kw_call_value_0_1 = MAKE_FUNCTION_trio$testing$_sequencer$$36$$$36$$$36$function__1_lambda(tstate);

            tmp_kw_call_value_1_1 = Py_False;
            frame_frame_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_2->m_frame.f_lineno = 57;
            {
                PyObject *kw_values[2] = {tmp_kw_call_value_0_1, tmp_kw_call_value_1_1};

                tmp_dictset_value = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_called_value_4, kw_values, mod_consts[48]);
            }

            Py_DECREF(tmp_called_value_4);
            Py_DECREF(tmp_kw_call_value_0_1);
            if (tmp_dictset_value == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 57;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
            tmp_result = DICT_SET_ITEM(locals_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_17, mod_consts[10], tmp_dictset_value);
            Py_DECREF(tmp_dictset_value);
            if (tmp_result == false) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 57;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
        }
        {
            PyObject *tmp_ass_subvalue_1;
            PyObject *tmp_ass_subscribed_1;
            PyObject *tmp_ass_subscript_1;
            tmp_ass_subvalue_1 = mod_consts[49];
            tmp_ass_subscribed_1 = DICT_GET_ITEM0(tstate, locals_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_17, mod_consts[44]);

            if (unlikely(tmp_ass_subscribed_1 == NULL && CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate))) {

            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[44]);

                exception_lineno = 57;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }

            if (tmp_ass_subscribed_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 57;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
            tmp_ass_subscript_1 = mod_consts[10];
            tmp_result = SET_SUBSCRIPT(tstate, tmp_ass_subscribed_1, tmp_ass_subscript_1, tmp_ass_subvalue_1);
            if (tmp_result == false) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 57;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
        }
        {
            PyObject *tmp_called_value_5;
            PyObject *tmp_expression_value_4;
            tmp_expression_value_4 = module_var_accessor_trio$$36$testing$$36$_sequencer$attrs(tstate);
            if (unlikely(tmp_expression_value_4 == NULL)) {
                RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[31]);
            }

            if (tmp_expression_value_4 == NULL) {
                assert(HAS_EXCEPTION_STATE(&exception_state));



                exception_lineno = 61;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
            tmp_called_value_5 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_4, mod_consts[45]);
            if (tmp_called_value_5 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 61;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
            frame_frame_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_2->m_frame.f_lineno = 61;
            tmp_dictset_value = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_called_value_5, &PyTuple_GET_ITEM(mod_consts[50], 0), mod_consts[48]);
            Py_DECREF(tmp_called_value_5);
            if (tmp_dictset_value == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 61;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
            tmp_result = DICT_SET_ITEM(locals_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_17, mod_consts[4], tmp_dictset_value);
            Py_DECREF(tmp_dictset_value);
            if (tmp_result == false) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 61;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
        }
        {
            PyObject *tmp_ass_subvalue_2;
            PyObject *tmp_ass_subscribed_2;
            PyObject *tmp_ass_subscript_2;
            tmp_ass_subvalue_2 = mod_consts[51];
            tmp_ass_subscribed_2 = DICT_GET_ITEM0(tstate, locals_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_17, mod_consts[44]);

            if (unlikely(tmp_ass_subscribed_2 == NULL && CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate))) {

            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[44]);

                exception_lineno = 61;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }

            if (tmp_ass_subscribed_2 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 61;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
            tmp_ass_subscript_2 = mod_consts[4];
            tmp_result = SET_SUBSCRIPT(tstate, tmp_ass_subscribed_2, tmp_ass_subscript_2, tmp_ass_subvalue_2);
            if (tmp_result == false) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 61;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
        }
        {
            PyObject *tmp_called_value_6;
            PyObject *tmp_expression_value_5;
            tmp_expression_value_5 = module_var_accessor_trio$$36$testing$$36$_sequencer$attrs(tstate);
            if (unlikely(tmp_expression_value_5 == NULL)) {
                RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[31]);
            }

            if (tmp_expression_value_5 == NULL) {
                assert(HAS_EXCEPTION_STATE(&exception_state));



                exception_lineno = 62;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
            tmp_called_value_6 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_5, mod_consts[45]);
            if (tmp_called_value_6 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 62;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
            frame_frame_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_2->m_frame.f_lineno = 62;
            tmp_dictset_value = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_called_value_6, &PyTuple_GET_ITEM(mod_consts[37], 0), mod_consts[52]);
            Py_DECREF(tmp_called_value_6);
            if (tmp_dictset_value == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 62;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
            tmp_result = DICT_SET_ITEM(locals_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_17, mod_consts[7], tmp_dictset_value);
            Py_DECREF(tmp_dictset_value);
            if (tmp_result == false) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 62;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
        }
        {
            PyObject *tmp_ass_subvalue_3;
            PyObject *tmp_ass_subscribed_3;
            PyObject *tmp_ass_subscript_3;
            tmp_ass_subvalue_3 = mod_consts[53];
            tmp_ass_subscribed_3 = DICT_GET_ITEM0(tstate, locals_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_17, mod_consts[44]);

            if (unlikely(tmp_ass_subscribed_3 == NULL && CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate))) {

            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[44]);

                exception_lineno = 62;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }

            if (tmp_ass_subscribed_3 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 62;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
            tmp_ass_subscript_3 = mod_consts[7];
            tmp_result = SET_SUBSCRIPT(tstate, tmp_ass_subscribed_3, tmp_ass_subscript_3, tmp_ass_subvalue_3);
            if (tmp_result == false) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 62;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
        }
        {
            PyObject *tmp_called_value_7;
            PyObject *tmp_args_element_value_3;
            PyObject *tmp_annotations_1;
            tmp_called_value_7 = module_var_accessor_trio$$36$testing$$36$_sequencer$asynccontextmanager(tstate);
            if (unlikely(tmp_called_value_7 == NULL)) {
                RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[29]);
            }

            if (tmp_called_value_7 == NULL) {
                assert(HAS_EXCEPTION_STATE(&exception_state));



                exception_lineno = 64;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
            tmp_annotations_1 = DICT_COPY(tstate, mod_consts[54]);


            tmp_args_element_value_3 = MAKE_FUNCTION_trio$testing$_sequencer$$36$$$36$$$36$function__2___call__(tstate, tmp_annotations_1);

            frame_frame_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_2->m_frame.f_lineno = 64;
            tmp_dictset_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_7, tmp_args_element_value_3);
            Py_DECREF(tmp_args_element_value_3);
            if (tmp_dictset_value == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 64;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
            tmp_result = DICT_SET_ITEM(locals_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_17, mod_consts[17], tmp_dictset_value);
            Py_DECREF(tmp_dictset_value);
            if (tmp_result == false) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 65;
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
                exception_tb = MAKE_TRACEBACK(frame_frame_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_2, exception_lineno);
                SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
            } else if (exception_tb->tb_frame != &frame_frame_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_2->m_frame) {
                exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_2, exception_lineno);
                SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
            }
        }

        // Attaches locals to frame if any.
        Nuitka_Frame_AttachLocals(
            frame_frame_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_2,
            type_description_2,
            outline_0_var___class__
        );



        assertFrameObject(frame_frame_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_2);

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
            PyObject *tmp_assign_source_16;
            PyObject *tmp_called_value_8;
            PyObject *tmp_args_value_1;
            PyObject *tmp_tuple_element_1;
            PyObject *tmp_kwargs_value_1;
            tmp_called_value_8 = (PyObject *)&PyType_Type;
            tmp_tuple_element_1 = mod_consts[42];
            tmp_args_value_1 = MAKE_TUPLE_EMPTY(tstate, 3);
            PyTuple_SET_ITEM0(tmp_args_value_1, 0, tmp_tuple_element_1);
            tmp_tuple_element_1 = const_tuple_empty;
            PyTuple_SET_ITEM0(tmp_args_value_1, 1, tmp_tuple_element_1);
            tmp_tuple_element_1 = locals_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_17;
            PyTuple_SET_ITEM0(tmp_args_value_1, 2, tmp_tuple_element_1);
            CHECK_OBJECT(tmp_class_creation_1__class_decl_dict);
            tmp_kwargs_value_1 = tmp_class_creation_1__class_decl_dict;
            frame_frame_trio$testing$_sequencer->m_frame.f_lineno = 17;
            tmp_assign_source_16 = CALL_FUNCTION(tstate, tmp_called_value_8, tmp_args_value_1, tmp_kwargs_value_1);
            Py_DECREF(tmp_args_value_1);
            if (tmp_assign_source_16 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 17;

                goto try_except_handler_4;
            }
            assert(outline_0_var___class__ == NULL);
            outline_0_var___class__ = tmp_assign_source_16;
        }
        CHECK_OBJECT(outline_0_var___class__);
        tmp_args_element_value_2 = outline_0_var___class__;
        Py_INCREF(tmp_args_element_value_2);
        goto try_return_handler_4;
        NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
        return NULL;
        // Return handler code:
        try_return_handler_4:;
        Py_DECREF(locals_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_17);
        locals_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_17 = NULL;
        goto try_return_handler_3;
        // Exception handler code:
        try_except_handler_4:;
        exception_keeper_lineno_2 = exception_lineno;
        exception_lineno = 0;
        exception_keeper_name_2 = exception_state;
        INIT_ERROR_OCCURRED_STATE(&exception_state);

        Py_DECREF(locals_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_17);
        locals_trio$testing$_sequencer$$36$$$36$$$36$class__1_Sequencer_17 = NULL;
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
        exception_lineno = 17;
        goto try_except_handler_2;
        outline_result_1:;
        frame_frame_trio$testing$_sequencer->m_frame.f_lineno = 16;
        tmp_args_element_value_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_2, tmp_args_element_value_2);
        Py_DECREF(tmp_called_value_2);
        Py_DECREF(tmp_args_element_value_2);
        if (tmp_args_element_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_called_value_1);

            exception_lineno = 16;

            goto try_except_handler_2;
        }
        frame_frame_trio$testing$_sequencer->m_frame.f_lineno = 15;
        tmp_assign_source_15 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_1, tmp_args_element_value_1);
        Py_DECREF(tmp_called_value_1);
        Py_DECREF(tmp_args_element_value_1);
        if (tmp_assign_source_15 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 15;

            goto try_except_handler_2;
        }
        UPDATE_STRING_DICT1(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)mod_consts[42], tmp_assign_source_15);
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


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_2;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_trio$testing$_sequencer, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_trio$testing$_sequencer->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_trio$testing$_sequencer, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }



    assertFrameObject(frame_frame_trio$testing$_sequencer);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto module_exception_exit;
    frame_no_exception_2:;
    CHECK_OBJECT(tmp_class_creation_1__class_decl_dict);
    Py_DECREF(tmp_class_creation_1__class_decl_dict);
    tmp_class_creation_1__class_decl_dict = NULL;
    CHECK_OBJECT(tmp_class_creation_1__prepared);
    Py_DECREF(tmp_class_creation_1__prepared);
    tmp_class_creation_1__prepared = NULL;

    // Report to PGO about leaving the module without error.
    PGO_onModuleExit("trio$testing$_sequencer", false);

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *post_load = IMPORT_EMBEDDED_MODULE(tstate, "trio.testing._sequencer" "-postLoad");
        if (post_load == NULL) {
            return NULL;
        }
    }
#endif

    Py_INCREF(module_trio$testing$_sequencer);
    return module_trio$testing$_sequencer;
    module_exception_exit:

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_trio$testing$_sequencer, (Nuitka_StringObject *)const_str_plain___name__);

        if (module_name != NULL) {
            Nuitka_DelModule(tstate, module_name);
        }
    }
#endif
    PGO_onModuleExit("trio$testing$_sequencer", false);

    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);
    return NULL;
}
