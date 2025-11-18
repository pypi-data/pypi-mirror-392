/* Generated code for Python module 'rapidfuzz$_utils'
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

/* The "module_rapidfuzz$_utils" is a Python object pointer of module type.
 *
 * Note: For full compatibility with CPython, every module variable access
 * needs to go through it except for cases where the module cannot possibly
 * have changed in the mean time.
 */

PyObject *module_rapidfuzz$_utils;
PyDictObject *moduledict_rapidfuzz$_utils;

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
        loadConstantsBlob(tstate, &mod_consts[0], UN_TRANSLATE("rapidfuzz._utils"));
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
void checkModuleConstants_rapidfuzz$_utils(PyThreadState *tstate) {
    // The module may not have been used at all, then ignore this.
    if (constants_created == false) return;

    for (int i = 0; i < 59; i++) {
        assert(mod_consts_hash[i] == DEEP_HASH(tstate, mod_consts[i]));
        CHECK_OBJECT_DEEP(mod_consts[i]);
    }
}
#endif

// Helper to preserving module variables for Python3.11+
#if 10
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
static PyObject *module_var_accessor_rapidfuzz$$36$_utils$ScorerFlag(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_rapidfuzz$_utils->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_rapidfuzz$_utils->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[9]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_rapidfuzz$_utils->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[9]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[9]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[9]);
    }

    return result;
}

static PyObject *module_var_accessor_rapidfuzz$$36$_utils$__annotations__(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_rapidfuzz$_utils->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_rapidfuzz$_utils->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[21]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_rapidfuzz$_utils->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[21]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[21], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[21]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[21], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[21]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[21]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[21]);
    }

    return result;
}

static PyObject *module_var_accessor_rapidfuzz$$36$_utils$__spec__(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_rapidfuzz$_utils->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_rapidfuzz$_utils->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[58]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_rapidfuzz$_utils->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[58]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[58]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[58]);
    }

    return result;
}

static PyObject *module_var_accessor_rapidfuzz$$36$_utils$_get_scorer_flags_distance(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_rapidfuzz$_utils->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_rapidfuzz$_utils->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[38]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_rapidfuzz$_utils->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[38]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[38], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[38]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[38], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[38]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[38]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[38]);
    }

    return result;
}

static PyObject *module_var_accessor_rapidfuzz$$36$_utils$_get_scorer_flags_normalized_distance(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_rapidfuzz$_utils->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_rapidfuzz$_utils->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[40]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_rapidfuzz$_utils->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[40]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[40], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[40]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[40], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[40]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[40]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[40]);
    }

    return result;
}

static PyObject *module_var_accessor_rapidfuzz$$36$_utils$_get_scorer_flags_normalized_similarity(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_rapidfuzz$_utils->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_rapidfuzz$_utils->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[41]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_rapidfuzz$_utils->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[41]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[41], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[41]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[41], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[41]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[41]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[41]);
    }

    return result;
}

static PyObject *module_var_accessor_rapidfuzz$$36$_utils$_get_scorer_flags_similarity(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_rapidfuzz$_utils->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_rapidfuzz$_utils->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[39]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_rapidfuzz$_utils->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[39]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[39], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[39]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[39], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[39]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[39]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[39]);
    }

    return result;
}

static PyObject *module_var_accessor_rapidfuzz$$36$_utils$isnan(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_rapidfuzz$_utils->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_rapidfuzz$_utils->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[13]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_rapidfuzz$_utils->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[13]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[13], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[13]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[13], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[13]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[13]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[13]);
    }

    return result;
}

static PyObject *module_var_accessor_rapidfuzz$$36$_utils$pandas_NA(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_rapidfuzz$_utils->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_rapidfuzz$_utils->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[0]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_rapidfuzz$_utils->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[0]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[0]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[0]);
    }

    return result;
}

static PyObject *module_var_accessor_rapidfuzz$$36$_utils$setupPandas(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_rapidfuzz$_utils->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_rapidfuzz$_utils->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[28]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_rapidfuzz$_utils->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[28]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[28], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[28]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[28], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[28]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[28]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[28]);
    }

    return result;
}


#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
// The module code objects.
static PyCodeObject *code_objects_ed03f5129879a2552c6b074bf4f90ac8;
static PyCodeObject *code_objects_cab6cccd9fc6c94d24b01a53c160fd31;
static PyCodeObject *code_objects_c784bfd921e0b0180810e682bc514dea;
static PyCodeObject *code_objects_baafbbcc071a7aaa306dde15430f4408;
static PyCodeObject *code_objects_0b55db926c53065dd67d82d35ccf12fb;
static PyCodeObject *code_objects_c35f224c0000d962e008442d85c79e69;
static PyCodeObject *code_objects_6a79c3f6e306011d7fb0c9688e54adb0;
static PyCodeObject *code_objects_e0a717b12e23c77d2a37d33f7fe9f540;

static void createModuleCodeObjects(void) {
    module_filename_obj = MAKE_RELATIVE_PATH(mod_consts[52]); CHECK_OBJECT(module_filename_obj);
    code_objects_ed03f5129879a2552c6b074bf4f90ac8 = MAKE_CODE_OBJECT(module_filename_obj, 1, CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[53], mod_consts[53], NULL, NULL, 0, 0, 0);
    code_objects_cab6cccd9fc6c94d24b01a53c160fd31 = MAKE_CODE_OBJECT(module_filename_obj, 31, CO_OPTIMIZED | CO_NEWLOCALS | CO_VARKEYWORDS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[38], mod_consts[38], mod_consts[54], NULL, 0, 0, 0);
    code_objects_c784bfd921e0b0180810e682bc514dea = MAKE_CODE_OBJECT(module_filename_obj, 47, CO_OPTIMIZED | CO_NEWLOCALS | CO_VARKEYWORDS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[40], mod_consts[40], mod_consts[54], NULL, 0, 0, 0);
    code_objects_baafbbcc071a7aaa306dde15430f4408 = MAKE_CODE_OBJECT(module_filename_obj, 55, CO_OPTIMIZED | CO_NEWLOCALS | CO_VARKEYWORDS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[41], mod_consts[41], mod_consts[54], NULL, 0, 0, 0);
    code_objects_0b55db926c53065dd67d82d35ccf12fb = MAKE_CODE_OBJECT(module_filename_obj, 39, CO_OPTIMIZED | CO_NEWLOCALS | CO_VARKEYWORDS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[39], mod_consts[39], mod_consts[54], NULL, 0, 0, 0);
    code_objects_c35f224c0000d962e008442d85c79e69 = MAKE_CODE_OBJECT(module_filename_obj, 73, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[45], mod_consts[45], mod_consts[55], NULL, 2, 0, 0);
    code_objects_6a79c3f6e306011d7fb0c9688e54adb0 = MAKE_CODE_OBJECT(module_filename_obj, 63, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[43], mod_consts[43], mod_consts[56], NULL, 1, 0, 0);
    code_objects_e0a717b12e23c77d2a37d33f7fe9f540 = MAKE_CODE_OBJECT(module_filename_obj, 13, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[28], mod_consts[28], mod_consts[3], NULL, 0, 0, 0);
}
#endif

// The module function declarations.
static PyObject *MAKE_FUNCTION_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance(PyThreadState *tstate, PyObject *annotations);


static PyObject *MAKE_FUNCTION_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity(PyThreadState *tstate, PyObject *annotations);


static PyObject *MAKE_FUNCTION_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance(PyThreadState *tstate, PyObject *annotations);


static PyObject *MAKE_FUNCTION_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity(PyThreadState *tstate, PyObject *annotations);


static PyObject *MAKE_FUNCTION_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none(PyThreadState *tstate, PyObject *annotations);


static PyObject *MAKE_FUNCTION_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs(PyThreadState *tstate, PyObject *annotations);


// The module function definitions.
static PyObject *impl_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *var_pandas = NULL;
    struct Nuitka_FrameObject *frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    int tmp_res;
    static struct Nuitka_FrameObject *cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;

    // Actual function body.
    // Tried code:
    if (isFrameUnusable(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas)) {
        Py_XDECREF(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas = MAKE_FUNCTION_FRAME(tstate, code_objects_e0a717b12e23c77d2a37d33f7fe9f540, module_rapidfuzz$_utils, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas->m_type_description == NULL);
    frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas = cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas);
    assert(Py_REFCNT(frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas) == 2);

    // Framed code:
    {
        bool tmp_condition_result_1;
        PyObject *tmp_cmp_expr_left_1;
        PyObject *tmp_cmp_expr_right_1;
        tmp_cmp_expr_left_1 = module_var_accessor_rapidfuzz$$36$_utils$pandas_NA(tstate);
        if (unlikely(tmp_cmp_expr_left_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[0]);
        }

        if (tmp_cmp_expr_left_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 15;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
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
        PyObject *tmp_assign_source_1;
        PyObject *tmp_called_value_1;
        PyObject *tmp_expression_value_1;
        PyObject *tmp_expression_value_2;
        tmp_expression_value_2 = IMPORT_HARD_SYS();
        assert(!(tmp_expression_value_2 == NULL));
        tmp_expression_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_2, mod_consts[1]);
        if (tmp_expression_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 16;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_called_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[2]);
        Py_DECREF(tmp_expression_value_1);
        if (tmp_called_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 16;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas->m_frame.f_lineno = 16;
        tmp_assign_source_1 = CALL_FUNCTION_WITH_POS_ARGS1(tstate, tmp_called_value_1, mod_consts[3]);

        Py_DECREF(tmp_called_value_1);
        if (tmp_assign_source_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 16;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        assert(var_pandas == NULL);
        var_pandas = tmp_assign_source_1;
    }
    {
        bool tmp_condition_result_2;
        PyObject *tmp_expression_value_3;
        CHECK_OBJECT(var_pandas);
        tmp_expression_value_3 = var_pandas;
        tmp_res = HAS_ATTR_BOOL2(tstate, tmp_expression_value_3, mod_consts[4]);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 17;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_2 = (tmp_res != 0) ? true : false;
        if (tmp_condition_result_2 != false) {
            goto branch_yes_2;
        } else {
            goto branch_no_2;
        }
    }
    branch_yes_2:;
    {
        PyObject *tmp_assign_source_2;
        PyObject *tmp_expression_value_4;
        CHECK_OBJECT(var_pandas);
        tmp_expression_value_4 = var_pandas;
        tmp_assign_source_2 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_4, mod_consts[4]);
        if (tmp_assign_source_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 18;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[0], tmp_assign_source_2);
    }
    branch_no_2:;
    branch_no_1:;


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas,
        type_description_1,
        var_pandas
    );


    // Release cached frame if used for exception.
    if (frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas == cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas);
        cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas = NULL;
    }

    assertFrameObject(frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    tmp_return_value = Py_None;
    Py_INCREF(tmp_return_value);
    goto try_return_handler_1;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Return handler code:
    try_return_handler_1:;
    Py_XDECREF(var_pandas);
    var_pandas = NULL;
    goto function_return_exit;
    // Exception handler code:
    try_except_handler_1:;
    exception_keeper_lineno_1 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_1 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    Py_XDECREF(var_pandas);
    var_pandas = NULL;
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


static PyObject *impl_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par__kwargs = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    int tmp_res;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance)) {
        Py_XDECREF(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance = MAKE_FUNCTION_FRAME(tstate, code_objects_cab6cccd9fc6c94d24b01a53c160fd31, module_rapidfuzz$_utils, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance->m_type_description == NULL);
    frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance = cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance);
    assert(Py_REFCNT(frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance) == 2);

    // Framed code:
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[5];
        tmp_dict_value_1 = const_int_0;
        tmp_return_value = _PyDict_NewPresized( 3 );
        {
            PyObject *tmp_bitor_expr_left_1;
            PyObject *tmp_bitor_expr_right_1;
            PyObject *tmp_expression_value_1;
            PyObject *tmp_expression_value_2;
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[6];
            tmp_dict_value_1 = mod_consts[7];
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[8];
            tmp_expression_value_1 = module_var_accessor_rapidfuzz$$36$_utils$ScorerFlag(tstate);
            if (unlikely(tmp_expression_value_1 == NULL)) {
                RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[9]);
            }

            if (tmp_expression_value_1 == NULL) {
                assert(HAS_EXCEPTION_STATE(&exception_state));



                exception_lineno = 35;
                type_description_1 = "o";
                goto dict_build_exception_1;
            }
            tmp_bitor_expr_left_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[10]);
            if (tmp_bitor_expr_left_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 35;
                type_description_1 = "o";
                goto dict_build_exception_1;
            }
            tmp_expression_value_2 = module_var_accessor_rapidfuzz$$36$_utils$ScorerFlag(tstate);
            if (unlikely(tmp_expression_value_2 == NULL)) {
                RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[9]);
            }

            if (tmp_expression_value_2 == NULL) {
                assert(HAS_EXCEPTION_STATE(&exception_state));

                Py_DECREF(tmp_bitor_expr_left_1);

                exception_lineno = 35;
                type_description_1 = "o";
                goto dict_build_exception_1;
            }
            tmp_bitor_expr_right_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_2, mod_consts[11]);
            if (tmp_bitor_expr_right_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                Py_DECREF(tmp_bitor_expr_left_1);

                exception_lineno = 35;
                type_description_1 = "o";
                goto dict_build_exception_1;
            }
            tmp_dict_value_1 = BINARY_OPERATION_BITOR_OBJECT_OBJECT_OBJECT(tmp_bitor_expr_left_1, tmp_bitor_expr_right_1);
            Py_DECREF(tmp_bitor_expr_left_1);
            Py_DECREF(tmp_bitor_expr_right_1);
            if (tmp_dict_value_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 35;
                type_description_1 = "o";
                goto dict_build_exception_1;
            }
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
        }
        goto dict_build_noexception_1;
        // Exception handling pass through code for dict_build:
        dict_build_exception_1:;
        Py_DECREF(tmp_return_value);
        goto frame_exception_exit_1;
        // Finished with no exception for dict_build:
        dict_build_noexception_1:;
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
            exception_tb = MAKE_TRACEBACK(frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance,
        type_description_1,
        par__kwargs
    );


    // Release cached frame if used for exception.
    if (frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance == cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance);
        cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance = NULL;
    }

    assertFrameObject(frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par__kwargs);
    Py_DECREF(par__kwargs);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par__kwargs);
    Py_DECREF(par__kwargs);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par__kwargs = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    int tmp_res;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity)) {
        Py_XDECREF(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity = MAKE_FUNCTION_FRAME(tstate, code_objects_0b55db926c53065dd67d82d35ccf12fb, module_rapidfuzz$_utils, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity->m_type_description == NULL);
    frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity = cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity);
    assert(Py_REFCNT(frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity) == 2);

    // Framed code:
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[5];
        tmp_dict_value_1 = mod_consts[7];
        tmp_return_value = _PyDict_NewPresized( 3 );
        {
            PyObject *tmp_bitor_expr_left_1;
            PyObject *tmp_bitor_expr_right_1;
            PyObject *tmp_expression_value_1;
            PyObject *tmp_expression_value_2;
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[6];
            tmp_dict_value_1 = const_int_0;
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[8];
            tmp_expression_value_1 = module_var_accessor_rapidfuzz$$36$_utils$ScorerFlag(tstate);
            if (unlikely(tmp_expression_value_1 == NULL)) {
                RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[9]);
            }

            if (tmp_expression_value_1 == NULL) {
                assert(HAS_EXCEPTION_STATE(&exception_state));



                exception_lineno = 43;
                type_description_1 = "o";
                goto dict_build_exception_1;
            }
            tmp_bitor_expr_left_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[10]);
            if (tmp_bitor_expr_left_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 43;
                type_description_1 = "o";
                goto dict_build_exception_1;
            }
            tmp_expression_value_2 = module_var_accessor_rapidfuzz$$36$_utils$ScorerFlag(tstate);
            if (unlikely(tmp_expression_value_2 == NULL)) {
                RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[9]);
            }

            if (tmp_expression_value_2 == NULL) {
                assert(HAS_EXCEPTION_STATE(&exception_state));

                Py_DECREF(tmp_bitor_expr_left_1);

                exception_lineno = 43;
                type_description_1 = "o";
                goto dict_build_exception_1;
            }
            tmp_bitor_expr_right_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_2, mod_consts[11]);
            if (tmp_bitor_expr_right_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                Py_DECREF(tmp_bitor_expr_left_1);

                exception_lineno = 43;
                type_description_1 = "o";
                goto dict_build_exception_1;
            }
            tmp_dict_value_1 = BINARY_OPERATION_BITOR_OBJECT_OBJECT_OBJECT(tmp_bitor_expr_left_1, tmp_bitor_expr_right_1);
            Py_DECREF(tmp_bitor_expr_left_1);
            Py_DECREF(tmp_bitor_expr_right_1);
            if (tmp_dict_value_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 43;
                type_description_1 = "o";
                goto dict_build_exception_1;
            }
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
        }
        goto dict_build_noexception_1;
        // Exception handling pass through code for dict_build:
        dict_build_exception_1:;
        Py_DECREF(tmp_return_value);
        goto frame_exception_exit_1;
        // Finished with no exception for dict_build:
        dict_build_noexception_1:;
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
            exception_tb = MAKE_TRACEBACK(frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity,
        type_description_1,
        par__kwargs
    );


    // Release cached frame if used for exception.
    if (frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity == cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity);
        cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity = NULL;
    }

    assertFrameObject(frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par__kwargs);
    Py_DECREF(par__kwargs);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par__kwargs);
    Py_DECREF(par__kwargs);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par__kwargs = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    int tmp_res;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance)) {
        Py_XDECREF(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance = MAKE_FUNCTION_FRAME(tstate, code_objects_c784bfd921e0b0180810e682bc514dea, module_rapidfuzz$_utils, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance->m_type_description == NULL);
    frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance = cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance);
    assert(Py_REFCNT(frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance) == 2);

    // Framed code:
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[5];
        tmp_dict_value_1 = const_int_0;
        tmp_return_value = _PyDict_NewPresized( 3 );
        {
            PyObject *tmp_bitor_expr_left_1;
            PyObject *tmp_bitor_expr_right_1;
            PyObject *tmp_expression_value_1;
            PyObject *tmp_expression_value_2;
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[6];
            tmp_dict_value_1 = const_int_pos_1;
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[8];
            tmp_expression_value_1 = module_var_accessor_rapidfuzz$$36$_utils$ScorerFlag(tstate);
            if (unlikely(tmp_expression_value_1 == NULL)) {
                RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[9]);
            }

            if (tmp_expression_value_1 == NULL) {
                assert(HAS_EXCEPTION_STATE(&exception_state));



                exception_lineno = 51;
                type_description_1 = "o";
                goto dict_build_exception_1;
            }
            tmp_bitor_expr_left_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[12]);
            if (tmp_bitor_expr_left_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 51;
                type_description_1 = "o";
                goto dict_build_exception_1;
            }
            tmp_expression_value_2 = module_var_accessor_rapidfuzz$$36$_utils$ScorerFlag(tstate);
            if (unlikely(tmp_expression_value_2 == NULL)) {
                RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[9]);
            }

            if (tmp_expression_value_2 == NULL) {
                assert(HAS_EXCEPTION_STATE(&exception_state));

                Py_DECREF(tmp_bitor_expr_left_1);

                exception_lineno = 51;
                type_description_1 = "o";
                goto dict_build_exception_1;
            }
            tmp_bitor_expr_right_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_2, mod_consts[11]);
            if (tmp_bitor_expr_right_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                Py_DECREF(tmp_bitor_expr_left_1);

                exception_lineno = 51;
                type_description_1 = "o";
                goto dict_build_exception_1;
            }
            tmp_dict_value_1 = BINARY_OPERATION_BITOR_OBJECT_OBJECT_OBJECT(tmp_bitor_expr_left_1, tmp_bitor_expr_right_1);
            Py_DECREF(tmp_bitor_expr_left_1);
            Py_DECREF(tmp_bitor_expr_right_1);
            if (tmp_dict_value_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 51;
                type_description_1 = "o";
                goto dict_build_exception_1;
            }
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
        }
        goto dict_build_noexception_1;
        // Exception handling pass through code for dict_build:
        dict_build_exception_1:;
        Py_DECREF(tmp_return_value);
        goto frame_exception_exit_1;
        // Finished with no exception for dict_build:
        dict_build_noexception_1:;
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
            exception_tb = MAKE_TRACEBACK(frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance,
        type_description_1,
        par__kwargs
    );


    // Release cached frame if used for exception.
    if (frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance == cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance);
        cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance = NULL;
    }

    assertFrameObject(frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par__kwargs);
    Py_DECREF(par__kwargs);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par__kwargs);
    Py_DECREF(par__kwargs);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par__kwargs = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    int tmp_res;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity)) {
        Py_XDECREF(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity = MAKE_FUNCTION_FRAME(tstate, code_objects_baafbbcc071a7aaa306dde15430f4408, module_rapidfuzz$_utils, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity->m_type_description == NULL);
    frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity = cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity);
    assert(Py_REFCNT(frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity) == 2);

    // Framed code:
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[5];
        tmp_dict_value_1 = const_int_pos_1;
        tmp_return_value = _PyDict_NewPresized( 3 );
        {
            PyObject *tmp_bitor_expr_left_1;
            PyObject *tmp_bitor_expr_right_1;
            PyObject *tmp_expression_value_1;
            PyObject *tmp_expression_value_2;
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[6];
            tmp_dict_value_1 = const_int_0;
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[8];
            tmp_expression_value_1 = module_var_accessor_rapidfuzz$$36$_utils$ScorerFlag(tstate);
            if (unlikely(tmp_expression_value_1 == NULL)) {
                RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[9]);
            }

            if (tmp_expression_value_1 == NULL) {
                assert(HAS_EXCEPTION_STATE(&exception_state));



                exception_lineno = 59;
                type_description_1 = "o";
                goto dict_build_exception_1;
            }
            tmp_bitor_expr_left_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[12]);
            if (tmp_bitor_expr_left_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 59;
                type_description_1 = "o";
                goto dict_build_exception_1;
            }
            tmp_expression_value_2 = module_var_accessor_rapidfuzz$$36$_utils$ScorerFlag(tstate);
            if (unlikely(tmp_expression_value_2 == NULL)) {
                RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[9]);
            }

            if (tmp_expression_value_2 == NULL) {
                assert(HAS_EXCEPTION_STATE(&exception_state));

                Py_DECREF(tmp_bitor_expr_left_1);

                exception_lineno = 59;
                type_description_1 = "o";
                goto dict_build_exception_1;
            }
            tmp_bitor_expr_right_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_2, mod_consts[11]);
            if (tmp_bitor_expr_right_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                Py_DECREF(tmp_bitor_expr_left_1);

                exception_lineno = 59;
                type_description_1 = "o";
                goto dict_build_exception_1;
            }
            tmp_dict_value_1 = BINARY_OPERATION_BITOR_OBJECT_OBJECT_OBJECT(tmp_bitor_expr_left_1, tmp_bitor_expr_right_1);
            Py_DECREF(tmp_bitor_expr_left_1);
            Py_DECREF(tmp_bitor_expr_right_1);
            if (tmp_dict_value_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 59;
                type_description_1 = "o";
                goto dict_build_exception_1;
            }
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
        }
        goto dict_build_noexception_1;
        // Exception handling pass through code for dict_build:
        dict_build_exception_1:;
        Py_DECREF(tmp_return_value);
        goto frame_exception_exit_1;
        // Finished with no exception for dict_build:
        dict_build_noexception_1:;
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
            exception_tb = MAKE_TRACEBACK(frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity,
        type_description_1,
        par__kwargs
    );


    // Release cached frame if used for exception.
    if (frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity == cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity);
        cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity = NULL;
    }

    assertFrameObject(frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par__kwargs);
    Py_DECREF(par__kwargs);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par__kwargs);
    Py_DECREF(par__kwargs);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_s = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    PyObject *tmp_return_value = NULL;
    int tmp_res;
    static struct Nuitka_FrameObject *cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none)) {
        Py_XDECREF(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none = MAKE_FUNCTION_FRAME(tstate, code_objects_6a79c3f6e306011d7fb0c9688e54adb0, module_rapidfuzz$_utils, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none->m_type_description == NULL);
    frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none = cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none);
    assert(Py_REFCNT(frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none) == 2);

    // Framed code:
    {
        bool tmp_condition_result_1;
        int tmp_or_left_truth_1;
        bool tmp_or_left_value_1;
        bool tmp_or_right_value_1;
        PyObject *tmp_cmp_expr_left_1;
        PyObject *tmp_cmp_expr_right_1;
        PyObject *tmp_cmp_expr_left_2;
        PyObject *tmp_cmp_expr_right_2;
        CHECK_OBJECT(par_s);
        tmp_cmp_expr_left_1 = par_s;
        tmp_cmp_expr_right_1 = Py_None;
        tmp_or_left_value_1 = (tmp_cmp_expr_left_1 == tmp_cmp_expr_right_1) ? true : false;
        tmp_or_left_truth_1 = tmp_or_left_value_1 != false ? 1 : 0;
        if (tmp_or_left_truth_1 == 1) {
            goto or_left_1;
        } else {
            goto or_right_1;
        }
        or_right_1:;
        CHECK_OBJECT(par_s);
        tmp_cmp_expr_left_2 = par_s;
        tmp_cmp_expr_right_2 = module_var_accessor_rapidfuzz$$36$_utils$pandas_NA(tstate);
        if (unlikely(tmp_cmp_expr_right_2 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[0]);
        }

        if (tmp_cmp_expr_right_2 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 64;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_or_right_value_1 = (tmp_cmp_expr_left_2 == tmp_cmp_expr_right_2) ? true : false;
        tmp_condition_result_1 = tmp_or_right_value_1;
        goto or_end_1;
        or_left_1:;
        tmp_condition_result_1 = tmp_or_left_value_1;
        or_end_1:;
        if (tmp_condition_result_1 != false) {
            goto branch_yes_1;
        } else {
            goto branch_no_1;
        }
    }
    branch_yes_1:;
    tmp_return_value = Py_True;
    Py_INCREF(tmp_return_value);
    goto frame_return_exit_1;
    branch_no_1:;
    {
        nuitka_bool tmp_condition_result_2;
        int tmp_and_left_truth_1;
        nuitka_bool tmp_and_left_value_1;
        nuitka_bool tmp_and_right_value_1;
        PyObject *tmp_isinstance_inst_1;
        PyObject *tmp_isinstance_cls_1;
        PyObject *tmp_called_value_1;
        PyObject *tmp_call_result_1;
        PyObject *tmp_args_element_value_1;
        int tmp_truth_name_1;
        CHECK_OBJECT(par_s);
        tmp_isinstance_inst_1 = par_s;
        tmp_isinstance_cls_1 = (PyObject *)&PyFloat_Type;
        tmp_res = PyObject_IsInstance(tmp_isinstance_inst_1, tmp_isinstance_cls_1);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 67;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_and_left_value_1 = (tmp_res != 0) ? NUITKA_BOOL_TRUE : NUITKA_BOOL_FALSE;
        tmp_and_left_truth_1 = tmp_and_left_value_1 == NUITKA_BOOL_TRUE ? 1 : 0;
        if (tmp_and_left_truth_1 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 67;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        if (tmp_and_left_truth_1 == 1) {
            goto and_right_1;
        } else {
            goto and_left_1;
        }
        and_right_1:;
        tmp_called_value_1 = module_var_accessor_rapidfuzz$$36$_utils$isnan(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[13]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 67;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_s);
        tmp_args_element_value_1 = par_s;
        frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none->m_frame.f_lineno = 67;
        tmp_call_result_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_1, tmp_args_element_value_1);
        if (tmp_call_result_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 67;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_truth_name_1 = CHECK_IF_TRUE(tmp_call_result_1);
        if (tmp_truth_name_1 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_call_result_1);

            exception_lineno = 67;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_and_right_value_1 = tmp_truth_name_1 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        Py_DECREF(tmp_call_result_1);
        tmp_condition_result_2 = tmp_and_right_value_1;
        goto and_end_1;
        and_left_1:;
        tmp_condition_result_2 = tmp_and_left_value_1;
        and_end_1:;
        if (tmp_condition_result_2 == NUITKA_BOOL_TRUE) {
            goto branch_yes_2;
        } else {
            goto branch_no_2;
        }
    }
    branch_yes_2:;
    tmp_return_value = Py_True;
    Py_INCREF(tmp_return_value);
    goto frame_return_exit_1;
    branch_no_2:;


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
            exception_tb = MAKE_TRACEBACK(frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none,
        type_description_1,
        par_s
    );


    // Release cached frame if used for exception.
    if (frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none == cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none);
        cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none = NULL;
    }

    assertFrameObject(frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;
    tmp_return_value = Py_False;
    Py_INCREF(tmp_return_value);
    goto function_return_exit;

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


static PyObject *impl_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_func = python_pars[0];
    PyObject *par_cached_scorer_call = python_pars[1];
    struct Nuitka_FrameObject *frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    bool tmp_result;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs = NULL;
    PyObject *tmp_return_value = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs)) {
        Py_XDECREF(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs = MAKE_FUNCTION_FRAME(tstate, code_objects_c35f224c0000d962e008442d85c79e69, module_rapidfuzz$_utils, sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs->m_type_description == NULL);
    frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs = cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs);
    assert(Py_REFCNT(frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs) == 2);

    // Framed code:
    {
        PyObject *tmp_assattr_value_1;
        PyObject *tmp_assattr_target_1;
        CHECK_OBJECT(par_cached_scorer_call);
        tmp_assattr_value_1 = par_cached_scorer_call;
        CHECK_OBJECT(par_func);
        tmp_assattr_target_1 = par_func;
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_1, mod_consts[14], tmp_assattr_value_1);
        if (tmp_result == false) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 74;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
    }
    {
        PyObject *tmp_assattr_value_2;
        PyObject *tmp_assattr_target_2;
        CHECK_OBJECT(par_func);
        tmp_assattr_value_2 = par_func;
        CHECK_OBJECT(par_func);
        tmp_assattr_target_2 = par_func;
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_2, mod_consts[15], tmp_assattr_value_2);
        if (tmp_result == false) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 76;
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
            exception_tb = MAKE_TRACEBACK(frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs,
        type_description_1,
        par_func,
        par_cached_scorer_call
    );


    // Release cached frame if used for exception.
    if (frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs == cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs);
        cache_frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs = NULL;
    }

    assertFrameObject(frame_frame_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs);

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
    CHECK_OBJECT(par_func);
    Py_DECREF(par_func);
    CHECK_OBJECT(par_cached_scorer_call);
    Py_DECREF(par_cached_scorer_call);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_func);
    Py_DECREF(par_func);
    CHECK_OBJECT(par_cached_scorer_call);
    Py_DECREF(par_cached_scorer_call);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}



static PyObject *MAKE_FUNCTION_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas,
        mod_consts[28],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_e0a717b12e23c77d2a37d33f7fe9f540,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_rapidfuzz$_utils,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance(PyThreadState *tstate, PyObject *annotations) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance,
        mod_consts[38],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_cab6cccd9fc6c94d24b01a53c160fd31,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_rapidfuzz$_utils,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity(PyThreadState *tstate, PyObject *annotations) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity,
        mod_consts[39],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_0b55db926c53065dd67d82d35ccf12fb,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_rapidfuzz$_utils,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance(PyThreadState *tstate, PyObject *annotations) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance,
        mod_consts[40],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_c784bfd921e0b0180810e682bc514dea,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_rapidfuzz$_utils,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity(PyThreadState *tstate, PyObject *annotations) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity,
        mod_consts[41],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_baafbbcc071a7aaa306dde15430f4408,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_rapidfuzz$_utils,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none(PyThreadState *tstate, PyObject *annotations) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none,
        mod_consts[43],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_6a79c3f6e306011d7fb0c9688e54adb0,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_rapidfuzz$_utils,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs(PyThreadState *tstate, PyObject *annotations) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs,
        mod_consts[45],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_c35f224c0000d962e008442d85c79e69,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_rapidfuzz$_utils,
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

static function_impl_code const function_table_rapidfuzz$_utils[] = {
    impl_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas,
    impl_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance,
    impl_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity,
    impl_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance,
    impl_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity,
    impl_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none,
    impl_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs,
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

    return Nuitka_Function_GetFunctionState(function, function_table_rapidfuzz$_utils);
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
        module_rapidfuzz$_utils,
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
        function_table_rapidfuzz$_utils,
        sizeof(function_table_rapidfuzz$_utils) / sizeof(function_impl_code)
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
static char const *module_full_name = "rapidfuzz._utils";
#endif

// Internal entry point for module code.
PyObject *modulecode_rapidfuzz$_utils(PyThreadState *tstate, PyObject *module, struct Nuitka_MetaPathBasedLoaderEntry const *loader_entry) {
    // Report entry to PGO.
    PGO_onModuleEntered("rapidfuzz$_utils");

    // Store the module for future use.
    module_rapidfuzz$_utils = module;

    moduledict_rapidfuzz$_utils = MODULE_DICT(module_rapidfuzz$_utils);

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
        PRINT_STRING("rapidfuzz$_utils: Calling setupMetaPathBasedLoader().\n");
#endif
        setupMetaPathBasedLoader(tstate);
#if 0 >= 0
#ifdef _NUITKA_TRACE
        PRINT_STRING("rapidfuzz$_utils: Calling updateMetaPathBasedLoaderModuleRoot().\n");
#endif
        updateMetaPathBasedLoaderModuleRoot(module_full_name);
#endif


#if PYTHON_VERSION >= 0x300
        patchInspectModule(tstate);
#endif

#endif

        /* The constants only used by this module are created now. */
        NUITKA_PRINT_TRACE("rapidfuzz$_utils: Calling createModuleConstants().\n");
        createModuleConstants(tstate);

#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
        createModuleCodeObjects();
#endif
        init_done = true;
    }

#if _NUITKA_MODULE_MODE && 0
    PyObject *pre_load = IMPORT_EMBEDDED_MODULE(tstate, "rapidfuzz._utils" "-preLoad");
    if (pre_load == NULL) {
        return NULL;
    }
#endif

    // PRINT_STRING("in initrapidfuzz$_utils\n");

#ifdef _NUITKA_PLUGIN_DILL_ENABLED
    {
        char const *module_name_c;
        if (loader_entry != NULL) {
            module_name_c = loader_entry->name;
        } else {
            PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)const_str_plain___name__);
            module_name_c = Nuitka_String_AsString(module_name);
        }

        registerDillPluginTables(tstate, module_name_c, &_method_def_reduce_compiled_function, &_method_def_create_compiled_function);
    }
#endif

    // Set "__compiled__" to what version information we have.
    UPDATE_STRING_DICT0(
        moduledict_rapidfuzz$_utils,
        (Nuitka_StringObject *)const_str_plain___compiled__,
        Nuitka_dunder_compiled_value
    );

    // Update "__package__" value to what it ought to be.
    {
#if 0
        UPDATE_STRING_DICT0(
            moduledict_rapidfuzz$_utils,
            (Nuitka_StringObject *)const_str_plain___package__,
            mod_consts[57]
        );
#elif 0
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)const_str_plain___name__);

        UPDATE_STRING_DICT0(
            moduledict_rapidfuzz$_utils,
            (Nuitka_StringObject *)const_str_plain___package__,
            module_name
        );
#else

#if PYTHON_VERSION < 0x300
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)const_str_plain___name__);
        char const *module_name_cstr = PyString_AS_STRING(module_name);

        char const *last_dot = strrchr(module_name_cstr, '.');

        if (last_dot != NULL) {
            UPDATE_STRING_DICT1(
                moduledict_rapidfuzz$_utils,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyString_FromStringAndSize(module_name_cstr, last_dot - module_name_cstr)
            );
        }
#else
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)const_str_plain___name__);
        Py_ssize_t dot_index = PyUnicode_Find(module_name, const_str_dot, 0, PyUnicode_GetLength(module_name), -1);

        if (dot_index != -1) {
            UPDATE_STRING_DICT1(
                moduledict_rapidfuzz$_utils,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyUnicode_Substring(module_name, 0, dot_index)
            );
        }
#endif
#endif
    }

    CHECK_OBJECT(module_rapidfuzz$_utils);

    // For deep importing of a module we need to have "__builtins__", so we set
    // it ourselves in the same way than CPython does. Note: This must be done
    // before the frame object is allocated, or else it may fail.

    if (GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)const_str_plain___builtins__) == NULL) {
        PyObject *value = (PyObject *)builtin_module;

        // Check if main module, not a dict then but the module itself.
#if _NUITKA_MODULE_MODE || !0
        value = PyModule_GetDict(value);
#endif

        UPDATE_STRING_DICT0(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)const_str_plain___builtins__, value);
    }

    PyObject *module_loader = Nuitka_Loader_New(loader_entry);
    UPDATE_STRING_DICT0(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)const_str_plain___loader__, module_loader);

#if PYTHON_VERSION >= 0x300
// Set the "__spec__" value

#if 0
    // Main modules just get "None" as spec.
    UPDATE_STRING_DICT0(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)const_str_plain___spec__, Py_None);
#else
    // Other modules get a "ModuleSpec" from the standard mechanism.
    {
        PyObject *bootstrap_module = getImportLibBootstrapModule();
        CHECK_OBJECT(bootstrap_module);

        PyObject *_spec_from_module = PyObject_GetAttrString(bootstrap_module, "_spec_from_module");
        CHECK_OBJECT(_spec_from_module);

        PyObject *spec_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, _spec_from_module, module_rapidfuzz$_utils);
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

        UPDATE_STRING_DICT1(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)const_str_plain___spec__, spec_value);
    }
#endif
#endif

    // Temp variables if any
    PyObject *outline_0_var___class__ = NULL;
    PyObject *tmp_class_creation_1__class_decl_dict = NULL;
    PyObject *tmp_class_creation_1__prepared = NULL;
    PyObject *tmp_import_from_1__module = NULL;
    struct Nuitka_FrameObject *frame_frame_rapidfuzz$_utils;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    bool tmp_result;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;
    NUITKA_MAY_BE_UNUSED nuitka_void tmp_unused;
    PyObject *locals_rapidfuzz$_utils$$36$$$36$$$36$class__1_ScorerFlag_24 = NULL;
    PyObject *tmp_dictset_value;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_2;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_2;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_3;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_3;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_4;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_4;
    int tmp_res;

    // Module init code if any


    // Module code.
    {
        PyObject *tmp_assign_source_1;
        tmp_assign_source_1 = Py_None;
        UPDATE_STRING_DICT0(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[16], tmp_assign_source_1);
    }
    {
        PyObject *tmp_assign_source_2;
        tmp_assign_source_2 = module_filename_obj;
        UPDATE_STRING_DICT0(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[17], tmp_assign_source_2);
    }
    frame_frame_rapidfuzz$_utils = MAKE_MODULE_FRAME(code_objects_ed03f5129879a2552c6b074bf4f90ac8, module_rapidfuzz$_utils);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_rapidfuzz$_utils);
    assert(Py_REFCNT(frame_frame_rapidfuzz$_utils) == 2);

    // Framed code:
    {
        PyObject *tmp_assattr_value_1;
        PyObject *tmp_assattr_target_1;
        tmp_assattr_value_1 = module_filename_obj;
        tmp_assattr_target_1 = module_var_accessor_rapidfuzz$$36$_utils$__spec__(tstate);
        assert(!(tmp_assattr_target_1 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_1, mod_consts[18], tmp_assattr_value_1);
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
        tmp_assattr_target_2 = module_var_accessor_rapidfuzz$$36$_utils$__spec__(tstate);
        assert(!(tmp_assattr_target_2 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_2, mod_consts[19], tmp_assattr_value_2);
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
        UPDATE_STRING_DICT0(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[20], tmp_assign_source_3);
    }
    {
        PyObject *tmp_assign_source_4;
        tmp_assign_source_4 = MAKE_DICT_EMPTY(tstate);
        UPDATE_STRING_DICT1(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[21], tmp_assign_source_4);
    }
    {
        PyObject *tmp_assign_source_5;
        {
            PyObject *hard_module = IMPORT_HARD___FUTURE__();
            tmp_assign_source_5 = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[22]);
        }
        assert(!(tmp_assign_source_5 == NULL));
        UPDATE_STRING_DICT1(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[22], tmp_assign_source_5);
    }
    {
        PyObject *tmp_assign_source_6;
        tmp_assign_source_6 = IMPORT_HARD_SYS();
        assert(!(tmp_assign_source_6 == NULL));
        UPDATE_STRING_DICT0(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[23], tmp_assign_source_6);
    }
    {
        PyObject *tmp_assign_source_7;
        PyObject *tmp_import_name_from_1;
        PyObject *tmp_name_value_1;
        PyObject *tmp_globals_arg_value_1;
        PyObject *tmp_locals_arg_value_1;
        PyObject *tmp_fromlist_value_1;
        PyObject *tmp_level_value_1;
        tmp_name_value_1 = mod_consts[24];
        tmp_globals_arg_value_1 = (PyObject *)moduledict_rapidfuzz$_utils;
        tmp_locals_arg_value_1 = Py_None;
        tmp_fromlist_value_1 = mod_consts[25];
        tmp_level_value_1 = const_int_0;
        frame_frame_rapidfuzz$_utils->m_frame.f_lineno = 7;
        tmp_import_name_from_1 = IMPORT_MODULE5(tstate, tmp_name_value_1, tmp_globals_arg_value_1, tmp_locals_arg_value_1, tmp_fromlist_value_1, tmp_level_value_1);
        if (tmp_import_name_from_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 7;

            goto frame_exception_exit_1;
        }
        if (PyModule_Check(tmp_import_name_from_1)) {
            tmp_assign_source_7 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_1,
                (PyObject *)moduledict_rapidfuzz$_utils,
                mod_consts[13],
                const_int_0
            );
        } else {
            tmp_assign_source_7 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_1, mod_consts[13]);
        }

        Py_DECREF(tmp_import_name_from_1);
        if (tmp_assign_source_7 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 7;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[13], tmp_assign_source_7);
    }
    {
        PyObject *tmp_assign_source_8;
        tmp_assign_source_8 = IMPORT_HARD_TYPING();
        assert(!(tmp_assign_source_8 == NULL));
        assert(tmp_import_from_1__module == NULL);
        Py_INCREF(tmp_assign_source_8);
        tmp_import_from_1__module = tmp_assign_source_8;
    }
    // Tried code:
    {
        PyObject *tmp_assign_source_9;
        PyObject *tmp_import_name_from_2;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_2 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_2)) {
            tmp_assign_source_9 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_2,
                (PyObject *)moduledict_rapidfuzz$_utils,
                mod_consts[26],
                const_int_0
            );
        } else {
            tmp_assign_source_9 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_2, mod_consts[26]);
        }

        if (tmp_assign_source_9 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 8;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[26], tmp_assign_source_9);
    }
    {
        PyObject *tmp_assign_source_10;
        PyObject *tmp_import_name_from_3;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_3 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_3)) {
            tmp_assign_source_10 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_3,
                (PyObject *)moduledict_rapidfuzz$_utils,
                mod_consts[27],
                const_int_0
            );
        } else {
            tmp_assign_source_10 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_3, mod_consts[27]);
        }

        if (tmp_assign_source_10 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 8;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[27], tmp_assign_source_10);
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
        PyObject *tmp_assign_source_11;
        tmp_assign_source_11 = Py_None;
        UPDATE_STRING_DICT0(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[0], tmp_assign_source_11);
    }
    {
        PyObject *tmp_assign_source_12;


        tmp_assign_source_12 = MAKE_FUNCTION_rapidfuzz$_utils$$36$$$36$$$36$function__1_setupPandas(tstate);

        UPDATE_STRING_DICT1(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[28], tmp_assign_source_12);
    }
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_call_result_1;
        tmp_called_value_1 = module_var_accessor_rapidfuzz$$36$_utils$setupPandas(tstate);
        assert(!(tmp_called_value_1 == NULL));
        frame_frame_rapidfuzz$_utils->m_frame.f_lineno = 21;
        tmp_call_result_1 = CALL_FUNCTION_NO_ARGS(tstate, tmp_called_value_1);
        if (tmp_call_result_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 21;

            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_1);
    }
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
        {
            PyObject *tmp_set_locals_1;
            CHECK_OBJECT(tmp_class_creation_1__prepared);
            tmp_set_locals_1 = tmp_class_creation_1__prepared;
            locals_rapidfuzz$_utils$$36$$$36$$$36$class__1_ScorerFlag_24 = tmp_set_locals_1;
            Py_INCREF(tmp_set_locals_1);
        }
        tmp_dictset_value = mod_consts[29];
        tmp_result = DICT_SET_ITEM(locals_rapidfuzz$_utils$$36$$$36$$$36$class__1_ScorerFlag_24, mod_consts[30], tmp_dictset_value);
        assert(!(tmp_result == false));
        tmp_dictset_value = mod_consts[9];
        tmp_result = DICT_SET_ITEM(locals_rapidfuzz$_utils$$36$$$36$$$36$class__1_ScorerFlag_24, mod_consts[31], tmp_dictset_value);
        assert(!(tmp_result == false));
        tmp_dictset_value = mod_consts[32];
        tmp_result = DICT_SET_ITEM(locals_rapidfuzz$_utils$$36$$$36$$$36$class__1_ScorerFlag_24, mod_consts[12], tmp_dictset_value);
        assert(!(tmp_result == false));
        tmp_dictset_value = mod_consts[33];
        tmp_result = DICT_SET_ITEM(locals_rapidfuzz$_utils$$36$$$36$$$36$class__1_ScorerFlag_24, mod_consts[34], tmp_dictset_value);
        assert(!(tmp_result == false));
        tmp_dictset_value = mod_consts[35];
        tmp_result = DICT_SET_ITEM(locals_rapidfuzz$_utils$$36$$$36$$$36$class__1_ScorerFlag_24, mod_consts[10], tmp_dictset_value);
        assert(!(tmp_result == false));
        tmp_dictset_value = mod_consts[36];
        tmp_result = DICT_SET_ITEM(locals_rapidfuzz$_utils$$36$$$36$$$36$class__1_ScorerFlag_24, mod_consts[11], tmp_dictset_value);
        assert(!(tmp_result == false));
        // Tried code:
        // Tried code:
        {
            PyObject *tmp_assign_source_16;
            PyObject *tmp_called_value_2;
            PyObject *tmp_args_value_1;
            PyObject *tmp_tuple_element_1;
            PyObject *tmp_kwargs_value_1;
            tmp_called_value_2 = (PyObject *)&PyType_Type;
            tmp_tuple_element_1 = mod_consts[9];
            tmp_args_value_1 = MAKE_TUPLE_EMPTY(tstate, 3);
            PyTuple_SET_ITEM0(tmp_args_value_1, 0, tmp_tuple_element_1);
            tmp_tuple_element_1 = const_tuple_empty;
            PyTuple_SET_ITEM0(tmp_args_value_1, 1, tmp_tuple_element_1);
            tmp_tuple_element_1 = locals_rapidfuzz$_utils$$36$$$36$$$36$class__1_ScorerFlag_24;
            PyTuple_SET_ITEM0(tmp_args_value_1, 2, tmp_tuple_element_1);
            CHECK_OBJECT(tmp_class_creation_1__class_decl_dict);
            tmp_kwargs_value_1 = tmp_class_creation_1__class_decl_dict;
            frame_frame_rapidfuzz$_utils->m_frame.f_lineno = 24;
            tmp_assign_source_16 = CALL_FUNCTION(tstate, tmp_called_value_2, tmp_args_value_1, tmp_kwargs_value_1);
            Py_DECREF(tmp_args_value_1);
            if (tmp_assign_source_16 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 24;

                goto try_except_handler_4;
            }
            assert(outline_0_var___class__ == NULL);
            outline_0_var___class__ = tmp_assign_source_16;
        }
        CHECK_OBJECT(outline_0_var___class__);
        tmp_assign_source_15 = outline_0_var___class__;
        Py_INCREF(tmp_assign_source_15);
        goto try_return_handler_4;
        NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
        return NULL;
        // Return handler code:
        try_return_handler_4:;
        Py_DECREF(locals_rapidfuzz$_utils$$36$$$36$$$36$class__1_ScorerFlag_24);
        locals_rapidfuzz$_utils$$36$$$36$$$36$class__1_ScorerFlag_24 = NULL;
        goto try_return_handler_3;
        // Exception handler code:
        try_except_handler_4:;
        exception_keeper_lineno_2 = exception_lineno;
        exception_lineno = 0;
        exception_keeper_name_2 = exception_state;
        INIT_ERROR_OCCURRED_STATE(&exception_state);

        Py_DECREF(locals_rapidfuzz$_utils$$36$$$36$$$36$class__1_ScorerFlag_24);
        locals_rapidfuzz$_utils$$36$$$36$$$36$class__1_ScorerFlag_24 = NULL;
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
        UPDATE_STRING_DICT1(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[9], tmp_assign_source_15);
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
        PyObject *tmp_assign_source_17;
        PyObject *tmp_annotations_1;
        tmp_annotations_1 = DICT_COPY(tstate, mod_consts[37]);


        tmp_assign_source_17 = MAKE_FUNCTION_rapidfuzz$_utils$$36$$$36$$$36$function__2__get_scorer_flags_distance(tstate, tmp_annotations_1);

        UPDATE_STRING_DICT1(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[38], tmp_assign_source_17);
    }
    {
        PyObject *tmp_assign_source_18;
        PyObject *tmp_annotations_2;
        tmp_annotations_2 = DICT_COPY(tstate, mod_consts[37]);


        tmp_assign_source_18 = MAKE_FUNCTION_rapidfuzz$_utils$$36$$$36$$$36$function__3__get_scorer_flags_similarity(tstate, tmp_annotations_2);

        UPDATE_STRING_DICT1(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[39], tmp_assign_source_18);
    }
    {
        PyObject *tmp_assign_source_19;
        PyObject *tmp_annotations_3;
        tmp_annotations_3 = DICT_COPY(tstate, mod_consts[37]);


        tmp_assign_source_19 = MAKE_FUNCTION_rapidfuzz$_utils$$36$$$36$$$36$function__4__get_scorer_flags_normalized_distance(tstate, tmp_annotations_3);

        UPDATE_STRING_DICT1(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[40], tmp_assign_source_19);
    }
    {
        PyObject *tmp_assign_source_20;
        PyObject *tmp_annotations_4;
        tmp_annotations_4 = DICT_COPY(tstate, mod_consts[37]);


        tmp_assign_source_20 = MAKE_FUNCTION_rapidfuzz$_utils$$36$$$36$$$36$function__5__get_scorer_flags_normalized_similarity(tstate, tmp_annotations_4);

        UPDATE_STRING_DICT1(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[41], tmp_assign_source_20);
    }
    {
        PyObject *tmp_assign_source_21;
        PyObject *tmp_annotations_5;
        tmp_annotations_5 = DICT_COPY(tstate, mod_consts[42]);


        tmp_assign_source_21 = MAKE_FUNCTION_rapidfuzz$_utils$$36$$$36$$$36$function__6_is_none(tstate, tmp_annotations_5);

        UPDATE_STRING_DICT1(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[43], tmp_assign_source_21);
    }
    {
        PyObject *tmp_assign_source_22;
        PyObject *tmp_annotations_6;
        tmp_annotations_6 = DICT_COPY(tstate, mod_consts[44]);


        tmp_assign_source_22 = MAKE_FUNCTION_rapidfuzz$_utils$$36$$$36$$$36$function__7_add_scorer_attrs(tstate, tmp_annotations_6);

        UPDATE_STRING_DICT1(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[45], tmp_assign_source_22);
    }
    {
        PyObject *tmp_assign_source_23;
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[46];
        tmp_dict_value_1 = module_var_accessor_rapidfuzz$$36$_utils$_get_scorer_flags_distance(tstate);
        assert(!(tmp_dict_value_1 == NULL));
        tmp_assign_source_23 = _PyDict_NewPresized( 1 );
        tmp_res = PyDict_SetItem(tmp_assign_source_23, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        UPDATE_STRING_DICT1(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[47], tmp_assign_source_23);
    }
    {
        PyObject *tmp_ass_subvalue_1;
        PyObject *tmp_ass_subscribed_1;
        PyObject *tmp_ass_subscript_1;
        tmp_ass_subvalue_1 = mod_consts[48];
        tmp_ass_subscribed_1 = module_var_accessor_rapidfuzz$$36$_utils$__annotations__(tstate);
        if (unlikely(tmp_ass_subscribed_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[21]);
        }

        if (tmp_ass_subscribed_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 79;

            goto frame_exception_exit_1;
        }
        tmp_ass_subscript_1 = mod_consts[47];
        tmp_result = SET_SUBSCRIPT(tstate, tmp_ass_subscribed_1, tmp_ass_subscript_1, tmp_ass_subvalue_1);
        if (tmp_result == false) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 79;

            goto frame_exception_exit_1;
        }
    }
    {
        PyObject *tmp_assign_source_24;
        PyObject *tmp_dict_key_2;
        PyObject *tmp_dict_value_2;
        tmp_dict_key_2 = mod_consts[46];
        tmp_dict_value_2 = module_var_accessor_rapidfuzz$$36$_utils$_get_scorer_flags_similarity(tstate);
        if (unlikely(tmp_dict_value_2 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[39]);
        }

        if (tmp_dict_value_2 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 81;

            goto frame_exception_exit_1;
        }
        tmp_assign_source_24 = _PyDict_NewPresized( 1 );
        tmp_res = PyDict_SetItem(tmp_assign_source_24, tmp_dict_key_2, tmp_dict_value_2);
        assert(!(tmp_res != 0));
        UPDATE_STRING_DICT1(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[49], tmp_assign_source_24);
    }
    {
        PyObject *tmp_ass_subvalue_2;
        PyObject *tmp_ass_subscribed_2;
        PyObject *tmp_ass_subscript_2;
        tmp_ass_subvalue_2 = mod_consts[48];
        tmp_ass_subscribed_2 = module_var_accessor_rapidfuzz$$36$_utils$__annotations__(tstate);
        if (unlikely(tmp_ass_subscribed_2 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[21]);
        }

        if (tmp_ass_subscribed_2 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 80;

            goto frame_exception_exit_1;
        }
        tmp_ass_subscript_2 = mod_consts[49];
        tmp_result = SET_SUBSCRIPT(tstate, tmp_ass_subscribed_2, tmp_ass_subscript_2, tmp_ass_subvalue_2);
        if (tmp_result == false) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 80;

            goto frame_exception_exit_1;
        }
    }
    {
        PyObject *tmp_assign_source_25;
        PyObject *tmp_dict_key_3;
        PyObject *tmp_dict_value_3;
        tmp_dict_key_3 = mod_consts[46];
        tmp_dict_value_3 = module_var_accessor_rapidfuzz$$36$_utils$_get_scorer_flags_normalized_distance(tstate);
        if (unlikely(tmp_dict_value_3 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[40]);
        }

        if (tmp_dict_value_3 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 84;

            goto frame_exception_exit_1;
        }
        tmp_assign_source_25 = _PyDict_NewPresized( 1 );
        tmp_res = PyDict_SetItem(tmp_assign_source_25, tmp_dict_key_3, tmp_dict_value_3);
        assert(!(tmp_res != 0));
        UPDATE_STRING_DICT1(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[50], tmp_assign_source_25);
    }
    {
        PyObject *tmp_ass_subvalue_3;
        PyObject *tmp_ass_subscribed_3;
        PyObject *tmp_ass_subscript_3;
        tmp_ass_subvalue_3 = mod_consts[48];
        tmp_ass_subscribed_3 = module_var_accessor_rapidfuzz$$36$_utils$__annotations__(tstate);
        if (unlikely(tmp_ass_subscribed_3 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[21]);
        }

        if (tmp_ass_subscribed_3 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 83;

            goto frame_exception_exit_1;
        }
        tmp_ass_subscript_3 = mod_consts[50];
        tmp_result = SET_SUBSCRIPT(tstate, tmp_ass_subscribed_3, tmp_ass_subscript_3, tmp_ass_subvalue_3);
        if (tmp_result == false) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 83;

            goto frame_exception_exit_1;
        }
    }
    {
        PyObject *tmp_assign_source_26;
        PyObject *tmp_dict_key_4;
        PyObject *tmp_dict_value_4;
        tmp_dict_key_4 = mod_consts[46];
        tmp_dict_value_4 = module_var_accessor_rapidfuzz$$36$_utils$_get_scorer_flags_normalized_similarity(tstate);
        if (unlikely(tmp_dict_value_4 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[41]);
        }

        if (tmp_dict_value_4 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 87;

            goto frame_exception_exit_1;
        }
        tmp_assign_source_26 = _PyDict_NewPresized( 1 );
        tmp_res = PyDict_SetItem(tmp_assign_source_26, tmp_dict_key_4, tmp_dict_value_4);
        assert(!(tmp_res != 0));
        UPDATE_STRING_DICT1(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)mod_consts[51], tmp_assign_source_26);
    }
    {
        PyObject *tmp_ass_subvalue_4;
        PyObject *tmp_ass_subscribed_4;
        PyObject *tmp_ass_subscript_4;
        tmp_ass_subvalue_4 = mod_consts[48];
        tmp_ass_subscribed_4 = module_var_accessor_rapidfuzz$$36$_utils$__annotations__(tstate);
        if (unlikely(tmp_ass_subscribed_4 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[21]);
        }

        if (tmp_ass_subscribed_4 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 86;

            goto frame_exception_exit_1;
        }
        tmp_ass_subscript_4 = mod_consts[51];
        tmp_result = SET_SUBSCRIPT(tstate, tmp_ass_subscribed_4, tmp_ass_subscript_4, tmp_ass_subvalue_4);
        if (tmp_result == false) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 86;

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
            exception_tb = MAKE_TRACEBACK(frame_frame_rapidfuzz$_utils, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_rapidfuzz$_utils->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_rapidfuzz$_utils, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }



    assertFrameObject(frame_frame_rapidfuzz$_utils);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto module_exception_exit;
    frame_no_exception_1:;

    // Report to PGO about leaving the module without error.
    PGO_onModuleExit("rapidfuzz$_utils", false);

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *post_load = IMPORT_EMBEDDED_MODULE(tstate, "rapidfuzz._utils" "-postLoad");
        if (post_load == NULL) {
            return NULL;
        }
    }
#endif

    Py_INCREF(module_rapidfuzz$_utils);
    return module_rapidfuzz$_utils;
    module_exception_exit:

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$_utils, (Nuitka_StringObject *)const_str_plain___name__);

        if (module_name != NULL) {
            Nuitka_DelModule(tstate, module_name);
        }
    }
#endif
    PGO_onModuleExit("rapidfuzz$_utils", false);

    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);
    return NULL;
}
