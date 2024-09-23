<script setup lang="ts">
// import chroma from 'chroma-js'
import * as echarts from 'echarts/core'
import { GraphicComponent, GraphicComponentOption } from 'echarts/components'
import { CanvasRenderer } from 'echarts/renderers'
import { useTreeStore } from '@/stores/tree'
import { TreeModel } from '@/common'

const props = defineProps<{
    tree_model: TreeModel
}>()
const rootChart: Ref<echarts.EChartsType | null> = ref(null)
echarts.use([GraphicComponent, CanvasRenderer])
const chartContainer: Ref<HTMLElement | null> = ref(null)
const treeStore = useTreeStore()

type EChartsOption = echarts.ComposeOption<GraphicComponentOption>
const draw = () => {
    const chartDom = chartContainer.value
    rootChart.value = echarts.init(chartDom)

    const option: EChartsOption = {
        graphic: {
            elements: [
                {
                    type: 'group',
                    left: 'center',
                    top: 'center',
                    children: [
                        {
                            type: 'rect',
                            shape: {
                                x: 0,
                                y: -50,
                                width: 80,
                                height: 20,
                            },
                            style: {
                                fill: '#6aafce',
                            },
                            onclick: () => {
                                treeStore.openEditor(0)
                            },
                        },
                        {
                            type: 'rect',
                            shape: {
                                x: 0,
                                y: -40,
                                width: 80,
                                height: 20,
                            },
                            style: {
                                fill: '#6aafce',
                            },
                            onclick: () => {
                                treeStore.openEditor(0)
                            },
                        },
                        {
                            type: 'text',
                            left: '30',
                            top: '-55',
                            style: {
                                text: 'root',
                            },
                            shape: {
                                width: 80,
                            },
                        },
                    ],
                },
            ],
        },
    }

    option && rootChart.value.setOption(option)
}

const saveModel = () => {
    // console.log(props.tree_model)
    const img = new Image()
    img.src = rootChart.value?.getDataURL({
        backgroundColor: '#fff',
    }) as string
    props.tree_model.snap_image = img
    treeStore.appendTreeModel(props.tree_model)
    console.log(treeStore.treeList)
}

const handleResize = () => {
    if (rootChart.value !== null) {
        rootChart.value.resize()
    }
}

defineExpose({
    saveModel,
    handleResize,
})

onMounted(() => {
    draw()
})
</script>

<template>
    <div
        class="h-full border-spacing-0 border border-2"
        ref="chartContainer"
    ></div>
</template>
