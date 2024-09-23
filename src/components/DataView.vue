<script setup lang="ts">
import { useStringStore } from '@/stores/string'
import { useforecastModelStore } from '@/stores/forecastModel'
import Radar from '@/components/charts/Radar.vue'
import Bar from '@/components/charts/Bar.vue'
import chroma from 'chroma-js'
import {
    LABAL_COLOR_MAP,
    RESP_ForecastModelInfo,
    StringInfo,
    TreeFeatureInfo,
    LANG_TYPE,
} from '@/common'
import axios from '@/request'
import { useTreeStore } from '@/stores/tree'
import { labelInner } from 'echarts/types/src/label/labelStyle.js'

const stringStore = useStringStore()
const treeStore = useTreeStore()
const forecastModelStore = useforecastModelStore()

const handleScroll = () => {
    if (stringStore.scrollDisabled === true) {
        console.log('scrollDisabled === true ', stringStore.showNum)
        return
    }
    stringStore.handleScroll()
}
const cascaderProps = {
    checkStrictly: true,
}

const clusterOptions = [
    {
        value: 'kmeans',
        label: 'kmeans',
    },
    {
        value: 'dbscan',
        label: 'dbscan',
    },
]
const distOptions = [
    {
        value: 'DTW',
        label: 'DTW',
    },
    {
        value: 'Euclidean',
        label: 'Euclidean',
    },
]

const sortOptions = [
    {
        value: 'string_name',
        label: 'string_name',
    },
    {
        value: 'dispersion',
        label: 'dispersion',
    },
    {
        value: 'power_sum',
        label: 'power_sum',
    },
    {
        value: 'power_mean',
        label: 'power_mean',
    },

    {
        value: 'day_cnt',
        label: 'day_cnt',
    },

    {
        value: 'mse',
        label: 'mse',
    },
    {
        value: 'label',
        label: 'label',
    },
]

const cascaderOptions = computed(() => {
    const cascaderDict: {
        [key: string]: any
    } = {}
    if (stringStore.stringInfos.length === 0) return []

    stringStore.stringInfos.map((item) => {
        if (item.box_id in cascaderDict) {
            if (!(item.invertor_id in cascaderDict[item.box_id])) {
                cascaderDict[item.box_id][item.invertor_id] = {}
            }
        } else {
            cascaderDict[item.box_id] = {}
            cascaderDict[item.box_id][item.invertor_id] = {}
        }
    })

    return Object.keys(cascaderDict).map((box_id: string) => {
        return {
            value: box_id,
            label: box_id,
            children: Object.keys(cascaderDict[box_id]).map(
                (invertor_id: string) => {
                    return {
                        value: invertor_id,
                        label: invertor_id,
                    }
                }
            ),
        }
    })
})

const hanleOrderSwitch = () => {
    stringStore.orderSwitch()
}

const handleFilter = () => {
    console.log('filter change: ', stringStore.filterValue)
    stringStore.resetShowNum()
}

const sort = () => {
    stringStore.resetShowNum()
}

const handleStringClick = (string_name: string) => {
    stringStore.switchSelect(
        forecastModelStore.forecast_model.dataset,
        string_name
    )
}

const model_name = ref<string>('')
type Option = {
    value: string
    label: string
}
const modelOptions = ref<Option[]>([])
const clusterParams = reactive({
    clusterType: 'kmeans',
    clusterDist: 'dtw',
    clusterNum: 6,
})

const mse_cnt_list: Ref<number[]> = ref([])
const mse_cnt_step = 0.1
const updateState = ref(false)

const handleUpdateDataView = async () => {
    if (updateState.value === false) {
        return
    }
    axios
        .get<TreeFeatureInfo>('/api/tree/dataset/' + model_name.value)
        .then((resp) => {
            treeStore.updateTreeFeatureInfo(resp.data as TreeFeatureInfo)
        })
    await axios
        .get<RESP_ForecastModelInfo>('/api/model_info/' + model_name.value)
        .then((resp) => {
            const modelInfo = resp.data as RESP_ForecastModelInfo
            forecastModelStore.update(modelInfo)
        })

    axios
        .get<StringInfo[]>(
            '/api/string_info/' + forecastModelStore.forecast_model.dataset
        )
        .then((resp) => {
            const data = resp.data as StringInfo[]
            stringStore.updateStringInfos(data)
            const mse_list = data.map((item) => item.mse)
            mse_list.sort((a, b) => a - b)
            console.log(
                mse_list[0],
                mse_list[mse_list.length / 2],
                mse_list[mse_list.length - 1]
            )
            const temp =
                mse_list.reduce((acc, val) => acc + val, 0) / mse_list.length
            const cnt_len = 30
            const cnt_list = new Array(cnt_len).fill(0)
            mse_list.forEach((item) => {
                const loc_idx = Math.min(
                    Math.floor(item / mse_cnt_step),
                    cnt_len - 1
                )
                cnt_list[loc_idx]++
            })
            mse_cnt_list.value = cnt_list
            forecastModelStore.updateForecastMSE(temp)
        })

    getMapViewData()
    updateState.value = false
}

const getMapViewData = () => {
    let clusterNum = clusterParams.clusterNum
    if (
        clusterParams.clusterNum === undefined ||
        clusterParams.clusterNum === null ||
        clusterParams.clusterNum === 0
    ) {
        if (clusterParams.clusterType === 'kmeans') {
            ElMessage.error('使用Kmeans聚类时，必须设置聚簇个数')
            return
        }
        clusterNum = -1
    }

    if (clusterNum > 10) {
        ElMessage.error('聚簇数量过大，请输入<=10的值')
        return
    }
    axios
        .get(
            `/api/map/${forecastModelStore.forecast_model.dataset}/${clusterParams.clusterType}/${clusterParams.clusterNum}`,
            { timeout: 1000 * 6000 * 10 }
        )
        .then((resp) => {
            const data = resp.data
            stringStore.updateMapViewData(data)
        })
}
// const backgrounds = computed(() => {
//     return stringStore.showStringInfos.map((item: StringInfo) => {
//         if (item.string_name in stringStore.selectedString) {
//             console.log(
//                 'computed bg',
//                 chroma(stringStore.selectedString[item.string_name].color)
//             )
//             return chroma(
//                 stringStore.selectedString[item.string_name].color
//             ).alpha(0.1)
//         }

//         return '#fff'
//     })
// })

onMounted(() => {
    axios.get<string[]>('api/model_list').then((resp) => {
        const data = resp.data as string[]
        if (resp.code === 200) {
            modelOptions.value = data.map((item) => {
                return {
                    value: item,
                    label: item,
                }
            })
        } else {
            ElMessage.error('网络错误')
        }
    })
})

const handleModelChange = () => {
    updateState.value = true
}

watch(
    () => [clusterParams.clusterNum, clusterParams.clusterNum, model_name],
    () => {
        updateState.value = true
    }
)
</script>
<template>
    <div class="h-full w-full relative text-theme-dark">
        <div>
            <div
                :class="[
                    'bg-theme-dark  h-8  font-bold text-center text-lg text-theme-light z-10 content-center',
                    LANG_TYPE ? 'w-28' : 'w-28',
                ]"
            >
                {{ LANG_TYPE ? 'Data View' : '数据视图' }}
            </div>
            <div class="absolute right-5 top-2 content-center">
                <el-button size="small" @click="handleUpdateDataView">{{
                    LANG_TYPE ? 'Update' : '更新'
                }}</el-button>
            </div>
            <div class="flex">
                <div class="flex p-2 w-42 items-center">
                    <div
                        :class="[
                            'text-sm text-nowrap w-7 text-left',
                            LANG_TYPE ? 'mr-4' : 'mr-2',
                        ]"
                    >
                        {{ LANG_TYPE ? 'Model' : '模型' }}
                    </div>
                    <el-tooltip
                        :content="model_name"
                        :disabled="model_name === ''"
                    >
                        <el-select
                            v-model="model_name"
                            style="width: 90px"
                            :placeholder="
                                LANG_TYPE ? 'Select Model' : '选择模型'
                            "
                            size="small"
                            @click="handleModelChange"
                        >
                            <el-option
                                v-for="item in modelOptions"
                                :key="item.value"
                                :label="item.label"
                                :value="item.value"
                            />
                        </el-select>
                    </el-tooltip>
                </div>
                <div class="flex p-2 w-52 items-center">
                    <div
                        :class="[
                            'text-sm text-nowrap w-7 text-left',
                            LANG_TYPE ? 'mr-6' : 'mr-4',
                        ]"
                    >
                        {{ LANG_TYPE ? 'Dataset' : '数据集' }}
                    </div>
                    <el-tooltip
                        :content="forecastModelStore.forecast_model.dataset"
                        :disabled="
                            forecastModelStore.forecast_model.dataset === ''
                        "
                    >
                        <el-select
                            v-model="forecastModelStore.forecast_model.dataset"
                            style="width: 90px"
                            :placeholder="
                                LANG_TYPE ? 'Select Dataset' : '选择数据集'
                            "
                            size="small"
                        ></el-select>
                    </el-tooltip>
                </div>
            </div>
            <div class="flex">
                <div class="flex p-2 w-40 items-center">
                    <div
                        :class="[
                            'text-sm text-nowrap w-11 text-left',
                            LANG_TYPE ? 'mr-10' : 'mr-4',
                        ]"
                    >
                        {{ LANG_TYPE ? 'Cluster Type' : '聚类' }}
                    </div>
                    <el-select
                        v-model="clusterParams.clusterType"
                        style="width: 90px"
                        :placeholder="
                            LANG_TYPE ? 'Select Cluster' : '选择聚类方法'
                        "
                        size="small"
                        clearable
                    >
                        <el-option
                            v-for="item in clusterOptions"
                            :key="item.value"
                            :label="item.label"
                            :value="item.value"
                        />
                    </el-select>
                </div>
                <div class="flex p-2 w-40 items-center">
                    <div
                        :class="[
                            'text-sm text-nowrap w-8 text-left',
                            LANG_TYPE ? 'mr-4' : 'mr-2',
                        ]"
                    >
                        {{ LANG_TYPE ? 'metric' : 'metric' }}
                    </div>
                    <el-select
                        v-model="clusterParams.clusterDist"
                        style="width: 60px"
                        :placeholder="
                            LANG_TYPE ? 'Select Cluster' : '选择聚类度量'
                        "
                        size="small"
                        clearable
                    >
                        <el-option
                            v-for="item in distOptions"
                            :key="item.value"
                            :label="item.label"
                            :value="item.value"
                        />
                    </el-select>
                </div>
            </div>
            <div class="flex">
                <!-- <div class="flex p-2 w-52 items-center">
                    <div
                        class="text-sm text-nowrap mr-2 w-16 font-bold text-left"
                    >
                        mse_distribution
                    </div>
                </div> -->
                <div class="flex p-2 w-42 items-center">
                    <div class="text-sm text-nowrap mr-4 w-28 text-left">
                        {{ LANG_TYPE ? 'Number of clusters' : '聚簇' }}
                    </div>
                    <el-input-number
                        popper-class="filter-cascader"
                        v-model="clusterParams.clusterNum"
                        :placeholder="
                            LANG_TYPE
                                ? 'Select number of clusters'
                                : '输入聚簇个数'
                        "
                        style="width: 70px"
                        :props="clusterParams.clusterNum"
                        size="small"
                        clearable
                    />
                </div>
                <div class="flex p-2 w-52 items-center">
                    <div class="text-sm text-nowrap mr-4 w-16 text-left">
                        mean_mse
                    </div>
                    <el-input
                        style="width: 60px"
                        class="hover:border-theme-dark focus:border-theme-dark border-theme-dark w-40"
                        v-model="forecastModelStore.mean_mse_str"
                        size="small"
                    />
                </div>
            </div>
            <Bar
                class="h-16 w-auto"
                :data="mse_cnt_list"
                :x="
                    mse_cnt_list.map((_, idx) =>
                        parseFloat((mse_cnt_step * idx).toFixed(3))
                    )
                "
            >
            </Bar>
            <!-- <div class="flex">
                <div class="flex p-2 w-52">
                    <div class="text-sm text-nowrap mr-2 w-20 text-left">
                        model_type
                    </div>
                    <el-input
                        style="width: 80px"
                        class="hover:border-theme-dark focus:border-theme-dark border-theme-dark w-40"
                        v-model="forecastModelStore.forecast_model.model_type"
                        size="small"
                    />
                </div>
                <div class="flex p-2 w-52">
                    <div class="text-sm text-nowrap mr-2 w-20 text-left">
                        freq
                    </div>
                    <el-input
                        style="width: 80px"
                        class="hover:text-theme-dark focus:text-theme-dark"
                        v-model="forecastModelStore.forecast_model.freq"
                        size="small"
                        controls-position="right"
                    />
                </div>
            </div>
            <div class="flex">
                <div class="flex p-2 w-52">
                    <div class="text-sm text-nowrap mr-2 w-20 text-left">
                        seq_len
                    </div>
                    <el-input-number
                        style="width: 80px"
                        class="hover:text-theme-dark focus:text-theme-dark w-40"
                        v-model="forecastModelStore.forecast_model.seq_len"
                        size="small"
                        controls-position="right"
                    />
                </div>
                <div class="flex p-2 w-52">
                    <div class="text-sm text-nowrap mr-2 w-20 text-left">
                        label_len
                    </div>
                    <el-input-number
                        style="width: 80px"
                        width="40"
                        class="hover:text-theme-dark focus:text-theme-dark w-40"
                        v-model="forecastModelStore.forecast_model.label_len"
                        size="small"
                        controls-position="right"
                    />
                </div>
            </div>
            <div class="flex">
                <div class="flex p-2 w-52">
                    <div class="text-sm text-nowrap mr-2 w-20 text-left">
                        pred_len
                    </div>
                    <el-input-number
                        style="width: 80px"
                        class="hover:border-theme-dark focus:border-theme-dark w-40"
                        v-model="forecastModelStore.forecast_model.pred_len"
                        size="small"
                        controls-position="right"
                    />
                </div>
                <div class="flex p-2 w-52">
                    <div class="text-sm text-nowrap mr-2 w-20 text-left">
                        d_model
                    </div>
                    <el-input-number
                        style="width: 80px"
                        class="hover:text-theme-dark focus:text-theme-dark w-40"
                        v-model="forecastModelStore.forecast_model.d_model"
                        size="small"
                        controls-position="right"
                    />
                </div>
            </div>
            <div class="flex">
                <div class="flex p-2 w-52">
                    <div class="text-sm text-nowrap mr-2 w-20 text-left">
                        d_ff
                    </div>
                    <el-input-number
                        style="width: 80px"
                        width="40"
                        class="hover:text-theme-dark focus:text-theme-dark w-40"
                        v-model="forecastModelStore.forecast_model.d_ff"
                        size="small"
                        controls-position="right"
                    />
                </div>
                <div class="flex p-2 w-52">
                    <div class="text-sm text-nowrap mr-2 w-20 text-left">
                        feature_num
                    </div>
                    <el-input-number
                        disabled
                        style="width: 80px"
                        width="40"
                        class="hover:text-theme-dark focus:text-theme-dark w-40"
                        v-model="forecastModelStore.forecast_model.feature_num"
                        size="small"
                        controls-position="right"
                    />
                </div>
            </div> -->
        </div>
        <el-divider
            ><strong class="text-theme-dark">
                {{ LANG_TYPE ? 'String Infos' : '组串信息' }}</strong
            ></el-divider
        >
        <div class="flex mt-2">
            <div class="flex items-center ml-2">
                <div class="text-sm text-nowrap mr-2 text-left">
                    {{ LANG_TYPE ? 'Sort' : '排序' }}
                </div>
                <el-select
                    class="mr-2"
                    v-model="stringStore.sortParam"
                    style="width: 100px"
                    :placeholder="LANG_TYPE ? 'Select Sort' : '选择排序依据'"
                    size="small"
                    clearable
                    @change="sort"
                >
                    <el-option
                        v-for="item in sortOptions"
                        :key="item.value"
                        :label="item.label"
                        :value="item.value"
                    />
                </el-select>
                <div
                    class="flex flex-col text-[10px]"
                    @click="hanleOrderSwitch"
                >
                    <i-ant-design-caret-up-filled
                        :class="
                            stringStore.sortOrder !== 'asc'
                                ? 'text-[#ccc]'
                                : 'text-theme-dark'
                        "
                    ></i-ant-design-caret-up-filled>
                    <i-ant-design-caret-down-filled
                        :class="
                            stringStore.sortOrder === 'asc'
                                ? 'text-[#ccc]'
                                : 'text-theme-dark'
                        "
                    ></i-ant-design-caret-down-filled>
                </div>
            </div>
            <div class="flex items-center ml-4">
                <div class="text-sm text-nowrap mr-2 text-left">
                    {{ LANG_TYPE ? 'Filter' : '过滤' }}
                </div>
                <el-cascader
                    popper-class="filter-cascader"
                    v-model="stringStore.filterValue"
                    :placeholder="LANG_TYPE ? 'Select Filter' : '选择过滤器'"
                    :options="cascaderOptions"
                    :props="cascaderProps"
                    @change="handleFilter"
                    size="small"
                    clearable
                    style="margin-right: 10px"
                />
            </div>
        </div>
        <div
            class="mt-2.5 max-h-52 pl-2 pr-2 scrollbar flex flex-row flex-wrap overflow-y-scroll"
            style="font-size: 10px"
            v-infinite-scroll="handleScroll"
            :infinite-scroll-disabled="stringStore.scrollDisabled"
        >
            <div
                :class="['p-1 m-1 relative border']"
                v-for="item in stringStore.showStringInfos"
                :style="{
                    backgroundColor: 
                        item.string_name in stringStore.selectedString
                            ? chroma(
                                  stringStore.selectedString[item.string_name]
                                      .color
                              ).alpha(0.08)
                            : '#fff', //backgrounds[index] as any,
                } as any"
            >
                <div
                    class="h-1 w-full"
                    :style="{ backgroundColor: LABAL_COLOR_MAP[item.label] }"
                ></div>
                <div
                    class="h-16 w-16 mr-1 mb-5"
                    @click="handleStringClick(item.string_name)"
                >
                    <Radar :stringInfo="item" :key="item.string_name"></Radar>
                    <div class="absolute text-wrap bottom-0">
                        {{ item.string_name }}
                    </div>
                </div>
            </div>
            <!-- <el-auto-resizer>
                <template #default="{ height, width }">
                    <el-table-v2
                        :columns="columns"
                        :data="data"
                        :width="width"
                        :height="height"
                        fixed
                    >
                        <template #empty>
                            <el-empty
                                style="width: 100%; height: 260px"
                                description="description"
                            />
                        </template> </el-table-v2
                ></template>
            </el-auto-resizer> -->
        </div>
        <!-- <div class="h-1"></div> -->
    </div>
</template>
<style>
.filter-cascader :deep(.el-radio) {
    --el-radio-input-border-color-hover: #373d3b !important;
}
.el-radio {
    --el-radio-input-border-color-hover: #373d3b !important;
}

.filter-cascader {
    color: #373d3b;
}
.el-radio__input.is-checked .el-radio__inner {
    background: #373d3b !important;
    border-color: #373d3b !important;
}

.el-cascader-node.is-active,
.el-cascader-node.is-selectable.in-checked-path {
    color: #373d3b !important;
}
</style>
<style scoped>
:deep(.el-select__wrapper) {
    background-color: #fff !important;
    --el-color-primary: #373d3b88 !important;
    /* border: #373D3B !important; */
    /* box-shadow: none !important; */
}
:deep(.el-select__caret) {
    color: #373d3b !important;
}

.el-select-dropdown__item {
    color: #373d3b !important;
}

:deep(.el-input-number__decrease:hover) {
    color: #373d3b;
}
:deep(.el-input-number__increase:hover) {
    color: #373d3b;
}
:deep(.el-input) {
    --el-input-clear-hover-color: #373d3b88;
    --el-input-focus-border-color: #373d3b88;
}
.read-the-docs {
    color: #888;
}
.el-input {
    border: none;
}
:deep(.el-table-v2__header-cell-text) {
    font-size: 12px !important;
}
:deep(.el-table-v2:not(.is-dynamic) .el-table-v2__cell-text) {
    font-size: 10px !important;
}

:deep(.el-button) {
    --el-button-bg-color: #373d3b !important;
    --el-button-text-color: white !important;
    --el-button-hover-text-color: white !important;
    --el-button-hover-bg-color: #373d3b !important;
    --el-button-border-color: #fff !important;
    --el-button-active-border-color: #373d3b !important;
    --el-button-active-bg-color: #373d3b !important;
    box-shadow: none !important;
}

:deep(.el-button:hover) {
    border: 1 #373d3b !important;
    --el-button-hover-border-color: #373d3b !important;
}
</style>
