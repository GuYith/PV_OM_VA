<script setup lang="ts">
import chroma from 'chroma-js'
import * as echarts from 'echarts/core'
import {
    TooltipComponent,
    TooltipComponentOption,
    DataZoomComponent,
} from 'echarts/components'
import { SankeyChart, SankeySeriesOption } from 'echarts/charts'
import { CanvasRenderer, SVGRenderer } from 'echarts/renderers'
import { TreeModel } from '@/common'
import { useTreeStore } from '@/stores/tree'
echarts.use([
    TooltipComponent,
    SankeyChart,
    SVGRenderer,
    CanvasRenderer,
    DataZoomComponent,
])

type EChartsOption = echarts.ComposeOption<
    TooltipComponentOption | SankeySeriesOption
>
const treeStore = useTreeStore()
const label_color_map = [
    ...chroma.scale(['#9bbfce', '#6aafce', '#2A4858']).mode('lch').colors(6),
    '#444',
]

const props = defineProps<{
    tree_model: TreeModel
    feautreLabels: string[]
}>()

const handleResize = () => {
    if (myChart.value !== null) {
        myChart.value.resize()
    }
}

const treeContainer = ref(null)
const myChart: Ref<echarts.EChartsType | null> = ref(null)
const draw = () => {
    const chartDom = treeContainer.value
    myChart.value = echarts.init(chartDom, null, { renderer: 'svg' })

    const option: EChartsOption = {
        tooltip: {
            textStyle: {
                fontSize: 10, // 字体大小
            },
            trigger: 'item',
            triggerOn: 'mousemove',
            borderColor: '#2A4858',
            formatter: function (params: any) {
                if (params.dataType === 'edge') {
                    const item = params.data as any
                    return (
                        'node' +
                        item.source +
                        ' -> ' +
                        'node' +
                        item.target +
                        ' : ' +
                        item.value
                    )
                } else {
                    return 'node' + params.name
                }
            },
        },
        animation: false,
        dataZoom: [
            {
                type: 'slider', // 使用滑动条类型的缩放
                show: true, // 显示滑动条
                xAxisIndex: 0, // 缩放 Sankey 图的第一轴（通常是 x 轴）
                start: 0, // 滑动条的起始位置百分比
                end: 100, // 滑动条的结束位置百分比
            },
            {
                type: 'inside', // 使用内部缩放
                xAxisIndex: 0, // 缩放 Sankey 图的第一轴（通常是 x 轴）
                start: 0, // 初始缩放比例的起始位置
                end: 100, // 初始缩放比例的结束位置
            },
        ],
        series: [
            {
                type: 'sankey',
                top: 'center',
                left: 'center',
                nodeGap: 20,
                orient: 'vertical',
                layoutIterations: 0, //按nodes顺序
                // draggable: false,
                label: {
                    show: true,
                    position: 'top',
                    formatter: function (params) {
                        const item = params.data as any
                        if (item.feature_id !== -2) {
                            if (
                                props.feautreLabels[item.feature_id] ===
                                    'raw' ||
                                props.feautreLabels[item.feature_id] ===
                                    'irradiation' ||
                                props.feautreLabels[item.feature_id] ===
                                    'wind_speed'
                            ) {
                                return (
                                    props.feautreLabels[item.feature_id] +
                                    ' <= ' +
                                    item.threshold.toExponential(3)
                                )
                            } else {
                                return (
                                    props.feautreLabels[item.feature_id] +
                                    ' <= ' +
                                    item.threshold
                                )
                            }
                        } else {
                            return 'leaf'
                        }
                    },
                },
                color: label_color_map,
                data: treeStore.curTreeStruct.nodes,
                links: treeStore.curTreeStruct.links,
            },
        ],
    }

    option && myChart.value.setOption(option)
    myChart.value.on('click', { dataType: 'node' }, function (params: any) {
        // console.log(params)
        treeStore.openEditor(params.data.name as number)
    })
}

const saveModel = () => {
    // console.log(props.tree_model)
    const img = new Image()
    img.src = myChart.value?.getDataURL({
        backgroundColor: '#fff',
        type: 'svg',
    }) as string
    treeStore.appendTreeModel({
        ...JSON.parse(JSON.stringify(props.tree_model)),
        snap_image: img,
    })
    // console.log(treeStore.treeList)
}

onMounted(() => {
    draw()
})

watch(
    () => treeStore.curTreeStruct.nodes,
    () => {
        draw()
    }
)

defineExpose({
    saveModel,
    handleResize,
})
</script>
<template>
    <div
        class="h-full border-spacing-0 border border-2"
        id="treeContainer"
        ref="treeContainer"
    ></div>
</template>
