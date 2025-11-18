/* Generated code for Python module 'oauthlib$oauth1$rfc5849$utils'
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

/* The "module_oauthlib$oauth1$rfc5849$utils" is a Python object pointer of module type.
 *
 * Note: For full compatibility with CPython, every module variable access
 * needs to go through it except for cases where the module cannot possibly
 * have changed in the mean time.
 */

PyObject *module_oauthlib$oauth1$rfc5849$utils;
PyDictObject *moduledict_oauthlib$oauth1$rfc5849$utils;

/* The declarations of module constants used, if any. */
static PyObject *mod_consts[58];
#ifndef __NUITKA_NO_ASSERT__
static Py_hash_t mod_consts_hash[58];
#endif

static PyObject *module_filename_obj = NULL;

/* Indicator if this modules private constants were created yet. */
static bool constants_created = false;

/* Function to create module private constants. */
static void createModuleConstants(PyThreadState *tstate) {
    if (constants_created == false) {
        loadConstantsBlob(tstate, &mod_consts[0], UN_TRANSLATE("oauthlib.oauth1.rfc5849.utils"));
        constants_created = true;

#ifndef __NUITKA_NO_ASSERT__
        for (int i = 0; i < 58; i++) {
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
void checkModuleConstants_oauthlib$oauth1$rfc5849$utils(PyThreadState *tstate) {
    // The module may not have been used at all, then ignore this.
    if (constants_created == false) return;

    for (int i = 0; i < 58; i++) {
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
static PyObject *module_var_accessor_oauthlib$$36$oauth1$$36$rfc5849$$36$utils$__spec__(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_oauthlib$oauth1$rfc5849$utils->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_oauthlib$oauth1$rfc5849$utils->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[57]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_oauthlib$oauth1$rfc5849$utils->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[57]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[57], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[57]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[57], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[57]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[57]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[57]);
    }

    return result;
}

static PyObject *module_var_accessor_oauthlib$$36$oauth1$$36$rfc5849$$36$utils$filter_oauth_params(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_oauthlib$oauth1$rfc5849$utils->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_oauthlib$oauth1$rfc5849$utils->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[4]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_oauthlib$oauth1$rfc5849$utils->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[4]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[4], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[4]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[4], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[4]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[4]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[4]);
    }

    return result;
}

static PyObject *module_var_accessor_oauthlib$$36$oauth1$$36$rfc5849$$36$utils$parse_http_list(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_oauthlib$oauth1$rfc5849$utils->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_oauthlib$oauth1$rfc5849$utils->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[22]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_oauthlib$oauth1$rfc5849$utils->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[22]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[22]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[22]);
    }

    return result;
}

static PyObject *module_var_accessor_oauthlib$$36$oauth1$$36$rfc5849$$36$utils$parse_keqv_list(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_oauthlib$oauth1$rfc5849$utils->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_oauthlib$oauth1$rfc5849$utils->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[20]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_oauthlib$oauth1$rfc5849$utils->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[20]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[20]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[20]);
    }

    return result;
}

static PyObject *module_var_accessor_oauthlib$$36$oauth1$$36$rfc5849$$36$utils$quote(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_oauthlib$oauth1$rfc5849$utils->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_oauthlib$oauth1$rfc5849$utils->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[14]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_oauthlib$oauth1$rfc5849$utils->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[14]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[14]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[14]);
    }

    return result;
}

static PyObject *module_var_accessor_oauthlib$$36$oauth1$$36$rfc5849$$36$utils$unquote(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_oauthlib$oauth1$rfc5849$utils->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_oauthlib$oauth1$rfc5849$utils->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[18]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_oauthlib$oauth1$rfc5849$utils->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[18]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[18]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[18]);
    }

    return result;
}

static PyObject *module_var_accessor_oauthlib$$36$oauth1$$36$rfc5849$$36$utils$urllib2(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_oauthlib$oauth1$rfc5849$utils->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_oauthlib$oauth1$rfc5849$utils->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[19]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_oauthlib$oauth1$rfc5849$utils->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[19]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[19], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[19]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[19], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[19]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[19]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[19]);
    }

    return result;
}


#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
// The module code objects.
static PyCodeObject *code_objects_84ce88d53e34eefbbcd8eb6fe36f44eb;
static PyCodeObject *code_objects_0dbb49b86a3755c06d7a5fd9a741d332;
static PyCodeObject *code_objects_8209180ee940e61f59f6370a2913482d;
static PyCodeObject *code_objects_88106b63226aba3175e5f08001b84ae6;
static PyCodeObject *code_objects_6b7f0d6a33c825b15a2567335d2b1008;
static PyCodeObject *code_objects_3992bd78681b53edd831c9dbef734113;
static PyCodeObject *code_objects_147d7551bd2088674562b2b974da28c5;
static PyCodeObject *code_objects_72d18a6d338f28658fc75543bd9e40cb;
static PyCodeObject *code_objects_2c3a793824c5a61aca6f5852fee270f4;
static PyCodeObject *code_objects_d1755dfe63e23a4e710f43abccbe2c78;

static void createModuleCodeObjects(void) {
    module_filename_obj = MAKE_RELATIVE_PATH(mod_consts[46]); CHECK_OBJECT(module_filename_obj);
    code_objects_84ce88d53e34eefbbcd8eb6fe36f44eb = MAKE_CODE_OBJECT(module_filename_obj, 1, CO_NOFREE, mod_consts[47], mod_consts[47], NULL, NULL, 0, 0, 0);
    code_objects_0dbb49b86a3755c06d7a5fd9a741d332 = MAKE_CODE_OBJECT(module_filename_obj, 41, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[43], mod_consts[43], mod_consts[48], NULL, 1, 0, 0);
    code_objects_8209180ee940e61f59f6370a2913482d = MAKE_CODE_OBJECT(module_filename_obj, 31, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[4], mod_consts[4], mod_consts[49], NULL, 1, 0, 0);
    code_objects_88106b63226aba3175e5f08001b84ae6 = MAKE_CODE_OBJECT(module_filename_obj, 17, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[42], mod_consts[42], mod_consts[50], NULL, 1, 0, 0);
    code_objects_6b7f0d6a33c825b15a2567335d2b1008 = MAKE_CODE_OBJECT(module_filename_obj, 33, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[6], mod_consts[7], mod_consts[51], NULL, 1, 0, 0);
    code_objects_3992bd78681b53edd831c9dbef734113 = MAKE_CODE_OBJECT(module_filename_obj, 75, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[45], mod_consts[45], mod_consts[52], NULL, 1, 0, 0);
    code_objects_147d7551bd2088674562b2b974da28c5 = MAKE_CODE_OBJECT(module_filename_obj, 69, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[22], mod_consts[22], mod_consts[48], NULL, 1, 0, 0);
    code_objects_72d18a6d338f28658fc75543bd9e40cb = MAKE_CODE_OBJECT(module_filename_obj, 63, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[20], mod_consts[20], mod_consts[53], NULL, 1, 0, 0);
    code_objects_2c3a793824c5a61aca6f5852fee270f4 = MAKE_CODE_OBJECT(module_filename_obj, 57, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[44], mod_consts[44], mod_consts[48], NULL, 1, 0, 0);
    code_objects_d1755dfe63e23a4e710f43abccbe2c78 = MAKE_CODE_OBJECT(module_filename_obj, 23, CO_OPTIMIZED | CO_NEWLOCALS | CO_VARARGS | CO_VARKEYWORDS, mod_consts[0], mod_consts[1], mod_consts[54], mod_consts[55], 1, 0, 0);
}
#endif

// The module function declarations.
NUITKA_CROSS_MODULE PyObject *impl___main__$$36$$$36$$$36$helper_function_complex_call_helper_pos_star_list_star_dict(PyThreadState *tstate, PyObject **python_pars);


static PyObject *MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper(PyThreadState *tstate, struct Nuitka_CellObject **closure);


static PyObject *MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header(PyThreadState *tstate);


// The module function definitions.
static PyObject *impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    struct Nuitka_CellObject *par_target = Nuitka_Cell_New1(python_pars[0]);
    PyObject *var_wrapper = NULL;
    struct Nuitka_FrameObject *frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    bool tmp_result;
    static struct Nuitka_FrameObject *cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;

    // Actual function body.
    {
        PyObject *tmp_assign_source_1;
        struct Nuitka_CellObject *tmp_closure_1[1];

        tmp_closure_1[0] = par_target;
        Py_INCREF(tmp_closure_1[0]);

        tmp_assign_source_1 = MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper(tstate, tmp_closure_1);

        assert(var_wrapper == NULL);
        var_wrapper = tmp_assign_source_1;
    }
    // Tried code:
    if (isFrameUnusable(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params)) {
        Py_XDECREF(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params = MAKE_FUNCTION_FRAME(tstate, code_objects_88106b63226aba3175e5f08001b84ae6, module_oauthlib$oauth1$rfc5849$utils, sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params->m_type_description == NULL);
    frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params = cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params);
    assert(Py_REFCNT(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params) == 2);

    // Framed code:
    {
        PyObject *tmp_assattr_value_1;
        PyObject *tmp_expression_value_1;
        PyObject *tmp_assattr_target_1;
        CHECK_OBJECT(Nuitka_Cell_GET(par_target));
        tmp_expression_value_1 = Nuitka_Cell_GET(par_target);
        tmp_assattr_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[2]);
        if (tmp_assattr_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 27;
            type_description_1 = "co";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(var_wrapper);
        tmp_assattr_target_1 = var_wrapper;
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_1, mod_consts[2], tmp_assattr_value_1);
        Py_DECREF(tmp_assattr_value_1);
        if (tmp_result == false) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 27;
            type_description_1 = "co";
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
            exception_tb = MAKE_TRACEBACK(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params,
        type_description_1,
        par_target,
        var_wrapper
    );


    // Release cached frame if used for exception.
    if (frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params == cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params);
        cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params = NULL;
    }

    assertFrameObject(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    CHECK_OBJECT(var_wrapper);
    tmp_return_value = var_wrapper;
    Py_INCREF(tmp_return_value);
    goto try_return_handler_1;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Return handler code:
    try_return_handler_1:;
    CHECK_OBJECT(var_wrapper);
    Py_DECREF(var_wrapper);
    var_wrapper = NULL;
    goto function_return_exit;
    // Exception handler code:
    try_except_handler_1:;
    exception_keeper_lineno_1 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_1 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    CHECK_OBJECT(var_wrapper);
    Py_DECREF(var_wrapper);
    var_wrapper = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_1;
    exception_lineno = exception_keeper_lineno_1;

    goto function_exception_exit;
    // End of try:

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_target);
    Py_DECREF(par_target);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_target);
    Py_DECREF(par_target);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_params = python_pars[0];
    PyObject *par_args = python_pars[1];
    PyObject *par_kwargs = python_pars[2];
    struct Nuitka_FrameObject *frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    PyObject *tmp_return_value = NULL;
    static struct Nuitka_FrameObject *cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;

    // Actual function body.
    // Tried code:
    if (isFrameUnusable(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper)) {
        Py_XDECREF(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper = MAKE_FUNCTION_FRAME(tstate, code_objects_d1755dfe63e23a4e710f43abccbe2c78, module_oauthlib$oauth1$rfc5849$utils, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper->m_type_description == NULL);
    frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper = cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper);
    assert(Py_REFCNT(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper) == 2);

    // Framed code:
    {
        PyObject *tmp_assign_source_1;
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        tmp_called_value_1 = module_var_accessor_oauthlib$$36$oauth1$$36$rfc5849$$36$utils$filter_oauth_params(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[4]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 24;
            type_description_1 = "oooc";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_params);
        tmp_args_element_value_1 = par_params;
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper->m_frame.f_lineno = 24;
        tmp_assign_source_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_1, tmp_args_element_value_1);
        if (tmp_assign_source_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 24;
            type_description_1 = "oooc";
            goto frame_exception_exit_1;
        }
        {
            PyObject *old = par_params;
            assert(old != NULL);
            par_params = tmp_assign_source_1;
            Py_DECREF(old);
        }

    }
    {
        PyObject *tmp_direct_call_arg1_1;
        PyObject *tmp_direct_call_arg2_1;
        PyObject *tmp_tuple_element_1;
        PyObject *tmp_direct_call_arg3_1;
        PyObject *tmp_direct_call_arg4_1;
        if (Nuitka_Cell_GET(self->m_closure[0]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[5]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 25;
            type_description_1 = "oooc";
            goto frame_exception_exit_1;
        }

        tmp_direct_call_arg1_1 = Nuitka_Cell_GET(self->m_closure[0]);
        CHECK_OBJECT(par_params);
        tmp_tuple_element_1 = par_params;
        tmp_direct_call_arg2_1 = MAKE_TUPLE_EMPTY(tstate, 1);
        PyTuple_SET_ITEM0(tmp_direct_call_arg2_1, 0, tmp_tuple_element_1);
        CHECK_OBJECT(par_args);
        tmp_direct_call_arg3_1 = par_args;
        CHECK_OBJECT(par_kwargs);
        tmp_direct_call_arg4_1 = par_kwargs;
        Py_INCREF(tmp_direct_call_arg1_1);
        Py_INCREF(tmp_direct_call_arg3_1);
        Py_INCREF(tmp_direct_call_arg4_1);

        {
            PyObject *dir_call_args[] = {tmp_direct_call_arg1_1, tmp_direct_call_arg2_1, tmp_direct_call_arg3_1, tmp_direct_call_arg4_1};
            tmp_return_value = impl___main__$$36$$$36$$$36$helper_function_complex_call_helper_pos_star_list_star_dict(tstate, dir_call_args);
        }
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 25;
            type_description_1 = "oooc";
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
            exception_tb = MAKE_TRACEBACK(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper,
        type_description_1,
        par_params,
        par_args,
        par_kwargs,
        self->m_closure[0]
    );


    // Release cached frame if used for exception.
    if (frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper == cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper);
        cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper = NULL;
    }

    assertFrameObject(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Return handler code:
    try_return_handler_1:;
    CHECK_OBJECT(par_params);
    Py_DECREF(par_params);
    par_params = NULL;
    goto function_return_exit;
    // Exception handler code:
    try_except_handler_1:;
    exception_keeper_lineno_1 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_1 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    Py_XDECREF(par_params);
    par_params = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_1;
    exception_lineno = exception_keeper_lineno_1;

    goto function_exception_exit;
    // End of try:

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_args);
    Py_DECREF(par_args);
    CHECK_OBJECT(par_kwargs);
    Py_DECREF(par_kwargs);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_args);
    Py_DECREF(par_args);
    CHECK_OBJECT(par_kwargs);
    Py_DECREF(par_kwargs);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_params = python_pars[0];
    PyObject *var_is_oauth = NULL;
    struct Nuitka_FrameObject *frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    int tmp_res;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    PyObject *tmp_return_value = NULL;
    static struct Nuitka_FrameObject *cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;

    // Actual function body.
    {
        PyObject *tmp_assign_source_1;


        tmp_assign_source_1 = MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth(tstate);

        assert(var_is_oauth == NULL);
        var_is_oauth = tmp_assign_source_1;
    }
    // Tried code:
    if (isFrameUnusable(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params)) {
        Py_XDECREF(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params = MAKE_FUNCTION_FRAME(tstate, code_objects_8209180ee940e61f59f6370a2913482d, module_oauthlib$oauth1$rfc5849$utils, sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params->m_type_description == NULL);
    frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params = cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params);
    assert(Py_REFCNT(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params) == 2);

    // Framed code:
    {
        nuitka_bool tmp_condition_result_1;
        PyObject *tmp_isinstance_inst_1;
        PyObject *tmp_isinstance_cls_1;
        CHECK_OBJECT(par_params);
        tmp_isinstance_inst_1 = par_params;
        tmp_isinstance_cls_1 = (PyObject *)&PyDict_Type;
        tmp_res = PyObject_IsInstance(tmp_isinstance_inst_1, tmp_isinstance_cls_1);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 35;
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
    {
        PyObject *tmp_list_arg_1;
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_args_element_value_2;
        PyObject *tmp_list_arg_2;
        PyObject *tmp_called_value_2;
        PyObject *tmp_expression_value_1;
        tmp_called_value_1 = (PyObject *)&PyFilter_Type;
        CHECK_OBJECT(var_is_oauth);
        tmp_args_element_value_1 = var_is_oauth;
        CHECK_OBJECT(par_params);
        tmp_expression_value_1 = par_params;
        tmp_called_value_2 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[8]);
        if (tmp_called_value_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 36;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params->m_frame.f_lineno = 36;
        tmp_list_arg_2 = CALL_FUNCTION_NO_ARGS(tstate, tmp_called_value_2);
        Py_DECREF(tmp_called_value_2);
        if (tmp_list_arg_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 36;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        tmp_args_element_value_2 = MAKE_LIST(tstate, tmp_list_arg_2);
        Py_DECREF(tmp_list_arg_2);
        if (tmp_args_element_value_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 36;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params->m_frame.f_lineno = 36;
        {
            PyObject *call_args[] = {tmp_args_element_value_1, tmp_args_element_value_2};
            tmp_list_arg_1 = CALL_FUNCTION_WITH_ARGS2(tstate, tmp_called_value_1, call_args);
        }

        Py_DECREF(tmp_args_element_value_2);
        if (tmp_list_arg_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 36;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        tmp_return_value = MAKE_LIST(tstate, tmp_list_arg_1);
        Py_DECREF(tmp_list_arg_1);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 36;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        goto frame_return_exit_1;
    }
    goto branch_end_1;
    branch_no_1:;
    {
        PyObject *tmp_list_arg_3;
        PyObject *tmp_called_value_3;
        PyObject *tmp_args_element_value_3;
        PyObject *tmp_args_element_value_4;
        tmp_called_value_3 = (PyObject *)&PyFilter_Type;
        CHECK_OBJECT(var_is_oauth);
        tmp_args_element_value_3 = var_is_oauth;
        CHECK_OBJECT(par_params);
        tmp_args_element_value_4 = par_params;
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params->m_frame.f_lineno = 38;
        {
            PyObject *call_args[] = {tmp_args_element_value_3, tmp_args_element_value_4};
            tmp_list_arg_3 = CALL_FUNCTION_WITH_ARGS2(tstate, tmp_called_value_3, call_args);
        }

        if (tmp_list_arg_3 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 38;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        tmp_return_value = MAKE_LIST(tstate, tmp_list_arg_3);
        Py_DECREF(tmp_list_arg_3);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 38;
            type_description_1 = "oo";
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

    goto try_return_handler_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params,
        type_description_1,
        par_params,
        var_is_oauth
    );


    // Release cached frame if used for exception.
    if (frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params == cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params);
        cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params = NULL;
    }

    assertFrameObject(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Return handler code:
    try_return_handler_1:;
    Py_XDECREF(var_is_oauth);
    var_is_oauth = NULL;
    goto function_return_exit;
    // Exception handler code:
    try_except_handler_1:;
    exception_keeper_lineno_1 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_1 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    Py_XDECREF(var_is_oauth);
    var_is_oauth = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_1;
    exception_lineno = exception_keeper_lineno_1;

    goto function_exception_exit;
    // End of try:

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_params);
    Py_DECREF(par_params);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_params);
    Py_DECREF(par_params);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_kv = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth)) {
        Py_XDECREF(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth = MAKE_FUNCTION_FRAME(tstate, code_objects_6b7f0d6a33c825b15a2567335d2b1008, module_oauthlib$oauth1$rfc5849$utils, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth->m_type_description == NULL);
    frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth = cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth);
    assert(Py_REFCNT(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_expression_value_1;
        PyObject *tmp_expression_value_2;
        PyObject *tmp_subscript_value_1;
        CHECK_OBJECT(par_kv);
        tmp_expression_value_2 = par_kv;
        tmp_subscript_value_1 = const_int_0;
        tmp_expression_value_1 = LOOKUP_SUBSCRIPT_CONST(tstate, tmp_expression_value_2, tmp_subscript_value_1, 0);
        if (tmp_expression_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 34;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_called_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[10]);
        Py_DECREF(tmp_expression_value_1);
        if (tmp_called_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 34;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth->m_frame.f_lineno = 34;
        tmp_return_value = CALL_FUNCTION_WITH_POS_ARGS1(tstate, tmp_called_value_1, mod_consts[11]);

        Py_DECREF(tmp_called_value_1);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 34;
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
            exception_tb = MAKE_TRACEBACK(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth,
        type_description_1,
        par_kv
    );


    // Release cached frame if used for exception.
    if (frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth == cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth);
        cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth = NULL;
    }

    assertFrameObject(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_kv);
    Py_DECREF(par_kv);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_kv);
    Py_DECREF(par_kv);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_u = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    int tmp_res;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    PyObject *tmp_return_value = NULL;
    static struct Nuitka_FrameObject *cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape)) {
        Py_XDECREF(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape = MAKE_FUNCTION_FRAME(tstate, code_objects_0dbb49b86a3755c06d7a5fd9a741d332, module_oauthlib$oauth1$rfc5849$utils, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape->m_type_description == NULL);
    frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape = cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape);
    assert(Py_REFCNT(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape) == 2);

    // Framed code:
    {
        bool tmp_condition_result_1;
        PyObject *tmp_operand_value_1;
        PyObject *tmp_isinstance_inst_1;
        PyObject *tmp_isinstance_cls_1;
        CHECK_OBJECT(par_u);
        tmp_isinstance_inst_1 = par_u;
        tmp_isinstance_cls_1 = (PyObject *)&PyUnicode_Type;
        tmp_res = PyObject_IsInstance(tmp_isinstance_inst_1, tmp_isinstance_cls_1);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 49;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_operand_value_1 = (tmp_res != 0) ? Py_True : Py_False;
        tmp_res = CHECK_IF_TRUE(tmp_operand_value_1);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 49;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_1 = (tmp_res == 0) ? true : false;
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
        PyObject *tmp_add_expr_left_1;
        PyObject *tmp_add_expr_right_1;
        PyObject *tmp_kw_call_arg_value_0_1;
        PyObject *tmp_kw_call_arg_value_1_1;
        PyObject *tmp_kw_call_arg_value_2_1;
        PyObject *tmp_type_arg_1;
        tmp_add_expr_left_1 = mod_consts[12];
        tmp_kw_call_arg_value_0_1 = mod_consts[13];
        CHECK_OBJECT(par_u);
        tmp_kw_call_arg_value_1_1 = par_u;
        CHECK_OBJECT(par_u);
        tmp_type_arg_1 = par_u;
        tmp_kw_call_arg_value_2_1 = BUILTIN_TYPE1(tmp_type_arg_1);
        assert(!(tmp_kw_call_arg_value_2_1 == NULL));
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape->m_frame.f_lineno = 51;
        {
            PyObject *call_args[] = {tmp_kw_call_arg_value_0_1, tmp_kw_call_arg_value_1_1, tmp_kw_call_arg_value_2_1};
            tmp_add_expr_right_1 = CALL_FUNCTION_WITH_ARGS3(tstate, unicode_builtin_format, call_args);
        }

        Py_DECREF(tmp_kw_call_arg_value_2_1);
        if (tmp_add_expr_right_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 51;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_make_exception_arg_1 = BINARY_OPERATION_ADD_OBJECT_UNICODE_UNICODE(tmp_add_expr_left_1, tmp_add_expr_right_1);
        Py_DECREF(tmp_add_expr_right_1);
        assert(!(tmp_make_exception_arg_1 == NULL));
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape->m_frame.f_lineno = 50;
        tmp_raise_type_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_ValueError, tmp_make_exception_arg_1);
        Py_DECREF(tmp_make_exception_arg_1);
        assert(!(tmp_raise_type_1 == NULL));
        exception_state.exception_type = tmp_raise_type_1;
        exception_lineno = 50;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);
        type_description_1 = "o";
        goto frame_exception_exit_1;
    }
    branch_no_1:;
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_value_1;
        PyObject *tmp_tuple_element_1;
        PyObject *tmp_kwargs_value_1;
        tmp_called_value_1 = module_var_accessor_oauthlib$$36$oauth1$$36$rfc5849$$36$utils$quote(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[14]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 54;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_u);
        tmp_tuple_element_1 = par_u;
        tmp_args_value_1 = MAKE_TUPLE_EMPTY(tstate, 1);
        PyTuple_SET_ITEM0(tmp_args_value_1, 0, tmp_tuple_element_1);
        tmp_kwargs_value_1 = DICT_COPY(tstate, mod_consts[15]);
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape->m_frame.f_lineno = 54;
        tmp_return_value = CALL_FUNCTION(tstate, tmp_called_value_1, tmp_args_value_1, tmp_kwargs_value_1);
        Py_DECREF(tmp_args_value_1);
        Py_DECREF(tmp_kwargs_value_1);
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
            exception_tb = MAKE_TRACEBACK(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape,
        type_description_1,
        par_u
    );


    // Release cached frame if used for exception.
    if (frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape == cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape);
        cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape = NULL;
    }

    assertFrameObject(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_u);
    Py_DECREF(par_u);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_u);
    Py_DECREF(par_u);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_u = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    int tmp_res;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    PyObject *tmp_return_value = NULL;
    static struct Nuitka_FrameObject *cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape)) {
        Py_XDECREF(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape = MAKE_FUNCTION_FRAME(tstate, code_objects_2c3a793824c5a61aca6f5852fee270f4, module_oauthlib$oauth1$rfc5849$utils, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape->m_type_description == NULL);
    frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape = cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape);
    assert(Py_REFCNT(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape) == 2);

    // Framed code:
    {
        bool tmp_condition_result_1;
        PyObject *tmp_operand_value_1;
        PyObject *tmp_isinstance_inst_1;
        PyObject *tmp_isinstance_cls_1;
        CHECK_OBJECT(par_u);
        tmp_isinstance_inst_1 = par_u;
        tmp_isinstance_cls_1 = (PyObject *)&PyUnicode_Type;
        tmp_res = PyObject_IsInstance(tmp_isinstance_inst_1, tmp_isinstance_cls_1);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 58;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_operand_value_1 = (tmp_res != 0) ? Py_True : Py_False;
        tmp_res = CHECK_IF_TRUE(tmp_operand_value_1);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 58;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_1 = (tmp_res == 0) ? true : false;
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
        tmp_make_exception_arg_1 = mod_consts[17];
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape->m_frame.f_lineno = 59;
        tmp_raise_type_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_ValueError, tmp_make_exception_arg_1);
        assert(!(tmp_raise_type_1 == NULL));
        exception_state.exception_type = tmp_raise_type_1;
        exception_lineno = 59;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);
        type_description_1 = "o";
        goto frame_exception_exit_1;
    }
    branch_no_1:;
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        tmp_called_value_1 = module_var_accessor_oauthlib$$36$oauth1$$36$rfc5849$$36$utils$unquote(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[18]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 60;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_u);
        tmp_args_element_value_1 = par_u;
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape->m_frame.f_lineno = 60;
        tmp_return_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_1, tmp_args_element_value_1);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 60;
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
            exception_tb = MAKE_TRACEBACK(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape,
        type_description_1,
        par_u
    );


    // Release cached frame if used for exception.
    if (frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape == cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape);
        cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape = NULL;
    }

    assertFrameObject(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_u);
    Py_DECREF(par_u);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_u);
    Py_DECREF(par_u);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_l = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list)) {
        Py_XDECREF(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list = MAKE_FUNCTION_FRAME(tstate, code_objects_72d18a6d338f28658fc75543bd9e40cb, module_oauthlib$oauth1$rfc5849$utils, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list->m_type_description == NULL);
    frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list = cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list);
    assert(Py_REFCNT(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list) == 2);

    // Framed code:
    {
        PyObject *tmp_called_instance_1;
        PyObject *tmp_args_element_value_1;
        tmp_called_instance_1 = module_var_accessor_oauthlib$$36$oauth1$$36$rfc5849$$36$utils$urllib2(tstate);
        if (unlikely(tmp_called_instance_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[19]);
        }

        if (tmp_called_instance_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 66;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_l);
        tmp_args_element_value_1 = par_l;
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list->m_frame.f_lineno = 66;
        tmp_return_value = CALL_METHOD_WITH_SINGLE_ARG(tstate, tmp_called_instance_1, mod_consts[20], tmp_args_element_value_1);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 66;
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
            exception_tb = MAKE_TRACEBACK(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list,
        type_description_1,
        par_l
    );


    // Release cached frame if used for exception.
    if (frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list == cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list);
        cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list = NULL;
    }

    assertFrameObject(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_l);
    Py_DECREF(par_l);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_l);
    Py_DECREF(par_l);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_u = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    static struct Nuitka_FrameObject *cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list)) {
        Py_XDECREF(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list = MAKE_FUNCTION_FRAME(tstate, code_objects_147d7551bd2088674562b2b974da28c5, module_oauthlib$oauth1$rfc5849$utils, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list->m_type_description == NULL);
    frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list = cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list);
    assert(Py_REFCNT(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list) == 2);

    // Framed code:
    {
        PyObject *tmp_called_instance_1;
        PyObject *tmp_args_element_value_1;
        tmp_called_instance_1 = module_var_accessor_oauthlib$$36$oauth1$$36$rfc5849$$36$utils$urllib2(tstate);
        if (unlikely(tmp_called_instance_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[19]);
        }

        if (tmp_called_instance_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 72;
            type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_u);
        tmp_args_element_value_1 = par_u;
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list->m_frame.f_lineno = 72;
        tmp_return_value = CALL_METHOD_WITH_SINGLE_ARG(tstate, tmp_called_instance_1, mod_consts[22], tmp_args_element_value_1);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 72;
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
            exception_tb = MAKE_TRACEBACK(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list,
        type_description_1,
        par_u
    );


    // Release cached frame if used for exception.
    if (frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list == cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list);
        cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list = NULL;
    }

    assertFrameObject(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_u);
    Py_DECREF(par_u);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_u);
    Py_DECREF(par_u);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_authorization_header = python_pars[0];
    PyObject *var_items = NULL;
    struct Nuitka_FrameObject *frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;
    struct Nuitka_ExceptionStackItem exception_preserved_1;
    int tmp_res;
    bool tmp_result;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_2;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_2;
    static struct Nuitka_FrameObject *cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_3;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_3;

    // Actual function body.
    // Tried code:
    if (isFrameUnusable(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header)) {
        Py_XDECREF(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header = MAKE_FUNCTION_FRAME(tstate, code_objects_3992bd78681b53edd831c9dbef734113, module_oauthlib$oauth1$rfc5849$utils, sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header->m_type_description == NULL);
    frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header = cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header);
    assert(Py_REFCNT(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header) == 2);

    // Framed code:
    {
        nuitka_bool tmp_condition_result_1;
        PyObject *tmp_called_value_1;
        PyObject *tmp_expression_value_1;
        PyObject *tmp_called_value_2;
        PyObject *tmp_expression_value_2;
        PyObject *tmp_expression_value_3;
        PyObject *tmp_subscript_value_1;
        PyObject *tmp_call_result_1;
        int tmp_truth_name_1;
        CHECK_OBJECT(par_authorization_header);
        tmp_expression_value_3 = par_authorization_header;
        tmp_subscript_value_1 = mod_consts[24];
        tmp_expression_value_2 = LOOKUP_SUBSCRIPT(tstate, tmp_expression_value_3, tmp_subscript_value_1);
        if (tmp_expression_value_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 78;
            type_description_1 = "oNo";
            goto frame_exception_exit_1;
        }
        tmp_called_value_2 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_2, mod_consts[25]);
        Py_DECREF(tmp_expression_value_2);
        if (tmp_called_value_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 78;
            type_description_1 = "oNo";
            goto frame_exception_exit_1;
        }
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header->m_frame.f_lineno = 78;
        tmp_expression_value_1 = CALL_FUNCTION_NO_ARGS(tstate, tmp_called_value_2);
        Py_DECREF(tmp_called_value_2);
        if (tmp_expression_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 78;
            type_description_1 = "oNo";
            goto frame_exception_exit_1;
        }
        tmp_called_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[10]);
        Py_DECREF(tmp_expression_value_1);
        if (tmp_called_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 78;
            type_description_1 = "oNo";
            goto frame_exception_exit_1;
        }
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header->m_frame.f_lineno = 78;
        tmp_call_result_1 = CALL_FUNCTION_WITH_POS_ARGS1(tstate, tmp_called_value_1, mod_consts[26]);

        Py_DECREF(tmp_called_value_1);
        if (tmp_call_result_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 78;
            type_description_1 = "oNo";
            goto frame_exception_exit_1;
        }
        tmp_truth_name_1 = CHECK_IF_TRUE(tmp_call_result_1);
        if (tmp_truth_name_1 == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_call_result_1);

            exception_lineno = 78;
            type_description_1 = "oNo";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_1 = tmp_truth_name_1 == 0 ? NUITKA_BOOL_FALSE : NUITKA_BOOL_TRUE;
        Py_DECREF(tmp_call_result_1);
        if (tmp_condition_result_1 == NUITKA_BOOL_TRUE) {
            goto branch_yes_1;
        } else {
            goto branch_no_1;
        }
    }
    branch_yes_1:;
    {
        PyObject *tmp_assign_source_1;
        PyObject *tmp_called_value_3;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_expression_value_4;
        PyObject *tmp_subscript_value_2;
        tmp_called_value_3 = module_var_accessor_oauthlib$$36$oauth1$$36$rfc5849$$36$utils$parse_http_list(tstate);
        if (unlikely(tmp_called_value_3 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[22]);
        }

        if (tmp_called_value_3 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 79;
            type_description_1 = "oNo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_authorization_header);
        tmp_expression_value_4 = par_authorization_header;
        tmp_subscript_value_2 = mod_consts[27];
        tmp_args_element_value_1 = LOOKUP_SUBSCRIPT(tstate, tmp_expression_value_4, tmp_subscript_value_2);
        if (tmp_args_element_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 79;
            type_description_1 = "oNo";
            goto frame_exception_exit_1;
        }
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header->m_frame.f_lineno = 79;
        tmp_assign_source_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_3, tmp_args_element_value_1);
        Py_DECREF(tmp_args_element_value_1);
        if (tmp_assign_source_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 79;
            type_description_1 = "oNo";
            goto frame_exception_exit_1;
        }
        assert(var_items == NULL);
        var_items = tmp_assign_source_1;
    }
    // Tried code:
    {
        PyObject *tmp_list_arg_1;
        PyObject *tmp_called_value_4;
        PyObject *tmp_expression_value_5;
        PyObject *tmp_called_value_5;
        PyObject *tmp_args_element_value_2;
        tmp_called_value_5 = module_var_accessor_oauthlib$$36$oauth1$$36$rfc5849$$36$utils$parse_keqv_list(tstate);
        if (unlikely(tmp_called_value_5 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[20]);
        }

        if (tmp_called_value_5 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 81;
            type_description_1 = "oNo";
            goto try_except_handler_2;
        }
        CHECK_OBJECT(var_items);
        tmp_args_element_value_2 = var_items;
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header->m_frame.f_lineno = 81;
        tmp_expression_value_5 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_5, tmp_args_element_value_2);
        if (tmp_expression_value_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 81;
            type_description_1 = "oNo";
            goto try_except_handler_2;
        }
        tmp_called_value_4 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_5, mod_consts[8]);
        Py_DECREF(tmp_expression_value_5);
        if (tmp_called_value_4 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 81;
            type_description_1 = "oNo";
            goto try_except_handler_2;
        }
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header->m_frame.f_lineno = 81;
        tmp_list_arg_1 = CALL_FUNCTION_NO_ARGS(tstate, tmp_called_value_4);
        Py_DECREF(tmp_called_value_4);
        if (tmp_list_arg_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 81;
            type_description_1 = "oNo";
            goto try_except_handler_2;
        }
        tmp_return_value = MAKE_LIST(tstate, tmp_list_arg_1);
        Py_DECREF(tmp_list_arg_1);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 81;
            type_description_1 = "oNo";
            goto try_except_handler_2;
        }
        goto frame_return_exit_1;
    }
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Exception handler code:
    try_except_handler_2:;
    exception_keeper_lineno_1 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_1 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    // Preserve existing published exception id 1.
    exception_preserved_1 = GET_CURRENT_EXCEPTION(tstate);

    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_keeper_name_1);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header, exception_keeper_lineno_1);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_keeper_name_1, exception_tb);
        } else if (exception_keeper_lineno_1 != 0) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header, exception_keeper_lineno_1);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_keeper_name_1, exception_tb);
        }
    }

    PUBLISH_CURRENT_EXCEPTION(tstate, &exception_keeper_name_1);
    // Tried code:
    {
        bool tmp_condition_result_2;
        PyObject *tmp_cmp_expr_left_1;
        PyObject *tmp_cmp_expr_right_1;
        tmp_cmp_expr_left_1 = EXC_TYPE(tstate);
        tmp_cmp_expr_right_1 = mod_consts[28];
        tmp_res = EXCEPTION_MATCH_BOOL(tstate, tmp_cmp_expr_left_1, tmp_cmp_expr_right_1);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 82;
            type_description_1 = "oNo";
            goto try_except_handler_3;
        }
        tmp_condition_result_2 = (tmp_res == 0) ? true : false;
        if (tmp_condition_result_2 != false) {
            goto branch_yes_2;
        } else {
            goto branch_no_2;
        }
    }
    branch_yes_2:;
    tmp_result = RERAISE_EXCEPTION(tstate, &exception_state);
    if (unlikely(tmp_result == false)) {
        exception_lineno = 80;
    }

    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);

        if ((exception_tb != NULL) && (exception_tb->tb_frame == &frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header->m_frame)) {
            frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header->m_frame.f_lineno = exception_tb->tb_lineno;
        }
    }
    type_description_1 = "oNo";
    goto try_except_handler_3;
    branch_no_2:;
    goto try_end_1;
    // Exception handler code:
    try_except_handler_3:;
    exception_keeper_lineno_2 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_2 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    // Restore previous exception id 1.
    SET_CURRENT_EXCEPTION(tstate, &exception_preserved_1);

    // Re-raise.
    exception_state = exception_keeper_name_2;
    exception_lineno = exception_keeper_lineno_2;

    goto frame_exception_exit_1;
    // End of try:
    try_end_1:;
    // Restore previous exception id 1.
    SET_CURRENT_EXCEPTION(tstate, &exception_preserved_1);

    goto try_end_2;
    NUITKA_CANNOT_GET_HERE("exception handler codes exits in all cases");
    return NULL;
    // End of try:
    try_end_2:;
    branch_no_1:;
    {
        PyObject *tmp_raise_type_1;
        PyObject *tmp_make_exception_arg_1;
        tmp_make_exception_arg_1 = mod_consts[29];
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header->m_frame.f_lineno = 84;
        tmp_raise_type_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, PyExc_ValueError, tmp_make_exception_arg_1);
        assert(!(tmp_raise_type_1 == NULL));
        exception_state.exception_type = tmp_raise_type_1;
        exception_lineno = 84;
        RAISE_EXCEPTION_WITH_TYPE(tstate, &exception_state);
        type_description_1 = "oNo";
        goto frame_exception_exit_1;
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
            exception_tb = MAKE_TRACEBACK(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header,
        type_description_1,
        par_authorization_header,
        NULL,
        var_items
    );


    // Release cached frame if used for exception.
    if (frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header == cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header);
        cache_frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header = NULL;
    }

    assertFrameObject(frame_frame_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Return handler code:
    try_return_handler_1:;
    CHECK_OBJECT(var_items);
    Py_DECREF(var_items);
    var_items = NULL;
    goto function_return_exit;
    // Exception handler code:
    try_except_handler_1:;
    exception_keeper_lineno_3 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_3 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    Py_XDECREF(var_items);
    var_items = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_3;
    exception_lineno = exception_keeper_lineno_3;

    goto function_exception_exit;
    // End of try:

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_authorization_header);
    Py_DECREF(par_authorization_header);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_authorization_header);
    Py_DECREF(par_authorization_header);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}



static PyObject *MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params,
        mod_consts[42],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_88106b63226aba3175e5f08001b84ae6,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_oauthlib$oauth1$rfc5849$utils,
        mod_consts[3],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper(PyThreadState *tstate, struct Nuitka_CellObject **closure) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper,
        mod_consts[0],
#if PYTHON_VERSION >= 0x300
        mod_consts[1],
#endif
        code_objects_d1755dfe63e23a4e710f43abccbe2c78,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_oauthlib$oauth1$rfc5849$utils,
        NULL,
        closure,
        1
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params,
        mod_consts[4],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_8209180ee940e61f59f6370a2913482d,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_oauthlib$oauth1$rfc5849$utils,
        mod_consts[9],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth,
        mod_consts[6],
#if PYTHON_VERSION >= 0x300
        mod_consts[7],
#endif
        code_objects_6b7f0d6a33c825b15a2567335d2b1008,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_oauthlib$oauth1$rfc5849$utils,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape,
        mod_consts[43],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_0dbb49b86a3755c06d7a5fd9a741d332,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_oauthlib$oauth1$rfc5849$utils,
        mod_consts[16],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape,
        mod_consts[44],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_2c3a793824c5a61aca6f5852fee270f4,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_oauthlib$oauth1$rfc5849$utils,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list,
        mod_consts[20],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_72d18a6d338f28658fc75543bd9e40cb,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_oauthlib$oauth1$rfc5849$utils,
        mod_consts[21],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list,
        mod_consts[22],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_147d7551bd2088674562b2b974da28c5,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_oauthlib$oauth1$rfc5849$utils,
        mod_consts[23],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header,
        mod_consts[45],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_3992bd78681b53edd831c9dbef734113,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_oauthlib$oauth1$rfc5849$utils,
        mod_consts[30],
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

static function_impl_code const function_table_oauthlib$oauth1$rfc5849$utils[] = {
    impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params$$36$$$36$$$36$function__1_wrapper,
    impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params$$36$$$36$$$36$function__1_is_oauth,
    impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params,
    impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params,
    impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape,
    impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape,
    impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list,
    impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list,
    impl_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header,
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

    return Nuitka_Function_GetFunctionState(function, function_table_oauthlib$oauth1$rfc5849$utils);
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
        module_oauthlib$oauth1$rfc5849$utils,
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
        function_table_oauthlib$oauth1$rfc5849$utils,
        sizeof(function_table_oauthlib$oauth1$rfc5849$utils) / sizeof(function_impl_code)
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
static char const *module_full_name = "oauthlib.oauth1.rfc5849.utils";
#endif

// Internal entry point for module code.
PyObject *modulecode_oauthlib$oauth1$rfc5849$utils(PyThreadState *tstate, PyObject *module, struct Nuitka_MetaPathBasedLoaderEntry const *loader_entry) {
    // Report entry to PGO.
    PGO_onModuleEntered("oauthlib$oauth1$rfc5849$utils");

    // Store the module for future use.
    module_oauthlib$oauth1$rfc5849$utils = module;

    moduledict_oauthlib$oauth1$rfc5849$utils = MODULE_DICT(module_oauthlib$oauth1$rfc5849$utils);

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
        PRINT_STRING("oauthlib$oauth1$rfc5849$utils: Calling setupMetaPathBasedLoader().\n");
#endif
        setupMetaPathBasedLoader(tstate);
#if 0 >= 0
#ifdef _NUITKA_TRACE
        PRINT_STRING("oauthlib$oauth1$rfc5849$utils: Calling updateMetaPathBasedLoaderModuleRoot().\n");
#endif
        updateMetaPathBasedLoaderModuleRoot(module_full_name);
#endif


#if PYTHON_VERSION >= 0x300
        patchInspectModule(tstate);
#endif

#endif

        /* The constants only used by this module are created now. */
        NUITKA_PRINT_TRACE("oauthlib$oauth1$rfc5849$utils: Calling createModuleConstants().\n");
        createModuleConstants(tstate);

#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
        createModuleCodeObjects();
#endif
        init_done = true;
    }

#if _NUITKA_MODULE_MODE && 0
    PyObject *pre_load = IMPORT_EMBEDDED_MODULE(tstate, "oauthlib.oauth1.rfc5849.utils" "-preLoad");
    if (pre_load == NULL) {
        return NULL;
    }
#endif

    // PRINT_STRING("in initoauthlib$oauth1$rfc5849$utils\n");

#ifdef _NUITKA_PLUGIN_DILL_ENABLED
    {
        char const *module_name_c;
        if (loader_entry != NULL) {
            module_name_c = loader_entry->name;
        } else {
            PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)const_str_plain___name__);
            module_name_c = Nuitka_String_AsString(module_name);
        }

        registerDillPluginTables(tstate, module_name_c, &_method_def_reduce_compiled_function, &_method_def_create_compiled_function);
    }
#endif

    // Set "__compiled__" to what version information we have.
    UPDATE_STRING_DICT0(
        moduledict_oauthlib$oauth1$rfc5849$utils,
        (Nuitka_StringObject *)const_str_plain___compiled__,
        Nuitka_dunder_compiled_value
    );

    // Update "__package__" value to what it ought to be.
    {
#if 0
        UPDATE_STRING_DICT0(
            moduledict_oauthlib$oauth1$rfc5849$utils,
            (Nuitka_StringObject *)const_str_plain___package__,
            mod_consts[56]
        );
#elif 0
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)const_str_plain___name__);

        UPDATE_STRING_DICT0(
            moduledict_oauthlib$oauth1$rfc5849$utils,
            (Nuitka_StringObject *)const_str_plain___package__,
            module_name
        );
#else

#if PYTHON_VERSION < 0x300
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)const_str_plain___name__);
        char const *module_name_cstr = PyString_AS_STRING(module_name);

        char const *last_dot = strrchr(module_name_cstr, '.');

        if (last_dot != NULL) {
            UPDATE_STRING_DICT1(
                moduledict_oauthlib$oauth1$rfc5849$utils,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyString_FromStringAndSize(module_name_cstr, last_dot - module_name_cstr)
            );
        }
#else
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)const_str_plain___name__);
        Py_ssize_t dot_index = PyUnicode_Find(module_name, const_str_dot, 0, PyUnicode_GetLength(module_name), -1);

        if (dot_index != -1) {
            UPDATE_STRING_DICT1(
                moduledict_oauthlib$oauth1$rfc5849$utils,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyUnicode_Substring(module_name, 0, dot_index)
            );
        }
#endif
#endif
    }

    CHECK_OBJECT(module_oauthlib$oauth1$rfc5849$utils);

    // For deep importing of a module we need to have "__builtins__", so we set
    // it ourselves in the same way than CPython does. Note: This must be done
    // before the frame object is allocated, or else it may fail.

    if (GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)const_str_plain___builtins__) == NULL) {
        PyObject *value = (PyObject *)builtin_module;

        // Check if main module, not a dict then but the module itself.
#if _NUITKA_MODULE_MODE || !0
        value = PyModule_GetDict(value);
#endif

        UPDATE_STRING_DICT0(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)const_str_plain___builtins__, value);
    }

    PyObject *module_loader = Nuitka_Loader_New(loader_entry);
    UPDATE_STRING_DICT0(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)const_str_plain___loader__, module_loader);

#if PYTHON_VERSION >= 0x300
// Set the "__spec__" value

#if 0
    // Main modules just get "None" as spec.
    UPDATE_STRING_DICT0(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)const_str_plain___spec__, Py_None);
#else
    // Other modules get a "ModuleSpec" from the standard mechanism.
    {
        PyObject *bootstrap_module = getImportLibBootstrapModule();
        CHECK_OBJECT(bootstrap_module);

        PyObject *_spec_from_module = PyObject_GetAttrString(bootstrap_module, "_spec_from_module");
        CHECK_OBJECT(_spec_from_module);

        PyObject *spec_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, _spec_from_module, module_oauthlib$oauth1$rfc5849$utils);
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

        UPDATE_STRING_DICT1(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)const_str_plain___spec__, spec_value);
    }
#endif
#endif

    // Temp variables if any
    PyObject *tmp_import_from_1__module = NULL;
    struct Nuitka_FrameObject *frame_frame_oauthlib$oauth1$rfc5849$utils;
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
        tmp_assign_source_1 = mod_consts[31];
        UPDATE_STRING_DICT0(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[2], tmp_assign_source_1);
    }
    {
        PyObject *tmp_assign_source_2;
        tmp_assign_source_2 = module_filename_obj;
        UPDATE_STRING_DICT0(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[32], tmp_assign_source_2);
    }
    frame_frame_oauthlib$oauth1$rfc5849$utils = MAKE_MODULE_FRAME(code_objects_84ce88d53e34eefbbcd8eb6fe36f44eb, module_oauthlib$oauth1$rfc5849$utils);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_oauthlib$oauth1$rfc5849$utils);
    assert(Py_REFCNT(frame_frame_oauthlib$oauth1$rfc5849$utils) == 2);

    // Framed code:
    {
        PyObject *tmp_assattr_value_1;
        PyObject *tmp_assattr_target_1;
        tmp_assattr_value_1 = module_filename_obj;
        tmp_assattr_target_1 = module_var_accessor_oauthlib$$36$oauth1$$36$rfc5849$$36$utils$__spec__(tstate);
        assert(!(tmp_assattr_target_1 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_1, mod_consts[33], tmp_assattr_value_1);
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
        tmp_assattr_target_2 = module_var_accessor_oauthlib$$36$oauth1$$36$rfc5849$$36$utils$__spec__(tstate);
        assert(!(tmp_assattr_target_2 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_2, mod_consts[34], tmp_assattr_value_2);
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
        UPDATE_STRING_DICT0(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[35], tmp_assign_source_3);
    }
    {
        PyObject *tmp_assign_source_4;
        PyObject *tmp_import_name_from_1;
        PyObject *tmp_name_value_1;
        PyObject *tmp_globals_arg_value_1;
        PyObject *tmp_locals_arg_value_1;
        PyObject *tmp_fromlist_value_1;
        PyObject *tmp_level_value_1;
        tmp_name_value_1 = mod_consts[36];
        tmp_globals_arg_value_1 = (PyObject *)moduledict_oauthlib$oauth1$rfc5849$utils;
        tmp_locals_arg_value_1 = Py_None;
        tmp_fromlist_value_1 = Py_None;
        tmp_level_value_1 = const_int_0;
        frame_frame_oauthlib$oauth1$rfc5849$utils->m_frame.f_lineno = 8;
        tmp_import_name_from_1 = IMPORT_MODULE5(tstate, tmp_name_value_1, tmp_globals_arg_value_1, tmp_locals_arg_value_1, tmp_fromlist_value_1, tmp_level_value_1);
        if (tmp_import_name_from_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 8;

            goto frame_exception_exit_1;
        }
        if (PyModule_Check(tmp_import_name_from_1)) {
            tmp_assign_source_4 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_1,
                (PyObject *)moduledict_oauthlib$oauth1$rfc5849$utils,
                mod_consts[37],
                const_int_0
            );
        } else {
            tmp_assign_source_4 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_1, mod_consts[37]);
        }

        Py_DECREF(tmp_import_name_from_1);
        if (tmp_assign_source_4 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 8;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[19], tmp_assign_source_4);
    }
    {
        PyObject *tmp_assign_source_5;
        PyObject *tmp_name_value_2;
        PyObject *tmp_globals_arg_value_2;
        PyObject *tmp_locals_arg_value_2;
        PyObject *tmp_fromlist_value_2;
        PyObject *tmp_level_value_2;
        tmp_name_value_2 = mod_consts[38];
        tmp_globals_arg_value_2 = (PyObject *)moduledict_oauthlib$oauth1$rfc5849$utils;
        tmp_locals_arg_value_2 = Py_None;
        tmp_fromlist_value_2 = mod_consts[39];
        tmp_level_value_2 = const_int_0;
        frame_frame_oauthlib$oauth1$rfc5849$utils->m_frame.f_lineno = 10;
        tmp_assign_source_5 = IMPORT_MODULE5(tstate, tmp_name_value_2, tmp_globals_arg_value_2, tmp_locals_arg_value_2, tmp_fromlist_value_2, tmp_level_value_2);
        if (tmp_assign_source_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 10;

            goto frame_exception_exit_1;
        }
        assert(tmp_import_from_1__module == NULL);
        tmp_import_from_1__module = tmp_assign_source_5;
    }
    // Tried code:
    {
        PyObject *tmp_assign_source_6;
        PyObject *tmp_import_name_from_2;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_2 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_2)) {
            tmp_assign_source_6 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_2,
                (PyObject *)moduledict_oauthlib$oauth1$rfc5849$utils,
                mod_consts[14],
                const_int_0
            );
        } else {
            tmp_assign_source_6 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_2, mod_consts[14]);
        }

        if (tmp_assign_source_6 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 10;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[14], tmp_assign_source_6);
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
                (PyObject *)moduledict_oauthlib$oauth1$rfc5849$utils,
                mod_consts[18],
                const_int_0
            );
        } else {
            tmp_assign_source_7 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_3, mod_consts[18]);
        }

        if (tmp_assign_source_7 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 10;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[18], tmp_assign_source_7);
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


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_oauthlib$oauth1$rfc5849$utils, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_oauthlib$oauth1$rfc5849$utils->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_oauthlib$oauth1$rfc5849$utils, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }



    assertFrameObject(frame_frame_oauthlib$oauth1$rfc5849$utils);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto module_exception_exit;
    frame_no_exception_1:;
    CHECK_OBJECT(tmp_import_from_1__module);
    Py_DECREF(tmp_import_from_1__module);
    tmp_import_from_1__module = NULL;
    {
        PyObject *tmp_assign_source_8;
        tmp_assign_source_8 = mod_consts[40];
        UPDATE_STRING_DICT0(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[41], tmp_assign_source_8);
    }
    {
        PyObject *tmp_assign_source_9;


        tmp_assign_source_9 = MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__1_filter_params(tstate);

        UPDATE_STRING_DICT1(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[42], tmp_assign_source_9);
    }
    {
        PyObject *tmp_assign_source_10;


        tmp_assign_source_10 = MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__2_filter_oauth_params(tstate);

        UPDATE_STRING_DICT1(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[4], tmp_assign_source_10);
    }
    {
        PyObject *tmp_assign_source_11;


        tmp_assign_source_11 = MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__3_escape(tstate);

        UPDATE_STRING_DICT1(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[43], tmp_assign_source_11);
    }
    {
        PyObject *tmp_assign_source_12;


        tmp_assign_source_12 = MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__4_unescape(tstate);

        UPDATE_STRING_DICT1(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[44], tmp_assign_source_12);
    }
    {
        PyObject *tmp_assign_source_13;


        tmp_assign_source_13 = MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__5_parse_keqv_list(tstate);

        UPDATE_STRING_DICT1(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[20], tmp_assign_source_13);
    }
    {
        PyObject *tmp_assign_source_14;


        tmp_assign_source_14 = MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__6_parse_http_list(tstate);

        UPDATE_STRING_DICT1(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[22], tmp_assign_source_14);
    }
    {
        PyObject *tmp_assign_source_15;


        tmp_assign_source_15 = MAKE_FUNCTION_oauthlib$oauth1$rfc5849$utils$$36$$$36$$$36$function__7_parse_authorization_header(tstate);

        UPDATE_STRING_DICT1(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)mod_consts[45], tmp_assign_source_15);
    }

    // Report to PGO about leaving the module without error.
    PGO_onModuleExit("oauthlib$oauth1$rfc5849$utils", false);

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *post_load = IMPORT_EMBEDDED_MODULE(tstate, "oauthlib.oauth1.rfc5849.utils" "-postLoad");
        if (post_load == NULL) {
            return NULL;
        }
    }
#endif

    Py_INCREF(module_oauthlib$oauth1$rfc5849$utils);
    return module_oauthlib$oauth1$rfc5849$utils;
    module_exception_exit:

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_oauthlib$oauth1$rfc5849$utils, (Nuitka_StringObject *)const_str_plain___name__);

        if (module_name != NULL) {
            Nuitka_DelModule(tstate, module_name);
        }
    }
#endif
    PGO_onModuleExit("oauthlib$oauth1$rfc5849$utils", false);

    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);
    return NULL;
}
