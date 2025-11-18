/* Generated code for Python module 'markdown$extensions$legacy_em'
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

/* The "module_markdown$extensions$legacy_em" is a Python object pointer of module type.
 *
 * Note: For full compatibility with CPython, every module variable access
 * needs to go through it except for cases where the module cannot possibly
 * have changed in the mean time.
 */

PyObject *module_markdown$extensions$legacy_em;
PyDictObject *moduledict_markdown$extensions$legacy_em;

/* The declarations of module constants used, if any. */
static PyObject *mod_consts[64];
#ifndef __NUITKA_NO_ASSERT__
static Py_hash_t mod_consts_hash[64];
#endif

static PyObject *module_filename_obj = NULL;

/* Indicator if this modules private constants were created yet. */
static bool constants_created = false;

/* Function to create module private constants. */
static void createModuleConstants(PyThreadState *tstate) {
    if (constants_created == false) {
        loadConstantsBlob(tstate, &mod_consts[0], UN_TRANSLATE("markdown.extensions.legacy_em"));
        constants_created = true;

#ifndef __NUITKA_NO_ASSERT__
        for (int i = 0; i < 64; i++) {
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
void checkModuleConstants_markdown$extensions$legacy_em(PyThreadState *tstate) {
    // The module may not have been used at all, then ignore this.
    if (constants_created == false) return;

    for (int i = 0; i < 64; i++) {
        assert(mod_consts_hash[i] == DEEP_HASH(tstate, mod_consts[i]));
        CHECK_OBJECT_DEEP(mod_consts[i]);
    }
}
#endif

// Helper to preserving module variables for Python3.11+
#if 12
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
static PyObject *module_var_accessor_markdown$$36$extensions$$36$legacy_em$EMPHASIS_RE(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_markdown$extensions$legacy_em->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_markdown$extensions$legacy_em->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[28]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_markdown$extensions$legacy_em->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[28]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[28]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[28]);
    }

    return result;
}

static PyObject *module_var_accessor_markdown$$36$extensions$$36$legacy_em$EM_STRONG2_RE(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_markdown$extensions$legacy_em->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_markdown$extensions$legacy_em->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[24]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_markdown$extensions$legacy_em->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[24]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[24], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[24]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[24], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[24]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[24]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[24]);
    }

    return result;
}

static PyObject *module_var_accessor_markdown$$36$extensions$$36$legacy_em$EmStrongItem(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_markdown$extensions$legacy_em->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_markdown$extensions$legacy_em->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[23]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_markdown$extensions$legacy_em->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[23]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[23], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[23]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[23], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[23]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[23]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[23]);
    }

    return result;
}

static PyObject *module_var_accessor_markdown$$36$extensions$$36$legacy_em$Extension(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_markdown$extensions$legacy_em->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_markdown$extensions$legacy_em->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[18]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_markdown$extensions$legacy_em->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[18]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[18], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[18]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[18], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[18]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[18]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[18]);
    }

    return result;
}

static PyObject *module_var_accessor_markdown$$36$extensions$$36$legacy_em$LegacyEmExtension(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_markdown$extensions$legacy_em->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_markdown$extensions$legacy_em->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[7]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_markdown$extensions$legacy_em->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[7]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[7]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[7]);
    }

    return result;
}

static PyObject *module_var_accessor_markdown$$36$extensions$$36$legacy_em$LegacyUnderscoreProcessor(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_markdown$extensions$legacy_em->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_markdown$extensions$legacy_em->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[2]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_markdown$extensions$legacy_em->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[2]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[2], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[2]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[2], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[2]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[2]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[2]);
    }

    return result;
}

static PyObject *module_var_accessor_markdown$$36$extensions$$36$legacy_em$STRONG_EM2_RE(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_markdown$extensions$legacy_em->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_markdown$extensions$legacy_em->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[25]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_markdown$extensions$legacy_em->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[25]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[25], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[25]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[25], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[25]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[25]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[25]);
    }

    return result;
}

static PyObject *module_var_accessor_markdown$$36$extensions$$36$legacy_em$STRONG_EM_RE(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_markdown$extensions$legacy_em->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_markdown$extensions$legacy_em->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[32]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_markdown$extensions$legacy_em->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[32]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[32]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[32]);
    }

    return result;
}

static PyObject *module_var_accessor_markdown$$36$extensions$$36$legacy_em$STRONG_RE(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_markdown$extensions$legacy_em->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_markdown$extensions$legacy_em->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[30]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_markdown$extensions$legacy_em->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[30]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[30], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[30]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[30], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[30]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[30]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[30]);
    }

    return result;
}

static PyObject *module_var_accessor_markdown$$36$extensions$$36$legacy_em$UnderscoreProcessor(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_markdown$extensions$legacy_em->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_markdown$extensions$legacy_em->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[22]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_markdown$extensions$legacy_em->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[22]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[22]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[22]);
    }

    return result;
}

static PyObject *module_var_accessor_markdown$$36$extensions$$36$legacy_em$__spec__(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_markdown$extensions$legacy_em->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_markdown$extensions$legacy_em->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[63]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_markdown$extensions$legacy_em->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[63]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[63], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[63]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[63], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[63]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[63]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[63]);
    }

    return result;
}

static PyObject *module_var_accessor_markdown$$36$extensions$$36$legacy_em$re(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_markdown$extensions$legacy_em->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_markdown$extensions$legacy_em->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[26]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_markdown$extensions$legacy_em->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[26]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[26], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[26]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[26], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[26]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[26]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[26]);
    }

    return result;
}


#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
// The module code objects.
static PyCodeObject *code_objects_2bb7f0ee3150a82f74fd1df0c7d4fccb;
static PyCodeObject *code_objects_5342babc2c70b3a0aee8bb1999e29dd9;
static PyCodeObject *code_objects_fafa0a8de8b58686d8e20612dc0a0270;
static PyCodeObject *code_objects_b5efa86ce30ebb187bd97e029737736b;
static PyCodeObject *code_objects_1d130c201c5e14fa7e7e463a17f6d058;

static void createModuleCodeObjects(void) {
    module_filename_obj = MAKE_RELATIVE_PATH(mod_consts[58]); CHECK_OBJECT(module_filename_obj);
    code_objects_2bb7f0ee3150a82f74fd1df0c7d4fccb = MAKE_CODE_OBJECT(module_filename_obj, 1, CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[59], mod_consts[59], NULL, NULL, 0, 0, 0);
    code_objects_5342babc2c70b3a0aee8bb1999e29dd9 = MAKE_CODE_OBJECT(module_filename_obj, 42, CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[7], mod_consts[7], mod_consts[60], NULL, 0, 0, 0);
    code_objects_fafa0a8de8b58686d8e20612dc0a0270 = MAKE_CODE_OBJECT(module_filename_obj, 30, CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[2], mod_consts[2], mod_consts[60], NULL, 0, 0, 0);
    code_objects_b5efa86ce30ebb187bd97e029737736b = MAKE_CODE_OBJECT(module_filename_obj, 45, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[55], mod_consts[56], mod_consts[61], NULL, 2, 0, 0);
    code_objects_1d130c201c5e14fa7e7e463a17f6d058 = MAKE_CODE_OBJECT(module_filename_obj, 50, CO_OPTIMIZED | CO_NEWLOCALS | CO_VARKEYWORDS | CO_NOFREE | CO_FUTURE_ANNOTATIONS, mod_consts[57], mod_consts[57], mod_consts[62], NULL, 0, 0, 0);
}
#endif

// The module function declarations.
NUITKA_CROSS_MODULE PyObject *impl___main__$$36$$$36$$$36$helper_function__mro_entries_conversion(PyThreadState *tstate, PyObject **python_pars);


NUITKA_CROSS_MODULE PyObject *impl___main__$$36$$$36$$$36$helper_function_complex_call_helper_star_dict(PyThreadState *tstate, PyObject **python_pars);


static PyObject *MAKE_FUNCTION_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension(PyThreadState *tstate);


// The module function definitions.
static PyObject *impl_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_md = python_pars[1];
    struct Nuitka_FrameObject *frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    NUITKA_MAY_BE_UNUSED nuitka_void tmp_unused;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown = NULL;
    PyObject *tmp_return_value = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown)) {
        Py_XDECREF(cache_frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown = MAKE_FUNCTION_FRAME(tstate, code_objects_b5efa86ce30ebb187bd97e029737736b, module_markdown$extensions$legacy_em, sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown->m_type_description == NULL);
    frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown = cache_frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown);
    assert(Py_REFCNT(frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_expression_value_1;
        PyObject *tmp_expression_value_2;
        PyObject *tmp_call_result_1;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_called_value_2;
        PyObject *tmp_args_element_value_2;
        PyObject *tmp_args_element_value_3;
        CHECK_OBJECT(par_md);
        tmp_expression_value_2 = par_md;
        tmp_expression_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_2, mod_consts[0]);
        if (tmp_expression_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 47;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        tmp_called_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[1]);
        Py_DECREF(tmp_expression_value_1);
        if (tmp_called_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 47;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        tmp_called_value_2 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$LegacyUnderscoreProcessor(tstate);
        if (unlikely(tmp_called_value_2 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[2]);
        }

        if (tmp_called_value_2 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));

            Py_DECREF(tmp_called_value_1);

            exception_lineno = 47;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown->m_frame.f_lineno = 47;
        tmp_args_element_value_1 = CALL_FUNCTION_WITH_POS_ARGS1(tstate, tmp_called_value_2, mod_consts[3]);

        if (tmp_args_element_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_called_value_1);

            exception_lineno = 47;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        tmp_args_element_value_2 = mod_consts[4];
        tmp_args_element_value_3 = mod_consts[5];
        frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown->m_frame.f_lineno = 47;
        {
            PyObject *call_args[] = {tmp_args_element_value_1, tmp_args_element_value_2, tmp_args_element_value_3};
            tmp_call_result_1 = CALL_FUNCTION_WITH_ARGS3(tstate, tmp_called_value_1, call_args);
        }

        Py_DECREF(tmp_called_value_1);
        Py_DECREF(tmp_args_element_value_1);
        if (tmp_call_result_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 47;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_1);
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown,
        type_description_1,
        par_self,
        par_md
    );


    // Release cached frame if used for exception.
    if (frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown == cache_frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown);
        cache_frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown = NULL;
    }

    assertFrameObject(frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown);

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
    CHECK_OBJECT(par_md);
    Py_DECREF(par_md);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_OBJECT(par_md);
    Py_DECREF(par_md);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_kwargs = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension)) {
        Py_XDECREF(cache_frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension = MAKE_FUNCTION_FRAME(tstate, code_objects_1d130c201c5e14fa7e7e463a17f6d058, module_markdown$extensions$legacy_em, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension->m_type_description == NULL);
    frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension = cache_frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension);
    assert(Py_REFCNT(frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension) == 2);

    // Framed code:
    {
        PyObject *tmp_direct_call_arg1_1;
        PyObject *tmp_direct_call_arg2_1;
        tmp_direct_call_arg1_1 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$LegacyEmExtension(tstate);
        if (unlikely(tmp_direct_call_arg1_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[7]);
        }

        if (tmp_direct_call_arg1_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 52;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_kwargs);
        tmp_direct_call_arg2_1 = par_kwargs;
        Py_INCREF(tmp_direct_call_arg1_1);
        Py_INCREF(tmp_direct_call_arg2_1);

        {
            PyObject *dir_call_args[] = {tmp_direct_call_arg1_1, tmp_direct_call_arg2_1};
            tmp_return_value = impl___main__$$36$$$36$$$36$helper_function_complex_call_helper_star_dict(tstate, dir_call_args);
        }
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 52;
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
            exception_tb = MAKE_TRACEBACK(frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension,
        type_description_1,
        par_kwargs
    );


    // Release cached frame if used for exception.
    if (frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension == cache_frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension);
        cache_frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension = NULL;
    }

    assertFrameObject(frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_kwargs);
    Py_DECREF(par_kwargs);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_kwargs);
    Py_DECREF(par_kwargs);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}



static PyObject *MAKE_FUNCTION_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown,
        mod_consts[55],
#if PYTHON_VERSION >= 0x300
        mod_consts[56],
#endif
        code_objects_b5efa86ce30ebb187bd97e029737736b,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_markdown$extensions$legacy_em,
        mod_consts[6],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension,
        mod_consts[57],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_1d130c201c5e14fa7e7e463a17f6d058,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_markdown$extensions$legacy_em,
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

static function_impl_code const function_table_markdown$extensions$legacy_em[] = {
    impl_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown,
    impl_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension,
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

    return Nuitka_Function_GetFunctionState(function, function_table_markdown$extensions$legacy_em);
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
        module_markdown$extensions$legacy_em,
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
        function_table_markdown$extensions$legacy_em,
        sizeof(function_table_markdown$extensions$legacy_em) / sizeof(function_impl_code)
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
static char const *module_full_name = "markdown.extensions.legacy_em";
#endif

// Internal entry point for module code.
PyObject *modulecode_markdown$extensions$legacy_em(PyThreadState *tstate, PyObject *module, struct Nuitka_MetaPathBasedLoaderEntry const *loader_entry) {
    // Report entry to PGO.
    PGO_onModuleEntered("markdown$extensions$legacy_em");

    // Store the module for future use.
    module_markdown$extensions$legacy_em = module;

    moduledict_markdown$extensions$legacy_em = MODULE_DICT(module_markdown$extensions$legacy_em);

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
        PRINT_STRING("markdown$extensions$legacy_em: Calling setupMetaPathBasedLoader().\n");
#endif
        setupMetaPathBasedLoader(tstate);
#if 0 >= 0
#ifdef _NUITKA_TRACE
        PRINT_STRING("markdown$extensions$legacy_em: Calling updateMetaPathBasedLoaderModuleRoot().\n");
#endif
        updateMetaPathBasedLoaderModuleRoot(module_full_name);
#endif


#if PYTHON_VERSION >= 0x300
        patchInspectModule(tstate);
#endif

#endif

        /* The constants only used by this module are created now. */
        NUITKA_PRINT_TRACE("markdown$extensions$legacy_em: Calling createModuleConstants().\n");
        createModuleConstants(tstate);

#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
        createModuleCodeObjects();
#endif
        init_done = true;
    }

#if _NUITKA_MODULE_MODE && 0
    PyObject *pre_load = IMPORT_EMBEDDED_MODULE(tstate, "markdown.extensions.legacy_em" "-preLoad");
    if (pre_load == NULL) {
        return NULL;
    }
#endif

    // PRINT_STRING("in initmarkdown$extensions$legacy_em\n");

#ifdef _NUITKA_PLUGIN_DILL_ENABLED
    {
        char const *module_name_c;
        if (loader_entry != NULL) {
            module_name_c = loader_entry->name;
        } else {
            PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)const_str_plain___name__);
            module_name_c = Nuitka_String_AsString(module_name);
        }

        registerDillPluginTables(tstate, module_name_c, &_method_def_reduce_compiled_function, &_method_def_create_compiled_function);
    }
#endif

    // Set "__compiled__" to what version information we have.
    UPDATE_STRING_DICT0(
        moduledict_markdown$extensions$legacy_em,
        (Nuitka_StringObject *)const_str_plain___compiled__,
        Nuitka_dunder_compiled_value
    );

    // Update "__package__" value to what it ought to be.
    {
#if 0
        UPDATE_STRING_DICT0(
            moduledict_markdown$extensions$legacy_em,
            (Nuitka_StringObject *)const_str_plain___package__,
            mod_consts[16]
        );
#elif 0
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)const_str_plain___name__);

        UPDATE_STRING_DICT0(
            moduledict_markdown$extensions$legacy_em,
            (Nuitka_StringObject *)const_str_plain___package__,
            module_name
        );
#else

#if PYTHON_VERSION < 0x300
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)const_str_plain___name__);
        char const *module_name_cstr = PyString_AS_STRING(module_name);

        char const *last_dot = strrchr(module_name_cstr, '.');

        if (last_dot != NULL) {
            UPDATE_STRING_DICT1(
                moduledict_markdown$extensions$legacy_em,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyString_FromStringAndSize(module_name_cstr, last_dot - module_name_cstr)
            );
        }
#else
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)const_str_plain___name__);
        Py_ssize_t dot_index = PyUnicode_Find(module_name, const_str_dot, 0, PyUnicode_GetLength(module_name), -1);

        if (dot_index != -1) {
            UPDATE_STRING_DICT1(
                moduledict_markdown$extensions$legacy_em,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyUnicode_Substring(module_name, 0, dot_index)
            );
        }
#endif
#endif
    }

    CHECK_OBJECT(module_markdown$extensions$legacy_em);

    // For deep importing of a module we need to have "__builtins__", so we set
    // it ourselves in the same way than CPython does. Note: This must be done
    // before the frame object is allocated, or else it may fail.

    if (GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)const_str_plain___builtins__) == NULL) {
        PyObject *value = (PyObject *)builtin_module;

        // Check if main module, not a dict then but the module itself.
#if _NUITKA_MODULE_MODE || !0
        value = PyModule_GetDict(value);
#endif

        UPDATE_STRING_DICT0(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)const_str_plain___builtins__, value);
    }

    PyObject *module_loader = Nuitka_Loader_New(loader_entry);
    UPDATE_STRING_DICT0(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)const_str_plain___loader__, module_loader);

#if PYTHON_VERSION >= 0x300
// Set the "__spec__" value

#if 0
    // Main modules just get "None" as spec.
    UPDATE_STRING_DICT0(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)const_str_plain___spec__, Py_None);
#else
    // Other modules get a "ModuleSpec" from the standard mechanism.
    {
        PyObject *bootstrap_module = getImportLibBootstrapModule();
        CHECK_OBJECT(bootstrap_module);

        PyObject *_spec_from_module = PyObject_GetAttrString(bootstrap_module, "_spec_from_module");
        CHECK_OBJECT(_spec_from_module);

        PyObject *spec_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, _spec_from_module, module_markdown$extensions$legacy_em);
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

        UPDATE_STRING_DICT1(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)const_str_plain___spec__, spec_value);
    }
#endif
#endif

    // Temp variables if any
    PyObject *outline_0_var___class__ = NULL;
    PyObject *outline_1_var___class__ = NULL;
    PyObject *tmp_class_creation_1__bases = NULL;
    PyObject *tmp_class_creation_1__bases_orig = NULL;
    PyObject *tmp_class_creation_1__class_decl_dict = NULL;
    PyObject *tmp_class_creation_1__metaclass = NULL;
    PyObject *tmp_class_creation_1__prepared = NULL;
    PyObject *tmp_class_creation_2__bases = NULL;
    PyObject *tmp_class_creation_2__bases_orig = NULL;
    PyObject *tmp_class_creation_2__class_decl_dict = NULL;
    PyObject *tmp_class_creation_2__metaclass = NULL;
    PyObject *tmp_class_creation_2__prepared = NULL;
    PyObject *tmp_import_from_1__module = NULL;
    struct Nuitka_FrameObject *frame_frame_markdown$extensions$legacy_em;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    bool tmp_result;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;
    int tmp_res;
    PyObject *locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30 = NULL;
    PyObject *tmp_dictset_value;
    struct Nuitka_FrameObject *frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_2;
    NUITKA_MAY_BE_UNUSED char const *type_description_2 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_2;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_2;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_3;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_3;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_4;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_4;
    PyObject *locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__2_LegacyEmExtension_42 = NULL;
    struct Nuitka_FrameObject *frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__2_LegacyEmExtension_3;
    NUITKA_MAY_BE_UNUSED char const *type_description_3 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_5;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_5;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_6;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_6;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_7;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_7;

    // Module init code if any


    // Module code.
    {
        PyObject *tmp_assign_source_1;
        tmp_assign_source_1 = mod_consts[9];
        UPDATE_STRING_DICT0(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[10], tmp_assign_source_1);
    }
    {
        PyObject *tmp_assign_source_2;
        tmp_assign_source_2 = module_filename_obj;
        UPDATE_STRING_DICT0(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[11], tmp_assign_source_2);
    }
    frame_frame_markdown$extensions$legacy_em = MAKE_MODULE_FRAME(code_objects_2bb7f0ee3150a82f74fd1df0c7d4fccb, module_markdown$extensions$legacy_em);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_markdown$extensions$legacy_em);
    assert(Py_REFCNT(frame_frame_markdown$extensions$legacy_em) == 2);

    // Framed code:
    {
        PyObject *tmp_assattr_value_1;
        PyObject *tmp_assattr_target_1;
        tmp_assattr_value_1 = module_filename_obj;
        tmp_assattr_target_1 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$__spec__(tstate);
        assert(!(tmp_assattr_target_1 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_1, mod_consts[12], tmp_assattr_value_1);
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
        tmp_assattr_target_2 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$__spec__(tstate);
        assert(!(tmp_assattr_target_2 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_2, mod_consts[13], tmp_assattr_value_2);
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
        UPDATE_STRING_DICT0(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[14], tmp_assign_source_3);
    }
    {
        PyObject *tmp_assign_source_4;
        {
            PyObject *hard_module = IMPORT_HARD___FUTURE__();
            tmp_assign_source_4 = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[15]);
        }
        assert(!(tmp_assign_source_4 == NULL));
        UPDATE_STRING_DICT1(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[15], tmp_assign_source_4);
    }
    {
        PyObject *tmp_assign_source_5;
        PyObject *tmp_import_name_from_1;
        PyObject *tmp_name_value_1;
        PyObject *tmp_globals_arg_value_1;
        PyObject *tmp_locals_arg_value_1;
        PyObject *tmp_fromlist_value_1;
        PyObject *tmp_level_value_1;
        tmp_name_value_1 = mod_consts[16];
        tmp_globals_arg_value_1 = (PyObject *)moduledict_markdown$extensions$legacy_em;
        tmp_locals_arg_value_1 = Py_None;
        tmp_fromlist_value_1 = mod_consts[17];
        tmp_level_value_1 = const_int_pos_1;
        frame_frame_markdown$extensions$legacy_em->m_frame.f_lineno = 16;
        tmp_import_name_from_1 = IMPORT_MODULE5(tstate, tmp_name_value_1, tmp_globals_arg_value_1, tmp_locals_arg_value_1, tmp_fromlist_value_1, tmp_level_value_1);
        if (tmp_import_name_from_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 16;

            goto frame_exception_exit_1;
        }
        if (PyModule_Check(tmp_import_name_from_1)) {
            tmp_assign_source_5 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_1,
                (PyObject *)moduledict_markdown$extensions$legacy_em,
                mod_consts[18],
                const_int_0
            );
        } else {
            tmp_assign_source_5 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_1, mod_consts[18]);
        }

        Py_DECREF(tmp_import_name_from_1);
        if (tmp_assign_source_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 16;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[18], tmp_assign_source_5);
    }
    {
        PyObject *tmp_assign_source_6;
        PyObject *tmp_name_value_2;
        PyObject *tmp_globals_arg_value_2;
        PyObject *tmp_locals_arg_value_2;
        PyObject *tmp_fromlist_value_2;
        PyObject *tmp_level_value_2;
        tmp_name_value_2 = mod_consts[19];
        tmp_globals_arg_value_2 = (PyObject *)moduledict_markdown$extensions$legacy_em;
        tmp_locals_arg_value_2 = Py_None;
        tmp_fromlist_value_2 = mod_consts[20];
        tmp_level_value_2 = mod_consts[21];
        frame_frame_markdown$extensions$legacy_em->m_frame.f_lineno = 17;
        tmp_assign_source_6 = IMPORT_MODULE5(tstate, tmp_name_value_2, tmp_globals_arg_value_2, tmp_locals_arg_value_2, tmp_fromlist_value_2, tmp_level_value_2);
        if (tmp_assign_source_6 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 17;

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
                (PyObject *)moduledict_markdown$extensions$legacy_em,
                mod_consts[22],
                const_int_0
            );
        } else {
            tmp_assign_source_7 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_2, mod_consts[22]);
        }

        if (tmp_assign_source_7 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 17;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[22], tmp_assign_source_7);
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
                (PyObject *)moduledict_markdown$extensions$legacy_em,
                mod_consts[23],
                const_int_0
            );
        } else {
            tmp_assign_source_8 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_3, mod_consts[23]);
        }

        if (tmp_assign_source_8 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 17;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[23], tmp_assign_source_8);
    }
    {
        PyObject *tmp_assign_source_9;
        PyObject *tmp_import_name_from_4;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_4 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_4)) {
            tmp_assign_source_9 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_4,
                (PyObject *)moduledict_markdown$extensions$legacy_em,
                mod_consts[24],
                const_int_0
            );
        } else {
            tmp_assign_source_9 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_4, mod_consts[24]);
        }

        if (tmp_assign_source_9 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 17;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[24], tmp_assign_source_9);
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
                (PyObject *)moduledict_markdown$extensions$legacy_em,
                mod_consts[25],
                const_int_0
            );
        } else {
            tmp_assign_source_10 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_5, mod_consts[25]);
        }

        if (tmp_assign_source_10 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 17;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[25], tmp_assign_source_10);
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
        PyObject *tmp_name_value_3;
        PyObject *tmp_globals_arg_value_3;
        PyObject *tmp_locals_arg_value_3;
        PyObject *tmp_fromlist_value_3;
        PyObject *tmp_level_value_3;
        tmp_name_value_3 = mod_consts[26];
        tmp_globals_arg_value_3 = (PyObject *)moduledict_markdown$extensions$legacy_em;
        tmp_locals_arg_value_3 = Py_None;
        tmp_fromlist_value_3 = Py_None;
        tmp_level_value_3 = const_int_0;
        frame_frame_markdown$extensions$legacy_em->m_frame.f_lineno = 18;
        tmp_assign_source_11 = IMPORT_MODULE5(tstate, tmp_name_value_3, tmp_globals_arg_value_3, tmp_locals_arg_value_3, tmp_fromlist_value_3, tmp_level_value_3);
        if (tmp_assign_source_11 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 18;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[26], tmp_assign_source_11);
    }
    {
        PyObject *tmp_assign_source_12;
        tmp_assign_source_12 = mod_consts[27];
        UPDATE_STRING_DICT0(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[28], tmp_assign_source_12);
    }
    {
        PyObject *tmp_assign_source_13;
        tmp_assign_source_13 = mod_consts[29];
        UPDATE_STRING_DICT0(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[30], tmp_assign_source_13);
    }
    {
        PyObject *tmp_assign_source_14;
        tmp_assign_source_14 = mod_consts[31];
        UPDATE_STRING_DICT0(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[32], tmp_assign_source_14);
    }
    // Tried code:
    {
        PyObject *tmp_assign_source_15;
        PyObject *tmp_tuple_element_1;
        tmp_tuple_element_1 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$UnderscoreProcessor(tstate);
        if (unlikely(tmp_tuple_element_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[22]);
        }

        if (tmp_tuple_element_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 30;

            goto try_except_handler_2;
        }
        tmp_assign_source_15 = MAKE_TUPLE_EMPTY(tstate, 1);
        PyTuple_SET_ITEM0(tmp_assign_source_15, 0, tmp_tuple_element_1);
        assert(tmp_class_creation_1__bases_orig == NULL);
        tmp_class_creation_1__bases_orig = tmp_assign_source_15;
    }
    {
        PyObject *tmp_assign_source_16;
        PyObject *tmp_direct_call_arg1_1;
        CHECK_OBJECT(tmp_class_creation_1__bases_orig);
        tmp_direct_call_arg1_1 = tmp_class_creation_1__bases_orig;
        Py_INCREF(tmp_direct_call_arg1_1);

        {
            PyObject *dir_call_args[] = {tmp_direct_call_arg1_1};
            tmp_assign_source_16 = impl___main__$$36$$$36$$$36$helper_function__mro_entries_conversion(tstate, dir_call_args);
        }
        if (tmp_assign_source_16 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 30;

            goto try_except_handler_2;
        }
        assert(tmp_class_creation_1__bases == NULL);
        tmp_class_creation_1__bases = tmp_assign_source_16;
    }
    {
        PyObject *tmp_assign_source_17;
        tmp_assign_source_17 = MAKE_DICT_EMPTY(tstate);
        assert(tmp_class_creation_1__class_decl_dict == NULL);
        tmp_class_creation_1__class_decl_dict = tmp_assign_source_17;
    }
    {
        PyObject *tmp_assign_source_18;
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


            exception_lineno = 30;

            goto try_except_handler_2;
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


            exception_lineno = 30;

            goto try_except_handler_2;
        }
        tmp_metaclass_value_1 = BUILTIN_TYPE1(tmp_type_arg_1);
        Py_DECREF(tmp_type_arg_1);
        if (tmp_metaclass_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 30;

            goto try_except_handler_2;
        }
        goto condexpr_end_1;
        condexpr_false_1:;
        tmp_metaclass_value_1 = (PyObject *)&PyType_Type;
        Py_INCREF(tmp_metaclass_value_1);
        condexpr_end_1:;
        CHECK_OBJECT(tmp_class_creation_1__bases);
        tmp_bases_value_1 = tmp_class_creation_1__bases;
        tmp_assign_source_18 = SELECT_METACLASS(tstate, tmp_metaclass_value_1, tmp_bases_value_1);
        Py_DECREF(tmp_metaclass_value_1);
        if (tmp_assign_source_18 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 30;

            goto try_except_handler_2;
        }
        assert(tmp_class_creation_1__metaclass == NULL);
        tmp_class_creation_1__metaclass = tmp_assign_source_18;
    }
    {
        bool tmp_condition_result_2;
        PyObject *tmp_expression_value_2;
        CHECK_OBJECT(tmp_class_creation_1__metaclass);
        tmp_expression_value_2 = tmp_class_creation_1__metaclass;
        tmp_res = HAS_ATTR_BOOL2(tstate, tmp_expression_value_2, mod_consts[33]);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 30;

            goto try_except_handler_2;
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
        PyObject *tmp_assign_source_19;
        PyObject *tmp_called_value_1;
        PyObject *tmp_expression_value_3;
        PyObject *tmp_args_value_1;
        PyObject *tmp_tuple_element_2;
        PyObject *tmp_kwargs_value_1;
        CHECK_OBJECT(tmp_class_creation_1__metaclass);
        tmp_expression_value_3 = tmp_class_creation_1__metaclass;
        tmp_called_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_3, mod_consts[33]);
        if (tmp_called_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 30;

            goto try_except_handler_2;
        }
        tmp_tuple_element_2 = mod_consts[2];
        tmp_args_value_1 = MAKE_TUPLE_EMPTY(tstate, 2);
        PyTuple_SET_ITEM0(tmp_args_value_1, 0, tmp_tuple_element_2);
        CHECK_OBJECT(tmp_class_creation_1__bases);
        tmp_tuple_element_2 = tmp_class_creation_1__bases;
        PyTuple_SET_ITEM0(tmp_args_value_1, 1, tmp_tuple_element_2);
        CHECK_OBJECT(tmp_class_creation_1__class_decl_dict);
        tmp_kwargs_value_1 = tmp_class_creation_1__class_decl_dict;
        frame_frame_markdown$extensions$legacy_em->m_frame.f_lineno = 30;
        tmp_assign_source_19 = CALL_FUNCTION(tstate, tmp_called_value_1, tmp_args_value_1, tmp_kwargs_value_1);
        Py_DECREF(tmp_called_value_1);
        Py_DECREF(tmp_args_value_1);
        if (tmp_assign_source_19 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 30;

            goto try_except_handler_2;
        }
        assert(tmp_class_creation_1__prepared == NULL);
        tmp_class_creation_1__prepared = tmp_assign_source_19;
    }
    {
        bool tmp_condition_result_3;
        PyObject *tmp_operand_value_1;
        PyObject *tmp_expression_value_4;
        CHECK_OBJECT(tmp_class_creation_1__prepared);
        tmp_expression_value_4 = tmp_class_creation_1__prepared;
        tmp_res = HAS_ATTR_BOOL2(tstate, tmp_expression_value_4, mod_consts[34]);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 30;

            goto try_except_handler_2;
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
        PyObject *tmp_name_value_4;
        PyObject *tmp_default_value_1;
        tmp_mod_expr_left_1 = mod_consts[35];
        CHECK_OBJECT(tmp_class_creation_1__metaclass);
        tmp_expression_value_5 = tmp_class_creation_1__metaclass;
        tmp_name_value_4 = mod_consts[36];
        tmp_default_value_1 = mod_consts[37];
        tmp_tuple_element_3 = BUILTIN_GETATTR(tstate, tmp_expression_value_5, tmp_name_value_4, tmp_default_value_1);
        if (tmp_tuple_element_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 30;

            goto try_except_handler_2;
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
            tmp_tuple_element_3 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_6, mod_consts[36]);
            Py_DECREF(tmp_expression_value_6);
            if (tmp_tuple_element_3 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 30;

                goto tuple_build_exception_1;
            }
            PyTuple_SET_ITEM(tmp_mod_expr_right_1, 1, tmp_tuple_element_3);
        }
        goto tuple_build_noexception_1;
        // Exception handling pass through code for tuple_build:
        tuple_build_exception_1:;
        Py_DECREF(tmp_mod_expr_right_1);
        goto try_except_handler_2;
        // Finished with no exception for tuple_build:
        tuple_build_noexception_1:;
        tmp_make_exception_arg_1 = BINARY_OPERATION_MOD_OBJECT_UNICODE_TUPLE(tmp_mod_expr_left_1, tmp_mod_expr_right_1);
        Py_DECREF(tmp_mod_expr_right_1);
        if (tmp_make_exception_arg_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 30;

            goto try_except_handler_2;
        }
        frame_frame_markdown$extensions$legacy_em->m_frame.f_lineno = 30;
        tmp_raise_type_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_TypeError, tmp_make_exception_arg_1);
        Py_DECREF(tmp_make_exception_arg_1);
        assert(!(tmp_raise_type_1 == NULL));
        exception_state.exception_type = tmp_raise_type_1;
        exception_lineno = 30;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);

        goto try_except_handler_2;
    }
    branch_no_2:;
    goto branch_end_1;
    branch_no_1:;
    {
        PyObject *tmp_assign_source_20;
        tmp_assign_source_20 = MAKE_DICT_EMPTY(tstate);
        assert(tmp_class_creation_1__prepared == NULL);
        tmp_class_creation_1__prepared = tmp_assign_source_20;
    }
    branch_end_1:;
    {
        PyObject *tmp_assign_source_21;
        {
            PyObject *tmp_set_locals_1;
            CHECK_OBJECT(tmp_class_creation_1__prepared);
            tmp_set_locals_1 = tmp_class_creation_1__prepared;
            locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30 = tmp_set_locals_1;
            Py_INCREF(tmp_set_locals_1);
        }
        // Tried code:
        // Tried code:
        tmp_dictset_value = mod_consts[38];
        tmp_res = PyObject_SetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[39], tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 30;

            goto try_except_handler_4;
        }
        tmp_dictset_value = mod_consts[40];
        tmp_res = PyObject_SetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[10], tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 30;

            goto try_except_handler_4;
        }
        tmp_dictset_value = mod_consts[2];
        tmp_res = PyObject_SetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[41], tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 30;

            goto try_except_handler_4;
        }
        frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_2 = MAKE_CLASS_FRAME(tstate, code_objects_fafa0a8de8b58686d8e20612dc0a0270, module_markdown$extensions$legacy_em, NULL, sizeof(void *));

        // Push the new frame as the currently active one, and we should be exclusively
        // owning it.
        pushFrameStackCompiledFrame(tstate, frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_2);
        assert(Py_REFCNT(frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_2) == 2);

        // Framed code:
        {
            PyObject *tmp_list_element_1;
            PyObject *tmp_called_value_2;
            PyObject *tmp_args_element_value_1;
            PyObject *tmp_called_value_3;
            PyObject *tmp_expression_value_7;
            PyObject *tmp_args_element_value_2;
            PyObject *tmp_args_element_value_3;
            PyObject *tmp_bitor_expr_left_1;
            PyObject *tmp_bitor_expr_right_1;
            PyObject *tmp_expression_value_8;
            PyObject *tmp_expression_value_9;
            PyObject *tmp_args_element_value_4;
            PyObject *tmp_args_element_value_5;
            tmp_called_value_2 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[23]);

            if (tmp_called_value_2 == NULL) {
                if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                    tmp_called_value_2 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$EmStrongItem(tstate);
                    if (unlikely(tmp_called_value_2 == NULL)) {
                        RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[23]);
                    }

                    if (tmp_called_value_2 == NULL) {
                        assert(HAS_EXCEPTION_STATE(&exception_state));



                        exception_lineno = 34;
                        type_description_2 = "o";
                        goto frame_exception_exit_2;
                    }
                    Py_INCREF(tmp_called_value_2);
                } else {
                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    goto frame_exception_exit_2;
                }
            }

            tmp_expression_value_7 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[26]);

            if (tmp_expression_value_7 == NULL) {
                if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                    tmp_expression_value_7 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$re(tstate);
                    if (unlikely(tmp_expression_value_7 == NULL)) {
                        RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[26]);
                    }

                    if (tmp_expression_value_7 == NULL) {
                        assert(HAS_EXCEPTION_STATE(&exception_state));

                        Py_DECREF(tmp_called_value_2);

                        exception_lineno = 34;
                        type_description_2 = "o";
                        goto frame_exception_exit_2;
                    }
                    Py_INCREF(tmp_expression_value_7);
                } else {
                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    goto frame_exception_exit_2;
                }
            }

            tmp_called_value_3 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_7, mod_consts[42]);
            Py_DECREF(tmp_expression_value_7);
            if (tmp_called_value_3 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                Py_DECREF(tmp_called_value_2);

                exception_lineno = 34;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
            tmp_args_element_value_2 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[24]);

            if (tmp_args_element_value_2 == NULL) {
                if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                    tmp_args_element_value_2 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$EM_STRONG2_RE(tstate);
                    if (unlikely(tmp_args_element_value_2 == NULL)) {
                        RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[24]);
                    }

                    if (tmp_args_element_value_2 == NULL) {
                        assert(HAS_EXCEPTION_STATE(&exception_state));

                        Py_DECREF(tmp_called_value_2);
                        Py_DECREF(tmp_called_value_3);

                        exception_lineno = 34;
                        type_description_2 = "o";
                        goto frame_exception_exit_2;
                    }
                    Py_INCREF(tmp_args_element_value_2);
                } else {
                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    goto frame_exception_exit_2;
                }
            }

            tmp_expression_value_8 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[26]);

            if (tmp_expression_value_8 == NULL) {
                if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                    tmp_expression_value_8 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$re(tstate);
                    if (unlikely(tmp_expression_value_8 == NULL)) {
                        RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[26]);
                    }

                    if (tmp_expression_value_8 == NULL) {
                        assert(HAS_EXCEPTION_STATE(&exception_state));

                        Py_DECREF(tmp_called_value_2);
                        Py_DECREF(tmp_called_value_3);
                        Py_DECREF(tmp_args_element_value_2);

                        exception_lineno = 34;
                        type_description_2 = "o";
                        goto frame_exception_exit_2;
                    }
                    Py_INCREF(tmp_expression_value_8);
                } else {
                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    goto frame_exception_exit_2;
                }
            }

            tmp_bitor_expr_left_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_8, mod_consts[43]);
            Py_DECREF(tmp_expression_value_8);
            if (tmp_bitor_expr_left_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                Py_DECREF(tmp_called_value_2);
                Py_DECREF(tmp_called_value_3);
                Py_DECREF(tmp_args_element_value_2);

                exception_lineno = 34;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
            tmp_expression_value_9 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[26]);

            if (tmp_expression_value_9 == NULL) {
                if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                    tmp_expression_value_9 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$re(tstate);
                    if (unlikely(tmp_expression_value_9 == NULL)) {
                        RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[26]);
                    }

                    if (tmp_expression_value_9 == NULL) {
                        assert(HAS_EXCEPTION_STATE(&exception_state));

                        Py_DECREF(tmp_called_value_2);
                        Py_DECREF(tmp_called_value_3);
                        Py_DECREF(tmp_args_element_value_2);
                        Py_DECREF(tmp_bitor_expr_left_1);

                        exception_lineno = 34;
                        type_description_2 = "o";
                        goto frame_exception_exit_2;
                    }
                    Py_INCREF(tmp_expression_value_9);
                } else {
                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    goto frame_exception_exit_2;
                }
            }

            tmp_bitor_expr_right_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_9, mod_consts[44]);
            Py_DECREF(tmp_expression_value_9);
            if (tmp_bitor_expr_right_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                Py_DECREF(tmp_called_value_2);
                Py_DECREF(tmp_called_value_3);
                Py_DECREF(tmp_args_element_value_2);
                Py_DECREF(tmp_bitor_expr_left_1);

                exception_lineno = 34;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
            tmp_args_element_value_3 = BINARY_OPERATION_BITOR_OBJECT_OBJECT_OBJECT(tmp_bitor_expr_left_1, tmp_bitor_expr_right_1);
            Py_DECREF(tmp_bitor_expr_left_1);
            Py_DECREF(tmp_bitor_expr_right_1);
            if (tmp_args_element_value_3 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                Py_DECREF(tmp_called_value_2);
                Py_DECREF(tmp_called_value_3);
                Py_DECREF(tmp_args_element_value_2);

                exception_lineno = 34;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
            frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_2->m_frame.f_lineno = 34;
            {
                PyObject *call_args[] = {tmp_args_element_value_2, tmp_args_element_value_3};
                tmp_args_element_value_1 = CALL_FUNCTION_WITH_ARGS2(tstate, tmp_called_value_3, call_args);
            }

            Py_DECREF(tmp_called_value_3);
            Py_DECREF(tmp_args_element_value_2);
            Py_DECREF(tmp_args_element_value_3);
            if (tmp_args_element_value_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                Py_DECREF(tmp_called_value_2);

                exception_lineno = 34;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
            tmp_args_element_value_4 = mod_consts[45];
            tmp_args_element_value_5 = mod_consts[46];
            frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_2->m_frame.f_lineno = 34;
            {
                PyObject *call_args[] = {tmp_args_element_value_1, tmp_args_element_value_4, tmp_args_element_value_5};
                tmp_list_element_1 = CALL_FUNCTION_WITH_ARGS3(tstate, tmp_called_value_2, call_args);
            }

            Py_DECREF(tmp_called_value_2);
            Py_DECREF(tmp_args_element_value_1);
            if (tmp_list_element_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 34;
                type_description_2 = "o";
                goto frame_exception_exit_2;
            }
            tmp_dictset_value = MAKE_LIST_EMPTY(tstate, 5);
            {
                PyObject *tmp_called_value_4;
                PyObject *tmp_args_element_value_6;
                PyObject *tmp_called_value_5;
                PyObject *tmp_expression_value_10;
                PyObject *tmp_args_element_value_7;
                PyObject *tmp_args_element_value_8;
                PyObject *tmp_bitor_expr_left_2;
                PyObject *tmp_bitor_expr_right_2;
                PyObject *tmp_expression_value_11;
                PyObject *tmp_expression_value_12;
                PyObject *tmp_args_element_value_9;
                PyObject *tmp_args_element_value_10;
                PyObject *tmp_called_value_6;
                PyObject *tmp_args_element_value_11;
                PyObject *tmp_called_value_7;
                PyObject *tmp_expression_value_13;
                PyObject *tmp_args_element_value_12;
                PyObject *tmp_args_element_value_13;
                PyObject *tmp_bitor_expr_left_3;
                PyObject *tmp_bitor_expr_right_3;
                PyObject *tmp_expression_value_14;
                PyObject *tmp_expression_value_15;
                PyObject *tmp_args_element_value_14;
                PyObject *tmp_args_element_value_15;
                PyObject *tmp_called_value_8;
                PyObject *tmp_args_element_value_16;
                PyObject *tmp_called_value_9;
                PyObject *tmp_expression_value_16;
                PyObject *tmp_args_element_value_17;
                PyObject *tmp_args_element_value_18;
                PyObject *tmp_bitor_expr_left_4;
                PyObject *tmp_bitor_expr_right_4;
                PyObject *tmp_expression_value_17;
                PyObject *tmp_expression_value_18;
                PyObject *tmp_args_element_value_19;
                PyObject *tmp_args_element_value_20;
                PyObject *tmp_called_value_10;
                PyObject *tmp_args_element_value_21;
                PyObject *tmp_called_value_11;
                PyObject *tmp_expression_value_19;
                PyObject *tmp_args_element_value_22;
                PyObject *tmp_args_element_value_23;
                PyObject *tmp_bitor_expr_left_5;
                PyObject *tmp_bitor_expr_right_5;
                PyObject *tmp_expression_value_20;
                PyObject *tmp_expression_value_21;
                PyObject *tmp_args_element_value_24;
                PyObject *tmp_args_element_value_25;
                PyList_SET_ITEM(tmp_dictset_value, 0, tmp_list_element_1);
                tmp_called_value_4 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[23]);

                if (tmp_called_value_4 == NULL) {
                    if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                        tmp_called_value_4 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$EmStrongItem(tstate);
                        if (unlikely(tmp_called_value_4 == NULL)) {
                            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[23]);
                        }

                        if (tmp_called_value_4 == NULL) {
                            assert(HAS_EXCEPTION_STATE(&exception_state));



                            exception_lineno = 35;
                            type_description_2 = "o";
                            goto list_build_exception_1;
                        }
                        Py_INCREF(tmp_called_value_4);
                    } else {
                        FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                        goto list_build_exception_1;
                    }
                }

                tmp_expression_value_10 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[26]);

                if (tmp_expression_value_10 == NULL) {
                    if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                        tmp_expression_value_10 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$re(tstate);
                        if (unlikely(tmp_expression_value_10 == NULL)) {
                            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[26]);
                        }

                        if (tmp_expression_value_10 == NULL) {
                            assert(HAS_EXCEPTION_STATE(&exception_state));

                            Py_DECREF(tmp_called_value_4);

                            exception_lineno = 35;
                            type_description_2 = "o";
                            goto list_build_exception_1;
                        }
                        Py_INCREF(tmp_expression_value_10);
                    } else {
                        FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                        goto list_build_exception_1;
                    }
                }

                tmp_called_value_5 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_10, mod_consts[42]);
                Py_DECREF(tmp_expression_value_10);
                if (tmp_called_value_5 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    Py_DECREF(tmp_called_value_4);

                    exception_lineno = 35;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                tmp_args_element_value_7 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[25]);

                if (tmp_args_element_value_7 == NULL) {
                    if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                        tmp_args_element_value_7 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$STRONG_EM2_RE(tstate);
                        if (unlikely(tmp_args_element_value_7 == NULL)) {
                            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[25]);
                        }

                        if (tmp_args_element_value_7 == NULL) {
                            assert(HAS_EXCEPTION_STATE(&exception_state));

                            Py_DECREF(tmp_called_value_4);
                            Py_DECREF(tmp_called_value_5);

                            exception_lineno = 35;
                            type_description_2 = "o";
                            goto list_build_exception_1;
                        }
                        Py_INCREF(tmp_args_element_value_7);
                    } else {
                        FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                        goto list_build_exception_1;
                    }
                }

                tmp_expression_value_11 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[26]);

                if (tmp_expression_value_11 == NULL) {
                    if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                        tmp_expression_value_11 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$re(tstate);
                        if (unlikely(tmp_expression_value_11 == NULL)) {
                            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[26]);
                        }

                        if (tmp_expression_value_11 == NULL) {
                            assert(HAS_EXCEPTION_STATE(&exception_state));

                            Py_DECREF(tmp_called_value_4);
                            Py_DECREF(tmp_called_value_5);
                            Py_DECREF(tmp_args_element_value_7);

                            exception_lineno = 35;
                            type_description_2 = "o";
                            goto list_build_exception_1;
                        }
                        Py_INCREF(tmp_expression_value_11);
                    } else {
                        FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                        goto list_build_exception_1;
                    }
                }

                tmp_bitor_expr_left_2 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_11, mod_consts[43]);
                Py_DECREF(tmp_expression_value_11);
                if (tmp_bitor_expr_left_2 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    Py_DECREF(tmp_called_value_4);
                    Py_DECREF(tmp_called_value_5);
                    Py_DECREF(tmp_args_element_value_7);

                    exception_lineno = 35;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                tmp_expression_value_12 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[26]);

                if (tmp_expression_value_12 == NULL) {
                    if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                        tmp_expression_value_12 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$re(tstate);
                        if (unlikely(tmp_expression_value_12 == NULL)) {
                            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[26]);
                        }

                        if (tmp_expression_value_12 == NULL) {
                            assert(HAS_EXCEPTION_STATE(&exception_state));

                            Py_DECREF(tmp_called_value_4);
                            Py_DECREF(tmp_called_value_5);
                            Py_DECREF(tmp_args_element_value_7);
                            Py_DECREF(tmp_bitor_expr_left_2);

                            exception_lineno = 35;
                            type_description_2 = "o";
                            goto list_build_exception_1;
                        }
                        Py_INCREF(tmp_expression_value_12);
                    } else {
                        FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                        goto list_build_exception_1;
                    }
                }

                tmp_bitor_expr_right_2 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_12, mod_consts[44]);
                Py_DECREF(tmp_expression_value_12);
                if (tmp_bitor_expr_right_2 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    Py_DECREF(tmp_called_value_4);
                    Py_DECREF(tmp_called_value_5);
                    Py_DECREF(tmp_args_element_value_7);
                    Py_DECREF(tmp_bitor_expr_left_2);

                    exception_lineno = 35;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                tmp_args_element_value_8 = BINARY_OPERATION_BITOR_OBJECT_OBJECT_OBJECT(tmp_bitor_expr_left_2, tmp_bitor_expr_right_2);
                Py_DECREF(tmp_bitor_expr_left_2);
                Py_DECREF(tmp_bitor_expr_right_2);
                if (tmp_args_element_value_8 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    Py_DECREF(tmp_called_value_4);
                    Py_DECREF(tmp_called_value_5);
                    Py_DECREF(tmp_args_element_value_7);

                    exception_lineno = 35;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_2->m_frame.f_lineno = 35;
                {
                    PyObject *call_args[] = {tmp_args_element_value_7, tmp_args_element_value_8};
                    tmp_args_element_value_6 = CALL_FUNCTION_WITH_ARGS2(tstate, tmp_called_value_5, call_args);
                }

                Py_DECREF(tmp_called_value_5);
                Py_DECREF(tmp_args_element_value_7);
                Py_DECREF(tmp_args_element_value_8);
                if (tmp_args_element_value_6 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    Py_DECREF(tmp_called_value_4);

                    exception_lineno = 35;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                tmp_args_element_value_9 = mod_consts[45];
                tmp_args_element_value_10 = mod_consts[47];
                frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_2->m_frame.f_lineno = 35;
                {
                    PyObject *call_args[] = {tmp_args_element_value_6, tmp_args_element_value_9, tmp_args_element_value_10};
                    tmp_list_element_1 = CALL_FUNCTION_WITH_ARGS3(tstate, tmp_called_value_4, call_args);
                }

                Py_DECREF(tmp_called_value_4);
                Py_DECREF(tmp_args_element_value_6);
                if (tmp_list_element_1 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                    exception_lineno = 35;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                PyList_SET_ITEM(tmp_dictset_value, 1, tmp_list_element_1);
                tmp_called_value_6 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[23]);

                if (tmp_called_value_6 == NULL) {
                    if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                        tmp_called_value_6 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$EmStrongItem(tstate);
                        if (unlikely(tmp_called_value_6 == NULL)) {
                            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[23]);
                        }

                        if (tmp_called_value_6 == NULL) {
                            assert(HAS_EXCEPTION_STATE(&exception_state));



                            exception_lineno = 36;
                            type_description_2 = "o";
                            goto list_build_exception_1;
                        }
                        Py_INCREF(tmp_called_value_6);
                    } else {
                        FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                        goto list_build_exception_1;
                    }
                }

                tmp_expression_value_13 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[26]);

                if (tmp_expression_value_13 == NULL) {
                    if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                        tmp_expression_value_13 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$re(tstate);
                        if (unlikely(tmp_expression_value_13 == NULL)) {
                            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[26]);
                        }

                        if (tmp_expression_value_13 == NULL) {
                            assert(HAS_EXCEPTION_STATE(&exception_state));

                            Py_DECREF(tmp_called_value_6);

                            exception_lineno = 36;
                            type_description_2 = "o";
                            goto list_build_exception_1;
                        }
                        Py_INCREF(tmp_expression_value_13);
                    } else {
                        FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                        goto list_build_exception_1;
                    }
                }

                tmp_called_value_7 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_13, mod_consts[42]);
                Py_DECREF(tmp_expression_value_13);
                if (tmp_called_value_7 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    Py_DECREF(tmp_called_value_6);

                    exception_lineno = 36;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                tmp_args_element_value_12 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[32]);

                if (tmp_args_element_value_12 == NULL) {
                    if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                        tmp_args_element_value_12 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$STRONG_EM_RE(tstate);
                        if (unlikely(tmp_args_element_value_12 == NULL)) {
                            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[32]);
                        }

                        if (tmp_args_element_value_12 == NULL) {
                            assert(HAS_EXCEPTION_STATE(&exception_state));

                            Py_DECREF(tmp_called_value_6);
                            Py_DECREF(tmp_called_value_7);

                            exception_lineno = 36;
                            type_description_2 = "o";
                            goto list_build_exception_1;
                        }
                        Py_INCREF(tmp_args_element_value_12);
                    } else {
                        FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                        goto list_build_exception_1;
                    }
                }

                tmp_expression_value_14 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[26]);

                if (tmp_expression_value_14 == NULL) {
                    if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                        tmp_expression_value_14 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$re(tstate);
                        if (unlikely(tmp_expression_value_14 == NULL)) {
                            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[26]);
                        }

                        if (tmp_expression_value_14 == NULL) {
                            assert(HAS_EXCEPTION_STATE(&exception_state));

                            Py_DECREF(tmp_called_value_6);
                            Py_DECREF(tmp_called_value_7);
                            Py_DECREF(tmp_args_element_value_12);

                            exception_lineno = 36;
                            type_description_2 = "o";
                            goto list_build_exception_1;
                        }
                        Py_INCREF(tmp_expression_value_14);
                    } else {
                        FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                        goto list_build_exception_1;
                    }
                }

                tmp_bitor_expr_left_3 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_14, mod_consts[43]);
                Py_DECREF(tmp_expression_value_14);
                if (tmp_bitor_expr_left_3 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    Py_DECREF(tmp_called_value_6);
                    Py_DECREF(tmp_called_value_7);
                    Py_DECREF(tmp_args_element_value_12);

                    exception_lineno = 36;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                tmp_expression_value_15 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[26]);

                if (tmp_expression_value_15 == NULL) {
                    if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                        tmp_expression_value_15 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$re(tstate);
                        if (unlikely(tmp_expression_value_15 == NULL)) {
                            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[26]);
                        }

                        if (tmp_expression_value_15 == NULL) {
                            assert(HAS_EXCEPTION_STATE(&exception_state));

                            Py_DECREF(tmp_called_value_6);
                            Py_DECREF(tmp_called_value_7);
                            Py_DECREF(tmp_args_element_value_12);
                            Py_DECREF(tmp_bitor_expr_left_3);

                            exception_lineno = 36;
                            type_description_2 = "o";
                            goto list_build_exception_1;
                        }
                        Py_INCREF(tmp_expression_value_15);
                    } else {
                        FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                        goto list_build_exception_1;
                    }
                }

                tmp_bitor_expr_right_3 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_15, mod_consts[44]);
                Py_DECREF(tmp_expression_value_15);
                if (tmp_bitor_expr_right_3 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    Py_DECREF(tmp_called_value_6);
                    Py_DECREF(tmp_called_value_7);
                    Py_DECREF(tmp_args_element_value_12);
                    Py_DECREF(tmp_bitor_expr_left_3);

                    exception_lineno = 36;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                tmp_args_element_value_13 = BINARY_OPERATION_BITOR_OBJECT_OBJECT_OBJECT(tmp_bitor_expr_left_3, tmp_bitor_expr_right_3);
                Py_DECREF(tmp_bitor_expr_left_3);
                Py_DECREF(tmp_bitor_expr_right_3);
                if (tmp_args_element_value_13 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    Py_DECREF(tmp_called_value_6);
                    Py_DECREF(tmp_called_value_7);
                    Py_DECREF(tmp_args_element_value_12);

                    exception_lineno = 36;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_2->m_frame.f_lineno = 36;
                {
                    PyObject *call_args[] = {tmp_args_element_value_12, tmp_args_element_value_13};
                    tmp_args_element_value_11 = CALL_FUNCTION_WITH_ARGS2(tstate, tmp_called_value_7, call_args);
                }

                Py_DECREF(tmp_called_value_7);
                Py_DECREF(tmp_args_element_value_12);
                Py_DECREF(tmp_args_element_value_13);
                if (tmp_args_element_value_11 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    Py_DECREF(tmp_called_value_6);

                    exception_lineno = 36;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                tmp_args_element_value_14 = mod_consts[48];
                tmp_args_element_value_15 = mod_consts[46];
                frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_2->m_frame.f_lineno = 36;
                {
                    PyObject *call_args[] = {tmp_args_element_value_11, tmp_args_element_value_14, tmp_args_element_value_15};
                    tmp_list_element_1 = CALL_FUNCTION_WITH_ARGS3(tstate, tmp_called_value_6, call_args);
                }

                Py_DECREF(tmp_called_value_6);
                Py_DECREF(tmp_args_element_value_11);
                if (tmp_list_element_1 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                    exception_lineno = 36;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                PyList_SET_ITEM(tmp_dictset_value, 2, tmp_list_element_1);
                tmp_called_value_8 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[23]);

                if (tmp_called_value_8 == NULL) {
                    if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                        tmp_called_value_8 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$EmStrongItem(tstate);
                        if (unlikely(tmp_called_value_8 == NULL)) {
                            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[23]);
                        }

                        if (tmp_called_value_8 == NULL) {
                            assert(HAS_EXCEPTION_STATE(&exception_state));



                            exception_lineno = 37;
                            type_description_2 = "o";
                            goto list_build_exception_1;
                        }
                        Py_INCREF(tmp_called_value_8);
                    } else {
                        FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                        goto list_build_exception_1;
                    }
                }

                tmp_expression_value_16 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[26]);

                if (tmp_expression_value_16 == NULL) {
                    if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                        tmp_expression_value_16 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$re(tstate);
                        if (unlikely(tmp_expression_value_16 == NULL)) {
                            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[26]);
                        }

                        if (tmp_expression_value_16 == NULL) {
                            assert(HAS_EXCEPTION_STATE(&exception_state));

                            Py_DECREF(tmp_called_value_8);

                            exception_lineno = 37;
                            type_description_2 = "o";
                            goto list_build_exception_1;
                        }
                        Py_INCREF(tmp_expression_value_16);
                    } else {
                        FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                        goto list_build_exception_1;
                    }
                }

                tmp_called_value_9 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_16, mod_consts[42]);
                Py_DECREF(tmp_expression_value_16);
                if (tmp_called_value_9 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    Py_DECREF(tmp_called_value_8);

                    exception_lineno = 37;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                tmp_args_element_value_17 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[30]);

                if (tmp_args_element_value_17 == NULL) {
                    if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                        tmp_args_element_value_17 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$STRONG_RE(tstate);
                        if (unlikely(tmp_args_element_value_17 == NULL)) {
                            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[30]);
                        }

                        if (tmp_args_element_value_17 == NULL) {
                            assert(HAS_EXCEPTION_STATE(&exception_state));

                            Py_DECREF(tmp_called_value_8);
                            Py_DECREF(tmp_called_value_9);

                            exception_lineno = 37;
                            type_description_2 = "o";
                            goto list_build_exception_1;
                        }
                        Py_INCREF(tmp_args_element_value_17);
                    } else {
                        FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                        goto list_build_exception_1;
                    }
                }

                tmp_expression_value_17 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[26]);

                if (tmp_expression_value_17 == NULL) {
                    if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                        tmp_expression_value_17 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$re(tstate);
                        if (unlikely(tmp_expression_value_17 == NULL)) {
                            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[26]);
                        }

                        if (tmp_expression_value_17 == NULL) {
                            assert(HAS_EXCEPTION_STATE(&exception_state));

                            Py_DECREF(tmp_called_value_8);
                            Py_DECREF(tmp_called_value_9);
                            Py_DECREF(tmp_args_element_value_17);

                            exception_lineno = 37;
                            type_description_2 = "o";
                            goto list_build_exception_1;
                        }
                        Py_INCREF(tmp_expression_value_17);
                    } else {
                        FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                        goto list_build_exception_1;
                    }
                }

                tmp_bitor_expr_left_4 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_17, mod_consts[43]);
                Py_DECREF(tmp_expression_value_17);
                if (tmp_bitor_expr_left_4 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    Py_DECREF(tmp_called_value_8);
                    Py_DECREF(tmp_called_value_9);
                    Py_DECREF(tmp_args_element_value_17);

                    exception_lineno = 37;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                tmp_expression_value_18 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[26]);

                if (tmp_expression_value_18 == NULL) {
                    if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                        tmp_expression_value_18 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$re(tstate);
                        if (unlikely(tmp_expression_value_18 == NULL)) {
                            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[26]);
                        }

                        if (tmp_expression_value_18 == NULL) {
                            assert(HAS_EXCEPTION_STATE(&exception_state));

                            Py_DECREF(tmp_called_value_8);
                            Py_DECREF(tmp_called_value_9);
                            Py_DECREF(tmp_args_element_value_17);
                            Py_DECREF(tmp_bitor_expr_left_4);

                            exception_lineno = 37;
                            type_description_2 = "o";
                            goto list_build_exception_1;
                        }
                        Py_INCREF(tmp_expression_value_18);
                    } else {
                        FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                        goto list_build_exception_1;
                    }
                }

                tmp_bitor_expr_right_4 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_18, mod_consts[44]);
                Py_DECREF(tmp_expression_value_18);
                if (tmp_bitor_expr_right_4 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    Py_DECREF(tmp_called_value_8);
                    Py_DECREF(tmp_called_value_9);
                    Py_DECREF(tmp_args_element_value_17);
                    Py_DECREF(tmp_bitor_expr_left_4);

                    exception_lineno = 37;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                tmp_args_element_value_18 = BINARY_OPERATION_BITOR_OBJECT_OBJECT_OBJECT(tmp_bitor_expr_left_4, tmp_bitor_expr_right_4);
                Py_DECREF(tmp_bitor_expr_left_4);
                Py_DECREF(tmp_bitor_expr_right_4);
                if (tmp_args_element_value_18 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    Py_DECREF(tmp_called_value_8);
                    Py_DECREF(tmp_called_value_9);
                    Py_DECREF(tmp_args_element_value_17);

                    exception_lineno = 37;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_2->m_frame.f_lineno = 37;
                {
                    PyObject *call_args[] = {tmp_args_element_value_17, tmp_args_element_value_18};
                    tmp_args_element_value_16 = CALL_FUNCTION_WITH_ARGS2(tstate, tmp_called_value_9, call_args);
                }

                Py_DECREF(tmp_called_value_9);
                Py_DECREF(tmp_args_element_value_17);
                Py_DECREF(tmp_args_element_value_18);
                if (tmp_args_element_value_16 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    Py_DECREF(tmp_called_value_8);

                    exception_lineno = 37;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                tmp_args_element_value_19 = mod_consts[49];
                tmp_args_element_value_20 = mod_consts[50];
                frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_2->m_frame.f_lineno = 37;
                {
                    PyObject *call_args[] = {tmp_args_element_value_16, tmp_args_element_value_19, tmp_args_element_value_20};
                    tmp_list_element_1 = CALL_FUNCTION_WITH_ARGS3(tstate, tmp_called_value_8, call_args);
                }

                Py_DECREF(tmp_called_value_8);
                Py_DECREF(tmp_args_element_value_16);
                if (tmp_list_element_1 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                    exception_lineno = 37;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                PyList_SET_ITEM(tmp_dictset_value, 3, tmp_list_element_1);
                tmp_called_value_10 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[23]);

                if (tmp_called_value_10 == NULL) {
                    if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                        tmp_called_value_10 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$EmStrongItem(tstate);
                        if (unlikely(tmp_called_value_10 == NULL)) {
                            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[23]);
                        }

                        if (tmp_called_value_10 == NULL) {
                            assert(HAS_EXCEPTION_STATE(&exception_state));



                            exception_lineno = 38;
                            type_description_2 = "o";
                            goto list_build_exception_1;
                        }
                        Py_INCREF(tmp_called_value_10);
                    } else {
                        FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                        goto list_build_exception_1;
                    }
                }

                tmp_expression_value_19 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[26]);

                if (tmp_expression_value_19 == NULL) {
                    if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                        tmp_expression_value_19 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$re(tstate);
                        if (unlikely(tmp_expression_value_19 == NULL)) {
                            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[26]);
                        }

                        if (tmp_expression_value_19 == NULL) {
                            assert(HAS_EXCEPTION_STATE(&exception_state));

                            Py_DECREF(tmp_called_value_10);

                            exception_lineno = 38;
                            type_description_2 = "o";
                            goto list_build_exception_1;
                        }
                        Py_INCREF(tmp_expression_value_19);
                    } else {
                        FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                        goto list_build_exception_1;
                    }
                }

                tmp_called_value_11 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_19, mod_consts[42]);
                Py_DECREF(tmp_expression_value_19);
                if (tmp_called_value_11 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    Py_DECREF(tmp_called_value_10);

                    exception_lineno = 38;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                tmp_args_element_value_22 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[28]);

                if (tmp_args_element_value_22 == NULL) {
                    if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                        tmp_args_element_value_22 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$EMPHASIS_RE(tstate);
                        if (unlikely(tmp_args_element_value_22 == NULL)) {
                            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[28]);
                        }

                        if (tmp_args_element_value_22 == NULL) {
                            assert(HAS_EXCEPTION_STATE(&exception_state));

                            Py_DECREF(tmp_called_value_10);
                            Py_DECREF(tmp_called_value_11);

                            exception_lineno = 38;
                            type_description_2 = "o";
                            goto list_build_exception_1;
                        }
                        Py_INCREF(tmp_args_element_value_22);
                    } else {
                        FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                        goto list_build_exception_1;
                    }
                }

                tmp_expression_value_20 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[26]);

                if (tmp_expression_value_20 == NULL) {
                    if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                        tmp_expression_value_20 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$re(tstate);
                        if (unlikely(tmp_expression_value_20 == NULL)) {
                            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[26]);
                        }

                        if (tmp_expression_value_20 == NULL) {
                            assert(HAS_EXCEPTION_STATE(&exception_state));

                            Py_DECREF(tmp_called_value_10);
                            Py_DECREF(tmp_called_value_11);
                            Py_DECREF(tmp_args_element_value_22);

                            exception_lineno = 38;
                            type_description_2 = "o";
                            goto list_build_exception_1;
                        }
                        Py_INCREF(tmp_expression_value_20);
                    } else {
                        FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                        goto list_build_exception_1;
                    }
                }

                tmp_bitor_expr_left_5 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_20, mod_consts[43]);
                Py_DECREF(tmp_expression_value_20);
                if (tmp_bitor_expr_left_5 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    Py_DECREF(tmp_called_value_10);
                    Py_DECREF(tmp_called_value_11);
                    Py_DECREF(tmp_args_element_value_22);

                    exception_lineno = 38;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                tmp_expression_value_21 = PyObject_GetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[26]);

                if (tmp_expression_value_21 == NULL) {
                    if (CHECK_AND_CLEAR_KEY_ERROR_OCCURRED(tstate)) {
                        tmp_expression_value_21 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$re(tstate);
                        if (unlikely(tmp_expression_value_21 == NULL)) {
                            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[26]);
                        }

                        if (tmp_expression_value_21 == NULL) {
                            assert(HAS_EXCEPTION_STATE(&exception_state));

                            Py_DECREF(tmp_called_value_10);
                            Py_DECREF(tmp_called_value_11);
                            Py_DECREF(tmp_args_element_value_22);
                            Py_DECREF(tmp_bitor_expr_left_5);

                            exception_lineno = 38;
                            type_description_2 = "o";
                            goto list_build_exception_1;
                        }
                        Py_INCREF(tmp_expression_value_21);
                    } else {
                        FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                        goto list_build_exception_1;
                    }
                }

                tmp_bitor_expr_right_5 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_21, mod_consts[44]);
                Py_DECREF(tmp_expression_value_21);
                if (tmp_bitor_expr_right_5 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    Py_DECREF(tmp_called_value_10);
                    Py_DECREF(tmp_called_value_11);
                    Py_DECREF(tmp_args_element_value_22);
                    Py_DECREF(tmp_bitor_expr_left_5);

                    exception_lineno = 38;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                tmp_args_element_value_23 = BINARY_OPERATION_BITOR_OBJECT_OBJECT_OBJECT(tmp_bitor_expr_left_5, tmp_bitor_expr_right_5);
                Py_DECREF(tmp_bitor_expr_left_5);
                Py_DECREF(tmp_bitor_expr_right_5);
                if (tmp_args_element_value_23 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    Py_DECREF(tmp_called_value_10);
                    Py_DECREF(tmp_called_value_11);
                    Py_DECREF(tmp_args_element_value_22);

                    exception_lineno = 38;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_2->m_frame.f_lineno = 38;
                {
                    PyObject *call_args[] = {tmp_args_element_value_22, tmp_args_element_value_23};
                    tmp_args_element_value_21 = CALL_FUNCTION_WITH_ARGS2(tstate, tmp_called_value_11, call_args);
                }

                Py_DECREF(tmp_called_value_11);
                Py_DECREF(tmp_args_element_value_22);
                Py_DECREF(tmp_args_element_value_23);
                if (tmp_args_element_value_21 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
                    Py_DECREF(tmp_called_value_10);

                    exception_lineno = 38;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                tmp_args_element_value_24 = mod_consts[49];
                tmp_args_element_value_25 = mod_consts[51];
                frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_2->m_frame.f_lineno = 38;
                {
                    PyObject *call_args[] = {tmp_args_element_value_21, tmp_args_element_value_24, tmp_args_element_value_25};
                    tmp_list_element_1 = CALL_FUNCTION_WITH_ARGS3(tstate, tmp_called_value_10, call_args);
                }

                Py_DECREF(tmp_called_value_10);
                Py_DECREF(tmp_args_element_value_21);
                if (tmp_list_element_1 == NULL) {
                    assert(HAS_ERROR_OCCURRED(tstate));

                    FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                    exception_lineno = 38;
                    type_description_2 = "o";
                    goto list_build_exception_1;
                }
                PyList_SET_ITEM(tmp_dictset_value, 4, tmp_list_element_1);
            }
            goto list_build_noexception_1;
            // Exception handling pass through code for list_build:
            list_build_exception_1:;
            Py_DECREF(tmp_dictset_value);
            goto frame_exception_exit_2;
            // Finished with no exception for list_build:
            list_build_noexception_1:;
            tmp_res = PyObject_SetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[52], tmp_dictset_value);
            Py_DECREF(tmp_dictset_value);
            if (tmp_res != 0) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 33;
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
                exception_tb = MAKE_TRACEBACK(frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_2, exception_lineno);
                SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
            } else if (exception_tb->tb_frame != &frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_2->m_frame) {
                exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_2, exception_lineno);
                SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
            }
        }

        // Attaches locals to frame if any.
        Nuitka_Frame_AttachLocals(
            frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_2,
            type_description_2,
            outline_0_var___class__
        );



        assertFrameObject(frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_2);

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


                exception_lineno = 30;

                goto try_except_handler_4;
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
        tmp_res = PyObject_SetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30, mod_consts[53], tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 30;

            goto try_except_handler_4;
        }
        branch_no_3:;
        {
            PyObject *tmp_assign_source_22;
            PyObject *tmp_called_value_12;
            PyObject *tmp_args_value_2;
            PyObject *tmp_tuple_element_4;
            PyObject *tmp_kwargs_value_2;
            CHECK_OBJECT(tmp_class_creation_1__metaclass);
            tmp_called_value_12 = tmp_class_creation_1__metaclass;
            tmp_tuple_element_4 = mod_consts[2];
            tmp_args_value_2 = MAKE_TUPLE_EMPTY(tstate, 3);
            PyTuple_SET_ITEM0(tmp_args_value_2, 0, tmp_tuple_element_4);
            CHECK_OBJECT(tmp_class_creation_1__bases);
            tmp_tuple_element_4 = tmp_class_creation_1__bases;
            PyTuple_SET_ITEM0(tmp_args_value_2, 1, tmp_tuple_element_4);
            tmp_tuple_element_4 = locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30;
            PyTuple_SET_ITEM0(tmp_args_value_2, 2, tmp_tuple_element_4);
            CHECK_OBJECT(tmp_class_creation_1__class_decl_dict);
            tmp_kwargs_value_2 = tmp_class_creation_1__class_decl_dict;
            frame_frame_markdown$extensions$legacy_em->m_frame.f_lineno = 30;
            tmp_assign_source_22 = CALL_FUNCTION(tstate, tmp_called_value_12, tmp_args_value_2, tmp_kwargs_value_2);
            Py_DECREF(tmp_args_value_2);
            if (tmp_assign_source_22 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 30;

                goto try_except_handler_4;
            }
            assert(outline_0_var___class__ == NULL);
            outline_0_var___class__ = tmp_assign_source_22;
        }
        CHECK_OBJECT(outline_0_var___class__);
        tmp_assign_source_21 = outline_0_var___class__;
        Py_INCREF(tmp_assign_source_21);
        goto try_return_handler_4;
        NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
        return NULL;
        // Return handler code:
        try_return_handler_4:;
        Py_DECREF(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30);
        locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30 = NULL;
        goto try_return_handler_3;
        // Exception handler code:
        try_except_handler_4:;
        exception_keeper_lineno_2 = exception_lineno;
        exception_lineno = 0;
        exception_keeper_name_2 = exception_state;
        INIT_ERROR_OCCURRED_STATE(&exception_state);

        Py_DECREF(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30);
        locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__1_LegacyUnderscoreProcessor_30 = NULL;
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
        exception_lineno = 30;
        goto try_except_handler_2;
        outline_result_1:;
        UPDATE_STRING_DICT1(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[2], tmp_assign_source_21);
    }
    goto try_end_2;
    // Exception handler code:
    try_except_handler_2:;
    exception_keeper_lineno_4 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_4 = exception_state;
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
    exception_state = exception_keeper_name_4;
    exception_lineno = exception_keeper_lineno_4;

    goto frame_exception_exit_1;
    // End of try:
    try_end_2:;
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
    // Tried code:
    {
        PyObject *tmp_assign_source_23;
        PyObject *tmp_tuple_element_5;
        tmp_tuple_element_5 = module_var_accessor_markdown$$36$extensions$$36$legacy_em$Extension(tstate);
        if (unlikely(tmp_tuple_element_5 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[18]);
        }

        if (tmp_tuple_element_5 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 42;

            goto try_except_handler_5;
        }
        tmp_assign_source_23 = MAKE_TUPLE_EMPTY(tstate, 1);
        PyTuple_SET_ITEM0(tmp_assign_source_23, 0, tmp_tuple_element_5);
        assert(tmp_class_creation_2__bases_orig == NULL);
        tmp_class_creation_2__bases_orig = tmp_assign_source_23;
    }
    {
        PyObject *tmp_assign_source_24;
        PyObject *tmp_direct_call_arg1_2;
        CHECK_OBJECT(tmp_class_creation_2__bases_orig);
        tmp_direct_call_arg1_2 = tmp_class_creation_2__bases_orig;
        Py_INCREF(tmp_direct_call_arg1_2);

        {
            PyObject *dir_call_args[] = {tmp_direct_call_arg1_2};
            tmp_assign_source_24 = impl___main__$$36$$$36$$$36$helper_function__mro_entries_conversion(tstate, dir_call_args);
        }
        if (tmp_assign_source_24 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 42;

            goto try_except_handler_5;
        }
        assert(tmp_class_creation_2__bases == NULL);
        tmp_class_creation_2__bases = tmp_assign_source_24;
    }
    {
        PyObject *tmp_assign_source_25;
        tmp_assign_source_25 = MAKE_DICT_EMPTY(tstate);
        assert(tmp_class_creation_2__class_decl_dict == NULL);
        tmp_class_creation_2__class_decl_dict = tmp_assign_source_25;
    }
    {
        PyObject *tmp_assign_source_26;
        PyObject *tmp_metaclass_value_2;
        nuitka_bool tmp_condition_result_5;
        int tmp_truth_name_2;
        PyObject *tmp_type_arg_3;
        PyObject *tmp_expression_value_22;
        PyObject *tmp_subscript_value_2;
        PyObject *tmp_bases_value_2;
        CHECK_OBJECT(tmp_class_creation_2__bases);
        tmp_truth_name_2 = CHECK_IF_TRUE(tmp_class_creation_2__bases);
        if (tmp_truth_name_2 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 42;

            goto try_except_handler_5;
        }
        tmp_condition_result_5 = tmp_truth_name_2 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        if (tmp_condition_result_5 == NUITKA_BOOL_TRUE) {
            goto condexpr_true_2;
        } else {
            goto condexpr_false_2;
        }
        condexpr_true_2:;
        CHECK_OBJECT(tmp_class_creation_2__bases);
        tmp_expression_value_22 = tmp_class_creation_2__bases;
        tmp_subscript_value_2 = const_int_0;
        tmp_type_arg_3 = LOOKUP_SUBSCRIPT_CONST(tstate, tmp_expression_value_22, tmp_subscript_value_2, 0);
        if (tmp_type_arg_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 42;

            goto try_except_handler_5;
        }
        tmp_metaclass_value_2 = BUILTIN_TYPE1(tmp_type_arg_3);
        Py_DECREF(tmp_type_arg_3);
        if (tmp_metaclass_value_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 42;

            goto try_except_handler_5;
        }
        goto condexpr_end_2;
        condexpr_false_2:;
        tmp_metaclass_value_2 = (PyObject *)&PyType_Type;
        Py_INCREF(tmp_metaclass_value_2);
        condexpr_end_2:;
        CHECK_OBJECT(tmp_class_creation_2__bases);
        tmp_bases_value_2 = tmp_class_creation_2__bases;
        tmp_assign_source_26 = SELECT_METACLASS(tstate, tmp_metaclass_value_2, tmp_bases_value_2);
        Py_DECREF(tmp_metaclass_value_2);
        if (tmp_assign_source_26 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 42;

            goto try_except_handler_5;
        }
        assert(tmp_class_creation_2__metaclass == NULL);
        tmp_class_creation_2__metaclass = tmp_assign_source_26;
    }
    {
        bool tmp_condition_result_6;
        PyObject *tmp_expression_value_23;
        CHECK_OBJECT(tmp_class_creation_2__metaclass);
        tmp_expression_value_23 = tmp_class_creation_2__metaclass;
        tmp_res = HAS_ATTR_BOOL2(tstate, tmp_expression_value_23, mod_consts[33]);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 42;

            goto try_except_handler_5;
        }
        tmp_condition_result_6 = (tmp_res != 0) ? true : false;
        if (tmp_condition_result_6 != false) {
            goto branch_yes_4;
        } else {
            goto branch_no_4;
        }
    }
    branch_yes_4:;
    {
        PyObject *tmp_assign_source_27;
        PyObject *tmp_called_value_13;
        PyObject *tmp_expression_value_24;
        PyObject *tmp_args_value_3;
        PyObject *tmp_tuple_element_6;
        PyObject *tmp_kwargs_value_3;
        CHECK_OBJECT(tmp_class_creation_2__metaclass);
        tmp_expression_value_24 = tmp_class_creation_2__metaclass;
        tmp_called_value_13 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_24, mod_consts[33]);
        if (tmp_called_value_13 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 42;

            goto try_except_handler_5;
        }
        tmp_tuple_element_6 = mod_consts[7];
        tmp_args_value_3 = MAKE_TUPLE_EMPTY(tstate, 2);
        PyTuple_SET_ITEM0(tmp_args_value_3, 0, tmp_tuple_element_6);
        CHECK_OBJECT(tmp_class_creation_2__bases);
        tmp_tuple_element_6 = tmp_class_creation_2__bases;
        PyTuple_SET_ITEM0(tmp_args_value_3, 1, tmp_tuple_element_6);
        CHECK_OBJECT(tmp_class_creation_2__class_decl_dict);
        tmp_kwargs_value_3 = tmp_class_creation_2__class_decl_dict;
        frame_frame_markdown$extensions$legacy_em->m_frame.f_lineno = 42;
        tmp_assign_source_27 = CALL_FUNCTION(tstate, tmp_called_value_13, tmp_args_value_3, tmp_kwargs_value_3);
        Py_DECREF(tmp_called_value_13);
        Py_DECREF(tmp_args_value_3);
        if (tmp_assign_source_27 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 42;

            goto try_except_handler_5;
        }
        assert(tmp_class_creation_2__prepared == NULL);
        tmp_class_creation_2__prepared = tmp_assign_source_27;
    }
    {
        bool tmp_condition_result_7;
        PyObject *tmp_operand_value_2;
        PyObject *tmp_expression_value_25;
        CHECK_OBJECT(tmp_class_creation_2__prepared);
        tmp_expression_value_25 = tmp_class_creation_2__prepared;
        tmp_res = HAS_ATTR_BOOL2(tstate, tmp_expression_value_25, mod_consts[34]);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 42;

            goto try_except_handler_5;
        }
        tmp_operand_value_2 = (tmp_res != 0) ? Py_True : Py_False;
        tmp_res = CHECK_IF_TRUE(tmp_operand_value_2);
        assert(!(tmp_res == -1));
        tmp_condition_result_7 = (tmp_res == 0) ? true : false;
        if (tmp_condition_result_7 != false) {
            goto branch_yes_5;
        } else {
            goto branch_no_5;
        }
    }
    branch_yes_5:;
    {
        PyObject *tmp_raise_type_2;
        PyObject *tmp_make_exception_arg_2;
        PyObject *tmp_mod_expr_left_2;
        PyObject *tmp_mod_expr_right_2;
        PyObject *tmp_tuple_element_7;
        PyObject *tmp_expression_value_26;
        PyObject *tmp_name_value_5;
        PyObject *tmp_default_value_2;
        tmp_mod_expr_left_2 = mod_consts[35];
        CHECK_OBJECT(tmp_class_creation_2__metaclass);
        tmp_expression_value_26 = tmp_class_creation_2__metaclass;
        tmp_name_value_5 = mod_consts[36];
        tmp_default_value_2 = mod_consts[37];
        tmp_tuple_element_7 = BUILTIN_GETATTR(tstate, tmp_expression_value_26, tmp_name_value_5, tmp_default_value_2);
        if (tmp_tuple_element_7 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 42;

            goto try_except_handler_5;
        }
        tmp_mod_expr_right_2 = MAKE_TUPLE_EMPTY(tstate, 2);
        {
            PyObject *tmp_expression_value_27;
            PyObject *tmp_type_arg_4;
            PyTuple_SET_ITEM(tmp_mod_expr_right_2, 0, tmp_tuple_element_7);
            CHECK_OBJECT(tmp_class_creation_2__prepared);
            tmp_type_arg_4 = tmp_class_creation_2__prepared;
            tmp_expression_value_27 = BUILTIN_TYPE1(tmp_type_arg_4);
            assert(!(tmp_expression_value_27 == NULL));
            tmp_tuple_element_7 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_27, mod_consts[36]);
            Py_DECREF(tmp_expression_value_27);
            if (tmp_tuple_element_7 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 42;

                goto tuple_build_exception_2;
            }
            PyTuple_SET_ITEM(tmp_mod_expr_right_2, 1, tmp_tuple_element_7);
        }
        goto tuple_build_noexception_2;
        // Exception handling pass through code for tuple_build:
        tuple_build_exception_2:;
        Py_DECREF(tmp_mod_expr_right_2);
        goto try_except_handler_5;
        // Finished with no exception for tuple_build:
        tuple_build_noexception_2:;
        tmp_make_exception_arg_2 = BINARY_OPERATION_MOD_OBJECT_UNICODE_TUPLE(tmp_mod_expr_left_2, tmp_mod_expr_right_2);
        Py_DECREF(tmp_mod_expr_right_2);
        if (tmp_make_exception_arg_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 42;

            goto try_except_handler_5;
        }
        frame_frame_markdown$extensions$legacy_em->m_frame.f_lineno = 42;
        tmp_raise_type_2 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_TypeError, tmp_make_exception_arg_2);
        Py_DECREF(tmp_make_exception_arg_2);
        assert(!(tmp_raise_type_2 == NULL));
        exception_state.exception_type = tmp_raise_type_2;
        exception_lineno = 42;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);

        goto try_except_handler_5;
    }
    branch_no_5:;
    goto branch_end_4;
    branch_no_4:;
    {
        PyObject *tmp_assign_source_28;
        tmp_assign_source_28 = MAKE_DICT_EMPTY(tstate);
        assert(tmp_class_creation_2__prepared == NULL);
        tmp_class_creation_2__prepared = tmp_assign_source_28;
    }
    branch_end_4:;
    {
        PyObject *tmp_assign_source_29;
        {
            PyObject *tmp_set_locals_2;
            CHECK_OBJECT(tmp_class_creation_2__prepared);
            tmp_set_locals_2 = tmp_class_creation_2__prepared;
            locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__2_LegacyEmExtension_42 = tmp_set_locals_2;
            Py_INCREF(tmp_set_locals_2);
        }
        // Tried code:
        // Tried code:
        tmp_dictset_value = mod_consts[38];
        tmp_res = PyObject_SetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__2_LegacyEmExtension_42, mod_consts[39], tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 42;

            goto try_except_handler_7;
        }
        tmp_dictset_value = mod_consts[54];
        tmp_res = PyObject_SetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__2_LegacyEmExtension_42, mod_consts[10], tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 42;

            goto try_except_handler_7;
        }
        tmp_dictset_value = mod_consts[7];
        tmp_res = PyObject_SetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__2_LegacyEmExtension_42, mod_consts[41], tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 42;

            goto try_except_handler_7;
        }
        frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__2_LegacyEmExtension_3 = MAKE_CLASS_FRAME(tstate, code_objects_5342babc2c70b3a0aee8bb1999e29dd9, module_markdown$extensions$legacy_em, NULL, sizeof(void *));

        // Push the new frame as the currently active one, and we should be exclusively
        // owning it.
        pushFrameStackCompiledFrame(tstate, frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__2_LegacyEmExtension_3);
        assert(Py_REFCNT(frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__2_LegacyEmExtension_3) == 2);

        // Framed code:


        tmp_dictset_value = MAKE_FUNCTION_markdown$extensions$legacy_em$$36$$$36$$$36$function__1_extendMarkdown(tstate);

        tmp_res = PyObject_SetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__2_LegacyEmExtension_42, mod_consts[55], tmp_dictset_value);
        Py_DECREF(tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 45;
            type_description_2 = "o";
            goto frame_exception_exit_3;
        }


        // Put the previous frame back on top.
        popFrameStack(tstate);

        goto frame_no_exception_2;
        frame_exception_exit_3:


        {
            PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
            if (exception_tb == NULL) {
                exception_tb = MAKE_TRACEBACK(frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__2_LegacyEmExtension_3, exception_lineno);
                SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
            } else if (exception_tb->tb_frame != &frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__2_LegacyEmExtension_3->m_frame) {
                exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__2_LegacyEmExtension_3, exception_lineno);
                SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
            }
        }

        // Attaches locals to frame if any.
        Nuitka_Frame_AttachLocals(
            frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__2_LegacyEmExtension_3,
            type_description_2,
            outline_1_var___class__
        );



        assertFrameObject(frame_frame_markdown$extensions$legacy_em$$36$$$36$$$36$class__2_LegacyEmExtension_3);

        // Put the previous frame back on top.
        popFrameStack(tstate);

        // Return the error.
        goto nested_frame_exit_2;
        frame_no_exception_2:;
        goto skip_nested_handling_2;
        nested_frame_exit_2:;

        goto try_except_handler_7;
        skip_nested_handling_2:;
        {
            nuitka_bool tmp_condition_result_8;
            PyObject *tmp_cmp_expr_left_2;
            PyObject *tmp_cmp_expr_right_2;
            CHECK_OBJECT(tmp_class_creation_2__bases);
            tmp_cmp_expr_left_2 = tmp_class_creation_2__bases;
            CHECK_OBJECT(tmp_class_creation_2__bases_orig);
            tmp_cmp_expr_right_2 = tmp_class_creation_2__bases_orig;
            tmp_condition_result_8 = RICH_COMPARE_NE_NBOOL_OBJECT_TUPLE(tmp_cmp_expr_left_2, tmp_cmp_expr_right_2);
            if (tmp_condition_result_8 == NUITKA_BOOL_EXCEPTION) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 42;

                goto try_except_handler_7;
            }
            if (tmp_condition_result_8 == NUITKA_BOOL_TRUE) {
                goto branch_yes_6;
            } else {
                goto branch_no_6;
            }
        }
        branch_yes_6:;
        CHECK_OBJECT(tmp_class_creation_2__bases_orig);
        tmp_dictset_value = tmp_class_creation_2__bases_orig;
        tmp_res = PyObject_SetItem(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__2_LegacyEmExtension_42, mod_consts[53], tmp_dictset_value);
        if (tmp_res != 0) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 42;

            goto try_except_handler_7;
        }
        branch_no_6:;
        {
            PyObject *tmp_assign_source_30;
            PyObject *tmp_called_value_14;
            PyObject *tmp_args_value_4;
            PyObject *tmp_tuple_element_8;
            PyObject *tmp_kwargs_value_4;
            CHECK_OBJECT(tmp_class_creation_2__metaclass);
            tmp_called_value_14 = tmp_class_creation_2__metaclass;
            tmp_tuple_element_8 = mod_consts[7];
            tmp_args_value_4 = MAKE_TUPLE_EMPTY(tstate, 3);
            PyTuple_SET_ITEM0(tmp_args_value_4, 0, tmp_tuple_element_8);
            CHECK_OBJECT(tmp_class_creation_2__bases);
            tmp_tuple_element_8 = tmp_class_creation_2__bases;
            PyTuple_SET_ITEM0(tmp_args_value_4, 1, tmp_tuple_element_8);
            tmp_tuple_element_8 = locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__2_LegacyEmExtension_42;
            PyTuple_SET_ITEM0(tmp_args_value_4, 2, tmp_tuple_element_8);
            CHECK_OBJECT(tmp_class_creation_2__class_decl_dict);
            tmp_kwargs_value_4 = tmp_class_creation_2__class_decl_dict;
            frame_frame_markdown$extensions$legacy_em->m_frame.f_lineno = 42;
            tmp_assign_source_30 = CALL_FUNCTION(tstate, tmp_called_value_14, tmp_args_value_4, tmp_kwargs_value_4);
            Py_DECREF(tmp_args_value_4);
            if (tmp_assign_source_30 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 42;

                goto try_except_handler_7;
            }
            assert(outline_1_var___class__ == NULL);
            outline_1_var___class__ = tmp_assign_source_30;
        }
        CHECK_OBJECT(outline_1_var___class__);
        tmp_assign_source_29 = outline_1_var___class__;
        Py_INCREF(tmp_assign_source_29);
        goto try_return_handler_7;
        NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
        return NULL;
        // Return handler code:
        try_return_handler_7:;
        Py_DECREF(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__2_LegacyEmExtension_42);
        locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__2_LegacyEmExtension_42 = NULL;
        goto try_return_handler_6;
        // Exception handler code:
        try_except_handler_7:;
        exception_keeper_lineno_5 = exception_lineno;
        exception_lineno = 0;
        exception_keeper_name_5 = exception_state;
        INIT_ERROR_OCCURRED_STATE(&exception_state);

        Py_DECREF(locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__2_LegacyEmExtension_42);
        locals_markdown$extensions$legacy_em$$36$$$36$$$36$class__2_LegacyEmExtension_42 = NULL;
        // Re-raise.
        exception_state = exception_keeper_name_5;
        exception_lineno = exception_keeper_lineno_5;

        goto try_except_handler_6;
        // End of try:
        NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
        return NULL;
        // Return handler code:
        try_return_handler_6:;
        CHECK_OBJECT(outline_1_var___class__);
        Py_DECREF(outline_1_var___class__);
        outline_1_var___class__ = NULL;
        goto outline_result_2;
        // Exception handler code:
        try_except_handler_6:;
        exception_keeper_lineno_6 = exception_lineno;
        exception_lineno = 0;
        exception_keeper_name_6 = exception_state;
        INIT_ERROR_OCCURRED_STATE(&exception_state);

        // Re-raise.
        exception_state = exception_keeper_name_6;
        exception_lineno = exception_keeper_lineno_6;

        goto outline_exception_2;
        // End of try:
        NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
        return NULL;
        outline_exception_2:;
        exception_lineno = 42;
        goto try_except_handler_5;
        outline_result_2:;
        UPDATE_STRING_DICT1(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[7], tmp_assign_source_29);
    }
    goto try_end_3;
    // Exception handler code:
    try_except_handler_5:;
    exception_keeper_lineno_7 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_7 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    Py_XDECREF(tmp_class_creation_2__bases_orig);
    tmp_class_creation_2__bases_orig = NULL;
    Py_XDECREF(tmp_class_creation_2__bases);
    tmp_class_creation_2__bases = NULL;
    Py_XDECREF(tmp_class_creation_2__class_decl_dict);
    tmp_class_creation_2__class_decl_dict = NULL;
    Py_XDECREF(tmp_class_creation_2__metaclass);
    tmp_class_creation_2__metaclass = NULL;
    Py_XDECREF(tmp_class_creation_2__prepared);
    tmp_class_creation_2__prepared = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_7;
    exception_lineno = exception_keeper_lineno_7;

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
            exception_tb = MAKE_TRACEBACK(frame_frame_markdown$extensions$legacy_em, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_markdown$extensions$legacy_em->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_markdown$extensions$legacy_em, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }



    assertFrameObject(frame_frame_markdown$extensions$legacy_em);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto module_exception_exit;
    frame_no_exception_3:;
    CHECK_OBJECT(tmp_class_creation_2__bases_orig);
    Py_DECREF(tmp_class_creation_2__bases_orig);
    tmp_class_creation_2__bases_orig = NULL;
    CHECK_OBJECT(tmp_class_creation_2__bases);
    Py_DECREF(tmp_class_creation_2__bases);
    tmp_class_creation_2__bases = NULL;
    CHECK_OBJECT(tmp_class_creation_2__class_decl_dict);
    Py_DECREF(tmp_class_creation_2__class_decl_dict);
    tmp_class_creation_2__class_decl_dict = NULL;
    CHECK_OBJECT(tmp_class_creation_2__metaclass);
    Py_DECREF(tmp_class_creation_2__metaclass);
    tmp_class_creation_2__metaclass = NULL;
    CHECK_OBJECT(tmp_class_creation_2__prepared);
    Py_DECREF(tmp_class_creation_2__prepared);
    tmp_class_creation_2__prepared = NULL;
    {
        PyObject *tmp_assign_source_31;


        tmp_assign_source_31 = MAKE_FUNCTION_markdown$extensions$legacy_em$$36$$$36$$$36$function__2_makeExtension(tstate);

        UPDATE_STRING_DICT1(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)mod_consts[57], tmp_assign_source_31);
    }

    // Report to PGO about leaving the module without error.
    PGO_onModuleExit("markdown$extensions$legacy_em", false);

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *post_load = IMPORT_EMBEDDED_MODULE(tstate, "markdown.extensions.legacy_em" "-postLoad");
        if (post_load == NULL) {
            return NULL;
        }
    }
#endif

    Py_INCREF(module_markdown$extensions$legacy_em);
    return module_markdown$extensions$legacy_em;
    module_exception_exit:

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_markdown$extensions$legacy_em, (Nuitka_StringObject *)const_str_plain___name__);

        if (module_name != NULL) {
            Nuitka_DelModule(tstate, module_name);
        }
    }
#endif
    PGO_onModuleExit("markdown$extensions$legacy_em", false);

    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);
    return NULL;
}
