<script setup lang="ts">
import * as d3 from 'd3'
import chroma from 'chroma-js'
import { useStringStore } from '@/stores/string'
import { useforecastModelStore } from '@/stores/forecastModel'
const gradientContainer: Ref<HTMLDivElement | null> = ref(null)
// const model_name: Ref<string> = ref('power_new_covariate_120_24')
// const dataset: Ref<string> = ref('all_filtered_string_power_df')

const stringStore = useStringStore()
const forecastModelStore = useforecastModelStore()
const props = defineProps<{
    feature_importance: number[] | undefined
}>()

const toolTipVisible = ref(false)
const toolTipContent = reactive({
    string_name: '',
    value: '',
})
const triggerRef = ref({
    getBoundingClientRect() {
        return toolTipPosition.value
    },
})

const toolTipPosition = ref({
    top: 0,
    left: 0,
    bottom: 0,
    right: 0,
})

const draw = () => {
    const colors = chroma.scale(['#e4edf5', '#203e5b']).mode('lch').colors(5)
    let bands = 7
    if (forecastModelStore.forecast_model.dataset === 'cleaned') {
        bands = 2
    }
    if (props.feature_importance === undefined) {
        return
    }

    const container_width = (gradientContainer.value as HTMLDivElement)
        .clientWidth
    const container_height = (gradientContainer.value as HTMLDivElement)
        .clientHeight

    const margin = { top: 0, right: 2, bottom: 0, left: 0 },
        width = container_width - margin.left - margin.right,
        height = container_height - margin.top - margin.bottom

    const size: number = height
    const padding = 1
    const x = d3
        .scaleLinear()
        .domain([0, props.feature_importance.length - 1])
        .range([margin.right, width])

    const y_min = d3.min(props.feature_importance) as number
    const y_max = d3.max(props.feature_importance) as number
    const y = d3
        .scaleLinear()
        .domain([y_min, y_max])
        .range([size, size - bands * (size - padding)])

    const area = d3
        .area()
        .defined((d: any) => !isNaN(d))
        .x((_, idx) => {
            return x(idx)
        })
        .y0(size)
        .y1((d: any) => y(d))

    // A unique identifier (to avoid conflicts) for the clip rect and the reusable paths.
    const uid = `O-${Math.random().toString(16).slice(2)}`

    // clear
    d3.select('#gradientContainer').selectAll('*').remove()
    // Create the SVG container.
    const svg = d3.select('#gradientContainer').append('svg')

    svg.attr('width', width)
        .attr('height', height)
        .attr('viewBox', [0, 0, width, height])
        .attr('style', 'max-width: 100%; height: auto; font: 10px sans-serif;')
        .on('pointerenter pointermove', pointermoved)
        .on('pointerleave', pointerleft)
        .on('touchstart', (event) => event.preventDefault())

    const g = svg.append('g').attr('transform', `translate(0,${margin.top})`)

    // Add a rectangular clipPath and the reference area.
    const defs = g.append('defs')
    defs.append('clipPath')
        .attr('id', `${uid}-clip`)
        .append('rect')
        .attr('y', padding)
        .attr('width', width)
        .attr('height', size - padding)

    defs.append('path')
        .attr('id', `${uid}-path`)
        .attr('d', area(props.feature_importance as any))

    const horizonG = g.append('g')
    horizonG
        .attr(
            'clip-path',
            `url(${new URL(`#${uid}-clip`, location.toString())})`
        )
        .selectAll('use')
        .data(new Array(bands).fill(0))
        .enter()
        .append('use')
        .attr('xlink:href', `${new URL(`#${uid}-path`, location.toString())}`)
        .attr('fill', (_, i) => {
            return colors[i]
        })
        .attr('transform', (_, i) => `translate(0,${i * size})`)

    const xAxis = (g: any, x: any) => {
        g.call(
            d3
                .axisTop(x)
                .ticks(width / 80)
                .tickSizeOuter(0)
        )
            .call((gg: any) =>
                gg
                    .selectAll('.tick')
                    .filter((d: any) => {
                        return (
                            x(d as number) < margin.left ||
                            x(d as number) >= width - margin.right
                        )
                    })
                    .remove()
            )
            .call((gg: any) => gg.select('.domain').remove())
    }

    const gx = svg
        .append('g')
        .attr('transform', `translate(0,${height - margin.bottom})`)
        .call(xAxis as any, x)
    // Add the horizontal axis.
    // const xAxis = gx
    //     .call(
    //         d3
    //             .axisTop(x)
    //             .ticks(width / 80)
    //             .tickSizeOuter(0)
    //     )
    //     .call((g) =>
    //         g
    //             .selectAll('.tick')
    //             .filter((d) => {
    //                 return (
    //                     x(d as number) < margin.left ||
    //                     x(d as number) >= width - margin.right
    //                 )
    //             })
    //             .remove()
    //     )
    //     .call((g) => g.select('.domain').remove())

    gx.selectAll('text').style('fill', '#999')
    gx.selectAll('line').style('stroke', '#999')

    // Create the zoom behavior.
    const zoom = d3
        .zoom()
        .scaleExtent([1, 18])
        .extent([
            [margin.left, 0],
            [width - margin.right, height],
        ])
        .translateExtent([
            [margin.left, -Infinity],
            [width - margin.right, Infinity],
        ])
        .on('zoom', zoomed)
    // Initial zoom.
    svg.call(zoom as any)
    var xz = x
    // When zooming, redraw the area and the x axis.
    function zoomed(event: any) {
        toolTipVisible.value = false
        xz = event.transform.rescaleX(x)
        defs.attr(
            'transform',
            `translate(${event.transform.x},0) scale(${event.transform.k},1)`
        ).attr('stroke-width', 1 / event.transform.k)
        horizonG
            .attr(
                'transform',
                `translate(${event.transform.x},0) scale(${event.transform.k},1)`
            )
            .attr('stroke-width', 1 / event.transform.k)
        // pred.attr(
        //     'transform',
        //     `translate(${event.transform.x},0) scale(${event.transform.k},1)`
        // ).attr('stroke-width', 1 / event.transform.k)
        // grad.attr(
        //     'transform',
        //     `translate(${event.transform.x},0) scale(${event.transform.k},1)`
        // ).attr('stroke-width', 1 / event.transform.k)
        // // raw.attr('d', line(props.data['raw'] as any))
        // // pred.attr('d', line(props.data['pred'] as any))
        gx.call(xAxis, xz)
    }

    const bisect = d3.bisector((d) => d).center
    const x_rangeList = d3.range(0, props.feature_importance.length - 1)
    function pointermoved(event: MouseEvent) {
        toolTipVisible.value = true
        const idx = bisect(x_rangeList, xz.invert(d3.pointer(event)[0]))
        // console.log(event)
        toolTipContent.string_name = stringStore.stringNames[idx]
        const val = props.feature_importance?.at(idx) as number
        toolTipContent.value = val.toExponential(2)
        //idx.toString()

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
}

watch(
    () => props.feature_importance,
    () => {
        draw()
    }
)
</script>
<template>
    <div
        class="w-full h-full"
        ref="gradientContainer"
        id="gradientContainer"
    ></div>
    <el-tooltip
        v-model:visible="toolTipVisible"
        placement="right"
        effect="dark"
        trigger="click"
        virtual-triggering
        :virtual-ref="triggerRef as any"
    >
        <template #content>
            <strong>{{ toolTipContent.string_name }} </strong> <br />
            feature_importance: {{ toolTipContent.value }}
        </template>
    </el-tooltip>
</template>
