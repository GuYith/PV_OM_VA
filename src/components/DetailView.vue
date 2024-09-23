<script setup lang="ts">
import axios from '@/request.ts'
import Horizon from '@/components/charts/Horizon.vue'
import { useforecastModelStore } from '@/stores/forecastModel.ts'
import { useStringStore } from '@/stores/string'
import {
    TIMESERIES_COLORS,
    TIMESERIES_LABEL,
    LANG_TYPE,
    LABAL_COLOR_MAP,
    PredictResults,
} from '@/common'
import TimeSeries from '@/components/charts/TimeSeries.vue'
// const model_name: Ref<string> = ref('power_new_covariate_120_24')
// const dataset: Ref<string> = ref('all_filtered_string_power_df')

const forecastModelStore = useforecastModelStore()
const stringStore = useStringStore()

const feature_importance: Ref<number[]> = ref([])
// const time_series = reactive({})
const updateFeatureImportance = () => {
    axios
        .get<number[]>(
            '/api/feature_importance/' +
                forecastModelStore.forecast_model.model_name
        )
        .then((resp) => {
            feature_importance.value = resp.data as number[]
        })
}

const updateTimeSeries = () => {
    console.log(
        '/api/time_series/' +
            forecastModelStore.forecast_model.model_name +
            '/' +
            forecastModelStore.forecast_model.dataset
    )
    axios
        .get(
            '/api/time_series/fast/' +
                forecastModelStore.forecast_model.model_name +
                '/' +
                forecastModelStore.forecast_model.dataset,
            { timeout: 1000 * 6000 * 10 }
        )
        .then((resp) => {
            const data = resp.data as PredictResults
            stringStore.updatePredictResults(data)
        })

    axios
        .get(
            '/api/time_series/' +
                forecastModelStore.forecast_model.model_name +
                '/' +
                forecastModelStore.forecast_model.dataset,
            { timeout: 1000 * 6000 * 10 }
        )
        .then((resp) => {
            const data = resp.data as PredictResults
            stringStore.updatePredictResults(data)
        })
}

const handleScroll = () => {
    if (stringStore.scrollDisabled === true) {
        return
    }
    stringStore.handleScroll()
}

watch(
    () => forecastModelStore.forecast_model.model_name,
    () => {
        updateFeatureImportance()
        updateTimeSeries()
    }
)
</script>
<template>
    <div class="h-full w-full relative flex-col flex">
        <div
            :class="[
                'bg-theme-dark  h-8  font-bold text-center text-lg text-theme-light z-10 content-center',
                LANG_TYPE ? 'w-32' : 'w-28',
            ]"
        >
            {{ LANG_TYPE ? 'Detail View' : '详细视图' }}
        </div>
        <div
            class="w-full timeseries-view overflow-y-scroll scrollbar"
            v-infinite-scroll="handleScroll"
            :infinite-scroll-disabled="stringStore.scrollDisabled"
        >
            <div class="absolute right-10 top-2 flex">
                <div class="w-36 m-1 flex items-center">
                    <span class="label mr-1 text-nowrap">
                        {{ LANG_TYPE ? 'anomaly threshold' : '异常阈值' }}</span
                    >
                    <el-slider
                        size="small"
                        v-model="stringStore.anomalyThreshold"
                        :max="10"
                    ></el-slider>
                </div>
                <div class="w-36 m-1 flex items-center">
                    <span class="label mr-1 text-nowrap">
                        {{ LANG_TYPE ? 'anomaly step' : '偏差倍数' }}</span
                    >
                    <el-slider
                        size="small"
                        v-model="stringStore.anomalyStep"
                        :max="24"
                    ></el-slider>
                </div>
                <div
                    class="flex m-2 content-center text-center"
                    v-for="(item, idx) in TIMESERIES_LABEL"
                    :key="item"
                >
                    <div
                        class="h-4 w-4 m-1"
                        :style="{ backgroundColor: TIMESERIES_COLORS[idx] }"
                    ></div>
                    <div
                        class="content-center text-center"
                        style="font-size: 12px"
                    >
                        {{ item }}
                    </div>
                </div>
            </div>
            <div
                class="h-32 m-3 flex relative"
                v-for="(item, idx) in stringStore.showSeries"
                :key="item.string_name"
            >
                <div class="label relative w-16 m-auto">
                    <div class="flex">
                        <div
                            class="h-7 w-2"
                            :style="{
                                backgroundColor: LABAL_COLOR_MAP[item.label],
                            }"
                        ></div>
                        <div class="ml-[2px]">{{ item['string_name'] }}</div>
                    </div>
                </div>
                <TimeSeries
                    :data="item"
                    :showXAxis="idx === 0"
                    :key="item['string_name']"
                ></TimeSeries>
            </div>
        </div>
        <div class="w-full h-10">
            <Horizon :feature_importance="feature_importance"></Horizon>
        </div>
    </div>
</template>

<style scoped>
.timeseries-view {
    height: 440px;
    /* height: calc(100% - 2rem); */
}

:deep(.el-slider) {
    --el-slider-main-bg-color: #373d3b !important;
    --el-slider-button-size: 14px;
}

.label {
    font-size: 10px;
}
</style>
