import chroma from 'chroma-js'
// 0 为中文 | 1 为英文
export const LANG_TYPE = 1
export const TREE_CRITERION = [
    'squared_error',
    'friedman_mse',
    'absolute_error',
    'poisson',
]
export const TREE_SPLITTER = ['best', 'random']

// export const TREE_FEATURES = ['raw', 'month', 'day', 'weekday', 'hour']
export type Range = {
    [key: string]: number
    min: number
    max: number
}
export type RangesObject = {
    [key: string]: Range
}
export type TreeFeatureInfo = {
    ranges: RangesObject
    columns: string[]
}

export const TIMESERIES_LABEL = ['true', 'pred', 'importance']
export const TIMESERIES_COLORS = ['#666', '#fd8d3c', '#e4edf5']
// export const TIMESERIES_COLORS = ['#8f8f8f', '#6aafce', '#d2f8f1']

export const LABAL_COLOR_MAP = [
    ...chroma
        .scale([
            '#1f77b4',
            '#ff7f0e',
            '#2ca02c',
            '#d62728',
            '#9467bd',
            '#8c564b',
        ]) //['#93CD00', '#FFDF0B', '#FB8C77', '#BE5846']) '#e9a3c9', '#d05d7b'
        .colors(6),
    // ...chroma.scale(['#fafa6e', '#2A4858']).mode('lch').colors(6),
    // ...chroma.scale(['#bafa6e', '#200e4a']).mode('lch').colors(6),
    '#aaa',
]

export type FormNode = {
    name: number
    feature_id: number
    threshold: number
}
export type TableInfo = {
    [key: string]: string | number | [] | string[]
    table_name: string
    rows_cnt: number
    cols_cnt: number
    data: []
    columns: string[]
}

export type ForecastModel = {
    [key: string]: string | number
    model_type: string
    model_name: string
    dataset: string
    freq: string
    seq_len: number
    label_len: number
    pred_len: number
    d_model: number
    d_ff: number
    feature_num: number
}

export type RESP_ForecastModelInfo = {
    [key: string]: string | number
}

export type TreeNode = {
    name: number
    node_idx?: number
    feature_id: number
    threshold: number
}

export type TreeLink = { source: number; target: number; value: number }

export type TreeStructure = {
    nodes: TreeNode[]
    links: TreeLink[]
}

export const INIT_STATUS = 0
export const TRAINGED_STATUS = 1
export const DEAFULT_TREE: TreeModel = {
    model_name: 'Default',
    max_depth: 8, // undefined 默认设置为8
    criterion: 'squared_error',
    splitter: 'best',
    min_samples_leaf: 1,
    min_samples_split: 2,
    min_weight_fraction_leaf: 0,
    min_impurity_decrease: 0,
    min_impurity_split: 0,
    random_state: undefined,
    max_features: undefined,
    max_leaf_nodes: undefined,
    features: [],
    structure: {
        nodes: [],
        links: [],
    },
    metrics: {
        raw: 100,
        tree: 80,
    },
    status: INIT_STATUS,
    snap_image: undefined,
}
export const STRING_PARAMETERS = [
    'dispersion',
    'power_sum',
    'power_mean',
    'day_cnt',
    'mse',
]

export type StringInfo = {
    [key: string]: string | number
    string_name: string
    id: number
    dispersion: number
    power_sum: number
    power_mean: number
    day_cnt: number
    mse: number
    box_id: string
    invertor_id: string
    string_id: string
    label: number
}

export type PredictResults = {
    pred_datetime: any[]
    grad_datetime: any[]
    series: Series[]
}

export type StringCV = {
    [key: string]: number[] | string[]
    datetime: string[]
    current: number[]
    voltage: number[]
}
// with color
export type StringCVC = {
    [key: string]: number[] | string[] | string
    datetime: string[]
    current: number[]
    voltage: number[]
    color: string
}

export type Metric = {
    [key: string]: number
    raw: number
    tree: number
}

export type Series = {
    [key: string]: number[] | number | string | undefined
    id: number
    string_name: string
    raw: number[]
    pred: number[]
    mse?: number
    time_grad?: number[]
    residual: number[]
    residual_mean: number
    residual_var: number
    label: number
}

export type TreeModel = {
    [key: string]: string | number | string[] | Object | undefined
    model_name: string
    max_depth: number | undefined
    criterion: string
    splitter: string
    min_samples_leaf: number
    min_samples_split: number
    min_weight_fraction_leaf: number
    min_impurity_decrease: number
    min_impurity_split: number
    max_features: number | string | undefined
    random_state: number | undefined
    max_leaf_nodes: number | undefined
    features: string[]
    structure: TreeStructure
    metrics: Metric
    status: number
    snap_image: HTMLImageElement | undefined
}

export type StringPoint = {
    [key: string]: string | number
    x: number
    y: number
    string_name: string
    box_id: string
    inverter_id: string
    string_id: string
    label: number
}
