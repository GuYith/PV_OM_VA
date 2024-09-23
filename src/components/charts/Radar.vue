<script setup lang="ts">
import * as echarts from 'echarts/core'
import {
    TitleComponent,
    TitleComponentOption,
    LegendComponent,
    LegendComponentOption,
    // GridComponent,
} from 'echarts/components'
import { RadarChart, RadarSeriesOption } from 'echarts/charts'
import { SVGRenderer, CanvasRenderer } from 'echarts/renderers'
import { useStringStore } from '@/stores/string'
import { STRING_PARAMETERS, StringInfo } from '@/common'
import {} from 'echarts/components'
echarts.use([
    TitleComponent,
    // GridComponent,
    LegendComponent,
    RadarChart,
    CanvasRenderer,
    SVGRenderer,
])

type EChartsOption = echarts.ComposeOption<
    TitleComponentOption | LegendComponentOption | RadarSeriesOption
>

const props = defineProps<{
    stringInfo: StringInfo
}>()
const store = useStringStore()
const radarContainer = ref(null)

const draw = () => {
    const chartDom = radarContainer.value
    var myChart = echarts.init(chartDom, null, { renderer: 'svg' })
    var option: EChartsOption
    const data: any[] = []
    STRING_PARAMETERS.forEach((item) => {
        data.push(props.stringInfo[item])
    })
    const indicator = STRING_PARAMETERS.map((key) => {
        return {
            name: key,
            max: store.param_max_dict[key] as number,
            min: 0,
            axisLabel: { show: false },
        }
    })
    option = {
        tooltip: {
            trigger: 'item',
            backgroundColor: '#303133',
            appendToBody: true,
            textStyle: {
                fontSize: 10, // 字体大小
                color: 'white',
            },
            position: function (point: any) {
                return [point[0] + 10, point[1]]
            },
            borderColor: '#2A4858',
            formatter: (params: any) => {
                var str =
                    '<strong>' + props.stringInfo.string_name + '</strong><br/>'
                STRING_PARAMETERS.forEach((key, idx) => {
                    str +=
                        key +
                        ': ' +
                        Number(params.value[idx]).toFixed(2) +
                        '<br/>'
                })
                return str
            },
        },
        // yAxis: {
        //     // ... 其他 yAxis 配置项
        //     axisLabel: {
        //         show: false, // 隐藏刻度标签
        //     },
        // },
        axisName: {
            formatter: '',
        },
        radar: {
            // shape: 'circle',
            indicator: indicator,
        },
        series: [
            {
                type: 'radar',
                symbol: 'none',
                data: [
                    {
                        value: data,
                        name: props.stringInfo.string_name,
                        areaStyle: {
                            color: '#30313322', //'rgba(155, 191, 206, 0.6)',
                        },
                        lineStyle: {
                            color: '#666', //'rgb(32, 62, 74)',
                        },
                    },
                ],
            },
        ],
    }
    option && myChart.setOption(option)
}

onMounted(() => {
    draw()
})
</script>
<template>
    <div class="h-full" ref="radarContainer"></div>
</template>
