<script setup lang="ts">
import { useStringStore } from '@/stores/string'
import { LANG_TYPE } from '@/common'
import { useforecastModelStore } from '@/stores/forecastModel'
import * as d3 from 'd3'

const stringStore = useStringStore()
const forecastModelStore = useforecastModelStore()
const currentContainer: Ref<HTMLDivElement | null> = ref(null)

const toolTipVisible = ref(false)
const toolTipContent: {
    date: string
    value_name: string
    string_list: string[]
    value_list: string[]
} = reactive({
    date: '',
    value_name: '',
    string_list: [],
    value_list: [],
})

const triggerRef = ref({
    getBoundingClientRect() {
        return toolTipPosition.value
    },
})

let currents: any
let voltages: any
const toolTipPosition = ref({
    top: 0,
    left: 0,
    bottom: 0,
    right: 0,
})
// const colorMap = ['#008080', '#ff69b4', '#f98841', '#0087cd', '#ffd800']
// const LegendContainer: Ref<HTMLDivElement | null> = ref(null)
const highLightStringIdx = ref(-1)
const draw = () => {
    const stringData = Object.keys(stringStore.selectedString).map(
        (key) => stringStore.selectedString[key]
    )

    if (stringData.length === 0) {
        // clear
        d3.select(currentContainer.value).selectAll('*').remove()
        return
    }

    const container_width = (currentContainer.value as HTMLDivElement)
        .clientWidth
    const container_height = (currentContainer.value as HTMLDivElement)
        .clientHeight

    const height_current = container_height * 0.35
    const height_voltage = container_height * 0.35
    const height_context = container_height * 0.1
    const margin = {
        top: 0,
        right: 20,
        bottom: 0,
        left: 40,
    }
    const margin_voltage = {
        top: container_height * 0.1,
        right: 0,
        bottom: 0,
        left: 0,
    }

    const margin_current = {
        top: height_voltage + container_height * 0.1,
        right: 0,
        bottom: 0,
        left: 0,
    }
    const margin_context = {
        top: height_current + height_voltage + container_height * 0.13,
        right: 0,
        bottom: 0,
        left: 40,
    }
    const width = container_width - margin.left - margin.right
    const height = container_height

    const datetime = stringData[0].datetime.map(
        d3.utcParse('%Y-%m-%d %H:%M:%S')
    )

    const x = d3.scaleUtc(d3.extent(datetime as any) as any, [
        margin.left,
        width,
    ])

    const x_context = d3.scaleUtc(d3.extent(datetime as any) as any, [0, width])

    const y_voltage = d3.scaleLinear(
        [
            d3.min(stringData, (item) => d3.min(item.voltage)) as number,
            d3.max(stringData, (item) => d3.max(item.voltage)) as number,
        ],
        [height_voltage - margin_voltage.bottom, margin_voltage.top]
    )

    const y_current = d3.scaleLinear(
        [
            d3.min(stringData, (item) => d3.min(item.current)) as number,
            d3.max(stringData, (item) => d3.max(item.current)) as number,
        ],
        [
            height_current - margin_current.bottom,
            margin_current.top - height_current,
        ]
    )

    const y_context = d3.scaleLinear(
        [
            d3.min(stringData, (item) => d3.min(item.current)) as number,
            d3.max(stringData, (item) => d3.max(item.current)) as number,
        ],

        [
            height_context - margin_context.bottom,
            container_height * 0.05,
            // margin_context.top - height_context,
        ]
    )

    const line_current = d3
        .line()
        .x((_, idx) => {
            return x(datetime[idx] as any)
        })
        .y((d) => {
            return y_current(d as any)
        })

    const line_voltage = d3
        .line()
        .x((_, idx) => x(datetime[idx] as any))
        .y((d) => {
            return y_voltage(d as any)
        })

    const line_context = d3
        .line()
        .x((_, idx) => x(datetime[idx] as any))
        .y((d) => {
            return y_context(d as any)
        })
    // clear
    d3.select(currentContainer.value).selectAll('*').remove()
    // Create the SVG container.
    const svg = d3
        .select(currentContainer.value)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('transform', `translate(${10}, 0)`)
        .on('pointerenter pointermove', pointermoved)
        .on('pointerleave', pointerleft)
        .on('touchstart', (event) => event.preventDefault())

    const rule = svg
        .append('g')
        .append('line')
        .attr('y1', height)
        .attr('y2', container_height * 0.1)
        .attr('stroke', '#666')
        .attr('stroke-dasharray', '2,2')
        .attr('transform', 'translate(-1, 0)')

    svg.append('defs')
        .append('clipPath')
        .attr('id', 'clip')
        .append('rect')
        .attr('x', margin.left)
        .attr('width', width)
        .attr('height', height)

    svg.append('text')
        .attr('x', 20)
        .attr('y', 60)
        .attr('text-anchor', 'middle')
        .style('font-size', '10px')
        .text('Voltage')

    svg.append('text')
        .attr('x', 20)
        .attr('y', margin_current.top + 25)
        .attr('text-anchor', 'middle')
        .style('font-size', '10px')
        .text('Current')
    const xAxis = d3.axisBottom(x).ticks(height / 20)
    // xAxis 1
    svg.append('g')
        .attr(
            'transform',
            `translate(${0}, ${margin_context.top + height_context + 2})`
        )
        .call(xAxis)
        .call((g) =>
            g
                .selectAll('.tick line')
                .attr('stroke', '#ddd')
                .attr('stroke-opacity', 0.1)
        )
    // xAxis 2
    svg.append('g')
        .attr('class', 'xAxis')
        .attr(
            'transform',
            `translate(${0}, ${margin_current.top + height_current + 2})`
        )
        .call(xAxis)
        .call((g) =>
            g
                .selectAll('.tick line')
                .attr('stroke', '#ddd')
                .attr('stroke-opacity', 0.1)
        )
    // yAxis
    svg.append('g')
        .attr('transform', `translate(${margin.left}, ${margin_current.top})`)
        .call(d3.axisLeft(y_current).ticks(height / 50))
        .call((g) =>
            g
                .selectAll('.tick line')
                .attr('stroke', '#ddd')
                .attr('stroke-opacity', 0.1)
        )

    svg.append('g')
        .attr('transform', `translate(${margin.left}, ${margin_voltage.top})`)
        .call(d3.axisLeft(y_voltage).ticks(height / 50))
        .call((g) =>
            g
                .selectAll('.tick line')
                .attr('stroke', '#ddd')
                .attr('stroke-opacity', 0.1)
        )

    const currentG = svg
        .append('g')
        .selectAll('g')
        .data(stringData)
        .join('g')
        .attr('class', 'current')
        .attr('transform', `translate(${0}, ${margin_current.top})`)
        .attr('clip-path', 'url(#clip)')

    const voltageG = svg
        .append('g')
        .selectAll('g')
        .data(stringData)
        .join('g')
        .attr('class', 'voltage')
        .attr('transform', `translate(${0}, ${margin_voltage.top})`)
        .attr('clip-path', 'url(#clip)')

    const contextG = svg
        .append('g')
        .selectAll('g')
        .data(stringData)
        .join('g')
        .attr('class', 'context')
        .attr('transform', `translate(${0}, ${margin_context.top})`)

    const brushG = svg
        .append('g')
        .attr('class', 'brush')
        .attr('transform', `translate(${0}, ${margin_context.top})`)

    const brush = d3
        .brushX()
        .extent([
            [0, height_context - container_height * 0.05],
            [width, height_context],
        ])
        .on('brush', brushed)

    brushG.call(brush)

    currents = currentG
        .append('path')
        .attr('fill', 'none')
        .attr('stroke', (d) => d.color)
        .attr('stroke-width', 1)
        .attr('d', (d) => line_current(d['current'] as any))

    voltages = voltageG
        .append('path')
        .attr('fill', 'none')
        .attr('stroke', (d) => d.color)
        .attr('stroke-width', 1)
        .attr('d', (d) => line_voltage(d['voltage'] as any))

    contextG
        .append('path')
        .attr('fill', 'none')
        .attr('stroke', (d) => d.color)
        .attr('stroke-width', 1)
        .attr('d', (d) => line_context(d['current'] as any))

    // 创建图例容器
    const legend = svg
        .append('g')
        .attr('transform', `translate(${width - 120}, ${30})`) // 定位到 SVG 的右侧
    Object.keys(stringStore.selectedString).map((key, index) => {
        const legendItem = legend
            .append('g')
            .attr('transform', `translate( ${-index * 120}, 0)`)

        legendItem
            .append('rect')
            .attr('width', 10)
            .attr('height', 10)
            .attr('fill', stringStore.selectedString[key].color)
            .on('click', () => {
                highLightString(index)
            })
            .on('dblclick', () => {
                stringStore.switchSelect(
                    forecastModelStore.forecast_model.dataset,
                    key
                )
            })

        legendItem
            .append('text')
            .attr('x', 15)
            .attr('y', 5)
            .style('font-size', '10px')
            .attr('dy', '0.35em') // 调整文本垂直对齐
            .text(key)
    })

    const bisect = d3.bisector((d) => d).center

    var offsetIdx = 0
    console.log(offsetIdx)
    function brushed({ selection }: any) {
        const selected = selection.map(x_context.invert, x_context)
        offsetIdx = bisect(
            datetime,
            x.invert(Math.min(selection[0], selection[1]))
        )
        x.domain(selected)

        d3.selectAll('.current')
            .select('path')
            .attr('d', (d: any) => line_current(d['current'] as any))

        d3.selectAll('.voltage')
            .select('path')
            .attr('d', (d: any) => line_voltage(d['voltage'] as any))

        d3.select('.xAxis').call(xAxis as any)
    }
    function pointermoved(event: MouseEvent) {
        const mouseY = d3.pointer(event)[1]
        if (mouseY < 150 && mouseY > 70) {
            toolTipContent.value_name = 'Voltage'
        } else if (mouseY < 270 && mouseY > 190) {
            toolTipContent.value_name = 'Current'
        } else {
            toolTipVisible.value = false
            return
        }
        const idx = bisect(datetime, x.invert(d3.pointer(event)[0]))
        toolTipVisible.value = true

        toolTipContent.string_list = Object.keys(stringStore.selectedString)
        toolTipContent.value_list = stringData.map((string) => {
            if (toolTipContent.value_name == 'Current') {
                return string.current[idx].toExponential(2)
            } else {
                return string.voltage[idx].toExponential(2)
            }
        })

        toolTipContent.date = datetime[idx]?.toUTCString() as string
        toolTipPosition.value = DOMRect.fromRect({
            width: 0,
            height: 0,
            x: event.clientX,
            y: event.clientY,
        })
    }

    function pointerleft() {
        toolTipVisible.value = false
    }

    svg.on('mousemove', function (event) {
        const date = x.invert(d3.pointer(event, this)[0])
        rule.attr('transform', `translate(${x(date)}, 0)`)
        event.preventDefault()
    }).on('mouseleave', function () {
        rule.attr('transform', 'translate(-1, 0)')
    })
}

const highLightString = (stringIdx: number) => {
    // 没有高亮，点击不同的stringIdx
    if (highLightStringIdx.value != stringIdx) {
        currents
            .attr('opacity', 0.2)
            .filter((_: any, idx: any) => idx === stringIdx)
            .attr('opacity', 1)

        voltages
            .attr('opacity', 0.2)
            .filter((_: any, idx: any) => idx === stringIdx)
            .attr('opacity', 1)

        highLightStringIdx.value = stringIdx
    } else {
        //点击之前的stringIdx取消高亮
        currents.attr('opacity', 1)
        voltages.attr('opacity', 1)
        highLightStringIdx.value = -1
    }
}

onMounted(() => {
    draw()
})

watch(
    () => forecastModelStore.forecast_model.model_name,
    () => {
        stringStore.clearSelectedString()
        draw()
    }
)

watch(
    () => stringStore.selectedString,
    () => {
        draw()
    }
)
</script>
<template>
    <div class="h-full w-full relative">
        <div
            :class="[
                'bg-theme-dark absolute h-8  font-bold text-center text-lg text-theme-light z-10 content-center',
                LANG_TYPE ? 'w-36' : 'w-28',
            ]"
        >
            {{ LANG_TYPE ? 'Compare View' : '比较视图' }}
        </div>
        <div class="h-80 w-full" ref="currentContainer"></div>
        <el-tooltip
            v-model:visible="toolTipVisible"
            placement="right"
            effect="dark"
            trigger="click"
            virtual-triggering
            :virtual-ref="triggerRef as any"
        >
            <template #content>
                <strong>{{ toolTipContent.value_name }} </strong> <br />
                <div
                    v-for="(item, idx) in toolTipContent.string_list"
                    class="flex content-center"
                >
                    <div
                        class="w-2 h-1 m-1"
                        :style="{
                            backgroundColor:
                                stringStore.selectedString[item].color,
                        }"
                    ></div>
                    {{ item }} : {{ toolTipContent.value_list[idx] }}
                </div>
                Date: {{ toolTipContent.date }} <br />
            </template>
        </el-tooltip>
    </div>
</template>

<style scoped>
.read-the-docs {
    color: #888;
}
</style>
