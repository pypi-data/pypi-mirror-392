/* Generated code for Python module 'bs4$_deprecation'
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

/* The "module_bs4$_deprecation" is a Python object pointer of module type.
 *
 * Note: For full compatibility with CPython, every module variable access
 * needs to go through it except for cases where the module cannot possibly
 * have changed in the mean time.
 */

PyObject *module_bs4$_deprecation;
PyDictObject *moduledict_bs4$_deprecation;

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
        loadConstantsBlob(tstate, &mod_consts[0], UN_TRANSLATE("bs4._deprecation"));
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
void checkModuleConstants_bs4$_deprecation(PyThreadState *tstate) {
    // The module may not have been used at all, then ignore this.
    if (constants_created == false) return;

    for (int i = 0; i < 58; i++) {
        assert(mod_consts_hash[i] == DEEP_HASH(tstate, mod_consts[i]));
        CHECK_OBJECT_DEEP(mod_consts[i]);
    }
}
#endif

// Helper to preserving module variables for Python3.11+
#if 5
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
static PyObject *module_var_accessor_bs4$$36$_deprecation$Any(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_bs4$_deprecation->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_bs4$_deprecation->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[1]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_bs4$_deprecation->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[1]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[1]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[1]);
    }

    return result;
}

static PyObject *module_var_accessor_bs4$$36$_deprecation$Callable(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_bs4$_deprecation->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_bs4$_deprecation->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[26]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_bs4$_deprecation->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[26]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[26]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[26]);
    }

    return result;
}

static PyObject *module_var_accessor_bs4$$36$_deprecation$DeprecationWarning(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_bs4$_deprecation->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_bs4$_deprecation->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[18]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_bs4$_deprecation->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[18]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[18]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[18]);
    }

    return result;
}

static PyObject *module_var_accessor_bs4$$36$_deprecation$__spec__(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_bs4$_deprecation->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_bs4$_deprecation->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[57]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_bs4$_deprecation->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[57]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[57]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[57]);
    }

    return result;
}

static PyObject *module_var_accessor_bs4$$36$_deprecation$warnings(PyThreadState *tstate) {
#if 1
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_bs4$_deprecation->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_bs4$_deprecation->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[8]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_bs4$_deprecation->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[8]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[8]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[8]);
    }

    return result;
}


#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
// The module code objects.
static PyCodeObject *code_objects_bf290a46c2257bddeb5bc0e9a9fba6aa;
static PyCodeObject *code_objects_cb3dbea03ab50ab74dece3da876841f1;
static PyCodeObject *code_objects_a6234e2d240c1443fc7156c4e8b18d24;
static PyCodeObject *code_objects_95858e4d4a80ba4b0ae59dce6edf650a;
static PyCodeObject *code_objects_cfd3d698b014c3be85c33bd7381c389e;
static PyCodeObject *code_objects_1a76f189cfe03fe170485beaad95e4df;
static PyCodeObject *code_objects_03042f7654d982f910de4f1341aad7fb;
static PyCodeObject *code_objects_026cb297a34658f48abf1d75eab043f8;
static PyCodeObject *code_objects_54ccb6b959c4b8cd845850120f4f910a;

static void createModuleCodeObjects(void) {
    module_filename_obj = MAKE_RELATIVE_PATH(mod_consts[45]); CHECK_OBJECT(module_filename_obj);
    code_objects_bf290a46c2257bddeb5bc0e9a9fba6aa = MAKE_CODE_OBJECT(module_filename_obj, 1, CO_NOFREE, mod_consts[46], mod_consts[46], NULL, NULL, 0, 0, 0);
    code_objects_cb3dbea03ab50ab74dece3da876841f1 = MAKE_CODE_OBJECT(module_filename_obj, 66, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[44], mod_consts[44], mod_consts[47], NULL, 2, 0, 0);
    code_objects_a6234e2d240c1443fc7156c4e8b18d24 = MAKE_CODE_OBJECT(module_filename_obj, 22, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[42], mod_consts[42], mod_consts[48], NULL, 3, 0, 0);
    code_objects_95858e4d4a80ba4b0ae59dce6edf650a = MAKE_CODE_OBJECT(module_filename_obj, 51, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[43], mod_consts[43], mod_consts[48], NULL, 3, 0, 0);
    code_objects_cfd3d698b014c3be85c33bd7381c389e = MAKE_CODE_OBJECT(module_filename_obj, 29, CO_OPTIMIZED | CO_NEWLOCALS, mod_consts[3], mod_consts[4], mod_consts[49], mod_consts[50], 1, 0, 0);
    code_objects_1a76f189cfe03fe170485beaad95e4df = MAKE_CODE_OBJECT(module_filename_obj, 39, CO_OPTIMIZED | CO_NEWLOCALS, mod_consts[3], mod_consts[4], mod_consts[51], mod_consts[50], 2, 0, 0);
    code_objects_03042f7654d982f910de4f1341aad7fb = MAKE_CODE_OBJECT(module_filename_obj, 54, CO_OPTIMIZED | CO_NEWLOCALS | CO_VARARGS | CO_VARKEYWORDS, mod_consts[3], mod_consts[23], mod_consts[52], mod_consts[50], 1, 0, 0);
    code_objects_026cb297a34658f48abf1d75eab043f8 = MAKE_CODE_OBJECT(module_filename_obj, 67, CO_OPTIMIZED | CO_NEWLOCALS, mod_consts[27], mod_consts[28], mod_consts[53], mod_consts[54], 1, 0, 0);
    code_objects_54ccb6b959c4b8cd845850120f4f910a = MAKE_CODE_OBJECT(module_filename_obj, 69, CO_OPTIMIZED | CO_NEWLOCALS | CO_VARARGS | CO_VARKEYWORDS, mod_consts[30], mod_consts[31], mod_consts[55], mod_consts[56], 0, 0, 0);
}
#endif

// The module function declarations.
NUITKA_CROSS_MODULE PyObject *impl___main__$$36$$$36$$$36$helper_function_complex_call_helper_star_list_star_dict(PyThreadState *tstate, PyObject **python_pars);


static PyObject *MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias(PyThreadState *tstate, PyObject *annotations);


static PyObject *MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias(PyThreadState *tstate, PyObject *annotations, struct Nuitka_CellObject **closure);


static PyObject *MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias(PyThreadState *tstate, PyObject *annotations, struct Nuitka_CellObject **closure);


static PyObject *MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias(PyThreadState *tstate, PyObject *annotations);


static PyObject *MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias(PyThreadState *tstate, PyObject *annotations, struct Nuitka_CellObject **closure);


static PyObject *MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated(PyThreadState *tstate, PyObject *annotations);


static PyObject *MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate(PyThreadState *tstate, PyObject *annotations, struct Nuitka_CellObject **closure);


static PyObject *MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning(PyThreadState *tstate, PyObject *annotations, struct Nuitka_CellObject **closure);


// The module function definitions.
static PyObject *impl_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    struct Nuitka_CellObject *par_old_name = Nuitka_Cell_New1(python_pars[0]);
    struct Nuitka_CellObject *par_new_name = Nuitka_Cell_New1(python_pars[1]);
    struct Nuitka_CellObject *par_version = Nuitka_Cell_New1(python_pars[2]);
    PyObject *var_alias = NULL;
    struct Nuitka_FrameObject *frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    int tmp_res;
    static struct Nuitka_FrameObject *cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;

    // Actual function body.
    // Tried code:
    if (isFrameUnusable(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias)) {
        Py_XDECREF(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias = MAKE_FUNCTION_FRAME(tstate, code_objects_a6234e2d240c1443fc7156c4e8b18d24, module_bs4$_deprecation, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias->m_type_description == NULL);
    frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias = cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias);
    assert(Py_REFCNT(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias) == 2);

    // Framed code:
    {
        PyObject *tmp_assign_source_1;
        PyObject *tmp_called_value_1;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_annotations_1;
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        struct Nuitka_CellObject *tmp_closure_1[3];
        tmp_called_value_1 = (PyObject *)&PyProperty_Type;
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = module_var_accessor_bs4$$36$_deprecation$Any(tstate);
        if (unlikely(tmp_dict_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[1]);
        }

        if (tmp_dict_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 29;
            type_description_1 = "ccco";
            goto frame_exception_exit_1;
        }
        tmp_annotations_1 = _PyDict_NewPresized( 1 );
        tmp_res = PyDict_SetItem(tmp_annotations_1, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));

        tmp_closure_1[0] = par_new_name;
        Py_INCREF(tmp_closure_1[0]);
        tmp_closure_1[1] = par_old_name;
        Py_INCREF(tmp_closure_1[1]);
        tmp_closure_1[2] = par_version;
        Py_INCREF(tmp_closure_1[2]);

        tmp_args_element_value_1 = MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias(tstate, tmp_annotations_1, tmp_closure_1);

        frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias->m_frame.f_lineno = 28;
        tmp_assign_source_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_1, tmp_args_element_value_1);
        Py_DECREF(tmp_args_element_value_1);
        if (tmp_assign_source_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 28;
            type_description_1 = "ccco";
            goto frame_exception_exit_1;
        }
        assert(var_alias == NULL);
        var_alias = tmp_assign_source_1;
    }
    {
        PyObject *tmp_assign_source_2;
        PyObject *tmp_called_instance_1;
        PyObject *tmp_args_element_value_2;
        PyObject *tmp_annotations_2;
        struct Nuitka_CellObject *tmp_closure_2[3];
        CHECK_OBJECT(var_alias);
        tmp_called_instance_1 = var_alias;
        tmp_annotations_2 = DICT_COPY(tstate, mod_consts[6]);

        tmp_closure_2[0] = par_new_name;
        Py_INCREF(tmp_closure_2[0]);
        tmp_closure_2[1] = par_old_name;
        Py_INCREF(tmp_closure_2[1]);
        tmp_closure_2[2] = par_version;
        Py_INCREF(tmp_closure_2[2]);

        tmp_args_element_value_2 = MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias(tstate, tmp_annotations_2, tmp_closure_2);

        frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias->m_frame.f_lineno = 38;
        tmp_assign_source_2 = CALL_METHOD_WITH_SINGLE_ARG(tstate, tmp_called_instance_1, mod_consts[5], tmp_args_element_value_2);
        Py_DECREF(tmp_args_element_value_2);
        if (tmp_assign_source_2 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 38;
            type_description_1 = "ccco";
            goto frame_exception_exit_1;
        }
        {
            PyObject *old = var_alias;
            assert(old != NULL);
            var_alias = tmp_assign_source_2;
            Py_DECREF(old);
        }

    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias,
        type_description_1,
        par_old_name,
        par_new_name,
        par_version,
        var_alias
    );


    // Release cached frame if used for exception.
    if (frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias == cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias);
        cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias = NULL;
    }

    assertFrameObject(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    CHECK_OBJECT(var_alias);
    tmp_return_value = var_alias;
    Py_INCREF(tmp_return_value);
    goto try_return_handler_1;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Return handler code:
    try_return_handler_1:;
    CHECK_OBJECT(var_alias);
    Py_DECREF(var_alias);
    var_alias = NULL;
    goto function_return_exit;
    // Exception handler code:
    try_except_handler_1:;
    exception_keeper_lineno_1 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_1 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    Py_XDECREF(var_alias);
    var_alias = NULL;
    // Re-raise.
    exception_state = exception_keeper_name_1;
    exception_lineno = exception_keeper_lineno_1;

    goto function_exception_exit;
    // End of try:

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_old_name);
    Py_DECREF(par_old_name);
    CHECK_OBJECT(par_new_name);
    Py_DECREF(par_new_name);
    CHECK_OBJECT(par_version);
    Py_DECREF(par_version);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_old_name);
    Py_DECREF(par_old_name);
    CHECK_OBJECT(par_new_name);
    Py_DECREF(par_new_name);
    CHECK_OBJECT(par_version);
    Py_DECREF(par_version);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    struct Nuitka_FrameObject *frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    NUITKA_MAY_BE_UNUSED nuitka_void tmp_unused;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    PyObject *tmp_return_value = NULL;
    static struct Nuitka_FrameObject *cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias)) {
        Py_XDECREF(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias = MAKE_FUNCTION_FRAME(tstate, code_objects_cfd3d698b014c3be85c33bd7381c389e, module_bs4$_deprecation, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias->m_type_description == NULL);
    frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias = cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias);
    assert(Py_REFCNT(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_expression_value_1;
        PyObject *tmp_call_result_1;
        PyObject *tmp_args_value_1;
        PyObject *tmp_tuple_element_1;
        PyObject *tmp_string_concat_values_1;
        PyObject *tmp_tuple_element_2;
        PyObject *tmp_kwargs_value_1;
        tmp_expression_value_1 = module_var_accessor_bs4$$36$_deprecation$warnings(tstate);
        if (unlikely(tmp_expression_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[8]);
        }

        if (tmp_expression_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 31;
            type_description_1 = "occc";
            goto frame_exception_exit_1;
        }
        tmp_called_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[9]);
        if (tmp_called_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 31;
            type_description_1 = "occc";
            goto frame_exception_exit_1;
        }
        tmp_tuple_element_2 = mod_consts[10];
        tmp_string_concat_values_1 = MAKE_TUPLE_EMPTY(tstate, 7);
        {
            PyObject *tmp_format_value_1;
            PyObject *tmp_format_spec_1;
            PyObject *tmp_format_value_2;
            PyObject *tmp_format_spec_2;
            PyObject *tmp_format_value_3;
            PyObject *tmp_format_spec_3;
            PyTuple_SET_ITEM0(tmp_string_concat_values_1, 0, tmp_tuple_element_2);
            if (Nuitka_Cell_GET(self->m_closure[1]) == NULL) {

                FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[11]);
                NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
                CHAIN_EXCEPTION(tstate, exception_state.exception_value);

                exception_lineno = 32;
                type_description_1 = "occc";
                goto tuple_build_exception_1;
            }

            tmp_format_value_1 = Nuitka_Cell_GET(self->m_closure[1]);
            tmp_format_spec_1 = mod_consts[12];
            tmp_tuple_element_2 = BUILTIN_FORMAT(tstate, tmp_format_value_1, tmp_format_spec_1);
            if (tmp_tuple_element_2 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 32;
                type_description_1 = "occc";
                goto tuple_build_exception_1;
            }
            PyTuple_SET_ITEM(tmp_string_concat_values_1, 1, tmp_tuple_element_2);
            tmp_tuple_element_2 = mod_consts[13];
            PyTuple_SET_ITEM0(tmp_string_concat_values_1, 2, tmp_tuple_element_2);
            if (Nuitka_Cell_GET(self->m_closure[0]) == NULL) {

                FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[14]);
                NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
                CHAIN_EXCEPTION(tstate, exception_state.exception_value);

                exception_lineno = 32;
                type_description_1 = "occc";
                goto tuple_build_exception_1;
            }

            tmp_format_value_2 = Nuitka_Cell_GET(self->m_closure[0]);
            tmp_format_spec_2 = mod_consts[12];
            tmp_tuple_element_2 = BUILTIN_FORMAT(tstate, tmp_format_value_2, tmp_format_spec_2);
            if (tmp_tuple_element_2 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 32;
                type_description_1 = "occc";
                goto tuple_build_exception_1;
            }
            PyTuple_SET_ITEM(tmp_string_concat_values_1, 3, tmp_tuple_element_2);
            tmp_tuple_element_2 = mod_consts[15];
            PyTuple_SET_ITEM0(tmp_string_concat_values_1, 4, tmp_tuple_element_2);
            if (Nuitka_Cell_GET(self->m_closure[2]) == NULL) {

                FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[16]);
                NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
                CHAIN_EXCEPTION(tstate, exception_state.exception_value);

                exception_lineno = 32;
                type_description_1 = "occc";
                goto tuple_build_exception_1;
            }

            tmp_format_value_3 = Nuitka_Cell_GET(self->m_closure[2]);
            tmp_format_spec_3 = mod_consts[12];
            tmp_tuple_element_2 = BUILTIN_FORMAT(tstate, tmp_format_value_3, tmp_format_spec_3);
            if (tmp_tuple_element_2 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 32;
                type_description_1 = "occc";
                goto tuple_build_exception_1;
            }
            PyTuple_SET_ITEM(tmp_string_concat_values_1, 5, tmp_tuple_element_2);
            tmp_tuple_element_2 = mod_consts[17];
            PyTuple_SET_ITEM0(tmp_string_concat_values_1, 6, tmp_tuple_element_2);
        }
        goto tuple_build_noexception_1;
        // Exception handling pass through code for tuple_build:
        tuple_build_exception_1:;
        Py_DECREF(tmp_called_value_1);
        Py_DECREF(tmp_string_concat_values_1);
        goto frame_exception_exit_1;
        // Finished with no exception for tuple_build:
        tuple_build_noexception_1:;
        tmp_tuple_element_1 = PyUnicode_Join(mod_consts[12], tmp_string_concat_values_1);
        Py_DECREF(tmp_string_concat_values_1);
        if (tmp_tuple_element_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_called_value_1);

            exception_lineno = 32;
            type_description_1 = "occc";
            goto frame_exception_exit_1;
        }
        tmp_args_value_1 = MAKE_TUPLE_EMPTY(tstate, 2);
        PyTuple_SET_ITEM(tmp_args_value_1, 0, tmp_tuple_element_1);
        tmp_tuple_element_1 = module_var_accessor_bs4$$36$_deprecation$DeprecationWarning(tstate);
        if (unlikely(tmp_tuple_element_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[18]);
        }

        if (tmp_tuple_element_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 33;
            type_description_1 = "occc";
            goto tuple_build_exception_2;
        }
        PyTuple_SET_ITEM0(tmp_args_value_1, 1, tmp_tuple_element_1);
        goto tuple_build_noexception_2;
        // Exception handling pass through code for tuple_build:
        tuple_build_exception_2:;
        Py_DECREF(tmp_called_value_1);
        Py_DECREF(tmp_args_value_1);
        goto frame_exception_exit_1;
        // Finished with no exception for tuple_build:
        tuple_build_noexception_2:;
        tmp_kwargs_value_1 = DICT_COPY(tstate, mod_consts[19]);
        frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias->m_frame.f_lineno = 31;
        tmp_call_result_1 = CALL_FUNCTION(tstate, tmp_called_value_1, tmp_args_value_1, tmp_kwargs_value_1);
        Py_DECREF(tmp_called_value_1);
        Py_DECREF(tmp_args_value_1);
        Py_DECREF(tmp_kwargs_value_1);
        if (tmp_call_result_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 31;
            type_description_1 = "occc";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_1);
    }
    {
        PyObject *tmp_expression_value_2;
        PyObject *tmp_name_value_1;
        CHECK_OBJECT(par_self);
        tmp_expression_value_2 = par_self;
        if (Nuitka_Cell_GET(self->m_closure[0]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[14]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 36;
            type_description_1 = "occc";
            goto frame_exception_exit_1;
        }

        tmp_name_value_1 = Nuitka_Cell_GET(self->m_closure[0]);
        tmp_return_value = BUILTIN_GETATTR(tstate, tmp_expression_value_2, tmp_name_value_1, NULL);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 36;
            type_description_1 = "occc";
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
            exception_tb = MAKE_TRACEBACK(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias,
        type_description_1,
        par_self,
        self->m_closure[1],
        self->m_closure[0],
        self->m_closure[2]
    );


    // Release cached frame if used for exception.
    if (frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias == cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias);
        cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias = NULL;
    }

    assertFrameObject(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_value = python_pars[1];
    struct Nuitka_FrameObject *frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    NUITKA_MAY_BE_UNUSED nuitka_void tmp_unused;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    PyObject *tmp_return_value = NULL;
    static struct Nuitka_FrameObject *cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias)) {
        Py_XDECREF(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias = MAKE_FUNCTION_FRAME(tstate, code_objects_1a76f189cfe03fe170485beaad95e4df, module_bs4$_deprecation, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias->m_type_description == NULL);
    frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias = cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias);
    assert(Py_REFCNT(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_expression_value_1;
        PyObject *tmp_call_result_1;
        PyObject *tmp_args_value_1;
        PyObject *tmp_tuple_element_1;
        PyObject *tmp_string_concat_values_1;
        PyObject *tmp_tuple_element_2;
        PyObject *tmp_kwargs_value_1;
        tmp_expression_value_1 = module_var_accessor_bs4$$36$_deprecation$warnings(tstate);
        if (unlikely(tmp_expression_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[8]);
        }

        if (tmp_expression_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 41;
            type_description_1 = "ooccc";
            goto frame_exception_exit_1;
        }
        tmp_called_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[9]);
        if (tmp_called_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 41;
            type_description_1 = "ooccc";
            goto frame_exception_exit_1;
        }
        tmp_tuple_element_2 = mod_consts[20];
        tmp_string_concat_values_1 = MAKE_TUPLE_EMPTY(tstate, 7);
        {
            PyObject *tmp_format_value_1;
            PyObject *tmp_format_spec_1;
            PyObject *tmp_format_value_2;
            PyObject *tmp_format_spec_2;
            PyObject *tmp_format_value_3;
            PyObject *tmp_format_spec_3;
            PyTuple_SET_ITEM0(tmp_string_concat_values_1, 0, tmp_tuple_element_2);
            if (Nuitka_Cell_GET(self->m_closure[1]) == NULL) {

                FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[11]);
                NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
                CHAIN_EXCEPTION(tstate, exception_state.exception_value);

                exception_lineno = 42;
                type_description_1 = "ooccc";
                goto tuple_build_exception_1;
            }

            tmp_format_value_1 = Nuitka_Cell_GET(self->m_closure[1]);
            tmp_format_spec_1 = mod_consts[12];
            tmp_tuple_element_2 = BUILTIN_FORMAT(tstate, tmp_format_value_1, tmp_format_spec_1);
            if (tmp_tuple_element_2 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 42;
                type_description_1 = "ooccc";
                goto tuple_build_exception_1;
            }
            PyTuple_SET_ITEM(tmp_string_concat_values_1, 1, tmp_tuple_element_2);
            tmp_tuple_element_2 = mod_consts[13];
            PyTuple_SET_ITEM0(tmp_string_concat_values_1, 2, tmp_tuple_element_2);
            if (Nuitka_Cell_GET(self->m_closure[0]) == NULL) {

                FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[14]);
                NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
                CHAIN_EXCEPTION(tstate, exception_state.exception_value);

                exception_lineno = 42;
                type_description_1 = "ooccc";
                goto tuple_build_exception_1;
            }

            tmp_format_value_2 = Nuitka_Cell_GET(self->m_closure[0]);
            tmp_format_spec_2 = mod_consts[12];
            tmp_tuple_element_2 = BUILTIN_FORMAT(tstate, tmp_format_value_2, tmp_format_spec_2);
            if (tmp_tuple_element_2 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 42;
                type_description_1 = "ooccc";
                goto tuple_build_exception_1;
            }
            PyTuple_SET_ITEM(tmp_string_concat_values_1, 3, tmp_tuple_element_2);
            tmp_tuple_element_2 = mod_consts[15];
            PyTuple_SET_ITEM0(tmp_string_concat_values_1, 4, tmp_tuple_element_2);
            if (Nuitka_Cell_GET(self->m_closure[2]) == NULL) {

                FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[16]);
                NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
                CHAIN_EXCEPTION(tstate, exception_state.exception_value);

                exception_lineno = 42;
                type_description_1 = "ooccc";
                goto tuple_build_exception_1;
            }

            tmp_format_value_3 = Nuitka_Cell_GET(self->m_closure[2]);
            tmp_format_spec_3 = mod_consts[12];
            tmp_tuple_element_2 = BUILTIN_FORMAT(tstate, tmp_format_value_3, tmp_format_spec_3);
            if (tmp_tuple_element_2 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 42;
                type_description_1 = "ooccc";
                goto tuple_build_exception_1;
            }
            PyTuple_SET_ITEM(tmp_string_concat_values_1, 5, tmp_tuple_element_2);
            tmp_tuple_element_2 = mod_consts[17];
            PyTuple_SET_ITEM0(tmp_string_concat_values_1, 6, tmp_tuple_element_2);
        }
        goto tuple_build_noexception_1;
        // Exception handling pass through code for tuple_build:
        tuple_build_exception_1:;
        Py_DECREF(tmp_called_value_1);
        Py_DECREF(tmp_string_concat_values_1);
        goto frame_exception_exit_1;
        // Finished with no exception for tuple_build:
        tuple_build_noexception_1:;
        tmp_tuple_element_1 = PyUnicode_Join(mod_consts[12], tmp_string_concat_values_1);
        Py_DECREF(tmp_string_concat_values_1);
        if (tmp_tuple_element_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_called_value_1);

            exception_lineno = 42;
            type_description_1 = "ooccc";
            goto frame_exception_exit_1;
        }
        tmp_args_value_1 = MAKE_TUPLE_EMPTY(tstate, 2);
        PyTuple_SET_ITEM(tmp_args_value_1, 0, tmp_tuple_element_1);
        tmp_tuple_element_1 = module_var_accessor_bs4$$36$_deprecation$DeprecationWarning(tstate);
        if (unlikely(tmp_tuple_element_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[18]);
        }

        if (tmp_tuple_element_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 43;
            type_description_1 = "ooccc";
            goto tuple_build_exception_2;
        }
        PyTuple_SET_ITEM0(tmp_args_value_1, 1, tmp_tuple_element_1);
        goto tuple_build_noexception_2;
        // Exception handling pass through code for tuple_build:
        tuple_build_exception_2:;
        Py_DECREF(tmp_called_value_1);
        Py_DECREF(tmp_args_value_1);
        goto frame_exception_exit_1;
        // Finished with no exception for tuple_build:
        tuple_build_noexception_2:;
        tmp_kwargs_value_1 = DICT_COPY(tstate, mod_consts[19]);
        frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias->m_frame.f_lineno = 41;
        tmp_call_result_1 = CALL_FUNCTION(tstate, tmp_called_value_1, tmp_args_value_1, tmp_kwargs_value_1);
        Py_DECREF(tmp_called_value_1);
        Py_DECREF(tmp_args_value_1);
        Py_DECREF(tmp_kwargs_value_1);
        if (tmp_call_result_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 41;
            type_description_1 = "ooccc";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_1);
    }
    {
        PyObject *tmp_expression_value_2;
        PyObject *tmp_name_value_1;
        PyObject *tmp_value_value_1;
        CHECK_OBJECT(par_self);
        tmp_expression_value_2 = par_self;
        if (Nuitka_Cell_GET(self->m_closure[0]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[14]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 46;
            type_description_1 = "ooccc";
            goto frame_exception_exit_1;
        }

        tmp_name_value_1 = Nuitka_Cell_GET(self->m_closure[0]);
        CHECK_OBJECT(par_value);
        tmp_value_value_1 = par_value;
        tmp_return_value = BUILTIN_SETATTR(tmp_expression_value_2, tmp_name_value_1, tmp_value_value_1);
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 46;
            type_description_1 = "ooccc";
            goto frame_exception_exit_1;
        }
        Py_INCREF(tmp_return_value);
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
            exception_tb = MAKE_TRACEBACK(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias,
        type_description_1,
        par_self,
        par_value,
        self->m_closure[1],
        self->m_closure[0],
        self->m_closure[2]
    );


    // Release cached frame if used for exception.
    if (frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias == cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias);
        cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias = NULL;
    }

    assertFrameObject(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_OBJECT(par_value);
    Py_DECREF(par_value);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_OBJECT(par_value);
    Py_DECREF(par_value);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    struct Nuitka_CellObject *par_old_name = Nuitka_Cell_New1(python_pars[0]);
    struct Nuitka_CellObject *par_new_name = Nuitka_Cell_New1(python_pars[1]);
    struct Nuitka_CellObject *par_version = Nuitka_Cell_New1(python_pars[2]);
    PyObject *var_alias = NULL;
    struct Nuitka_FrameObject *frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    int tmp_res;
    static struct Nuitka_FrameObject *cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;

    // Actual function body.
    // Tried code:
    if (isFrameUnusable(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias)) {
        Py_XDECREF(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias = MAKE_FUNCTION_FRAME(tstate, code_objects_95858e4d4a80ba4b0ae59dce6edf650a, module_bs4$_deprecation, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias->m_type_description == NULL);
    frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias = cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias);
    assert(Py_REFCNT(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias) == 2);

    // Framed code:
    {
        PyObject *tmp_assign_source_1;
        PyObject *tmp_annotations_1;
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        struct Nuitka_CellObject *tmp_closure_1[3];
        tmp_dict_key_1 = mod_consts[21];
        tmp_dict_value_1 = module_var_accessor_bs4$$36$_deprecation$Any(tstate);
        if (unlikely(tmp_dict_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[1]);
        }

        if (tmp_dict_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 54;
            type_description_1 = "ccco";
            goto frame_exception_exit_1;
        }
        tmp_annotations_1 = _PyDict_NewPresized( 3 );
        tmp_res = PyDict_SetItem(tmp_annotations_1, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[22];
        tmp_dict_value_1 = module_var_accessor_bs4$$36$_deprecation$Any(tstate);
        if (unlikely(tmp_dict_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[1]);
        }

        if (tmp_dict_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 54;
            type_description_1 = "ccco";
            goto dict_build_exception_1;
        }
        tmp_res = PyDict_SetItem(tmp_annotations_1, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = module_var_accessor_bs4$$36$_deprecation$Any(tstate);
        if (unlikely(tmp_dict_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[1]);
        }

        if (tmp_dict_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 54;
            type_description_1 = "ccco";
            goto dict_build_exception_1;
        }
        tmp_res = PyDict_SetItem(tmp_annotations_1, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        goto dict_build_noexception_1;
        // Exception handling pass through code for dict_build:
        dict_build_exception_1:;
        Py_DECREF(tmp_annotations_1);
        goto frame_exception_exit_1;
        // Finished with no exception for dict_build:
        dict_build_noexception_1:;

        tmp_closure_1[0] = par_new_name;
        Py_INCREF(tmp_closure_1[0]);
        tmp_closure_1[1] = par_old_name;
        Py_INCREF(tmp_closure_1[1]);
        tmp_closure_1[2] = par_version;
        Py_INCREF(tmp_closure_1[2]);

        tmp_assign_source_1 = MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias(tstate, tmp_annotations_1, tmp_closure_1);

        assert(var_alias == NULL);
        var_alias = tmp_assign_source_1;
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias,
        type_description_1,
        par_old_name,
        par_new_name,
        par_version,
        var_alias
    );


    // Release cached frame if used for exception.
    if (frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias == cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias);
        cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias = NULL;
    }

    assertFrameObject(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    CHECK_OBJECT(var_alias);
    tmp_return_value = var_alias;
    Py_INCREF(tmp_return_value);
    goto try_return_handler_1;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Return handler code:
    try_return_handler_1:;
    CHECK_OBJECT(var_alias);
    Py_DECREF(var_alias);
    var_alias = NULL;
    goto function_return_exit;
    // Exception handler code:
    try_except_handler_1:;
    exception_keeper_lineno_1 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_1 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    // Re-raise.
    exception_state = exception_keeper_name_1;
    exception_lineno = exception_keeper_lineno_1;

    goto function_exception_exit;
    // End of try:

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_old_name);
    Py_DECREF(par_old_name);
    CHECK_OBJECT(par_new_name);
    Py_DECREF(par_new_name);
    CHECK_OBJECT(par_version);
    Py_DECREF(par_version);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_old_name);
    Py_DECREF(par_old_name);
    CHECK_OBJECT(par_new_name);
    Py_DECREF(par_new_name);
    CHECK_OBJECT(par_version);
    Py_DECREF(par_version);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_self = python_pars[0];
    PyObject *par_args = python_pars[1];
    PyObject *par_kwargs = python_pars[2];
    struct Nuitka_FrameObject *frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    NUITKA_MAY_BE_UNUSED nuitka_void tmp_unused;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    PyObject *tmp_return_value = NULL;
    static struct Nuitka_FrameObject *cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias)) {
        Py_XDECREF(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias = MAKE_FUNCTION_FRAME(tstate, code_objects_03042f7654d982f910de4f1341aad7fb, module_bs4$_deprecation, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias->m_type_description == NULL);
    frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias = cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias);
    assert(Py_REFCNT(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_expression_value_1;
        PyObject *tmp_call_result_1;
        PyObject *tmp_args_value_1;
        PyObject *tmp_tuple_element_1;
        PyObject *tmp_string_concat_values_1;
        PyObject *tmp_tuple_element_2;
        PyObject *tmp_kwargs_value_1;
        tmp_expression_value_1 = module_var_accessor_bs4$$36$_deprecation$warnings(tstate);
        if (unlikely(tmp_expression_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[8]);
        }

        if (tmp_expression_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 56;
            type_description_1 = "oooccc";
            goto frame_exception_exit_1;
        }
        tmp_called_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[9]);
        if (tmp_called_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 56;
            type_description_1 = "oooccc";
            goto frame_exception_exit_1;
        }
        tmp_tuple_element_2 = mod_consts[24];
        tmp_string_concat_values_1 = MAKE_TUPLE_EMPTY(tstate, 7);
        {
            PyObject *tmp_format_value_1;
            PyObject *tmp_format_spec_1;
            PyObject *tmp_format_value_2;
            PyObject *tmp_format_spec_2;
            PyObject *tmp_format_value_3;
            PyObject *tmp_format_spec_3;
            PyTuple_SET_ITEM0(tmp_string_concat_values_1, 0, tmp_tuple_element_2);
            if (Nuitka_Cell_GET(self->m_closure[1]) == NULL) {

                FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[11]);
                NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
                CHAIN_EXCEPTION(tstate, exception_state.exception_value);

                exception_lineno = 57;
                type_description_1 = "oooccc";
                goto tuple_build_exception_1;
            }

            tmp_format_value_1 = Nuitka_Cell_GET(self->m_closure[1]);
            tmp_format_spec_1 = mod_consts[12];
            tmp_tuple_element_2 = BUILTIN_FORMAT(tstate, tmp_format_value_1, tmp_format_spec_1);
            if (tmp_tuple_element_2 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 57;
                type_description_1 = "oooccc";
                goto tuple_build_exception_1;
            }
            PyTuple_SET_ITEM(tmp_string_concat_values_1, 1, tmp_tuple_element_2);
            tmp_tuple_element_2 = mod_consts[13];
            PyTuple_SET_ITEM0(tmp_string_concat_values_1, 2, tmp_tuple_element_2);
            if (Nuitka_Cell_GET(self->m_closure[0]) == NULL) {

                FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[14]);
                NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
                CHAIN_EXCEPTION(tstate, exception_state.exception_value);

                exception_lineno = 57;
                type_description_1 = "oooccc";
                goto tuple_build_exception_1;
            }

            tmp_format_value_2 = Nuitka_Cell_GET(self->m_closure[0]);
            tmp_format_spec_2 = mod_consts[12];
            tmp_tuple_element_2 = BUILTIN_FORMAT(tstate, tmp_format_value_2, tmp_format_spec_2);
            if (tmp_tuple_element_2 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 57;
                type_description_1 = "oooccc";
                goto tuple_build_exception_1;
            }
            PyTuple_SET_ITEM(tmp_string_concat_values_1, 3, tmp_tuple_element_2);
            tmp_tuple_element_2 = mod_consts[15];
            PyTuple_SET_ITEM0(tmp_string_concat_values_1, 4, tmp_tuple_element_2);
            if (Nuitka_Cell_GET(self->m_closure[2]) == NULL) {

                FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[16]);
                NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
                CHAIN_EXCEPTION(tstate, exception_state.exception_value);

                exception_lineno = 57;
                type_description_1 = "oooccc";
                goto tuple_build_exception_1;
            }

            tmp_format_value_3 = Nuitka_Cell_GET(self->m_closure[2]);
            tmp_format_spec_3 = mod_consts[12];
            tmp_tuple_element_2 = BUILTIN_FORMAT(tstate, tmp_format_value_3, tmp_format_spec_3);
            if (tmp_tuple_element_2 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 57;
                type_description_1 = "oooccc";
                goto tuple_build_exception_1;
            }
            PyTuple_SET_ITEM(tmp_string_concat_values_1, 5, tmp_tuple_element_2);
            tmp_tuple_element_2 = mod_consts[17];
            PyTuple_SET_ITEM0(tmp_string_concat_values_1, 6, tmp_tuple_element_2);
        }
        goto tuple_build_noexception_1;
        // Exception handling pass through code for tuple_build:
        tuple_build_exception_1:;
        Py_DECREF(tmp_called_value_1);
        Py_DECREF(tmp_string_concat_values_1);
        goto frame_exception_exit_1;
        // Finished with no exception for tuple_build:
        tuple_build_noexception_1:;
        tmp_tuple_element_1 = PyUnicode_Join(mod_consts[12], tmp_string_concat_values_1);
        Py_DECREF(tmp_string_concat_values_1);
        if (tmp_tuple_element_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_called_value_1);

            exception_lineno = 57;
            type_description_1 = "oooccc";
            goto frame_exception_exit_1;
        }
        tmp_args_value_1 = MAKE_TUPLE_EMPTY(tstate, 2);
        PyTuple_SET_ITEM(tmp_args_value_1, 0, tmp_tuple_element_1);
        tmp_tuple_element_1 = module_var_accessor_bs4$$36$_deprecation$DeprecationWarning(tstate);
        if (unlikely(tmp_tuple_element_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[18]);
        }

        if (tmp_tuple_element_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 58;
            type_description_1 = "oooccc";
            goto tuple_build_exception_2;
        }
        PyTuple_SET_ITEM0(tmp_args_value_1, 1, tmp_tuple_element_1);
        goto tuple_build_noexception_2;
        // Exception handling pass through code for tuple_build:
        tuple_build_exception_2:;
        Py_DECREF(tmp_called_value_1);
        Py_DECREF(tmp_args_value_1);
        goto frame_exception_exit_1;
        // Finished with no exception for tuple_build:
        tuple_build_noexception_2:;
        tmp_kwargs_value_1 = DICT_COPY(tstate, mod_consts[19]);
        frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias->m_frame.f_lineno = 56;
        tmp_call_result_1 = CALL_FUNCTION(tstate, tmp_called_value_1, tmp_args_value_1, tmp_kwargs_value_1);
        Py_DECREF(tmp_called_value_1);
        Py_DECREF(tmp_args_value_1);
        Py_DECREF(tmp_kwargs_value_1);
        if (tmp_call_result_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 56;
            type_description_1 = "oooccc";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_1);
    }
    {
        PyObject *tmp_direct_call_arg1_1;
        PyObject *tmp_expression_value_2;
        PyObject *tmp_name_value_1;
        PyObject *tmp_direct_call_arg2_1;
        PyObject *tmp_direct_call_arg3_1;
        CHECK_OBJECT(par_self);
        tmp_expression_value_2 = par_self;
        if (Nuitka_Cell_GET(self->m_closure[0]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[14]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 61;
            type_description_1 = "oooccc";
            goto frame_exception_exit_1;
        }

        tmp_name_value_1 = Nuitka_Cell_GET(self->m_closure[0]);
        tmp_direct_call_arg1_1 = BUILTIN_GETATTR(tstate, tmp_expression_value_2, tmp_name_value_1, NULL);
        if (tmp_direct_call_arg1_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 61;
            type_description_1 = "oooccc";
            goto frame_exception_exit_1;
        }
        CHECK_OBJECT(par_args);
        tmp_direct_call_arg2_1 = par_args;
        CHECK_OBJECT(par_kwargs);
        tmp_direct_call_arg3_1 = par_kwargs;
        Py_INCREF(tmp_direct_call_arg2_1);
        Py_INCREF(tmp_direct_call_arg3_1);

        {
            PyObject *dir_call_args[] = {tmp_direct_call_arg1_1, tmp_direct_call_arg2_1, tmp_direct_call_arg3_1};
            tmp_return_value = impl___main__$$36$$$36$$$36$helper_function_complex_call_helper_star_list_star_dict(tstate, dir_call_args);
        }
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 61;
            type_description_1 = "oooccc";
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
            exception_tb = MAKE_TRACEBACK(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias,
        type_description_1,
        par_self,
        par_args,
        par_kwargs,
        self->m_closure[1],
        self->m_closure[0],
        self->m_closure[2]
    );


    // Release cached frame if used for exception.
    if (frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias == cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias);
        cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias = NULL;
    }

    assertFrameObject(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
    CHECK_OBJECT(par_args);
    Py_DECREF(par_args);
    CHECK_OBJECT(par_kwargs);
    Py_DECREF(par_kwargs);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_self);
    Py_DECREF(par_self);
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


static PyObject *impl_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    struct Nuitka_CellObject *par_replaced_by = Nuitka_Cell_New1(python_pars[0]);
    struct Nuitka_CellObject *par_version = Nuitka_Cell_New1(python_pars[1]);
    PyObject *var_deprecate = NULL;
    struct Nuitka_FrameObject *frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    int tmp_res;
    static struct Nuitka_FrameObject *cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;

    // Actual function body.
    // Tried code:
    if (isFrameUnusable(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated)) {
        Py_XDECREF(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated = MAKE_FUNCTION_FRAME(tstate, code_objects_cb3dbea03ab50ab74dece3da876841f1, module_bs4$_deprecation, sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated->m_type_description == NULL);
    frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated = cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated);
    assert(Py_REFCNT(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated) == 2);

    // Framed code:
    {
        PyObject *tmp_assign_source_1;
        PyObject *tmp_annotations_1;
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        struct Nuitka_CellObject *tmp_closure_1[2];
        tmp_dict_key_1 = mod_consts[25];
        tmp_dict_value_1 = module_var_accessor_bs4$$36$_deprecation$Callable(tstate);
        if (unlikely(tmp_dict_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[26]);
        }

        if (tmp_dict_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 67;
            type_description_1 = "cco";
            goto frame_exception_exit_1;
        }
        tmp_annotations_1 = _PyDict_NewPresized( 2 );
        tmp_res = PyDict_SetItem(tmp_annotations_1, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = module_var_accessor_bs4$$36$_deprecation$Callable(tstate);
        if (unlikely(tmp_dict_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[26]);
        }

        if (tmp_dict_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 67;
            type_description_1 = "cco";
            goto dict_build_exception_1;
        }
        tmp_res = PyDict_SetItem(tmp_annotations_1, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        goto dict_build_noexception_1;
        // Exception handling pass through code for dict_build:
        dict_build_exception_1:;
        Py_DECREF(tmp_annotations_1);
        goto frame_exception_exit_1;
        // Finished with no exception for dict_build:
        dict_build_noexception_1:;

        tmp_closure_1[0] = par_replaced_by;
        Py_INCREF(tmp_closure_1[0]);
        tmp_closure_1[1] = par_version;
        Py_INCREF(tmp_closure_1[1]);

        tmp_assign_source_1 = MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate(tstate, tmp_annotations_1, tmp_closure_1);

        assert(var_deprecate == NULL);
        var_deprecate = tmp_assign_source_1;
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated,
        type_description_1,
        par_replaced_by,
        par_version,
        var_deprecate
    );


    // Release cached frame if used for exception.
    if (frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated == cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated);
        cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated = NULL;
    }

    assertFrameObject(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    CHECK_OBJECT(var_deprecate);
    tmp_return_value = var_deprecate;
    Py_INCREF(tmp_return_value);
    goto try_return_handler_1;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Return handler code:
    try_return_handler_1:;
    CHECK_OBJECT(var_deprecate);
    Py_DECREF(var_deprecate);
    var_deprecate = NULL;
    goto function_return_exit;
    // Exception handler code:
    try_except_handler_1:;
    exception_keeper_lineno_1 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_1 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    // Re-raise.
    exception_state = exception_keeper_name_1;
    exception_lineno = exception_keeper_lineno_1;

    goto function_exception_exit;
    // End of try:

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_replaced_by);
    Py_DECREF(par_replaced_by);
    CHECK_OBJECT(par_version);
    Py_DECREF(par_version);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_replaced_by);
    Py_DECREF(par_replaced_by);
    CHECK_OBJECT(par_version);
    Py_DECREF(par_version);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    struct Nuitka_CellObject *par_func = Nuitka_Cell_New1(python_pars[0]);
    PyObject *var_with_warning = NULL;
    struct Nuitka_FrameObject *frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    int tmp_res;
    static struct Nuitka_FrameObject *cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate = NULL;
    PyObject *tmp_return_value = NULL;
    struct Nuitka_ExceptionPreservationItem exception_keeper_name_1;
    NUITKA_MAY_BE_UNUSED int exception_keeper_lineno_1;

    // Actual function body.
    // Tried code:
    if (isFrameUnusable(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate)) {
        Py_XDECREF(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate = MAKE_FUNCTION_FRAME(tstate, code_objects_026cb297a34658f48abf1d75eab043f8, module_bs4$_deprecation, sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate->m_type_description == NULL);
    frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate = cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate);
    assert(Py_REFCNT(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate) == 2);

    // Framed code:
    {
        PyObject *tmp_assign_source_1;
        PyObject *tmp_called_value_1;
        PyObject *tmp_called_instance_1;
        PyObject *tmp_args_element_value_1;
        PyObject *tmp_args_element_value_2;
        PyObject *tmp_annotations_1;
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        struct Nuitka_CellObject *tmp_closure_1[3];
        tmp_called_instance_1 = IMPORT_HARD_FUNCTOOLS();
        assert(!(tmp_called_instance_1 == NULL));
        CHECK_OBJECT(Nuitka_Cell_GET(par_func));
        tmp_args_element_value_1 = Nuitka_Cell_GET(par_func);
        frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate->m_frame.f_lineno = 68;
        tmp_called_value_1 = CALL_METHOD_WITH_SINGLE_ARG(tstate, tmp_called_instance_1, mod_consts[29], tmp_args_element_value_1);
        if (tmp_called_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 68;
            type_description_1 = "co";
            goto frame_exception_exit_1;
        }
        tmp_dict_key_1 = mod_consts[21];
        tmp_dict_value_1 = module_var_accessor_bs4$$36$_deprecation$Any(tstate);
        if (unlikely(tmp_dict_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[1]);
        }

        if (tmp_dict_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));

            Py_DECREF(tmp_called_value_1);

            exception_lineno = 69;
            type_description_1 = "co";
            goto frame_exception_exit_1;
        }
        tmp_annotations_1 = _PyDict_NewPresized( 3 );
        tmp_res = PyDict_SetItem(tmp_annotations_1, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[22];
        tmp_dict_value_1 = module_var_accessor_bs4$$36$_deprecation$Any(tstate);
        if (unlikely(tmp_dict_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[1]);
        }

        if (tmp_dict_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 69;
            type_description_1 = "co";
            goto dict_build_exception_1;
        }
        tmp_res = PyDict_SetItem(tmp_annotations_1, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = module_var_accessor_bs4$$36$_deprecation$Any(tstate);
        if (unlikely(tmp_dict_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[1]);
        }

        if (tmp_dict_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 69;
            type_description_1 = "co";
            goto dict_build_exception_1;
        }
        tmp_res = PyDict_SetItem(tmp_annotations_1, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        goto dict_build_noexception_1;
        // Exception handling pass through code for dict_build:
        dict_build_exception_1:;
        Py_DECREF(tmp_called_value_1);
        Py_DECREF(tmp_annotations_1);
        goto frame_exception_exit_1;
        // Finished with no exception for dict_build:
        dict_build_noexception_1:;

        tmp_closure_1[0] = par_func;
        Py_INCREF(tmp_closure_1[0]);
        tmp_closure_1[1] = self->m_closure[0];
        Py_INCREF(tmp_closure_1[1]);
        tmp_closure_1[2] = self->m_closure[1];
        Py_INCREF(tmp_closure_1[2]);

        tmp_args_element_value_2 = MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning(tstate, tmp_annotations_1, tmp_closure_1);

        frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate->m_frame.f_lineno = 68;
        tmp_assign_source_1 = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, tmp_called_value_1, tmp_args_element_value_2);
        Py_DECREF(tmp_called_value_1);
        Py_DECREF(tmp_args_element_value_2);
        if (tmp_assign_source_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 68;
            type_description_1 = "co";
            goto frame_exception_exit_1;
        }
        assert(var_with_warning == NULL);
        var_with_warning = tmp_assign_source_1;
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate,
        type_description_1,
        par_func,
        var_with_warning
    );


    // Release cached frame if used for exception.
    if (frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate == cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate);
        cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate = NULL;
    }

    assertFrameObject(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto try_except_handler_1;
    frame_no_exception_1:;
    CHECK_OBJECT(var_with_warning);
    tmp_return_value = var_with_warning;
    Py_INCREF(tmp_return_value);
    goto try_return_handler_1;
    NUITKA_CANNOT_GET_HERE("tried codes exits in all cases");
    return NULL;
    // Return handler code:
    try_return_handler_1:;
    CHECK_OBJECT(var_with_warning);
    Py_DECREF(var_with_warning);
    var_with_warning = NULL;
    goto function_return_exit;
    // Exception handler code:
    try_except_handler_1:;
    exception_keeper_lineno_1 = exception_lineno;
    exception_lineno = 0;
    exception_keeper_name_1 = exception_state;
    INIT_ERROR_OCCURRED_STATE(&exception_state);

    // Re-raise.
    exception_state = exception_keeper_name_1;
    exception_lineno = exception_keeper_lineno_1;

    goto function_exception_exit;
    // End of try:

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;

function_exception_exit:
    CHECK_OBJECT(par_func);
    Py_DECREF(par_func);
    CHECK_EXCEPTION_STATE(&exception_state);
    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);

    return NULL;

function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_func);
    Py_DECREF(par_func);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_args = python_pars[0];
    PyObject *par_kwargs = python_pars[1];
    struct Nuitka_FrameObject *frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    NUITKA_MAY_BE_UNUSED nuitka_void tmp_unused;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;
    PyObject *tmp_return_value = NULL;
    static struct Nuitka_FrameObject *cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning = NULL;

    // Actual function body.
    if (isFrameUnusable(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning)) {
        Py_XDECREF(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning);

#if _DEBUG_REFCOUNTS
        if (cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning == NULL) {
            count_active_frame_cache_instances += 1;
        } else {
            count_released_frame_cache_instances += 1;
        }
        count_allocated_frame_cache_instances += 1;
#endif
        cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning = MAKE_FUNCTION_FRAME(tstate, code_objects_54ccb6b959c4b8cd845850120f4f910a, module_bs4$_deprecation, sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *)+sizeof(void *));
#if _DEBUG_REFCOUNTS
    } else {
        count_hit_frame_cache_instances += 1;
#endif
    }

    assert(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning->m_type_description == NULL);
    frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning = cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning;

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning);
    assert(Py_REFCNT(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning) == 2);

    // Framed code:
    {
        PyObject *tmp_called_value_1;
        PyObject *tmp_expression_value_1;
        PyObject *tmp_call_result_1;
        PyObject *tmp_args_value_1;
        PyObject *tmp_tuple_element_1;
        PyObject *tmp_string_concat_values_1;
        PyObject *tmp_tuple_element_2;
        PyObject *tmp_kwargs_value_1;
        tmp_expression_value_1 = module_var_accessor_bs4$$36$_deprecation$warnings(tstate);
        if (unlikely(tmp_expression_value_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[8]);
        }

        if (tmp_expression_value_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 71;
            type_description_1 = "ooccc";
            goto frame_exception_exit_1;
        }
        tmp_called_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_1, mod_consts[9]);
        if (tmp_called_value_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 71;
            type_description_1 = "ooccc";
            goto frame_exception_exit_1;
        }
        tmp_tuple_element_2 = mod_consts[24];
        tmp_string_concat_values_1 = MAKE_TUPLE_EMPTY(tstate, 7);
        {
            PyObject *tmp_format_value_1;
            PyObject *tmp_expression_value_2;
            PyObject *tmp_format_spec_1;
            PyObject *tmp_format_value_2;
            PyObject *tmp_format_spec_2;
            PyObject *tmp_format_value_3;
            PyObject *tmp_format_spec_3;
            PyTuple_SET_ITEM0(tmp_string_concat_values_1, 0, tmp_tuple_element_2);
            if (Nuitka_Cell_GET(self->m_closure[0]) == NULL) {

                FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[25]);
                NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
                CHAIN_EXCEPTION(tstate, exception_state.exception_value);

                exception_lineno = 72;
                type_description_1 = "ooccc";
                goto tuple_build_exception_1;
            }

            tmp_expression_value_2 = Nuitka_Cell_GET(self->m_closure[0]);
            tmp_format_value_1 = LOOKUP_ATTRIBUTE(tstate, tmp_expression_value_2, mod_consts[32]);
            if (tmp_format_value_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 72;
                type_description_1 = "ooccc";
                goto tuple_build_exception_1;
            }
            tmp_format_spec_1 = mod_consts[12];
            tmp_tuple_element_2 = BUILTIN_FORMAT(tstate, tmp_format_value_1, tmp_format_spec_1);
            Py_DECREF(tmp_format_value_1);
            if (tmp_tuple_element_2 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 72;
                type_description_1 = "ooccc";
                goto tuple_build_exception_1;
            }
            PyTuple_SET_ITEM(tmp_string_concat_values_1, 1, tmp_tuple_element_2);
            tmp_tuple_element_2 = mod_consts[13];
            PyTuple_SET_ITEM0(tmp_string_concat_values_1, 2, tmp_tuple_element_2);
            if (Nuitka_Cell_GET(self->m_closure[1]) == NULL) {

                FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[33]);
                NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
                CHAIN_EXCEPTION(tstate, exception_state.exception_value);

                exception_lineno = 72;
                type_description_1 = "ooccc";
                goto tuple_build_exception_1;
            }

            tmp_format_value_2 = Nuitka_Cell_GET(self->m_closure[1]);
            tmp_format_spec_2 = mod_consts[12];
            tmp_tuple_element_2 = BUILTIN_FORMAT(tstate, tmp_format_value_2, tmp_format_spec_2);
            if (tmp_tuple_element_2 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 72;
                type_description_1 = "ooccc";
                goto tuple_build_exception_1;
            }
            PyTuple_SET_ITEM(tmp_string_concat_values_1, 3, tmp_tuple_element_2);
            tmp_tuple_element_2 = mod_consts[15];
            PyTuple_SET_ITEM0(tmp_string_concat_values_1, 4, tmp_tuple_element_2);
            if (Nuitka_Cell_GET(self->m_closure[2]) == NULL) {

                FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[16]);
                NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
                CHAIN_EXCEPTION(tstate, exception_state.exception_value);

                exception_lineno = 72;
                type_description_1 = "ooccc";
                goto tuple_build_exception_1;
            }

            tmp_format_value_3 = Nuitka_Cell_GET(self->m_closure[2]);
            tmp_format_spec_3 = mod_consts[12];
            tmp_tuple_element_2 = BUILTIN_FORMAT(tstate, tmp_format_value_3, tmp_format_spec_3);
            if (tmp_tuple_element_2 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 72;
                type_description_1 = "ooccc";
                goto tuple_build_exception_1;
            }
            PyTuple_SET_ITEM(tmp_string_concat_values_1, 5, tmp_tuple_element_2);
            tmp_tuple_element_2 = mod_consts[17];
            PyTuple_SET_ITEM0(tmp_string_concat_values_1, 6, tmp_tuple_element_2);
        }
        goto tuple_build_noexception_1;
        // Exception handling pass through code for tuple_build:
        tuple_build_exception_1:;
        Py_DECREF(tmp_called_value_1);
        Py_DECREF(tmp_string_concat_values_1);
        goto frame_exception_exit_1;
        // Finished with no exception for tuple_build:
        tuple_build_noexception_1:;
        tmp_tuple_element_1 = PyUnicode_Join(mod_consts[12], tmp_string_concat_values_1);
        Py_DECREF(tmp_string_concat_values_1);
        if (tmp_tuple_element_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);
            Py_DECREF(tmp_called_value_1);

            exception_lineno = 72;
            type_description_1 = "ooccc";
            goto frame_exception_exit_1;
        }
        tmp_args_value_1 = MAKE_TUPLE_EMPTY(tstate, 2);
        PyTuple_SET_ITEM(tmp_args_value_1, 0, tmp_tuple_element_1);
        tmp_tuple_element_1 = module_var_accessor_bs4$$36$_deprecation$DeprecationWarning(tstate);
        if (unlikely(tmp_tuple_element_1 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[18]);
        }

        if (tmp_tuple_element_1 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 73;
            type_description_1 = "ooccc";
            goto tuple_build_exception_2;
        }
        PyTuple_SET_ITEM0(tmp_args_value_1, 1, tmp_tuple_element_1);
        goto tuple_build_noexception_2;
        // Exception handling pass through code for tuple_build:
        tuple_build_exception_2:;
        Py_DECREF(tmp_called_value_1);
        Py_DECREF(tmp_args_value_1);
        goto frame_exception_exit_1;
        // Finished with no exception for tuple_build:
        tuple_build_noexception_2:;
        tmp_kwargs_value_1 = DICT_COPY(tstate, mod_consts[19]);
        frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning->m_frame.f_lineno = 71;
        tmp_call_result_1 = CALL_FUNCTION(tstate, tmp_called_value_1, tmp_args_value_1, tmp_kwargs_value_1);
        Py_DECREF(tmp_called_value_1);
        Py_DECREF(tmp_args_value_1);
        Py_DECREF(tmp_kwargs_value_1);
        if (tmp_call_result_1 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 71;
            type_description_1 = "ooccc";
            goto frame_exception_exit_1;
        }
        Py_DECREF(tmp_call_result_1);
    }
    {
        PyObject *tmp_direct_call_arg1_1;
        PyObject *tmp_direct_call_arg2_1;
        PyObject *tmp_direct_call_arg3_1;
        if (Nuitka_Cell_GET(self->m_closure[0]) == NULL) {

            FORMAT_UNBOUND_CLOSURE_ERROR(tstate, &exception_state, mod_consts[25]);
            NORMALIZE_EXCEPTION_STATE(tstate, &exception_state);
            CHAIN_EXCEPTION(tstate, exception_state.exception_value);

            exception_lineno = 76;
            type_description_1 = "ooccc";
            goto frame_exception_exit_1;
        }

        tmp_direct_call_arg1_1 = Nuitka_Cell_GET(self->m_closure[0]);
        CHECK_OBJECT(par_args);
        tmp_direct_call_arg2_1 = par_args;
        CHECK_OBJECT(par_kwargs);
        tmp_direct_call_arg3_1 = par_kwargs;
        Py_INCREF(tmp_direct_call_arg1_1);
        Py_INCREF(tmp_direct_call_arg2_1);
        Py_INCREF(tmp_direct_call_arg3_1);

        {
            PyObject *dir_call_args[] = {tmp_direct_call_arg1_1, tmp_direct_call_arg2_1, tmp_direct_call_arg3_1};
            tmp_return_value = impl___main__$$36$$$36$$$36$helper_function_complex_call_helper_star_list_star_dict(tstate, dir_call_args);
        }
        if (tmp_return_value == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 76;
            type_description_1 = "ooccc";
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
            exception_tb = MAKE_TRACEBACK(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }

    // Attaches locals to frame if any.
    Nuitka_Frame_AttachLocals(
        frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning,
        type_description_1,
        par_args,
        par_kwargs,
        self->m_closure[0],
        self->m_closure[1],
        self->m_closure[2]
    );


    // Release cached frame if used for exception.
    if (frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning == cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning) {
#if _DEBUG_REFCOUNTS
        count_active_frame_cache_instances -= 1;
        count_released_frame_cache_instances += 1;
#endif
        Py_DECREF(cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning);
        cache_frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning = NULL;
    }

    assertFrameObject(frame_frame_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto function_exception_exit;
    frame_no_exception_1:;

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



static PyObject *MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias(PyThreadState *tstate, PyObject *annotations) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias,
        mod_consts[42],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_a6234e2d240c1443fc7156c4e8b18d24,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_bs4$_deprecation,
        mod_consts[7],
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias(PyThreadState *tstate, PyObject *annotations, struct Nuitka_CellObject **closure) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias,
        mod_consts[3],
#if PYTHON_VERSION >= 0x300
        mod_consts[4],
#endif
        code_objects_cfd3d698b014c3be85c33bd7381c389e,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_bs4$_deprecation,
        mod_consts[2],
        closure,
        3
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias(PyThreadState *tstate, PyObject *annotations, struct Nuitka_CellObject **closure) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias,
        mod_consts[3],
#if PYTHON_VERSION >= 0x300
        mod_consts[4],
#endif
        code_objects_1a76f189cfe03fe170485beaad95e4df,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_bs4$_deprecation,
        mod_consts[2],
        closure,
        3
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias(PyThreadState *tstate, PyObject *annotations) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias,
        mod_consts[43],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_95858e4d4a80ba4b0ae59dce6edf650a,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_bs4$_deprecation,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias(PyThreadState *tstate, PyObject *annotations, struct Nuitka_CellObject **closure) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias,
        mod_consts[3],
#if PYTHON_VERSION >= 0x300
        mod_consts[23],
#endif
        code_objects_03042f7654d982f910de4f1341aad7fb,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_bs4$_deprecation,
        mod_consts[2],
        closure,
        3
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated(PyThreadState *tstate, PyObject *annotations) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated,
        mod_consts[44],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_cb3dbea03ab50ab74dece3da876841f1,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_bs4$_deprecation,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate(PyThreadState *tstate, PyObject *annotations, struct Nuitka_CellObject **closure) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate,
        mod_consts[27],
#if PYTHON_VERSION >= 0x300
        mod_consts[28],
#endif
        code_objects_026cb297a34658f48abf1d75eab043f8,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_bs4$_deprecation,
        NULL,
        closure,
        2
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning(PyThreadState *tstate, PyObject *annotations, struct Nuitka_CellObject **closure) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning,
        mod_consts[30],
#if PYTHON_VERSION >= 0x300
        mod_consts[31],
#endif
        code_objects_54ccb6b959c4b8cd845850120f4f910a,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        annotations,
#endif
        module_bs4$_deprecation,
        mod_consts[2],
        closure,
        3
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

static function_impl_code const function_table_bs4$_deprecation[] = {
    impl_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__1_alias,
    impl_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias$$36$$$36$$$36$function__2_alias,
    impl_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias$$36$$$36$$$36$function__1_alias,
    impl_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate,
    impl_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated$$36$$$36$$$36$function__1_deprecate$$36$$$36$$$36$function__1_with_warning,
    impl_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias,
    impl_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias,
    impl_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated,
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

    return Nuitka_Function_GetFunctionState(function, function_table_bs4$_deprecation);
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
        module_bs4$_deprecation,
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
        function_table_bs4$_deprecation,
        sizeof(function_table_bs4$_deprecation) / sizeof(function_impl_code)
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
static char const *module_full_name = "bs4._deprecation";
#endif

// Internal entry point for module code.
PyObject *modulecode_bs4$_deprecation(PyThreadState *tstate, PyObject *module, struct Nuitka_MetaPathBasedLoaderEntry const *loader_entry) {
    // Report entry to PGO.
    PGO_onModuleEntered("bs4$_deprecation");

    // Store the module for future use.
    module_bs4$_deprecation = module;

    moduledict_bs4$_deprecation = MODULE_DICT(module_bs4$_deprecation);

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
        PRINT_STRING("bs4$_deprecation: Calling setupMetaPathBasedLoader().\n");
#endif
        setupMetaPathBasedLoader(tstate);
#if 0 >= 0
#ifdef _NUITKA_TRACE
        PRINT_STRING("bs4$_deprecation: Calling updateMetaPathBasedLoaderModuleRoot().\n");
#endif
        updateMetaPathBasedLoaderModuleRoot(module_full_name);
#endif


#if PYTHON_VERSION >= 0x300
        patchInspectModule(tstate);
#endif

#endif

        /* The constants only used by this module are created now. */
        NUITKA_PRINT_TRACE("bs4$_deprecation: Calling createModuleConstants().\n");
        createModuleConstants(tstate);

#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
        createModuleCodeObjects();
#endif
        init_done = true;
    }

#if _NUITKA_MODULE_MODE && 0
    PyObject *pre_load = IMPORT_EMBEDDED_MODULE(tstate, "bs4._deprecation" "-preLoad");
    if (pre_load == NULL) {
        return NULL;
    }
#endif

    // PRINT_STRING("in initbs4$_deprecation\n");

#ifdef _NUITKA_PLUGIN_DILL_ENABLED
    {
        char const *module_name_c;
        if (loader_entry != NULL) {
            module_name_c = loader_entry->name;
        } else {
            PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_bs4$_deprecation, (Nuitka_StringObject *)const_str_plain___name__);
            module_name_c = Nuitka_String_AsString(module_name);
        }

        registerDillPluginTables(tstate, module_name_c, &_method_def_reduce_compiled_function, &_method_def_create_compiled_function);
    }
#endif

    // Set "__compiled__" to what version information we have.
    UPDATE_STRING_DICT0(
        moduledict_bs4$_deprecation,
        (Nuitka_StringObject *)const_str_plain___compiled__,
        Nuitka_dunder_compiled_value
    );

    // Update "__package__" value to what it ought to be.
    {
#if 0
        UPDATE_STRING_DICT0(
            moduledict_bs4$_deprecation,
            (Nuitka_StringObject *)const_str_plain___package__,
            mod_consts[12]
        );
#elif 0
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_bs4$_deprecation, (Nuitka_StringObject *)const_str_plain___name__);

        UPDATE_STRING_DICT0(
            moduledict_bs4$_deprecation,
            (Nuitka_StringObject *)const_str_plain___package__,
            module_name
        );
#else

#if PYTHON_VERSION < 0x300
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_bs4$_deprecation, (Nuitka_StringObject *)const_str_plain___name__);
        char const *module_name_cstr = PyString_AS_STRING(module_name);

        char const *last_dot = strrchr(module_name_cstr, '.');

        if (last_dot != NULL) {
            UPDATE_STRING_DICT1(
                moduledict_bs4$_deprecation,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyString_FromStringAndSize(module_name_cstr, last_dot - module_name_cstr)
            );
        }
#else
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_bs4$_deprecation, (Nuitka_StringObject *)const_str_plain___name__);
        Py_ssize_t dot_index = PyUnicode_Find(module_name, const_str_dot, 0, PyUnicode_GetLength(module_name), -1);

        if (dot_index != -1) {
            UPDATE_STRING_DICT1(
                moduledict_bs4$_deprecation,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyUnicode_Substring(module_name, 0, dot_index)
            );
        }
#endif
#endif
    }

    CHECK_OBJECT(module_bs4$_deprecation);

    // For deep importing of a module we need to have "__builtins__", so we set
    // it ourselves in the same way than CPython does. Note: This must be done
    // before the frame object is allocated, or else it may fail.

    if (GET_STRING_DICT_VALUE(moduledict_bs4$_deprecation, (Nuitka_StringObject *)const_str_plain___builtins__) == NULL) {
        PyObject *value = (PyObject *)builtin_module;

        // Check if main module, not a dict then but the module itself.
#if _NUITKA_MODULE_MODE || !0
        value = PyModule_GetDict(value);
#endif

        UPDATE_STRING_DICT0(moduledict_bs4$_deprecation, (Nuitka_StringObject *)const_str_plain___builtins__, value);
    }

    PyObject *module_loader = Nuitka_Loader_New(loader_entry);
    UPDATE_STRING_DICT0(moduledict_bs4$_deprecation, (Nuitka_StringObject *)const_str_plain___loader__, module_loader);

#if PYTHON_VERSION >= 0x300
// Set the "__spec__" value

#if 0
    // Main modules just get "None" as spec.
    UPDATE_STRING_DICT0(moduledict_bs4$_deprecation, (Nuitka_StringObject *)const_str_plain___spec__, Py_None);
#else
    // Other modules get a "ModuleSpec" from the standard mechanism.
    {
        PyObject *bootstrap_module = getImportLibBootstrapModule();
        CHECK_OBJECT(bootstrap_module);

        PyObject *_spec_from_module = PyObject_GetAttrString(bootstrap_module, "_spec_from_module");
        CHECK_OBJECT(_spec_from_module);

        PyObject *spec_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, _spec_from_module, module_bs4$_deprecation);
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

        UPDATE_STRING_DICT1(moduledict_bs4$_deprecation, (Nuitka_StringObject *)const_str_plain___spec__, spec_value);
    }
#endif
#endif

    // Temp variables if any
    PyObject *tmp_import_from_1__module = NULL;
    struct Nuitka_FrameObject *frame_frame_bs4$_deprecation;
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
        tmp_assign_source_1 = mod_consts[34];
        UPDATE_STRING_DICT0(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[35], tmp_assign_source_1);
    }
    {
        PyObject *tmp_assign_source_2;
        tmp_assign_source_2 = module_filename_obj;
        UPDATE_STRING_DICT0(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[36], tmp_assign_source_2);
    }
    frame_frame_bs4$_deprecation = MAKE_MODULE_FRAME(code_objects_bf290a46c2257bddeb5bc0e9a9fba6aa, module_bs4$_deprecation);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_bs4$_deprecation);
    assert(Py_REFCNT(frame_frame_bs4$_deprecation) == 2);

    // Framed code:
    {
        PyObject *tmp_assattr_value_1;
        PyObject *tmp_assattr_target_1;
        tmp_assattr_value_1 = module_filename_obj;
        tmp_assattr_target_1 = module_var_accessor_bs4$$36$_deprecation$__spec__(tstate);
        assert(!(tmp_assattr_target_1 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_1, mod_consts[37], tmp_assattr_value_1);
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
        tmp_assattr_target_2 = module_var_accessor_bs4$$36$_deprecation$__spec__(tstate);
        assert(!(tmp_assattr_target_2 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_2, mod_consts[38], tmp_assattr_value_2);
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
        UPDATE_STRING_DICT0(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[39], tmp_assign_source_3);
    }
    {
        PyObject *tmp_assign_source_4;
        tmp_assign_source_4 = IMPORT_HARD_FUNCTOOLS();
        assert(!(tmp_assign_source_4 == NULL));
        UPDATE_STRING_DICT0(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[40], tmp_assign_source_4);
    }
    {
        PyObject *tmp_assign_source_5;
        PyObject *tmp_name_value_1;
        PyObject *tmp_globals_arg_value_1;
        PyObject *tmp_locals_arg_value_1;
        PyObject *tmp_fromlist_value_1;
        PyObject *tmp_level_value_1;
        tmp_name_value_1 = mod_consts[8];
        tmp_globals_arg_value_1 = (PyObject *)moduledict_bs4$_deprecation;
        tmp_locals_arg_value_1 = Py_None;
        tmp_fromlist_value_1 = Py_None;
        tmp_level_value_1 = const_int_0;
        frame_frame_bs4$_deprecation->m_frame.f_lineno = 14;
        tmp_assign_source_5 = IMPORT_MODULE5(tstate, tmp_name_value_1, tmp_globals_arg_value_1, tmp_locals_arg_value_1, tmp_fromlist_value_1, tmp_level_value_1);
        if (tmp_assign_source_5 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 14;

            goto frame_exception_exit_1;
        }
        UPDATE_STRING_DICT1(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[8], tmp_assign_source_5);
    }
    {
        PyObject *tmp_assign_source_6;
        tmp_assign_source_6 = IMPORT_HARD_TYPING();
        assert(!(tmp_assign_source_6 == NULL));
        assert(tmp_import_from_1__module == NULL);
        Py_INCREF(tmp_assign_source_6);
        tmp_import_from_1__module = tmp_assign_source_6;
    }
    // Tried code:
    {
        PyObject *tmp_assign_source_7;
        PyObject *tmp_import_name_from_1;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_1 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_1)) {
            tmp_assign_source_7 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_1,
                (PyObject *)moduledict_bs4$_deprecation,
                mod_consts[1],
                const_int_0
            );
        } else {
            tmp_assign_source_7 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_1, mod_consts[1]);
        }

        if (tmp_assign_source_7 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 16;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[1], tmp_assign_source_7);
    }
    {
        PyObject *tmp_assign_source_8;
        PyObject *tmp_import_name_from_2;
        CHECK_OBJECT(tmp_import_from_1__module);
        tmp_import_name_from_2 = tmp_import_from_1__module;
        if (PyModule_Check(tmp_import_name_from_2)) {
            tmp_assign_source_8 = IMPORT_NAME_OR_MODULE(
                tstate,
                tmp_import_name_from_2,
                (PyObject *)moduledict_bs4$_deprecation,
                mod_consts[26],
                const_int_0
            );
        } else {
            tmp_assign_source_8 = IMPORT_NAME_FROM_MODULE(tstate, tmp_import_name_from_2, mod_consts[26]);
        }

        if (tmp_assign_source_8 == NULL) {
            assert(HAS_ERROR_OCCURRED(tstate));

            FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


            exception_lineno = 16;

            goto try_except_handler_1;
        }
        UPDATE_STRING_DICT1(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[26], tmp_assign_source_8);
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
        PyObject *tmp_annotations_1;
        tmp_annotations_1 = DICT_COPY(tstate, mod_consts[41]);


        tmp_assign_source_9 = MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__1__deprecated_alias(tstate, tmp_annotations_1);

        UPDATE_STRING_DICT1(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[42], tmp_assign_source_9);
    }
    {
        PyObject *tmp_assign_source_10;
        PyObject *tmp_annotations_2;
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[11];
        tmp_dict_value_1 = (PyObject *)&PyUnicode_Type;
        tmp_annotations_2 = _PyDict_NewPresized( 4 );
        {
            PyObject *tmp_expression_value_1;
            PyObject *tmp_subscript_value_1;
            PyObject *tmp_tuple_element_1;
            PyObject *tmp_list_element_1;
            tmp_res = PyDict_SetItem(tmp_annotations_2, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[14];
            tmp_dict_value_1 = (PyObject *)&PyUnicode_Type;
            tmp_res = PyDict_SetItem(tmp_annotations_2, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[16];
            tmp_dict_value_1 = (PyObject *)&PyUnicode_Type;
            tmp_res = PyDict_SetItem(tmp_annotations_2, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[0];
            tmp_expression_value_1 = module_var_accessor_bs4$$36$_deprecation$Callable(tstate);
            assert(!(tmp_expression_value_1 == NULL));
            tmp_list_element_1 = module_var_accessor_bs4$$36$_deprecation$Any(tstate);
            assert(!(tmp_list_element_1 == NULL));
            tmp_tuple_element_1 = MAKE_LIST_EMPTY(tstate, 1);
            PyList_SET_ITEM0(tmp_tuple_element_1, 0, tmp_list_element_1);
            tmp_subscript_value_1 = MAKE_TUPLE_EMPTY(tstate, 2);
            PyTuple_SET_ITEM(tmp_subscript_value_1, 0, tmp_tuple_element_1);
            tmp_tuple_element_1 = module_var_accessor_bs4$$36$_deprecation$Any(tstate);
            assert(!(tmp_tuple_element_1 == NULL));
            PyTuple_SET_ITEM0(tmp_subscript_value_1, 1, tmp_tuple_element_1);
            tmp_dict_value_1 = LOOKUP_SUBSCRIPT(tstate, tmp_expression_value_1, tmp_subscript_value_1);
            Py_DECREF(tmp_subscript_value_1);
            if (tmp_dict_value_1 == NULL) {
                assert(HAS_ERROR_OCCURRED(tstate));

                FETCH_ERROR_OCCURRED_STATE(tstate, &exception_state);


                exception_lineno = 53;

                goto dict_build_exception_1;
            }
            tmp_res = PyDict_SetItem(tmp_annotations_2, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
        }
        goto dict_build_noexception_1;
        // Exception handling pass through code for dict_build:
        dict_build_exception_1:;
        Py_DECREF(tmp_annotations_2);
        goto frame_exception_exit_1;
        // Finished with no exception for dict_build:
        dict_build_noexception_1:;


        tmp_assign_source_10 = MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__2__deprecated_function_alias(tstate, tmp_annotations_2);

        UPDATE_STRING_DICT1(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[43], tmp_assign_source_10);
    }
    {
        PyObject *tmp_assign_source_11;
        PyObject *tmp_annotations_3;
        PyObject *tmp_dict_key_2;
        PyObject *tmp_dict_value_2;
        tmp_dict_key_2 = mod_consts[33];
        tmp_dict_value_2 = (PyObject *)&PyUnicode_Type;
        tmp_annotations_3 = _PyDict_NewPresized( 3 );
        tmp_res = PyDict_SetItem(tmp_annotations_3, tmp_dict_key_2, tmp_dict_value_2);
        assert(!(tmp_res != 0));
        tmp_dict_key_2 = mod_consts[16];
        tmp_dict_value_2 = (PyObject *)&PyUnicode_Type;
        tmp_res = PyDict_SetItem(tmp_annotations_3, tmp_dict_key_2, tmp_dict_value_2);
        assert(!(tmp_res != 0));
        tmp_dict_key_2 = mod_consts[0];
        tmp_dict_value_2 = module_var_accessor_bs4$$36$_deprecation$Callable(tstate);
        if (unlikely(tmp_dict_value_2 == NULL)) {
            RAISE_CURRENT_EXCEPTION_NAME_ERROR(tstate, &exception_state, mod_consts[26]);
        }

        if (tmp_dict_value_2 == NULL) {
            assert(HAS_EXCEPTION_STATE(&exception_state));



            exception_lineno = 66;

            goto dict_build_exception_2;
        }
        tmp_res = PyDict_SetItem(tmp_annotations_3, tmp_dict_key_2, tmp_dict_value_2);
        assert(!(tmp_res != 0));
        goto dict_build_noexception_2;
        // Exception handling pass through code for dict_build:
        dict_build_exception_2:;
        Py_DECREF(tmp_annotations_3);
        goto frame_exception_exit_1;
        // Finished with no exception for dict_build:
        dict_build_noexception_2:;


        tmp_assign_source_11 = MAKE_FUNCTION_bs4$_deprecation$$36$$$36$$$36$function__3__deprecated(tstate, tmp_annotations_3);

        UPDATE_STRING_DICT1(moduledict_bs4$_deprecation, (Nuitka_StringObject *)mod_consts[44], tmp_assign_source_11);
    }


    // Put the previous frame back on top.
    popFrameStack(tstate);

    goto frame_no_exception_1;
    frame_exception_exit_1:


    {
        PyTracebackObject *exception_tb = GET_EXCEPTION_STATE_TRACEBACK(&exception_state);
        if (exception_tb == NULL) {
            exception_tb = MAKE_TRACEBACK(frame_frame_bs4$_deprecation, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_bs4$_deprecation->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_bs4$_deprecation, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }



    assertFrameObject(frame_frame_bs4$_deprecation);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto module_exception_exit;
    frame_no_exception_1:;

    // Report to PGO about leaving the module without error.
    PGO_onModuleExit("bs4$_deprecation", false);

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *post_load = IMPORT_EMBEDDED_MODULE(tstate, "bs4._deprecation" "-postLoad");
        if (post_load == NULL) {
            return NULL;
        }
    }
#endif

    Py_INCREF(module_bs4$_deprecation);
    return module_bs4$_deprecation;
    module_exception_exit:

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_bs4$_deprecation, (Nuitka_StringObject *)const_str_plain___name__);

        if (module_name != NULL) {
            Nuitka_DelModule(tstate, module_name);
        }
    }
#endif
    PGO_onModuleExit("bs4$_deprecation", false);

    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);
    return NULL;
}
