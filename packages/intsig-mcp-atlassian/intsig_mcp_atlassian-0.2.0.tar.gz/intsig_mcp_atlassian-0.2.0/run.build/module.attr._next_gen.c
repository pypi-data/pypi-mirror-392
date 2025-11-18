/* Generated code for Python module 'attr$_next_gen'
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

/* The "module_attr$_next_gen" is a Python object pointer of module type.
 *
 * Note: For full compatibility with CPython, every module variable access
 * needs to go through it except for cases where the module cannot possibly
 * have changed in the mean time.
 */

PyObject *module_attr$_next_gen;
PyDictObject *moduledict_attr$_next_gen;

/* The declarations of module constants used, if any. */
static PyObject *mod_consts[89];
#ifndef __NUITKA_NO_ASSERT__
static Py_hash_t mod_consts_hash[89];
#endif

static PyObject *module_filename_obj = NULL;

/* Indicator if this modules private constants were created yet. */
static bool constants_created = false;

/* Function to create module private constants. */
static void createModuleConstants(PyThreadState *tstate) {
    if (constants_created == false) {
        loadConstantsBlob(tstate, &mod_consts[0], UN_TRANSLATE("attr._next_gen"));
        constants_created = true;

#ifndef __NUITKA_NO_ASSERT__
        for (int i = 0; i < 89; i++) {
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
void checkModuleConstants_attr$_next_gen(PyThreadState *tstate) {
    // The module may not have been used at all, then ignore this.
    if (constants_created == false) return;

    for (int i = 0; i < 89; i++) {
        assert(mod_consts_hash[i] == DEEP_HASH(tstate, mod_consts[i]));
        CHECK_OBJECT_DEEP(mod_consts[i]);
    }
}
#endif

// Helper to preserving module variables for Python3.11+
#if 11
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
static PyObject *module_var_accessor_attr$$36$_next_gen$NOTHING(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_attr$_next_gen->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_attr$_next_gen->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[61]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_attr$_next_gen->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[61]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[61], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[61]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[61], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[61]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[61]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[61]);
    }

    return result;
}

static PyObject *module_var_accessor_attr$$36$_next_gen$UnannotatedAttributeError(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_attr$_next_gen->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_attr$_next_gen->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[35]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_attr$_next_gen->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[35]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[35], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[35]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[35], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[35]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[35]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[35]);
    }

    return result;
}

static PyObject *module_var_accessor_attr$$36$_next_gen$_DEFAULT_ON_SETATTR(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_attr$_next_gen->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_attr$_next_gen->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[29]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_attr$_next_gen->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[29]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[29]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[29]);
    }

    return result;
}

static PyObject *module_var_accessor_attr$$36$_next_gen$__spec__(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_attr$_next_gen->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_attr$_next_gen->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[88]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_attr$_next_gen->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[88]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[88], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[88]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[88], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[88]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[88]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[88]);
    }

    return result;
}

static PyObject *module_var_accessor_attr$$36$_next_gen$_asdict(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_attr$_next_gen->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_attr$_next_gen->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[39]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_attr$_next_gen->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[39]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[39]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[39]);
    }

    return result;
}

static PyObject *module_var_accessor_attr$$36$_next_gen$_astuple(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_attr$_next_gen->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_attr$_next_gen->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[42]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_attr$_next_gen->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[42]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[42]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[42]);
    }

    return result;
}

static PyObject *module_var_accessor_attr$$36$_next_gen$_frozen_setattrs(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_attr$_next_gen->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_attr$_next_gen->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[32]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_attr$_next_gen->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[32]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[32], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[32]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[32], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[32]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[32]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[32]);
    }

    return result;
}

static PyObject *module_var_accessor_attr$$36$_next_gen$attrib(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_attr$_next_gen->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_attr$_next_gen->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[36]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_attr$_next_gen->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[36]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[36], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[36]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[36], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[36]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[36]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[36]);
    }

    return result;
}

static PyObject *module_var_accessor_attr$$36$_next_gen$attrs(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_attr$_next_gen->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_attr$_next_gen->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[6]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_attr$_next_gen->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[6]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[6]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[6]);
    }

    return result;
}

static PyObject *module_var_accessor_attr$$36$_next_gen$define(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_attr$_next_gen->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_attr$_next_gen->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[66]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_attr$_next_gen->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[66]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[66], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[66]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[66], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[66]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[66]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[66]);
    }

    return result;
}

static PyObject *module_var_accessor_attr$$36$_next_gen$setters(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_attr$_next_gen->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_attr$_next_gen->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[27]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_attr$_next_gen->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[27]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[27]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[27]);
    }

    return result;
}


#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
// The module code objects.
static PyCodeObject *code_objects_95b95cc6575a762369322027ca59bd4c;
static PyCodeObject *code_objects_e21a30179c71ad1d3f6279f71c307632;
static PyCodeObject *code_objects_2e69c79df4c6f03af861a05de2725eb6;
static PyCodeObject *code_objects_2495b058fcbd29cf0f4d697b6742b40a;
static PyCodeObject *code_objects_befb1b9f7bb60137de72f249d182b5b7;
static PyCodeObject *code_objects_26067c832c2ccb3b824677eb076a8325;
static PyCodeObject *code_objects_5c12c03745f7ac59f865dcf21de946cc;

static void createModuleCodeObjects(void) {
    module_filename_obj = MAKE_RELATIVE_PATH(mod_consts[79]); CHECK_OBJECT(module_filename_obj);
    code_objects_95b95cc6575a762369322027ca59bd4c = MAKE_CODE_OBJECT(module_filename_obj, 1, CO_NOFREE, mod_consts[80], mod_consts[80], NULL, NULL, 0, 0, 0);
    code_objects_e21a30179c71ad1d3f6279f71c307632 = MAKE_CODE_OBJECT(module_filename_obj, 598, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[56], mod_consts[56], mod_consts[81], NULL, 1, 3, 0);
    code_objects_2e69c79df4c6f03af861a05de2725eb6 = MAKE_CODE_OBJECT(module_filename_obj, 614, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[58], mod_consts[58], mod_consts[82], NULL, 1, 2, 0);
    code_objects_2495b058fcbd29cf0f4d697b6742b40a = MAKE_CODE_OBJECT(module_filename_obj, 23, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[66], mod_consts[66], mod_consts[83], NULL, 1, 20, 0);
    code_objects_befb1b9f7bb60137de72f249d182b5b7 = MAKE_CODE_OBJECT(module_filename_obj, 345, CO_OPTIMIZED | CO_NEWLOCALS, mod_consts[0], mod_consts[1], mod_consts[84], mod_consts[85], 2, 0, 0);
    code_objects_26067c832c2ccb3b824677eb076a8325 = MAKE_CODE_OBJECT(module_filename_obj, 416, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[76], mod_consts[76], mod_consts[37], NULL, 0, 14, 0);
    code_objects_5c12c03745f7ac59f865dcf21de946cc = MAKE_CODE_OBJECT(module_filename_obj, 371, CO_OPTIMIZED | CO_NEWLOCALS, mod_consts[3], mod_consts[4], mod_consts[86], mod_consts[87], 1, 0, 0);
}
#endif

// The module function declarations.
static PyObject *MAKE_FUNCTION_attr$_next_gen$$36$$$36$$$36$function__1_define(PyThreadState *tstate, PyObject *defaults, PyObject *kw_defaults);


static PyObject *MAKE_FUNCTION_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it(PyThreadState *tstate, struct Nuitka_CellObject **closure);


static PyObject *MAKE_FUNCTION_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap(PyThreadState *tstate, struct Nuitka_CellObject **closure);


static PyObject *MAKE_FUNCTION_attr$_next_gen$$36$$$36$$$36$function__2_field(PyThreadState *tstate, PyObject *kw_defaults);


static PyObject *MAKE_FUNCTION_attr$_next_gen$$36$$$36$$$36$function__3_asdict(PyThreadState *tstate, PyObject *kw_defaults);


static PyObject *MAKE_FUNCTION_attr$_next_gen$$36$$$36$$$36$function__4_astuple(PyThreadState *tstate, PyObject *kw_defaults);


// The module function definitions.
static PyObject *impl_attr$_next_gen$$36$$$36$$$36$function__1_define(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_maybe_cls = python_pars[0];
    struct Nuitka_CellObject *par_these = Nuitka_Cell_New1(python_pars[1]);
    struct Nuitka_CellObject *par_repr = Nuitka_Cell_New1(python_pars[2]);
    struct Nuitka_CellObject *par_unsafe_hash = Nuitka_Cell_New1(python_pars[3]);
    struct Nuitka_CellObject *par_hash = Nuitka_Cell_New1(python_pars[4]);
    struct Nuitka_CellObject *par_init = Nuitka_Cell_New1(python_pars[5]);
    struct Nuitka_CellObject *par_slots = Nuitka_Cell_New1(python_pars[6]);
    struct Nuitka_CellObject *par_frozen = Nuitka_Cell_New1(python_pars[7]);
    struct Nuitka_CellObject *par_weakref_slot = Nuitka_Cell_New1(python_pars[8]);
    struct Nuitka_CellObject *par_str = Nuitka_Cell_New1(python_pars[9]);
    struct Nuitka_CellObject *par_auto_attribs = Nuitka_Cell_New1(python_pars[10]);
    struct Nuitka_CellObject *par_kw_only = Nuitka_Cell_New1(python_pars[11]);
    struct Nuitka_CellObject *par_cache_hash = Nuitka_Cell_New1(python_pars[12]);
    struct Nuitka_CellObject *par_auto_exc = Nuitka_Cell_New1(python_pars[13]);
    struct Nuitka_CellObject *par_eq = Nuitka_Cell_New1(python_pars[14]);
    struct Nuitka_CellObject *par_order = Nuitka_Cell_New1(python_pars[15]);
    struct Nuitka_CellObject *par_auto_detect = Nuitka_Cell_New1(python_pars[16]);
    struct Nuitka_CellObject *par_getstate_setstate = Nuitka_Cell_New1(python_pars[17]);
    struct Nuitka_CellObject *par_on_setattr = Nuitka_Cell_New1(python_pars[18]);
    struct Nuitka_CellObject *par_field_transformer = Nuitka_Cell_New1(python_pars[19]);
    struct Nuitka_CellObject *par_match_args = Nuitka_Cell_New1(python_pars[20]);
    struct Nuitka_CellObject *var_do_it = Nuitka_Cell_NewEmpty();
    PyObject *var_wrap = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_FrameObject *frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;

    // Actual function body.
    {
        PyObject *tmp_assign_source_1;
        struct Nuitka_CellObject *tmp_closure_1[19];

        tmp_closure_1[0] = par_auto_detect;
        Py_INCREF(tmp_closure_1[0]);
        tmp_closure_1[1] = par_auto_exc;
        Py_INCREF(tmp_closure_1[1]);
        tmp_closure_1[2] = par_cache_hash;
        Py_INCREF(tmp_closure_1[2]);
        tmp_closure_1[3] = par_eq;
        Py_INCREF(tmp_closure_1[3]);
        tmp_closure_1[4] = par_field_transformer;
        Py_INCREF(tmp_closure_1[4]);
        tmp_closure_1[5] = par_frozen;
        Py_INCREF(tmp_closure_1[5]);
        tmp_closure_1[6] = par_getstate_setstate;
        Py_INCREF(tmp_closure_1[6]);
        tmp_closure_1[7] = par_hash;
        Py_INCREF(tmp_closure_1[7]);
        tmp_closure_1[8] = par_init;
        Py_INCREF(tmp_closure_1[8]);
        tmp_closure_1[9] = par_kw_only;
        Py_INCREF(tmp_closure_1[9]);
        tmp_closure_1[10] = par_match_args;
        Py_INCREF(tmp_closure_1[10]);
        tmp_closure_1[11] = par_on_setattr;
        Py_INCREF(tmp_closure_1[11]);
        tmp_closure_1[12] = par_order;
        Py_INCREF(tmp_closure_1[12]);
        tmp_closure_1[13] = par_repr;
        Py_INCREF(tmp_closure_1[13]);
        tmp_closure_1[14] = par_slots;
        Py_INCREF(tmp_closure_1[14]);
        tmp_closure_1[15] = par_str;
        Py_INCREF(tmp_closure_1[15]);
        tmp_closure_1[16] = par_these;
        Py_INCREF(tmp_closure_1[16]);
        tmp_closure_1[17] = par_unsafe_hash;
        Py_INCREF(tmp_closure_1[17]);
        tmp_closure_1[18] = par_weakref_slot;
        Py_INCREF(tmp_closure_1[18]);

        tmp_assign_source_1 = MAKE_FUNCTION_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it(tstate, tmp_closure_1);

        assert(Nuitka_Cell_GET(var_do_it) == NULL);
        Nuitka_Cell_SET(var_do_it, tmp_assign_source_1);

    }
    {
        PyObject *tmp_assign_source_2;
        struct Nuitka_CellObject *tmp_closure_2[4];

        tmp_closure_2[0] = par_auto_attribs;
        Py_INCREF(tmp_closure_2[0]);
        tmp_closure_2[1] = var_do_it;
        Py_INCREF(tmp_closure_2[1]);
        tmp_closure_2[2] = par_frozen;
        Py_INCREF(tmp_closure_2[2]);
        tmp_closure_2[3] = par_on_setattr;
        Py_INCREF(tmp_closure_2[3]);

        tmp_assign_source_2 = MAKE_FUNCTION_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap(tstate, tmp_closure_2);

        assert(var_wrap == NULL);
        var_wrap = tmp_assign_source_2;
    }
    // Tried code:
    {
        bool tmp_condition_result_1;
        PyObject *tmp_cmp_expr_left_1;
        PyObject *tmp_cmp_expr_right_1;
        CHECK_OBJECT(par_maybe_cls);
        tmp_cmp_expr_left_1 = par_maybe_cls;
        tmp_cmp_expr_right_1 = Py_None;
        tmp_condition_result_1 = (tmp_cmp_expr_left_1 == tmp_cmp_expr_right_1) ? true : false;
        if (tmp_condition_result_1 != false) {
            goto branch_yes_1;
        } else {
            goto branch_no_1;
        }
    }
    branch_yes_1:;
    CHECK_OBJECT(var_wrap);
    tmp_return_value = var_wrap;
    Py_INCREF(tmp_return_value);
    goto try_return_handler_1;
    branch_no_1:;
    if (isFrameUnusable(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define)) {
        Py_XDECREF(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define = MAKE_FUNCTION_FRAME(tstate, code_objects_2495b058fcbd29cf0f4d697b6742b40a, module_attr$_next_gen, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define->m_type_description == NULL);
    frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define = cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define);
    assert(Py_REFCNT(frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        CHECK_OBJECT(var_wrap);
        tmp_called_value_1 = var_wrap;
        CHECK_OBJECT(par_maybe_cls);
        tmp_args_element_value_1 = par_maybe_cls;
        frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define->m_frame.f_lineno = 409;
        tmp_return_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_1, tmp_args_element_value_1);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 409;
            type_description_1 = "occccccccccccccccccccco";
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
            exception_tb = MAKE_TRACEBACK(frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define,
        type_description_1,
        par_maybe_cls,
        par_these,
        par_repr,
        par_unsafe_hash,
        par_hash,
        par_init,
        par_slots,
        par_frozen,
        par_weakref_slot,
        par_str,
        par_auto_attribs,
        par_kw_only,
        par_cache_hash,
        par_auto_exc,
        par_eq,
        par_order,
        par_auto_detect,
        par_getstate_setstate,
        par_on_setattr,
        par_field_transformer,
        par_match_args,
        var_do_it,
        var_wrap
    );


    // Release cached frame if used for exception.
    if (frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define == cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define);
        cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define = NULL;
    }

    assertFrameObject(frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Return handler code:
    try_return_handler_1:;
    CHECK_OBJECT(par_on_setattr);
    Py_DECREF(par_on_setattr);
    par_on_setattr = NULL;
    CHECK_OBJECT(var_do_it);
    Py_DECREF(var_do_it);
    var_do_it = NULL;
    CHECK_OBJECT(var_wrap);
    Py_DECREF(var_wrap);
    var_wrap = NULL;
    goto function_return_exit;
    // Exception handler code:
    try_except_handler_1:;
    exception_keeper_lineno_1 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_1 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    CHECK_OBJECT(par_on_setattr);
    Py_DECREF(par_on_setattr);
    par_on_setattr = NULL;
    CHECK_OBJECT(var_do_it);
    Py_DECREF(var_do_it);
    var_do_it = NULL;
    CHECK_OBJECT(var_wrap);
    Py_DECREF(var_wrap);
    var_wrap = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_1;
    exception_lineno = exception_keeper_lineno_1;

    goto function_exception_exit;
    // End of try:

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_maybe_cls);
    Py_DECREF(par_maybe_cls);
    CHECK_OBJECT(par_these);
    Py_DECREF(par_these);
    CHECK_OBJECT(par_repr);
    Py_DECREF(par_repr);
    CHECK_OBJECT(par_unsafe_hash);
    Py_DECREF(par_unsafe_hash);
    CHECK_OBJECT(par_hash);
    Py_DECREF(par_hash);
    CHECK_OBJECT(par_init);
    Py_DECREF(par_init);
    CHECK_OBJECT(par_slots);
    Py_DECREF(par_slots);
    CHECK_OBJECT(par_frozen);
    Py_DECREF(par_frozen);
    CHECK_OBJECT(par_weakref_slot);
    Py_DECREF(par_weakref_slot);
    CHECK_OBJECT(par_str);
    Py_DECREF(par_str);
    CHECK_OBJECT(par_auto_attribs);
    Py_DECREF(par_auto_attribs);
    CHECK_OBJECT(par_kw_only);
    Py_DECREF(par_kw_only);
    CHECK_OBJECT(par_cache_hash);
    Py_DECREF(par_cache_hash);
    CHECK_OBJECT(par_auto_exc);
    Py_DECREF(par_auto_exc);
    CHECK_OBJECT(par_eq);
    Py_DECREF(par_eq);
    CHECK_OBJECT(par_order);
    Py_DECREF(par_order);
    CHECK_OBJECT(par_auto_detect);
    Py_DECREF(par_auto_detect);
    CHECK_OBJECT(par_getstate_setstate);
    Py_DECREF(par_getstate_setstate);
    CHECK_OBJECT(par_field_transformer);
    Py_DECREF(par_field_transformer);
    CHECK_OBJECT(par_match_args);
    Py_DECREF(par_match_args);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_maybe_cls);
    Py_DECREF(par_maybe_cls);
    CHECK_OBJECT(par_these);
    Py_DECREF(par_these);
    CHECK_OBJECT(par_repr);
    Py_DECREF(par_repr);
    CHECK_OBJECT(par_unsafe_hash);
    Py_DECREF(par_unsafe_hash);
    CHECK_OBJECT(par_hash);
    Py_DECREF(par_hash);
    CHECK_OBJECT(par_init);
    Py_DECREF(par_init);
    CHECK_OBJECT(par_slots);
    Py_DECREF(par_slots);
    CHECK_OBJECT(par_frozen);
    Py_DECREF(par_frozen);
    CHECK_OBJECT(par_weakref_slot);
    Py_DECREF(par_weakref_slot);
    CHECK_OBJECT(par_str);
    Py_DECREF(par_str);
    CHECK_OBJECT(par_auto_attribs);
    Py_DECREF(par_auto_attribs);
    CHECK_OBJECT(par_kw_only);
    Py_DECREF(par_kw_only);
    CHECK_OBJECT(par_cache_hash);
    Py_DECREF(par_cache_hash);
    CHECK_OBJECT(par_auto_exc);
    Py_DECREF(par_auto_exc);
    CHECK_OBJECT(par_eq);
    Py_DECREF(par_eq);
    CHECK_OBJECT(par_order);
    Py_DECREF(par_order);
    CHECK_OBJECT(par_auto_detect);
    Py_DECREF(par_auto_detect);
    CHECK_OBJECT(par_getstate_setstate);
    Py_DECREF(par_getstate_setstate);
    CHECK_OBJECT(par_field_transformer);
    Py_DECREF(par_field_transformer);
    CHECK_OBJECT(par_match_args);
    Py_DECREF(par_match_args);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_cls = python_pars[0];
    PyObject *par_auto_attribs = python_pars[1];
    struct Nuitka_FrameObject *frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it)) {
        Py_XDECREF(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it = MAKE_FUNCTION_FRAME(tstate, code_objects_befb1b9f7bb60137de72f249d182b5b7, module_attr$_next_gen, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it->m_type_description == NULL);
    frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it = cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it);
    assert(Py_REFCNT(frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_kw_call_value_0_1;
        PyObject *tmp_kw_call_value_1_1;
        PyObject *tmp_kw_call_value_2_1;
        PyObject *tmp_kw_call_value_3_1;
        PyObject *tmp_kw_call_value_4_1;
        PyObject *tmp_kw_call_value_5_1;
        PyObject *tmp_kw_call_value_6_1;
        PyObject *tmp_kw_call_value_7_1;
        PyObject *tmp_kw_call_value_8_1;
        PyObject *tmp_kw_call_value_9_1;
        PyObject *tmp_kw_call_value_10_1;
        PyObject *tmp_kw_call_value_11_1;
        PyObject *tmp_kw_call_value_12_1;
        PyObject *tmp_kw_call_value_13_1;
        PyObject *tmp_kw_call_value_14_1;
        PyObject *tmp_kw_call_value_15_1;
        PyObject *tmp_kw_call_value_16_1;
        PyObject *tmp_kw_call_value_17_1;
        PyObject *tmp_kw_call_value_18_1;
        PyObject *tmp_kw_call_value_19_1;
        PyObject *tmp_kw_call_value_20_1;
        PyObject *tmp_kw_call_value_21_1;
        tmp_called_value_1 = module_var_accessor_attr$$36$_next_gen$attrs(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[6]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 346;
            type_description_1 = "ooccccccccccccccccccc";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_cls);
        tmp_kw_call_value_0_1 = par_cls;
        if (Nuitka_Cell_GET(self->m_closure[16]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[7]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 348;
            type_description_1 = "ooccccccccccccccccccc";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_value_1_1 = Nuitka_Cell_GET(self->m_closure[16]);
        if (Nuitka_Cell_GET(self->m_closure[13]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[8]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 349;
            type_description_1 = "ooccccccccccccccccccc";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_value_2_1 = Nuitka_Cell_GET(self->m_closure[13]);
        if (Nuitka_Cell_GET(self->m_closure[7]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[9]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 350;
            type_description_1 = "ooccccccccccccccccccc";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_value_3_1 = Nuitka_Cell_GET(self->m_closure[7]);
        if (Nuitka_Cell_GET(self->m_closure[17]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[10]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 351;
            type_description_1 = "ooccccccccccccccccccc";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_value_4_1 = Nuitka_Cell_GET(self->m_closure[17]);
        if (Nuitka_Cell_GET(self->m_closure[8]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[11]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 352;
            type_description_1 = "ooccccccccccccccccccc";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_value_5_1 = Nuitka_Cell_GET(self->m_closure[8]);
        if (Nuitka_Cell_GET(self->m_closure[14]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[12]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 353;
            type_description_1 = "ooccccccccccccccccccc";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_value_6_1 = Nuitka_Cell_GET(self->m_closure[14]);
        if (Nuitka_Cell_GET(self->m_closure[5]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[13]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 354;
            type_description_1 = "ooccccccccccccccccccc";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_value_7_1 = Nuitka_Cell_GET(self->m_closure[5]);
        if (Nuitka_Cell_GET(self->m_closure[18]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[14]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 355;
            type_description_1 = "ooccccccccccccccccccc";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_value_8_1 = Nuitka_Cell_GET(self->m_closure[18]);
        if (Nuitka_Cell_GET(self->m_closure[15]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[15]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 356;
            type_description_1 = "ooccccccccccccccccccc";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_value_9_1 = Nuitka_Cell_GET(self->m_closure[15]);
        CHECK_OBJECT(par_auto_attribs);
        tmp_kw_call_value_10_1 = par_auto_attribs;
        if (Nuitka_Cell_GET(self->m_closure[9]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[16]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 358;
            type_description_1 = "ooccccccccccccccccccc";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_value_11_1 = Nuitka_Cell_GET(self->m_closure[9]);
        if (Nuitka_Cell_GET(self->m_closure[2]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[17]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 359;
            type_description_1 = "ooccccccccccccccccccc";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_value_12_1 = Nuitka_Cell_GET(self->m_closure[2]);
        if (Nuitka_Cell_GET(self->m_closure[1]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[18]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 360;
            type_description_1 = "ooccccccccccccccccccc";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_value_13_1 = Nuitka_Cell_GET(self->m_closure[1]);
        if (Nuitka_Cell_GET(self->m_closure[3]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[19]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 361;
            type_description_1 = "ooccccccccccccccccccc";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_value_14_1 = Nuitka_Cell_GET(self->m_closure[3]);
        if (Nuitka_Cell_GET(self->m_closure[12]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[20]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 362;
            type_description_1 = "ooccccccccccccccccccc";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_value_15_1 = Nuitka_Cell_GET(self->m_closure[12]);
        if (Nuitka_Cell_GET(self->m_closure[0]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[21]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 363;
            type_description_1 = "ooccccccccccccccccccc";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_value_16_1 = Nuitka_Cell_GET(self->m_closure[0]);
        tmp_kw_call_value_17_1 = Py_True;
        if (Nuitka_Cell_GET(self->m_closure[6]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[22]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 365;
            type_description_1 = "ooccccccccccccccccccc";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_value_18_1 = Nuitka_Cell_GET(self->m_closure[6]);
        if (Nuitka_Cell_GET(self->m_closure[11]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[23]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 366;
            type_description_1 = "ooccccccccccccccccccc";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_value_19_1 = Nuitka_Cell_GET(self->m_closure[11]);
        if (Nuitka_Cell_GET(self->m_closure[4]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[24]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 367;
            type_description_1 = "ooccccccccccccccccccc";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_value_20_1 = Nuitka_Cell_GET(self->m_closure[4]);
        if (Nuitka_Cell_GET(self->m_closure[10]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[25]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 368;
            type_description_1 = "ooccccccccccccccccccc";
            goto frame_exception_exit_1;
        }

        tmp_kw_call_value_21_1 = Nuitka_Cell_GET(self->m_closure[10]);
        frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it->m_frame.f_lineno = 346;
        {
            PyObject *kw_values[22] = {tmp_kw_call_value_0_1, tmp_kw_call_value_1_1, tmp_kw_call_value_2_1, tmp_kw_call_value_3_1, tmp_kw_call_value_4_1, tmp_kw_call_value_5_1, tmp_kw_call_value_6_1, tmp_kw_call_value_7_1, tmp_kw_call_value_8_1, tmp_kw_call_value_9_1, tmp_kw_call_value_10_1, tmp_kw_call_value_11_1, tmp_kw_call_value_12_1, tmp_kw_call_value_13_1, tmp_kw_call_value_14_1, tmp_kw_call_value_15_1, tmp_kw_call_value_16_1, tmp_kw_call_value_17_1, tmp_kw_call_value_18_1, tmp_kw_call_value_19_1, tmp_kw_call_value_20_1, tmp_kw_call_value_21_1};

            tmp_return_value = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_called_value_1, kw_values, mod_consts[26]);
        }

        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 346;
            type_description_1 = "ooccccccccccccccccccc";
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
            exception_tb = MAKE_TRACEBACK(frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it,
        type_description_1,
        par_cls,
        par_auto_attribs,
        self->m_closure[16],
        self->m_closure[13],
        self->m_closure[7],
        self->m_closure[17],
        self->m_closure[8],
        self->m_closure[14],
        self->m_closure[5],
        self->m_closure[18],
        self->m_closure[15],
        self->m_closure[9],
        self->m_closure[2],
        self->m_closure[1],
        self->m_closure[3],
        self->m_closure[12],
        self->m_closure[0],
        self->m_closure[6],
        self->m_closure[11],
        self->m_closure[4],
        self->m_closure[10]
    );


    // Release cached frame if used for exception.
    if (frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it == cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it);
        cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it = NULL;
    }

    assertFrameObject(frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_cls);
    Py_DECREF(par_cls);
    CHECK_OBJECT(par_auto_attribs);
    Py_DECREF(par_auto_attribs);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_cls);
    Py_DECREF(par_cls);
    CHECK_OBJECT(par_auto_attribs);
    Py_DECREF(par_auto_attribs);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_cls = python_pars[0];
    nuitka_bool var_had_on_setattr = NUITKA_BOOL_UNASSIGNED;
    PyObject *var_base_cls = NULL;
    PyObject *tmp_for_loop_1__for_iterator = NULL;
    PyObject *tmp_for_loop_1__iter_value = NULL;
    struct Nuitka_FrameObject *frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    int tmp_res;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_2;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_2;
    struct Nuitka_ExceptionStackItem exception_preserved_1;
    bool tmp_result;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_3;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_3;
    static struct Nuitka_FrameObject *cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_4;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_4;

    // Actual function body.
    // Tried code:
    if (isFrameUnusable(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap)) {
        Py_XDECREF(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap = MAKE_FUNCTION_FRAME(tstate, code_objects_5c12c03745f7ac59f865dcf21de946cc, module_attr$_next_gen, sizeof(void *)+sizeof(nuitka_bool)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap->m_type_description == NULL);
    frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap = cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap);
    assert(Py_REFCNT(frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap) == 2);

    // Framed code:
    {
        nuitka_bool tmp_assign_source_1;
        PyObject *tmp_cmp_expr_left_1;
        PyObject *tmp_cmp_expr_right_1;
        PyObject *tmp_tuple_element_1;
        if (Nuitka_Cell_GET(self->m_closure[3]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[23]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 379;
            type_description_1 = "occboNcc";
            goto frame_exception_exit_1;
        }

        tmp_cmp_expr_left_1 = Nuitka_Cell_GET(self->m_closure[3]);
        tmp_tuple_element_1 = Py_None;
        tmp_cmp_expr_right_1 = MAKE_TUPLE_EMPTY(tstate, 2);
        {
            PyObject *tmp_expression_value_1;
            PyTuple_SET_ITEM0(tmp_cmp_expr_right_1, 0, tmp_tuple_element_1);
            tmp_expression_value_1 = module_var_accessor_attr$$36$_next_gen$setters(tstate);
            if (unlikely(tmp_expression_value_1 == NULL)) {
                RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[27]);
            }

            if (tmp_expression_value_1 == NULL) {
                assert(HAS_EXCEPTION_STATE(&exception_state));



                exception_lineno = 379;
                type_description_1 = "occboNcc";
                goto tuple_build_exception_1;
            }
            tmp_tuple_element_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[28]);
            if (tmp_tuple_element_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 379;
                type_description_1 = "occboNcc";
                goto tuple_build_exception_1;
            }
            PyTuple_SET_ITEM(tmp_cmp_expr_right_1, 1, tmp_tuple_element_1);
        }
        goto tuple_build_noexception_1;
        // Exception handling pass through code for tuple_build:
        tuple_build_exception_1:;
        Py_DECREF(tmp_cmp_expr_right_1);
        goto frame_exception_exit_1;
        // Finished with no exception for tuple_build:
        tuple_build_noexception_1:;
        tmp_res = PySequence_Contains(tmp_cmp_expr_right_1, tmp_cmp_expr_left_1);
        Py_DECREF(tmp_cmp_expr_right_1);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 379;
            type_description_1 = "occboNcc";
            goto frame_exception_exit_1;
        }
        tmp_assign_source_1 = (tmp_res == 0) ? NUITKA_BOOL_TRUE : NUITKA_BOOL_FALSE;
        var_had_on_setattr = tmp_assign_source_1;
    }
    {
        bool tmp_condition_result_1;
        int tmp_and_left_truth_1;
        bool tmp_and_left_value_1;
        bool tmp_and_right_value_1;
        PyObject *tmp_cmp_expr_left_2;
        PyObject *tmp_cmp_expr_right_2;
        PyObject *tmp_cmp_expr_left_3;
        PyObject *tmp_cmp_expr_right_3;
        if (Nuitka_Cell_GET(self->m_closure[2]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[13]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 382;
            type_description_1 = "occboNcc";
            goto frame_exception_exit_1;
        }

        tmp_cmp_expr_left_2 = Nuitka_Cell_GET(self->m_closure[2]);
        tmp_cmp_expr_right_2 = Py_False;
        tmp_and_left_value_1 = (tmp_cmp_expr_left_2 == tmp_cmp_expr_right_2) ? true : false;
        tmp_and_left_truth_1 = tmp_and_left_value_1 != false ? 1 : 0;
        if (tmp_and_left_truth_1 == 1) {
            goto and_right_1;
        } else {
            goto and_left_1;
        }
        and_right_1:;
        if (Nuitka_Cell_GET(self->m_closure[3]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[23]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 382;
            type_description_1 = "occboNcc";
            goto frame_exception_exit_1;
        }

        tmp_cmp_expr_left_3 = Nuitka_Cell_GET(self->m_closure[3]);
        tmp_cmp_expr_right_3 = Py_None;
        tmp_and_right_value_1 = (tmp_cmp_expr_left_3 == tmp_cmp_expr_right_3) ? true : false;
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
        PyObject *tmp_assign_source_2;
        tmp_assign_source_2 = module_var_accessor_attr$$36$_next_gen$_DEFAULT_ON_SETATTR(tstate);
        if (unlikely(tmp_assign_source_2 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[29]);
        }

        if (tmp_assign_source_2 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 383;
            type_description_1 = "occboNcc";
            goto frame_exception_exit_1;
        }
        {
            PyObject *old = Nuitka_Cell_GET(self->m_closure[3]);
            Nuitka_Cell_SET(self->m_closure[3], tmp_assign_source_2);
            Py_INCREF(tmp_assign_source_2);
            Py_XDECREF(old);
        }

    }
    branch_no_1:;
    {
        PyObject *tmp_assign_source_3;
        PyObject *tmp_iter_arg_1;
        PyObject *tmp_expression_value_2;
        CHECK_OBJECT(par_cls);
        tmp_expression_value_2 = par_cls;
        tmp_iter_arg_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_2, mod_consts[30]);
        if (tmp_iter_arg_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 387;
            type_description_1 = "occboNcc";
            goto frame_exception_exit_1;
        }
        tmp_assign_source_3 = MAKE_ITERATOR(tstate, tmp_iter_arg_1);
        Py_DECREF(tmp_iter_arg_1);
        if (tmp_assign_source_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 387;
            type_description_1 = "occboNcc";
            goto frame_exception_exit_1;
        }
        assert(tmp_for_loop_1__for_iterator == NULL);
        tmp_for_loop_1__for_iterator = tmp_assign_source_3;
    }
    // Tried code:
    loop_start_1:;
    {
        PyObject *tmp_next_source_1;
        PyObject *tmp_assign_source_4;
        CHECK_OBJECT(tmp_for_loop_1__for_iterator);
        tmp_next_source_1 = tmp_for_loop_1__for_iterator;
        tmp_assign_source_4 = ITERATOR_NEXT(tmp_next_source_1);
        if (tmp_assign_source_4 == NULL) {
            if (CHECK_AND_CLEAR_STOP_ITERATION_OCCURRED(tstate)) {

                goto loop_end_1;
            } else {

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                type_description_1 = "occboNcc";
                exception_lineno = 387;
                goto try_except_handler_2;
            }
        }

        {
            PyObject *old = tmp_for_loop_1__iter_value;
            tmp_for_loop_1__iter_value = tmp_assign_source_4;
            Py_XDECREF(old);
        }

    }
    {
        PyObject *tmp_assign_source_5;
        CHECK_OBJECT(tmp_for_loop_1__iter_value);
        tmp_assign_source_5 = tmp_for_loop_1__iter_value;
        {
            PyObject *old = var_base_cls;
            var_base_cls = tmp_assign_source_5;
            Py_INCREF(var_base_cls);
            Py_XDECREF(old);
        }

    }
    {
        bool tmp_condition_result_2;
        PyObject *tmp_cmp_expr_left_4;
        PyObject *tmp_cmp_expr_right_4;
        PyObject *tmp_expression_value_3;
        CHECK_OBJECT(var_base_cls);
        tmp_expression_value_3 = var_base_cls;
        tmp_cmp_expr_left_4 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_3, mod_consts[31]);
        if (tmp_cmp_expr_left_4 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 388;
            type_description_1 = "occboNcc";
            goto try_except_handler_2;
        }
        tmp_cmp_expr_right_4 = module_var_accessor_attr$$36$_next_gen$_frozen_setattrs(tstate);
        if (unlikely(tmp_cmp_expr_right_4 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[32]);
        }

        if (tmp_cmp_expr_right_4 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));

            Py_DECREF(tmp_cmp_expr_left_4);

            exception_lineno = 388;
            type_description_1 = "occboNcc";
            goto try_except_handler_2;
        }
        tmp_condition_result_2 = (tmp_cmp_expr_left_4 == tmp_cmp_expr_right_4) ? true : false;
        Py_DECREF(tmp_cmp_expr_left_4);
        if (tmp_condition_result_2 != false) {
            goto branch_yes_2;
        } else {
            goto branch_no_2;
        }
    }
    branch_yes_2:;
    {
        bool tmp_condition_result_3;
        assert(var_had_on_setattr != NUITKA_BOOL_UNASSIGNED);
        tmp_condition_result_3 = var_had_on_setattr == NUITKA_BOOL_TRUE;
        if (tmp_condition_result_3 != false) {
            goto branch_yes_3;
        } else {
            goto branch_no_3;
        }
    }
    branch_yes_3:;
    {
        PyObject *tmp_raise_type_1;
        PyObject *tmp_make_exception_arg_1;
        tmp_make_exception_arg_1 = mod_consts[33];
        frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap->m_frame.f_lineno = 391;
        tmp_raise_type_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_ValueError, tmp_make_exception_arg_1);
        assert(!(tmp_raise_type_1 == NULL));
        exception_state.exception_type = tmp_raise_type_1;
        exception_lineno = 391;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);
        type_description_1 = "occboNcc";
        goto try_except_handler_2;
    }
    branch_no_3:;
    {
        PyObject *tmp_assign_source_6;
        PyObject *tmp_expression_value_4;
        tmp_expression_value_4 = module_var_accessor_attr$$36$_next_gen$setters(tstate);
        if (unlikely(tmp_expression_value_4 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[27]);
        }

        if (tmp_expression_value_4 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 393;
            type_description_1 = "occboNcc";
            goto try_except_handler_2;
        }
        tmp_assign_source_6 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_4, mod_consts[28]);
        if (tmp_assign_source_6 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 393;
            type_description_1 = "occboNcc";
            goto try_except_handler_2;
        }
        {
            PyObject *old = Nuitka_Cell_GET(self->m_closure[3]);
            Nuitka_Cell_SET(self->m_closure[3], tmp_assign_source_6);
            Py_XDECREF(old);
        }

    }
    goto loop_end_1;
    branch_no_2:;
    if (CONSIDER_THREADING(tstate) == false) {
        assert(HAS_ERROR_OCCURRED(tstate));

        FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


        exception_lineno = 387;
        type_description_1 = "occboNcc";
        goto try_except_handler_2;
    }
    goto loop_start_1;
    loop_end_1:;
    goto try_end_1;
    // Exception handler code:
    try_except_handler_2:;
    exception_keeper_lineno_1 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_1 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    Py_XDECREF(tmp_for_loop_1__iter_value);
    tmp_for_loop_1__iter_value = NULL;
    CHECK_OBJECT(tmp_for_loop_1__for_iterator);
    Py_DECREF(tmp_for_loop_1__for_iterator);
    tmp_for_loop_1__for_iterator = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_1;
    exception_lineno = exception_keeper_lineno_1;

    goto frame_exception_exit_1;
    // End of try:
    try_end_1:;
    Py_XDECREF(tmp_for_loop_1__iter_value);
    tmp_for_loop_1__iter_value = NULL;
    CHECK_OBJECT(tmp_for_loop_1__for_iterator);
    Py_DECREF(tmp_for_loop_1__for_iterator);
    tmp_for_loop_1__for_iterator = NULL;
    {
        bool tmp_condition_result_4;
        PyObject *tmp_cmp_expr_left_5;
        PyObject *tmp_cmp_expr_right_5;
        if (Nuitka_Cell_GET(self->m_closure[0]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[34]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 396;
            type_description_1 = "occboNcc";
            goto frame_exception_exit_1;
        }

        tmp_cmp_expr_left_5 = Nuitka_Cell_GET(self->m_closure[0]);
        tmp_cmp_expr_right_5 = Py_None;
        tmp_condition_result_4 = (tmp_cmp_expr_left_5 != tmp_cmp_expr_right_5) ? true : false;
        if (tmp_condition_result_4 != false) {
            goto branch_yes_4;
        } else {
            goto branch_no_4;
        }
    }
    branch_yes_4:;
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_args_element_value_2;
        if (Nuitka_Cell_GET(self->m_closure[1]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[0]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 397;
            type_description_1 = "occboNcc";
            goto frame_exception_exit_1;
        }

        tmp_called_value_1 = Nuitka_Cell_GET(self->m_closure[1]);
        CHECK_OBJECT(par_cls);
        tmp_args_element_value_1 = par_cls;
        if (Nuitka_Cell_GET(self->m_closure[0]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[34]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 397;
            type_description_1 = "occboNcc";
            goto frame_exception_exit_1;
        }

        tmp_args_element_value_2 = Nuitka_Cell_GET(self->m_closure[0]);
        frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap->m_frame.f_lineno = 397;
        {
            PyObject *call_args[] = {tmp_args_element_value_1, tmp_args_element_value_2};
            tmp_return_value = CALL_FUNCTION_WITH_ARGS2(tstate, tmp_called_value_1, call_args);
        }

        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 397;
            type_description_1 = "occboNcc";
            goto frame_exception_exit_1;
        }
        goto frame_return_exit_1;
    }
    branch_no_4:;
    // Tried code:
    {
        PyObject *tmp_called_value_2;
        PyObject *tmp_args_element_value_3;
        PyObject *tmp_args_element_value_4;
        if (Nuitka_Cell_GET(self->m_closure[1]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[0]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 400;
            type_description_1 = "occboNcc";
            goto try_except_handler_3;
        }

        tmp_called_value_2 = Nuitka_Cell_GET(self->m_closure[1]);
        CHECK_OBJECT(par_cls);
        tmp_args_element_value_3 = par_cls;
        tmp_args_element_value_4 = Py_True;
        frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap->m_frame.f_lineno = 400;
        {
            PyObject *call_args[] = {tmp_args_element_value_3, tmp_args_element_value_4};
            tmp_return_value = CALL_FUNCTION_WITH_ARGS2(tstate, tmp_called_value_2, call_args);
        }

        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 400;
            type_description_1 = "occboNcc";
            goto try_except_handler_3;
        }
        goto frame_return_exit_1;
    }
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Exception handler code:
    try_except_handler_3:;
    exception_keeper_lineno_2 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_2 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    // Preserve existing published exception id 1.
    exception_preserved_1 = GET_CURRENT_EXCEPTION(tstate);

    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_keeper_name_2);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap, exception_keeper_lineno_2);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_keeper_name_2, exception_tb);
        } else if (exception_keeper_lineno_2 != 0) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap, exception_keeper_lineno_2);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_keeper_name_2, exception_tb);
        }
    }

    PUBLISH_CURRENT_EXCEPTION(tstate, &exception_keeper_name_2);
    // Tried code:
    {
        bool tmp_condition_result_5;
        PyObject *tmp_cmp_expr_left_6;
        PyObject *tmp_cmp_expr_right_6;
        tmp_cmp_expr_left_6 = EXC_TYPE(tstate);
        tmp_cmp_expr_right_6 = module_var_accessor_attr$$36$_next_gen$UnannotatedAttributeError(tstate);
        if (unlikely(tmp_cmp_expr_right_6 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[35]);
        }

        if (tmp_cmp_expr_right_6 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 401;
            type_description_1 = "occboNcc";
            goto try_except_handler_4;
        }
        tmp_res = EXCEPTION_MATCH_BOOL(tstate, tmp_cmp_expr_left_6, tmp_cmp_expr_right_6);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 401;
            type_description_1 = "occboNcc";
            goto try_except_handler_4;
        }
        tmp_condition_result_5 = (tmp_res != 0) ? true : false;
        if (tmp_condition_result_5 != false) {
            goto branch_yes_5;
        } else {
            goto branch_no_5;
        }
    }
    branch_yes_5:;
    {
        PyObject *tmp_called_value_3;
        PyObject *tmp_args_element_value_5;
        PyObject *tmp_args_element_value_6;
        if (Nuitka_Cell_GET(self->m_closure[1]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[0]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 402;
            type_description_1 = "occboNcc";
            goto try_except_handler_4;
        }

        tmp_called_value_3 = Nuitka_Cell_GET(self->m_closure[1]);
        CHECK_OBJECT(par_cls);
        tmp_args_element_value_5 = par_cls;
        tmp_args_element_value_6 = Py_False;
        frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap->m_frame.f_lineno = 402;
        {
            PyObject *call_args[] = {tmp_args_element_value_5, tmp_args_element_value_6};
            tmp_return_value = CALL_FUNCTION_WITH_ARGS2(tstate, tmp_called_value_3, call_args);
        }

        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 402;
            type_description_1 = "occboNcc";
            goto try_except_handler_4;
        }
        goto try_return_handler_4;
    }
    goto branch_end_5;
    branch_no_5:;
    tmp_result = RERAISE_EXCEPTION(tstate, &exception_state);
    if (unlikely(tmp_result == false)) {
        exception_lineno = 399;
    }

    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);

        if ((exception_tb != NULL) && (exception_tb->tb_frame == &frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap->m_frame)) {
            frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap->m_frame.f_lineno = exception_tb->tb_lineno;
        }
    }
    type_description_1 = "occboNcc";
    goto try_except_handler_4;
    branch_end_5:;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Return handler code:
    try_return_handler_4:;
    // Restore previous exception id 1.
    SET_CURRENT_EXCEPTION(tstate, &exception_preserved_1);

    goto frame_return_exit_1;
    // Exception handler code:
    try_except_handler_4:;
    exception_keeper_lineno_3 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_3 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    // Restore previous exception id 1.
    SET_CURRENT_EXCEPTION(tstate, &exception_preserved_1);

    // Re-raise.
    exception_state = exception_keeper_name_3;
    exception_lineno = exception_keeper_lineno_3;

    goto frame_exception_exit_1;
    // End of try:
    // End of try:


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
            exception_tb = MAKE_TRACEBACK(frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap,
        type_description_1,
        par_cls,
        self->m_closure[2],
        self->m_closure[3],
        (int)var_had_on_setattr,
        var_base_cls,
        NULL,
        self->m_closure[0],
        self->m_closure[1]
    );


    // Release cached frame if used for exception.
    if (frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap == cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap);
        cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap = NULL;
    }

    assertFrameObject(frame_frame_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Return handler code:
    try_return_handler_1:;
    assert(var_had_on_setattr != NUITKA_BOOL_UNASSIGNED);
    var_had_on_setattr = NUITKA_BOOL_UNASSIGNED;
    Py_XDECREF(var_base_cls);
    var_base_cls = NULL;
    goto function_return_exit;
    // Exception handler code:
    try_except_handler_1:;
    exception_keeper_lineno_4 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_4 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    var_had_on_setattr = NUITKA_BOOL_UNASSIGNED;
    Py_XDECREF(var_base_cls);
    var_base_cls = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_4;
    exception_lineno = exception_keeper_lineno_4;

    goto function_exception_exit;
    // End of try:

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_cls);
    Py_DECREF(par_cls);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_cls);
    Py_DECREF(par_cls);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_attr$_next_gen$$36$$$36$$$36$function__2_field(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_default = python_pars[0];
    PyObject *par_validator = python_pars[1];
    PyObject *par_repr = python_pars[2];
    PyObject *par_hash = python_pars[3];
    PyObject *par_init = python_pars[4];
    PyObject *par_metadata = python_pars[5];
    PyObject *par_type = python_pars[6];
    PyObject *par_converter = python_pars[7];
    PyObject *par_factory = python_pars[8];
    PyObject *par_kw_only = python_pars[9];
    PyObject *par_eq = python_pars[10];
    PyObject *par_order = python_pars[11];
    PyObject *par_on_setattr = python_pars[12];
    PyObject *par_alias = python_pars[13];
    struct Nuitka_FrameObject *frame_frame_attr$_next_gen$$36$$$36$$$36$function__2_field;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__2_field = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__2_field)) {
        Py_XDECREF(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__2_field);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__2_field == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__2_field = MAKE_FUNCTION_FRAME(tstate, code_objects_26067c832c2ccb3b824677eb076a8325, module_attr$_next_gen, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__2_field->m_type_description == NULL);
    frame_frame_attr$_next_gen$$36$$$36$$$36$function__2_field = cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__2_field;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_attr$_next_gen$$36$$$36$$$36$function__2_field);
    assert(Py_REFCNT(frame_frame_attr$_next_gen$$36$$$36$$$36$function__2_field) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_kw_call_value_0_1;
        PyObject *tmp_kw_call_value_1_1;
        PyObject *tmp_kw_call_value_2_1;
        PyObject *tmp_kw_call_value_3_1;
        PyObject *tmp_kw_call_value_4_1;
        PyObject *tmp_kw_call_value_5_1;
        PyObject *tmp_kw_call_value_6_1;
        PyObject *tmp_kw_call_value_7_1;
        PyObject *tmp_kw_call_value_8_1;
        PyObject *tmp_kw_call_value_9_1;
        PyObject *tmp_kw_call_value_10_1;
        PyObject *tmp_kw_call_value_11_1;
        PyObject *tmp_kw_call_value_12_1;
        PyObject *tmp_kw_call_value_13_1;
        tmp_called_value_1 = module_var_accessor_attr$$36$_next_gen$attrib(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[36]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 580;
            type_description_1 = "oooooooooooooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_default);
        tmp_kw_call_value_0_1 = par_default;
        CHECK_OBJECT(par_validator);
        tmp_kw_call_value_1_1 = par_validator;
        CHECK_OBJECT(par_repr);
        tmp_kw_call_value_2_1 = par_repr;
        CHECK_OBJECT(par_hash);
        tmp_kw_call_value_3_1 = par_hash;
        CHECK_OBJECT(par_init);
        tmp_kw_call_value_4_1 = par_init;
        CHECK_OBJECT(par_metadata);
        tmp_kw_call_value_5_1 = par_metadata;
        CHECK_OBJECT(par_type);
        tmp_kw_call_value_6_1 = par_type;
        CHECK_OBJECT(par_converter);
        tmp_kw_call_value_7_1 = par_converter;
        CHECK_OBJECT(par_factory);
        tmp_kw_call_value_8_1 = par_factory;
        CHECK_OBJECT(par_kw_only);
        tmp_kw_call_value_9_1 = par_kw_only;
        CHECK_OBJECT(par_eq);
        tmp_kw_call_value_10_1 = par_eq;
        CHECK_OBJECT(par_order);
        tmp_kw_call_value_11_1 = par_order;
        CHECK_OBJECT(par_on_setattr);
        tmp_kw_call_value_12_1 = par_on_setattr;
        CHECK_OBJECT(par_alias);
        tmp_kw_call_value_13_1 = par_alias;
        frame_frame_attr$_next_gen$$36$$$36$$$36$function__2_field->m_frame.f_lineno = 580;
        {
            PyObject *kw_values[14] = {tmp_kw_call_value_0_1, tmp_kw_call_value_1_1, tmp_kw_call_value_2_1, tmp_kw_call_value_3_1, tmp_kw_call_value_4_1, tmp_kw_call_value_5_1, tmp_kw_call_value_6_1, tmp_kw_call_value_7_1, tmp_kw_call_value_8_1, tmp_kw_call_value_9_1, tmp_kw_call_value_10_1, tmp_kw_call_value_11_1, tmp_kw_call_value_12_1, tmp_kw_call_value_13_1};

            tmp_return_value = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_called_value_1, kw_values, mod_consts[37]);
        }

        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 580;
            type_description_1 = "oooooooooooooo";
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
            exception_tb = MAKE_TRACEBACK(frame_frame_attr$_next_gen$$36$$$36$$$36$function__2_field, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_attr$_next_gen$$36$$$36$$$36$function__2_field->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_attr$_next_gen$$36$$$36$$$36$function__2_field, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_attr$_next_gen$$36$$$36$$$36$function__2_field,
        type_description_1,
        par_default,
        par_validator,
        par_repr,
        par_hash,
        par_init,
        par_metadata,
        par_type,
        par_converter,
        par_factory,
        par_kw_only,
        par_eq,
        par_order,
        par_on_setattr,
        par_alias
    );


    // Release cached frame if used for exception.
    if (frame_frame_attr$_next_gen$$36$$$36$$$36$function__2_field == cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__2_field) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__2_field);
        cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__2_field = NULL;
    }

    assertFrameObject(frame_frame_attr$_next_gen$$36$$$36$$$36$function__2_field);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_default);
    Py_DECREF(par_default);
    CHECK_OBJECT(par_validator);
    Py_DECREF(par_validator);
    CHECK_OBJECT(par_repr);
    Py_DECREF(par_repr);
    CHECK_OBJECT(par_hash);
    Py_DECREF(par_hash);
    CHECK_OBJECT(par_init);
    Py_DECREF(par_init);
    CHECK_OBJECT(par_metadata);
    Py_DECREF(par_metadata);
    CHECK_OBJECT(par_type);
    Py_DECREF(par_type);
    CHECK_OBJECT(par_converter);
    Py_DECREF(par_converter);
    CHECK_OBJECT(par_factory);
    Py_DECREF(par_factory);
    CHECK_OBJECT(par_kw_only);
    Py_DECREF(par_kw_only);
    CHECK_OBJECT(par_eq);
    Py_DECREF(par_eq);
    CHECK_OBJECT(par_order);
    Py_DECREF(par_order);
    CHECK_OBJECT(par_on_setattr);
    Py_DECREF(par_on_setattr);
    CHECK_OBJECT(par_alias);
    Py_DECREF(par_alias);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_default);
    Py_DECREF(par_default);
    CHECK_OBJECT(par_validator);
    Py_DECREF(par_validator);
    CHECK_OBJECT(par_repr);
    Py_DECREF(par_repr);
    CHECK_OBJECT(par_hash);
    Py_DECREF(par_hash);
    CHECK_OBJECT(par_init);
    Py_DECREF(par_init);
    CHECK_OBJECT(par_metadata);
    Py_DECREF(par_metadata);
    CHECK_OBJECT(par_type);
    Py_DECREF(par_type);
    CHECK_OBJECT(par_converter);
    Py_DECREF(par_converter);
    CHECK_OBJECT(par_factory);
    Py_DECREF(par_factory);
    CHECK_OBJECT(par_kw_only);
    Py_DECREF(par_kw_only);
    CHECK_OBJECT(par_eq);
    Py_DECREF(par_eq);
    CHECK_OBJECT(par_order);
    Py_DECREF(par_order);
    CHECK_OBJECT(par_on_setattr);
    Py_DECREF(par_on_setattr);
    CHECK_OBJECT(par_alias);
    Py_DECREF(par_alias);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_attr$_next_gen$$36$$$36$$$36$function__3_asdict(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_inst = python_pars[0];
    PyObject *par_recurse = python_pars[1];
    PyObject *par_filter = python_pars[2];
    PyObject *par_value_serializer = python_pars[3];
    struct Nuitka_FrameObject *frame_frame_attr$_next_gen$$36$$$36$$$36$function__3_asdict;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__3_asdict = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__3_asdict)) {
        Py_XDECREF(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__3_asdict);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__3_asdict == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__3_asdict = MAKE_FUNCTION_FRAME(tstate, code_objects_e21a30179c71ad1d3f6279f71c307632, module_attr$_next_gen, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__3_asdict->m_type_description == NULL);
    frame_frame_attr$_next_gen$$36$$$36$$$36$function__3_asdict = cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__3_asdict;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_attr$_next_gen$$36$$$36$$$36$function__3_asdict);
    assert(Py_REFCNT(frame_frame_attr$_next_gen$$36$$$36$$$36$function__3_asdict) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_kw_call_value_0_1;
        PyObject *tmp_kw_call_value_1_1;
        PyObject *tmp_kw_call_value_2_1;
        PyObject *tmp_kw_call_value_3_1;
        PyObject *tmp_kw_call_value_4_1;
        tmp_called_value_1 = module_var_accessor_attr$$36$_next_gen$_asdict(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[39]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 605;
            type_description_1 = "oooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_inst);
        tmp_kw_call_value_0_1 = par_inst;
        CHECK_OBJECT(par_recurse);
        tmp_kw_call_value_1_1 = par_recurse;
        CHECK_OBJECT(par_filter);
        tmp_kw_call_value_2_1 = par_filter;
        CHECK_OBJECT(par_value_serializer);
        tmp_kw_call_value_3_1 = par_value_serializer;
        tmp_kw_call_value_4_1 = Py_True;
        frame_frame_attr$_next_gen$$36$$$36$$$36$function__3_asdict->m_frame.f_lineno = 605;
        {
            PyObject *kw_values[5] = {tmp_kw_call_value_0_1, tmp_kw_call_value_1_1, tmp_kw_call_value_2_1, tmp_kw_call_value_3_1, tmp_kw_call_value_4_1};

            tmp_return_value = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_called_value_1, kw_values, mod_consts[40]);
        }

        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 605;
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
            exception_tb = MAKE_TRACEBACK(frame_frame_attr$_next_gen$$36$$$36$$$36$function__3_asdict, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_attr$_next_gen$$36$$$36$$$36$function__3_asdict->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_attr$_next_gen$$36$$$36$$$36$function__3_asdict, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_attr$_next_gen$$36$$$36$$$36$function__3_asdict,
        type_description_1,
        par_inst,
        par_recurse,
        par_filter,
        par_value_serializer
    );


    // Release cached frame if used for exception.
    if (frame_frame_attr$_next_gen$$36$$$36$$$36$function__3_asdict == cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__3_asdict) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__3_asdict);
        cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__3_asdict = NULL;
    }

    assertFrameObject(frame_frame_attr$_next_gen$$36$$$36$$$36$function__3_asdict);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_inst);
    Py_DECREF(par_inst);
    CHECK_OBJECT(par_recurse);
    Py_DECREF(par_recurse);
    CHECK_OBJECT(par_filter);
    Py_DECREF(par_filter);
    CHECK_OBJECT(par_value_serializer);
    Py_DECREF(par_value_serializer);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_inst);
    Py_DECREF(par_inst);
    CHECK_OBJECT(par_recurse);
    Py_DECREF(par_recurse);
    CHECK_OBJECT(par_filter);
    Py_DECREF(par_filter);
    CHECK_OBJECT(par_value_serializer);
    Py_DECREF(par_value_serializer);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_attr$_next_gen$$36$$$36$$$36$function__4_astuple(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_inst = python_pars[0];
    PyObject *par_recurse = python_pars[1];
    PyObject *par_filter = python_pars[2];
    struct Nuitka_FrameObject *frame_frame_attr$_next_gen$$36$$$36$$$36$function__4_astuple;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__4_astuple = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__4_astuple)) {
        Py_XDECREF(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__4_astuple);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__4_astuple == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__4_astuple = MAKE_FUNCTION_FRAME(tstate, code_objects_2e69c79df4c6f03af861a05de2725eb6, module_attr$_next_gen, sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__4_astuple->m_type_description == NULL);
    frame_frame_attr$_next_gen$$36$$$36$$$36$function__4_astuple = cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__4_astuple;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_attr$_next_gen$$36$$$36$$$36$function__4_astuple);
    assert(Py_REFCNT(frame_frame_attr$_next_gen$$36$$$36$$$36$function__4_astuple) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_kw_call_value_0_1;
        PyObject *tmp_kw_call_value_1_1;
        PyObject *tmp_kw_call_value_2_1;
        PyObject *tmp_kw_call_value_3_1;
        tmp_called_value_1 = module_var_accessor_attr$$36$_next_gen$_astuple(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[42]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 621;
            type_description_1 = "ooo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_inst);
        tmp_kw_call_value_0_1 = par_inst;
        CHECK_OBJECT(par_recurse);
        tmp_kw_call_value_1_1 = par_recurse;
        CHECK_OBJECT(par_filter);
        tmp_kw_call_value_2_1 = par_filter;
        tmp_kw_call_value_3_1 = Py_True;
        frame_frame_attr$_next_gen$$36$$$36$$$36$function__4_astuple->m_frame.f_lineno = 621;
        {
            PyObject *kw_values[4] = {tmp_kw_call_value_0_1, tmp_kw_call_value_1_1, tmp_kw_call_value_2_1, tmp_kw_call_value_3_1};

            tmp_return_value = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_called_value_1, kw_values, mod_consts[43]);
        }

        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 621;
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
            exception_tb = MAKE_TRACEBACK(frame_frame_attr$_next_gen$$36$$$36$$$36$function__4_astuple, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_attr$_next_gen$$36$$$36$$$36$function__4_astuple->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_attr$_next_gen$$36$$$36$$$36$function__4_astuple, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_attr$_next_gen$$36$$$36$$$36$function__4_astuple,
        type_description_1,
        par_inst,
        par_recurse,
        par_filter
    );


    // Release cached frame if used for exception.
    if (frame_frame_attr$_next_gen$$36$$$36$$$36$function__4_astuple == cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__4_astuple) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__4_astuple);
        cache_frame_frame_attr$_next_gen$$36$$$36$$$36$function__4_astuple = NULL;
    }

    assertFrameObject(frame_frame_attr$_next_gen$$36$$$36$$$36$function__4_astuple);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_inst);
    Py_DECREF(par_inst);
    CHECK_OBJECT(par_recurse);
    Py_DECREF(par_recurse);
    CHECK_OBJECT(par_filter);
    Py_DECREF(par_filter);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_inst);
    Py_DECREF(par_inst);
    CHECK_OBJECT(par_recurse);
    Py_DECREF(par_recurse);
    CHECK_OBJECT(par_filter);
    Py_DECREF(par_filter);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}



static PyObject *MAKE_FUNCTION_attr$_next_gen$$36$$$36$$$36$function__1_define(PyThreadState *tstate, PyObject *defaults, PyObject *kw_defaults) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_attr$_next_gen$$36$$$36$$$36$function__1_define,
        mod_consts[66],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_2495b058fcbd29cf0f4d697b6742b40a,
        defaults,
#if PYTHON_VERSION >= 0x300
        kw_defaults,
        NULL,
#endif
        module_attr$_next_gen,
        mod_consts[5],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it(PyThreadState *tstate, struct Nuitka_CellObject **closure) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it,
        mod_consts[0],
#if PYTHON_VERSION >= 0x300
        mod_consts[1],
#endif
        code_objects_befb1b9f7bb60137de72f249d182b5b7,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_attr$_next_gen,
        NULL,
        closure,
        19
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap(PyThreadState *tstate, struct Nuitka_CellObject **closure) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap,
        mod_consts[3],
#if PYTHON_VERSION >= 0x300
        mod_consts[4],
#endif
        code_objects_5c12c03745f7ac59f865dcf21de946cc,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_attr$_next_gen,
        mod_consts[2],
        closure,
        4
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_attr$_next_gen$$36$$$36$$$36$function__2_field(PyThreadState *tstate, PyObject *kw_defaults) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_attr$_next_gen$$36$$$36$$$36$function__2_field,
        mod_consts[76],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_26067c832c2ccb3b824677eb076a8325,
        NULL,
#if PYTHON_VERSION >= 0x300
        kw_defaults,
        NULL,
#endif
        module_attr$_next_gen,
        mod_consts[38],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_attr$_next_gen$$36$$$36$$$36$function__3_asdict(PyThreadState *tstate, PyObject *kw_defaults) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_attr$_next_gen$$36$$$36$$$36$function__3_asdict,
        mod_consts[56],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_e21a30179c71ad1d3f6279f71c307632,
        NULL,
#if PYTHON_VERSION >= 0x300
        kw_defaults,
        NULL,
#endif
        module_attr$_next_gen,
        mod_consts[41],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_attr$_next_gen$$36$$$36$$$36$function__4_astuple(PyThreadState *tstate, PyObject *kw_defaults) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_attr$_next_gen$$36$$$36$$$36$function__4_astuple,
        mod_consts[58],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_2e69c79df4c6f03af861a05de2725eb6,
        NULL,
#if PYTHON_VERSION >= 0x300
        kw_defaults,
        NULL,
#endif
        module_attr$_next_gen,
        mod_consts[44],
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

static function_impl_code const function_table_attr$_next_gen[] = {
    impl_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__1_do_it,
    impl_attr$_next_gen$$36$$$36$$$36$function__1_define$$36$$$36$$$36$function__2_wrap,
    impl_attr$_next_gen$$36$$$36$$$36$function__1_define,
    impl_attr$_next_gen$$36$$$36$$$36$function__2_field,
    impl_attr$_next_gen$$36$$$36$$$36$function__3_asdict,
    impl_attr$_next_gen$$36$$$36$$$36$function__4_astuple,
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

    return Nuitka_Function_GetFunctionState(function, function_table_attr$_next_gen);
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
        module_attr$_next_gen,
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
        function_table_attr$_next_gen,
        sizeof(function_table_attr$_next_gen) / sizeof(function_impl_code)
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
static char const *module_full_name = "attr._next_gen";
#endif

// Internal entry point for module code.
PyObject *modulecode_attr$_next_gen(PyThreadState *tstate, PyObject *module, struct Nuitka_MetaPathBasedLoaderEntry const *loader_entry) {
    // Report entry to PGO.
    PGO_onModuleEntered("attr$_next_gen");

    // Store the module for future use.
    module_attr$_next_gen = module;

    moduledict_attr$_next_gen = MODULE_DICT(module_attr$_next_gen);

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
        PRINT_STRING("attr$_next_gen: Calling setupMetaPathBasedLoader().\n");
#endif
        setupMetaPathBasedLoader(tstate);
#if 0 >= 0
#ifdef _NUITKA_TRACE
        PRINT_STRING("attr$_next_gen: Calling updateMetaPathBasedLoaderModuleRoot().\n");
#endif
        updateMetaPathBasedLoaderModuleRoot(module_full_name);
#endif


#if PYTHON_VERSION >= 0x300
        patchInspectModule(tstate);
#endif

#endif

        /* The constants only used by this module are created now. */
        NUITKA_PRINT_TRACE("attr$_next_gen: Calling createModuleConstants().\n");
        createModuleConstants(tstate);

#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
        createModuleCodeObjects();
#endif
        init_done = true;
    }

#if _NUITKA_MODULE_MODE && 0
    PyObject *pre_load = IMPORT_EMBEDDED_MODULE(tstate, "attr._next_gen" "-preLoad");
    if (pre_load == NULL) {
        return NULL;
    }
#endif

    // PRINT_STRING("in initattr$_next_gen\n");

#ifdef _NUITKA_PLUGIN_DILL_ENABLED
    {
        char const *module_name_c;
        if (loader_entry != NULL) {
            module_name_c = loader_entry->name;
        } else {
            PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)const_str_plain___name__);
            module_name_c = Nuitka_String_AsString(module_name);
        }

        registerDillPluginTables(tstate, module_name_c, &_method_def_reduce_compiled_function, &_method_def_create_compiled_function);
    }
#endif

    // Set "__compiled__" to what version information we have.
    UPDATE_STRING_DICT0(
        moduledict_attr$_next_gen,
        (Nuitka_StringObject *)const_str_plain___compiled__,
        Nuitka_dunder_compiled_value
    );

    // Update "__package__" value to what it ought to be.
    {
#if 0
        UPDATE_STRING_DICT0(
            moduledict_attr$_next_gen,
            (Nuitka_StringObject *)const_str_plain___package__,
            mod_consts[52]
        );
#elif 0
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)const_str_plain___name__);

        UPDATE_STRING_DICT0(
            moduledict_attr$_next_gen,
            (Nuitka_StringObject *)const_str_plain___package__,
            module_name
        );
#else

#if PYTHON_VERSION < 0x300
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)const_str_plain___name__);
        char const *module_name_cstr = PyString_AS_STRING(module_name);

        char const *last_dot = strrchr(module_name_cstr, '.');

        if (last_dot != NULL) {
            UPDATE_STRING_DICT1(
                moduledict_attr$_next_gen,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyString_FromStringAndSize(module_name_cstr, last_dot - module_name_cstr)
            );
        }
#else
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)const_str_plain___name__);
        Py_ssize_t dot_index = PyUnicode_Find(module_name, const_str_dot, 0, PyUnicode_GetLength(module_name), -1);

        if (dot_index != -1) {
            UPDATE_STRING_DICT1(
                moduledict_attr$_next_gen,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyUnicode_Substring(module_name, 0, dot_index)
            );
        }
#endif
#endif
    }

    CHECK_OBJECT(module_attr$_next_gen);

    // For deep importing of a module we need to have "__builtins__", so we set
    // it ourselves in the same way than CPython does. Note: This must be done
    // before the frame object is allocated, or else it may fail.

    if (GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)const_str_plain___builtins__) == NULL) {
        PyObject *value = (PyObject *)builtin_module;

        // Check if main module, not a dict then but the module itself.
#if _NUITKA_MODULE_MODE || !0
        value = PyModule_GetDict(value);
#endif

        UPDATE_STRING_DICT0(moduledict_attr$_next_gen, (Nuitka_StringObject *)const_str_plain___builtins__, value);
    }

    PyObject *module_loader = Nuitka_Loader_New(loader_entry);
    UPDATE_STRING_DICT0(moduledict_attr$_next_gen, (Nuitka_StringObject *)const_str_plain___loader__, module_loader);

#if PYTHON_VERSION >= 0x300
// Set the "__spec__" value

#if 0
    // Main modules just get "None" as spec.
    UPDATE_STRING_DICT0(moduledict_attr$_next_gen, (Nuitka_StringObject *)const_str_plain___spec__, Py_None);
#else
    // Other modules get a "ModuleSpec" from the standard mechanism.
    {
        PyObject *bootstrap_module = getImportLibBootstrapModule();
        CHECK_OBJECT(bootstrap_module);

        PyObject *_spec_from_module = PyObject_GetAttrString(bootstrap_module, "_spec_from_module");
        CHECK_OBJECT(_spec_from_module);

        PyObject *spec_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, _spec_from_module, module_attr$_next_gen);
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

        UPDATE_STRING_DICT1(moduledict_attr$_next_gen, (Nuitka_StringObject *)const_str_plain___spec__, spec_value);
    }
#endif
#endif

    // Temp variables if any
    PyObject *tmp_import_from_1__module = NULL;
    struct Nuitka_FrameObject *frame_frame_attr$_next_gen;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    bool tmp_result;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;
    int tmp_res;

    // Module init code if any


    // Module code.
    {
        PyObject *tmp_assign_source_1;
        tmp_assign_source_1 = mod_consts[45];
        UPDATE_STRING_DICT0(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[46], tmp_assign_source_1);
    }
    {
        PyObject *tmp_assign_source_2;
        tmp_assign_source_2 = module_filename_obj;
        UPDATE_STRING_DICT0(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[47], tmp_assign_source_2);
    }
    frame_frame_attr$_next_gen = MAKE_MODULE_FRAME(code_objects_95b95cc6575a762369322027ca59bd4c, module_attr$_next_gen);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_attr$_next_gen);
    assert(Py_REFCNT(frame_frame_attr$_next_gen) == 2);

    // Framed code:
    {
        PyObject *tmp_assattr_value_1;
        PyObject *tmp_assattr_target_1;
        tmp_assattr_value_1 = module_filename_obj;
        tmp_assattr_target_1 = module_var_accessor_attr$$36$_next_gen$__spec__(tstate);
        assert(!(tmp_assattr_target_1 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_1, mod_consts[48], tmp_assattr_value_1);
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
        tmp_assattr_target_2 = module_var_accessor_attr$$36$_next_gen$__spec__(tstate);
        assert(!(tmp_assattr_target_2 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_2, mod_consts[49], tmp_assattr_value_2);
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
        UPDATE_STRING_DICT0(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[50], tmp_assign_source_3);
    }
    {
        PyObject *tmp_assign_source_4;
        {
            PyObject *hard_module = IMPORT_HARD_FUNCTOOLS();
            tmp_assign_source_4 = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[51]);
        }
        assert(!(tmp_assign_source_4 == NULL));
        UPDATE_STRING_DICT1(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[51], tmp_assign_source_4);
    }
    {
        PyObject *tmp_assign_source_5;
        PyObject *tmp_import_name_from_1;
        PyObject *tmp_name_value_1;
        PyObject *tmp_globals_arg_value_1;
        PyObject *tmp_locals_arg_value_1;
        PyObject *tmp_fromlist_value_1;
        PyObject *tmp_level_value_1;
        tmp_name_value_1 = mod_consts[52];
        tmp_globals_arg_value_1 = (PyObject *)moduledict_attr$_next_gen;
        tmp_locals_arg_value_1 = Py_None;
        tmp_fromlist_value_1 = mod_consts[53];
        tmp_level_value_1 = const_int_pos_1;
        frame_frame_attr$_next_gen->m_frame.f_lineno = 10;
        tmp_import_name_from_1 = IMPORT_MODULE5(tstate, tmp_name_value_1, tmp_globals_arg_value_1, tmp_locals_arg_value_1, tmp_fromlist_value_1, tmp_level_value_1);
        if (tmp_import_name_from_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 10;

            goto frame_exception_exit_1;
        }
        if (PyModule_Check(tmp_import_name_from_1)) {
            tmp_assign_source_5 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_1,
                (PyObject *)moduledict_attr$_next_gen,
                mod_consts[27],
                const_int_0
            );
        } else {
            tmp_assign_source_5 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_1, mod_consts[27]);
        }

        Py_DECREF(tmp_import_name_from_1);
        if (tmp_assign_source_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 10;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[27], tmp_assign_source_5);
    }
    {
        PyObject *tmp_assign_source_6;
        PyObject *tmp_import_name_from_2;
        PyObject *tmp_name_value_2;
        PyObject *tmp_globals_arg_value_2;
        PyObject *tmp_locals_arg_value_2;
        PyObject *tmp_fromlist_value_2;
        PyObject *tmp_level_value_2;
        tmp_name_value_2 = mod_consts[54];
        tmp_globals_arg_value_2 = (PyObject *)moduledict_attr$_next_gen;
        tmp_locals_arg_value_2 = Py_None;
        tmp_fromlist_value_2 = mod_consts[55];
        tmp_level_value_2 = const_int_pos_1;
        frame_frame_attr$_next_gen->m_frame.f_lineno = 11;
        tmp_import_name_from_2 = IMPORT_MODULE5(tstate, tmp_name_value_2, tmp_globals_arg_value_2, tmp_locals_arg_value_2, tmp_fromlist_value_2, tmp_level_value_2);
        if (tmp_import_name_from_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 11;

            goto frame_exception_exit_1;
        }
        if (PyModule_Check(tmp_import_name_from_2)) {
            tmp_assign_source_6 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_2,
                (PyObject *)moduledict_attr$_next_gen,
                mod_consts[56],
                const_int_0
            );
        } else {
            tmp_assign_source_6 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_2, mod_consts[56]);
        }

        Py_DECREF(tmp_import_name_from_2);
        if (tmp_assign_source_6 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 11;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[39], tmp_assign_source_6);
    }
    {
        PyObject *tmp_assign_source_7;
        PyObject *tmp_import_name_from_3;
        PyObject *tmp_name_value_3;
        PyObject *tmp_globals_arg_value_3;
        PyObject *tmp_locals_arg_value_3;
        PyObject *tmp_fromlist_value_3;
        PyObject *tmp_level_value_3;
        tmp_name_value_3 = mod_consts[54];
        tmp_globals_arg_value_3 = (PyObject *)moduledict_attr$_next_gen;
        tmp_locals_arg_value_3 = Py_None;
        tmp_fromlist_value_3 = mod_consts[57];
        tmp_level_value_3 = const_int_pos_1;
        frame_frame_attr$_next_gen->m_frame.f_lineno = 12;
        tmp_import_name_from_3 = IMPORT_MODULE5(tstate, tmp_name_value_3, tmp_globals_arg_value_3, tmp_locals_arg_value_3, tmp_fromlist_value_3, tmp_level_value_3);
        if (tmp_import_name_from_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 12;

            goto frame_exception_exit_1;
        }
        if (PyModule_Check(tmp_import_name_from_3)) {
            tmp_assign_source_7 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_3,
                (PyObject *)moduledict_attr$_next_gen,
                mod_consts[58],
                const_int_0
            );
        } else {
            tmp_assign_source_7 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_3, mod_consts[58]);
        }

        Py_DECREF(tmp_import_name_from_3);
        if (tmp_assign_source_7 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 12;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[42], tmp_assign_source_7);
    }
    {
        PyObject *tmp_assign_source_8;
        PyObject *tmp_name_value_4;
        PyObject *tmp_globals_arg_value_4;
        PyObject *tmp_locals_arg_value_4;
        PyObject *tmp_fromlist_value_4;
        PyObject *tmp_level_value_4;
        tmp_name_value_4 = mod_consts[59];
        tmp_globals_arg_value_4 = (PyObject *)moduledict_attr$_next_gen;
        tmp_locals_arg_value_4 = Py_None;
        tmp_fromlist_value_4 = mod_consts[60];
        tmp_level_value_4 = const_int_pos_1;
        frame_frame_attr$_next_gen->m_frame.f_lineno = 13;
        tmp_assign_source_8 = IMPORT_MODULE5(tstate, tmp_name_value_4, tmp_globals_arg_value_4, tmp_locals_arg_value_4, tmp_fromlist_value_4, tmp_level_value_4);
        if (tmp_assign_source_8 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 13;

            goto frame_exception_exit_1;
        }
        assert(tmp_import_from_1__module == NULL);
        tmp_import_from_1__module = tmp_assign_source_8;
    }
    // Tried code:
    {
        PyObject *tmp_assign_source_9;
        PyObject *tmp_import_name_from_4;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_4 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_4)) {
            tmp_assign_source_9 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_4,
                (PyObject *)moduledict_attr$_next_gen,
                mod_consts[29],
                const_int_0
            );
        } else {
            tmp_assign_source_9 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_4, mod_consts[29]);
        }

        if (tmp_assign_source_9 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 13;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[29], tmp_assign_source_9);
    }
    {
        PyObject *tmp_assign_source_10;
        PyObject *tmp_import_name_from_5;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_5 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_5)) {
            tmp_assign_source_10 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_5,
                (PyObject *)moduledict_attr$_next_gen,
                mod_consts[61],
                const_int_0
            );
        } else {
            tmp_assign_source_10 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_5, mod_consts[61]);
        }

        if (tmp_assign_source_10 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 13;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[61], tmp_assign_source_10);
    }
    {
        PyObject *tmp_assign_source_11;
        PyObject *tmp_import_name_from_6;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_6 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_6)) {
            tmp_assign_source_11 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_6,
                (PyObject *)moduledict_attr$_next_gen,
                mod_consts[32],
                const_int_0
            );
        } else {
            tmp_assign_source_11 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_6, mod_consts[32]);
        }

        if (tmp_assign_source_11 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 13;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[32], tmp_assign_source_11);
    }
    {
        PyObject *tmp_assign_source_12;
        PyObject *tmp_import_name_from_7;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_7 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_7)) {
            tmp_assign_source_12 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_7,
                (PyObject *)moduledict_attr$_next_gen,
                mod_consts[36],
                const_int_0
            );
        } else {
            tmp_assign_source_12 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_7, mod_consts[36]);
        }

        if (tmp_assign_source_12 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 13;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[36], tmp_assign_source_12);
    }
    {
        PyObject *tmp_assign_source_13;
        PyObject *tmp_import_name_from_8;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_8 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_8)) {
            tmp_assign_source_13 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_8,
                (PyObject *)moduledict_attr$_next_gen,
                mod_consts[6],
                const_int_0
            );
        } else {
            tmp_assign_source_13 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_8, mod_consts[6]);
        }

        if (tmp_assign_source_13 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 13;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[6], tmp_assign_source_13);
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
        PyObject *tmp_assign_source_14;
        PyObject *tmp_import_name_from_9;
        PyObject *tmp_name_value_5;
        PyObject *tmp_globals_arg_value_5;
        PyObject *tmp_locals_arg_value_5;
        PyObject *tmp_fromlist_value_5;
        PyObject *tmp_level_value_5;
        tmp_name_value_5 = mod_consts[62];
        tmp_globals_arg_value_5 = (PyObject *)moduledict_attr$_next_gen;
        tmp_locals_arg_value_5 = Py_None;
        tmp_fromlist_value_5 = mod_consts[63];
        tmp_level_value_5 = const_int_pos_1;
        frame_frame_attr$_next_gen->m_frame.f_lineno = 20;
        tmp_import_name_from_9 = IMPORT_MODULE5(tstate, tmp_name_value_5, tmp_globals_arg_value_5, tmp_locals_arg_value_5, tmp_fromlist_value_5, tmp_level_value_5);
        if (tmp_import_name_from_9 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 20;

            goto frame_exception_exit_1;
        }
        if (PyModule_Check(tmp_import_name_from_9)) {
            tmp_assign_source_14 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_9,
                (PyObject *)moduledict_attr$_next_gen,
                mod_consts[35],
                const_int_0
            );
        } else {
            tmp_assign_source_14 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_9, mod_consts[35]);
        }

        Py_DECREF(tmp_import_name_from_9);
        if (tmp_assign_source_14 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 20;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[35], tmp_assign_source_14);
    }
    {
        PyObject *tmp_assign_source_15;
        PyObject *tmp_defaults_1;
        PyObject *tmp_kw_defaults_1;
        tmp_defaults_1 = mod_consts[64];
        tmp_kw_defaults_1 = DICT_COPY(tstate, mod_consts[65]);
        Py_INCREF(tmp_defaults_1);


        tmp_assign_source_15 = MAKE_FUNCTION_attr$_next_gen$$36$$$36$$$36$function__1_define(tstate, tmp_defaults_1, tmp_kw_defaults_1);

        UPDATE_STRING_DICT1(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[66], tmp_assign_source_15);
    }
    {
        PyObject *tmp_assign_source_16;
        tmp_assign_source_16 = module_var_accessor_attr$$36$_next_gen$define(tstate);
        assert(!(tmp_assign_source_16 == NULL));
        UPDATE_STRING_DICT0(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[67], tmp_assign_source_16);
    }
    {
        PyObject *tmp_assign_source_17;
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_value_1;
        PyObject *tmp_tuple_element_1;
        PyObject *tmp_kwargs_value_1;
        {
            PyObject *hard_module = IMPORT_HARD_FUNCTOOLS();
            tmp_called_value_1 = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[51]);
        }
        assert(!(tmp_called_value_1 == NULL));
        tmp_tuple_element_1 = module_var_accessor_attr$$36$_next_gen$define(tstate);
        if (unlikely(tmp_tuple_element_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[66]);
        }

        if (tmp_tuple_element_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));

            Py_DECREF(tmp_called_value_1);

            exception_lineno = 413;

            goto frame_exception_exit_1;
        }
        tmp_args_value_1 = MAKE_TUPLE_EMPTY(tstate, 1);
        PyTuple_SET_ITEM0(tmp_args_value_1, 0, tmp_tuple_element_1);
        tmp_kwargs_value_1 = DICT_COPY(tstate, mod_consts[68]);
        frame_frame_attr$_next_gen->m_frame.f_lineno = 413;
        tmp_assign_source_17 = CALL_FUNCTION(tstate, tmp_called_value_1, tmp_args_value_1, tmp_kwargs_value_1);
        Py_DECREF(tmp_called_value_1);
        Py_DECREF(tmp_args_value_1);
        Py_DECREF(tmp_kwargs_value_1);
        if (tmp_assign_source_17 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 413;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[13], tmp_assign_source_17);
    }
    {
        PyObject *tmp_assign_source_18;
        PyObject *tmp_kw_defaults_2;
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[69];
        tmp_dict_value_1 = module_var_accessor_attr$$36$_next_gen$NOTHING(tstate);
        if (unlikely(tmp_dict_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[61]);
        }

        if (tmp_dict_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 418;

            goto frame_exception_exit_1;
        }
        tmp_kw_defaults_2 = _PyDict_NewPresized( 14 );
        tmp_res = PyDict_SetItem(tmp_kw_defaults_2, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[70];
        tmp_dict_value_1 = Py_None;
        tmp_res = PyDict_SetItem(tmp_kw_defaults_2, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[8];
        tmp_dict_value_1 = Py_True;
        tmp_res = PyDict_SetItem(tmp_kw_defaults_2, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[9];
        tmp_dict_value_1 = Py_None;
        tmp_res = PyDict_SetItem(tmp_kw_defaults_2, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[11];
        tmp_dict_value_1 = Py_True;
        tmp_res = PyDict_SetItem(tmp_kw_defaults_2, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[71];
        tmp_dict_value_1 = Py_None;
        tmp_res = PyDict_SetItem(tmp_kw_defaults_2, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[72];
        tmp_dict_value_1 = Py_None;
        tmp_res = PyDict_SetItem(tmp_kw_defaults_2, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[73];
        tmp_dict_value_1 = Py_None;
        tmp_res = PyDict_SetItem(tmp_kw_defaults_2, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[74];
        tmp_dict_value_1 = Py_None;
        tmp_res = PyDict_SetItem(tmp_kw_defaults_2, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[16];
        tmp_dict_value_1 = Py_False;
        tmp_res = PyDict_SetItem(tmp_kw_defaults_2, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[19];
        tmp_dict_value_1 = Py_None;
        tmp_res = PyDict_SetItem(tmp_kw_defaults_2, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[20];
        tmp_dict_value_1 = Py_None;
        tmp_res = PyDict_SetItem(tmp_kw_defaults_2, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[23];
        tmp_dict_value_1 = Py_None;
        tmp_res = PyDict_SetItem(tmp_kw_defaults_2, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[75];
        tmp_dict_value_1 = Py_None;
        tmp_res = PyDict_SetItem(tmp_kw_defaults_2, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));


        tmp_assign_source_18 = MAKE_FUNCTION_attr$_next_gen$$36$$$36$$$36$function__2_field(tstate, tmp_kw_defaults_2);

        UPDATE_STRING_DICT1(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[76], tmp_assign_source_18);
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_attr$_next_gen, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_attr$_next_gen->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_attr$_next_gen, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }



    assertFrameObject(frame_frame_attr$_next_gen);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto module_exception_exit;
    frame_no_exception_1:;
    {
        PyObject *tmp_assign_source_19;
        PyObject *tmp_kw_defaults_3;
        tmp_kw_defaults_3 = DICT_COPY(tstate, mod_consts[77]);


        tmp_assign_source_19 = MAKE_FUNCTION_attr$_next_gen$$36$$$36$$$36$function__3_asdict(tstate, tmp_kw_defaults_3);

        UPDATE_STRING_DICT1(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[56], tmp_assign_source_19);
    }
    {
        PyObject *tmp_assign_source_20;
        PyObject *tmp_kw_defaults_4;
        tmp_kw_defaults_4 = DICT_COPY(tstate, mod_consts[78]);


        tmp_assign_source_20 = MAKE_FUNCTION_attr$_next_gen$$36$$$36$$$36$function__4_astuple(tstate, tmp_kw_defaults_4);

        UPDATE_STRING_DICT1(moduledict_attr$_next_gen, (Nuitka_StringObject *)mod_consts[58], tmp_assign_source_20);
    }

    // Report to PGO about leaving the module without error.
    PGO_onModuleExit("attr$_next_gen", false);

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *post_load = IMPORT_EMBEDDED_MODULE(tstate, "attr._next_gen" "-postLoad");
        if (post_load == NULL) {
            return NULL;
        }
    }
#endif

    Py_INCREF(module_attr$_next_gen);
    return module_attr$_next_gen;
    module_exception_exit:

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_attr$_next_gen, (Nuitka_StringObject *)const_str_plain___name__);

        if (module_name != NULL) {
            Nuitka_DelModule(tstate, module_name);
        }
    }
#endif
    PGO_onModuleExit("attr$_next_gen", false);

    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);
    return NULL;
}
