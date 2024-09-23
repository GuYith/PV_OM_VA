<script setup lang="ts">
import * as echarts from 'echarts/core'
import { GridComponent } from 'echarts/components'
import { BarChart } from 'echarts/charts'
import { SVGRenderer, CanvasRenderer } from 'echarts/renderers'

echarts.use([GridComponent, BarChart, SVGRenderer, CanvasRenderer])

const props = defineProps<{
    data: number[]
    x: number[]
}>()
const barContainer = ref(null)

const draw = () => {
    if (!props.data || props.data.length === 0) {
        return
    }
    var chartDom = barContainer.value
    var myChart = echarts.init(chartDom, null, { renderer: 'svg' })
    var option

    option = {
        tooltip: {
            trigger: 'axis',
            axisPointer: {
                type: 'shadow',
            },
            backgroundColor: '#303133',
            appendToBody: true,
            textStyle: {
                fontSize: 10, // 字体大小
                color: 'white',
            },
            position: function (point: any) {
                return [point[0] + 10, point[1]]
            },
        },
        // title: {
        //     text: 'mse distribution', // 标题文本
        //     left: 'center', // 标题距离图表右侧的距离
        //     top: 0,
        //     // top: 'center', // 标题垂直居中
        //     textStyle: {
        //         fontSize: 14, // 字体大小
        //         fontWeight: 'normal',
        //     },
        //     textAlign: 'left', // 文本对齐到右侧
        // },
        grid: {
            top: 0,
            left: 25,
            right: 10,
            bottom: 20,
            width: 'auto',
            height: 'auto',
        },
        xAxis: {
            type: 'category',
            data: props.x,
            axisTick: {
                alignWithLabel: true,
            },
            axisLabel: {
                interval: 5,
                formatter: function (value: number) {
                    // toFixed(3) 将数字格式化为三位小数的字符串
                    return Number(value).toFixed(3)
                },
            },
        },
        yAxis: {
            show: false,
        },
        series: [
            {
                data: props.data,
                type: 'bar',
                color: '#333',
            },
        ],
    }

    option && myChart.setOption(option)
}

watch(
    () => [props.data, props.x],
    () => {
        draw()
    }
)
onMounted(() => {
    draw()
})
</script>
<template>
    <div ref="barContainer"></div>
</template>
