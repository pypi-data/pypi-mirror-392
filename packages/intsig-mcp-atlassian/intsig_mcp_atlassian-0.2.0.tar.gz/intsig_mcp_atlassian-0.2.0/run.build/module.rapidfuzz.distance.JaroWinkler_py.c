/* Generated code for Python module 'rapidfuzz$distance$JaroWinkler_py'
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

/* The "module_rapidfuzz$distance$JaroWinkler_py" is a Python object pointer of module type.
 *
 * Note: For full compatibility with CPython, every module variable access
 * needs to go through it except for cases where the module cannot possibly
 * have changed in the mean time.
 */

PyObject *module_rapidfuzz$distance$JaroWinkler_py;
PyDictObject *moduledict_rapidfuzz$distance$JaroWinkler_py;

/* The declarations of module constants used, if any. */
static PyObject *mod_consts[46];
#ifndef __NUITKA_NO_ASSERT__
static Py_hash_t mod_consts_hash[46];
#endif

static PyObject *module_filename_obj = NULL;

/* Indicator if this modules private constants were created yet. */
static bool constants_created = false;

/* Function to create module private constants. */
static void createModuleConstants(PyThreadState *tstate) {
    if (constants_created == false) {
        loadConstantsBlob(tstate, &mod_consts[0], UN_TRANSLATE("rapidfuzz.distance.JaroWinkler_py"));
        constants_created = true;

#ifndef __NUITKA_NO_ASSERT__
        for (int i = 0; i < 46; i++) {
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
void checkModuleConstants_rapidfuzz$distance$JaroWinkler_py(PyThreadState *tstate) {
    // The module may not have been used at all, then ignore this.
    if (constants_created == false) return;

    for (int i = 0; i < 46; i++) {
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
static PyObject *module_var_accessor_rapidfuzz$$36$distance$$36$JaroWinkler_py$Jaro(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_rapidfuzz$distance$JaroWinkler_py->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_rapidfuzz$distance$JaroWinkler_py->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[13]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_rapidfuzz$distance$JaroWinkler_py->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[13]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[13]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[13]);
    }

    return result;
}

static PyObject *module_var_accessor_rapidfuzz$$36$distance$$36$JaroWinkler_py$__spec__(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_rapidfuzz$distance$JaroWinkler_py->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_rapidfuzz$distance$JaroWinkler_py->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[45]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_rapidfuzz$distance$JaroWinkler_py->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[45]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[45], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[45]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[45], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[45]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[45]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[45]);
    }

    return result;
}

static PyObject *module_var_accessor_rapidfuzz$$36$distance$$36$JaroWinkler_py$conv_sequences(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_rapidfuzz$distance$JaroWinkler_py->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_rapidfuzz$distance$JaroWinkler_py->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[5]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_rapidfuzz$distance$JaroWinkler_py->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[5]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[5]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[5]);
    }

    return result;
}

static PyObject *module_var_accessor_rapidfuzz$$36$distance$$36$JaroWinkler_py$distance(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_rapidfuzz$distance$JaroWinkler_py->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_rapidfuzz$distance$JaroWinkler_py->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[21]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_rapidfuzz$distance$JaroWinkler_py->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[21]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[21]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[21]);
    }

    return result;
}

static PyObject *module_var_accessor_rapidfuzz$$36$distance$$36$JaroWinkler_py$is_none(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_rapidfuzz$distance$JaroWinkler_py->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_rapidfuzz$distance$JaroWinkler_py->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[1]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_rapidfuzz$distance$JaroWinkler_py->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[1]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[1]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[1]);
    }

    return result;
}

static PyObject *module_var_accessor_rapidfuzz$$36$distance$$36$JaroWinkler_py$setupPandas(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_rapidfuzz$distance$JaroWinkler_py->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_rapidfuzz$distance$JaroWinkler_py->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[0]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_rapidfuzz$distance$JaroWinkler_py->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[0]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[0]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[0]);
    }

    return result;
}

static PyObject *module_var_accessor_rapidfuzz$$36$distance$$36$JaroWinkler_py$similarity(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_rapidfuzz$distance$JaroWinkler_py->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_rapidfuzz$distance$JaroWinkler_py->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[14]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_rapidfuzz$distance$JaroWinkler_py->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[14]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[14]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[14]);
    }

    return result;
}


#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
// The module code objects.
static PyCodeObject *code_objects_7d2d9abfa02e929e05121032224e541f;
static PyCodeObject *code_objects_cfb09c48659e1f42639c5c629ab51f17;
static PyCodeObject *code_objects_c416b8ee1b7afff8b7a91eaf7fdea91b;
static PyCodeObject *code_objects_9c9b4c2e0e2f2710833410deef40c2d1;
static PyCodeObject *code_objects_adb104a4a76125230f5fc2440402217c;

static void createModuleCodeObjects(void) {
    module_filename_obj = MAKE_RELATIVE_PATH(mod_consts[39]); CHECK_OBJECT(module_filename_obj);
    code_objects_7d2d9abfa02e929e05121032224e541f = MAKE_CODE_OBJECT(module_filename_obj, 1, CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[40], mod_consts[40], NULL, NULL, 0, 0, 0);
    code_objects_cfb09c48659e1f42639c5c629ab51f17 = MAKE_CODE_OBJECT(module_filename_obj, 139, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[21], mod_consts[21], mod_consts[41], NULL, 2, 3, 0);
    code_objects_c416b8ee1b7afff8b7a91eaf7fdea91b = MAKE_CODE_OBJECT(module_filename_obj, 191, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[38], mod_consts[38], mod_consts[42], NULL, 2, 3, 0);
    code_objects_9c9b4c2e0e2f2710833410deef40c2d1 = MAKE_CODE_OBJECT(module_filename_obj, 92, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[37], mod_consts[37], mod_consts[42], NULL, 2, 3, 0);
    code_objects_adb104a4a76125230f5fc2440402217c = MAKE_CODE_OBJECT(module_filename_obj, 10, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[14], mod_consts[14], mod_consts[43], NULL, 2, 3, 0);
}
#endif

// The module function declarations.
static PyObject *MAKE_FUNCTION_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity(PyThreadState *tstate, PyObject *kw_defaults);


static PyObject *MAKE_FUNCTION_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity(PyThreadState *tstate, PyObject *kw_defaults);


static PyObject *MAKE_FUNCTION_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance(PyThreadState *tstate, PyObject *kw_defaults);


static PyObject *MAKE_FUNCTION_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance(PyThreadState *tstate, PyObject *kw_defaults);


// The module function definitions.
static PyObject *impl_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_s1 = python_pars[0];
    PyObject *par_s2 = python_pars[1];
    PyObject *par_prefix_weight = python_pars[2];
    PyObject *par_processor = python_pars[3];
    PyObject *par_score_cutoff = python_pars[4];
    PyObject *var_P_len = NULL;
    PyObject *var_T_len = NULL;
    PyObject *var_min_len = NULL;
    PyObject *var_prefix = NULL;
    PyObject *var_max_prefix = NULL;
    PyObject *var__ = NULL;
    PyObject *var_jaro_score_cutoff = NULL;
    PyObject *var_prefix_sim = NULL;
    PyObject *var_Sim = NULL;
    PyObject *tmp_for_loop_1__for_iterator = NULL;
    PyObject *tmp_for_loop_1__iter_value = NULL;
    PyObject *tmp_tuple_unpack_1__element_1 = NULL;
    PyObject *tmp_tuple_unpack_1__element_2 = NULL;
    PyObject *tmp_tuple_unpack_1__source_iter = NULL;
    struct Nuitka_FrameObject *frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    NUITKA_MAY_BE_UNUSED nuitka_void tmp_unused;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    PyObject *tmp_return_value = NULL;
    bool tmp_result;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_2;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_2;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_3;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_3;
    static struct Nuitka_FrameObject *cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_4;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_4;

    // Actual function body.
    // Tried code:
    if (isFrameUnusable(cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity)) {
        Py_XDECREF(cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity = MAKE_FUNCTION_FRAME(tstate, code_objects_adb104a4a76125230f5fc2440402217c, module_rapidfuzz$distance$JaroWinkler_py, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity->m_type_description == NULL);
    frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity = cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity);
    assert(Py_REFCNT(frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_call_result_1;
        tmp_called_value_1 = module_var_accessor_rapidfuzz$$36$distance$$36$JaroWinkler_py$setupPandas(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[0]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 48;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity->m_frame.f_lineno = 48;
        tmp_call_result_1 = CALL_FUNCTION_NO_ARGS(tstate, tmp_called_value_1);
        if (tmp_call_result_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 48;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_1);
    }
    {
        nuitka_bool tmp_condition_result_1;
        int tmp_or_left_truth_1;
        nuitka_bool tmp_or_left_value_1;
        nuitka_bool tmp_or_right_value_1;
        PyObject *tmp_called_value_2;
        PyObject *tmp_call_result_2;
        PyObject *tmp_args_element_value_1;
        int tmp_truth_name_1;
        PyObject *tmp_called_value_3;
        PyObject *tmp_call_result_3;
        PyObject *tmp_args_element_value_2;
        int tmp_truth_name_2;
        tmp_called_value_2 = module_var_accessor_rapidfuzz$$36$distance$$36$JaroWinkler_py$is_none(tstate);
        if (unlikely(tmp_called_value_2 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[1]);
        }

        if (tmp_called_value_2 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 49;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_s1);
        tmp_args_element_value_1 = par_s1;
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity->m_frame.f_lineno = 49;
        tmp_call_result_2 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_2, tmp_args_element_value_1);
        if (tmp_call_result_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 49;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        tmp_truth_name_1 = CHECK_IF_TRUE(tmp_call_result_2);
        if (tmp_truth_name_1 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_call_result_2);

            exception_lineno = 49;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        tmp_or_left_value_1 = tmp_truth_name_1 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        Py_DECREF(tmp_call_result_2);
        tmp_or_left_truth_1 = tmp_or_left_value_1 == NUITKA_BOOL_TRUE ? 1 : 0;
        if (tmp_or_left_truth_1 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 49;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        if (tmp_or_left_truth_1 == 1) {
            goto or_left_1;
        } else {
            goto or_right_1;
        }
        or_right_1:;
        tmp_called_value_3 = module_var_accessor_rapidfuzz$$36$distance$$36$JaroWinkler_py$is_none(tstate);
        if (unlikely(tmp_called_value_3 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[1]);
        }

        if (tmp_called_value_3 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 49;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_s2);
        tmp_args_element_value_2 = par_s2;
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity->m_frame.f_lineno = 49;
        tmp_call_result_3 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_3, tmp_args_element_value_2);
        if (tmp_call_result_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 49;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        tmp_truth_name_2 = CHECK_IF_TRUE(tmp_call_result_3);
        if (tmp_truth_name_2 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_call_result_3);

            exception_lineno = 49;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        tmp_or_right_value_1 = tmp_truth_name_2 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        Py_DECREF(tmp_call_result_3);
        tmp_condition_result_1 = tmp_or_right_value_1;
        goto or_end_1;
        or_left_1:;
        tmp_condition_result_1 = tmp_or_left_value_1;
        or_end_1:;
        if (tmp_condition_result_1 == NUITKA_BOOL_TRUE) {
            goto branch_yes_1;
        } else {
            goto branch_no_1;
        }
    }
    branch_yes_1:;
    tmp_return_value = mod_consts[2];
    Py_INCREF(tmp_return_value);
    goto frame_return_exit_1;
    branch_no_1:;
    {
        bool tmp_condition_result_2;
        PyObject *tmp_cmp_expr_left_1;
        PyObject *tmp_cmp_expr_right_1;
        CHECK_OBJECT(par_processor);
        tmp_cmp_expr_left_1 = par_processor;
        tmp_cmp_expr_right_1 = Py_None;
        tmp_condition_result_2 = (tmp_cmp_expr_left_1 != tmp_cmp_expr_right_1) ? true : false;
        if (tmp_condition_result_2 != false) {
            goto branch_yes_2;
        } else {
            goto branch_no_2;
        }
    }
    branch_yes_2:;
    {
        PyObject *tmp_assign_source_1;
        PyObject *tmp_called_value_4;
        PyObject *tmp_args_element_value_3;
        CHECK_OBJECT(par_processor);
        tmp_called_value_4 = par_processor;
        CHECK_OBJECT(par_s1);
        tmp_args_element_value_3 = par_s1;
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity->m_frame.f_lineno = 53;
        tmp_assign_source_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_4, tmp_args_element_value_3);
        if (tmp_assign_source_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 53;
            type_description_1 = "oooooNooooooooo";
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
        PyObject *tmp_called_value_5;
        PyObject *tmp_args_element_value_4;
        CHECK_OBJECT(par_processor);
        tmp_called_value_5 = par_processor;
        CHECK_OBJECT(par_s2);
        tmp_args_element_value_4 = par_s2;
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity->m_frame.f_lineno = 54;
        tmp_assign_source_2 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_5, tmp_args_element_value_4);
        if (tmp_assign_source_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 54;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        {
            PyObject *old = par_s2;
            assert(old != NULL);
            par_s2 = tmp_assign_source_2;
            Py_DECREF(old);
        }

    }
    branch_no_2:;
    {
        bool tmp_condition_result_3;
        PyObject *tmp_cmp_expr_left_2;
        PyObject *tmp_cmp_expr_right_2;
        CHECK_OBJECT(par_score_cutoff);
        tmp_cmp_expr_left_2 = par_score_cutoff;
        tmp_cmp_expr_right_2 = Py_None;
        tmp_condition_result_3 = (tmp_cmp_expr_left_2 == tmp_cmp_expr_right_2) ? true : false;
        if (tmp_condition_result_3 != false) {
            goto branch_yes_3;
        } else {
            goto branch_no_3;
        }
    }
    branch_yes_3:;
    {
        PyObject *tmp_assign_source_3;
        tmp_assign_source_3 = const_int_0;
        {
            PyObject *old = par_score_cutoff;
            assert(old != NULL);
            par_score_cutoff = tmp_assign_source_3;
            Py_INCREF(par_score_cutoff);
            Py_DECREF(old);
        }

    }
    branch_no_3:;
    {
        nuitka_bool tmp_condition_result_4;
        int tmp_or_left_truth_2;
        nuitka_bool tmp_or_left_value_2;
        nuitka_bool tmp_or_right_value_2;
        PyObject *tmp_cmp_expr_left_3;
        PyObject *tmp_cmp_expr_right_3;
        PyObject *tmp_cmp_expr_left_4;
        PyObject *tmp_cmp_expr_right_4;
        CHECK_OBJECT(par_prefix_weight);
        tmp_cmp_expr_left_3 = par_prefix_weight;
        tmp_cmp_expr_right_3 = mod_consts[3];
        tmp_or_left_value_2 = RICH_COMPARE_GT_NBOOL_OBJECT_FLOAT(tmp_cmp_expr_left_3, tmp_cmp_expr_right_3);
        if (tmp_or_left_value_2 == NUITKA_BOOL_EXCEPTION) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 59;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        tmp_or_left_truth_2 = tmp_or_left_value_2 == NUITKA_BOOL_TRUE ? 1 : 0;
        if (tmp_or_left_truth_2 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 59;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        if (tmp_or_left_truth_2 == 1) {
            goto or_left_2;
        } else {
            goto or_right_2;
        }
        or_right_2:;
        CHECK_OBJECT(par_prefix_weight);
        tmp_cmp_expr_left_4 = par_prefix_weight;
        tmp_cmp_expr_right_4 = mod_consts[2];
        tmp_or_right_value_2 = RICH_COMPARE_LT_NBOOL_OBJECT_FLOAT(tmp_cmp_expr_left_4, tmp_cmp_expr_right_4);
        if (tmp_or_right_value_2 == NUITKA_BOOL_EXCEPTION) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 59;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_4 = tmp_or_right_value_2;
        goto or_end_2;
        or_left_2:;
        tmp_condition_result_4 = tmp_or_left_value_2;
        or_end_2:;
        if (tmp_condition_result_4 == NUITKA_BOOL_TRUE) {
            goto branch_yes_4;
        } else {
            goto branch_no_4;
        }
    }
    branch_yes_4:;
    {
        PyObject *tmp_raise_type_1;
        PyObject *tmp_make_exception_arg_1;
        tmp_make_exception_arg_1 = mod_consts[4];
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity->m_frame.f_lineno = 61;
        tmp_raise_type_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_ValueError, tmp_make_exception_arg_1);
        assert(!(tmp_raise_type_1 == NULL));
        exception_state.exception_type = tmp_raise_type_1;
        exception_lineno = 61;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);
        type_description_1 = "oooooNooooooooo";
        goto frame_exception_exit_1;
    }
    branch_no_4:;
    // Tried code:
    {
        PyObject *tmp_assign_source_4;
        PyObject *tmp_iter_arg_1;
        PyObject *tmp_called_value_6;
        PyObject *tmp_args_element_value_5;
        PyObject *tmp_args_element_value_6;
        tmp_called_value_6 = module_var_accessor_rapidfuzz$$36$distance$$36$JaroWinkler_py$conv_sequences(tstate);
        if (unlikely(tmp_called_value_6 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[5]);
        }

        if (tmp_called_value_6 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 63;
            type_description_1 = "oooooNooooooooo";
            goto try_except_handler_2;
        }
        if (par_s1 == NULL) {

            FORMAT_UNBOUND_LOCAL_ERROR(tstate, &exception_state, mod_consts[6]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 63;
            type_description_1 = "oooooNooooooooo";
            goto try_except_handler_2;
        }

        tmp_args_element_value_5 = par_s1;
        if (par_s2 == NULL) {

            FORMAT_UNBOUND_LOCAL_ERROR(tstate, &exception_state, mod_consts[7]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 63;
            type_description_1 = "oooooNooooooooo";
            goto try_except_handler_2;
        }

        tmp_args_element_value_6 = par_s2;
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity->m_frame.f_lineno = 63;
        {
            PyObject *call_args[] = {tmp_args_element_value_5, tmp_args_element_value_6};
            tmp_iter_arg_1 = CALL_FUNCTION_WITH_ARGS2(tstate, tmp_called_value_6, call_args);
        }

        if (tmp_iter_arg_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 63;
            type_description_1 = "oooooNooooooooo";
            goto try_except_handler_2;
        }
        tmp_assign_source_4 = MAKE_UNPACK_ITERATOR(tmp_iter_arg_1);
        Py_DECREF(tmp_iter_arg_1);
        if (tmp_assign_source_4 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 63;
            type_description_1 = "oooooNooooooooo";
            goto try_except_handler_2;
        }
        assert(tmp_tuple_unpack_1__source_iter == NULL);
        tmp_tuple_unpack_1__source_iter = tmp_assign_source_4;
    }
    // Tried code:
    {
        PyObject *tmp_assign_source_5;
        PyObject *tmp_unpack_1;
        CHECK_OBJECT(tmp_tuple_unpack_1__source_iter);
        tmp_unpack_1 = tmp_tuple_unpack_1__source_iter;
        tmp_assign_source_5 = UNPACK_NEXT(tstate, &exception_state, tmp_unpack_1, 0, 2);
        if (tmp_assign_source_5 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 63;
            type_description_1 = "oooooNooooooooo";
            goto try_except_handler_3;
        }
        assert(tmp_tuple_unpack_1__element_1 == NULL);
        tmp_tuple_unpack_1__element_1 = tmp_assign_source_5;
    }
    {
        PyObject *tmp_assign_source_6;
        PyObject *tmp_unpack_2;
        CHECK_OBJECT(tmp_tuple_unpack_1__source_iter);
        tmp_unpack_2 = tmp_tuple_unpack_1__source_iter;
        tmp_assign_source_6 = UNPACK_NEXT(tstate, &exception_state, tmp_unpack_2, 1, 2);
        if (tmp_assign_source_6 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 63;
            type_description_1 = "oooooNooooooooo";
            goto try_except_handler_3;
        }
        assert(tmp_tuple_unpack_1__element_2 == NULL);
        tmp_tuple_unpack_1__element_2 = tmp_assign_source_6;
    }
    {
        PyObject *tmp_iterator_name_1;
        CHECK_OBJECT(tmp_tuple_unpack_1__source_iter);
        tmp_iterator_name_1 = tmp_tuple_unpack_1__source_iter;
        tmp_result = UNPACK_ITERATOR_CHECK(tstate, &exception_state, tmp_iterator_name_1, 2);
        if (tmp_result == false) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 63;
            type_description_1 = "oooooNooooooooo";
            goto try_except_handler_3;
        }
    }
    goto try_end_1;
    // Exception handler code:
    try_except_handler_3:;
    exception_keeper_lineno_1 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_1 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    CHECK_OBJECT(tmp_tuple_unpack_1__source_iter);
    Py_DECREF(tmp_tuple_unpack_1__source_iter);
    tmp_tuple_unpack_1__source_iter = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_1;
    exception_lineno = exception_keeper_lineno_1;

    goto try_except_handler_2;
    // End of try:
    try_end_1:;
    goto try_end_2;
    // Exception handler code:
    try_except_handler_2:;
    exception_keeper_lineno_2 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_2 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    Py_XDECREF(tmp_tuple_unpack_1__element_1);
    tmp_tuple_unpack_1__element_1 = NULL;
    Py_XDECREF(tmp_tuple_unpack_1__element_2);
    tmp_tuple_unpack_1__element_2 = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_2;
    exception_lineno = exception_keeper_lineno_2;

    goto frame_exception_exit_1;
    // End of try:
    try_end_2:;
    CHECK_OBJECT(tmp_tuple_unpack_1__source_iter);
    Py_DECREF(tmp_tuple_unpack_1__source_iter);
    tmp_tuple_unpack_1__source_iter = NULL;
    {
        PyObject *tmp_assign_source_7;
        CHECK_OBJECT(tmp_tuple_unpack_1__element_1);
        tmp_assign_source_7 = tmp_tuple_unpack_1__element_1;
        {
            PyObject *old = par_s1;
            par_s1 = tmp_assign_source_7;
            Py_INCREF(par_s1);
            Py_XDECREF(old);
        }

    }
    Py_XDECREF(tmp_tuple_unpack_1__element_1);
    tmp_tuple_unpack_1__element_1 = NULL;

    {
        PyObject *tmp_assign_source_8;
        CHECK_OBJECT(tmp_tuple_unpack_1__element_2);
        tmp_assign_source_8 = tmp_tuple_unpack_1__element_2;
        {
            PyObject *old = par_s2;
            par_s2 = tmp_assign_source_8;
            Py_INCREF(par_s2);
            Py_XDECREF(old);
        }

    }
    Py_XDECREF(tmp_tuple_unpack_1__element_2);
    tmp_tuple_unpack_1__element_2 = NULL;

    {
        PyObject *tmp_assign_source_9;
        PyObject *tmp_len_arg_1;
        CHECK_OBJECT(par_s1);
        tmp_len_arg_1 = par_s1;
        tmp_assign_source_9 = BUILTIN_LEN(tstate, tmp_len_arg_1);
        if (tmp_assign_source_9 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 64;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        assert(var_P_len == NULL);
        var_P_len = tmp_assign_source_9;
    }
    {
        PyObject *tmp_assign_source_10;
        PyObject *tmp_len_arg_2;
        CHECK_OBJECT(par_s2);
        tmp_len_arg_2 = par_s2;
        tmp_assign_source_10 = BUILTIN_LEN(tstate, tmp_len_arg_2);
        if (tmp_assign_source_10 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 65;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        assert(var_T_len == NULL);
        var_T_len = tmp_assign_source_10;
    }
    {
        PyObject *tmp_assign_source_11;
        PyObject *tmp_called_value_7;
        PyObject *tmp_args_element_value_7;
        PyObject *tmp_args_element_value_8;
        tmp_called_value_7 = LOOKUP_BUILTIN(mod_consts[8]);
        assert(tmp_called_value_7 != NULL);
        CHECK_OBJECT(var_P_len);
        tmp_args_element_value_7 = var_P_len;
        CHECK_OBJECT(var_T_len);
        tmp_args_element_value_8 = var_T_len;
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity->m_frame.f_lineno = 66;
        {
            PyObject *call_args[] = {tmp_args_element_value_7, tmp_args_element_value_8};
            tmp_assign_source_11 = CALL_FUNCTION_WITH_ARGS2(tstate, tmp_called_value_7, call_args);
        }

        if (tmp_assign_source_11 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 66;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        assert(var_min_len == NULL);
        var_min_len = tmp_assign_source_11;
    }
    {
        PyObject *tmp_assign_source_12;
        tmp_assign_source_12 = const_int_0;
        assert(var_prefix == NULL);
        Py_INCREF(tmp_assign_source_12);
        var_prefix = tmp_assign_source_12;
    }
    {
        PyObject *tmp_assign_source_13;
        PyObject *tmp_called_value_8;
        PyObject *tmp_args_element_value_9;
        PyObject *tmp_args_element_value_10;
        tmp_called_value_8 = LOOKUP_BUILTIN(mod_consts[8]);
        assert(tmp_called_value_8 != NULL);
        CHECK_OBJECT(var_min_len);
        tmp_args_element_value_9 = var_min_len;
        tmp_args_element_value_10 = mod_consts[9];
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity->m_frame.f_lineno = 68;
        {
            PyObject *call_args[] = {tmp_args_element_value_9, tmp_args_element_value_10};
            tmp_assign_source_13 = CALL_FUNCTION_WITH_ARGS2(tstate, tmp_called_value_8, call_args);
        }

        if (tmp_assign_source_13 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 68;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        assert(var_max_prefix == NULL);
        var_max_prefix = tmp_assign_source_13;
    }
    {
        PyObject *tmp_assign_source_14;
        PyObject *tmp_iter_arg_2;
        PyObject *tmp_xrange_low_1;
        CHECK_OBJECT(var_max_prefix);
        tmp_xrange_low_1 = var_max_prefix;
        tmp_iter_arg_2 = BUILTIN_XRANGE1(tstate, tmp_xrange_low_1);
        if (tmp_iter_arg_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 70;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        tmp_assign_source_14 = MAKE_ITERATOR(tstate, tmp_iter_arg_2);
        Py_DECREF(tmp_iter_arg_2);
        if (tmp_assign_source_14 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 70;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        assert(tmp_for_loop_1__for_iterator == NULL);
        tmp_for_loop_1__for_iterator = tmp_assign_source_14;
    }
    // Tried code:
    loop_start_1:;
    {
        PyObject *tmp_next_source_1;
        PyObject *tmp_assign_source_15;
        CHECK_OBJECT(tmp_for_loop_1__for_iterator);
        tmp_next_source_1 = tmp_for_loop_1__for_iterator;
        tmp_assign_source_15 = ITERATOR_NEXT_ITERATOR(tmp_next_source_1);
        if (tmp_assign_source_15 == NULL) {
            if (CHECK_AND_CLEAR_STOP_ITERATION_OCCURRED(tstate)) {

                goto loop_end_1;
            } else {

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                type_description_1 = "oooooNooooooooo";
                exception_lineno = 70;
                goto try_except_handler_4;
            }
        }

        {
            PyObject *old = tmp_for_loop_1__iter_value;
            tmp_for_loop_1__iter_value = tmp_assign_source_15;
            Py_XDECREF(old);
        }

    }
    {
        PyObject *tmp_assign_source_16;
        CHECK_OBJECT(tmp_for_loop_1__iter_value);
        tmp_assign_source_16 = tmp_for_loop_1__iter_value;
        {
            PyObject *old = var__;
            var__ = tmp_assign_source_16;
            Py_INCREF(var__);
            Py_XDECREF(old);
        }

    }
    {
        nuitka_bool tmp_condition_result_5;
        PyObject *tmp_cmp_expr_left_5;
        PyObject *tmp_cmp_expr_right_5;
        PyObject *tmp_expression_value_1;
        PyObject *tmp_subscript_value_1;
        PyObject *tmp_expression_value_2;
        PyObject *tmp_subscript_value_2;
        CHECK_OBJECT(par_s1);
        tmp_expression_value_1 = par_s1;
        if (var_prefix == NULL) {

            FORMAT_UNBOUND_LOCAL_ERROR(tstate, &exception_state, mod_consts[10]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 71;
            type_description_1 = "oooooNooooooooo";
            goto try_except_handler_4;
        }

        tmp_subscript_value_1 = var_prefix;
        tmp_cmp_expr_left_5 = LOOKUP_SUBSCRIPT(tstate, tmp_expression_value_1, tmp_subscript_value_1);
        if (tmp_cmp_expr_left_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 71;
            type_description_1 = "oooooNooooooooo";
            goto try_except_handler_4;
        }
        CHECK_OBJECT(par_s2);
        tmp_expression_value_2 = par_s2;
        if (var_prefix == NULL) {
            Py_DECREF(tmp_cmp_expr_left_5);
            FORMAT_UNBOUND_LOCAL_ERROR(tstate, &exception_state, mod_consts[10]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 71;
            type_description_1 = "oooooNooooooooo";
            goto try_except_handler_4;
        }

        tmp_subscript_value_2 = var_prefix;
        tmp_cmp_expr_right_5 = LOOKUP_SUBSCRIPT(tstate, tmp_expression_value_2, tmp_subscript_value_2);
        if (tmp_cmp_expr_right_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_cmp_expr_left_5);

            exception_lineno = 71;
            type_description_1 = "oooooNooooooooo";
            goto try_except_handler_4;
        }
        tmp_condition_result_5 = RICH_COMPARE_NE_NBOOL_OBJECT_OBJECT(tmp_cmp_expr_left_5, tmp_cmp_expr_right_5);
        Py_DECREF(tmp_cmp_expr_left_5);
        Py_DECREF(tmp_cmp_expr_right_5);
        if (tmp_condition_result_5 == NUITKA_BOOL_EXCEPTION) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 71;
            type_description_1 = "oooooNooooooooo";
            goto try_except_handler_4;
        }
        if (tmp_condition_result_5 == NUITKA_BOOL_TRUE) {
            goto branch_yes_5;
        } else {
            goto branch_no_5;
        }
    }
    branch_yes_5:;
    goto loop_end_1;
    branch_no_5:;
    {
        PyObject *tmp_assign_source_17;
        PyObject *tmp_iadd_expr_left_1;
        nuitka_digit tmp_iadd_expr_right_1;
        if (var_prefix == NULL) {

            FORMAT_UNBOUND_LOCAL_ERROR(tstate, &exception_state, mod_consts[10]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 73;
            type_description_1 = "oooooNooooooooo";
            goto try_except_handler_4;
        }

        tmp_iadd_expr_left_1 = var_prefix;
        tmp_iadd_expr_right_1 = 1;
        tmp_result = INPLACE_OPERATION_ADD_LONG_DIGIT(&tmp_iadd_expr_left_1, tmp_iadd_expr_right_1);
        assert(!(tmp_result == false));
        tmp_assign_source_17 = tmp_iadd_expr_left_1;
        var_prefix = tmp_assign_source_17;

    }
    if (CONSIDER_THREADING(tstate) == false) {
        assert(HAS_ERROR_OCCURRED(tstate));

        FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


        exception_lineno = 70;
        type_description_1 = "oooooNooooooooo";
        goto try_except_handler_4;
    }
    goto loop_start_1;
    loop_end_1:;
    goto try_end_3;
    // Exception handler code:
    try_except_handler_4:;
    exception_keeper_lineno_3 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_3 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    Py_XDECREF(tmp_for_loop_1__iter_value);
    tmp_for_loop_1__iter_value = NULL;
    CHECK_OBJECT(tmp_for_loop_1__for_iterator);
    Py_DECREF(tmp_for_loop_1__for_iterator);
    tmp_for_loop_1__for_iterator = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_3;
    exception_lineno = exception_keeper_lineno_3;

    goto frame_exception_exit_1;
    // End of try:
    try_end_3:;
    Py_XDECREF(tmp_for_loop_1__iter_value);
    tmp_for_loop_1__iter_value = NULL;
    CHECK_OBJECT(tmp_for_loop_1__for_iterator);
    Py_DECREF(tmp_for_loop_1__for_iterator);
    tmp_for_loop_1__for_iterator = NULL;
    {
        PyObject *tmp_assign_source_18;
        CHECK_OBJECT(par_score_cutoff);
        tmp_assign_source_18 = par_score_cutoff;
        assert(var_jaro_score_cutoff == NULL);
        Py_INCREF(tmp_assign_source_18);
        var_jaro_score_cutoff = tmp_assign_source_18;
    }
    {
        nuitka_bool tmp_condition_result_6;
        PyObject *tmp_cmp_expr_left_6;
        PyObject *tmp_cmp_expr_right_6;
        CHECK_OBJECT(var_jaro_score_cutoff);
        tmp_cmp_expr_left_6 = var_jaro_score_cutoff;
        tmp_cmp_expr_right_6 = mod_consts[11];
        tmp_condition_result_6 = RICH_COMPARE_GT_NBOOL_OBJECT_FLOAT(tmp_cmp_expr_left_6, tmp_cmp_expr_right_6);
        if (tmp_condition_result_6 == NUITKA_BOOL_EXCEPTION) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 76;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        if (tmp_condition_result_6 == NUITKA_BOOL_TRUE) {
            goto branch_yes_6;
        } else {
            goto branch_no_6;
        }
    }
    branch_yes_6:;
    {
        PyObject *tmp_assign_source_19;
        PyObject *tmp_mult_expr_left_1;
        PyObject *tmp_mult_expr_right_1;
        if (var_prefix == NULL) {

            FORMAT_UNBOUND_LOCAL_ERROR(tstate, &exception_state, mod_consts[10]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 77;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }

        tmp_mult_expr_left_1 = var_prefix;
        CHECK_OBJECT(par_prefix_weight);
        tmp_mult_expr_right_1 = par_prefix_weight;
        tmp_assign_source_19 = BINARY_OPERATION_MULT_OBJECT_LONG_OBJECT(tmp_mult_expr_left_1, tmp_mult_expr_right_1);
        if (tmp_assign_source_19 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 77;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        assert(var_prefix_sim == NULL);
        var_prefix_sim = tmp_assign_source_19;
    }
    {
        nuitka_bool tmp_condition_result_7;
        PyObject *tmp_cmp_expr_left_7;
        PyObject *tmp_cmp_expr_right_7;
        CHECK_OBJECT(var_prefix_sim);
        tmp_cmp_expr_left_7 = var_prefix_sim;
        tmp_cmp_expr_right_7 = mod_consts[3];
        tmp_condition_result_7 = RICH_COMPARE_GE_NBOOL_OBJECT_FLOAT(tmp_cmp_expr_left_7, tmp_cmp_expr_right_7);
        if (tmp_condition_result_7 == NUITKA_BOOL_EXCEPTION) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 79;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        if (tmp_condition_result_7 == NUITKA_BOOL_TRUE) {
            goto branch_yes_7;
        } else {
            goto branch_no_7;
        }
    }
    branch_yes_7:;
    {
        PyObject *tmp_assign_source_20;
        tmp_assign_source_20 = mod_consts[11];
        {
            PyObject *old = var_jaro_score_cutoff;
            assert(old != NULL);
            var_jaro_score_cutoff = tmp_assign_source_20;
            Py_INCREF(var_jaro_score_cutoff);
            Py_DECREF(old);
        }

    }
    goto branch_end_7;
    branch_no_7:;
    {
        PyObject *tmp_assign_source_21;
        PyObject *tmp_called_value_9;
        PyObject *tmp_args_element_value_11;
        PyObject *tmp_args_element_value_12;
        PyObject *tmp_truediv_expr_left_1;
        PyObject *tmp_truediv_expr_right_1;
        PyObject *tmp_sub_expr_left_1;
        PyObject *tmp_sub_expr_right_1;
        PyObject *tmp_sub_expr_left_2;
        PyObject *tmp_sub_expr_right_2;
        tmp_called_value_9 = LOOKUP_BUILTIN(mod_consts[12]);
        assert(tmp_called_value_9 != NULL);
        tmp_args_element_value_11 = mod_consts[11];
        CHECK_OBJECT(var_prefix_sim);
        tmp_sub_expr_left_1 = var_prefix_sim;
        CHECK_OBJECT(var_jaro_score_cutoff);
        tmp_sub_expr_right_1 = var_jaro_score_cutoff;
        tmp_truediv_expr_left_1 = BINARY_OPERATION_SUB_OBJECT_OBJECT_OBJECT(tmp_sub_expr_left_1, tmp_sub_expr_right_1);
        if (tmp_truediv_expr_left_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 82;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(var_prefix_sim);
        tmp_sub_expr_left_2 = var_prefix_sim;
        tmp_sub_expr_right_2 = mod_consts[3];
        tmp_truediv_expr_right_1 = BINARY_OPERATION_SUB_OBJECT_OBJECT_FLOAT(tmp_sub_expr_left_2, tmp_sub_expr_right_2);
        if (tmp_truediv_expr_right_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_truediv_expr_left_1);

            exception_lineno = 82;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        tmp_args_element_value_12 = BINARY_OPERATION_TRUEDIV_OBJECT_OBJECT_OBJECT(tmp_truediv_expr_left_1, tmp_truediv_expr_right_1);
        Py_DECREF(tmp_truediv_expr_left_1);
        Py_DECREF(tmp_truediv_expr_right_1);
        if (tmp_args_element_value_12 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 82;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity->m_frame.f_lineno = 82;
        {
            PyObject *call_args[] = {tmp_args_element_value_11, tmp_args_element_value_12};
            tmp_assign_source_21 = CALL_FUNCTION_WITH_ARGS2(tstate, tmp_called_value_9, call_args);
        }

        Py_DECREF(tmp_args_element_value_12);
        if (tmp_assign_source_21 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 82;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        {
            PyObject *old = var_jaro_score_cutoff;
            assert(old != NULL);
            var_jaro_score_cutoff = tmp_assign_source_21;
            Py_DECREF(old);
        }

    }
    branch_end_7:;
    branch_no_6:;
    {
        PyObject *tmp_assign_source_22;
        PyObject *tmp_called_value_10;
        PyObject *tmp_expression_value_3;
        PyObject *tmp_kw_call_arg_value_0_1;
        PyObject *tmp_kw_call_arg_value_1_1;
        PyObject *tmp_kw_call_dict_value_0_1;
        tmp_expression_value_3 = module_var_accessor_rapidfuzz$$36$distance$$36$JaroWinkler_py$Jaro(tstate);
        if (unlikely(tmp_expression_value_3 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[13]);
        }

        if (tmp_expression_value_3 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 84;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        tmp_called_value_10 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_3, mod_consts[14]);
        if (tmp_called_value_10 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 84;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_s1);
        tmp_kw_call_arg_value_0_1 = par_s1;
        CHECK_OBJECT(par_s2);
        tmp_kw_call_arg_value_1_1 = par_s2;
        CHECK_OBJECT(var_jaro_score_cutoff);
        tmp_kw_call_dict_value_0_1 = var_jaro_score_cutoff;
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity->m_frame.f_lineno = 84;
        {
            PyObject *args[] = {tmp_kw_call_arg_value_0_1, tmp_kw_call_arg_value_1_1};
            PyObject *kw_values[1] = {tmp_kw_call_dict_value_0_1};
            tmp_assign_source_22 = CALL_FUNCTION_WITH_ARGS2_KW_SPLIT(tstate, tmp_called_value_10, args, kw_values, mod_consts[15]);
        }

        Py_DECREF(tmp_called_value_10);
        if (tmp_assign_source_22 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 84;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        assert(var_Sim == NULL);
        var_Sim = tmp_assign_source_22;
    }
    {
        nuitka_bool tmp_condition_result_8;
        PyObject *tmp_cmp_expr_left_8;
        PyObject *tmp_cmp_expr_right_8;
        CHECK_OBJECT(var_Sim);
        tmp_cmp_expr_left_8 = var_Sim;
        tmp_cmp_expr_right_8 = mod_consts[11];
        tmp_condition_result_8 = RICH_COMPARE_GT_NBOOL_OBJECT_FLOAT(tmp_cmp_expr_left_8, tmp_cmp_expr_right_8);
        if (tmp_condition_result_8 == NUITKA_BOOL_EXCEPTION) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 85;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        if (tmp_condition_result_8 == NUITKA_BOOL_TRUE) {
            goto branch_yes_8;
        } else {
            goto branch_no_8;
        }
    }
    branch_yes_8:;
    {
        PyObject *tmp_assign_source_23;
        PyObject *tmp_iadd_expr_left_2;
        PyObject *tmp_iadd_expr_right_2;
        PyObject *tmp_mult_expr_left_2;
        PyObject *tmp_mult_expr_right_2;
        PyObject *tmp_mult_expr_left_3;
        PyObject *tmp_mult_expr_right_3;
        PyObject *tmp_sub_expr_left_3;
        PyObject *tmp_sub_expr_right_3;
        CHECK_OBJECT(var_Sim);
        tmp_iadd_expr_left_2 = var_Sim;
        if (var_prefix == NULL) {

            FORMAT_UNBOUND_LOCAL_ERROR(tstate, &exception_state, mod_consts[10]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 86;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }

        tmp_mult_expr_left_3 = var_prefix;
        CHECK_OBJECT(par_prefix_weight);
        tmp_mult_expr_right_3 = par_prefix_weight;
        tmp_mult_expr_left_2 = BINARY_OPERATION_MULT_OBJECT_LONG_OBJECT(tmp_mult_expr_left_3, tmp_mult_expr_right_3);
        if (tmp_mult_expr_left_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 86;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        tmp_sub_expr_left_3 = mod_consts[3];
        CHECK_OBJECT(var_Sim);
        tmp_sub_expr_right_3 = var_Sim;
        tmp_mult_expr_right_2 = BINARY_OPERATION_SUB_OBJECT_FLOAT_OBJECT(tmp_sub_expr_left_3, tmp_sub_expr_right_3);
        if (tmp_mult_expr_right_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_mult_expr_left_2);

            exception_lineno = 86;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        tmp_iadd_expr_right_2 = BINARY_OPERATION_MULT_OBJECT_OBJECT_OBJECT(tmp_mult_expr_left_2, tmp_mult_expr_right_2);
        Py_DECREF(tmp_mult_expr_left_2);
        Py_DECREF(tmp_mult_expr_right_2);
        if (tmp_iadd_expr_right_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 86;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        tmp_result = INPLACE_OPERATION_ADD_OBJECT_OBJECT(&tmp_iadd_expr_left_2, tmp_iadd_expr_right_2);
        Py_DECREF(tmp_iadd_expr_right_2);
        if (tmp_result == false) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 86;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        tmp_assign_source_23 = tmp_iadd_expr_left_2;
        var_Sim = tmp_assign_source_23;

    }
    {
        PyObject *tmp_assign_source_24;
        PyObject *tmp_called_value_11;
        PyObject *tmp_args_element_value_13;
        PyObject *tmp_args_element_value_14;
        tmp_called_value_11 = LOOKUP_BUILTIN(mod_consts[8]);
        assert(tmp_called_value_11 != NULL);
        CHECK_OBJECT(var_Sim);
        tmp_args_element_value_13 = var_Sim;
        tmp_args_element_value_14 = mod_consts[3];
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity->m_frame.f_lineno = 87;
        {
            PyObject *call_args[] = {tmp_args_element_value_13, tmp_args_element_value_14};
            tmp_assign_source_24 = CALL_FUNCTION_WITH_ARGS2(tstate, tmp_called_value_11, call_args);
        }

        if (tmp_assign_source_24 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 87;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        {
            PyObject *old = var_Sim;
            assert(old != NULL);
            var_Sim = tmp_assign_source_24;
            Py_DECREF(old);
        }

    }
    branch_no_8:;
    {
        nuitka_bool tmp_condition_result_9;
        PyObject *tmp_cmp_expr_left_9;
        PyObject *tmp_cmp_expr_right_9;
        CHECK_OBJECT(var_Sim);
        tmp_cmp_expr_left_9 = var_Sim;
        CHECK_OBJECT(par_score_cutoff);
        tmp_cmp_expr_right_9 = par_score_cutoff;
        tmp_condition_result_9 = RICH_COMPARE_GE_NBOOL_OBJECT_OBJECT(tmp_cmp_expr_left_9, tmp_cmp_expr_right_9);
        if (tmp_condition_result_9 == NUITKA_BOOL_EXCEPTION) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 89;
            type_description_1 = "oooooNooooooooo";
            goto frame_exception_exit_1;
        }
        if (tmp_condition_result_9 == NUITKA_BOOL_TRUE) {
            goto condexpr_true_1;
        } else {
            goto condexpr_false_1;
        }
        condexpr_true_1:;
        CHECK_OBJECT(var_Sim);
        tmp_return_value = var_Sim;
        goto condexpr_end_1;
        condexpr_false_1:;
        tmp_return_value = const_int_0;
        condexpr_end_1:;
        Py_INCREF(tmp_return_value);
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
            exception_tb = MAKE_TRACEBACK(frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity,
        type_description_1,
        par_s1,
        par_s2,
        par_prefix_weight,
        par_processor,
        par_score_cutoff,
        NULL,
        var_P_len,
        var_T_len,
        var_min_len,
        var_prefix,
        var_max_prefix,
        var__,
        var_jaro_score_cutoff,
        var_prefix_sim,
        var_Sim
    );


    // Release cached frame if used for exception.
    if (frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity == cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity);
        cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity = NULL;
    }

    assertFrameObject(frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity);

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
    Py_XDECREF(par_score_cutoff);
    par_score_cutoff = NULL;
    Py_XDECREF(var_P_len);
    var_P_len = NULL;
    Py_XDECREF(var_T_len);
    var_T_len = NULL;
    Py_XDECREF(var_min_len);
    var_min_len = NULL;
    Py_XDECREF(var_prefix);
    var_prefix = NULL;
    Py_XDECREF(var_max_prefix);
    var_max_prefix = NULL;
    Py_XDECREF(var__);
    var__ = NULL;
    Py_XDECREF(var_jaro_score_cutoff);
    var_jaro_score_cutoff = NULL;
    Py_XDECREF(var_prefix_sim);
    var_prefix_sim = NULL;
    Py_XDECREF(var_Sim);
    var_Sim = NULL;
    goto function_return_exit;
    // Exception handler code:
    try_except_handler_1:;
    exception_keeper_lineno_4 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_4 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    Py_XDECREF(par_s1);
    par_s1 = NULL;
    Py_XDECREF(par_s2);
    par_s2 = NULL;
    Py_XDECREF(par_score_cutoff);
    par_score_cutoff = NULL;
    Py_XDECREF(var_P_len);
    var_P_len = NULL;
    Py_XDECREF(var_T_len);
    var_T_len = NULL;
    Py_XDECREF(var_min_len);
    var_min_len = NULL;
    Py_XDECREF(var_prefix);
    var_prefix = NULL;
    Py_XDECREF(var_max_prefix);
    var_max_prefix = NULL;
    Py_XDECREF(var__);
    var__ = NULL;
    Py_XDECREF(var_jaro_score_cutoff);
    var_jaro_score_cutoff = NULL;
    Py_XDECREF(var_prefix_sim);
    var_prefix_sim = NULL;
    Py_XDECREF(var_Sim);
    var_Sim = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_4;
    exception_lineno = exception_keeper_lineno_4;

    goto function_exception_exit;
    // End of try:

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_prefix_weight);
    Py_DECREF(par_prefix_weight);
    CHECK_OBJECT(par_processor);
    Py_DECREF(par_processor);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_prefix_weight);
    Py_DECREF(par_prefix_weight);
    CHECK_OBJECT(par_processor);
    Py_DECREF(par_processor);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_s1 = python_pars[0];
    PyObject *par_s2 = python_pars[1];
    PyObject *par_prefix_weight = python_pars[2];
    PyObject *par_processor = python_pars[3];
    PyObject *par_score_cutoff = python_pars[4];
    struct Nuitka_FrameObject *frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity)) {
        Py_XDECREF(cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity = MAKE_FUNCTION_FRAME(tstate, code_objects_9c9b4c2e0e2f2710833410deef40c2d1, module_rapidfuzz$distance$JaroWinkler_py, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity->m_type_description == NULL);
    frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity = cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity);
    assert(Py_REFCNT(frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_kw_call_arg_value_0_1;
        PyObject *tmp_kw_call_arg_value_1_1;
        PyObject *tmp_kw_call_dict_value_0_1;
        PyObject *tmp_kw_call_dict_value_1_1;
        PyObject *tmp_kw_call_dict_value_2_1;
        tmp_called_value_1 = module_var_accessor_rapidfuzz$$36$distance$$36$JaroWinkler_py$similarity(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[14]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 130;
            type_description_1 = "ooooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_s1);
        tmp_kw_call_arg_value_0_1 = par_s1;
        CHECK_OBJECT(par_s2);
        tmp_kw_call_arg_value_1_1 = par_s2;
        CHECK_OBJECT(par_prefix_weight);
        tmp_kw_call_dict_value_0_1 = par_prefix_weight;
        CHECK_OBJECT(par_processor);
        tmp_kw_call_dict_value_1_1 = par_processor;
        CHECK_OBJECT(par_score_cutoff);
        tmp_kw_call_dict_value_2_1 = par_score_cutoff;
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity->m_frame.f_lineno = 130;
        {
            PyObject *args[] = {tmp_kw_call_arg_value_0_1, tmp_kw_call_arg_value_1_1};
            PyObject *kw_values[3] = {tmp_kw_call_dict_value_0_1, tmp_kw_call_dict_value_1_1, tmp_kw_call_dict_value_2_1};
            tmp_return_value = CALL_FUNCTION_WITH_ARGS2_KW_SPLIT(tstate, tmp_called_value_1, args, kw_values, mod_consts[17]);
        }

        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 130;
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

    goto function_return_exit;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity,
        type_description_1,
        par_s1,
        par_s2,
        par_prefix_weight,
        par_processor,
        par_score_cutoff
    );


    // Release cached frame if used for exception.
    if (frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity == cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity);
        cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity = NULL;
    }

    assertFrameObject(frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity);

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
    CHECK_OBJECT(par_prefix_weight);
    Py_DECREF(par_prefix_weight);
    CHECK_OBJECT(par_processor);
    Py_DECREF(par_processor);
    CHECK_OBJECT(par_score_cutoff);
    Py_DECREF(par_score_cutoff);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_s1);
    Py_DECREF(par_s1);
    CHECK_OBJECT(par_s2);
    Py_DECREF(par_s2);
    CHECK_OBJECT(par_prefix_weight);
    Py_DECREF(par_prefix_weight);
    CHECK_OBJECT(par_processor);
    Py_DECREF(par_processor);
    CHECK_OBJECT(par_score_cutoff);
    Py_DECREF(par_score_cutoff);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_s1 = python_pars[0];
    PyObject *par_s2 = python_pars[1];
    PyObject *par_prefix_weight = python_pars[2];
    PyObject *par_processor = python_pars[3];
    PyObject *par_score_cutoff = python_pars[4];
    PyObject *var_cutoff_distance = NULL;
    PyObject *var_sim = NULL;
    PyObject *var_dist = NULL;
    struct Nuitka_FrameObject *frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    NUITKA_MAY_BE_UNUSED nuitka_void tmp_unused;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    PyObject *tmp_return_value = NULL;
    static struct Nuitka_FrameObject *cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;

    // Actual function body.
    // Tried code:
    if (isFrameUnusable(cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance)) {
        Py_XDECREF(cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance = MAKE_FUNCTION_FRAME(tstate, code_objects_cfb09c48659e1f42639c5c629ab51f17, module_rapidfuzz$distance$JaroWinkler_py, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance->m_type_description == NULL);
    frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance = cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance);
    assert(Py_REFCNT(frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_call_result_1;
        tmp_called_value_1 = module_var_accessor_rapidfuzz$$36$distance$$36$JaroWinkler_py$setupPandas(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[0]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 177;
            type_description_1 = "oooooooo";
            goto frame_exception_exit_1;
        }
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance->m_frame.f_lineno = 177;
        tmp_call_result_1 = CALL_FUNCTION_NO_ARGS(tstate, tmp_called_value_1);
        if (tmp_call_result_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 177;
            type_description_1 = "oooooooo";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_1);
    }
    {
        nuitka_bool tmp_condition_result_1;
        int tmp_or_left_truth_1;
        nuitka_bool tmp_or_left_value_1;
        nuitka_bool tmp_or_right_value_1;
        PyObject *tmp_called_value_2;
        PyObject *tmp_call_result_2;
        PyObject *tmp_args_element_value_1;
        int tmp_truth_name_1;
        PyObject *tmp_called_value_3;
        PyObject *tmp_call_result_3;
        PyObject *tmp_args_element_value_2;
        int tmp_truth_name_2;
        tmp_called_value_2 = module_var_accessor_rapidfuzz$$36$distance$$36$JaroWinkler_py$is_none(tstate);
        if (unlikely(tmp_called_value_2 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[1]);
        }

        if (tmp_called_value_2 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 178;
            type_description_1 = "oooooooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_s1);
        tmp_args_element_value_1 = par_s1;
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance->m_frame.f_lineno = 178;
        tmp_call_result_2 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_2, tmp_args_element_value_1);
        if (tmp_call_result_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 178;
            type_description_1 = "oooooooo";
            goto frame_exception_exit_1;
        }
        tmp_truth_name_1 = CHECK_IF_TRUE(tmp_call_result_2);
        if (tmp_truth_name_1 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_call_result_2);

            exception_lineno = 178;
            type_description_1 = "oooooooo";
            goto frame_exception_exit_1;
        }
        tmp_or_left_value_1 = tmp_truth_name_1 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        Py_DECREF(tmp_call_result_2);
        tmp_or_left_truth_1 = tmp_or_left_value_1 == NUITKA_BOOL_TRUE ? 1 : 0;
        if (tmp_or_left_truth_1 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 178;
            type_description_1 = "oooooooo";
            goto frame_exception_exit_1;
        }
        if (tmp_or_left_truth_1 == 1) {
            goto or_left_1;
        } else {
            goto or_right_1;
        }
        or_right_1:;
        tmp_called_value_3 = module_var_accessor_rapidfuzz$$36$distance$$36$JaroWinkler_py$is_none(tstate);
        if (unlikely(tmp_called_value_3 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[1]);
        }

        if (tmp_called_value_3 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 178;
            type_description_1 = "oooooooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_s2);
        tmp_args_element_value_2 = par_s2;
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance->m_frame.f_lineno = 178;
        tmp_call_result_3 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_3, tmp_args_element_value_2);
        if (tmp_call_result_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 178;
            type_description_1 = "oooooooo";
            goto frame_exception_exit_1;
        }
        tmp_truth_name_2 = CHECK_IF_TRUE(tmp_call_result_3);
        if (tmp_truth_name_2 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_call_result_3);

            exception_lineno = 178;
            type_description_1 = "oooooooo";
            goto frame_exception_exit_1;
        }
        tmp_or_right_value_1 = tmp_truth_name_2 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        Py_DECREF(tmp_call_result_3);
        tmp_condition_result_1 = tmp_or_right_value_1;
        goto or_end_1;
        or_left_1:;
        tmp_condition_result_1 = tmp_or_left_value_1;
        or_end_1:;
        if (tmp_condition_result_1 == NUITKA_BOOL_TRUE) {
            goto branch_yes_1;
        } else {
            goto branch_no_1;
        }
    }
    branch_yes_1:;
    tmp_return_value = mod_consts[3];
    Py_INCREF(tmp_return_value);
    goto frame_return_exit_1;
    branch_no_1:;
    {
        bool tmp_condition_result_2;
        PyObject *tmp_cmp_expr_left_1;
        PyObject *tmp_cmp_expr_right_1;
        CHECK_OBJECT(par_processor);
        tmp_cmp_expr_left_1 = par_processor;
        tmp_cmp_expr_right_1 = Py_None;
        tmp_condition_result_2 = (tmp_cmp_expr_left_1 != tmp_cmp_expr_right_1) ? true : false;
        if (tmp_condition_result_2 != false) {
            goto branch_yes_2;
        } else {
            goto branch_no_2;
        }
    }
    branch_yes_2:;
    {
        PyObject *tmp_assign_source_1;
        PyObject *tmp_called_value_4;
        PyObject *tmp_args_element_value_3;
        CHECK_OBJECT(par_processor);
        tmp_called_value_4 = par_processor;
        CHECK_OBJECT(par_s1);
        tmp_args_element_value_3 = par_s1;
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance->m_frame.f_lineno = 182;
        tmp_assign_source_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_4, tmp_args_element_value_3);
        if (tmp_assign_source_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 182;
            type_description_1 = "oooooooo";
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
        PyObject *tmp_called_value_5;
        PyObject *tmp_args_element_value_4;
        CHECK_OBJECT(par_processor);
        tmp_called_value_5 = par_processor;
        CHECK_OBJECT(par_s2);
        tmp_args_element_value_4 = par_s2;
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance->m_frame.f_lineno = 183;
        tmp_assign_source_2 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_5, tmp_args_element_value_4);
        if (tmp_assign_source_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 183;
            type_description_1 = "oooooooo";
            goto frame_exception_exit_1;
        }
        {
            PyObject *old = par_s2;
            assert(old != NULL);
            par_s2 = tmp_assign_source_2;
            Py_DECREF(old);
        }

    }
    branch_no_2:;
    {
        PyObject *tmp_assign_source_3;
        nuitka_bool tmp_condition_result_3;
        int tmp_or_left_truth_2;
        nuitka_bool tmp_or_left_value_2;
        nuitka_bool tmp_or_right_value_2;
        PyObject *tmp_cmp_expr_left_2;
        PyObject *tmp_cmp_expr_right_2;
        PyObject *tmp_cmp_expr_left_3;
        PyObject *tmp_cmp_expr_right_3;
        PyObject *tmp_sub_expr_left_1;
        PyObject *tmp_sub_expr_right_1;
        CHECK_OBJECT(par_score_cutoff);
        tmp_cmp_expr_left_2 = par_score_cutoff;
        tmp_cmp_expr_right_2 = Py_None;
        tmp_or_left_value_2 = (tmp_cmp_expr_left_2 == tmp_cmp_expr_right_2) ? NUITKA_BOOL_TRUE : NUITKA_BOOL_FALSE;
        tmp_or_left_truth_2 = tmp_or_left_value_2 == NUITKA_BOOL_TRUE ? 1 : 0;
        if (tmp_or_left_truth_2 == 1) {
            goto or_left_2;
        } else {
            goto or_right_2;
        }
        or_right_2:;
        CHECK_OBJECT(par_score_cutoff);
        tmp_cmp_expr_left_3 = par_score_cutoff;
        tmp_cmp_expr_right_3 = mod_consts[3];
        tmp_or_right_value_2 = RICH_COMPARE_GT_NBOOL_OBJECT_FLOAT(tmp_cmp_expr_left_3, tmp_cmp_expr_right_3);
        if (tmp_or_right_value_2 == NUITKA_BOOL_EXCEPTION) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 185;
            type_description_1 = "oooooooo";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_3 = tmp_or_right_value_2;
        goto or_end_2;
        or_left_2:;
        tmp_condition_result_3 = tmp_or_left_value_2;
        or_end_2:;
        if (tmp_condition_result_3 == NUITKA_BOOL_TRUE) {
            goto condexpr_true_1;
        } else {
            goto condexpr_false_1;
        }
        condexpr_true_1:;
        tmp_assign_source_3 = Py_None;
        Py_INCREF(tmp_assign_source_3);
        goto condexpr_end_1;
        condexpr_false_1:;
        tmp_sub_expr_left_1 = mod_consts[3];
        CHECK_OBJECT(par_score_cutoff);
        tmp_sub_expr_right_1 = par_score_cutoff;
        tmp_assign_source_3 = BINARY_OPERATION_SUB_OBJECT_FLOAT_OBJECT(tmp_sub_expr_left_1, tmp_sub_expr_right_1);
        if (tmp_assign_source_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 185;
            type_description_1 = "oooooooo";
            goto frame_exception_exit_1;
        }
        condexpr_end_1:;
        assert(var_cutoff_distance == NULL);
        var_cutoff_distance = tmp_assign_source_3;
    }
    {
        PyObject *tmp_assign_source_4;
        PyObject *tmp_called_value_6;
        PyObject *tmp_kw_call_arg_value_0_1;
        PyObject *tmp_kw_call_arg_value_1_1;
        PyObject *tmp_kw_call_dict_value_0_1;
        PyObject *tmp_kw_call_dict_value_1_1;
        tmp_called_value_6 = module_var_accessor_rapidfuzz$$36$distance$$36$JaroWinkler_py$similarity(tstate);
        if (unlikely(tmp_called_value_6 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[14]);
        }

        if (tmp_called_value_6 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 186;
            type_description_1 = "oooooooo";
            goto frame_exception_exit_1;
        }
        if (par_s1 == NULL) {

            FORMAT_UNBOUND_LOCAL_ERROR(tstate, &exception_state, mod_consts[6]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 186;
            type_description_1 = "oooooooo";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_arg_value_0_1 = par_s1;
        if (par_s2 == NULL) {

            FORMAT_UNBOUND_LOCAL_ERROR(tstate, &exception_state, mod_consts[7]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 186;
            type_description_1 = "oooooooo";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_arg_value_1_1 = par_s2;
        CHECK_OBJECT(par_prefix_weight);
        tmp_kw_call_dict_value_0_1 = par_prefix_weight;
        CHECK_OBJECT(var_cutoff_distance);
        tmp_kw_call_dict_value_1_1 = var_cutoff_distance;
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance->m_frame.f_lineno = 186;
        {
            PyObject *args[] = {tmp_kw_call_arg_value_0_1, tmp_kw_call_arg_value_1_1};
            PyObject *kw_values[2] = {tmp_kw_call_dict_value_0_1, tmp_kw_call_dict_value_1_1};
            tmp_assign_source_4 = CALL_FUNCTION_WITH_ARGS2_KW_SPLIT(tstate, tmp_called_value_6, args, kw_values, mod_consts[19]);
        }

        if (tmp_assign_source_4 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 186;
            type_description_1 = "oooooooo";
            goto frame_exception_exit_1;
        }
        assert(var_sim == NULL);
        var_sim = tmp_assign_source_4;
    }
    {
        PyObject *tmp_assign_source_5;
        PyObject *tmp_sub_expr_left_2;
        PyObject *tmp_sub_expr_right_2;
        tmp_sub_expr_left_2 = mod_consts[3];
        CHECK_OBJECT(var_sim);
        tmp_sub_expr_right_2 = var_sim;
        tmp_assign_source_5 = BINARY_OPERATION_SUB_OBJECT_FLOAT_OBJECT(tmp_sub_expr_left_2, tmp_sub_expr_right_2);
        if (tmp_assign_source_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 187;
            type_description_1 = "oooooooo";
            goto frame_exception_exit_1;
        }
        assert(var_dist == NULL);
        var_dist = tmp_assign_source_5;
    }
    {
        nuitka_bool tmp_condition_result_4;
        int tmp_or_left_truth_3;
        nuitka_bool tmp_or_left_value_3;
        nuitka_bool tmp_or_right_value_3;
        PyObject *tmp_cmp_expr_left_4;
        PyObject *tmp_cmp_expr_right_4;
        PyObject *tmp_cmp_expr_left_5;
        PyObject *tmp_cmp_expr_right_5;
        CHECK_OBJECT(par_score_cutoff);
        tmp_cmp_expr_left_4 = par_score_cutoff;
        tmp_cmp_expr_right_4 = Py_None;
        tmp_or_left_value_3 = (tmp_cmp_expr_left_4 == tmp_cmp_expr_right_4) ? NUITKA_BOOL_TRUE : NUITKA_BOOL_FALSE;
        tmp_or_left_truth_3 = tmp_or_left_value_3 == NUITKA_BOOL_TRUE ? 1 : 0;
        if (tmp_or_left_truth_3 == 1) {
            goto or_left_3;
        } else {
            goto or_right_3;
        }
        or_right_3:;
        CHECK_OBJECT(var_dist);
        tmp_cmp_expr_left_5 = var_dist;
        CHECK_OBJECT(par_score_cutoff);
        tmp_cmp_expr_right_5 = par_score_cutoff;
        tmp_or_right_value_3 = RICH_COMPARE_LE_NBOOL_OBJECT_OBJECT(tmp_cmp_expr_left_5, tmp_cmp_expr_right_5);
        if (tmp_or_right_value_3 == NUITKA_BOOL_EXCEPTION) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 188;
            type_description_1 = "oooooooo";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_4 = tmp_or_right_value_3;
        goto or_end_3;
        or_left_3:;
        tmp_condition_result_4 = tmp_or_left_value_3;
        or_end_3:;
        if (tmp_condition_result_4 == NUITKA_BOOL_TRUE) {
            goto condexpr_true_2;
        } else {
            goto condexpr_false_2;
        }
        condexpr_true_2:;
        CHECK_OBJECT(var_dist);
        tmp_return_value = var_dist;
        goto condexpr_end_2;
        condexpr_false_2:;
        tmp_return_value = mod_consts[3];
        condexpr_end_2:;
        Py_INCREF(tmp_return_value);
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
            exception_tb = MAKE_TRACEBACK(frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance,
        type_description_1,
        par_s1,
        par_s2,
        par_prefix_weight,
        par_processor,
        par_score_cutoff,
        var_cutoff_distance,
        var_sim,
        var_dist
    );


    // Release cached frame if used for exception.
    if (frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance == cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance);
        cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance = NULL;
    }

    assertFrameObject(frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance);

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
    Py_XDECREF(var_cutoff_distance);
    var_cutoff_distance = NULL;
    Py_XDECREF(var_sim);
    var_sim = NULL;
    Py_XDECREF(var_dist);
    var_dist = NULL;
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
    Py_XDECREF(var_cutoff_distance);
    var_cutoff_distance = NULL;
    Py_XDECREF(var_sim);
    var_sim = NULL;
    Py_XDECREF(var_dist);
    var_dist = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_1;
    exception_lineno = exception_keeper_lineno_1;

    goto function_exception_exit;
    // End of try:

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_prefix_weight);
    Py_DECREF(par_prefix_weight);
    CHECK_OBJECT(par_processor);
    Py_DECREF(par_processor);
    CHECK_OBJECT(par_score_cutoff);
    Py_DECREF(par_score_cutoff);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_prefix_weight);
    Py_DECREF(par_prefix_weight);
    CHECK_OBJECT(par_processor);
    Py_DECREF(par_processor);
    CHECK_OBJECT(par_score_cutoff);
    Py_DECREF(par_score_cutoff);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_s1 = python_pars[0];
    PyObject *par_s2 = python_pars[1];
    PyObject *par_prefix_weight = python_pars[2];
    PyObject *par_processor = python_pars[3];
    PyObject *par_score_cutoff = python_pars[4];
    struct Nuitka_FrameObject *frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance)) {
        Py_XDECREF(cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance = MAKE_FUNCTION_FRAME(tstate, code_objects_c416b8ee1b7afff8b7a91eaf7fdea91b, module_rapidfuzz$distance$JaroWinkler_py, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance->m_type_description == NULL);
    frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance = cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance);
    assert(Py_REFCNT(frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_kw_call_arg_value_0_1;
        PyObject *tmp_kw_call_arg_value_1_1;
        PyObject *tmp_kw_call_dict_value_0_1;
        PyObject *tmp_kw_call_dict_value_1_1;
        PyObject *tmp_kw_call_dict_value_2_1;
        tmp_called_value_1 = module_var_accessor_rapidfuzz$$36$distance$$36$JaroWinkler_py$distance(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[21]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 229;
            type_description_1 = "ooooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_s1);
        tmp_kw_call_arg_value_0_1 = par_s1;
        CHECK_OBJECT(par_s2);
        tmp_kw_call_arg_value_1_1 = par_s2;
        CHECK_OBJECT(par_prefix_weight);
        tmp_kw_call_dict_value_0_1 = par_prefix_weight;
        CHECK_OBJECT(par_processor);
        tmp_kw_call_dict_value_1_1 = par_processor;
        CHECK_OBJECT(par_score_cutoff);
        tmp_kw_call_dict_value_2_1 = par_score_cutoff;
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance->m_frame.f_lineno = 229;
        {
            PyObject *args[] = {tmp_kw_call_arg_value_0_1, tmp_kw_call_arg_value_1_1};
            PyObject *kw_values[3] = {tmp_kw_call_dict_value_0_1, tmp_kw_call_dict_value_1_1, tmp_kw_call_dict_value_2_1};
            tmp_return_value = CALL_FUNCTION_WITH_ARGS2_KW_SPLIT(tstate, tmp_called_value_1, args, kw_values, mod_consts[17]);
        }

        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 229;
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

    goto function_return_exit;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance,
        type_description_1,
        par_s1,
        par_s2,
        par_prefix_weight,
        par_processor,
        par_score_cutoff
    );


    // Release cached frame if used for exception.
    if (frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance == cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance);
        cache_frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance = NULL;
    }

    assertFrameObject(frame_frame_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance);

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
    CHECK_OBJECT(par_prefix_weight);
    Py_DECREF(par_prefix_weight);
    CHECK_OBJECT(par_processor);
    Py_DECREF(par_processor);
    CHECK_OBJECT(par_score_cutoff);
    Py_DECREF(par_score_cutoff);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_s1);
    Py_DECREF(par_s1);
    CHECK_OBJECT(par_s2);
    Py_DECREF(par_s2);
    CHECK_OBJECT(par_prefix_weight);
    Py_DECREF(par_prefix_weight);
    CHECK_OBJECT(par_processor);
    Py_DECREF(par_processor);
    CHECK_OBJECT(par_score_cutoff);
    Py_DECREF(par_score_cutoff);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}



static PyObject *MAKE_FUNCTION_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity(PyThreadState *tstate, PyObject *kw_defaults) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity,
        mod_consts[14],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_adb104a4a76125230f5fc2440402217c,
        NULL,
#if PYTHON_VERSION >= 0x300
        kw_defaults,
        NULL,
#endif
        module_rapidfuzz$distance$JaroWinkler_py,
        mod_consts[16],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity(PyThreadState *tstate, PyObject *kw_defaults) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity,
        mod_consts[37],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_9c9b4c2e0e2f2710833410deef40c2d1,
        NULL,
#if PYTHON_VERSION >= 0x300
        kw_defaults,
        NULL,
#endif
        module_rapidfuzz$distance$JaroWinkler_py,
        mod_consts[18],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance(PyThreadState *tstate, PyObject *kw_defaults) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance,
        mod_consts[21],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_cfb09c48659e1f42639c5c629ab51f17,
        NULL,
#if PYTHON_VERSION >= 0x300
        kw_defaults,
        NULL,
#endif
        module_rapidfuzz$distance$JaroWinkler_py,
        mod_consts[20],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance(PyThreadState *tstate, PyObject *kw_defaults) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance,
        mod_consts[38],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_c416b8ee1b7afff8b7a91eaf7fdea91b,
        NULL,
#if PYTHON_VERSION >= 0x300
        kw_defaults,
        NULL,
#endif
        module_rapidfuzz$distance$JaroWinkler_py,
        mod_consts[22],
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

static function_impl_code const function_table_rapidfuzz$distance$JaroWinkler_py[] = {
    impl_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity,
    impl_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity,
    impl_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance,
    impl_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance,
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

    return Nuitka_Function_GetFunctionState(function, function_table_rapidfuzz$distance$JaroWinkler_py);
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
        module_rapidfuzz$distance$JaroWinkler_py,
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
        function_table_rapidfuzz$distance$JaroWinkler_py,
        sizeof(function_table_rapidfuzz$distance$JaroWinkler_py) / sizeof(function_impl_code)
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
static char const *module_full_name = "rapidfuzz.distance.JaroWinkler_py";
#endif

// Internal entry point for module code.
PyObject *modulecode_rapidfuzz$distance$JaroWinkler_py(PyThreadState *tstate, PyObject *module, struct Nuitka_MetaPathBasedLoaderEntry const *loader_entry) {
    // Report entry to PGO.
    PGO_onModuleEntered("rapidfuzz$distance$JaroWinkler_py");

    // Store the module for future use.
    module_rapidfuzz$distance$JaroWinkler_py = module;

    moduledict_rapidfuzz$distance$JaroWinkler_py = MODULE_DICT(module_rapidfuzz$distance$JaroWinkler_py);

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
        PRINT_STRING("rapidfuzz$distance$JaroWinkler_py: Calling setupMetaPathBasedLoader().\n");
#endif
        setupMetaPathBasedLoader(tstate);
#if 0 >= 0
#ifdef _NUITKA_TRACE
        PRINT_STRING("rapidfuzz$distance$JaroWinkler_py: Calling updateMetaPathBasedLoaderModuleRoot().\n");
#endif
        updateMetaPathBasedLoaderModuleRoot(module_full_name);
#endif


#if PYTHON_VERSION >= 0x300
        patchInspectModule(tstate);
#endif

#endif

        /* The constants only used by this module are created now. */
        NUITKA_PRINT_TRACE("rapidfuzz$distance$JaroWinkler_py: Calling createModuleConstants().\n");
        createModuleConstants(tstate);

#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
        createModuleCodeObjects();
#endif
        init_done = true;
    }

#if _NUITKA_MODULE_MODE && 0
    PyObject *pre_load = IMPORT_EMBEDDED_MODULE(tstate, "rapidfuzz.distance.JaroWinkler_py" "-preLoad");
    if (pre_load == NULL) {
        return NULL;
    }
#endif

    // PRINT_STRING("in initrapidfuzz$distance$JaroWinkler_py\n");

#ifdef _NUITKA_PLUGIN_DILL_ENABLED
    {
        char const *module_name_c;
        if (loader_entry != NULL) {
            module_name_c = loader_entry->name;
        } else {
            PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)const_str_plain___name__);
            module_name_c = Nuitka_String_AsString(module_name);
        }

        registerDillPluginTables(tstate, module_name_c, &_method_def_reduce_compiled_function, &_method_def_create_compiled_function);
    }
#endif

    // Set "__compiled__" to what version information we have.
    UPDATE_STRING_DICT0(
        moduledict_rapidfuzz$distance$JaroWinkler_py,
        (Nuitka_StringObject *)const_str_plain___compiled__,
        Nuitka_dunder_compiled_value
    );

    // Update "__package__" value to what it ought to be.
    {
#if 0
        UPDATE_STRING_DICT0(
            moduledict_rapidfuzz$distance$JaroWinkler_py,
            (Nuitka_StringObject *)const_str_plain___package__,
            mod_consts[44]
        );
#elif 0
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)const_str_plain___name__);

        UPDATE_STRING_DICT0(
            moduledict_rapidfuzz$distance$JaroWinkler_py,
            (Nuitka_StringObject *)const_str_plain___package__,
            module_name
        );
#else

#if PYTHON_VERSION < 0x300
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)const_str_plain___name__);
        char const *module_name_cstr = PyString_AS_STRING(module_name);

        char const *last_dot = strrchr(module_name_cstr, '.');

        if (last_dot != NULL) {
            UPDATE_STRING_DICT1(
                moduledict_rapidfuzz$distance$JaroWinkler_py,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyString_FromStringAndSize(module_name_cstr, last_dot - module_name_cstr)
            );
        }
#else
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)const_str_plain___name__);
        Py_ssize_t dot_index = PyUnicode_Find(module_name, const_str_dot, 0, PyUnicode_GetLength(module_name), -1);

        if (dot_index != -1) {
            UPDATE_STRING_DICT1(
                moduledict_rapidfuzz$distance$JaroWinkler_py,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyUnicode_Substring(module_name, 0, dot_index)
            );
        }
#endif
#endif
    }

    CHECK_OBJECT(module_rapidfuzz$distance$JaroWinkler_py);

    // For deep importing of a module we need to have "__builtins__", so we set
    // it ourselves in the same way than CPython does. Note: This must be done
    // before the frame object is allocated, or else it may fail.

    if (GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)const_str_plain___builtins__) == NULL) {
        PyObject *value = (PyObject *)builtin_module;

        // Check if main module, not a dict then but the module itself.
#if _NUITKA_MODULE_MODE || !0
        value = PyModule_GetDict(value);
#endif

        UPDATE_STRING_DICT0(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)const_str_plain___builtins__, value);
    }

    PyObject *module_loader = Nuitka_Loader_New(loader_entry);
    UPDATE_STRING_DICT0(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)const_str_plain___loader__, module_loader);

#if PYTHON_VERSION >= 0x300
// Set the "__spec__" value

#if 0
    // Main modules just get "None" as spec.
    UPDATE_STRING_DICT0(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)const_str_plain___spec__, Py_None);
#else
    // Other modules get a "ModuleSpec" from the standard mechanism.
    {
        PyObject *bootstrap_module = getImportLibBootstrapModule();
        CHECK_OBJECT(bootstrap_module);

        PyObject *_spec_from_module = PyObject_GetAttrString(bootstrap_module, "_spec_from_module");
        CHECK_OBJECT(_spec_from_module);

        PyObject *spec_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, _spec_from_module, module_rapidfuzz$distance$JaroWinkler_py);
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

        UPDATE_STRING_DICT1(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)const_str_plain___spec__, spec_value);
    }
#endif
#endif

    // Temp variables if any
    PyObject *tmp_import_from_1__module = NULL;
    struct Nuitka_FrameObject *frame_frame_rapidfuzz$distance$JaroWinkler_py;
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
        UPDATE_STRING_DICT0(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[23], tmp_assign_source_1);
    }
    {
        PyObject *tmp_assign_source_2;
        tmp_assign_source_2 = module_filename_obj;
        UPDATE_STRING_DICT0(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[24], tmp_assign_source_2);
    }
    frame_frame_rapidfuzz$distance$JaroWinkler_py = MAKE_MODULE_FRAME(code_objects_7d2d9abfa02e929e05121032224e541f, module_rapidfuzz$distance$JaroWinkler_py);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_rapidfuzz$distance$JaroWinkler_py);
    assert(Py_REFCNT(frame_frame_rapidfuzz$distance$JaroWinkler_py) == 2);

    // Framed code:
    {
        PyObject *tmp_assattr_value_1;
        PyObject *tmp_assattr_target_1;
        tmp_assattr_value_1 = module_filename_obj;
        tmp_assattr_target_1 = module_var_accessor_rapidfuzz$$36$distance$$36$JaroWinkler_py$__spec__(tstate);
        assert(!(tmp_assattr_target_1 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_1, mod_consts[25], tmp_assattr_value_1);
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
        tmp_assattr_target_2 = module_var_accessor_rapidfuzz$$36$distance$$36$JaroWinkler_py$__spec__(tstate);
        assert(!(tmp_assattr_target_2 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_2, mod_consts[26], tmp_assattr_value_2);
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
        UPDATE_STRING_DICT0(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[27], tmp_assign_source_3);
    }
    {
        PyObject *tmp_assign_source_4;
        {
            PyObject *hard_module = IMPORT_HARD___FUTURE__();
            tmp_assign_source_4 = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[28]);
        }
        assert(!(tmp_assign_source_4 == NULL));
        UPDATE_STRING_DICT1(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[28], tmp_assign_source_4);
    }
    {
        PyObject *tmp_assign_source_5;
        PyObject *tmp_import_name_from_1;
        PyObject *tmp_name_value_1;
        PyObject *tmp_globals_arg_value_1;
        PyObject *tmp_locals_arg_value_1;
        PyObject *tmp_fromlist_value_1;
        PyObject *tmp_level_value_1;
        tmp_name_value_1 = mod_consts[29];
        tmp_globals_arg_value_1 = (PyObject *)moduledict_rapidfuzz$distance$JaroWinkler_py;
        tmp_locals_arg_value_1 = Py_None;
        tmp_fromlist_value_1 = mod_consts[30];
        tmp_level_value_1 = const_int_0;
        frame_frame_rapidfuzz$distance$JaroWinkler_py->m_frame.f_lineno = 5;
        tmp_import_name_from_1 = IMPORT_MODULE5(tstate, tmp_name_value_1, tmp_globals_arg_value_1, tmp_locals_arg_value_1, tmp_fromlist_value_1, tmp_level_value_1);
        if (tmp_import_name_from_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 5;

            goto frame_exception_exit_1;
        }
        if (PyModule_Check(tmp_import_name_from_1)) {
            tmp_assign_source_5 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_1,
                (PyObject *)moduledict_rapidfuzz$distance$JaroWinkler_py,
                mod_consts[5],
                const_int_0
            );
        } else {
            tmp_assign_source_5 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_1, mod_consts[5]);
        }

        Py_DECREF(tmp_import_name_from_1);
        if (tmp_assign_source_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 5;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[5], tmp_assign_source_5);
    }
    {
        PyObject *tmp_assign_source_6;
        PyObject *tmp_name_value_2;
        PyObject *tmp_globals_arg_value_2;
        PyObject *tmp_locals_arg_value_2;
        PyObject *tmp_fromlist_value_2;
        PyObject *tmp_level_value_2;
        tmp_name_value_2 = mod_consts[31];
        tmp_globals_arg_value_2 = (PyObject *)moduledict_rapidfuzz$distance$JaroWinkler_py;
        tmp_locals_arg_value_2 = Py_None;
        tmp_fromlist_value_2 = mod_consts[32];
        tmp_level_value_2 = const_int_0;
        frame_frame_rapidfuzz$distance$JaroWinkler_py->m_frame.f_lineno = 6;
        tmp_assign_source_6 = IMPORT_MODULE5(tstate, tmp_name_value_2, tmp_globals_arg_value_2, tmp_locals_arg_value_2, tmp_fromlist_value_2, tmp_level_value_2);
        if (tmp_assign_source_6 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 6;

            goto frame_exception_exit_1;
        }
        assert(tmp_import_from_1__module == NULL);
        tmp_import_from_1__module = tmp_assign_source_6;
    }
    // Tried code:
    {
        PyObject *tmp_assign_source_7;
        PyObject *tmp_import_name_from_2;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_2 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_2)) {
            tmp_assign_source_7 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_2,
                (PyObject *)moduledict_rapidfuzz$distance$JaroWinkler_py,
                mod_consts[1],
                const_int_0
            );
        } else {
            tmp_assign_source_7 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_2, mod_consts[1]);
        }

        if (tmp_assign_source_7 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 6;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[1], tmp_assign_source_7);
    }
    {
        PyObject *tmp_assign_source_8;
        PyObject *tmp_import_name_from_3;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_3 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_3)) {
            tmp_assign_source_8 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_3,
                (PyObject *)moduledict_rapidfuzz$distance$JaroWinkler_py,
                mod_consts[0],
                const_int_0
            );
        } else {
            tmp_assign_source_8 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_3, mod_consts[0]);
        }

        if (tmp_assign_source_8 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 6;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[0], tmp_assign_source_8);
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
        PyObject *tmp_import_name_from_4;
        PyObject *tmp_name_value_3;
        PyObject *tmp_globals_arg_value_3;
        PyObject *tmp_locals_arg_value_3;
        PyObject *tmp_fromlist_value_3;
        PyObject *tmp_level_value_3;
        tmp_name_value_3 = mod_consts[33];
        tmp_globals_arg_value_3 = (PyObject *)moduledict_rapidfuzz$distance$JaroWinkler_py;
        tmp_locals_arg_value_3 = Py_None;
        tmp_fromlist_value_3 = mod_consts[34];
        tmp_level_value_3 = const_int_0;
        frame_frame_rapidfuzz$distance$JaroWinkler_py->m_frame.f_lineno = 7;
        tmp_import_name_from_4 = IMPORT_MODULE5(tstate, tmp_name_value_3, tmp_globals_arg_value_3, tmp_locals_arg_value_3, tmp_fromlist_value_3, tmp_level_value_3);
        if (tmp_import_name_from_4 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 7;

            goto frame_exception_exit_1;
        }
        if (PyModule_Check(tmp_import_name_from_4)) {
            tmp_assign_source_9 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_4,
                (PyObject *)moduledict_rapidfuzz$distance$JaroWinkler_py,
                mod_consts[35],
                const_int_0
            );
        } else {
            tmp_assign_source_9 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_4, mod_consts[35]);
        }

        Py_DECREF(tmp_import_name_from_4);
        if (tmp_assign_source_9 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 7;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[13], tmp_assign_source_9);
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_rapidfuzz$distance$JaroWinkler_py, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_rapidfuzz$distance$JaroWinkler_py->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_rapidfuzz$distance$JaroWinkler_py, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }



    assertFrameObject(frame_frame_rapidfuzz$distance$JaroWinkler_py);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto module_exception_exit;
    frame_no_exception_1:;
    {
        PyObject *tmp_assign_source_10;
        PyObject *tmp_kw_defaults_1;
        tmp_kw_defaults_1 = DICT_COPY(tstate, mod_consts[36]);


        tmp_assign_source_10 = MAKE_FUNCTION_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__1_similarity(tstate, tmp_kw_defaults_1);

        UPDATE_STRING_DICT1(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[14], tmp_assign_source_10);
    }
    {
        PyObject *tmp_assign_source_11;
        PyObject *tmp_kw_defaults_2;
        tmp_kw_defaults_2 = DICT_COPY(tstate, mod_consts[36]);


        tmp_assign_source_11 = MAKE_FUNCTION_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__2_normalized_similarity(tstate, tmp_kw_defaults_2);

        UPDATE_STRING_DICT1(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[37], tmp_assign_source_11);
    }
    {
        PyObject *tmp_assign_source_12;
        PyObject *tmp_kw_defaults_3;
        tmp_kw_defaults_3 = DICT_COPY(tstate, mod_consts[36]);


        tmp_assign_source_12 = MAKE_FUNCTION_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__3_distance(tstate, tmp_kw_defaults_3);

        UPDATE_STRING_DICT1(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[21], tmp_assign_source_12);
    }
    {
        PyObject *tmp_assign_source_13;
        PyObject *tmp_kw_defaults_4;
        tmp_kw_defaults_4 = DICT_COPY(tstate, mod_consts[36]);


        tmp_assign_source_13 = MAKE_FUNCTION_rapidfuzz$distance$JaroWinkler_py$$36$$$36$$$36$function__4_normalized_distance(tstate, tmp_kw_defaults_4);

        UPDATE_STRING_DICT1(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)mod_consts[38], tmp_assign_source_13);
    }

    // Report to PGO about leaving the module without error.
    PGO_onModuleExit("rapidfuzz$distance$JaroWinkler_py", false);

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *post_load = IMPORT_EMBEDDED_MODULE(tstate, "rapidfuzz.distance.JaroWinkler_py" "-postLoad");
        if (post_load == NULL) {
            return NULL;
        }
    }
#endif

    Py_INCREF(module_rapidfuzz$distance$JaroWinkler_py);
    return module_rapidfuzz$distance$JaroWinkler_py;
    module_exception_exit:

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_rapidfuzz$distance$JaroWinkler_py, (Nuitka_StringObject *)const_str_plain___name__);

        if (module_name != NULL) {
            Nuitka_DelModule(tstate, module_name);
        }
    }
#endif
    PGO_onModuleExit("rapidfuzz$distance$JaroWinkler_py", false);

    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);
    return NULL;
}
