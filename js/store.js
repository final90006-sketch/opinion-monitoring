/**
 * @file 集中式 State Manager。
 * 實作 Single Source of Truth，供 UI 與 Document Service 共用。
 */

import { DEFAULT_CASE_TYPE, getCaseSchema } from './config.js';

/**
 * @typedef {Object} StoreState
 * @property {string} currentCaseType
 * @property {Record<string, unknown>} formData
 * @property {Record<string, string>} errors
 * @property {boolean} isGenerating
 */

/**
 * @typedef {(state: Readonly<StoreState>) => void} StoreListener
 */

/**
 * @typedef {Object} CreateStoreOptions
 * @property {string} [initialCaseType]
 */

/**
 * 建立新的 state manager。
 * @param {CreateStoreOptions} [options]
 */
export function createStore(options = {}) {
  /** @type {Set<StoreListener>} */
  const listeners = new Set();

  /** @type {StoreState} */
  let state = {
    currentCaseType: options.initialCaseType || DEFAULT_CASE_TYPE,
    formData: {},
    errors: {},
    isGenerating: false,
  };

  initializeFormData();

  function initializeFormData() {
    const schema = getCaseSchema(state.currentCaseType);
    const nextFormData = {};

    schema.sections.forEach((section) => {
      section.fields.forEach((field) => {
        nextFormData[field.key] = '';
      });
    });

    state = {
      ...state,
      formData: nextFormData,
      errors: {},
    };
  }

  function emit() {
    const snapshot = getState();
    listeners.forEach((listener) => listener(snapshot));
  }

  /**
   * @returns {Readonly<StoreState>}
   */
  function getState() {
    return Object.freeze({
      ...state,
      formData: { ...state.formData },
      errors: { ...state.errors },
    });
  }

  /**
   * @param {StoreListener} listener
   * @returns {() => void}
   */
  function subscribe(listener) {
    listeners.add(listener);
    return () => listeners.delete(listener);
  }

  /**
   * @param {string} caseType
   */
  function setCaseType(caseType) {
    if (caseType === state.currentCaseType) return;
    getCaseSchema(caseType);
    state = {
      ...state,
      currentCaseType: caseType,
    };
    initializeFormData();
    emit();
  }

  /**
   * @param {string} key
   * @param {unknown} value
   */
  function updateField(key, value) {
    state = {
      ...state,
      formData: {
        ...state.formData,
        [key]: value,
      },
      errors: {
        ...state.errors,
        [key]: '',
      },
    };
    emit();
  }

  /**
   * @param {boolean} nextValue
   */
  function setGenerating(nextValue) {
    state = {
      ...state,
      isGenerating: nextValue,
    };
    emit();
  }

  /**
   * @param {Record<string,string>} errors
   */
  function setErrors(errors) {
    state = {
      ...state,
      errors: { ...errors },
    };
    emit();
  }

  /**
   * @returns {Record<string, unknown>}
   */
  function getPayload() {
    return { ...state.formData };
  }

  return {
    getState,
    subscribe,
    setCaseType,
    updateField,
    setGenerating,
    setErrors,
    getPayload,
  };
}
