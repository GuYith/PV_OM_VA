<script setup lang="ts">
import * as d3 from 'd3'
import { useStringStore } from '@/stores/string'
import { Series, TIMESERIES_COLORS } from '@/common'
const stringStore = useStringStore()

const timeSeriesContainer: Ref<HTMLDivElement | null> = ref(null)
const props = defineProps<{
    data: Series
    showXAxis: boolean
}>()
const toolTipVisible = ref(false)
const toolTipContent = reactive({
    date: '',
    string_name: props.data.string_name,
    pred: '',
    true: '',
    importance: '',
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
const isAnomaly = (val: number) => {
    const { residual_mean, residual_var } = props.data
    if (val <= residual_mean + stringStore.anomalyThreshold * residual_var) {
        return false
    }
    return true
}
const generate_anomaly = () => {
    // stringStore.anomalyStep
    // stringStore.anomalyThreshold
    const { residual } = props.data
    if (!residual || residual.length === 0) {
        return []
    }
    const len = residual.length
    const anomalyWindows = []
    var i = 0
    while (i < len) {
        if (isAnomaly(residual[i]) === false) {
            i += 1
            continue
        }
        var r = i
        while (r < len && isAnomaly(residual[r]) === true) {
            r++
        }

        if (r - i >= stringStore.anomalyStep) {
            anomalyWindows.push([i, r - 1])
        }
        if (i == r) {
            i += 1
        } else {
            i = r
        }
    }
    return anomalyWindows
}

const draw = () => {
    if (!props.data || Object.keys(props.data).length === 0) {
        return
    }
    const container_width = (timeSeriesContainer.value as HTMLDivElement)
        .clientWidth
    const container_height = (timeSeriesContainer.value as HTMLDivElement)
        .clientHeight

    const margin = { top: 0, right: 40, bottom: 20, left: 40 }
    if (props.showXAxis === true) {
        margin.top = 20
    }

    const width = container_width - margin.left / 4
    const height = container_height

    const datetime = stringStore.predictResults.pred_datetime.map(
        d3.utcParse('%Y-%m-%d %H:%M:%S')
    )
    const anomalyWindows = generate_anomaly()
    // const grad_datetime = stringStore.predictResults.grad_datetime.map(
    //     d3.utcParse('%Y-%m-%d %H:%M:%S')
    // )
    const x = d3.scaleUtc(d3.extent(datetime as any) as any, [
        margin.left,
        width - margin.right,
    ])

    const y = d3.scaleLinear(
        [
            d3.min([...props.data['raw'], ...props.data['pred']]) as number,
            d3.max([...props.data['raw'], ...props.data['pred']]) as number,
        ],
        [height - margin.bottom, margin.top]
    )

    // const x_grad = d3.scaleUtc(d3.extent(grad_datetime as any) as any, [
    //     margin.left,
    //     width,
    // ])

    const curGrad = props.data['time_grad'] as number[]

    const y_grad = d3.scaleLinear(
        [d3.min(curGrad) as number, d3.max(curGrad) as number],
        [height - margin.bottom, margin.top]
    )

    const area = d3
        .area()
        .x((_, idx) => x(datetime[idx] as any))
        .y0(y_grad(0))
        .y1((d) => y_grad(d as any))

    const line = d3
        .line()
        .x((_, idx) => x(datetime[idx] as any))
        .y((d) => {
            return y(d as any)
        })

    // clear
    d3.select(timeSeriesContainer.value).selectAll('*').remove()
    // Create the SVG container.
    const svg = d3
        .select(timeSeriesContainer.value)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .on('pointerenter pointermove', pointermoved)
        .on('pointerleave', pointerleft)
        .on('touchstart', (event) => event.preventDefault())
    // .attr('style', 'max-width: 100%; height: auto; font: 10px sans-serif;')

    // 蒙版，防止折线超过左右边界
    svg.append('defs')
        .append('clipPath')
        .attr('id', `clip-${props.data.string_name}`)
        .append('rect')
        .attr('x', margin.left)
        .attr('width', width - margin.right * 2)
        .attr('height', height)

    // const dateFormat = d3.timeFormat('%Y-%m-%d %H:%M:%S')

    const gradG = svg
        .append('g')
        .attr('clip-path', `url(#clip-${props.data.string_name})`)
    const rawG = svg
        .append('g')
        .attr('clip-path', `url(#clip-${props.data.string_name})`)
    const predG = svg
        .append('g')
        .attr('clip-path', `url(#clip-${props.data.string_name})`)
    const anomalyG = svg
        .append('g')
        .attr('clip-path', `url(#clip-${props.data.string_name})`)

    const rects = anomalyG
        .selectAll('rect')
        .data(anomalyWindows)
        .enter()
        .append('rect')
        .attr('x', (d) =>
            Math.min(x(datetime[d[0]] as any), x(datetime[d[1]] as any))
        )
        .attr('width', (d) =>
            Math.abs(x(datetime[d[1]] as any) - x(datetime[d[0]] as any))
        )
        .attr('height', height)
        .attr('fill', 'rgba(200,200,200, 0.3)')

    // const y_anomaly = d3.scaleLinear(
    //     [
    //         d3.min(props.data['residual']) as number,
    //         d3.max(props.data['residual']) as number,
    //     ],
    //     [height - margin.bottom, margin.top]
    // )

    // const line_anomly = d3
    //     .line()
    //     .x((_, idx) => x(datetime[idx] as any))
    //     .y((d) => {
    //         return y_anomaly(d as any)
    //     })
    // const anomaly = anomalyG
    //     .append('path')
    //     .attr('fill', 'none')
    //     .attr('stroke', 'red')
    //     .attr('stroke-width', 1)
    //     .attr('d', line_anomly(props.data['residual'] as any))

    // Add the x-axis
    const xAxis = (g: any, x: any) =>
        g.call(
            d3
                .axisBottom(x)
                .ticks(width / 80)
                .tickSizeOuter(0)
            // .tickFormat(dateFormat)
        )
    // Add the x-axis.
    const gx = svg
        .append('g')
        .attr('transform', `translate(0,${height - margin.bottom})`)
        .call(xAxis as any, x)

    // Add the left y-axis for timeseries
    svg.append('g')
        .attr('transform', `translate(${margin.left}, 0)`)
        .call(d3.axisLeft(y).ticks(height / 20))
        .call((g) =>
            g
                .selectAll('.tick line')
                .attr('stroke', '#ddd')
                .attr('stroke-opacity', 0.1)
        )
    // Add the right y-axis for timeseries
    svg.append('g')
        .attr('transform', `translate(${width - margin.right}, 0)`)
        .call(
            d3
                .axisRight(y_grad)
                .ticks(height / 30)
                .tickFormat(d3.format('.1e'))
        )
        .call((g) =>
            g
                .selectAll('.tick line')
                .attr('stroke', '#ddd')
                .attr('stroke-opacity', 0.1)
        )

    // Append a path for the line.
    const raw = rawG
        .append('path')
        .attr('fill', 'none')
        .attr('stroke', TIMESERIES_COLORS[0])
        .attr('stroke-width', 1)
        .attr('d', line(props.data['raw'] as any))

    const pred = predG
        .append('path')
        .attr('fill', 'none')
        .attr('stroke', TIMESERIES_COLORS[1])
        .attr('stroke-width', 1)
        .attr('d', line(props.data['pred'] as any))

    // add grad area
    const grad = gradG
        .append('path')
        .attr('fill', TIMESERIES_COLORS[2])
        .attr('d', area(props.data['time_grad'] as any))

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
        xz = event.transform.rescaleX(x)
        raw.attr(
            'transform',
            `translate(${event.transform.x},0) scale(${event.transform.k},1)`
        ).attr('stroke-width', 1 / event.transform.k)
        pred.attr(
            'transform',
            `translate(${event.transform.x},0) scale(${event.transform.k},1)`
        ).attr('stroke-width', 1 / event.transform.k)

        rects
            .attr(
                'transform',
                `translate(${event.transform.x},0) scale(${event.transform.k},1)`
            )
            .attr('stroke-width', 1 / event.transform.k)
        grad.attr(
            'transform',
            `translate(${event.transform.x},0) scale(${event.transform.k},1)`
        ).attr('stroke-width', 1 / event.transform.k)
        // raw.attr('d', line(props.data['raw'] as any))
        // pred.attr('d', line(props.data['pred'] as any))
        gx.call(xAxis, xz)
    }

    const bisect = d3.bisector((d) => d).center
    function pointermoved(event: MouseEvent) {
        toolTipVisible.value = true
        const idx = bisect(datetime, xz.invert(d3.pointer(event)[0]))
        // console.log(idx, x.invert(d3.pointer(event)[0]))
        toolTipContent.pred = props.data['pred'][idx].toExponential(2)
        toolTipContent.true = props.data['raw'][idx].toExponential(2)
        toolTipContent.importance =
            props.data['time_grad']![idx].toExponential(2)
        toolTipContent.date = stringStore.predictResults.pred_datetime[idx]
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

    const rule = svg
        .append('g')
        .append('line')
        .attr('y1', height)
        .attr('y2', 0)
        .attr('stroke', '#666')
        .attr('stroke-dasharray', '2,2')
        .attr('transform', 'translate(-1, 0)')

    svg.on('mousemove', function (event) {
        const date = xz.invert(d3.pointer(event)[0])
        rule.attr('transform', `translate(${xz(date)}, 0)`)
        event.preventDefault()
    }).on('mouseleave', function () {
        rule.attr('transform', 'translate(-1, 0)')
    })
}

onMounted(() => {
    draw()
})

watch(
    () => [
        props.data['raw'],
        props.data['pred'],
        stringStore.anomalyStep,
        stringStore.anomalyThreshold,
    ],
    () => {
        draw()
    }
)
</script>
<template>
    <div
        class="w-full h-full"
        ref="timeSeriesContainer"
        id="timeSeriesContainer"
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
            date: {{ toolTipContent.date }} <br />
            pred: {{ toolTipContent.pred }} <br />
            true:{{ toolTipContent.true }} <br />
            feature_importance: {{ toolTipContent.importance }}
        </template>
    </el-tooltip>
</template>
