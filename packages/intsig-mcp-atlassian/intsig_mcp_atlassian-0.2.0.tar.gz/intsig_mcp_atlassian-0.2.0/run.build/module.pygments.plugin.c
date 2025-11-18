/* Generated code for Python module 'pygments$plugin'
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

/* The "module_pygments$plugin" is a Python object pointer of module type.
 *
 * Note: For full compatibility with CPython, every module variable access
 * needs to go through it except for cases where the module cannot possibly
 * have changed in the mean time.
 */

PyObject *module_pygments$plugin;
PyDictObject *moduledict_pygments$plugin;

/* The declarations of module constants used, if any. */
static PyObject *mod_consts[220];
#ifndef __NUITKA_NO_ASSERT__
static Py_hash_t mod_consts_hash[220];
#endif

static PyObject *module_filename_obj = NULL;

/* Indicator if this modules private constants were created yet. */
static bool constants_created = false;

/* Function to create module private constants. */
static void createModuleConstants(PyThreadState *tstate) {
    if (constants_created == false) {
        loadConstantsBlob(tstate, &mod_consts[0], UN_TRANSLATE("pygments.plugin"));
        constants_created = true;

#ifndef __NUITKA_NO_ASSERT__
        for (int i = 0; i < 220; i++) {
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
void checkModuleConstants_pygments$plugin(PyThreadState *tstate) {
    // The module may not have been used at all, then ignore this.
    if (constants_created == false) return;

    for (int i = 0; i < 220; i++) {
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
static PyObject *module_var_accessor_pygments$$36$plugin$FILTER_ENTRY_POINT(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_pygments$plugin->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_pygments$plugin->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[201]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_pygments$plugin->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[201]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[201], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[201]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[201], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[201]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[201]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[201]);
    }

    return result;
}

static PyObject *module_var_accessor_pygments$$36$plugin$FORMATTER_ENTRY_POINT(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_pygments$plugin->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_pygments$plugin->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[196]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_pygments$plugin->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[196]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[196], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[196]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[196], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[196]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[196]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[196]);
    }

    return result;
}

static PyObject *module_var_accessor_pygments$$36$plugin$LEXER_ENTRY_POINT(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_pygments$plugin->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_pygments$plugin->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[193]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_pygments$plugin->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[193]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[193], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[193]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[193], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[193]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[193]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[193]);
    }

    return result;
}

static PyObject *module_var_accessor_pygments$$36$plugin$STYLE_ENTRY_POINT(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_pygments$plugin->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_pygments$plugin->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[199]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_pygments$plugin->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[199]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[199], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[199]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[199], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[199]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[199]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[199]);
    }

    return result;
}

static PyObject *module_var_accessor_pygments$$36$plugin$__spec__(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_pygments$plugin->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_pygments$plugin->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[219]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_pygments$plugin->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[219]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[219], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[219]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[219], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[219]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[219]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[219]);
    }

    return result;
}

static PyObject *module_var_accessor_pygments$$36$plugin$iter_entry_points(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_pygments$plugin->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_pygments$plugin->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[192]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_pygments$plugin->ma_keys;
    if (likely(DK_IS_UNICODE(dk))) {

#if PYTHON_VERSION >= 0x3c0
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(tstate->interp, dk);
#else
        uint32_t current_dk_version = _Nuitka_PyDictKeys_GetVersionForCurrentState(dk);
#endif

        if (current_dk_version != dict_keys_version) {
            dict_keys_version = current_dk_version;
            Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[192]);
            assert(hash != -1);

            cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[192], hash);
        }

        if (cache_dk_index >= 0) {
            assert(dk->dk_kind != DICT_KEYS_SPLIT);

            PyDictUnicodeEntry *entries = DK_UNICODE_ENTRIES(dk);

            result = entries[cache_dk_index].me_value;

            if (unlikely(result == NULL)) {
                Py_hash_t hash = Nuitka_Py_unicode_get_hash(mod_consts[192]);
                assert(hash != -1);

                cache_dk_index = Nuitka_Py_unicodekeys_lookup_unicode(dk, mod_consts[192], hash);

                if (cache_dk_index >= 0) {
                    result = entries[cache_dk_index].me_value;
                }
            }
        } else {
            result = NULL;
        }
    } else {
        result = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[192]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[192]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[192]);
    }

    return result;
}


#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
// The module code objects.
static PyCodeObject *code_objects_ebe3fc16cc6109fce68be05c0d37c541;
static PyCodeObject *code_objects_2e34d522e2f73478237594a44c21fbc1;
static PyCodeObject *code_objects_f123c9c0a67e7b7b8b0f91665e25826b;
static PyCodeObject *code_objects_84336ce5a4222a6d216dfad8579142cb;
static PyCodeObject *code_objects_176b0d6761461dd1b73c1c6755e3a385;
static PyCodeObject *code_objects_08ae733c9c6ae412f7e5d03217c4342d;

static void createModuleCodeObjects(void) {
    module_filename_obj = MAKE_RELATIVE_PATH(mod_consts[214]); CHECK_OBJECT(module_filename_obj);
    code_objects_ebe3fc16cc6109fce68be05c0d37c541 = MAKE_CODE_OBJECT(module_filename_obj, 1, CO_NOFREE, mod_consts[215], mod_consts[215], NULL, NULL, 0, 0, 0);
    code_objects_2e34d522e2f73478237594a44c21fbc1 = MAKE_CODE_OBJECT(module_filename_obj, 70, CO_GENERATOR | CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[202], mod_consts[202], mod_consts[216], NULL, 0, 0, 0);
    code_objects_f123c9c0a67e7b7b8b0f91665e25826b = MAKE_CODE_OBJECT(module_filename_obj, 60, CO_GENERATOR | CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[198], mod_consts[198], mod_consts[216], NULL, 0, 0, 0);
    code_objects_84336ce5a4222a6d216dfad8579142cb = MAKE_CODE_OBJECT(module_filename_obj, 55, CO_GENERATOR | CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[195], mod_consts[195], mod_consts[216], NULL, 0, 0, 0);
    code_objects_176b0d6761461dd1b73c1c6755e3a385 = MAKE_CODE_OBJECT(module_filename_obj, 65, CO_GENERATOR | CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[200], mod_consts[200], mod_consts[216], NULL, 0, 0, 0);
    code_objects_08ae733c9c6ae412f7e5d03217c4342d = MAKE_CODE_OBJECT(module_filename_obj, 43, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[192], mod_consts[192], mod_consts[217], NULL, 1, 0, 0);
}
#endif

// The module function declarations.
static PyObject *MAKE_GENERATOR_pygments$plugin$$36$$$36$$$36$function__2_find_plugin_lexers$$36$$$36$$$36$genobj__1_find_plugin_lexers(PyThreadState *tstate);


static PyObject *MAKE_GENERATOR_pygments$plugin$$36$$$36$$$36$function__3_find_plugin_formatters$$36$$$36$$$36$genobj__1_find_plugin_formatters(PyThreadState *tstate);


static PyObject *MAKE_GENERATOR_pygments$plugin$$36$$$36$$$36$function__4_find_plugin_styles$$36$$$36$$$36$genobj__1_find_plugin_styles(PyThreadState *tstate);


static PyObject *MAKE_GENERATOR_pygments$plugin$$36$$$36$$$36$function__5_find_plugin_filters$$36$$$36$$$36$genobj__1_find_plugin_filters(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_pygments$plugin$$36$$$36$$$36$function__2_find_plugin_lexers(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_pygments$plugin$$36$$$36$$$36$function__3_find_plugin_formatters(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_pygments$plugin$$36$$$36$$$36$function__4_find_plugin_styles(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_pygments$plugin$$36$$$36$$$36$function__5_find_plugin_filters(PyThreadState *tstate);


// The module function definitions.
static PyObject *impl_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_group_name = python_pars[0];
    PyObject *var_groups = NULL;
    PyObject *tmp_selectable_groups_class;
    PyObject *tmp_entry_points_class;
    PyObject *tmp_entry_point_class;
    int tmp_res;
    struct Nuitka_FrameObject *frame_frame_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    PyObject *tmp_return_value = NULL;
    static struct Nuitka_FrameObject *cache_frame_frame_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;

    // Actual function body.
    {
        PyObject *tmp_assign_source_1;
        PyObject *tmp_selectable_group_dict_1;
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        PyObject *tmp_selectable_group_dict_2;
        PyObject *tmp_tuple_element_1;
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_selectable_groups_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[0]);
        }
        assert(!(tmp_selectable_groups_class == NULL));
        tmp_dict_key_1 = mod_consts[1];
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_points_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[2]);
        }
        assert(!(tmp_entry_points_class == NULL));
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[4], mod_consts[5], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        tmp_selectable_group_dict_2 = MAKE_TUPLE_EMPTY(tstate, 32);
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 0, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[7], mod_consts[8], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 1, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[9], mod_consts[10], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 2, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[11], mod_consts[12], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 3, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[13], mod_consts[12], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 4, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[14], mod_consts[12], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 5, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[15], mod_consts[16], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 6, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[17], mod_consts[18], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 7, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[19], mod_consts[20], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 8, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[21], mod_consts[22], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 9, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[23], mod_consts[24], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 10, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[25], mod_consts[26], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 11, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[27], mod_consts[28], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 12, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[29], mod_consts[30], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 13, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[31], mod_consts[32], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 14, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[33], mod_consts[34], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 15, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[35], mod_consts[36], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 16, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[37], mod_consts[38], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 17, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[39], mod_consts[40], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 18, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[41], mod_consts[42], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 19, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[43], mod_consts[44], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 20, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[45], mod_consts[46], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 21, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[47], mod_consts[48], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 22, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[49], mod_consts[50], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 23, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[51], mod_consts[52], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 24, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[53], mod_consts[54], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 25, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[55], mod_consts[54], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 26, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[56], mod_consts[57], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 27, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[58], mod_consts[59], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 28, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[60], mod_consts[61], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 29, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[62], mod_consts[63], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 30, tmp_tuple_element_1);
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
        }
        assert(!(tmp_entry_point_class == NULL));
        {
            PyObject *kw_values[3] = {mod_consts[64], mod_consts[65], mod_consts[1]};

            tmp_tuple_element_1 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
        }

        Py_DECREF(tmp_entry_point_class);
        assert(!(tmp_tuple_element_1 == NULL));
        PyTuple_SET_ITEM(tmp_selectable_group_dict_2, 31, tmp_tuple_element_1);
        tmp_dict_value_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_entry_points_class, tmp_selectable_group_dict_2);
        Py_DECREF(tmp_entry_points_class);
        Py_DECREF(tmp_selectable_group_dict_2);
        assert(!(tmp_dict_value_1 == NULL));
        tmp_selectable_group_dict_1 = _PyDict_NewPresized( 14 );
        {
            PyObject *tmp_selectable_group_dict_3;
            PyObject *tmp_tuple_element_2;
            PyObject *tmp_selectable_group_dict_4;
            PyObject *tmp_tuple_element_3;
            PyObject *tmp_selectable_group_dict_5;
            PyObject *tmp_tuple_element_4;
            PyObject *tmp_selectable_group_dict_6;
            PyObject *tmp_tuple_element_5;
            PyObject *tmp_selectable_group_dict_7;
            PyObject *tmp_tuple_element_6;
            PyObject *tmp_selectable_group_dict_8;
            PyObject *tmp_tuple_element_7;
            PyObject *tmp_selectable_group_dict_9;
            PyObject *tmp_tuple_element_8;
            PyObject *tmp_selectable_group_dict_10;
            PyObject *tmp_tuple_element_9;
            PyObject *tmp_selectable_group_dict_11;
            PyObject *tmp_tuple_element_10;
            PyObject *tmp_selectable_group_dict_12;
            PyObject *tmp_tuple_element_11;
            PyObject *tmp_selectable_group_dict_13;
            PyObject *tmp_tuple_element_12;
            PyObject *tmp_selectable_group_dict_14;
            PyObject *tmp_tuple_element_13;
            PyObject *tmp_selectable_group_dict_15;
            PyObject *tmp_tuple_element_14;
            tmp_res = PyDict_SetItem(tmp_selectable_group_dict_1, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[66];
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_points_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[2]);
            }
            assert(!(tmp_entry_points_class == NULL));
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[21], mod_consts[67], mod_consts[66]};

                tmp_tuple_element_2 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_2 == NULL));
            tmp_selectable_group_dict_3 = MAKE_TUPLE_EMPTY(tstate, 1);
            PyTuple_SET_ITEM(tmp_selectable_group_dict_3, 0, tmp_tuple_element_2);
            tmp_dict_value_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_entry_points_class, tmp_selectable_group_dict_3);
            Py_DECREF(tmp_entry_points_class);
            Py_DECREF(tmp_selectable_group_dict_3);
            assert(!(tmp_dict_value_1 == NULL));
            tmp_res = PyDict_SetItem(tmp_selectable_group_dict_1, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[68];
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_points_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[2]);
            }
            assert(!(tmp_entry_points_class == NULL));
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[69], mod_consts[70], mod_consts[68]};

                tmp_tuple_element_3 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_3 == NULL));
            tmp_selectable_group_dict_4 = MAKE_TUPLE_EMPTY(tstate, 3);
            PyTuple_SET_ITEM(tmp_selectable_group_dict_4, 0, tmp_tuple_element_3);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[71], mod_consts[72], mod_consts[68]};

                tmp_tuple_element_3 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_3 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_4, 1, tmp_tuple_element_3);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[73], mod_consts[74], mod_consts[68]};

                tmp_tuple_element_3 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_3 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_4, 2, tmp_tuple_element_3);
            tmp_dict_value_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_entry_points_class, tmp_selectable_group_dict_4);
            Py_DECREF(tmp_entry_points_class);
            Py_DECREF(tmp_selectable_group_dict_4);
            assert(!(tmp_dict_value_1 == NULL));
            tmp_res = PyDict_SetItem(tmp_selectable_group_dict_1, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[75];
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_points_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[2]);
            }
            assert(!(tmp_entry_points_class == NULL));
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[76], mod_consts[77], mod_consts[75]};

                tmp_tuple_element_4 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_4 == NULL));
            tmp_selectable_group_dict_5 = MAKE_TUPLE_EMPTY(tstate, 2);
            PyTuple_SET_ITEM(tmp_selectable_group_dict_5, 0, tmp_tuple_element_4);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[78], mod_consts[79], mod_consts[75]};

                tmp_tuple_element_4 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_4 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_5, 1, tmp_tuple_element_4);
            tmp_dict_value_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_entry_points_class, tmp_selectable_group_dict_5);
            Py_DECREF(tmp_entry_points_class);
            Py_DECREF(tmp_selectable_group_dict_5);
            assert(!(tmp_dict_value_1 == NULL));
            tmp_res = PyDict_SetItem(tmp_selectable_group_dict_1, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[80];
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_points_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[2]);
            }
            assert(!(tmp_entry_points_class == NULL));
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[81], mod_consts[82], mod_consts[80]};

                tmp_tuple_element_5 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_5 == NULL));
            tmp_selectable_group_dict_6 = MAKE_TUPLE_EMPTY(tstate, 1);
            PyTuple_SET_ITEM(tmp_selectable_group_dict_6, 0, tmp_tuple_element_5);
            tmp_dict_value_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_entry_points_class, tmp_selectable_group_dict_6);
            Py_DECREF(tmp_entry_points_class);
            Py_DECREF(tmp_selectable_group_dict_6);
            assert(!(tmp_dict_value_1 == NULL));
            tmp_res = PyDict_SetItem(tmp_selectable_group_dict_1, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[83];
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_points_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[2]);
            }
            assert(!(tmp_entry_points_class == NULL));
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[84], mod_consts[85], mod_consts[83]};

                tmp_tuple_element_6 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_6 == NULL));
            tmp_selectable_group_dict_7 = MAKE_TUPLE_EMPTY(tstate, 6);
            PyTuple_SET_ITEM(tmp_selectable_group_dict_7, 0, tmp_tuple_element_6);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[86], mod_consts[87], mod_consts[83]};

                tmp_tuple_element_6 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_6 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_7, 1, tmp_tuple_element_6);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[88], mod_consts[89], mod_consts[83]};

                tmp_tuple_element_6 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_6 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_7, 2, tmp_tuple_element_6);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[90], mod_consts[91], mod_consts[83]};

                tmp_tuple_element_6 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_6 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_7, 3, tmp_tuple_element_6);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[92], mod_consts[93], mod_consts[83]};

                tmp_tuple_element_6 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_6 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_7, 4, tmp_tuple_element_6);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[94], mod_consts[95], mod_consts[83]};

                tmp_tuple_element_6 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_6 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_7, 5, tmp_tuple_element_6);
            tmp_dict_value_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_entry_points_class, tmp_selectable_group_dict_7);
            Py_DECREF(tmp_entry_points_class);
            Py_DECREF(tmp_selectable_group_dict_7);
            assert(!(tmp_dict_value_1 == NULL));
            tmp_res = PyDict_SetItem(tmp_selectable_group_dict_1, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[96];
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_points_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[2]);
            }
            assert(!(tmp_entry_points_class == NULL));
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[97], mod_consts[98], mod_consts[96]};

                tmp_tuple_element_7 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_7 == NULL));
            tmp_selectable_group_dict_8 = MAKE_TUPLE_EMPTY(tstate, 18);
            PyTuple_SET_ITEM(tmp_selectable_group_dict_8, 0, tmp_tuple_element_7);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[99], mod_consts[100], mod_consts[96]};

                tmp_tuple_element_7 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_7 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_8, 1, tmp_tuple_element_7);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[101], mod_consts[102], mod_consts[96]};

                tmp_tuple_element_7 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_7 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_8, 2, tmp_tuple_element_7);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[103], mod_consts[104], mod_consts[96]};

                tmp_tuple_element_7 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_7 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_8, 3, tmp_tuple_element_7);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[105], mod_consts[106], mod_consts[96]};

                tmp_tuple_element_7 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_7 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_8, 4, tmp_tuple_element_7);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[107], mod_consts[108], mod_consts[96]};

                tmp_tuple_element_7 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_7 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_8, 5, tmp_tuple_element_7);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[109], mod_consts[110], mod_consts[96]};

                tmp_tuple_element_7 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_7 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_8, 6, tmp_tuple_element_7);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[111], mod_consts[112], mod_consts[96]};

                tmp_tuple_element_7 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_7 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_8, 7, tmp_tuple_element_7);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[113], mod_consts[114], mod_consts[96]};

                tmp_tuple_element_7 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_7 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_8, 8, tmp_tuple_element_7);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[115], mod_consts[116], mod_consts[96]};

                tmp_tuple_element_7 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_7 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_8, 9, tmp_tuple_element_7);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[117], mod_consts[118], mod_consts[96]};

                tmp_tuple_element_7 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_7 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_8, 10, tmp_tuple_element_7);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[119], mod_consts[120], mod_consts[96]};

                tmp_tuple_element_7 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_7 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_8, 11, tmp_tuple_element_7);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[121], mod_consts[122], mod_consts[96]};

                tmp_tuple_element_7 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_7 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_8, 12, tmp_tuple_element_7);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[123], mod_consts[124], mod_consts[96]};

                tmp_tuple_element_7 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_7 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_8, 13, tmp_tuple_element_7);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[125], mod_consts[126], mod_consts[96]};

                tmp_tuple_element_7 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_7 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_8, 14, tmp_tuple_element_7);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[127], mod_consts[128], mod_consts[96]};

                tmp_tuple_element_7 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_7 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_8, 15, tmp_tuple_element_7);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[129], mod_consts[130], mod_consts[96]};

                tmp_tuple_element_7 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_7 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_8, 16, tmp_tuple_element_7);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[131], mod_consts[132], mod_consts[96]};

                tmp_tuple_element_7 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_7 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_8, 17, tmp_tuple_element_7);
            tmp_dict_value_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_entry_points_class, tmp_selectable_group_dict_8);
            Py_DECREF(tmp_entry_points_class);
            Py_DECREF(tmp_selectable_group_dict_8);
            assert(!(tmp_dict_value_1 == NULL));
            tmp_res = PyDict_SetItem(tmp_selectable_group_dict_1, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[133];
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_points_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[2]);
            }
            assert(!(tmp_entry_points_class == NULL));
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[134], mod_consts[135], mod_consts[133]};

                tmp_tuple_element_8 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_8 == NULL));
            tmp_selectable_group_dict_9 = MAKE_TUPLE_EMPTY(tstate, 2);
            PyTuple_SET_ITEM(tmp_selectable_group_dict_9, 0, tmp_tuple_element_8);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[136], mod_consts[137], mod_consts[133]};

                tmp_tuple_element_8 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_8 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_9, 1, tmp_tuple_element_8);
            tmp_dict_value_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_entry_points_class, tmp_selectable_group_dict_9);
            Py_DECREF(tmp_entry_points_class);
            Py_DECREF(tmp_selectable_group_dict_9);
            assert(!(tmp_dict_value_1 == NULL));
            tmp_res = PyDict_SetItem(tmp_selectable_group_dict_1, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[138];
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_points_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[2]);
            }
            assert(!(tmp_entry_points_class == NULL));
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[139], mod_consts[140], mod_consts[138]};

                tmp_tuple_element_9 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_9 == NULL));
            tmp_selectable_group_dict_10 = MAKE_TUPLE_EMPTY(tstate, 3);
            PyTuple_SET_ITEM(tmp_selectable_group_dict_10, 0, tmp_tuple_element_9);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[141], mod_consts[142], mod_consts[138]};

                tmp_tuple_element_9 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_9 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_10, 1, tmp_tuple_element_9);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[143], mod_consts[144], mod_consts[138]};

                tmp_tuple_element_9 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_9 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_10, 2, tmp_tuple_element_9);
            tmp_dict_value_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_entry_points_class, tmp_selectable_group_dict_10);
            Py_DECREF(tmp_entry_points_class);
            Py_DECREF(tmp_selectable_group_dict_10);
            assert(!(tmp_dict_value_1 == NULL));
            tmp_res = PyDict_SetItem(tmp_selectable_group_dict_1, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[145];
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_points_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[2]);
            }
            assert(!(tmp_entry_points_class == NULL));
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[4], mod_consts[146], mod_consts[145]};

                tmp_tuple_element_10 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_10 == NULL));
            tmp_selectable_group_dict_11 = MAKE_TUPLE_EMPTY(tstate, 1);
            PyTuple_SET_ITEM(tmp_selectable_group_dict_11, 0, tmp_tuple_element_10);
            tmp_dict_value_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_entry_points_class, tmp_selectable_group_dict_11);
            Py_DECREF(tmp_entry_points_class);
            Py_DECREF(tmp_selectable_group_dict_11);
            assert(!(tmp_dict_value_1 == NULL));
            tmp_res = PyDict_SetItem(tmp_selectable_group_dict_1, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[147];
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_points_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[2]);
            }
            assert(!(tmp_entry_points_class == NULL));
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[148], mod_consts[149], mod_consts[147]};

                tmp_tuple_element_11 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_11 == NULL));
            tmp_selectable_group_dict_12 = MAKE_TUPLE_EMPTY(tstate, 7);
            PyTuple_SET_ITEM(tmp_selectable_group_dict_12, 0, tmp_tuple_element_11);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[150], mod_consts[151], mod_consts[147]};

                tmp_tuple_element_11 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_11 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_12, 1, tmp_tuple_element_11);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[152], mod_consts[153], mod_consts[147]};

                tmp_tuple_element_11 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_11 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_12, 2, tmp_tuple_element_11);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[154], mod_consts[155], mod_consts[147]};

                tmp_tuple_element_11 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_11 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_12, 3, tmp_tuple_element_11);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[156], mod_consts[157], mod_consts[147]};

                tmp_tuple_element_11 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_11 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_12, 4, tmp_tuple_element_11);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[158], mod_consts[159], mod_consts[147]};

                tmp_tuple_element_11 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_11 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_12, 5, tmp_tuple_element_11);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[160], mod_consts[161], mod_consts[147]};

                tmp_tuple_element_11 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_11 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_12, 6, tmp_tuple_element_11);
            tmp_dict_value_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_entry_points_class, tmp_selectable_group_dict_12);
            Py_DECREF(tmp_entry_points_class);
            Py_DECREF(tmp_selectable_group_dict_12);
            assert(!(tmp_dict_value_1 == NULL));
            tmp_res = PyDict_SetItem(tmp_selectable_group_dict_1, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[162];
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_points_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[2]);
            }
            assert(!(tmp_entry_points_class == NULL));
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[163], mod_consts[164], mod_consts[162]};

                tmp_tuple_element_12 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_12 == NULL));
            tmp_selectable_group_dict_13 = MAKE_TUPLE_EMPTY(tstate, 9);
            PyTuple_SET_ITEM(tmp_selectable_group_dict_13, 0, tmp_tuple_element_12);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[165], mod_consts[166], mod_consts[162]};

                tmp_tuple_element_12 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_12 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_13, 1, tmp_tuple_element_12);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[167], mod_consts[168], mod_consts[162]};

                tmp_tuple_element_12 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_12 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_13, 2, tmp_tuple_element_12);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[169], mod_consts[170], mod_consts[162]};

                tmp_tuple_element_12 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_12 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_13, 3, tmp_tuple_element_12);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[171], mod_consts[172], mod_consts[162]};

                tmp_tuple_element_12 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_12 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_13, 4, tmp_tuple_element_12);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[173], mod_consts[174], mod_consts[162]};

                tmp_tuple_element_12 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_12 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_13, 5, tmp_tuple_element_12);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[175], mod_consts[176], mod_consts[162]};

                tmp_tuple_element_12 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_12 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_13, 6, tmp_tuple_element_12);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[177], mod_consts[178], mod_consts[162]};

                tmp_tuple_element_12 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_12 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_13, 7, tmp_tuple_element_12);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[179], mod_consts[180], mod_consts[162]};

                tmp_tuple_element_12 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_12 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_13, 8, tmp_tuple_element_12);
            tmp_dict_value_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_entry_points_class, tmp_selectable_group_dict_13);
            Py_DECREF(tmp_entry_points_class);
            Py_DECREF(tmp_selectable_group_dict_13);
            assert(!(tmp_dict_value_1 == NULL));
            tmp_res = PyDict_SetItem(tmp_selectable_group_dict_1, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[181];
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_points_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[2]);
            }
            assert(!(tmp_entry_points_class == NULL));
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[182], mod_consts[183], mod_consts[181]};

                tmp_tuple_element_13 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_13 == NULL));
            tmp_selectable_group_dict_14 = MAKE_TUPLE_EMPTY(tstate, 1);
            PyTuple_SET_ITEM(tmp_selectable_group_dict_14, 0, tmp_tuple_element_13);
            tmp_dict_value_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_entry_points_class, tmp_selectable_group_dict_14);
            Py_DECREF(tmp_entry_points_class);
            Py_DECREF(tmp_selectable_group_dict_14);
            assert(!(tmp_dict_value_1 == NULL));
            tmp_res = PyDict_SetItem(tmp_selectable_group_dict_1, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[184];
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_points_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[2]);
            }
            assert(!(tmp_entry_points_class == NULL));
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[185], mod_consts[186], mod_consts[184]};

                tmp_tuple_element_14 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_14 == NULL));
            tmp_selectable_group_dict_15 = MAKE_TUPLE_EMPTY(tstate, 2);
            PyTuple_SET_ITEM(tmp_selectable_group_dict_15, 0, tmp_tuple_element_14);
            {
                PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
                tmp_entry_point_class = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[3]);
            }
            assert(!(tmp_entry_point_class == NULL));
            {
                PyObject *kw_values[3] = {mod_consts[187], mod_consts[188], mod_consts[184]};

                tmp_tuple_element_14 = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_entry_point_class, kw_values, mod_consts[6]);
            }

            Py_DECREF(tmp_entry_point_class);
            assert(!(tmp_tuple_element_14 == NULL));
            PyTuple_SET_ITEM(tmp_selectable_group_dict_15, 1, tmp_tuple_element_14);
            tmp_dict_value_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_entry_points_class, tmp_selectable_group_dict_15);
            Py_DECREF(tmp_entry_points_class);
            Py_DECREF(tmp_selectable_group_dict_15);
            assert(!(tmp_dict_value_1 == NULL));
            tmp_res = PyDict_SetItem(tmp_selectable_group_dict_1, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
        }
        tmp_assign_source_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_selectable_groups_class, tmp_selectable_group_dict_1);
        Py_DECREF(tmp_selectable_groups_class);
        Py_DECREF(tmp_selectable_group_dict_1);
        assert(!(tmp_assign_source_1 == NULL));
        assert(var_groups == NULL);
        var_groups = tmp_assign_source_1;
    }
    // Tried code:
    if (isFrameUnusable(cache_frame_frame_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points)) {
        Py_XDECREF(cache_frame_frame_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points = MAKE_FUNCTION_FRAME(tstate, code_objects_08ae733c9c6ae412f7e5d03217c4342d, module_pygments$plugin, sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points->m_type_description == NULL);
    frame_frame_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points = cache_frame_frame_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points);
    assert(Py_REFCNT(frame_frame_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points) == 2);

    // Framed code:
    {
        bool tmp_condition_result_1;
        PyObject *tmp_expression_value_1;
        CHECK_OBJECT(var_groups);
        tmp_expression_value_1 = var_groups;
        tmp_res = HAS_ATTR_BOOL2(tstate, tmp_expression_value_1, mod_consts[189]);
        if (tmp_res == -1) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 45;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        tmp_condition_result_1 = (tmp_res != 0) ? true : false;
        if (tmp_condition_result_1 != false) {
            goto branch_yes_1;
        } else {
            goto branch_no_1;
        }
    }
    branch_yes_1:;
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_expression_value_2;
        PyObject *tmp_kw_call_value_0_1;
        CHECK_OBJECT(var_groups);
        tmp_expression_value_2 = var_groups;
        tmp_called_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_2, mod_consts[189]);
        if (tmp_called_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 48;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_group_name);
        tmp_kw_call_value_0_1 = par_group_name;
        frame_frame_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points->m_frame.f_lineno = 48;
        {
            PyObject *kw_values[1] = {tmp_kw_call_value_0_1};

            tmp_return_value = CALL_FUNCTION_WITH_NO_ARGS_KW_SPLIT(tstate, tmp_called_value_1, kw_values, mod_consts[190]);
        }

        Py_DECREF(tmp_called_value_1);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 48;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        goto frame_return_exit_1;
    }
    goto branch_end_1;
    branch_no_1:;
    {
        PyObject *tmp_called_value_2;
        PyObject *tmp_expression_value_3;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_args_element_value_2;
        CHECK_OBJECT(var_groups);
        tmp_expression_value_3 = var_groups;
        tmp_called_value_2 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_3, mod_consts[191]);
        if (tmp_called_value_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 52;
            type_description_1 = "oo";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_group_name);
        tmp_args_element_value_1 = par_group_name;
        tmp_args_element_value_2 = MAKE_LIST_EMPTY(tstate, 0);
        frame_frame_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points->m_frame.f_lineno = 52;
        {
            PyObject *call_args[] = {tmp_args_element_value_1, tmp_args_element_value_2};
            tmp_return_value = CALL_FUNCTION_WITH_ARGS2(tstate, tmp_called_value_2, call_args);
        }

        Py_DECREF(tmp_called_value_2);
        Py_DECREF(tmp_args_element_value_2);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 52;
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
            exception_tb = MAKE_TRACEBACK(frame_frame_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points,
        type_description_1,
        par_group_name,
        var_groups
    );


    // Release cached frame if used for exception.
    if (frame_frame_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points == cache_frame_frame_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points);
        cache_frame_frame_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points = NULL;
    }

    assertFrameObject(frame_frame_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Return handler code:
    try_return_handler_1:;
    Py_XDECREF(var_groups);
    var_groups = NULL;
    goto function_return_exit;
    // Exception handler code:
    try_except_handler_1:;
    exception_keeper_lineno_1 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_1 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    Py_XDECREF(var_groups);
    var_groups = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_1;
    exception_lineno = exception_keeper_lineno_1;

    goto function_exception_exit;
    // End of try:

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_group_name);
    Py_DECREF(par_group_name);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_group_name);
    Py_DECREF(par_group_name);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_pygments$plugin$$36$$$36$$$36$function__2_find_plugin_lexers(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *tmp_return_value = NULL;

    // Actual function body.


    tmp_return_value = MAKE_GENERATOR_pygments$plugin$$36$$$36$$$36$function__2_find_plugin_lexers$$36$$$36$$$36$genobj__1_find_plugin_lexers(tstate);

    goto function_return_exit;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.


   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}



#if 1
struct pygments$plugin$$36$$$36$$$36$function__2_find_plugin_lexers$$36$$$36$$$36$genobj__1_find_plugin_lexers_locals {
    PyObject *var_entrypoint;
    PyObject *tmp_for_loop_1__for_iterator;
    PyObject *tmp_for_loop_1__iter_value;
    char const *type_description_1;
    struct Nuitka_ExceptionPreservationItem exception_state;
    int exception_lineno;
    char yield_tmps[1024];
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    int exception_keeper_lineno_1;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_2;
    int exception_keeper_lineno_2;
};
#endif

static PyObject *pygments$plugin$$36$$$36$$$36$function__2_find_plugin_lexers$$36$$$36$$$36$genobj__1_find_plugin_lexers_context(PyThreadState *tstate, struct Nuitka_GeneratorObject *generator, PyObject *yield_return_value) {
    CHECK_OBJECT(generator);
    assert(Nuitka_Generator_Check((PyObject *)generator));
    CHECK_OBJECT_X(yield_return_value);

#if 1
    // Heap access.
    struct pygments$plugin$$36$$$36$$$36$function__2_find_plugin_lexers$$36$$$36$$$36$genobj__1_find_plugin_lexers_locals *generator_heap = (struct pygments$plugin$$36$$$36$$$36$function__2_find_plugin_lexers$$36$$$36$$$36$genobj__1_find_plugin_lexers_locals *)generator->m_heap_storage;
#endif

    // Dispatch to yield based on return label index:
    switch(generator->m_yield_return_index) {
    case 1: goto yield_return_1;
    }

    // Local variable initialization
    NUITKA_MAY_BE_UNUSED nuitka_void tmp_unused;
    static struct Nuitka_FrameObject *cache_m_frame = NULL;
    generator_heap->var_entrypoint = NULL;
    generator_heap->tmp_for_loop_1__for_iterator = NULL;
    generator_heap->tmp_for_loop_1__iter_value = NULL;
    generator_heap->type_description_1 = NULL;
    generator_heap->exception_state = Empty_Nuitka_ExceptionPreservationItem;
    generator_heap->exception_lineno = 0;

    // Actual generator function body.
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
        cache_m_frame = MAKE_FUNCTION_FRAME(tstate, code_objects_84336ce5a4222a6d216dfad8579142cb, module_pygments$plugin, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_m_frame->m_type_description == NULL);
    generator->m_frame = cache_m_frame;
    // Mark the frame object as in use, ref count 1 will be up for reuse.
    Py_INCREF(generator->m_frame);
    assert(Py_REFCNT(generator->m_frame) == 2); // Frame stack

    Nuitka_SetFrameGenerator(generator->m_frame, (PyObject *)generator);

    assert(generator->m_frame->m_frame.f_back == NULL);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackGeneratorCompiledFrame(tstate, generator->m_frame);
    assert(Py_REFCNT(generator->m_frame) == 2);

    // Store currently existing exception as the one to publish again when we
    // yield or yield from.
    STORE_GENERATOR_EXCEPTION(tstate, generator);

    // Framed code:
    {
        PyObject *tmp_assign_source_1;
        PyObject *tmp_iter_arg_1;
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        tmp_called_value_1 = module_var_accessor_pygments$$36$plugin$iter_entry_points(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &generator_heap->exception_state, mod_consts[192]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&generator_heap->exception_state));



            generator_heap->exception_lineno = 56;
            generator_heap->type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_args_element_value_1 = module_var_accessor_pygments$$36$plugin$LEXER_ENTRY_POINT(tstate);
        if (unlikely(tmp_args_element_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &generator_heap->exception_state, mod_consts[193]);
        }

        if (tmp_args_element_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&generator_heap->exception_state));



            generator_heap->exception_lineno = 56;
            generator_heap->type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        generator->m_frame->m_frame.f_lineno = 56;
        tmp_iter_arg_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_1, tmp_args_element_value_1);
        if (tmp_iter_arg_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


            generator_heap->exception_lineno = 56;
            generator_heap->type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_assign_source_1 = MAKE_ITERATOR(tstate, tmp_iter_arg_1);
        Py_DECREF(tmp_iter_arg_1);
        if (tmp_assign_source_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


            generator_heap->exception_lineno = 56;
            generator_heap->type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        assert(generator_heap->tmp_for_loop_1__for_iterator == NULL);
        generator_heap->tmp_for_loop_1__for_iterator = tmp_assign_source_1;
    }
    // Tried code:
    loop_start_1:;
    {
        PyObject *tmp_next_source_1;
        PyObject *tmp_assign_source_2;
        CHECK_OBJECT(generator_heap->tmp_for_loop_1__for_iterator);
        tmp_next_source_1 = generator_heap->tmp_for_loop_1__for_iterator;
        tmp_assign_source_2 = ITERATOR_NEXT(tmp_next_source_1);
        if (tmp_assign_source_2 == NULL) {
            if (CHECK_AND_CLEAR_STOP_ITERATION_OCCURRED(tstate)) {

                goto loop_end_1;
            } else {

                FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);
                generator_heap->type_description_1 = "o";
                generator_heap->exception_lineno = 56;
                goto try_except_handler_2;
            }
        }

        {
            PyObject *old = generator_heap->tmp_for_loop_1__iter_value;
            generator_heap->tmp_for_loop_1__iter_value = tmp_assign_source_2;
            Py_XDECREF(old);
        }

    }
    {
        PyObject *tmp_assign_source_3;
        CHECK_OBJECT(generator_heap->tmp_for_loop_1__iter_value);
        tmp_assign_source_3 = generator_heap->tmp_for_loop_1__iter_value;
        {
            PyObject *old = generator_heap->var_entrypoint;
            generator_heap->var_entrypoint = tmp_assign_source_3;
            Py_INCREF(generator_heap->var_entrypoint);
            Py_XDECREF(old);
        }

    }
    {
        PyObject *tmp_expression_value_1;
        PyObject *tmp_called_instance_1;
        NUITKA_MAY_BE_UNUSED PyObject *tmp_yield_result_1;
        CHECK_OBJECT(generator_heap->var_entrypoint);
        tmp_called_instance_1 = generator_heap->var_entrypoint;
        generator->m_frame->m_frame.f_lineno = 57;
        tmp_expression_value_1 = CALL_METHOD_NO_ARGS(tstate, tmp_called_instance_1, mod_consts[194]);
        if (tmp_expression_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


            generator_heap->exception_lineno = 57;
            generator_heap->type_description_1 = "o";
            goto try_except_handler_2;
        }
        Nuitka_PreserveHeap(generator_heap->yield_tmps, &tmp_called_instance_1, sizeof(PyObject *), NULL);
        generator->m_yield_return_index = 1;
        return tmp_expression_value_1;
        yield_return_1:
        Nuitka_RestoreHeap(generator_heap->yield_tmps, &tmp_called_instance_1, sizeof(PyObject *), NULL);
        if (yield_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


            generator_heap->exception_lineno = 57;
            generator_heap->type_description_1 = "o";
            goto try_except_handler_2;
        }
        tmp_yield_result_1 = yield_return_value;
        Py_DECREF(tmp_yield_result_1);
    }
    if (CONSIDER_THREADING(tstate) == false) {
        assert(HAS_ERROR_OCCURRED(tstate));

        FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


        generator_heap->exception_lineno = 56;
        generator_heap->type_description_1 = "o";
        goto try_except_handler_2;
    }
    goto loop_start_1;
    loop_end_1:;
    goto try_end_1;
    // Exception handler code:
    try_except_handler_2:;
    generator_heap->exception_keeper_lineno_1 = generator_heap->exception_lineno;
    generator_heap->exception_lineno = 0;
    generator_heap->exception_keeper_name_1 = generator_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&generator_heap->exception_state);

    Py_XDECREF(generator_heap->tmp_for_loop_1__iter_value);
    generator_heap->tmp_for_loop_1__iter_value = NULL;
    CHECK_OBJECT(generator_heap->tmp_for_loop_1__for_iterator);
    Py_DECREF(generator_heap->tmp_for_loop_1__for_iterator);
    generator_heap->tmp_for_loop_1__for_iterator = NULL;
    // Re-raise.
    generator_heap->exception_state = generator_heap->exception_keeper_name_1;
    generator_heap->exception_lineno = generator_heap->exception_keeper_lineno_1;

    goto frame_exception_exit_1;
    // End of try:
    try_end_1:;

    // Release exception attached to the frame
    DROP_GENERATOR_EXCEPTION(generator);



    goto frame_no_exception_1;
    frame_exception_exit_1:;

    // If it's not an exit exception, consider and create a traceback for it.
    if (!EXCEPTION_STATE_MATCH_GENERATOR(tstate, &generator_heap->exception_state)) {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&generator_heap->exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(generator->m_frame, generator_heap->exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&generator_heap->exception_state, exception_tb);
        } else if ((generator_heap->exception_lineno != 0) && (exception_tb->tb_frame != &generator->m_frame->m_frame)) {
            exception_tb = ADD_TRACEBACK(exception_tb, generator->m_frame, generator_heap->exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&generator_heap->exception_state, exception_tb);
        }

        Nuitka_Frame_AttachLocals(
            generator->m_frame,
            generator_heap->type_description_1,
            generator_heap->var_entrypoint
        );


        // Release cached frame if used for exception.
        if (generator->m_frame == cache_m_frame) {
#if _DEBUG_REFCOUNTS
            count_active_frame_cache_instances -= 1;
            count_released_frame_cache_instances += 1;
#endif

            Py_DECREF(cache_m_frame);
            cache_m_frame = NULL;
        }

        assertFrameObject(generator->m_frame);
    }

    // Release exception attached to the frame
    DROP_GENERATOR_EXCEPTION(generator);


    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    goto try_end_2;
    // Exception handler code:
    try_except_handler_1:;
    generator_heap->exception_keeper_lineno_2 = generator_heap->exception_lineno;
    generator_heap->exception_lineno = 0;
    generator_heap->exception_keeper_name_2 = generator_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&generator_heap->exception_state);

    Py_XDECREF(generator_heap->var_entrypoint);
    generator_heap->var_entrypoint = NULL;
    // Re-raise.
    generator_heap->exception_state = generator_heap->exception_keeper_name_2;
    generator_heap->exception_lineno = generator_heap->exception_keeper_lineno_2;

    goto function_exception_exit;
    // End of try:
    try_end_2:;
    Py_XDECREF(generator_heap->tmp_for_loop_1__iter_value);
    generator_heap->tmp_for_loop_1__iter_value = NULL;
    CHECK_OBJECT(generator_heap->tmp_for_loop_1__for_iterator);
    Py_DECREF(generator_heap->tmp_for_loop_1__for_iterator);
    generator_heap->tmp_for_loop_1__for_iterator = NULL;
    Py_XDECREF(generator_heap->var_entrypoint);
    generator_heap->var_entrypoint = NULL;


    return NULL;

    function_exception_exit:

    CHECK_EXCEPTION_STATE(&generator_heap->exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);

    return NULL;

}

static PyObject *MAKE_GENERATOR_pygments$plugin$$36$$$36$$$36$function__2_find_plugin_lexers$$36$$$36$$$36$genobj__1_find_plugin_lexers(PyThreadState *tstate) {
    return Nuitka_Generator_New(
        pygments$plugin$$36$$$36$$$36$function__2_find_plugin_lexers$$36$$$36$$$36$genobj__1_find_plugin_lexers_context,
        module_pygments$plugin,
        mod_consts[195],
#if PYTHON_VERSION >= 0x350
        NULL,
#endif
        code_objects_84336ce5a4222a6d216dfad8579142cb,
        NULL,
        0,
#if 1
        sizeof(struct pygments$plugin$$36$$$36$$$36$function__2_find_plugin_lexers$$36$$$36$$$36$genobj__1_find_plugin_lexers_locals)
#else
        0
#endif
    );
}


static PyObject *impl_pygments$plugin$$36$$$36$$$36$function__3_find_plugin_formatters(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *tmp_return_value = NULL;

    // Actual function body.


    tmp_return_value = MAKE_GENERATOR_pygments$plugin$$36$$$36$$$36$function__3_find_plugin_formatters$$36$$$36$$$36$genobj__1_find_plugin_formatters(tstate);

    goto function_return_exit;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.


   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}



#if 1
struct pygments$plugin$$36$$$36$$$36$function__3_find_plugin_formatters$$36$$$36$$$36$genobj__1_find_plugin_formatters_locals {
    PyObject *var_entrypoint;
    PyObject *tmp_for_loop_1__for_iterator;
    PyObject *tmp_for_loop_1__iter_value;
    char const *type_description_1;
    struct Nuitka_ExceptionPreservationItem exception_state;
    int exception_lineno;
    char yield_tmps[1024];
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    int exception_keeper_lineno_1;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_2;
    int exception_keeper_lineno_2;
};
#endif

static PyObject *pygments$plugin$$36$$$36$$$36$function__3_find_plugin_formatters$$36$$$36$$$36$genobj__1_find_plugin_formatters_context(PyThreadState *tstate, struct Nuitka_GeneratorObject *generator, PyObject *yield_return_value) {
    CHECK_OBJECT(generator);
    assert(Nuitka_Generator_Check((PyObject *)generator));
    CHECK_OBJECT_X(yield_return_value);

#if 1
    // Heap access.
    struct pygments$plugin$$36$$$36$$$36$function__3_find_plugin_formatters$$36$$$36$$$36$genobj__1_find_plugin_formatters_locals *generator_heap = (struct pygments$plugin$$36$$$36$$$36$function__3_find_plugin_formatters$$36$$$36$$$36$genobj__1_find_plugin_formatters_locals *)generator->m_heap_storage;
#endif

    // Dispatch to yield based on return label index:
    switch(generator->m_yield_return_index) {
    case 1: goto yield_return_1;
    }

    // Local variable initialization
    NUITKA_MAY_BE_UNUSED nuitka_void tmp_unused;
    static struct Nuitka_FrameObject *cache_m_frame = NULL;
    generator_heap->var_entrypoint = NULL;
    generator_heap->tmp_for_loop_1__for_iterator = NULL;
    generator_heap->tmp_for_loop_1__iter_value = NULL;
    generator_heap->type_description_1 = NULL;
    generator_heap->exception_state = Empty_Nuitka_ExceptionPreservationItem;
    generator_heap->exception_lineno = 0;

    // Actual generator function body.
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
        cache_m_frame = MAKE_FUNCTION_FRAME(tstate, code_objects_f123c9c0a67e7b7b8b0f91665e25826b, module_pygments$plugin, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_m_frame->m_type_description == NULL);
    generator->m_frame = cache_m_frame;
    // Mark the frame object as in use, ref count 1 will be up for reuse.
    Py_INCREF(generator->m_frame);
    assert(Py_REFCNT(generator->m_frame) == 2); // Frame stack

    Nuitka_SetFrameGenerator(generator->m_frame, (PyObject *)generator);

    assert(generator->m_frame->m_frame.f_back == NULL);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackGeneratorCompiledFrame(tstate, generator->m_frame);
    assert(Py_REFCNT(generator->m_frame) == 2);

    // Store currently existing exception as the one to publish again when we
    // yield or yield from.
    STORE_GENERATOR_EXCEPTION(tstate, generator);

    // Framed code:
    {
        PyObject *tmp_assign_source_1;
        PyObject *tmp_iter_arg_1;
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        tmp_called_value_1 = module_var_accessor_pygments$$36$plugin$iter_entry_points(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &generator_heap->exception_state, mod_consts[192]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&generator_heap->exception_state));



            generator_heap->exception_lineno = 61;
            generator_heap->type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_args_element_value_1 = module_var_accessor_pygments$$36$plugin$FORMATTER_ENTRY_POINT(tstate);
        if (unlikely(tmp_args_element_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &generator_heap->exception_state, mod_consts[196]);
        }

        if (tmp_args_element_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&generator_heap->exception_state));



            generator_heap->exception_lineno = 61;
            generator_heap->type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        generator->m_frame->m_frame.f_lineno = 61;
        tmp_iter_arg_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_1, tmp_args_element_value_1);
        if (tmp_iter_arg_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


            generator_heap->exception_lineno = 61;
            generator_heap->type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_assign_source_1 = MAKE_ITERATOR(tstate, tmp_iter_arg_1);
        Py_DECREF(tmp_iter_arg_1);
        if (tmp_assign_source_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


            generator_heap->exception_lineno = 61;
            generator_heap->type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        assert(generator_heap->tmp_for_loop_1__for_iterator == NULL);
        generator_heap->tmp_for_loop_1__for_iterator = tmp_assign_source_1;
    }
    // Tried code:
    loop_start_1:;
    {
        PyObject *tmp_next_source_1;
        PyObject *tmp_assign_source_2;
        CHECK_OBJECT(generator_heap->tmp_for_loop_1__for_iterator);
        tmp_next_source_1 = generator_heap->tmp_for_loop_1__for_iterator;
        tmp_assign_source_2 = ITERATOR_NEXT(tmp_next_source_1);
        if (tmp_assign_source_2 == NULL) {
            if (CHECK_AND_CLEAR_STOP_ITERATION_OCCURRED(tstate)) {

                goto loop_end_1;
            } else {

                FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);
                generator_heap->type_description_1 = "o";
                generator_heap->exception_lineno = 61;
                goto try_except_handler_2;
            }
        }

        {
            PyObject *old = generator_heap->tmp_for_loop_1__iter_value;
            generator_heap->tmp_for_loop_1__iter_value = tmp_assign_source_2;
            Py_XDECREF(old);
        }

    }
    {
        PyObject *tmp_assign_source_3;
        CHECK_OBJECT(generator_heap->tmp_for_loop_1__iter_value);
        tmp_assign_source_3 = generator_heap->tmp_for_loop_1__iter_value;
        {
            PyObject *old = generator_heap->var_entrypoint;
            generator_heap->var_entrypoint = tmp_assign_source_3;
            Py_INCREF(generator_heap->var_entrypoint);
            Py_XDECREF(old);
        }

    }
    {
        PyObject *tmp_expression_value_1;
        PyObject *tmp_tuple_element_1;
        PyObject *tmp_expression_value_2;
        NUITKA_MAY_BE_UNUSED PyObject *tmp_yield_result_1;
        CHECK_OBJECT(generator_heap->var_entrypoint);
        tmp_expression_value_2 = generator_heap->var_entrypoint;
        tmp_tuple_element_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_2, mod_consts[197]);
        if (tmp_tuple_element_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


            generator_heap->exception_lineno = 62;
            generator_heap->type_description_1 = "o";
            goto try_except_handler_2;
        }
        tmp_expression_value_1 = MAKE_TUPLE_EMPTY(tstate, 2);
        {
            PyObject *tmp_called_instance_1;
            PyTuple_SET_ITEM(tmp_expression_value_1, 0, tmp_tuple_element_1);
            CHECK_OBJECT(generator_heap->var_entrypoint);
            tmp_called_instance_1 = generator_heap->var_entrypoint;
            generator->m_frame->m_frame.f_lineno = 62;
            tmp_tuple_element_1 = CALL_METHOD_NO_ARGS(tstate, tmp_called_instance_1, mod_consts[194]);
            if (tmp_tuple_element_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


                generator_heap->exception_lineno = 62;
                generator_heap->type_description_1 = "o";
                goto tuple_build_exception_1;
            }
            PyTuple_SET_ITEM(tmp_expression_value_1, 1, tmp_tuple_element_1);
        }
        goto tuple_build_noexception_1;
        // Exception handling pass through code for tuple_build:
        tuple_build_exception_1:;
        Py_DECREF(tmp_expression_value_1);
        goto try_except_handler_2;
        // Finished with no exception for tuple_build:
        tuple_build_noexception_1:;
        Nuitka_PreserveHeap(generator_heap->yield_tmps, &tmp_tuple_element_1, sizeof(PyObject *), &tmp_expression_value_2, sizeof(PyObject *), NULL);
        generator->m_yield_return_index = 1;
        return tmp_expression_value_1;
        yield_return_1:
        Nuitka_RestoreHeap(generator_heap->yield_tmps, &tmp_tuple_element_1, sizeof(PyObject *), &tmp_expression_value_2, sizeof(PyObject *), NULL);
        if (yield_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


            generator_heap->exception_lineno = 62;
            generator_heap->type_description_1 = "o";
            goto try_except_handler_2;
        }
        tmp_yield_result_1 = yield_return_value;
        Py_DECREF(tmp_yield_result_1);
    }
    if (CONSIDER_THREADING(tstate) == false) {
        assert(HAS_ERROR_OCCURRED(tstate));

        FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


        generator_heap->exception_lineno = 61;
        generator_heap->type_description_1 = "o";
        goto try_except_handler_2;
    }
    goto loop_start_1;
    loop_end_1:;
    goto try_end_1;
    // Exception handler code:
    try_except_handler_2:;
    generator_heap->exception_keeper_lineno_1 = generator_heap->exception_lineno;
    generator_heap->exception_lineno = 0;
    generator_heap->exception_keeper_name_1 = generator_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&generator_heap->exception_state);

    Py_XDECREF(generator_heap->tmp_for_loop_1__iter_value);
    generator_heap->tmp_for_loop_1__iter_value = NULL;
    CHECK_OBJECT(generator_heap->tmp_for_loop_1__for_iterator);
    Py_DECREF(generator_heap->tmp_for_loop_1__for_iterator);
    generator_heap->tmp_for_loop_1__for_iterator = NULL;
    // Re-raise.
    generator_heap->exception_state = generator_heap->exception_keeper_name_1;
    generator_heap->exception_lineno = generator_heap->exception_keeper_lineno_1;

    goto frame_exception_exit_1;
    // End of try:
    try_end_1:;

    // Release exception attached to the frame
    DROP_GENERATOR_EXCEPTION(generator);



    goto frame_no_exception_1;
    frame_exception_exit_1:;

    // If it's not an exit exception, consider and create a traceback for it.
    if (!EXCEPTION_STATE_MATCH_GENERATOR(tstate, &generator_heap->exception_state)) {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&generator_heap->exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(generator->m_frame, generator_heap->exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&generator_heap->exception_state, exception_tb);
        } else if ((generator_heap->exception_lineno != 0) && (exception_tb->tb_frame != &generator->m_frame->m_frame)) {
            exception_tb = ADD_TRACEBACK(exception_tb, generator->m_frame, generator_heap->exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&generator_heap->exception_state, exception_tb);
        }

        Nuitka_Frame_AttachLocals(
            generator->m_frame,
            generator_heap->type_description_1,
            generator_heap->var_entrypoint
        );


        // Release cached frame if used for exception.
        if (generator->m_frame == cache_m_frame) {
#if _DEBUG_REFCOUNTS
            count_active_frame_cache_instances -= 1;
            count_released_frame_cache_instances += 1;
#endif

            Py_DECREF(cache_m_frame);
            cache_m_frame = NULL;
        }

        assertFrameObject(generator->m_frame);
    }

    // Release exception attached to the frame
    DROP_GENERATOR_EXCEPTION(generator);


    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    goto try_end_2;
    // Exception handler code:
    try_except_handler_1:;
    generator_heap->exception_keeper_lineno_2 = generator_heap->exception_lineno;
    generator_heap->exception_lineno = 0;
    generator_heap->exception_keeper_name_2 = generator_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&generator_heap->exception_state);

    Py_XDECREF(generator_heap->var_entrypoint);
    generator_heap->var_entrypoint = NULL;
    // Re-raise.
    generator_heap->exception_state = generator_heap->exception_keeper_name_2;
    generator_heap->exception_lineno = generator_heap->exception_keeper_lineno_2;

    goto function_exception_exit;
    // End of try:
    try_end_2:;
    Py_XDECREF(generator_heap->tmp_for_loop_1__iter_value);
    generator_heap->tmp_for_loop_1__iter_value = NULL;
    CHECK_OBJECT(generator_heap->tmp_for_loop_1__for_iterator);
    Py_DECREF(generator_heap->tmp_for_loop_1__for_iterator);
    generator_heap->tmp_for_loop_1__for_iterator = NULL;
    Py_XDECREF(generator_heap->var_entrypoint);
    generator_heap->var_entrypoint = NULL;


    return NULL;

    function_exception_exit:

    CHECK_EXCEPTION_STATE(&generator_heap->exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);

    return NULL;

}

static PyObject *MAKE_GENERATOR_pygments$plugin$$36$$$36$$$36$function__3_find_plugin_formatters$$36$$$36$$$36$genobj__1_find_plugin_formatters(PyThreadState *tstate) {
    return Nuitka_Generator_New(
        pygments$plugin$$36$$$36$$$36$function__3_find_plugin_formatters$$36$$$36$$$36$genobj__1_find_plugin_formatters_context,
        module_pygments$plugin,
        mod_consts[198],
#if PYTHON_VERSION >= 0x350
        NULL,
#endif
        code_objects_f123c9c0a67e7b7b8b0f91665e25826b,
        NULL,
        0,
#if 1
        sizeof(struct pygments$plugin$$36$$$36$$$36$function__3_find_plugin_formatters$$36$$$36$$$36$genobj__1_find_plugin_formatters_locals)
#else
        0
#endif
    );
}


static PyObject *impl_pygments$plugin$$36$$$36$$$36$function__4_find_plugin_styles(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *tmp_return_value = NULL;

    // Actual function body.


    tmp_return_value = MAKE_GENERATOR_pygments$plugin$$36$$$36$$$36$function__4_find_plugin_styles$$36$$$36$$$36$genobj__1_find_plugin_styles(tstate);

    goto function_return_exit;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.


   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}



#if 1
struct pygments$plugin$$36$$$36$$$36$function__4_find_plugin_styles$$36$$$36$$$36$genobj__1_find_plugin_styles_locals {
    PyObject *var_entrypoint;
    PyObject *tmp_for_loop_1__for_iterator;
    PyObject *tmp_for_loop_1__iter_value;
    char const *type_description_1;
    struct Nuitka_ExceptionPreservationItem exception_state;
    int exception_lineno;
    char yield_tmps[1024];
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    int exception_keeper_lineno_1;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_2;
    int exception_keeper_lineno_2;
};
#endif

static PyObject *pygments$plugin$$36$$$36$$$36$function__4_find_plugin_styles$$36$$$36$$$36$genobj__1_find_plugin_styles_context(PyThreadState *tstate, struct Nuitka_GeneratorObject *generator, PyObject *yield_return_value) {
    CHECK_OBJECT(generator);
    assert(Nuitka_Generator_Check((PyObject *)generator));
    CHECK_OBJECT_X(yield_return_value);

#if 1
    // Heap access.
    struct pygments$plugin$$36$$$36$$$36$function__4_find_plugin_styles$$36$$$36$$$36$genobj__1_find_plugin_styles_locals *generator_heap = (struct pygments$plugin$$36$$$36$$$36$function__4_find_plugin_styles$$36$$$36$$$36$genobj__1_find_plugin_styles_locals *)generator->m_heap_storage;
#endif

    // Dispatch to yield based on return label index:
    switch(generator->m_yield_return_index) {
    case 1: goto yield_return_1;
    }

    // Local variable initialization
    NUITKA_MAY_BE_UNUSED nuitka_void tmp_unused;
    static struct Nuitka_FrameObject *cache_m_frame = NULL;
    generator_heap->var_entrypoint = NULL;
    generator_heap->tmp_for_loop_1__for_iterator = NULL;
    generator_heap->tmp_for_loop_1__iter_value = NULL;
    generator_heap->type_description_1 = NULL;
    generator_heap->exception_state = Empty_Nuitka_ExceptionPreservationItem;
    generator_heap->exception_lineno = 0;

    // Actual generator function body.
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
        cache_m_frame = MAKE_FUNCTION_FRAME(tstate, code_objects_176b0d6761461dd1b73c1c6755e3a385, module_pygments$plugin, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_m_frame->m_type_description == NULL);
    generator->m_frame = cache_m_frame;
    // Mark the frame object as in use, ref count 1 will be up for reuse.
    Py_INCREF(generator->m_frame);
    assert(Py_REFCNT(generator->m_frame) == 2); // Frame stack

    Nuitka_SetFrameGenerator(generator->m_frame, (PyObject *)generator);

    assert(generator->m_frame->m_frame.f_back == NULL);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackGeneratorCompiledFrame(tstate, generator->m_frame);
    assert(Py_REFCNT(generator->m_frame) == 2);

    // Store currently existing exception as the one to publish again when we
    // yield or yield from.
    STORE_GENERATOR_EXCEPTION(tstate, generator);

    // Framed code:
    {
        PyObject *tmp_assign_source_1;
        PyObject *tmp_iter_arg_1;
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        tmp_called_value_1 = module_var_accessor_pygments$$36$plugin$iter_entry_points(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &generator_heap->exception_state, mod_consts[192]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&generator_heap->exception_state));



            generator_heap->exception_lineno = 66;
            generator_heap->type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_args_element_value_1 = module_var_accessor_pygments$$36$plugin$STYLE_ENTRY_POINT(tstate);
        if (unlikely(tmp_args_element_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &generator_heap->exception_state, mod_consts[199]);
        }

        if (tmp_args_element_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&generator_heap->exception_state));



            generator_heap->exception_lineno = 66;
            generator_heap->type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        generator->m_frame->m_frame.f_lineno = 66;
        tmp_iter_arg_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_1, tmp_args_element_value_1);
        if (tmp_iter_arg_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


            generator_heap->exception_lineno = 66;
            generator_heap->type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_assign_source_1 = MAKE_ITERATOR(tstate, tmp_iter_arg_1);
        Py_DECREF(tmp_iter_arg_1);
        if (tmp_assign_source_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


            generator_heap->exception_lineno = 66;
            generator_heap->type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        assert(generator_heap->tmp_for_loop_1__for_iterator == NULL);
        generator_heap->tmp_for_loop_1__for_iterator = tmp_assign_source_1;
    }
    // Tried code:
    loop_start_1:;
    {
        PyObject *tmp_next_source_1;
        PyObject *tmp_assign_source_2;
        CHECK_OBJECT(generator_heap->tmp_for_loop_1__for_iterator);
        tmp_next_source_1 = generator_heap->tmp_for_loop_1__for_iterator;
        tmp_assign_source_2 = ITERATOR_NEXT(tmp_next_source_1);
        if (tmp_assign_source_2 == NULL) {
            if (CHECK_AND_CLEAR_STOP_ITERATION_OCCURRED(tstate)) {

                goto loop_end_1;
            } else {

                FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);
                generator_heap->type_description_1 = "o";
                generator_heap->exception_lineno = 66;
                goto try_except_handler_2;
            }
        }

        {
            PyObject *old = generator_heap->tmp_for_loop_1__iter_value;
            generator_heap->tmp_for_loop_1__iter_value = tmp_assign_source_2;
            Py_XDECREF(old);
        }

    }
    {
        PyObject *tmp_assign_source_3;
        CHECK_OBJECT(generator_heap->tmp_for_loop_1__iter_value);
        tmp_assign_source_3 = generator_heap->tmp_for_loop_1__iter_value;
        {
            PyObject *old = generator_heap->var_entrypoint;
            generator_heap->var_entrypoint = tmp_assign_source_3;
            Py_INCREF(generator_heap->var_entrypoint);
            Py_XDECREF(old);
        }

    }
    {
        PyObject *tmp_expression_value_1;
        PyObject *tmp_tuple_element_1;
        PyObject *tmp_expression_value_2;
        NUITKA_MAY_BE_UNUSED PyObject *tmp_yield_result_1;
        CHECK_OBJECT(generator_heap->var_entrypoint);
        tmp_expression_value_2 = generator_heap->var_entrypoint;
        tmp_tuple_element_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_2, mod_consts[197]);
        if (tmp_tuple_element_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


            generator_heap->exception_lineno = 67;
            generator_heap->type_description_1 = "o";
            goto try_except_handler_2;
        }
        tmp_expression_value_1 = MAKE_TUPLE_EMPTY(tstate, 2);
        {
            PyObject *tmp_called_instance_1;
            PyTuple_SET_ITEM(tmp_expression_value_1, 0, tmp_tuple_element_1);
            CHECK_OBJECT(generator_heap->var_entrypoint);
            tmp_called_instance_1 = generator_heap->var_entrypoint;
            generator->m_frame->m_frame.f_lineno = 67;
            tmp_tuple_element_1 = CALL_METHOD_NO_ARGS(tstate, tmp_called_instance_1, mod_consts[194]);
            if (tmp_tuple_element_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


                generator_heap->exception_lineno = 67;
                generator_heap->type_description_1 = "o";
                goto tuple_build_exception_1;
            }
            PyTuple_SET_ITEM(tmp_expression_value_1, 1, tmp_tuple_element_1);
        }
        goto tuple_build_noexception_1;
        // Exception handling pass through code for tuple_build:
        tuple_build_exception_1:;
        Py_DECREF(tmp_expression_value_1);
        goto try_except_handler_2;
        // Finished with no exception for tuple_build:
        tuple_build_noexception_1:;
        Nuitka_PreserveHeap(generator_heap->yield_tmps, &tmp_tuple_element_1, sizeof(PyObject *), &tmp_expression_value_2, sizeof(PyObject *), NULL);
        generator->m_yield_return_index = 1;
        return tmp_expression_value_1;
        yield_return_1:
        Nuitka_RestoreHeap(generator_heap->yield_tmps, &tmp_tuple_element_1, sizeof(PyObject *), &tmp_expression_value_2, sizeof(PyObject *), NULL);
        if (yield_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


            generator_heap->exception_lineno = 67;
            generator_heap->type_description_1 = "o";
            goto try_except_handler_2;
        }
        tmp_yield_result_1 = yield_return_value;
        Py_DECREF(tmp_yield_result_1);
    }
    if (CONSIDER_THREADING(tstate) == false) {
        assert(HAS_ERROR_OCCURRED(tstate));

        FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


        generator_heap->exception_lineno = 66;
        generator_heap->type_description_1 = "o";
        goto try_except_handler_2;
    }
    goto loop_start_1;
    loop_end_1:;
    goto try_end_1;
    // Exception handler code:
    try_except_handler_2:;
    generator_heap->exception_keeper_lineno_1 = generator_heap->exception_lineno;
    generator_heap->exception_lineno = 0;
    generator_heap->exception_keeper_name_1 = generator_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&generator_heap->exception_state);

    Py_XDECREF(generator_heap->tmp_for_loop_1__iter_value);
    generator_heap->tmp_for_loop_1__iter_value = NULL;
    CHECK_OBJECT(generator_heap->tmp_for_loop_1__for_iterator);
    Py_DECREF(generator_heap->tmp_for_loop_1__for_iterator);
    generator_heap->tmp_for_loop_1__for_iterator = NULL;
    // Re-raise.
    generator_heap->exception_state = generator_heap->exception_keeper_name_1;
    generator_heap->exception_lineno = generator_heap->exception_keeper_lineno_1;

    goto frame_exception_exit_1;
    // End of try:
    try_end_1:;

    // Release exception attached to the frame
    DROP_GENERATOR_EXCEPTION(generator);



    goto frame_no_exception_1;
    frame_exception_exit_1:;

    // If it's not an exit exception, consider and create a traceback for it.
    if (!EXCEPTION_STATE_MATCH_GENERATOR(tstate, &generator_heap->exception_state)) {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&generator_heap->exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(generator->m_frame, generator_heap->exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&generator_heap->exception_state, exception_tb);
        } else if ((generator_heap->exception_lineno != 0) && (exception_tb->tb_frame != &generator->m_frame->m_frame)) {
            exception_tb = ADD_TRACEBACK(exception_tb, generator->m_frame, generator_heap->exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&generator_heap->exception_state, exception_tb);
        }

        Nuitka_Frame_AttachLocals(
            generator->m_frame,
            generator_heap->type_description_1,
            generator_heap->var_entrypoint
        );


        // Release cached frame if used for exception.
        if (generator->m_frame == cache_m_frame) {
#if _DEBUG_REFCOUNTS
            count_active_frame_cache_instances -= 1;
            count_released_frame_cache_instances += 1;
#endif

            Py_DECREF(cache_m_frame);
            cache_m_frame = NULL;
        }

        assertFrameObject(generator->m_frame);
    }

    // Release exception attached to the frame
    DROP_GENERATOR_EXCEPTION(generator);


    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    goto try_end_2;
    // Exception handler code:
    try_except_handler_1:;
    generator_heap->exception_keeper_lineno_2 = generator_heap->exception_lineno;
    generator_heap->exception_lineno = 0;
    generator_heap->exception_keeper_name_2 = generator_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&generator_heap->exception_state);

    Py_XDECREF(generator_heap->var_entrypoint);
    generator_heap->var_entrypoint = NULL;
    // Re-raise.
    generator_heap->exception_state = generator_heap->exception_keeper_name_2;
    generator_heap->exception_lineno = generator_heap->exception_keeper_lineno_2;

    goto function_exception_exit;
    // End of try:
    try_end_2:;
    Py_XDECREF(generator_heap->tmp_for_loop_1__iter_value);
    generator_heap->tmp_for_loop_1__iter_value = NULL;
    CHECK_OBJECT(generator_heap->tmp_for_loop_1__for_iterator);
    Py_DECREF(generator_heap->tmp_for_loop_1__for_iterator);
    generator_heap->tmp_for_loop_1__for_iterator = NULL;
    Py_XDECREF(generator_heap->var_entrypoint);
    generator_heap->var_entrypoint = NULL;


    return NULL;

    function_exception_exit:

    CHECK_EXCEPTION_STATE(&generator_heap->exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);

    return NULL;

}

static PyObject *MAKE_GENERATOR_pygments$plugin$$36$$$36$$$36$function__4_find_plugin_styles$$36$$$36$$$36$genobj__1_find_plugin_styles(PyThreadState *tstate) {
    return Nuitka_Generator_New(
        pygments$plugin$$36$$$36$$$36$function__4_find_plugin_styles$$36$$$36$$$36$genobj__1_find_plugin_styles_context,
        module_pygments$plugin,
        mod_consts[200],
#if PYTHON_VERSION >= 0x350
        NULL,
#endif
        code_objects_176b0d6761461dd1b73c1c6755e3a385,
        NULL,
        0,
#if 1
        sizeof(struct pygments$plugin$$36$$$36$$$36$function__4_find_plugin_styles$$36$$$36$$$36$genobj__1_find_plugin_styles_locals)
#else
        0
#endif
    );
}


static PyObject *impl_pygments$plugin$$36$$$36$$$36$function__5_find_plugin_filters(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *tmp_return_value = NULL;

    // Actual function body.


    tmp_return_value = MAKE_GENERATOR_pygments$plugin$$36$$$36$$$36$function__5_find_plugin_filters$$36$$$36$$$36$genobj__1_find_plugin_filters(tstate);

    goto function_return_exit;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.


   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}



#if 1
struct pygments$plugin$$36$$$36$$$36$function__5_find_plugin_filters$$36$$$36$$$36$genobj__1_find_plugin_filters_locals {
    PyObject *var_entrypoint;
    PyObject *tmp_for_loop_1__for_iterator;
    PyObject *tmp_for_loop_1__iter_value;
    char const *type_description_1;
    struct Nuitka_ExceptionPreservationItem exception_state;
    int exception_lineno;
    char yield_tmps[1024];
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    int exception_keeper_lineno_1;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_2;
    int exception_keeper_lineno_2;
};
#endif

static PyObject *pygments$plugin$$36$$$36$$$36$function__5_find_plugin_filters$$36$$$36$$$36$genobj__1_find_plugin_filters_context(PyThreadState *tstate, struct Nuitka_GeneratorObject *generator, PyObject *yield_return_value) {
    CHECK_OBJECT(generator);
    assert(Nuitka_Generator_Check((PyObject *)generator));
    CHECK_OBJECT_X(yield_return_value);

#if 1
    // Heap access.
    struct pygments$plugin$$36$$$36$$$36$function__5_find_plugin_filters$$36$$$36$$$36$genobj__1_find_plugin_filters_locals *generator_heap = (struct pygments$plugin$$36$$$36$$$36$function__5_find_plugin_filters$$36$$$36$$$36$genobj__1_find_plugin_filters_locals *)generator->m_heap_storage;
#endif

    // Dispatch to yield based on return label index:
    switch(generator->m_yield_return_index) {
    case 1: goto yield_return_1;
    }

    // Local variable initialization
    NUITKA_MAY_BE_UNUSED nuitka_void tmp_unused;
    static struct Nuitka_FrameObject *cache_m_frame = NULL;
    generator_heap->var_entrypoint = NULL;
    generator_heap->tmp_for_loop_1__for_iterator = NULL;
    generator_heap->tmp_for_loop_1__iter_value = NULL;
    generator_heap->type_description_1 = NULL;
    generator_heap->exception_state = Empty_Nuitka_ExceptionPreservationItem;
    generator_heap->exception_lineno = 0;

    // Actual generator function body.
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
        cache_m_frame = MAKE_FUNCTION_FRAME(tstate, code_objects_2e34d522e2f73478237594a44c21fbc1, module_pygments$plugin, sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_m_frame->m_type_description == NULL);
    generator->m_frame = cache_m_frame;
    // Mark the frame object as in use, ref count 1 will be up for reuse.
    Py_INCREF(generator->m_frame);
    assert(Py_REFCNT(generator->m_frame) == 2); // Frame stack

    Nuitka_SetFrameGenerator(generator->m_frame, (PyObject *)generator);

    assert(generator->m_frame->m_frame.f_back == NULL);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackGeneratorCompiledFrame(tstate, generator->m_frame);
    assert(Py_REFCNT(generator->m_frame) == 2);

    // Store currently existing exception as the one to publish again when we
    // yield or yield from.
    STORE_GENERATOR_EXCEPTION(tstate, generator);

    // Framed code:
    {
        PyObject *tmp_assign_source_1;
        PyObject *tmp_iter_arg_1;
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        tmp_called_value_1 = module_var_accessor_pygments$$36$plugin$iter_entry_points(tstate);
        if (unlikely(tmp_called_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &generator_heap->exception_state, mod_consts[192]);
        }

        if (tmp_called_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&generator_heap->exception_state));



            generator_heap->exception_lineno = 71;
            generator_heap->type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_args_element_value_1 = module_var_accessor_pygments$$36$plugin$FILTER_ENTRY_POINT(tstate);
        if (unlikely(tmp_args_element_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &generator_heap->exception_state, mod_consts[201]);
        }

        if (tmp_args_element_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&generator_heap->exception_state));



            generator_heap->exception_lineno = 71;
            generator_heap->type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        generator->m_frame->m_frame.f_lineno = 71;
        tmp_iter_arg_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_1, tmp_args_element_value_1);
        if (tmp_iter_arg_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


            generator_heap->exception_lineno = 71;
            generator_heap->type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        tmp_assign_source_1 = MAKE_ITERATOR(tstate, tmp_iter_arg_1);
        Py_DECREF(tmp_iter_arg_1);
        if (tmp_assign_source_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


            generator_heap->exception_lineno = 71;
            generator_heap->type_description_1 = "o";
            goto frame_exception_exit_1;
        }
        assert(generator_heap->tmp_for_loop_1__for_iterator == NULL);
        generator_heap->tmp_for_loop_1__for_iterator = tmp_assign_source_1;
    }
    // Tried code:
    loop_start_1:;
    {
        PyObject *tmp_next_source_1;
        PyObject *tmp_assign_source_2;
        CHECK_OBJECT(generator_heap->tmp_for_loop_1__for_iterator);
        tmp_next_source_1 = generator_heap->tmp_for_loop_1__for_iterator;
        tmp_assign_source_2 = ITERATOR_NEXT(tmp_next_source_1);
        if (tmp_assign_source_2 == NULL) {
            if (CHECK_AND_CLEAR_STOP_ITERATION_OCCURRED(tstate)) {

                goto loop_end_1;
            } else {

                FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);
                generator_heap->type_description_1 = "o";
                generator_heap->exception_lineno = 71;
                goto try_except_handler_2;
            }
        }

        {
            PyObject *old = generator_heap->tmp_for_loop_1__iter_value;
            generator_heap->tmp_for_loop_1__iter_value = tmp_assign_source_2;
            Py_XDECREF(old);
        }

    }
    {
        PyObject *tmp_assign_source_3;
        CHECK_OBJECT(generator_heap->tmp_for_loop_1__iter_value);
        tmp_assign_source_3 = generator_heap->tmp_for_loop_1__iter_value;
        {
            PyObject *old = generator_heap->var_entrypoint;
            generator_heap->var_entrypoint = tmp_assign_source_3;
            Py_INCREF(generator_heap->var_entrypoint);
            Py_XDECREF(old);
        }

    }
    {
        PyObject *tmp_expression_value_1;
        PyObject *tmp_tuple_element_1;
        PyObject *tmp_expression_value_2;
        NUITKA_MAY_BE_UNUSED PyObject *tmp_yield_result_1;
        CHECK_OBJECT(generator_heap->var_entrypoint);
        tmp_expression_value_2 = generator_heap->var_entrypoint;
        tmp_tuple_element_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_2, mod_consts[197]);
        if (tmp_tuple_element_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


            generator_heap->exception_lineno = 72;
            generator_heap->type_description_1 = "o";
            goto try_except_handler_2;
        }
        tmp_expression_value_1 = MAKE_TUPLE_EMPTY(tstate, 2);
        {
            PyObject *tmp_called_instance_1;
            PyTuple_SET_ITEM(tmp_expression_value_1, 0, tmp_tuple_element_1);
            CHECK_OBJECT(generator_heap->var_entrypoint);
            tmp_called_instance_1 = generator_heap->var_entrypoint;
            generator->m_frame->m_frame.f_lineno = 72;
            tmp_tuple_element_1 = CALL_METHOD_NO_ARGS(tstate, tmp_called_instance_1, mod_consts[194]);
            if (tmp_tuple_element_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


                generator_heap->exception_lineno = 72;
                generator_heap->type_description_1 = "o";
                goto tuple_build_exception_1;
            }
            PyTuple_SET_ITEM(tmp_expression_value_1, 1, tmp_tuple_element_1);
        }
        goto tuple_build_noexception_1;
        // Exception handling pass through code for tuple_build:
        tuple_build_exception_1:;
        Py_DECREF(tmp_expression_value_1);
        goto try_except_handler_2;
        // Finished with no exception for tuple_build:
        tuple_build_noexception_1:;
        Nuitka_PreserveHeap(generator_heap->yield_tmps, &tmp_tuple_element_1, sizeof(PyObject *), &tmp_expression_value_2, sizeof(PyObject *), NULL);
        generator->m_yield_return_index = 1;
        return tmp_expression_value_1;
        yield_return_1:
        Nuitka_RestoreHeap(generator_heap->yield_tmps, &tmp_tuple_element_1, sizeof(PyObject *), &tmp_expression_value_2, sizeof(PyObject *), NULL);
        if (yield_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


            generator_heap->exception_lineno = 72;
            generator_heap->type_description_1 = "o";
            goto try_except_handler_2;
        }
        tmp_yield_result_1 = yield_return_value;
        Py_DECREF(tmp_yield_result_1);
    }
    if (CONSIDER_THREADING(tstate) == false) {
        assert(HAS_ERROR_OCCURRED(tstate));

        FETCH_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);


        generator_heap->exception_lineno = 71;
        generator_heap->type_description_1 = "o";
        goto try_except_handler_2;
    }
    goto loop_start_1;
    loop_end_1:;
    goto try_end_1;
    // Exception handler code:
    try_except_handler_2:;
    generator_heap->exception_keeper_lineno_1 = generator_heap->exception_lineno;
    generator_heap->exception_lineno = 0;
    generator_heap->exception_keeper_name_1 = generator_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&generator_heap->exception_state);

    Py_XDECREF(generator_heap->tmp_for_loop_1__iter_value);
    generator_heap->tmp_for_loop_1__iter_value = NULL;
    CHECK_OBJECT(generator_heap->tmp_for_loop_1__for_iterator);
    Py_DECREF(generator_heap->tmp_for_loop_1__for_iterator);
    generator_heap->tmp_for_loop_1__for_iterator = NULL;
    // Re-raise.
    generator_heap->exception_state = generator_heap->exception_keeper_name_1;
    generator_heap->exception_lineno = generator_heap->exception_keeper_lineno_1;

    goto frame_exception_exit_1;
    // End of try:
    try_end_1:;

    // Release exception attached to the frame
    DROP_GENERATOR_EXCEPTION(generator);



    goto frame_no_exception_1;
    frame_exception_exit_1:;

    // If it's not an exit exception, consider and create a traceback for it.
    if (!EXCEPTION_STATE_MATCH_GENERATOR(tstate, &generator_heap->exception_state)) {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&generator_heap->exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(generator->m_frame, generator_heap->exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&generator_heap->exception_state, exception_tb);
        } else if ((generator_heap->exception_lineno != 0) && (exception_tb->tb_frame != &generator->m_frame->m_frame)) {
            exception_tb = ADD_TRACEBACK(exception_tb, generator->m_frame, generator_heap->exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&generator_heap->exception_state, exception_tb);
        }

        Nuitka_Frame_AttachLocals(
            generator->m_frame,
            generator_heap->type_description_1,
            generator_heap->var_entrypoint
        );


        // Release cached frame if used for exception.
        if (generator->m_frame == cache_m_frame) {
#if _DEBUG_REFCOUNTS
            count_active_frame_cache_instances -= 1;
            count_released_frame_cache_instances += 1;
#endif

            Py_DECREF(cache_m_frame);
            cache_m_frame = NULL;
        }

        assertFrameObject(generator->m_frame);
    }

    // Release exception attached to the frame
    DROP_GENERATOR_EXCEPTION(generator);


    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    goto try_end_2;
    // Exception handler code:
    try_except_handler_1:;
    generator_heap->exception_keeper_lineno_2 = generator_heap->exception_lineno;
    generator_heap->exception_lineno = 0;
    generator_heap->exception_keeper_name_2 = generator_heap->exception_state;
    INIT_ERROR_OCCURRED_STATE(&generator_heap->exception_state);

    Py_XDECREF(generator_heap->var_entrypoint);
    generator_heap->var_entrypoint = NULL;
    // Re-raise.
    generator_heap->exception_state = generator_heap->exception_keeper_name_2;
    generator_heap->exception_lineno = generator_heap->exception_keeper_lineno_2;

    goto function_exception_exit;
    // End of try:
    try_end_2:;
    Py_XDECREF(generator_heap->tmp_for_loop_1__iter_value);
    generator_heap->tmp_for_loop_1__iter_value = NULL;
    CHECK_OBJECT(generator_heap->tmp_for_loop_1__for_iterator);
    Py_DECREF(generator_heap->tmp_for_loop_1__for_iterator);
    generator_heap->tmp_for_loop_1__for_iterator = NULL;
    Py_XDECREF(generator_heap->var_entrypoint);
    generator_heap->var_entrypoint = NULL;


    return NULL;

    function_exception_exit:

    CHECK_EXCEPTION_STATE(&generator_heap->exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &generator_heap->exception_state);

    return NULL;

}

static PyObject *MAKE_GENERATOR_pygments$plugin$$36$$$36$$$36$function__5_find_plugin_filters$$36$$$36$$$36$genobj__1_find_plugin_filters(PyThreadState *tstate) {
    return Nuitka_Generator_New(
        pygments$plugin$$36$$$36$$$36$function__5_find_plugin_filters$$36$$$36$$$36$genobj__1_find_plugin_filters_context,
        module_pygments$plugin,
        mod_consts[202],
#if PYTHON_VERSION >= 0x350
        NULL,
#endif
        code_objects_2e34d522e2f73478237594a44c21fbc1,
        NULL,
        0,
#if 1
        sizeof(struct pygments$plugin$$36$$$36$$$36$function__5_find_plugin_filters$$36$$$36$$$36$genobj__1_find_plugin_filters_locals)
#else
        0
#endif
    );
}



static PyObject *MAKE_FUNCTION_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points,
        mod_consts[192],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_08ae733c9c6ae412f7e5d03217c4342d,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_pygments$plugin,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_pygments$plugin$$36$$$36$$$36$function__2_find_plugin_lexers(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_pygments$plugin$$36$$$36$$$36$function__2_find_plugin_lexers,
        mod_consts[195],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_84336ce5a4222a6d216dfad8579142cb,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_pygments$plugin,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_pygments$plugin$$36$$$36$$$36$function__3_find_plugin_formatters(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_pygments$plugin$$36$$$36$$$36$function__3_find_plugin_formatters,
        mod_consts[198],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_f123c9c0a67e7b7b8b0f91665e25826b,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_pygments$plugin,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_pygments$plugin$$36$$$36$$$36$function__4_find_plugin_styles(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_pygments$plugin$$36$$$36$$$36$function__4_find_plugin_styles,
        mod_consts[200],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_176b0d6761461dd1b73c1c6755e3a385,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_pygments$plugin,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_pygments$plugin$$36$$$36$$$36$function__5_find_plugin_filters(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_pygments$plugin$$36$$$36$$$36$function__5_find_plugin_filters,
        mod_consts[202],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_2e34d522e2f73478237594a44c21fbc1,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_pygments$plugin,
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

static function_impl_code const function_table_pygments$plugin[] = {
    impl_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points,
    impl_pygments$plugin$$36$$$36$$$36$function__2_find_plugin_lexers,
    impl_pygments$plugin$$36$$$36$$$36$function__3_find_plugin_formatters,
    impl_pygments$plugin$$36$$$36$$$36$function__4_find_plugin_styles,
    impl_pygments$plugin$$36$$$36$$$36$function__5_find_plugin_filters,
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

    return Nuitka_Function_GetFunctionState(function, function_table_pygments$plugin);
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
        module_pygments$plugin,
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
        function_table_pygments$plugin,
        sizeof(function_table_pygments$plugin) / sizeof(function_impl_code)
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
static char const *module_full_name = "pygments.plugin";
#endif

// Internal entry point for module code.
PyObject *modulecode_pygments$plugin(PyThreadState *tstate, PyObject *module, struct Nuitka_MetaPathBasedLoaderEntry const *loader_entry) {
    // Report entry to PGO.
    PGO_onModuleEntered("pygments$plugin");

    // Store the module for future use.
    module_pygments$plugin = module;

    moduledict_pygments$plugin = MODULE_DICT(module_pygments$plugin);

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
        PRINT_STRING("pygments$plugin: Calling setupMetaPathBasedLoader().\n");
#endif
        setupMetaPathBasedLoader(tstate);
#if 0 >= 0
#ifdef _NUITKA_TRACE
        PRINT_STRING("pygments$plugin: Calling updateMetaPathBasedLoaderModuleRoot().\n");
#endif
        updateMetaPathBasedLoaderModuleRoot(module_full_name);
#endif


#if PYTHON_VERSION >= 0x300
        patchInspectModule(tstate);
#endif

#endif

        /* The constants only used by this module are created now. */
        NUITKA_PRINT_TRACE("pygments$plugin: Calling createModuleConstants().\n");
        createModuleConstants(tstate);

#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
        createModuleCodeObjects();
#endif
        init_done = true;
    }

#if _NUITKA_MODULE_MODE && 0
    PyObject *pre_load = IMPORT_EMBEDDED_MODULE(tstate, "pygments.plugin" "-preLoad");
    if (pre_load == NULL) {
        return NULL;
    }
#endif

    // PRINT_STRING("in initpygments$plugin\n");

#ifdef _NUITKA_PLUGIN_DILL_ENABLED
    {
        char const *module_name_c;
        if (loader_entry != NULL) {
            module_name_c = loader_entry->name;
        } else {
            PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)const_str_plain___name__);
            module_name_c = Nuitka_String_AsString(module_name);
        }

        registerDillPluginTables(tstate, module_name_c, &_method_def_reduce_compiled_function, &_method_def_create_compiled_function);
    }
#endif

    // Set "__compiled__" to what version information we have.
    UPDATE_STRING_DICT0(
        moduledict_pygments$plugin,
        (Nuitka_StringObject *)const_str_plain___compiled__,
        Nuitka_dunder_compiled_value
    );

    // Update "__package__" value to what it ought to be.
    {
#if 0
        UPDATE_STRING_DICT0(
            moduledict_pygments$plugin,
            (Nuitka_StringObject *)const_str_plain___package__,
            mod_consts[218]
        );
#elif 0
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)const_str_plain___name__);

        UPDATE_STRING_DICT0(
            moduledict_pygments$plugin,
            (Nuitka_StringObject *)const_str_plain___package__,
            module_name
        );
#else

#if PYTHON_VERSION < 0x300
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)const_str_plain___name__);
        char const *module_name_cstr = PyString_AS_STRING(module_name);

        char const *last_dot = strrchr(module_name_cstr, '.');

        if (last_dot != NULL) {
            UPDATE_STRING_DICT1(
                moduledict_pygments$plugin,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyString_FromStringAndSize(module_name_cstr, last_dot - module_name_cstr)
            );
        }
#else
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)const_str_plain___name__);
        Py_ssize_t dot_index = PyUnicode_Find(module_name, const_str_dot, 0, PyUnicode_GetLength(module_name), -1);

        if (dot_index != -1) {
            UPDATE_STRING_DICT1(
                moduledict_pygments$plugin,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyUnicode_Substring(module_name, 0, dot_index)
            );
        }
#endif
#endif
    }

    CHECK_OBJECT(module_pygments$plugin);

    // For deep importing of a module we need to have "__builtins__", so we set
    // it ourselves in the same way than CPython does. Note: This must be done
    // before the frame object is allocated, or else it may fail.

    if (GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)const_str_plain___builtins__) == NULL) {
        PyObject *value = (PyObject *)builtin_module;

        // Check if main module, not a dict then but the module itself.
#if _NUITKA_MODULE_MODE || !0
        value = PyModule_GetDict(value);
#endif

        UPDATE_STRING_DICT0(moduledict_pygments$plugin, (Nuitka_StringObject *)const_str_plain___builtins__, value);
    }

    PyObject *module_loader = Nuitka_Loader_New(loader_entry);
    UPDATE_STRING_DICT0(moduledict_pygments$plugin, (Nuitka_StringObject *)const_str_plain___loader__, module_loader);

#if PYTHON_VERSION >= 0x300
// Set the "__spec__" value

#if 0
    // Main modules just get "None" as spec.
    UPDATE_STRING_DICT0(moduledict_pygments$plugin, (Nuitka_StringObject *)const_str_plain___spec__, Py_None);
#else
    // Other modules get a "ModuleSpec" from the standard mechanism.
    {
        PyObject *bootstrap_module = getImportLibBootstrapModule();
        CHECK_OBJECT(bootstrap_module);

        PyObject *_spec_from_module = PyObject_GetAttrString(bootstrap_module, "_spec_from_module");
        CHECK_OBJECT(_spec_from_module);

        PyObject *spec_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, _spec_from_module, module_pygments$plugin);
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

        UPDATE_STRING_DICT1(moduledict_pygments$plugin, (Nuitka_StringObject *)const_str_plain___spec__, spec_value);
    }
#endif
#endif

    // Temp variables if any
    struct Nuitka_FrameObject *frame_frame_pygments$plugin;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    bool tmp_result;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;

    // Module init code if any


    // Module code.
    {
        PyObject *tmp_assign_source_1;
        tmp_assign_source_1 = mod_consts[203];
        UPDATE_STRING_DICT0(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[204], tmp_assign_source_1);
    }
    {
        PyObject *tmp_assign_source_2;
        tmp_assign_source_2 = module_filename_obj;
        UPDATE_STRING_DICT0(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[205], tmp_assign_source_2);
    }
    frame_frame_pygments$plugin = MAKE_MODULE_FRAME(code_objects_ebe3fc16cc6109fce68be05c0d37c541, module_pygments$plugin);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_pygments$plugin);
    assert(Py_REFCNT(frame_frame_pygments$plugin) == 2);

    // Framed code:
    {
        PyObject *tmp_assattr_value_1;
        PyObject *tmp_assattr_target_1;
        tmp_assattr_value_1 = module_filename_obj;
        tmp_assattr_target_1 = module_var_accessor_pygments$$36$plugin$__spec__(tstate);
        assert(!(tmp_assattr_target_1 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_1, mod_consts[206], tmp_assattr_value_1);
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
        tmp_assattr_target_2 = module_var_accessor_pygments$$36$plugin$__spec__(tstate);
        assert(!(tmp_assattr_target_2 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_2, mod_consts[207], tmp_assattr_value_2);
        if (tmp_result == false) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 1;

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
            exception_tb = MAKE_TRACEBACK(frame_frame_pygments$plugin, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_pygments$plugin->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_pygments$plugin, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }



    assertFrameObject(frame_frame_pygments$plugin);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto module_exception_exit;
    frame_no_exception_1:;
    {
        PyObject *tmp_assign_source_3;
        tmp_assign_source_3 = Py_None;
        UPDATE_STRING_DICT0(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[208], tmp_assign_source_3);
    }
    {
        PyObject *tmp_assign_source_4;
        {
            PyObject *hard_module = IMPORT_HARD_IMPORTLIB__METADATA();
            tmp_assign_source_4 = LOOKUP_ATTRIBUTE(tstate, hard_module, mod_consts[209]);
        }
        assert(!(tmp_assign_source_4 == NULL));
        UPDATE_STRING_DICT1(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[209], tmp_assign_source_4);
    }
    {
        PyObject *tmp_assign_source_5;
        tmp_assign_source_5 = mod_consts[210];
        UPDATE_STRING_DICT0(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[193], tmp_assign_source_5);
    }
    {
        PyObject *tmp_assign_source_6;
        tmp_assign_source_6 = mod_consts[211];
        UPDATE_STRING_DICT0(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[196], tmp_assign_source_6);
    }
    {
        PyObject *tmp_assign_source_7;
        tmp_assign_source_7 = mod_consts[212];
        UPDATE_STRING_DICT0(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[199], tmp_assign_source_7);
    }
    {
        PyObject *tmp_assign_source_8;
        tmp_assign_source_8 = mod_consts[213];
        UPDATE_STRING_DICT0(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[201], tmp_assign_source_8);
    }
    {
        PyObject *tmp_assign_source_9;


        tmp_assign_source_9 = MAKE_FUNCTION_pygments$plugin$$36$$$36$$$36$function__1_iter_entry_points(tstate);

        UPDATE_STRING_DICT1(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[192], tmp_assign_source_9);
    }
    {
        PyObject *tmp_assign_source_10;


        tmp_assign_source_10 = MAKE_FUNCTION_pygments$plugin$$36$$$36$$$36$function__2_find_plugin_lexers(tstate);

        UPDATE_STRING_DICT1(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[195], tmp_assign_source_10);
    }
    {
        PyObject *tmp_assign_source_11;


        tmp_assign_source_11 = MAKE_FUNCTION_pygments$plugin$$36$$$36$$$36$function__3_find_plugin_formatters(tstate);

        UPDATE_STRING_DICT1(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[198], tmp_assign_source_11);
    }
    {
        PyObject *tmp_assign_source_12;


        tmp_assign_source_12 = MAKE_FUNCTION_pygments$plugin$$36$$$36$$$36$function__4_find_plugin_styles(tstate);

        UPDATE_STRING_DICT1(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[200], tmp_assign_source_12);
    }
    {
        PyObject *tmp_assign_source_13;


        tmp_assign_source_13 = MAKE_FUNCTION_pygments$plugin$$36$$$36$$$36$function__5_find_plugin_filters(tstate);

        UPDATE_STRING_DICT1(moduledict_pygments$plugin, (Nuitka_StringObject *)mod_consts[202], tmp_assign_source_13);
    }

    // Report to PGO about leaving the module without error.
    PGO_onModuleExit("pygments$plugin", false);

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *post_load = IMPORT_EMBEDDED_MODULE(tstate, "pygments.plugin" "-postLoad");
        if (post_load == NULL) {
            return NULL;
        }
    }
#endif

    Py_INCREF(module_pygments$plugin);
    return module_pygments$plugin;
    module_exception_exit:

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_pygments$plugin, (Nuitka_StringObject *)const_str_plain___name__);

        if (module_name != NULL) {
            Nuitka_DelModule(tstate, module_name);
        }
    }
#endif
    PGO_onModuleExit("pygments$plugin", false);

    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);
    return NULL;
}
