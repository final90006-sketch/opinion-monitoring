/**
 * @file 系統設定與案件 Schema 定義。
 * 所有 UI 結構來自此處，作為 Single Source of Truth 的一部分。
 */

/**
 * @typedef {'text'|'date'|'select'|'textarea'} FieldType
 */

/**
 * @typedef {Object} ValidationRule
 * @property {boolean} [required] - 是否必填。
 * @property {number} [minLength] - 最小字元長度。
 * @property {number} [maxLength] - 最大字元長度。
 * @property {'taiwanNationalId'} [format] - 內建格式檢核識別碼。
 * @property {string} [message] - 自訂錯誤訊息。
 */

/**
 * @typedef {Object} SchemaField
 * @property {string} key - 對應 state 的欄位 key。
 * @property {string} label - 欄位顯示名稱。
 * @property {FieldType} type - 欄位類型。
 * @property {string} [placeholder] - placeholder 文案。
 * @property {boolean} [readonly] - 是否唯讀。
 * @property {Array<{label:string,value:string}>} [options] - select 的選項。
 * @property {ValidationRule} [validation] - 驗證規則。
 */

/**
 * @typedef {Object} SectionSchema
 * @property {string} id - 區塊唯一識別。
 * @property {string} title - 區塊標題。
 * @property {SchemaField[]} fields - 區塊欄位清單。
 */

/**
 * @typedef {Object} CaseSchema
 * @property {string} type - 案件類型識別碼。
 * @property {string} displayName - 顯示名稱。
 * @property {string} templatePath - 對應的 docx 模板路徑。
 * @property {SectionSchema[]} sections - 表單區塊。
 */

/**
 * 共用欄位定義，可於不同案件重用。
 * @type {SchemaField[]}
 */
const BASE_FIELDS = [
  {
    key: 'documentNumber',
    label: '文號',
    type: 'text',
    placeholder: '例如：刑字第114000123號',
    validation: { required: true, minLength: 6, message: '請輸入有效文號。' },
  },
  {
    key: 'caseDate',
    label: '發文日期',
    type: 'date',
    validation: { required: true, message: '請選擇發文日期。' },
  },
  {
    key: 'officerName',
    label: '承辦員警',
    type: 'text',
    placeholder: '請輸入承辦員警姓名',
    validation: { required: true, minLength: 2, message: '承辦員警姓名不可空白。' },
  },
];

/**
 * 案件類型 Schema Registry。
 * Phase 1 專注於資料模型，後續 Phase 3 將由 UI Builder 動態渲染。
 * @type {Record<string, CaseSchema>}
 */
export const CASE_SCHEMAS = {
  narcotics: {
    type: 'narcotics',
    displayName: '毒品案件',
    templatePath: '/templates/narcotics_case.docx',
    sections: [
      {
        id: 'base',
        title: '基本資訊',
        fields: BASE_FIELDS,
      },
      {
        id: 'suspect',
        title: '涉案人資訊',
        fields: [
          {
            key: 'suspectName',
            label: '嫌疑人姓名',
            type: 'text',
            placeholder: '請輸入嫌疑人姓名',
            validation: { required: true, minLength: 2, message: '嫌疑人姓名不可空白。' },
          },
          {
            key: 'suspectNationalId',
            label: '嫌疑人身分證字號',
            type: 'text',
            placeholder: '例如：A123456789',
            validation: {
              required: true,
              format: 'taiwanNationalId',
              message: '身分證字號格式錯誤，請重新確認。',
            },
          },
          {
            key: 'drugType',
            label: '查獲毒品種類',
            type: 'select',
            options: [
              { label: '第一級毒品', value: 'schedule_1' },
              { label: '第二級毒品', value: 'schedule_2' },
              { label: '第三級毒品', value: 'schedule_3' },
              { label: '其他', value: 'other' },
            ],
            validation: { required: true, message: '請選擇毒品種類。' },
          },
          {
            key: 'seizedAmount',
            label: '查扣數量/重量',
            type: 'text',
            placeholder: '例如：12.5 公克',
            validation: { required: true, message: '請填寫查扣數量/重量。' },
          },
        ],
      },
    ],
  },
  wanted: {
    type: 'wanted',
    displayName: '通緝案件',
    templatePath: '/templates/wanted_case.docx',
    sections: [
      {
        id: 'base',
        title: '基本資訊',
        fields: BASE_FIELDS,
      },
      {
        id: 'wanted_subject',
        title: '通緝對象資訊',
        fields: [
          {
            key: 'wantedName',
            label: '通緝對象姓名',
            type: 'text',
            placeholder: '請輸入姓名',
            validation: { required: true, minLength: 2, message: '請輸入通緝對象姓名。' },
          },
          {
            key: 'wantedNationalId',
            label: '身分證字號',
            type: 'text',
            placeholder: '例如：B123456789',
            validation: {
              required: true,
              format: 'taiwanNationalId',
              message: '身分證字號格式錯誤，請重新確認。',
            },
          },
          {
            key: 'warrantNumber',
            label: '通緝書字號',
            type: 'text',
            placeholder: '例如：院刑通字第114000456號',
            validation: { required: true, message: '請填寫通緝書字號。' },
          },
          {
            key: 'crimeSummary',
            label: '案由摘要',
            type: 'textarea',
            placeholder: '請輸入案由摘要',
            validation: { required: true, minLength: 10, message: '案由摘要至少需 10 字。' },
          },
        ],
      },
    ],
  },
};

/**
 * 系統初始案件類型。
 * @type {string}
 */
export const DEFAULT_CASE_TYPE = 'narcotics';

/**
 * 取得案件 schema。
 * @param {string} caseType
 * @returns {CaseSchema}
 * @throws {Error} 當 caseType 不存在時丟出。
 */
export function getCaseSchema(caseType) {
  const schema = CASE_SCHEMAS[caseType];
  if (!schema) {
    throw new Error(`找不到案件類型設定：${caseType}`);
  }
  return schema;
}

/**
 * 提供案件選單資料。
 * @returns {Array<{value:string,label:string}>}
 */
export function getCaseTypeOptions() {
  return Object.values(CASE_SCHEMAS).map((item) => ({
    value: item.type,
    label: item.displayName,
  }));
}
