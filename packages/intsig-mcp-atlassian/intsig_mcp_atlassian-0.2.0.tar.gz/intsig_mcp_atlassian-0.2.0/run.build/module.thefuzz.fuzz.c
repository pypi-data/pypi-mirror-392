/* Generated code for Python module 'thefuzz$fuzz'
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

/* The "module_thefuzz$fuzz" is a Python object pointer of module type.
 *
 * Note: For full compatibility with CPython, every module variable access
 * needs to go through it except for cases where the module cannot possibly
 * have changed in the mean time.
 */

PyObject *module_thefuzz$fuzz;
PyDictObject *moduledict_thefuzz$fuzz;

/* The declarations of module constants used, if any. */
static PyObject *mod_consts[50];
#ifndef __NUITKA_NO_ASSERT__
static Py_hash_t mod_consts_hash[50];
#endif

static PyObject *module_filename_obj = NULL;

/* Indicator if this modules private constants were created yet. */
static bool constants_created = false;

/* Function to create module private constants. */
static void createModuleConstants(PyThreadState *tstate) {
    if (constants_created == false) {
        loadConstantsBlob(tstate, &mod_consts[0], UN_TRANSLATE("thefuzz.fuzz"));
        constants_created = true;

#ifndef __NUITKA_NO_ASSERT__
        for (int i = 0; i < 50; i++) {
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
void checkModuleConstants_thefuzz$fuzz(PyThreadState *tstate) {
    // The module may not have been used at all, then ignore this.
    if (constants_created == false) return;

    for (int i = 0; i < 50; i++) {
        assert(mod_consts_hash[i] == DEEP_HASH(tstate, mod_consts[i]));
        CHECK_OBJECT_DEEP(mod_consts[i]);
    }
}
#endif

// Helper to preserving module variables for Python3.11+
#if 13
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
static PyObject *module_var_accessor_thefuzz$$36$fuzz$QRatio(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_thefuzz$fuzz->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_thefuzz$fuzz->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[17]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_thefuzz$fuzz->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[17]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[17], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[17]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[17], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[17]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[17]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[17]);
    }

    return result;
}

static PyObject *module_var_accessor_thefuzz$$36$fuzz$WRatio(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_thefuzz$fuzz->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_thefuzz$fuzz->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[22]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_thefuzz$fuzz->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[22]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[22], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[22]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[22], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[22]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[22]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[22]);
    }

    return result;
}

static PyObject *module_var_accessor_thefuzz$$36$fuzz$_QRatio(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_thefuzz$fuzz->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_thefuzz$fuzz->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[15]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_thefuzz$fuzz->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[15]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[15], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[15]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[15], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[15]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[15]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[15]);
    }

    return result;
}

static PyObject *module_var_accessor_thefuzz$$36$fuzz$_WRatio(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_thefuzz$fuzz->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_thefuzz$fuzz->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[20]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_thefuzz$fuzz->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[20]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[20]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[20]);
    }

    return result;
}

static PyObject *module_var_accessor_thefuzz$$36$fuzz$__spec__(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_thefuzz$fuzz->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_thefuzz$fuzz->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[49]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_thefuzz$fuzz->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[49]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[49], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[49]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[49], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[49]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[49]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[49]);
    }

    return result;
}

static PyObject *module_var_accessor_thefuzz$$36$fuzz$_partial_ratio(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_thefuzz$fuzz->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_thefuzz$fuzz->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[7]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_thefuzz$fuzz->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[7]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[7]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[7]);
    }

    return result;
}

static PyObject *module_var_accessor_thefuzz$$36$fuzz$_partial_token_set_ratio(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_thefuzz$fuzz->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_thefuzz$fuzz->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[14]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_thefuzz$fuzz->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[14]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[14], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[14]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[14], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[14]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[14]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[14]);
    }

    return result;
}

static PyObject *module_var_accessor_thefuzz$$36$fuzz$_partial_token_sort_ratio(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_thefuzz$fuzz->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_thefuzz$fuzz->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[11]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_thefuzz$fuzz->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[11]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[11], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[11]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[11], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[11]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[11]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[11]);
    }

    return result;
}

static PyObject *module_var_accessor_thefuzz$$36$fuzz$_rapidfuzz_scorer(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_thefuzz$fuzz->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_thefuzz$fuzz->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[5]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_thefuzz$fuzz->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[5]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[5]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[5]);
    }

    return result;
}

static PyObject *module_var_accessor_thefuzz$$36$fuzz$_ratio(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_thefuzz$fuzz->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_thefuzz$fuzz->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[6]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_thefuzz$fuzz->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[6]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[6], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[6]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[6], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[6]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[6]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[6]);
    }

    return result;
}

static PyObject *module_var_accessor_thefuzz$$36$fuzz$_token_set_ratio(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_thefuzz$fuzz->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_thefuzz$fuzz->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[13]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_thefuzz$fuzz->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[13]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[13]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[13]);
    }

    return result;
}

static PyObject *module_var_accessor_thefuzz$$36$fuzz$_token_sort_ratio(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_thefuzz$fuzz->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_thefuzz$fuzz->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[9]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_thefuzz$fuzz->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[9]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[9]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[9]);
    }

    return result;
}

static PyObject *module_var_accessor_thefuzz$$36$fuzz$utils(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_thefuzz$fuzz->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_thefuzz$fuzz->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[0]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_thefuzz$fuzz->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[0]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[0]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[0]);
    }

    return result;
}


#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
// The module code objects.
static PyCodeObject *code_objects_5070a8a80e2d3edc4dd6e1ba123f4623;
static PyCodeObject *code_objects_d0e7fd67e2d64f4b88b6ea4915c75365;
static PyCodeObject *code_objects_52501d05ba479b3778365fa632a1984d;
static PyCodeObject *code_objects_c1d2f7884d672d6c8954a72e8c096144;
static PyCodeObject *code_objects_f7aa1f3ca1b54c6947a27b13e783ddba;
static PyCodeObject *code_objects_f7a8e86a6deda9053888055f29944847;
static PyCodeObject *code_objects_8645436159ae0cea7144824ea223db26;
static PyCodeObject *code_objects_b693b319b4a3c2d48ede0bbcd85790f0;
static PyCodeObject *code_objects_d3e234be0084b933b9c2718fe6a84686;
static PyCodeObject *code_objects_767fa27878300320332448f01a9fe469;
static PyCodeObject *code_objects_cb06d54bad097f74f06b10342065e8e8;
static PyCodeObject *code_objects_ba21d2988bb293d7e4d4b9bb2eba5226;

static void createModuleCodeObjects(void) {
    module_filename_obj = MAKE_RELATIVE_PATH(mod_consts[43]); CHECK_OBJECT(module_filename_obj);
    code_objects_5070a8a80e2d3edc4dd6e1ba123f4623 = MAKE_CODE_OBJECT(module_filename_obj, 1, CO_NOFREE, mod_consts[44], mod_consts[44], NULL, NULL, 0, 0, 0);
    code_objects_d0e7fd67e2d64f4b88b6ea4915c75365 = MAKE_CODE_OBJECT(module_filename_obj, 88, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[17], mod_consts[17], mod_consts[45], NULL, 4, 0, 0);
    code_objects_52501d05ba479b3778365fa632a1984d = MAKE_CODE_OBJECT(module_filename_obj, 104, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[41], mod_consts[41], mod_consts[46], NULL, 3, 0, 0);
    code_objects_c1d2f7884d672d6c8954a72e8c096144 = MAKE_CODE_OBJECT(module_filename_obj, 155, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[42], mod_consts[42], mod_consts[46], NULL, 3, 0, 0);
    code_objects_f7aa1f3ca1b54c6947a27b13e783ddba = MAKE_CODE_OBJECT(module_filename_obj, 118, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[22], mod_consts[22], mod_consts[45], NULL, 4, 0, 0);
    code_objects_f7a8e86a6deda9053888055f29944847 = MAKE_CODE_OBJECT(module_filename_obj, 21, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[5], mod_consts[5], mod_consts[47], NULL, 5, 0, 0);
    code_objects_8645436159ae0cea7144824ea223db26 = MAKE_CODE_OBJECT(module_filename_obj, 39, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[32], mod_consts[32], mod_consts[48], NULL, 2, 0, 0);
    code_objects_b693b319b4a3c2d48ede0bbcd85790f0 = MAKE_CODE_OBJECT(module_filename_obj, 77, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[35], mod_consts[35], mod_consts[45], NULL, 4, 0, 0);
    code_objects_d3e234be0084b933b9c2718fe6a84686 = MAKE_CODE_OBJECT(module_filename_obj, 63, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[36], mod_consts[36], mod_consts[45], NULL, 4, 0, 0);
    code_objects_767fa27878300320332448f01a9fe469 = MAKE_CODE_OBJECT(module_filename_obj, 35, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[31], mod_consts[31], mod_consts[48], NULL, 2, 0, 0);
    code_objects_cb06d54bad097f74f06b10342065e8e8 = MAKE_CODE_OBJECT(module_filename_obj, 73, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[33], mod_consts[33], mod_consts[45], NULL, 4, 0, 0);
    code_objects_ba21d2988bb293d7e4d4b9bb2eba5226 = MAKE_CODE_OBJECT(module_filename_obj, 55, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[34], mod_consts[34], mod_consts[45], NULL, 4, 0, 0);
}
#endif

// The module function declarations.
static PyObject *MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio(PyThreadState *tstate, PyObject *defaults);


static PyObject *MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio(PyThreadState *tstate, PyObject *defaults);


static PyObject *MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio(PyThreadState *tstate, PyObject *defaults);


static PyObject *MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio(PyThreadState *tstate, PyObject *defaults);


static PyObject *MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio(PyThreadState *tstate, PyObject *defaults);


static PyObject *MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio(PyThreadState *tstate, PyObject *defaults);


static PyObject *MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio(PyThreadState *tstate, PyObject *defaults);


static PyObject *MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio(PyThreadState *tstate, PyObject *defaults);


// The module function definitions.
static PyObject *impl_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_scorer = python_pars[0];
    PyObject *par_s1 = python_pars[1];
    PyObject *par_s2 = python_pars[2];
    PyObject *par_force_ascii = python_pars[3];
    PyObject *par_full_process = python_pars[4];
    struct Nuitka_FrameObject *frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    PyObject *tmp_return_value = NULL;
    static struct Nuitka_FrameObject *cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;

    // Actual function body.
    // Tried code:
    if (isFrameUnusable(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer)) {
        Py_XDECREF(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer = MAKE_FUNCTION_FRAME(tstate, code_objects_f7a8e86a6deda9053888055f29944847, module_thefuzz$fuzz, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer->m_type_description == NULL);
    frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer = cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer);
    assert(Py_REFCNT(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer) == 2);

    // Framed code:
    {
        nuitka_bool tmp_condition_result_1;
        int tmp_truth_name_1;
        CHECK_OBJECT(par_full_process);
        tmp_truth_name_1 = CHECK_IF_TRUE(par_full_process);
        if (tmp_truth_name_1 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 25;
            type_description_1 = "ooooo";
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
        bool tmp_condition_result_2;
        int tmp_or_left_truth_1;
        bool tmp_or_left_value_1;
        bool tmp_or_right_value_1;
        PyObject *tmp_cmp_expr_left_1;
        PyObject *tmp_cmp_expr_right_1;
        PyObject *tmp_cmp_expr_left_2;
        PyObject *tmp_cmp_expr_right_2;
        CHECK_OBJECT(par_s1);
        tmp_cmp_expr_left_1 = par_s1;
        tmp_cmp_expr_right_1 = Py_None;
        tmp_or_left_value_1 = (tmp_cmp_expr_left_1 == tmp_cmp_expr_right_1) ? true : false;
        tmp_or_left_truth_1 = tmp_or_left_value_1 != false ? 1 : 0;
        if (tmp_or_left_truth_1 == 1) {
            goto or_left_1;
        } else {
            goto or_right_1;
        }
        or_right_1:;
        CHECK_OBJECT(par_s2);
        tmp_cmp_expr_left_2 = par_s2;
        tmp_cmp_expr_right_2 = Py_None;
        tmp_or_right_value_1 = (tmp_cmp_expr_left_2 == tmp_cmp_expr_right_2) ? true : false;
        tmp_condition_result_2 = tmp_or_right_value_1;
        goto or_end_1;
        or_left_1:;
        tmp_condition_result_2 = tmp_or_left_value_1;
        or_end_1:;
        if (tmp_condition_result_2 != false) {
            goto branch_yes_2;
        } else {
            goto branch_no_2;
        }
    }
    branch_yes_2:;
    tmp_return_value = const_int_0;
    Py_INCREF(tmp_return_value);
    goto frame_return_exit_1;
    branch_no_2:;
    {
        PyObject *tmp_assign_source_1;
        PyObject *tmp_called_value_1;
        PyObject *tmp_expression_value_1;
        PyObject *tmp_kw_call_arg_value_0_1;
        PyObject *tmp_kw_call_dict_value_0_1;
        tmp_expression_value_1 = module_var_accessor_thefuzz$$36$fuzz$utils(tstate);
        if (unlikely(tmp_expression_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[0]);
        }

        if (tmp_expression_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 29;
            type_description_1 = "ooooo";
            goto frame_exception_exit_1;
        }
        tmp_called_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[1]);
        if (tmp_called_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 29;
            type_description_1 = "ooooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_s1);
        tmp_kw_call_arg_value_0_1 = par_s1;
        CHECK_OBJECT(par_force_ascii);
        tmp_kw_call_dict_value_0_1 = par_force_ascii;
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer->m_frame.f_lineno = 29;
        {
            PyObject *args[] = {tmp_kw_call_arg_value_0_1};
            PyObject *kw_values[1] = {tmp_kw_call_dict_value_0_1};
            tmp_assign_source_1 = CALL_FUNCTION_WITH_ARGS1_KW_SPLIT(tstate, tmp_called_value_1, args, kw_values, mod_consts[2]);
        }

        Py_DECREF(tmp_called_value_1);
        if (tmp_assign_source_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 29;
            type_description_1 = "ooooo";
            goto frame_exception_exit_1;
        }
        {
            PyObject *old = par_s1;
            assert(old != NULL);
            par_s1 = tmp_assign_source_1;
            Py_DECREF(old);
        }

    }
    {
        PyObject *tmp_assign_source_2;
        PyObject *tmp_called_value_2;
        PyObject *tmp_expression_value_2;
        PyObject *tmp_kw_call_arg_value_0_2;
        PyObject *tmp_kw_call_dict_value_0_2;
        tmp_expression_value_2 = module_var_accessor_thefuzz$$36$fuzz$utils(tstate);
        if (unlikely(tmp_expression_value_2 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[0]);
        }

        if (tmp_expression_value_2 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 30;
            type_description_1 = "ooooo";
            goto frame_exception_exit_1;
        }
        tmp_called_value_2 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_2, mod_consts[1]);
        if (tmp_called_value_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 30;
            type_description_1 = "ooooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_s2);
        tmp_kw_call_arg_value_0_2 = par_s2;
        CHECK_OBJECT(par_force_ascii);
        tmp_kw_call_dict_value_0_2 = par_force_ascii;
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer->m_frame.f_lineno = 30;
        {
            PyObject *args[] = {tmp_kw_call_arg_value_0_2};
            PyObject *kw_values[1] = {tmp_kw_call_dict_value_0_2};
            tmp_assign_source_2 = CALL_FUNCTION_WITH_ARGS1_KW_SPLIT(tstate, tmp_called_value_2, args, kw_values, mod_consts[2]);
        }

        Py_DECREF(tmp_called_value_2);
        if (tmp_assign_source_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 30;
            type_description_1 = "ooooo";
            goto frame_exception_exit_1;
        }
        {
            PyObject *old = par_s2;
            assert(old != NULL);
            par_s2 = tmp_assign_source_2;
            Py_DECREF(old);
        }

    }
    branch_no_1:;
    {
        PyObject *tmp_int_arg_1;
        PyObject *tmp_called_value_3;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_called_value_4;
        PyObject *tmp_args_element_value_2;
        PyObject *tmp_args_element_value_3;
        tmp_called_value_3 = LOOKUP_BUILTIN(mod_consts[3]);
        assert(tmp_called_value_3 != NULL);
        CHECK_OBJECT(par_scorer);
        tmp_called_value_4 = par_scorer;
        CHECK_OBJECT(par_s1);
        tmp_args_element_value_2 = par_s1;
        CHECK_OBJECT(par_s2);
        tmp_args_element_value_3 = par_s2;
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer->m_frame.f_lineno = 32;
        {
            PyObject *call_args[] = {tmp_args_element_value_2, tmp_args_element_value_3};
            tmp_args_element_value_1 = CALL_FUNCTION_WITH_ARGS2(tstate, tmp_called_value_4, call_args);
        }

        if (tmp_args_element_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 32;
            type_description_1 = "ooooo";
            goto frame_exception_exit_1;
        }
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer->m_frame.f_lineno = 32;
        tmp_int_arg_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_3, tmp_args_element_value_1);
        Py_DECREF(tmp_args_element_value_1);
        if (tmp_int_arg_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 32;
            type_description_1 = "ooooo";
            goto frame_exception_exit_1;
        }
        tmp_return_value = PyNumber_Int(tmp_int_arg_1);
        Py_DECREF(tmp_int_arg_1);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 32;
            type_description_1 = "ooooo";
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
            exception_tb = MAKE_TRACEBACK(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer,
        type_description_1,
        par_scorer,
        par_s1,
        par_s2,
        par_force_ascii,
        par_full_process
    );


    // Release cached frame if used for exception.
    if (frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer == cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer);
        cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer = NULL;
    }

    assertFrameObject(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Return handler code:
    try_return_handler_1:;
    Py_XDECREF(par_s1);
    par_s1 = NULL;
    Py_XDECREF(par_s2);
    par_s2 = NULL;
    goto function_return_exit;
    // Exception handler code:
    try_except_handler_1:;
    exception_keeper_lineno_1 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_1 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    Py_XDECREF(par_s1);
    par_s1 = NULL;
    Py_XDECREF(par_s2);
    par_s2 = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_1;
    exception_lineno = exception_keeper_lineno_1;

    goto function_exception_exit;
    // End of try:

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_scorer);
    Py_DECREF(par_scorer);
    CHECK_OBJECT(par_force_ascii);
    Py_DECREF(par_force_ascii);
    CHECK_OBJECT(par_full_process);
    Py_DECREF(par_full_process);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_scorer);
    Py_DECREF(par_scorer);
    CHECK_OBJECT(par_force_ascii);
    Py_DECREF(par_force_ascii);
    CHECK_OBJECT(par_full_process);
    Py_DECREF(par_full_process);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_s1 = python_pars[0];
    PyObject *par_s2 = python_pars[1];
    struct Nuitka_FrameObject *frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio)) {
        Py_XDECREF(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio = MAKE_FUNCTION_FRAME(tstate, code_objects_767fa27878300320332448f01a9fe469, module_thefuzz$fuzz, sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio->m_type_description == NULL);
    frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio = cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio);
    assert(Py_REFCNT(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_args_element_value_2;
        PyObject *tmp_args_element_value_3;
        PyObject *tmp_args_element_value_4;
        PyObject *tmp_args_element_value_5;
        tmp_called_value_1 = module_var_accessor_thefuzz$$36$fuzz$_rapidfuzz_scorer(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 36;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        tmp_args_element_value_1 = module_var_accessor_thefuzz$$36$fuzz$_ratio(tstate);
        if (unlikely(tmp_args_element_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[6]);
        }

        if (tmp_args_element_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 36;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_s1);
        tmp_args_element_value_2 = par_s1;
        CHECK_OBJECT(par_s2);
        tmp_args_element_value_3 = par_s2;
        tmp_args_element_value_4 = Py_False;
        tmp_args_element_value_5 = Py_False;
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio->m_frame.f_lineno = 36;
        {
            PyObject *call_args[] = {tmp_args_element_value_1, tmp_args_element_value_2, tmp_args_element_value_3, tmp_args_element_value_4, tmp_args_element_value_5};
            tmp_return_value = CALL_FUNCTION_WITH_ARGS5(tstate, tmp_called_value_1, call_args);
        }

        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 36;
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
            exception_tb = MAKE_TRACEBACK(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio,
        type_description_1,
        par_s1,
        par_s2
    );


    // Release cached frame if used for exception.
    if (frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio == cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio);
        cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio = NULL;
    }

    assertFrameObject(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_s1);
    Py_DECREF(par_s1);
    CHECK_OBJECT(par_s2);
    Py_DECREF(par_s2);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_s1);
    Py_DECREF(par_s1);
    CHECK_OBJECT(par_s2);
    Py_DECREF(par_s2);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_s1 = python_pars[0];
    PyObject *par_s2 = python_pars[1];
    struct Nuitka_FrameObject *frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio)) {
        Py_XDECREF(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio = MAKE_FUNCTION_FRAME(tstate, code_objects_8645436159ae0cea7144824ea223db26, module_thefuzz$fuzz, sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio->m_type_description == NULL);
    frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio = cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio);
    assert(Py_REFCNT(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_args_element_value_2;
        PyObject *tmp_args_element_value_3;
        PyObject *tmp_args_element_value_4;
        PyObject *tmp_args_element_value_5;
        tmp_called_value_1 = module_var_accessor_thefuzz$$36$fuzz$_rapidfuzz_scorer(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 44;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        tmp_args_element_value_1 = module_var_accessor_thefuzz$$36$fuzz$_partial_ratio(tstate);
        if (unlikely(tmp_args_element_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[7]);
        }

        if (tmp_args_element_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 44;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_s1);
        tmp_args_element_value_2 = par_s1;
        CHECK_OBJECT(par_s2);
        tmp_args_element_value_3 = par_s2;
        tmp_args_element_value_4 = Py_False;
        tmp_args_element_value_5 = Py_False;
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio->m_frame.f_lineno = 44;
        {
            PyObject *call_args[] = {tmp_args_element_value_1, tmp_args_element_value_2, tmp_args_element_value_3, tmp_args_element_value_4, tmp_args_element_value_5};
            tmp_return_value = CALL_FUNCTION_WITH_ARGS5(tstate, tmp_called_value_1, call_args);
        }

        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 44;
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
            exception_tb = MAKE_TRACEBACK(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio,
        type_description_1,
        par_s1,
        par_s2
    );


    // Release cached frame if used for exception.
    if (frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio == cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio);
        cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio = NULL;
    }

    assertFrameObject(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_s1);
    Py_DECREF(par_s1);
    CHECK_OBJECT(par_s2);
    Py_DECREF(par_s2);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_s1);
    Py_DECREF(par_s1);
    CHECK_OBJECT(par_s2);
    Py_DECREF(par_s2);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_s1 = python_pars[0];
    PyObject *par_s2 = python_pars[1];
    PyObject *par_force_ascii = python_pars[2];
    PyObject *par_full_process = python_pars[3];
    struct Nuitka_FrameObject *frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio)) {
        Py_XDECREF(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio = MAKE_FUNCTION_FRAME(tstate, code_objects_ba21d2988bb293d7e4d4b9bb2eba5226, module_thefuzz$fuzz, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio->m_type_description == NULL);
    frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio = cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio);
    assert(Py_REFCNT(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_args_element_value_2;
        PyObject *tmp_args_element_value_3;
        PyObject *tmp_args_element_value_4;
        PyObject *tmp_args_element_value_5;
        tmp_called_value_1 = module_var_accessor_thefuzz$$36$fuzz$_rapidfuzz_scorer(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 60;
            type_description_1 = "oooo";
            goto frame_exception_exit_1;
        }
        tmp_args_element_value_1 = module_var_accessor_thefuzz$$36$fuzz$_token_sort_ratio(tstate);
        if (unlikely(tmp_args_element_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[9]);
        }

        if (tmp_args_element_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 60;
            type_description_1 = "oooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_s1);
        tmp_args_element_value_2 = par_s1;
        CHECK_OBJECT(par_s2);
        tmp_args_element_value_3 = par_s2;
        CHECK_OBJECT(par_force_ascii);
        tmp_args_element_value_4 = par_force_ascii;
        CHECK_OBJECT(par_full_process);
        tmp_args_element_value_5 = par_full_process;
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio->m_frame.f_lineno = 60;
        {
            PyObject *call_args[] = {tmp_args_element_value_1, tmp_args_element_value_2, tmp_args_element_value_3, tmp_args_element_value_4, tmp_args_element_value_5};
            tmp_return_value = CALL_FUNCTION_WITH_ARGS5(tstate, tmp_called_value_1, call_args);
        }

        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 60;
            type_description_1 = "oooo";
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
            exception_tb = MAKE_TRACEBACK(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio,
        type_description_1,
        par_s1,
        par_s2,
        par_force_ascii,
        par_full_process
    );


    // Release cached frame if used for exception.
    if (frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio == cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio);
        cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio = NULL;
    }

    assertFrameObject(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_s1);
    Py_DECREF(par_s1);
    CHECK_OBJECT(par_s2);
    Py_DECREF(par_s2);
    CHECK_OBJECT(par_force_ascii);
    Py_DECREF(par_force_ascii);
    CHECK_OBJECT(par_full_process);
    Py_DECREF(par_full_process);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_s1);
    Py_DECREF(par_s1);
    CHECK_OBJECT(par_s2);
    Py_DECREF(par_s2);
    CHECK_OBJECT(par_force_ascii);
    Py_DECREF(par_force_ascii);
    CHECK_OBJECT(par_full_process);
    Py_DECREF(par_full_process);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_s1 = python_pars[0];
    PyObject *par_s2 = python_pars[1];
    PyObject *par_force_ascii = python_pars[2];
    PyObject *par_full_process = python_pars[3];
    struct Nuitka_FrameObject *frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio)) {
        Py_XDECREF(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio = MAKE_FUNCTION_FRAME(tstate, code_objects_d3e234be0084b933b9c2718fe6a84686, module_thefuzz$fuzz, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio->m_type_description == NULL);
    frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio = cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio);
    assert(Py_REFCNT(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_args_element_value_2;
        PyObject *tmp_args_element_value_3;
        PyObject *tmp_args_element_value_4;
        PyObject *tmp_args_element_value_5;
        tmp_called_value_1 = module_var_accessor_thefuzz$$36$fuzz$_rapidfuzz_scorer(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 68;
            type_description_1 = "oooo";
            goto frame_exception_exit_1;
        }
        tmp_args_element_value_1 = module_var_accessor_thefuzz$$36$fuzz$_partial_token_sort_ratio(tstate);
        if (unlikely(tmp_args_element_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[11]);
        }

        if (tmp_args_element_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 69;
            type_description_1 = "oooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_s1);
        tmp_args_element_value_2 = par_s1;
        CHECK_OBJECT(par_s2);
        tmp_args_element_value_3 = par_s2;
        CHECK_OBJECT(par_force_ascii);
        tmp_args_element_value_4 = par_force_ascii;
        CHECK_OBJECT(par_full_process);
        tmp_args_element_value_5 = par_full_process;
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio->m_frame.f_lineno = 68;
        {
            PyObject *call_args[] = {tmp_args_element_value_1, tmp_args_element_value_2, tmp_args_element_value_3, tmp_args_element_value_4, tmp_args_element_value_5};
            tmp_return_value = CALL_FUNCTION_WITH_ARGS5(tstate, tmp_called_value_1, call_args);
        }

        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 68;
            type_description_1 = "oooo";
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
            exception_tb = MAKE_TRACEBACK(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio,
        type_description_1,
        par_s1,
        par_s2,
        par_force_ascii,
        par_full_process
    );


    // Release cached frame if used for exception.
    if (frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio == cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio);
        cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio = NULL;
    }

    assertFrameObject(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_s1);
    Py_DECREF(par_s1);
    CHECK_OBJECT(par_s2);
    Py_DECREF(par_s2);
    CHECK_OBJECT(par_force_ascii);
    Py_DECREF(par_force_ascii);
    CHECK_OBJECT(par_full_process);
    Py_DECREF(par_full_process);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_s1);
    Py_DECREF(par_s1);
    CHECK_OBJECT(par_s2);
    Py_DECREF(par_s2);
    CHECK_OBJECT(par_force_ascii);
    Py_DECREF(par_force_ascii);
    CHECK_OBJECT(par_full_process);
    Py_DECREF(par_full_process);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_s1 = python_pars[0];
    PyObject *par_s2 = python_pars[1];
    PyObject *par_force_ascii = python_pars[2];
    PyObject *par_full_process = python_pars[3];
    struct Nuitka_FrameObject *frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio)) {
        Py_XDECREF(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio = MAKE_FUNCTION_FRAME(tstate, code_objects_cb06d54bad097f74f06b10342065e8e8, module_thefuzz$fuzz, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio->m_type_description == NULL);
    frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio = cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio);
    assert(Py_REFCNT(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_args_element_value_2;
        PyObject *tmp_args_element_value_3;
        PyObject *tmp_args_element_value_4;
        PyObject *tmp_args_element_value_5;
        tmp_called_value_1 = module_var_accessor_thefuzz$$36$fuzz$_rapidfuzz_scorer(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 74;
            type_description_1 = "oooo";
            goto frame_exception_exit_1;
        }
        tmp_args_element_value_1 = module_var_accessor_thefuzz$$36$fuzz$_token_set_ratio(tstate);
        if (unlikely(tmp_args_element_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[13]);
        }

        if (tmp_args_element_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 74;
            type_description_1 = "oooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_s1);
        tmp_args_element_value_2 = par_s1;
        CHECK_OBJECT(par_s2);
        tmp_args_element_value_3 = par_s2;
        CHECK_OBJECT(par_force_ascii);
        tmp_args_element_value_4 = par_force_ascii;
        CHECK_OBJECT(par_full_process);
        tmp_args_element_value_5 = par_full_process;
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio->m_frame.f_lineno = 74;
        {
            PyObject *call_args[] = {tmp_args_element_value_1, tmp_args_element_value_2, tmp_args_element_value_3, tmp_args_element_value_4, tmp_args_element_value_5};
            tmp_return_value = CALL_FUNCTION_WITH_ARGS5(tstate, tmp_called_value_1, call_args);
        }

        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 74;
            type_description_1 = "oooo";
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
            exception_tb = MAKE_TRACEBACK(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio,
        type_description_1,
        par_s1,
        par_s2,
        par_force_ascii,
        par_full_process
    );


    // Release cached frame if used for exception.
    if (frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio == cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio);
        cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio = NULL;
    }

    assertFrameObject(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_s1);
    Py_DECREF(par_s1);
    CHECK_OBJECT(par_s2);
    Py_DECREF(par_s2);
    CHECK_OBJECT(par_force_ascii);
    Py_DECREF(par_force_ascii);
    CHECK_OBJECT(par_full_process);
    Py_DECREF(par_full_process);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_s1);
    Py_DECREF(par_s1);
    CHECK_OBJECT(par_s2);
    Py_DECREF(par_s2);
    CHECK_OBJECT(par_force_ascii);
    Py_DECREF(par_force_ascii);
    CHECK_OBJECT(par_full_process);
    Py_DECREF(par_full_process);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_s1 = python_pars[0];
    PyObject *par_s2 = python_pars[1];
    PyObject *par_force_ascii = python_pars[2];
    PyObject *par_full_process = python_pars[3];
    struct Nuitka_FrameObject *frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio)) {
        Py_XDECREF(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio = MAKE_FUNCTION_FRAME(tstate, code_objects_b693b319b4a3c2d48ede0bbcd85790f0, module_thefuzz$fuzz, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio->m_type_description == NULL);
    frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio = cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio);
    assert(Py_REFCNT(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_args_element_value_2;
        PyObject *tmp_args_element_value_3;
        PyObject *tmp_args_element_value_4;
        PyObject *tmp_args_element_value_5;
        tmp_called_value_1 = module_var_accessor_thefuzz$$36$fuzz$_rapidfuzz_scorer(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 78;
            type_description_1 = "oooo";
            goto frame_exception_exit_1;
        }
        tmp_args_element_value_1 = module_var_accessor_thefuzz$$36$fuzz$_partial_token_set_ratio(tstate);
        if (unlikely(tmp_args_element_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[14]);
        }

        if (tmp_args_element_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 79;
            type_description_1 = "oooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_s1);
        tmp_args_element_value_2 = par_s1;
        CHECK_OBJECT(par_s2);
        tmp_args_element_value_3 = par_s2;
        CHECK_OBJECT(par_force_ascii);
        tmp_args_element_value_4 = par_force_ascii;
        CHECK_OBJECT(par_full_process);
        tmp_args_element_value_5 = par_full_process;
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio->m_frame.f_lineno = 78;
        {
            PyObject *call_args[] = {tmp_args_element_value_1, tmp_args_element_value_2, tmp_args_element_value_3, tmp_args_element_value_4, tmp_args_element_value_5};
            tmp_return_value = CALL_FUNCTION_WITH_ARGS5(tstate, tmp_called_value_1, call_args);
        }

        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 78;
            type_description_1 = "oooo";
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
            exception_tb = MAKE_TRACEBACK(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio,
        type_description_1,
        par_s1,
        par_s2,
        par_force_ascii,
        par_full_process
    );


    // Release cached frame if used for exception.
    if (frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio == cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio);
        cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio = NULL;
    }

    assertFrameObject(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_s1);
    Py_DECREF(par_s1);
    CHECK_OBJECT(par_s2);
    Py_DECREF(par_s2);
    CHECK_OBJECT(par_force_ascii);
    Py_DECREF(par_force_ascii);
    CHECK_OBJECT(par_full_process);
    Py_DECREF(par_full_process);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_s1);
    Py_DECREF(par_s1);
    CHECK_OBJECT(par_s2);
    Py_DECREF(par_s2);
    CHECK_OBJECT(par_force_ascii);
    Py_DECREF(par_force_ascii);
    CHECK_OBJECT(par_full_process);
    Py_DECREF(par_full_process);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_s1 = python_pars[0];
    PyObject *par_s2 = python_pars[1];
    PyObject *par_force_ascii = python_pars[2];
    PyObject *par_full_process = python_pars[3];
    struct Nuitka_FrameObject *frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio)) {
        Py_XDECREF(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio = MAKE_FUNCTION_FRAME(tstate, code_objects_d0e7fd67e2d64f4b88b6ea4915c75365, module_thefuzz$fuzz, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio->m_type_description == NULL);
    frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio = cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio);
    assert(Py_REFCNT(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_args_element_value_2;
        PyObject *tmp_args_element_value_3;
        PyObject *tmp_args_element_value_4;
        PyObject *tmp_args_element_value_5;
        tmp_called_value_1 = module_var_accessor_thefuzz$$36$fuzz$_rapidfuzz_scorer(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 101;
            type_description_1 = "oooo";
            goto frame_exception_exit_1;
        }
        tmp_args_element_value_1 = module_var_accessor_thefuzz$$36$fuzz$_QRatio(tstate);
        if (unlikely(tmp_args_element_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[15]);
        }

        if (tmp_args_element_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 101;
            type_description_1 = "oooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_s1);
        tmp_args_element_value_2 = par_s1;
        CHECK_OBJECT(par_s2);
        tmp_args_element_value_3 = par_s2;
        CHECK_OBJECT(par_force_ascii);
        tmp_args_element_value_4 = par_force_ascii;
        CHECK_OBJECT(par_full_process);
        tmp_args_element_value_5 = par_full_process;
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio->m_frame.f_lineno = 101;
        {
            PyObject *call_args[] = {tmp_args_element_value_1, tmp_args_element_value_2, tmp_args_element_value_3, tmp_args_element_value_4, tmp_args_element_value_5};
            tmp_return_value = CALL_FUNCTION_WITH_ARGS5(tstate, tmp_called_value_1, call_args);
        }

        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 101;
            type_description_1 = "oooo";
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
            exception_tb = MAKE_TRACEBACK(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio,
        type_description_1,
        par_s1,
        par_s2,
        par_force_ascii,
        par_full_process
    );


    // Release cached frame if used for exception.
    if (frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio == cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio);
        cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio = NULL;
    }

    assertFrameObject(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_s1);
    Py_DECREF(par_s1);
    CHECK_OBJECT(par_s2);
    Py_DECREF(par_s2);
    CHECK_OBJECT(par_force_ascii);
    Py_DECREF(par_force_ascii);
    CHECK_OBJECT(par_full_process);
    Py_DECREF(par_full_process);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_s1);
    Py_DECREF(par_s1);
    CHECK_OBJECT(par_s2);
    Py_DECREF(par_s2);
    CHECK_OBJECT(par_force_ascii);
    Py_DECREF(par_force_ascii);
    CHECK_OBJECT(par_full_process);
    Py_DECREF(par_full_process);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_s1 = python_pars[0];
    PyObject *par_s2 = python_pars[1];
    PyObject *par_full_process = python_pars[2];
    struct Nuitka_FrameObject *frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio)) {
        Py_XDECREF(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio = MAKE_FUNCTION_FRAME(tstate, code_objects_52501d05ba479b3778365fa632a1984d, module_thefuzz$fuzz, sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio->m_type_description == NULL);
    frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio = cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio);
    assert(Py_REFCNT(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_kw_call_arg_value_0_1;
        PyObject *tmp_kw_call_arg_value_1_1;
        PyObject *tmp_kw_call_dict_value_0_1;
        PyObject *tmp_kw_call_dict_value_1_1;
        tmp_called_value_1 = module_var_accessor_thefuzz$$36$fuzz$QRatio(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[17]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 114;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_s1);
        tmp_kw_call_arg_value_0_1 = par_s1;
        CHECK_OBJECT(par_s2);
        tmp_kw_call_arg_value_1_1 = par_s2;
        tmp_kw_call_dict_value_0_1 = Py_False;
        CHECK_OBJECT(par_full_process);
        tmp_kw_call_dict_value_1_1 = par_full_process;
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio->m_frame.f_lineno = 114;
        {
            PyObject *args[] = {tmp_kw_call_arg_value_0_1, tmp_kw_call_arg_value_1_1};
            PyObject *kw_values[2] = {tmp_kw_call_dict_value_0_1, tmp_kw_call_dict_value_1_1};
            tmp_return_value = CALL_FUNCTION_WITH_ARGS2_KW_SPLIT(tstate, tmp_called_value_1, args, kw_values, mod_consts[18]);
        }

        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 114;
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
            exception_tb = MAKE_TRACEBACK(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio,
        type_description_1,
        par_s1,
        par_s2,
        par_full_process
    );


    // Release cached frame if used for exception.
    if (frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio == cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio);
        cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio = NULL;
    }

    assertFrameObject(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_s1);
    Py_DECREF(par_s1);
    CHECK_OBJECT(par_s2);
    Py_DECREF(par_s2);
    CHECK_OBJECT(par_full_process);
    Py_DECREF(par_full_process);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_s1);
    Py_DECREF(par_s1);
    CHECK_OBJECT(par_s2);
    Py_DECREF(par_s2);
    CHECK_OBJECT(par_full_process);
    Py_DECREF(par_full_process);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_s1 = python_pars[0];
    PyObject *par_s2 = python_pars[1];
    PyObject *par_force_ascii = python_pars[2];
    PyObject *par_full_process = python_pars[3];
    struct Nuitka_FrameObject *frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio)) {
        Py_XDECREF(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio = MAKE_FUNCTION_FRAME(tstate, code_objects_f7aa1f3ca1b54c6947a27b13e783ddba, module_thefuzz$fuzz, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio->m_type_description == NULL);
    frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio = cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio);
    assert(Py_REFCNT(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_args_element_value_2;
        PyObject *tmp_args_element_value_3;
        PyObject *tmp_args_element_value_4;
        PyObject *tmp_args_element_value_5;
        tmp_called_value_1 = module_var_accessor_thefuzz$$36$fuzz$_rapidfuzz_scorer(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 152;
            type_description_1 = "oooo";
            goto frame_exception_exit_1;
        }
        tmp_args_element_value_1 = module_var_accessor_thefuzz$$36$fuzz$_WRatio(tstate);
        if (unlikely(tmp_args_element_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[20]);
        }

        if (tmp_args_element_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 152;
            type_description_1 = "oooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_s1);
        tmp_args_element_value_2 = par_s1;
        CHECK_OBJECT(par_s2);
        tmp_args_element_value_3 = par_s2;
        CHECK_OBJECT(par_force_ascii);
        tmp_args_element_value_4 = par_force_ascii;
        CHECK_OBJECT(par_full_process);
        tmp_args_element_value_5 = par_full_process;
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio->m_frame.f_lineno = 152;
        {
            PyObject *call_args[] = {tmp_args_element_value_1, tmp_args_element_value_2, tmp_args_element_value_3, tmp_args_element_value_4, tmp_args_element_value_5};
            tmp_return_value = CALL_FUNCTION_WITH_ARGS5(tstate, tmp_called_value_1, call_args);
        }

        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 152;
            type_description_1 = "oooo";
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
            exception_tb = MAKE_TRACEBACK(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio,
        type_description_1,
        par_s1,
        par_s2,
        par_force_ascii,
        par_full_process
    );


    // Release cached frame if used for exception.
    if (frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio == cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio);
        cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio = NULL;
    }

    assertFrameObject(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_s1);
    Py_DECREF(par_s1);
    CHECK_OBJECT(par_s2);
    Py_DECREF(par_s2);
    CHECK_OBJECT(par_force_ascii);
    Py_DECREF(par_force_ascii);
    CHECK_OBJECT(par_full_process);
    Py_DECREF(par_full_process);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_s1);
    Py_DECREF(par_s1);
    CHECK_OBJECT(par_s2);
    Py_DECREF(par_s2);
    CHECK_OBJECT(par_force_ascii);
    Py_DECREF(par_force_ascii);
    CHECK_OBJECT(par_full_process);
    Py_DECREF(par_full_process);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_s1 = python_pars[0];
    PyObject *par_s2 = python_pars[1];
    PyObject *par_full_process = python_pars[2];
    struct Nuitka_FrameObject *frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio)) {
        Py_XDECREF(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio = MAKE_FUNCTION_FRAME(tstate, code_objects_c1d2f7884d672d6c8954a72e8c096144, module_thefuzz$fuzz, sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio->m_type_description == NULL);
    frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio = cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio);
    assert(Py_REFCNT(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_kw_call_arg_value_0_1;
        PyObject *tmp_kw_call_arg_value_1_1;
        PyObject *tmp_kw_call_dict_value_0_1;
        PyObject *tmp_kw_call_dict_value_1_1;
        tmp_called_value_1 = module_var_accessor_thefuzz$$36$fuzz$WRatio(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[22]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 160;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_s1);
        tmp_kw_call_arg_value_0_1 = par_s1;
        CHECK_OBJECT(par_s2);
        tmp_kw_call_arg_value_1_1 = par_s2;
        tmp_kw_call_dict_value_0_1 = Py_False;
        CHECK_OBJECT(par_full_process);
        tmp_kw_call_dict_value_1_1 = par_full_process;
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio->m_frame.f_lineno = 160;
        {
            PyObject *args[] = {tmp_kw_call_arg_value_0_1, tmp_kw_call_arg_value_1_1};
            PyObject *kw_values[2] = {tmp_kw_call_dict_value_0_1, tmp_kw_call_dict_value_1_1};
            tmp_return_value = CALL_FUNCTION_WITH_ARGS2_KW_SPLIT(tstate, tmp_called_value_1, args, kw_values, mod_consts[18]);
        }

        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 160;
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
            exception_tb = MAKE_TRACEBACK(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio,
        type_description_1,
        par_s1,
        par_s2,
        par_full_process
    );


    // Release cached frame if used for exception.
    if (frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio == cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio);
        cache_frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio = NULL;
    }

    assertFrameObject(frame_frame_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_s1);
    Py_DECREF(par_s1);
    CHECK_OBJECT(par_s2);
    Py_DECREF(par_s2);
    CHECK_OBJECT(par_full_process);
    Py_DECREF(par_full_process);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_s1);
    Py_DECREF(par_s1);
    CHECK_OBJECT(par_s2);
    Py_DECREF(par_s2);
    CHECK_OBJECT(par_full_process);
    Py_DECREF(par_full_process);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}



static PyObject *MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio(PyThreadState *tstate, PyObject *defaults) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio,
        mod_consts[22],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_f7aa1f3ca1b54c6947a27b13e783ddba,
        defaults,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_thefuzz$fuzz,
        mod_consts[21],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio(PyThreadState *tstate, PyObject *defaults) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio,
        mod_consts[42],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_c1d2f7884d672d6c8954a72e8c096144,
        defaults,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_thefuzz$fuzz,
        mod_consts[23],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer,
        mod_consts[5],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_f7a8e86a6deda9053888055f29944847,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_thefuzz$fuzz,
        mod_consts[4],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio,
        mod_consts[31],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_767fa27878300320332448f01a9fe469,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_thefuzz$fuzz,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio,
        mod_consts[32],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_8645436159ae0cea7144824ea223db26,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_thefuzz$fuzz,
        mod_consts[8],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio(PyThreadState *tstate, PyObject *defaults) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio,
        mod_consts[34],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_ba21d2988bb293d7e4d4b9bb2eba5226,
        defaults,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_thefuzz$fuzz,
        mod_consts[10],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio(PyThreadState *tstate, PyObject *defaults) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio,
        mod_consts[36],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_d3e234be0084b933b9c2718fe6a84686,
        defaults,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_thefuzz$fuzz,
        mod_consts[12],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio(PyThreadState *tstate, PyObject *defaults) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio,
        mod_consts[33],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_cb06d54bad097f74f06b10342065e8e8,
        defaults,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_thefuzz$fuzz,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio(PyThreadState *tstate, PyObject *defaults) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio,
        mod_consts[35],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_b693b319b4a3c2d48ede0bbcd85790f0,
        defaults,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_thefuzz$fuzz,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio(PyThreadState *tstate, PyObject *defaults) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio,
        mod_consts[17],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_d0e7fd67e2d64f4b88b6ea4915c75365,
        defaults,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_thefuzz$fuzz,
        mod_consts[16],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio(PyThreadState *tstate, PyObject *defaults) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio,
        mod_consts[41],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_52501d05ba479b3778365fa632a1984d,
        defaults,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_thefuzz$fuzz,
        mod_consts[19],
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

static function_impl_code const function_table_thefuzz$fuzz[] = {
    impl_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer,
    impl_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio,
    impl_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio,
    impl_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio,
    impl_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio,
    impl_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio,
    impl_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio,
    impl_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio,
    impl_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio,
    impl_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio,
    impl_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio,
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

    return Nuitka_Function_GetFunctionState(function, function_table_thefuzz$fuzz);
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
        module_thefuzz$fuzz,
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
        function_table_thefuzz$fuzz,
        sizeof(function_table_thefuzz$fuzz) / sizeof(function_impl_code)
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
static char const *module_full_name = "thefuzz.fuzz";
#endif

// Internal entry point for module code.
PyObject *modulecode_thefuzz$fuzz(PyThreadState *tstate, PyObject *module, struct Nuitka_MetaPathBasedLoaderEntry const *loader_entry) {
    // Report entry to PGO.
    PGO_onModuleEntered("thefuzz$fuzz");

    // Store the module for future use.
    module_thefuzz$fuzz = module;

    moduledict_thefuzz$fuzz = MODULE_DICT(module_thefuzz$fuzz);

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
        PRINT_STRING("thefuzz$fuzz: Calling setupMetaPathBasedLoader().\n");
#endif
        setupMetaPathBasedLoader(tstate);
#if 0 >= 0
#ifdef _NUITKA_TRACE
        PRINT_STRING("thefuzz$fuzz: Calling updateMetaPathBasedLoaderModuleRoot().\n");
#endif
        updateMetaPathBasedLoaderModuleRoot(module_full_name);
#endif


#if PYTHON_VERSION >= 0x300
        patchInspectModule(tstate);
#endif

#endif

        /* The constants only used by this module are created now. */
        NUITKA_PRINT_TRACE("thefuzz$fuzz: Calling createModuleConstants().\n");
        createModuleConstants(tstate);

#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
        createModuleCodeObjects();
#endif
        init_done = true;
    }

#if _NUITKA_MODULE_MODE && 0
    PyObject *pre_load = IMPORT_EMBEDDED_MODULE(tstate, "thefuzz.fuzz" "-preLoad");
    if (pre_load == NULL) {
        return NULL;
    }
#endif

    // PRINT_STRING("in initthefuzz$fuzz\n");

#ifdef _NUITKA_PLUGIN_DILL_ENABLED
    {
        char const *module_name_c;
        if (loader_entry != NULL) {
            module_name_c = loader_entry->name;
        } else {
            PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)const_str_plain___name__);
            module_name_c = Nuitka_String_AsString(module_name);
        }

        registerDillPluginTables(tstate, module_name_c, &_method_def_reduce_compiled_function, &_method_def_create_compiled_function);
    }
#endif

    // Set "__compiled__" to what version information we have.
    UPDATE_STRING_DICT0(
        moduledict_thefuzz$fuzz,
        (Nuitka_StringObject *)const_str_plain___compiled__,
        Nuitka_dunder_compiled_value
    );

    // Update "__package__" value to what it ought to be.
    {
#if 0
        UPDATE_STRING_DICT0(
            moduledict_thefuzz$fuzz,
            (Nuitka_StringObject *)const_str_plain___package__,
            mod_consts[37]
        );
#elif 0
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)const_str_plain___name__);

        UPDATE_STRING_DICT0(
            moduledict_thefuzz$fuzz,
            (Nuitka_StringObject *)const_str_plain___package__,
            module_name
        );
#else

#if PYTHON_VERSION < 0x300
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)const_str_plain___name__);
        char const *module_name_cstr = PyString_AS_STRING(module_name);

        char const *last_dot = strrchr(module_name_cstr, '.');

        if (last_dot != NULL) {
            UPDATE_STRING_DICT1(
                moduledict_thefuzz$fuzz,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyString_FromStringAndSize(module_name_cstr, last_dot - module_name_cstr)
            );
        }
#else
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)const_str_plain___name__);
        Py_ssize_t dot_index = PyUnicode_Find(module_name, const_str_dot, 0, PyUnicode_GetLength(module_name), -1);

        if (dot_index != -1) {
            UPDATE_STRING_DICT1(
                moduledict_thefuzz$fuzz,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyUnicode_Substring(module_name, 0, dot_index)
            );
        }
#endif
#endif
    }

    CHECK_OBJECT(module_thefuzz$fuzz);

    // For deep importing of a module we need to have "__builtins__", so we set
    // it ourselves in the same way than CPython does. Note: This must be done
    // before the frame object is allocated, or else it may fail.

    if (GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)const_str_plain___builtins__) == NULL) {
        PyObject *value = (PyObject *)builtin_module;

        // Check if main module, not a dict then but the module itself.
#if _NUITKA_MODULE_MODE || !0
        value = PyModule_GetDict(value);
#endif

        UPDATE_STRING_DICT0(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)const_str_plain___builtins__, value);
    }

    PyObject *module_loader = Nuitka_Loader_New(loader_entry);
    UPDATE_STRING_DICT0(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)const_str_plain___loader__, module_loader);

#if PYTHON_VERSION >= 0x300
// Set the "__spec__" value

#if 0
    // Main modules just get "None" as spec.
    UPDATE_STRING_DICT0(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)const_str_plain___spec__, Py_None);
#else
    // Other modules get a "ModuleSpec" from the standard mechanism.
    {
        PyObject *bootstrap_module = getImportLibBootstrapModule();
        CHECK_OBJECT(bootstrap_module);

        PyObject *_spec_from_module = PyObject_GetAttrString(bootstrap_module, "_spec_from_module");
        CHECK_OBJECT(_spec_from_module);

        PyObject *spec_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, _spec_from_module, module_thefuzz$fuzz);
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

        UPDATE_STRING_DICT1(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)const_str_plain___spec__, spec_value);
    }
#endif
#endif

    // Temp variables if any
    PyObject *tmp_import_from_1__module = NULL;
    struct Nuitka_FrameObject *frame_frame_thefuzz$fuzz;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    bool tmp_result;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;

    // Module init code if any


    // Module code.
    {
        PyObject *tmp_assign_source_1;
        tmp_assign_source_1 = Py_None;
        UPDATE_STRING_DICT0(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[24], tmp_assign_source_1);
    }
    {
        PyObject *tmp_assign_source_2;
        tmp_assign_source_2 = module_filename_obj;
        UPDATE_STRING_DICT0(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[25], tmp_assign_source_2);
    }
    frame_frame_thefuzz$fuzz = MAKE_MODULE_FRAME(code_objects_5070a8a80e2d3edc4dd6e1ba123f4623, module_thefuzz$fuzz);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_thefuzz$fuzz);
    assert(Py_REFCNT(frame_frame_thefuzz$fuzz) == 2);

    // Framed code:
    {
        PyObject *tmp_assattr_value_1;
        PyObject *tmp_assattr_target_1;
        tmp_assattr_value_1 = module_filename_obj;
        tmp_assattr_target_1 = module_var_accessor_thefuzz$$36$fuzz$__spec__(tstate);
        assert(!(tmp_assattr_target_1 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_1, mod_consts[26], tmp_assattr_value_1);
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
        tmp_assattr_target_2 = module_var_accessor_thefuzz$$36$fuzz$__spec__(tstate);
        assert(!(tmp_assattr_target_2 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_2, mod_consts[27], tmp_assattr_value_2);
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
        UPDATE_STRING_DICT0(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[28], tmp_assign_source_3);
    }
    {
        PyObject *tmp_assign_source_4;
        PyObject *tmp_name_value_1;
        PyObject *tmp_globals_arg_value_1;
        PyObject *tmp_locals_arg_value_1;
        PyObject *tmp_fromlist_value_1;
        PyObject *tmp_level_value_1;
        tmp_name_value_1 = mod_consts[29];
        tmp_globals_arg_value_1 = (PyObject *)moduledict_thefuzz$fuzz;
        tmp_locals_arg_value_1 = Py_None;
        tmp_fromlist_value_1 = mod_consts[30];
        tmp_level_value_1 = const_int_0;
        frame_frame_thefuzz$fuzz->m_frame.f_lineno = 3;
        tmp_assign_source_4 = IMPORT_MODULE5(tstate, tmp_name_value_1, tmp_globals_arg_value_1, tmp_locals_arg_value_1, tmp_fromlist_value_1, tmp_level_value_1);
        if (tmp_assign_source_4 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 3;

            goto frame_exception_exit_1;
        }
        assert(tmp_import_from_1__module == NULL);
        tmp_import_from_1__module = tmp_assign_source_4;
    }
    // Tried code:
    {
        PyObject *tmp_assign_source_5;
        PyObject *tmp_import_name_from_1;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_1 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_1)) {
            tmp_assign_source_5 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_1,
                (PyObject *)moduledict_thefuzz$fuzz,
                mod_consts[31],
                const_int_0
            );
        } else {
            tmp_assign_source_5 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_1, mod_consts[31]);
        }

        if (tmp_assign_source_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 3;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[6], tmp_assign_source_5);
    }
    {
        PyObject *tmp_assign_source_6;
        PyObject *tmp_import_name_from_2;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_2 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_2)) {
            tmp_assign_source_6 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_2,
                (PyObject *)moduledict_thefuzz$fuzz,
                mod_consts[32],
                const_int_0
            );
        } else {
            tmp_assign_source_6 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_2, mod_consts[32]);
        }

        if (tmp_assign_source_6 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 3;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[7], tmp_assign_source_6);
    }
    {
        PyObject *tmp_assign_source_7;
        PyObject *tmp_import_name_from_3;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_3 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_3)) {
            tmp_assign_source_7 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_3,
                (PyObject *)moduledict_thefuzz$fuzz,
                mod_consts[33],
                const_int_0
            );
        } else {
            tmp_assign_source_7 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_3, mod_consts[33]);
        }

        if (tmp_assign_source_7 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 3;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[13], tmp_assign_source_7);
    }
    {
        PyObject *tmp_assign_source_8;
        PyObject *tmp_import_name_from_4;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_4 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_4)) {
            tmp_assign_source_8 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_4,
                (PyObject *)moduledict_thefuzz$fuzz,
                mod_consts[34],
                const_int_0
            );
        } else {
            tmp_assign_source_8 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_4, mod_consts[34]);
        }

        if (tmp_assign_source_8 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 3;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[9], tmp_assign_source_8);
    }
    {
        PyObject *tmp_assign_source_9;
        PyObject *tmp_import_name_from_5;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_5 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_5)) {
            tmp_assign_source_9 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_5,
                (PyObject *)moduledict_thefuzz$fuzz,
                mod_consts[35],
                const_int_0
            );
        } else {
            tmp_assign_source_9 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_5, mod_consts[35]);
        }

        if (tmp_assign_source_9 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 3;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[14], tmp_assign_source_9);
    }
    {
        PyObject *tmp_assign_source_10;
        PyObject *tmp_import_name_from_6;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_6 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_6)) {
            tmp_assign_source_10 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_6,
                (PyObject *)moduledict_thefuzz$fuzz,
                mod_consts[36],
                const_int_0
            );
        } else {
            tmp_assign_source_10 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_6, mod_consts[36]);
        }

        if (tmp_assign_source_10 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 3;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[11], tmp_assign_source_10);
    }
    {
        PyObject *tmp_assign_source_11;
        PyObject *tmp_import_name_from_7;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_7 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_7)) {
            tmp_assign_source_11 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_7,
                (PyObject *)moduledict_thefuzz$fuzz,
                mod_consts[22],
                const_int_0
            );
        } else {
            tmp_assign_source_11 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_7, mod_consts[22]);
        }

        if (tmp_assign_source_11 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 3;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[20], tmp_assign_source_11);
    }
    {
        PyObject *tmp_assign_source_12;
        PyObject *tmp_import_name_from_8;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_8 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_8)) {
            tmp_assign_source_12 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_8,
                (PyObject *)moduledict_thefuzz$fuzz,
                mod_consts[17],
                const_int_0
            );
        } else {
            tmp_assign_source_12 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_8, mod_consts[17]);
        }

        if (tmp_assign_source_12 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 3;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[15], tmp_assign_source_12);
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
        PyObject *tmp_import_name_from_9;
        PyObject *tmp_name_value_2;
        PyObject *tmp_globals_arg_value_2;
        PyObject *tmp_locals_arg_value_2;
        PyObject *tmp_fromlist_value_2;
        PyObject *tmp_level_value_2;
        tmp_name_value_2 = mod_consts[37];
        tmp_globals_arg_value_2 = (PyObject *)moduledict_thefuzz$fuzz;
        tmp_locals_arg_value_2 = Py_None;
        tmp_fromlist_value_2 = mod_consts[38];
        tmp_level_value_2 = const_int_pos_1;
        frame_frame_thefuzz$fuzz->m_frame.f_lineno = 14;
        tmp_import_name_from_9 = IMPORT_MODULE5(tstate, tmp_name_value_2, tmp_globals_arg_value_2, tmp_locals_arg_value_2, tmp_fromlist_value_2, tmp_level_value_2);
        if (tmp_import_name_from_9 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 14;

            goto frame_exception_exit_1;
        }
        if (PyModule_Check(tmp_import_name_from_9)) {
            tmp_assign_source_13 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_9,
                (PyObject *)moduledict_thefuzz$fuzz,
                mod_consts[0],
                const_int_0
            );
        } else {
            tmp_assign_source_13 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_9, mod_consts[0]);
        }

        Py_DECREF(tmp_import_name_from_9);
        if (tmp_assign_source_13 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 14;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[0], tmp_assign_source_13);
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_thefuzz$fuzz, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_thefuzz$fuzz->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_thefuzz$fuzz, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }



    assertFrameObject(frame_frame_thefuzz$fuzz);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto module_exception_exit;
    frame_no_exception_1:;
    {
        PyObject *tmp_assign_source_14;


        tmp_assign_source_14 = MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__1__rapidfuzz_scorer(tstate);

        UPDATE_STRING_DICT1(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[5], tmp_assign_source_14);
    }
    {
        PyObject *tmp_assign_source_15;


        tmp_assign_source_15 = MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__2_ratio(tstate);

        UPDATE_STRING_DICT1(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[31], tmp_assign_source_15);
    }
    {
        PyObject *tmp_assign_source_16;


        tmp_assign_source_16 = MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__3_partial_ratio(tstate);

        UPDATE_STRING_DICT1(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[32], tmp_assign_source_16);
    }
    {
        PyObject *tmp_assign_source_17;
        PyObject *tmp_defaults_1;
        tmp_defaults_1 = mod_consts[39];
        Py_INCREF(tmp_defaults_1);


        tmp_assign_source_17 = MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__4_token_sort_ratio(tstate, tmp_defaults_1);

        UPDATE_STRING_DICT1(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[34], tmp_assign_source_17);
    }
    {
        PyObject *tmp_assign_source_18;
        PyObject *tmp_defaults_2;
        tmp_defaults_2 = mod_consts[39];
        Py_INCREF(tmp_defaults_2);


        tmp_assign_source_18 = MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__5_partial_token_sort_ratio(tstate, tmp_defaults_2);

        UPDATE_STRING_DICT1(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[36], tmp_assign_source_18);
    }
    {
        PyObject *tmp_assign_source_19;
        PyObject *tmp_defaults_3;
        tmp_defaults_3 = mod_consts[39];
        Py_INCREF(tmp_defaults_3);


        tmp_assign_source_19 = MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__6_token_set_ratio(tstate, tmp_defaults_3);

        UPDATE_STRING_DICT1(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[33], tmp_assign_source_19);
    }
    {
        PyObject *tmp_assign_source_20;
        PyObject *tmp_defaults_4;
        tmp_defaults_4 = mod_consts[39];
        Py_INCREF(tmp_defaults_4);


        tmp_assign_source_20 = MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__7_partial_token_set_ratio(tstate, tmp_defaults_4);

        UPDATE_STRING_DICT1(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[35], tmp_assign_source_20);
    }
    {
        PyObject *tmp_assign_source_21;
        PyObject *tmp_defaults_5;
        tmp_defaults_5 = mod_consts[39];
        Py_INCREF(tmp_defaults_5);


        tmp_assign_source_21 = MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__8_QRatio(tstate, tmp_defaults_5);

        UPDATE_STRING_DICT1(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[17], tmp_assign_source_21);
    }
    {
        PyObject *tmp_assign_source_22;
        PyObject *tmp_defaults_6;
        tmp_defaults_6 = mod_consts[40];
        Py_INCREF(tmp_defaults_6);


        tmp_assign_source_22 = MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__9_UQRatio(tstate, tmp_defaults_6);

        UPDATE_STRING_DICT1(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[41], tmp_assign_source_22);
    }
    {
        PyObject *tmp_assign_source_23;
        PyObject *tmp_defaults_7;
        tmp_defaults_7 = mod_consts[39];
        Py_INCREF(tmp_defaults_7);


        tmp_assign_source_23 = MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__10_WRatio(tstate, tmp_defaults_7);

        UPDATE_STRING_DICT1(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[22], tmp_assign_source_23);
    }
    {
        PyObject *tmp_assign_source_24;
        PyObject *tmp_defaults_8;
        tmp_defaults_8 = mod_consts[40];
        Py_INCREF(tmp_defaults_8);


        tmp_assign_source_24 = MAKE_FUNCTION_thefuzz$fuzz$$36$$$36$$$36$function__11_UWRatio(tstate, tmp_defaults_8);

        UPDATE_STRING_DICT1(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)mod_consts[42], tmp_assign_source_24);
    }

    // Report to PGO about leaving the module without error.
    PGO_onModuleExit("thefuzz$fuzz", false);

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *post_load = IMPORT_EMBEDDED_MODULE(tstate, "thefuzz.fuzz" "-postLoad");
        if (post_load == NULL) {
            return NULL;
        }
    }
#endif

    Py_INCREF(module_thefuzz$fuzz);
    return module_thefuzz$fuzz;
    module_exception_exit:

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_thefuzz$fuzz, (Nuitka_StringObject *)const_str_plain___name__);

        if (module_name != NULL) {
            Nuitka_DelModule(tstate, module_name);
        }
    }
#endif
    PGO_onModuleExit("thefuzz$fuzz", false);

    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);
    return NULL;
}
