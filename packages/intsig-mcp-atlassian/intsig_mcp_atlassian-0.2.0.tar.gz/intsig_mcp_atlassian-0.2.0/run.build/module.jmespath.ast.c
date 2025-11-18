/* Generated code for Python module 'jmespath$ast'
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

/* The "module_jmespath$ast" is a Python object pointer of module type.
 *
 * Note: For full compatibility with CPython, every module variable access
 * needs to go through it except for cases where the module cannot possibly
 * have changed in the mean time.
 */

PyObject *module_jmespath$ast;
PyDictObject *moduledict_jmespath$ast;

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
        loadConstantsBlob(tstate, &mod_consts[0], UN_TRANSLATE("jmespath.ast"));
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
void checkModuleConstants_jmespath$ast(PyThreadState *tstate) {
    // The module may not have been used at all, then ignore this.
    if (constants_created == false) return;

    for (int i = 0; i < 50; i++) {
        assert(mod_consts_hash[i] == DEEP_HASH(tstate, mod_consts[i]));
        CHECK_OBJECT_DEEP(mod_consts[i]);
    }
}
#endif

// Helper to preserving module variables for Python3.11+
#if 1
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
static PyObject *module_var_accessor_jmespath$$36$ast$__spec__(PyThreadState *tstate) {
#if 0
    PyObject *result;

#if PYTHON_VERSION < 0x3b0
    static uint64_t dict_version = 0;
    static PyObject *cache_value = NULL;

    if (moduledict_jmespath$ast->ma_version_tag == dict_version) {
        CHECK_OBJECT_X(cache_value);
        result = cache_value;
    } else {
        dict_version = moduledict_jmespath$ast->ma_version_tag;

        result = GET_STRING_DICT_VALUE(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[49]);
        cache_value = result;
    }
#else
    static uint32_t dict_keys_version = 0xFFFFFFFF;
    static Py_ssize_t cache_dk_index = 0;

    PyDictKeysObject *dk = moduledict_jmespath$ast->ma_keys;
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
        result = GET_STRING_DICT_VALUE(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[49]);
    }
#endif

#else
    PyObject *result = GET_STRING_DICT_VALUE(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[49]);
#endif

    if (unlikely(result == NULL)) {
        result = GET_STRING_DICT_VALUE(dict_builtin, (Nuitka_StringObject *)mod_consts[49]);
    }

    return result;
}


#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
// The module code objects.
static PyCodeObject *code_objects_bec8e6f1da0d826a0eb12ca1282ee2d2;
static PyCodeObject *code_objects_ad78df5ee4b2b88b821cc2d24b09566d;
static PyCodeObject *code_objects_3a36bcb896730cb23224944b358e2f06;
static PyCodeObject *code_objects_b5417a0798f80a52d0c4d55f69068100;
static PyCodeObject *code_objects_2f8d0b409e63def2cf6d5d5ae246bce6;
static PyCodeObject *code_objects_ecb3ec86ea5f0dc35dfc31901a04364c;
static PyCodeObject *code_objects_d11c996ea8457092673c39567df93627;
static PyCodeObject *code_objects_63a61d39654bbe99316afb446262445a;
static PyCodeObject *code_objects_7ac6ff2258a0e719f89a52de04d54c59;
static PyCodeObject *code_objects_6a2ff79ce89844daeb1e1da73aaaee25;
static PyCodeObject *code_objects_0b2e2ceeca7934996a193463c6bf2fd4;
static PyCodeObject *code_objects_48766a2a88bb46335b9b12aab6d1bd97;
static PyCodeObject *code_objects_bb3a512e6ec4e5cdc7a03b62079db8d6;
static PyCodeObject *code_objects_8127aea840d660cc2aac912f716b0dc3;
static PyCodeObject *code_objects_3fe33370cdd8fa4405c1ff1314a6444a;
static PyCodeObject *code_objects_c2ab02f0e5aeb2010ef3cf2638df1171;
static PyCodeObject *code_objects_15d06aa1223eed13d07226cf8070380a;
static PyCodeObject *code_objects_fc54ebacfd64f55ac4ef4d23250dddc4;
static PyCodeObject *code_objects_b7dbe5feb461bfd62fcff6a271f5ebb4;
static PyCodeObject *code_objects_c5fcce0ca9b929129fe74cf6ee6c3cd5;
static PyCodeObject *code_objects_87bf1713df280efb7bfb7a21288c9d89;
static PyCodeObject *code_objects_2b45564bb55aa994925520115852ac11;
static PyCodeObject *code_objects_6b9e6a43c2859dba38b80405fdea0e62;

static void createModuleCodeObjects(void) {
    module_filename_obj = MAKE_RELATIVE_PATH(mod_consts[32]); CHECK_OBJECT(module_filename_obj);
    code_objects_bec8e6f1da0d826a0eb12ca1282ee2d2 = MAKE_CODE_OBJECT(module_filename_obj, 1, CO_NOFREE, mod_consts[33], mod_consts[33], NULL, NULL, 0, 0, 0);
    code_objects_ad78df5ee4b2b88b821cc2d24b09566d = MAKE_CODE_OBJECT(module_filename_obj, 65, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[18], mod_consts[18], mod_consts[34], NULL, 2, 0, 0);
    code_objects_3a36bcb896730cb23224944b358e2f06 = MAKE_CODE_OBJECT(module_filename_obj, 5, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[1], mod_consts[1], mod_consts[35], NULL, 3, 0, 0);
    code_objects_b5417a0798f80a52d0c4d55f69068100 = MAKE_CODE_OBJECT(module_filename_obj, 9, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[30], mod_consts[30], NULL, NULL, 0, 0, 0);
    code_objects_2f8d0b409e63def2cf6d5d5ae246bce6 = MAKE_CODE_OBJECT(module_filename_obj, 13, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[5], mod_consts[5], mod_consts[36], NULL, 1, 0, 0);
    code_objects_ecb3ec86ea5f0dc35dfc31901a04364c = MAKE_CODE_OBJECT(module_filename_obj, 21, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[7], mod_consts[7], mod_consts[37], NULL, 1, 0, 0);
    code_objects_d11c996ea8457092673c39567df93627 = MAKE_CODE_OBJECT(module_filename_obj, 25, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[8], mod_consts[8], mod_consts[38], NULL, 3, 0, 0);
    code_objects_63a61d39654bbe99316afb446262445a = MAKE_CODE_OBJECT(module_filename_obj, 29, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[9], mod_consts[9], mod_consts[39], NULL, 1, 0, 0);
    code_objects_7ac6ff2258a0e719f89a52de04d54c59 = MAKE_CODE_OBJECT(module_filename_obj, 17, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[6], mod_consts[6], mod_consts[40], NULL, 2, 0, 0);
    code_objects_6a2ff79ce89844daeb1e1da73aaaee25 = MAKE_CODE_OBJECT(module_filename_obj, 33, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[31], mod_consts[31], NULL, NULL, 0, 0, 0);
    code_objects_0b2e2ceeca7934996a193463c6bf2fd4 = MAKE_CODE_OBJECT(module_filename_obj, 37, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[11], mod_consts[11], mod_consts[41], NULL, 1, 0, 0);
    code_objects_48766a2a88bb46335b9b12aab6d1bd97 = MAKE_CODE_OBJECT(module_filename_obj, 41, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[12], mod_consts[12], mod_consts[42], NULL, 1, 0, 0);
    code_objects_bb3a512e6ec4e5cdc7a03b62079db8d6 = MAKE_CODE_OBJECT(module_filename_obj, 45, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[13], mod_consts[13], mod_consts[43], NULL, 2, 0, 0);
    code_objects_8127aea840d660cc2aac912f716b0dc3 = MAKE_CODE_OBJECT(module_filename_obj, 49, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[14], mod_consts[14], mod_consts[44], NULL, 1, 0, 0);
    code_objects_3fe33370cdd8fa4405c1ff1314a6444a = MAKE_CODE_OBJECT(module_filename_obj, 53, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[15], mod_consts[15], mod_consts[45], NULL, 1, 0, 0);
    code_objects_c2ab02f0e5aeb2010ef3cf2638df1171 = MAKE_CODE_OBJECT(module_filename_obj, 57, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[16], mod_consts[16], mod_consts[45], NULL, 1, 0, 0);
    code_objects_15d06aa1223eed13d07226cf8070380a = MAKE_CODE_OBJECT(module_filename_obj, 69, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[19], mod_consts[19], mod_consts[46], NULL, 1, 0, 0);
    code_objects_fc54ebacfd64f55ac4ef4d23250dddc4 = MAKE_CODE_OBJECT(module_filename_obj, 61, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[17], mod_consts[17], mod_consts[34], NULL, 2, 0, 0);
    code_objects_b7dbe5feb461bfd62fcff6a271f5ebb4 = MAKE_CODE_OBJECT(module_filename_obj, 73, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[20], mod_consts[20], mod_consts[34], NULL, 2, 0, 0);
    code_objects_c5fcce0ca9b929129fe74cf6ee6c3cd5 = MAKE_CODE_OBJECT(module_filename_obj, 77, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[21], mod_consts[21], mod_consts[34], NULL, 2, 0, 0);
    code_objects_87bf1713df280efb7bfb7a21288c9d89 = MAKE_CODE_OBJECT(module_filename_obj, 85, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[23], mod_consts[23], mod_consts[47], NULL, 3, 0, 0);
    code_objects_2b45564bb55aa994925520115852ac11 = MAKE_CODE_OBJECT(module_filename_obj, 81, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[22], mod_consts[22], mod_consts[42], NULL, 1, 0, 0);
    code_objects_6b9e6a43c2859dba38b80405fdea0e62 = MAKE_CODE_OBJECT(module_filename_obj, 89, CO_OPTIMIZED | CO_NEWLOCALS | CO_NOFREE, mod_consts[24], mod_consts[24], mod_consts[34], NULL, 2, 0, 0);
}
#endif

// The module function declarations.
static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__10_index_expression(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__11_key_val_pair(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__12_literal(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__13_multi_select_dict(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__14_multi_select_list(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__15_or_expression(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__16_and_expression(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__17_not_expression(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__18_pipe(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__19_projection(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__1_comparator(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__20_subexpression(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__21_slice(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__22_value_projection(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__2_current_node(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__3_expref(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__4_function_expression(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__5_field(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__6_filter_projection(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__7_flatten(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__8_identity(PyThreadState *tstate);


static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__9_index(PyThreadState *tstate);


// The module function definitions.
static PyObject *impl_jmespath$ast$$36$$$36$$$36$function__1_comparator(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_name = python_pars[0];
    PyObject *par_first = python_pars[1];
    PyObject *par_second = python_pars[2];
    PyObject *tmp_return_value = NULL;
    int tmp_res;

    // Actual function body.
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = mod_consts[1];
        tmp_return_value = _PyDict_NewPresized( 3 );
        {
            PyObject *tmp_list_element_1;
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[2];
            CHECK_OBJECT(par_first);
            tmp_list_element_1 = par_first;
            tmp_dict_value_1 = MAKE_LIST_EMPTY(tstate, 2);
            PyList_SET_ITEM0(tmp_dict_value_1, 0, tmp_list_element_1);
            CHECK_OBJECT(par_second);
            tmp_list_element_1 = par_second;
            PyList_SET_ITEM0(tmp_dict_value_1, 1, tmp_list_element_1);
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[3];
            CHECK_OBJECT(par_name);
            tmp_dict_value_1 = par_name;
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
        }
        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_name);
    Py_DECREF(par_name);
    CHECK_OBJECT(par_first);
    Py_DECREF(par_first);
    CHECK_OBJECT(par_second);
    Py_DECREF(par_second);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_jmespath$ast$$36$$$36$$$36$function__2_current_node(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *tmp_return_value = NULL;

    // Actual function body.
    tmp_return_value = DEEP_COPY_DICT(tstate, mod_consts[4]);
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


static PyObject *impl_jmespath$ast$$36$$$36$$$36$function__3_expref(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_expression = python_pars[0];
    PyObject *tmp_return_value = NULL;
    int tmp_res;

    // Actual function body.
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = mod_consts[5];
        tmp_return_value = _PyDict_NewPresized( 2 );
        {
            PyObject *tmp_list_element_1;
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[2];
            CHECK_OBJECT(par_expression);
            tmp_list_element_1 = par_expression;
            tmp_dict_value_1 = MAKE_LIST_EMPTY(tstate, 1);
            PyList_SET_ITEM0(tmp_dict_value_1, 0, tmp_list_element_1);
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
        }
        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_expression);
    Py_DECREF(par_expression);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_jmespath$ast$$36$$$36$$$36$function__4_function_expression(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_name = python_pars[0];
    PyObject *par_args = python_pars[1];
    PyObject *tmp_return_value = NULL;
    int tmp_res;

    // Actual function body.
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = mod_consts[6];
        tmp_return_value = _PyDict_NewPresized( 3 );
        tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[2];
        CHECK_OBJECT(par_args);
        tmp_dict_value_1 = par_args;
        tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[3];
        CHECK_OBJECT(par_name);
        tmp_dict_value_1 = par_name;
        tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_name);
    Py_DECREF(par_name);
    CHECK_OBJECT(par_args);
    Py_DECREF(par_args);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_jmespath$ast$$36$$$36$$$36$function__5_field(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_name = python_pars[0];
    PyObject *tmp_return_value = NULL;
    int tmp_res;

    // Actual function body.
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = mod_consts[7];
        tmp_return_value = _PyDict_NewPresized( 3 );
        tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[2];
        tmp_dict_value_1 = MAKE_LIST_EMPTY(tstate, 0);
        tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
        Py_DECREF(tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[3];
        CHECK_OBJECT(par_name);
        tmp_dict_value_1 = par_name;
        tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_name);
    Py_DECREF(par_name);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_jmespath$ast$$36$$$36$$$36$function__6_filter_projection(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_left = python_pars[0];
    PyObject *par_right = python_pars[1];
    PyObject *par_comparator = python_pars[2];
    PyObject *tmp_return_value = NULL;
    int tmp_res;

    // Actual function body.
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = mod_consts[8];
        tmp_return_value = _PyDict_NewPresized( 2 );
        {
            PyObject *tmp_list_element_1;
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[2];
            CHECK_OBJECT(par_left);
            tmp_list_element_1 = par_left;
            tmp_dict_value_1 = MAKE_LIST_EMPTY(tstate, 3);
            PyList_SET_ITEM0(tmp_dict_value_1, 0, tmp_list_element_1);
            CHECK_OBJECT(par_right);
            tmp_list_element_1 = par_right;
            PyList_SET_ITEM0(tmp_dict_value_1, 1, tmp_list_element_1);
            CHECK_OBJECT(par_comparator);
            tmp_list_element_1 = par_comparator;
            PyList_SET_ITEM0(tmp_dict_value_1, 2, tmp_list_element_1);
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
        }
        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_left);
    Py_DECREF(par_left);
    CHECK_OBJECT(par_right);
    Py_DECREF(par_right);
    CHECK_OBJECT(par_comparator);
    Py_DECREF(par_comparator);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_jmespath$ast$$36$$$36$$$36$function__7_flatten(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_node = python_pars[0];
    PyObject *tmp_return_value = NULL;
    int tmp_res;

    // Actual function body.
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = mod_consts[9];
        tmp_return_value = _PyDict_NewPresized( 2 );
        {
            PyObject *tmp_list_element_1;
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[2];
            CHECK_OBJECT(par_node);
            tmp_list_element_1 = par_node;
            tmp_dict_value_1 = MAKE_LIST_EMPTY(tstate, 1);
            PyList_SET_ITEM0(tmp_dict_value_1, 0, tmp_list_element_1);
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
        }
        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_node);
    Py_DECREF(par_node);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_jmespath$ast$$36$$$36$$$36$function__8_identity(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *tmp_return_value = NULL;

    // Actual function body.
    tmp_return_value = DEEP_COPY_DICT(tstate, mod_consts[10]);
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


static PyObject *impl_jmespath$ast$$36$$$36$$$36$function__9_index(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_index = python_pars[0];
    PyObject *tmp_return_value = NULL;
    int tmp_res;

    // Actual function body.
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = mod_consts[11];
        tmp_return_value = _PyDict_NewPresized( 3 );
        tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[3];
        CHECK_OBJECT(par_index);
        tmp_dict_value_1 = par_index;
        tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[2];
        tmp_dict_value_1 = MAKE_LIST_EMPTY(tstate, 0);
        tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
        Py_DECREF(tmp_dict_value_1);
        assert(!(tmp_res != 0));
        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_index);
    Py_DECREF(par_index);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_jmespath$ast$$36$$$36$$$36$function__10_index_expression(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_children = python_pars[0];
    PyObject *tmp_return_value = NULL;
    int tmp_res;

    // Actual function body.
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = mod_consts[12];
        tmp_return_value = _PyDict_NewPresized( 2 );
        tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[2];
        CHECK_OBJECT(par_children);
        tmp_dict_value_1 = par_children;
        tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_children);
    Py_DECREF(par_children);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_jmespath$ast$$36$$$36$$$36$function__11_key_val_pair(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_key_name = python_pars[0];
    PyObject *par_node = python_pars[1];
    PyObject *tmp_return_value = NULL;
    int tmp_res;

    // Actual function body.
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = mod_consts[13];
        tmp_return_value = _PyDict_NewPresized( 3 );
        {
            PyObject *tmp_list_element_1;
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[2];
            CHECK_OBJECT(par_node);
            tmp_list_element_1 = par_node;
            tmp_dict_value_1 = MAKE_LIST_EMPTY(tstate, 1);
            PyList_SET_ITEM0(tmp_dict_value_1, 0, tmp_list_element_1);
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[3];
            CHECK_OBJECT(par_key_name);
            tmp_dict_value_1 = par_key_name;
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
        }
        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_key_name);
    Py_DECREF(par_key_name);
    CHECK_OBJECT(par_node);
    Py_DECREF(par_node);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_jmespath$ast$$36$$$36$$$36$function__12_literal(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_literal_value = python_pars[0];
    PyObject *tmp_return_value = NULL;
    int tmp_res;

    // Actual function body.
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = mod_consts[14];
        tmp_return_value = _PyDict_NewPresized( 3 );
        tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[3];
        CHECK_OBJECT(par_literal_value);
        tmp_dict_value_1 = par_literal_value;
        tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[2];
        tmp_dict_value_1 = MAKE_LIST_EMPTY(tstate, 0);
        tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
        Py_DECREF(tmp_dict_value_1);
        assert(!(tmp_res != 0));
        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_literal_value);
    Py_DECREF(par_literal_value);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_jmespath$ast$$36$$$36$$$36$function__13_multi_select_dict(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_nodes = python_pars[0];
    PyObject *tmp_return_value = NULL;
    int tmp_res;

    // Actual function body.
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = mod_consts[15];
        tmp_return_value = _PyDict_NewPresized( 2 );
        tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[2];
        CHECK_OBJECT(par_nodes);
        tmp_dict_value_1 = par_nodes;
        tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_nodes);
    Py_DECREF(par_nodes);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_jmespath$ast$$36$$$36$$$36$function__14_multi_select_list(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_nodes = python_pars[0];
    PyObject *tmp_return_value = NULL;
    int tmp_res;

    // Actual function body.
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = mod_consts[16];
        tmp_return_value = _PyDict_NewPresized( 2 );
        tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[2];
        CHECK_OBJECT(par_nodes);
        tmp_dict_value_1 = par_nodes;
        tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_nodes);
    Py_DECREF(par_nodes);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_jmespath$ast$$36$$$36$$$36$function__15_or_expression(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_left = python_pars[0];
    PyObject *par_right = python_pars[1];
    PyObject *tmp_return_value = NULL;
    int tmp_res;

    // Actual function body.
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = mod_consts[17];
        tmp_return_value = _PyDict_NewPresized( 2 );
        {
            PyObject *tmp_list_element_1;
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[2];
            CHECK_OBJECT(par_left);
            tmp_list_element_1 = par_left;
            tmp_dict_value_1 = MAKE_LIST_EMPTY(tstate, 2);
            PyList_SET_ITEM0(tmp_dict_value_1, 0, tmp_list_element_1);
            CHECK_OBJECT(par_right);
            tmp_list_element_1 = par_right;
            PyList_SET_ITEM0(tmp_dict_value_1, 1, tmp_list_element_1);
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
        }
        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_left);
    Py_DECREF(par_left);
    CHECK_OBJECT(par_right);
    Py_DECREF(par_right);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_jmespath$ast$$36$$$36$$$36$function__16_and_expression(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_left = python_pars[0];
    PyObject *par_right = python_pars[1];
    PyObject *tmp_return_value = NULL;
    int tmp_res;

    // Actual function body.
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = mod_consts[18];
        tmp_return_value = _PyDict_NewPresized( 2 );
        {
            PyObject *tmp_list_element_1;
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[2];
            CHECK_OBJECT(par_left);
            tmp_list_element_1 = par_left;
            tmp_dict_value_1 = MAKE_LIST_EMPTY(tstate, 2);
            PyList_SET_ITEM0(tmp_dict_value_1, 0, tmp_list_element_1);
            CHECK_OBJECT(par_right);
            tmp_list_element_1 = par_right;
            PyList_SET_ITEM0(tmp_dict_value_1, 1, tmp_list_element_1);
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
        }
        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_left);
    Py_DECREF(par_left);
    CHECK_OBJECT(par_right);
    Py_DECREF(par_right);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_jmespath$ast$$36$$$36$$$36$function__17_not_expression(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_expr = python_pars[0];
    PyObject *tmp_return_value = NULL;
    int tmp_res;

    // Actual function body.
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = mod_consts[19];
        tmp_return_value = _PyDict_NewPresized( 2 );
        {
            PyObject *tmp_list_element_1;
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[2];
            CHECK_OBJECT(par_expr);
            tmp_list_element_1 = par_expr;
            tmp_dict_value_1 = MAKE_LIST_EMPTY(tstate, 1);
            PyList_SET_ITEM0(tmp_dict_value_1, 0, tmp_list_element_1);
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
        }
        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_expr);
    Py_DECREF(par_expr);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_jmespath$ast$$36$$$36$$$36$function__18_pipe(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_left = python_pars[0];
    PyObject *par_right = python_pars[1];
    PyObject *tmp_return_value = NULL;
    int tmp_res;

    // Actual function body.
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = mod_consts[20];
        tmp_return_value = _PyDict_NewPresized( 2 );
        {
            PyObject *tmp_list_element_1;
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[2];
            CHECK_OBJECT(par_left);
            tmp_list_element_1 = par_left;
            tmp_dict_value_1 = MAKE_LIST_EMPTY(tstate, 2);
            PyList_SET_ITEM0(tmp_dict_value_1, 0, tmp_list_element_1);
            CHECK_OBJECT(par_right);
            tmp_list_element_1 = par_right;
            PyList_SET_ITEM0(tmp_dict_value_1, 1, tmp_list_element_1);
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
        }
        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_left);
    Py_DECREF(par_left);
    CHECK_OBJECT(par_right);
    Py_DECREF(par_right);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_jmespath$ast$$36$$$36$$$36$function__19_projection(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_left = python_pars[0];
    PyObject *par_right = python_pars[1];
    PyObject *tmp_return_value = NULL;
    int tmp_res;

    // Actual function body.
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = mod_consts[21];
        tmp_return_value = _PyDict_NewPresized( 2 );
        {
            PyObject *tmp_list_element_1;
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[2];
            CHECK_OBJECT(par_left);
            tmp_list_element_1 = par_left;
            tmp_dict_value_1 = MAKE_LIST_EMPTY(tstate, 2);
            PyList_SET_ITEM0(tmp_dict_value_1, 0, tmp_list_element_1);
            CHECK_OBJECT(par_right);
            tmp_list_element_1 = par_right;
            PyList_SET_ITEM0(tmp_dict_value_1, 1, tmp_list_element_1);
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
        }
        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_left);
    Py_DECREF(par_left);
    CHECK_OBJECT(par_right);
    Py_DECREF(par_right);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_jmespath$ast$$36$$$36$$$36$function__20_subexpression(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_children = python_pars[0];
    PyObject *tmp_return_value = NULL;
    int tmp_res;

    // Actual function body.
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = mod_consts[22];
        tmp_return_value = _PyDict_NewPresized( 2 );
        tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        tmp_dict_key_1 = mod_consts[2];
        CHECK_OBJECT(par_children);
        tmp_dict_value_1 = par_children;
        tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
        assert(!(tmp_res != 0));
        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_children);
    Py_DECREF(par_children);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_jmespath$ast$$36$$$36$$$36$function__21_slice(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_start = python_pars[0];
    PyObject *par_end = python_pars[1];
    PyObject *par_step = python_pars[2];
    PyObject *tmp_return_value = NULL;
    int tmp_res;

    // Actual function body.
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = mod_consts[23];
        tmp_return_value = _PyDict_NewPresized( 2 );
        {
            PyObject *tmp_list_element_1;
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[2];
            CHECK_OBJECT(par_start);
            tmp_list_element_1 = par_start;
            tmp_dict_value_1 = MAKE_LIST_EMPTY(tstate, 3);
            PyList_SET_ITEM0(tmp_dict_value_1, 0, tmp_list_element_1);
            CHECK_OBJECT(par_end);
            tmp_list_element_1 = par_end;
            PyList_SET_ITEM0(tmp_dict_value_1, 1, tmp_list_element_1);
            CHECK_OBJECT(par_step);
            tmp_list_element_1 = par_step;
            PyList_SET_ITEM0(tmp_dict_value_1, 2, tmp_list_element_1);
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
        }
        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_start);
    Py_DECREF(par_start);
    CHECK_OBJECT(par_end);
    Py_DECREF(par_end);
    CHECK_OBJECT(par_step);
    Py_DECREF(par_step);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}


static PyObject *impl_jmespath$ast$$36$$$36$$$36$function__22_value_projection(PyThreadState *tstate, struct Nuitka_FunctionObject const *self, PyObject **python_pars) {
    // Preserve error status for checks
#ifndef __NUITKA_NO_ASSERT__
    NUITKA_MAY_BE_UNUSED bool had_error = HAS_ERROR_OCCURRED(tstate);
#endif

    // Local variable declarations.
    PyObject *par_left = python_pars[0];
    PyObject *par_right = python_pars[1];
    PyObject *tmp_return_value = NULL;
    int tmp_res;

    // Actual function body.
    {
        PyObject *tmp_dict_key_1;
        PyObject *tmp_dict_value_1;
        tmp_dict_key_1 = mod_consts[0];
        tmp_dict_value_1 = mod_consts[24];
        tmp_return_value = _PyDict_NewPresized( 2 );
        {
            PyObject *tmp_list_element_1;
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            assert(!(tmp_res != 0));
            tmp_dict_key_1 = mod_consts[2];
            CHECK_OBJECT(par_left);
            tmp_list_element_1 = par_left;
            tmp_dict_value_1 = MAKE_LIST_EMPTY(tstate, 2);
            PyList_SET_ITEM0(tmp_dict_value_1, 0, tmp_list_element_1);
            CHECK_OBJECT(par_right);
            tmp_list_element_1 = par_right;
            PyList_SET_ITEM0(tmp_dict_value_1, 1, tmp_list_element_1);
            tmp_res = PyDict_SetItem(tmp_return_value, tmp_dict_key_1, tmp_dict_value_1);
            Py_DECREF(tmp_dict_value_1);
            assert(!(tmp_res != 0));
        }
        goto function_return_exit;
    }

    NUITKA_CANNOT_GET_HERE("Return statement must have exited already.");
    return NULL;


function_return_exit:
   // Function cleanup code if any.
    CHECK_OBJECT(par_left);
    Py_DECREF(par_left);
    CHECK_OBJECT(par_right);
    Py_DECREF(par_right);

   // Actual function exit with return value, making sure we did not make
   // the error status worse despite non-NULL return.
   CHECK_OBJECT(tmp_return_value);
   assert(had_error || !HAS_ERROR_OCCURRED(tstate));
   return tmp_return_value;
}



static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__10_index_expression(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_jmespath$ast$$36$$$36$$$36$function__10_index_expression,
        mod_consts[12],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_48766a2a88bb46335b9b12aab6d1bd97,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_jmespath$ast,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__11_key_val_pair(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_jmespath$ast$$36$$$36$$$36$function__11_key_val_pair,
        mod_consts[13],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_bb3a512e6ec4e5cdc7a03b62079db8d6,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_jmespath$ast,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__12_literal(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_jmespath$ast$$36$$$36$$$36$function__12_literal,
        mod_consts[14],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_8127aea840d660cc2aac912f716b0dc3,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_jmespath$ast,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__13_multi_select_dict(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_jmespath$ast$$36$$$36$$$36$function__13_multi_select_dict,
        mod_consts[15],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_3fe33370cdd8fa4405c1ff1314a6444a,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_jmespath$ast,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__14_multi_select_list(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_jmespath$ast$$36$$$36$$$36$function__14_multi_select_list,
        mod_consts[16],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_c2ab02f0e5aeb2010ef3cf2638df1171,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_jmespath$ast,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__15_or_expression(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_jmespath$ast$$36$$$36$$$36$function__15_or_expression,
        mod_consts[17],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_fc54ebacfd64f55ac4ef4d23250dddc4,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_jmespath$ast,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__16_and_expression(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_jmespath$ast$$36$$$36$$$36$function__16_and_expression,
        mod_consts[18],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_ad78df5ee4b2b88b821cc2d24b09566d,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_jmespath$ast,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__17_not_expression(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_jmespath$ast$$36$$$36$$$36$function__17_not_expression,
        mod_consts[19],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_15d06aa1223eed13d07226cf8070380a,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_jmespath$ast,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__18_pipe(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_jmespath$ast$$36$$$36$$$36$function__18_pipe,
        mod_consts[20],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_b7dbe5feb461bfd62fcff6a271f5ebb4,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_jmespath$ast,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__19_projection(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_jmespath$ast$$36$$$36$$$36$function__19_projection,
        mod_consts[21],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_c5fcce0ca9b929129fe74cf6ee6c3cd5,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_jmespath$ast,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__1_comparator(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_jmespath$ast$$36$$$36$$$36$function__1_comparator,
        mod_consts[1],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_3a36bcb896730cb23224944b358e2f06,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_jmespath$ast,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__20_subexpression(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_jmespath$ast$$36$$$36$$$36$function__20_subexpression,
        mod_consts[22],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_2b45564bb55aa994925520115852ac11,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_jmespath$ast,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__21_slice(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_jmespath$ast$$36$$$36$$$36$function__21_slice,
        mod_consts[23],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_87bf1713df280efb7bfb7a21288c9d89,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_jmespath$ast,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__22_value_projection(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_jmespath$ast$$36$$$36$$$36$function__22_value_projection,
        mod_consts[24],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_6b9e6a43c2859dba38b80405fdea0e62,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_jmespath$ast,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__2_current_node(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_jmespath$ast$$36$$$36$$$36$function__2_current_node,
        mod_consts[30],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_b5417a0798f80a52d0c4d55f69068100,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_jmespath$ast,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__3_expref(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_jmespath$ast$$36$$$36$$$36$function__3_expref,
        mod_consts[5],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_2f8d0b409e63def2cf6d5d5ae246bce6,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_jmespath$ast,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__4_function_expression(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_jmespath$ast$$36$$$36$$$36$function__4_function_expression,
        mod_consts[6],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_7ac6ff2258a0e719f89a52de04d54c59,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_jmespath$ast,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__5_field(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_jmespath$ast$$36$$$36$$$36$function__5_field,
        mod_consts[7],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_ecb3ec86ea5f0dc35dfc31901a04364c,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_jmespath$ast,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__6_filter_projection(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_jmespath$ast$$36$$$36$$$36$function__6_filter_projection,
        mod_consts[8],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_d11c996ea8457092673c39567df93627,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_jmespath$ast,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__7_flatten(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_jmespath$ast$$36$$$36$$$36$function__7_flatten,
        mod_consts[9],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_63a61d39654bbe99316afb446262445a,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_jmespath$ast,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__8_identity(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_jmespath$ast$$36$$$36$$$36$function__8_identity,
        mod_consts[31],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_6a2ff79ce89844daeb1e1da73aaaee25,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_jmespath$ast,
        NULL,
        NULL,
        0
    );


    return (PyObject *)result;
}



static PyObject *MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__9_index(PyThreadState *tstate) {
    struct Nuitka_FunctionObject *result = Nuitka_Function_New(
        impl_jmespath$ast$$36$$$36$$$36$function__9_index,
        mod_consts[11],
#if PYTHON_VERSION >= 0x300
        NULL,
#endif
        code_objects_0b2e2ceeca7934996a193463c6bf2fd4,
        NULL,
#if PYTHON_VERSION >= 0x300
        NULL,
        NULL,
#endif
        module_jmespath$ast,
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

static function_impl_code const function_table_jmespath$ast[] = {
    impl_jmespath$ast$$36$$$36$$$36$function__1_comparator,
    impl_jmespath$ast$$36$$$36$$$36$function__2_current_node,
    impl_jmespath$ast$$36$$$36$$$36$function__3_expref,
    impl_jmespath$ast$$36$$$36$$$36$function__4_function_expression,
    impl_jmespath$ast$$36$$$36$$$36$function__5_field,
    impl_jmespath$ast$$36$$$36$$$36$function__6_filter_projection,
    impl_jmespath$ast$$36$$$36$$$36$function__7_flatten,
    impl_jmespath$ast$$36$$$36$$$36$function__8_identity,
    impl_jmespath$ast$$36$$$36$$$36$function__9_index,
    impl_jmespath$ast$$36$$$36$$$36$function__10_index_expression,
    impl_jmespath$ast$$36$$$36$$$36$function__11_key_val_pair,
    impl_jmespath$ast$$36$$$36$$$36$function__12_literal,
    impl_jmespath$ast$$36$$$36$$$36$function__13_multi_select_dict,
    impl_jmespath$ast$$36$$$36$$$36$function__14_multi_select_list,
    impl_jmespath$ast$$36$$$36$$$36$function__15_or_expression,
    impl_jmespath$ast$$36$$$36$$$36$function__16_and_expression,
    impl_jmespath$ast$$36$$$36$$$36$function__17_not_expression,
    impl_jmespath$ast$$36$$$36$$$36$function__18_pipe,
    impl_jmespath$ast$$36$$$36$$$36$function__19_projection,
    impl_jmespath$ast$$36$$$36$$$36$function__20_subexpression,
    impl_jmespath$ast$$36$$$36$$$36$function__21_slice,
    impl_jmespath$ast$$36$$$36$$$36$function__22_value_projection,
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

    return Nuitka_Function_GetFunctionState(function, function_table_jmespath$ast);
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
        module_jmespath$ast,
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
        function_table_jmespath$ast,
        sizeof(function_table_jmespath$ast) / sizeof(function_impl_code)
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
static char const *module_full_name = "jmespath.ast";
#endif

// Internal entry point for module code.
PyObject *modulecode_jmespath$ast(PyThreadState *tstate, PyObject *module, struct Nuitka_MetaPathBasedLoaderEntry const *loader_entry) {
    // Report entry to PGO.
    PGO_onModuleEntered("jmespath$ast");

    // Store the module for future use.
    module_jmespath$ast = module;

    moduledict_jmespath$ast = MODULE_DICT(module_jmespath$ast);

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
        PRINT_STRING("jmespath$ast: Calling setupMetaPathBasedLoader().\n");
#endif
        setupMetaPathBasedLoader(tstate);
#if 0 >= 0
#ifdef _NUITKA_TRACE
        PRINT_STRING("jmespath$ast: Calling updateMetaPathBasedLoaderModuleRoot().\n");
#endif
        updateMetaPathBasedLoaderModuleRoot(module_full_name);
#endif


#if PYTHON_VERSION >= 0x300
        patchInspectModule(tstate);
#endif

#endif

        /* The constants only used by this module are created now. */
        NUITKA_PRINT_TRACE("jmespath$ast: Calling createModuleConstants().\n");
        createModuleConstants(tstate);

#if !defined(_NUITKA_EXPERIMENTAL_NEW_CODE_OBJECTS)
        createModuleCodeObjects();
#endif
        init_done = true;
    }

#if _NUITKA_MODULE_MODE && 0
    PyObject *pre_load = IMPORT_EMBEDDED_MODULE(tstate, "jmespath.ast" "-preLoad");
    if (pre_load == NULL) {
        return NULL;
    }
#endif

    // PRINT_STRING("in initjmespath$ast\n");

#ifdef _NUITKA_PLUGIN_DILL_ENABLED
    {
        char const *module_name_c;
        if (loader_entry != NULL) {
            module_name_c = loader_entry->name;
        } else {
            PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_jmespath$ast, (Nuitka_StringObject *)const_str_plain___name__);
            module_name_c = Nuitka_String_AsString(module_name);
        }

        registerDillPluginTables(tstate, module_name_c, &_method_def_reduce_compiled_function, &_method_def_create_compiled_function);
    }
#endif

    // Set "__compiled__" to what version information we have.
    UPDATE_STRING_DICT0(
        moduledict_jmespath$ast,
        (Nuitka_StringObject *)const_str_plain___compiled__,
        Nuitka_dunder_compiled_value
    );

    // Update "__package__" value to what it ought to be.
    {
#if 0
        UPDATE_STRING_DICT0(
            moduledict_jmespath$ast,
            (Nuitka_StringObject *)const_str_plain___package__,
            mod_consts[48]
        );
#elif 0
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_jmespath$ast, (Nuitka_StringObject *)const_str_plain___name__);

        UPDATE_STRING_DICT0(
            moduledict_jmespath$ast,
            (Nuitka_StringObject *)const_str_plain___package__,
            module_name
        );
#else

#if PYTHON_VERSION < 0x300
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_jmespath$ast, (Nuitka_StringObject *)const_str_plain___name__);
        char const *module_name_cstr = PyString_AS_STRING(module_name);

        char const *last_dot = strrchr(module_name_cstr, '.');

        if (last_dot != NULL) {
            UPDATE_STRING_DICT1(
                moduledict_jmespath$ast,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyString_FromStringAndSize(module_name_cstr, last_dot - module_name_cstr)
            );
        }
#else
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_jmespath$ast, (Nuitka_StringObject *)const_str_plain___name__);
        Py_ssize_t dot_index = PyUnicode_Find(module_name, const_str_dot, 0, PyUnicode_GetLength(module_name), -1);

        if (dot_index != -1) {
            UPDATE_STRING_DICT1(
                moduledict_jmespath$ast,
                (Nuitka_StringObject *)const_str_plain___package__,
                PyUnicode_Substring(module_name, 0, dot_index)
            );
        }
#endif
#endif
    }

    CHECK_OBJECT(module_jmespath$ast);

    // For deep importing of a module we need to have "__builtins__", so we set
    // it ourselves in the same way than CPython does. Note: This must be done
    // before the frame object is allocated, or else it may fail.

    if (GET_STRING_DICT_VALUE(moduledict_jmespath$ast, (Nuitka_StringObject *)const_str_plain___builtins__) == NULL) {
        PyObject *value = (PyObject *)builtin_module;

        // Check if main module, not a dict then but the module itself.
#if _NUITKA_MODULE_MODE || !0
        value = PyModule_GetDict(value);
#endif

        UPDATE_STRING_DICT0(moduledict_jmespath$ast, (Nuitka_StringObject *)const_str_plain___builtins__, value);
    }

    PyObject *module_loader = Nuitka_Loader_New(loader_entry);
    UPDATE_STRING_DICT0(moduledict_jmespath$ast, (Nuitka_StringObject *)const_str_plain___loader__, module_loader);

#if PYTHON_VERSION >= 0x300
// Set the "__spec__" value

#if 0
    // Main modules just get "None" as spec.
    UPDATE_STRING_DICT0(moduledict_jmespath$ast, (Nuitka_StringObject *)const_str_plain___spec__, Py_None);
#else
    // Other modules get a "ModuleSpec" from the standard mechanism.
    {
        PyObject *bootstrap_module = getImportLibBootstrapModule();
        CHECK_OBJECT(bootstrap_module);

        PyObject *_spec_from_module = PyObject_GetAttrString(bootstrap_module, "_spec_from_module");
        CHECK_OBJECT(_spec_from_module);

        PyObject *spec_value = CALL_FUNCTION_WITH_SINGLE_ARG(tstate, _spec_from_module, module_jmespath$ast);
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

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)const_str_plain___spec__, spec_value);
    }
#endif
#endif

    // Temp variables if any
    struct Nuitka_FrameObject *frame_frame_jmespath$ast;
    NUITKA_MAY_BE_UNUSED char const *type_description_1 = NULL;
    bool tmp_result;
    struct Nuitka_ExceptionPreservationItem exception_state = Empty_Nuitka_ExceptionPreservationItem;
    NUITKA_MAY_BE_UNUSED int exception_lineno = 0;

    // Module init code if any


    // Module code.
    {
        PyObject *tmp_assign_source_1;
        tmp_assign_source_1 = Py_None;
        UPDATE_STRING_DICT0(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[25], tmp_assign_source_1);
    }
    {
        PyObject *tmp_assign_source_2;
        tmp_assign_source_2 = module_filename_obj;
        UPDATE_STRING_DICT0(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[26], tmp_assign_source_2);
    }
    frame_frame_jmespath$ast = MAKE_MODULE_FRAME(code_objects_bec8e6f1da0d826a0eb12ca1282ee2d2, module_jmespath$ast);

    // Push the new frame as the currently active one, and we should be exclusively
    // owning it.
    pushFrameStackCompiledFrame(tstate, frame_frame_jmespath$ast);
    assert(Py_REFCNT(frame_frame_jmespath$ast) == 2);

    // Framed code:
    {
        PyObject *tmp_assattr_value_1;
        PyObject *tmp_assattr_target_1;
        tmp_assattr_value_1 = module_filename_obj;
        tmp_assattr_target_1 = module_var_accessor_jmespath$$36$ast$__spec__(tstate);
        assert(!(tmp_assattr_target_1 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_1, mod_consts[27], tmp_assattr_value_1);
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
        tmp_assattr_target_2 = module_var_accessor_jmespath$$36$ast$__spec__(tstate);
        assert(!(tmp_assattr_target_2 == NULL));
        tmp_result = SET_ATTRIBUTE(tstate, tmp_assattr_target_2, mod_consts[28], tmp_assattr_value_2);
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
            exception_tb = MAKE_TRACEBACK(frame_frame_jmespath$ast, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        } else if (exception_tb->tb_frame != &frame_frame_jmespath$ast->m_frame) {
            exception_tb = ADD_TRACEBACK(exception_tb, frame_frame_jmespath$ast, exception_lineno);
            SET_EXCEPTION_STATE_TRACEBACK(&exception_state, exception_tb);
        }
    }



    assertFrameObject(frame_frame_jmespath$ast);

    // Put the previous frame back on top.
    popFrameStack(tstate);

    // Return the error.
    goto module_exception_exit;
    frame_no_exception_1:;
    {
        PyObject *tmp_assign_source_3;
        tmp_assign_source_3 = Py_None;
        UPDATE_STRING_DICT0(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[29], tmp_assign_source_3);
    }
    {
        PyObject *tmp_assign_source_4;


        tmp_assign_source_4 = MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__1_comparator(tstate);

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[1], tmp_assign_source_4);
    }
    {
        PyObject *tmp_assign_source_5;


        tmp_assign_source_5 = MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__2_current_node(tstate);

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[30], tmp_assign_source_5);
    }
    {
        PyObject *tmp_assign_source_6;


        tmp_assign_source_6 = MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__3_expref(tstate);

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[5], tmp_assign_source_6);
    }
    {
        PyObject *tmp_assign_source_7;


        tmp_assign_source_7 = MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__4_function_expression(tstate);

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[6], tmp_assign_source_7);
    }
    {
        PyObject *tmp_assign_source_8;


        tmp_assign_source_8 = MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__5_field(tstate);

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[7], tmp_assign_source_8);
    }
    {
        PyObject *tmp_assign_source_9;


        tmp_assign_source_9 = MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__6_filter_projection(tstate);

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[8], tmp_assign_source_9);
    }
    {
        PyObject *tmp_assign_source_10;


        tmp_assign_source_10 = MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__7_flatten(tstate);

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[9], tmp_assign_source_10);
    }
    {
        PyObject *tmp_assign_source_11;


        tmp_assign_source_11 = MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__8_identity(tstate);

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[31], tmp_assign_source_11);
    }
    {
        PyObject *tmp_assign_source_12;


        tmp_assign_source_12 = MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__9_index(tstate);

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[11], tmp_assign_source_12);
    }
    {
        PyObject *tmp_assign_source_13;


        tmp_assign_source_13 = MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__10_index_expression(tstate);

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[12], tmp_assign_source_13);
    }
    {
        PyObject *tmp_assign_source_14;


        tmp_assign_source_14 = MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__11_key_val_pair(tstate);

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[13], tmp_assign_source_14);
    }
    {
        PyObject *tmp_assign_source_15;


        tmp_assign_source_15 = MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__12_literal(tstate);

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[14], tmp_assign_source_15);
    }
    {
        PyObject *tmp_assign_source_16;


        tmp_assign_source_16 = MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__13_multi_select_dict(tstate);

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[15], tmp_assign_source_16);
    }
    {
        PyObject *tmp_assign_source_17;


        tmp_assign_source_17 = MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__14_multi_select_list(tstate);

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[16], tmp_assign_source_17);
    }
    {
        PyObject *tmp_assign_source_18;


        tmp_assign_source_18 = MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__15_or_expression(tstate);

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[17], tmp_assign_source_18);
    }
    {
        PyObject *tmp_assign_source_19;


        tmp_assign_source_19 = MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__16_and_expression(tstate);

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[18], tmp_assign_source_19);
    }
    {
        PyObject *tmp_assign_source_20;


        tmp_assign_source_20 = MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__17_not_expression(tstate);

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[19], tmp_assign_source_20);
    }
    {
        PyObject *tmp_assign_source_21;


        tmp_assign_source_21 = MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__18_pipe(tstate);

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[20], tmp_assign_source_21);
    }
    {
        PyObject *tmp_assign_source_22;


        tmp_assign_source_22 = MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__19_projection(tstate);

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[21], tmp_assign_source_22);
    }
    {
        PyObject *tmp_assign_source_23;


        tmp_assign_source_23 = MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__20_subexpression(tstate);

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[22], tmp_assign_source_23);
    }
    {
        PyObject *tmp_assign_source_24;


        tmp_assign_source_24 = MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__21_slice(tstate);

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[23], tmp_assign_source_24);
    }
    {
        PyObject *tmp_assign_source_25;


        tmp_assign_source_25 = MAKE_FUNCTION_jmespath$ast$$36$$$36$$$36$function__22_value_projection(tstate);

        UPDATE_STRING_DICT1(moduledict_jmespath$ast, (Nuitka_StringObject *)mod_consts[24], tmp_assign_source_25);
    }

    // Report to PGO about leaving the module without error.
    PGO_onModuleExit("jmespath$ast", false);

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *post_load = IMPORT_EMBEDDED_MODULE(tstate, "jmespath.ast" "-postLoad");
        if (post_load == NULL) {
            return NULL;
        }
    }
#endif

    Py_INCREF(module_jmespath$ast);
    return module_jmespath$ast;
    module_exception_exit:

#if _NUITKA_MODULE_MODE && 0
    {
        PyObject *module_name = GET_STRING_DICT_VALUE(moduledict_jmespath$ast, (Nuitka_StringObject *)const_str_plain___name__);

        if (module_name != NULL) {
            Nuitka_DelModule(tstate, module_name);
        }
    }
#endif
    PGO_onModuleExit("jmespath$ast", false);

    RESTORE_ERROR_OCCURRED_STATE(tstate, &exception_state);
    return NULL;
}
