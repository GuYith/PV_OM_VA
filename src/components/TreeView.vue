<script setup lang="ts">
import {
    TreeModel,
    TREE_SPLITTER,
    TREE_CRITERION,
    LANG_TYPE,
    Series,
    DEAFULT_TREE,
    // INIT_STATUS,
    TRAINGED_STATUS,
} from '@/common'
import axios from '@/request'
// import chroma from 'chroma-js'
import { TooltipComponent } from 'echarts/components'
import { SankeyChart } from 'echarts/charts'
import { CanvasRenderer } from 'echarts/renderers'
import * as echarts from 'echarts/core'
import SankeyTree from '@/components/charts/SankeyTree.vue'
import { useTreeStore } from '@/stores/tree'
import { useforecastModelStore } from '@/stores/forecastModel'
import Root from '@/components/charts/Root.vue'
echarts.use([TooltipComponent, SankeyChart, CanvasRenderer])
// const label_color_map = [
//     ...chroma.scale(['#9bbfce', '#2A4858']).mode('lch').colors(6),
//     '#444',
// ]

const treeStore = useTreeStore()
const forecastModelStore = useforecastModelStore()
// const activeTree = computed(() => treeStore.activeTree)

// const featureIds: Ref<number[] | undefined> = ref(undefined)
const feautreLabels: Ref<string[]> = ref([])
const tree_model = reactive<TreeModel>({
    ...DEAFULT_TREE,
})
const treeRef: Ref<InstanceType<typeof SankeyTree> | null> = shallowRef(null)
// const rootRef: Ref<InstanceType<typeof Root> | null> = shallowRef(null)
const thresholdRange = reactive({
    min: 0,
    max: 100,
})
const isTraining = ref(false)
const handleTrainDT = () => {
    if (
        forecastModelStore.forecast_model.model_name === undefined ||
        forecastModelStore.forecast_model.model_name === ''
    ) {
        ElMessage.error('请先选择时序预测模型')
        return
    }
    if (
        !feautreLabels.value ||
        typeof feautreLabels.value === 'undefined' ||
        feautreLabels.value.length === 0
    ) {
        ElMessage.error('请先选择特征')
        return
    }
    isTraining.value = true
    tree_model.features = feautreLabels.value
    // console.log(featureIds.value, tree_model)
    axios
        .post(
            '/api/train/decisionTree',
            {
                forecast_model_name:
                    forecastModelStore.forecast_model.model_name,
                forecast_dataset: forecastModelStore.forecast_model.dataset,
                ...tree_model,
            },
            { timeout: 1000 * 600 * 10 }
        )
        .then((resp) => {
            isTraining.value = false

            tree_model.status = TRAINGED_STATUS
            const data = resp.data as any
            const series = data.series as Series[]
            treeStore.updateTreePredictResults(data)
            // caculate mean mse
            const mse_list = series.map((item) => item.mse) as number[]
            const mean_mse =
                mse_list.reduce((acc, val) => acc + val, 0) / mse_list.length
            tree_model.metrics.tree = mean_mse
            tree_model.metrics.raw = forecastModelStore.mean_mse
        })
}

const activeConfig = ref(false)

const handleFeatureChange = () => {
    if (
        treeStore.curNode.feature_id === -2 ||
        treeStore.curNode.feature_id === undefined
    ) {
        thresholdRange.min = -2
        thresholdRange.max = -2
    }
    const labels = feautreLabels.value as string[]
    const feature_label = labels[treeStore.curNode.feature_id] as string
    thresholdRange.min = treeStore.treeFeaturesRange[feature_label].min
    thresholdRange.max = treeStore.treeFeaturesRange[feature_label].max
}

const handleSave = () => {
    treeRef.value?.saveModel()
    // Clear tree
    Object.keys(DEAFULT_TREE).forEach((key: string) => {
        tree_model[key] = DEAFULT_TREE[key]
    })
}

const handleDelete = (model_name: string) => {
    treeStore.deleteTreeModel(model_name)
}

watch(
    () => treeStore.curTreeStruct,
    () => {
        tree_model.structure = treeStore.curTreeStruct
    }
)

onUpdated(() => {
    // 组件更新后，可能需要重新计算图表尺寸
    treeRef.value?.handleResize()
})
</script>

<template>
    <!-- TOOD: 点击生成决策树，传递前端结构到后端
    1. 前端修改树，更新
    2. 后端训练返回
    3. 准确度比较 -->
    <div class="h-full w-full relative text-theme-dark flex flex-col">
        <div
            :class="[
                'bg-theme-dark  h-8  font-bold text-center text-lg text-theme-light z-10 content-center',
                LANG_TYPE ? 'w-48' : 'w-32',
            ]"
        >
            {{ LANG_TYPE ? 'Decision Tree View' : '决策树视图' }}
        </div>
        <div class="absolute right-4 top-0">
            <el-switch
                v-model="activeConfig"
                :inactive-text="LANG_TYPE ? 'Config' : '配置'"
                size="small"
            />
            <el-switch
                class="ml-2"
                v-model="treeStore.activeTree"
                :inactive-text="LANG_TYPE ? 'Tree' : '启用'"
                size="small"
            />
        </div>
        <div>
            <div v-show="activeConfig">
                <div class="flex">
                    <div class="flex p-2 w-52 items-center">
                        <div
                            class="text-sm text-nowrap mr-2 w-22 text-left text-ellipsis overflow-hidden"
                        >
                            model_name
                        </div>
                        <el-input
                            style="width: 80px"
                            class="hover:border-theme-dark focus:border-theme-dark border-theme-dark w-40"
                            v-model="tree_model.model_name"
                            size="small"
                        />
                    </div>
                    <div class="flex p-2 w-52 items-center">
                        <div
                            class="text-sm text-nowrap mr-2 w-22 text-left text-ellipsis overflow-hidden"
                        >
                            criterion
                        </div>
                        <el-select
                            style="width: 80px"
                            class="hover:text-theme-dark focus:text-theme-dark"
                            v-model="tree_model.criterion"
                            size="small"
                            controls-position="right"
                        >
                            <el-option
                                v-for="item in TREE_CRITERION"
                                :key="item"
                                :label="item"
                                :value="item"
                            >
                            </el-option>
                        </el-select>
                    </div>
                </div>
                <div class="flex">
                    <div class="flex p-2 w-52 items-center">
                        <div
                            class="text-sm text-nowrap mr-2 w-22 text-left text-ellipsis overflow-hidden"
                        >
                            splitter
                        </div>
                        <el-select
                            style="width: 80px"
                            class="hover:text-theme-dark focus:text-theme-dark w-40"
                            v-model="tree_model.splitter"
                            size="small"
                            controls-position="right"
                            ><el-option
                                v-for="item in TREE_SPLITTER"
                                :key="item"
                                :label="item"
                                :value="item"
                            >
                            </el-option
                        ></el-select>
                    </div>
                    <div class="flex p-2 w-52 items-center">
                        <el-tooltip
                            content="min_impurity_split"
                            placement="top"
                        >
                            <div
                                class="text-sm text-nowrap mr-2 w-22 text-left text-ellipsis overflow-hidden"
                            >
                                min_impurity_split
                            </div></el-tooltip
                        >
                        <el-input-number
                            style="width: 80px"
                            width="40"
                            class="hover:text-theme-dark focus:text-theme-dark w-40"
                            v-model="tree_model.min_impurity_split"
                            size="small"
                            controls-position="right"
                        />
                    </div>
                </div>
                <div class="flex">
                    <div class="flex p-2 w-52 items-center">
                        <el-tooltip content="min_samples_leaf" placement="top">
                            <div
                                class="text-sm text-nowrap mr-2 w-22 text-left text-ellipsis overflow-hidden"
                            >
                                min_samples_leaf
                            </div>
                        </el-tooltip>
                        <el-input-number
                            style="width: 80px"
                            width="40"
                            class="hover:text-theme-dark focus:text-theme-dark w-40"
                            v-model="tree_model.min_samples_leaf"
                            size="small"
                            controls-position="right"
                        />
                    </div>
                    <div class="flex p-2 w-52 items-center">
                        <el-tooltip content="min_samples_split" placement="top">
                            <div
                                class="text-sm text-nowrap mr-2 w-22 text-left text-ellipsis overflow-hidden"
                            >
                                min_samples_split
                            </div>
                        </el-tooltip>
                        <el-input-number
                            style="width: 80px"
                            class="hover:text-theme-dark focus:text-theme-dark w-40"
                            v-model="tree_model.min_samples_split"
                            size="small"
                            controls-position="right"
                        />
                    </div>
                </div>
                <div class="flex">
                    <div class="flex p-2 w-52 items-center">
                        <el-tooltip
                            content="min_weight_fraction_leaf"
                            placement="top"
                        >
                            <div
                                class="text-sm text-nowrap mr-2 w-22 text-left text-ellipsis overflow-hidden"
                            >
                                min_weight_fraction_leaf
                            </div></el-tooltip
                        >
                        <el-input-number
                            style="width: 80px"
                            width="40"
                            class="hover:text-theme-dark focus:text-theme-dark w-40"
                            v-model="tree_model.min_weight_fraction_leaf"
                            size="small"
                            controls-position="right"
                        />
                    </div>
                    <div class="flex p-2 w-52 items-center">
                        <el-tooltip
                            content="min_impurity_decrease"
                            placement="top"
                        >
                            <div
                                class="text-sm text-nowrap mr-2 w-22 text-left text-ellipsis overflow-hidden"
                            >
                                min_impurity_decrease
                            </div></el-tooltip
                        >
                        <el-input-number
                            style="width: 80px"
                            class="hover:text-theme-dark focus:text-theme-dark w-40"
                            v-model="tree_model.min_impurity_decrease"
                            size="small"
                            controls-position="right"
                        />
                    </div>
                </div>

                <div class="flex">
                    <div class="flex p-2 w-52 items-center">
                        <div
                            class="text-sm text-nowrap mr-2 w-22 text-left text-ellipsis overflow-hidden"
                        >
                            max_depth
                        </div>
                        <el-input-number
                            style="width: 80px"
                            width="40"
                            class="hover:text-theme-dark focus:text-theme-dark w-40"
                            v-model="tree_model.max_depth"
                            size="small"
                            controls-position="right"
                        />
                    </div>
                    <div class="flex p-2 w-52 items-center">
                        <el-tooltip content="max_features" placement="top">
                            <div
                                class="text-sm text-nowrap mr-2 w-22 text-left text-ellipsis overflow-hidden"
                            >
                                max_features
                            </div></el-tooltip
                        >
                        <el-input
                            style="width: 80px"
                            class="hover:text-theme-dark focus:text-theme-dark w-40"
                            v-model="tree_model.max_features"
                            size="small"
                            controls-position="right"
                        />
                    </div>
                </div>
                <div class="flex">
                    <div class="flex p-2 w-52 items-center">
                        <el-tooltip content="random_state" placement="top">
                            <div
                                class="text-sm text-nowrap mr-2 w-22 text-left text-ellipsis overflow-hidden"
                            >
                                random_state
                            </div></el-tooltip
                        >
                        <el-input-number
                            style="width: 80px"
                            width="40"
                            class="hover:text-theme-dark focus:text-theme-dark w-40"
                            v-model="tree_model.random_state"
                            size="small"
                            controls-position="right"
                        />
                    </div>
                    <div class="flex p-2 w-52 items-center">
                        <el-tooltip content="max_leaf_nodes" placement="top">
                            <div
                                class="text-sm text-nowrap mr-2 w-22 text-left text-ellipsis overflow-hidden"
                            >
                                max_leaf_nodes
                            </div></el-tooltip
                        >
                        <el-input-number
                            style="width: 80px"
                            class="hover:text-theme-dark focus:text-theme-dark w-40"
                            v-model="tree_model.max_leaf_nodes"
                            size="small"
                            controls-position="right"
                        />
                    </div>
                </div>
            </div>
            <div class="flex p-2 items-center">
                <div
                    class="text-sm text-nowrap mr-2 w-22 text-left text-ellipsis overflow-hidden"
                >
                    features
                </div>
                <el-select
                    v-model="feautreLabels"
                    multiple
                    collapse-tags
                    collapse-tags-tooltip
                    :max-collapse-tags="3"
                    size="small"
                    class="hover:text-theme-dark focus:text-theme-dark w-40"
                >
                    <el-option
                        v-for="item in treeStore.treeFeaturesLabel"
                        :key="item"
                        :value="item"
                        :label="item"
                    >
                    </el-option>
                </el-select>
            </div>
            <el-button
                size="small"
                @click="handleTrainDT"
                :disabled="isTraining"
            >
                {{ LANG_TYPE ? 'Train' : '训练' }}
            </el-button>
            <el-button size="small" @click="handleSave" :disabled="isTraining">
                {{ LANG_TYPE ? 'Save' : '保存' }}
            </el-button>
        </div>
        <div
            class="m-2 mt-5 flex-grow relative"
            v-if="activeConfig === false"
            style="font-size: 12px"
            v-loading="isTraining"
        >
            <div class="absolute right-5 flex mt-2">
                <div class="mr-2">
                    <div class="bg-theme-dark w-7 h-3 rounded-lg"></div>
                    <div>{{ LANG_TYPE ? 'raw' : '原始' }}</div>
                </div>
                <div>
                    <div class="bg-[#9bbfce] w-7 h-3 rounded-lg"></div>
                    <div>{{ LANG_TYPE ? 'tree' : '决策树' }}</div>
                </div>
            </div>
            <div class="absolute m-2 z-50">
                <i-ant-design-undo-outlined
                    class="text-gray-400 hover:text-theme-dark"
                    @click="treeStore.clearTreeStruct"
                />
            </div>
            <Root
                v-if="treeStore.curTreeStruct.links.length === 0"
                :tree_model="tree_model"
            ></Root>
            <SankeyTree
                v-else
                ref="treeRef"
                :tree_model="tree_model"
                :feautreLabels="feautreLabels"
            >
            </SankeyTree>
            <el-dialog
                v-model="treeStore.treeNodeEditorVisible"
                title="Decision Tree Node Editor"
                width="500"
            >
                <el-form :model="treeStore.curNode">
                    <el-form-item label="Feature Id">
                        <el-select
                            v-model="treeStore.curNode.feature_id"
                            :onChange="handleFeatureChange"
                        >
                            <el-option
                                v-for="(item, idx) in feautreLabels"
                                :key="item"
                                :value="idx"
                                :label="item"
                            ></el-option>
                        </el-select>
                    </el-form-item>
                    <el-form-item label="threshold">
                        <el-slider
                            v-model="treeStore.curNode.threshold"
                            :min="thresholdRange.min"
                            :max="thresholdRange.max"
                        ></el-slider>
                    </el-form-item>
                </el-form>
                <template #footer>
                    <div class="dialog-footer">
                        <el-button @click="treeStore.closeEditor">{{
                            LANG_TYPE ? 'Cancel' : '取消'
                        }}</el-button>
                        <el-button
                            type="danger"
                            style="background-color: #f56c6c"
                        >
                            {{ LANG_TYPE ? 'Delete' : '删除' }}
                        </el-button>
                        <el-button
                            type="primary"
                            @click="treeStore.confirmEditor"
                        >
                            {{ LANG_TYPE ? 'Confirm' : '确定' }}
                        </el-button>
                    </div>
                </template>
            </el-dialog>

            <div class="w-full absolute bottom-0">
                <el-tooltip placement="top">
                    <template #content>
                        <div class="flex items-center">
                            <div class="w-2 h-1 mr-1 bg-theme-dark"></div>
                            raw: {{ tree_model.metrics.raw.toExponential(3) }}
                        </div>
                        <div class="flex items-center">
                            <div class="w-2 h-1 mr-1 bg-[#9bbfce]"></div>
                            tree: {{ tree_model.metrics.tree.toExponential(3) }}
                        </div>
                    </template>
                    <el-progress
                        :class="
                            tree_model.metrics.tree < tree_model.metrics.raw
                                ? 'treeBetter'
                                : 'rawBetter'
                        "
                        :show-text="false"
                        :percentage="
                            tree_model.metrics.tree < tree_model.metrics.raw
                                ? (tree_model.metrics.tree /
                                      Number(
                                          tree_model.metrics.raw.toExponential(
                                              3
                                          )
                                      )) *
                                  100
                                : (tree_model.metrics.raw /
                                      Number(
                                          tree_model.metrics.tree.toExponential(
                                              3
                                          )
                                      )) *
                                  100
                        "
                    />
                </el-tooltip>
            </div>
        </div>
        <div
            class="h-[380px] flex flex-col flex-wrap overflow-x-auto overflow-y-hidden scrollbar"
        >
            <div
                class="relative w-44 h-44 m-1 border-2 border-gray-100 rounded-md"
                v-for="item in treeStore.treeList"
            >
                <p class="text-sm mt-1">{{ item.model_name }}</p>
                <img class="h-full w-full" :src="item.snap_image?.src" />
                <div
                    class="absolute right-1 top-1 text-sm text-gray-400 hover:text-theme-dark"
                >
                    <i-ant-design-close-circle-outlined
                        @click="handleDelete(item.model_name)"
                    />
                </div>
                <div class="w-full absolute bottom-0">
                    <el-tooltip>
                        <template #content>
                            <div class="flex items-center">
                                <div class="w-2 h-1 mr-1 bg-theme-dark"></div>
                                raw: {{ item.metrics.raw }}
                            </div>
                            <div class="flex items-center">
                                <div class="w-2 h-1 mr-1 bg-[#9bbfce]"></div>
                                tree: {{ item.metrics.tree }}
                            </div>
                        </template>
                        <el-progress
                            :class="
                                item.metrics.tree < item.metrics.raw
                                    ? 'treeBetter'
                                    : 'rawBetter'
                            "
                            :show-text="false"
                            :percentage="
                                item.metrics.tree < item.metrics.raw
                                    ? (item.metrics.tree / item.metrics.raw) *
                                      100
                                    : (item.metrics.raw / item.metrics.tree) *
                                      100
                            "
                        />
                    </el-tooltip>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
.el-select-dropdown__item {
    color: #373d3b !important;
}

:deep(.el-input__wrapper.is-focus) {
    --el-input-focus-border-color: #373d3b88 !important;
}
.treeBetter {
    --el-color-primary: #9bbfce !important;
    --el-border-color-lighter: #373d3b !important;
}
.rawBetter {
    --el-color-primary: #373d3b !important;
    --el-border-color-lighter: #9bbfce !important;
}
/* :deep(.el-progress) {
    --el-color-primary: #9bbfce !important;
    --el-border-color-lighter: #373d3b !important;
} */

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

:deep(.el-switch__label) {
    color: #373d3b !important;
}
:deep(.el-switch) {
    --el-switch-on-color: #373d3b !important;
    --el-switch-off-color: #ccc !important;
}

:deep(.el-select__wrapper.is-focused) {
    box-shadow: 0 0 0 1px #373d3baa inset !important;
}
:deep(.el-tag) {
    --el-tag-text-color: #373d3b;
    /* --el-tag-bg-color: rgb(226, 248, 241); */
    --el-tag-border-color: #373d3b;
    border: 1px solid #373d3b !important;
    --el-tag-border-radius: 10px;
}

:deep(.el-slider) {
    --el-slider-main-bg-color: #373d3b !important;
}

.read-the-docs {
    color: #888;
}

.w-22 {
    width: 85px;
}
</style>
