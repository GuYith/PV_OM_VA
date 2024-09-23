<script setup lang="ts">
import * as d3 from 'd3'
import * as turf from '@turf/turf'
import mapboxgl, { Map } from 'mapbox-gl'
import MapboxDraw from '@mapbox/mapbox-gl-draw'
import '@mapbox/mapbox-gl-draw/dist/mapbox-gl-draw.css'
import mapdrawStyles from '@/assets/mapbox-theme.js'
import { ref, Ref, reactive, watch, onUnmounted } from 'vue'
// import { event as d3Event } from 'd3-selection'
import { Geometry } from 'geojson'
import 'mapbox-gl/dist/mapbox-gl.css'
import axios from '@/request.ts'
import { StringPoint, LABAL_COLOR_MAP, LANG_TYPE } from '@/common'
import { useforecastModelStore } from '@/stores/forecastModel'
import { useStringStore } from '@/stores/string'

const mapContainer: Ref<HTMLDivElement | null> = ref(null)
const scatterContainer: Ref<HTMLDivElement | null> = ref(null)
const LegendContainer: Ref<HTMLDivElement | null> = ref(null)
const forecastModelStore = useforecastModelStore()
const stringStore = useStringStore()
// 0 => map 1 => scatter
const status = ref(false)
const currentMode: Ref<String | null> = ref('zoom')
// const chartData = reactive([])
const opacityHighLight = 0.9
const scatterFilterStringNameList: Ref<string[] | undefined> = ref(undefined)
const mapFilterStringNameList: Ref<string[] | undefined> = ref(undefined)
let map: Map
let dot: any
let brushG: any
let brush: any
const modelValue = reactive({
    lat: 27.795514303438515,
    lng: 120.004,
    bearing: 0,
    pitch: 0,
    zoom: 14,
})

const toolTipVisible = ref(false)
const toolTipContent = reactive({
    string_name: '',
    label: 0,
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

const d3_gElement: Ref<any | null> = ref(null)
const getLocation = () => {
    return {
        ...map.getCenter(),
        bearing: map.getBearing(),
        pitch: map.getPitch(),
        zoom: map.getZoom(),
    }
}

const addPanelData = () => {
    const panelJson = stringStore.mapViewData.geo_map_data as any
    map.addSource('panel', {
        type: 'geojson',
        data: panelJson as Geometry,
    })

    map.addLayer({
        id: 'panel',
        type: 'fill',
        source: 'panel',
        paint: {
            'fill-color': [
                'case',
                ['boolean', ['feature-state', 'unselect'], false],
                LABAL_COLOR_MAP[6],
                ['==', ['get', 'label'], 0],
                LABAL_COLOR_MAP[0],
                ['==', ['get', 'label'], 1],
                LABAL_COLOR_MAP[1],
                ['==', ['get', 'label'], 2],
                LABAL_COLOR_MAP[2],
                ['==', ['get', 'label'], 3],
                LABAL_COLOR_MAP[3],
                ['==', ['get', 'label'], 4],
                LABAL_COLOR_MAP[4],
                ['==', ['get', 'label'], 5],
                LABAL_COLOR_MAP[5],
                LABAL_COLOR_MAP[6],
            ],
            'fill-opacity': [
                'case',
                ['boolean', ['feature-state', 'unselect'], false],
                0.5,
                1,
            ],
        },
    })

    map.on('click', 'panel', (e: any) => {
        const name = e.features[0].properties.name
        panelJson.features.forEach((panel: any, pIdx: any) => {
            if (panel.properties.name == name) {
                map.setFeatureState(
                    { source: 'panel', id: pIdx },
                    { clicked: true }
                )
                return
            }
        })
    })

    map.on('mouseenter', 'panel', () => {
        map.getCanvas().style.cursor = 'pointer'
    })

    map.on('mouseleave', 'panel', () => {
        map.getCanvas().style.cursor = ''
    })

    // map.addSource('panel-label', {
    //     type: 'geojson',
    //     data: panelLabelJson as unknown as Geometry,
    // })
}

function transformZoomBy([x, y]: [any, any], trans: any) {
    return {
        transformX: x * trans.k + trans.x,
        transformY: y * trans.k + trans.y,
    }
}
const drawscatterChart = async () => {
    // set the dimensions and margins of the graph
    const container_width = (scatterContainer.value as HTMLDivElement)
        .clientWidth
    const container_height = (scatterContainer.value as HTMLDivElement)
        .clientHeight

    const margin = { top: 10, right: 10, bottom: 10, left: 10 },
        width = container_width - margin.left - margin.right,
        height = container_height - margin.top - margin.bottom

    const data = stringStore.mapViewData.scatter_data as StringPoint[]

    stringStore.updateStringLables(data)

    // clear
    d3.select('#scatterContainer').selectAll('*').remove()
    // Create the SVG container

    const svg = d3
        .select<SVGSVGElement, unknown>('#scatterContainer')
        .append('svg')
        .attr('width', container_width)
        .attr('height', container_height)
        .on('pointerenter pointermove', pointermoved)
        .on('pointerleave', pointerleft)
        .on('touchstart', (event) => event.preventDefault())
    const g = svg.append('g')
    d3_gElement.value = g
    // Read the data
    // get max min
    var x_list: number[] = []
    var y_list: number[] = []
    var label_list: string[] = []
    const minZoomScale = 0.8,
        maxZoomScale = 8

    data.forEach((item: any) => {
        x_list.push(Number(item.x))
        y_list.push(Number(item.y))
        label_list.push(item.label)
    })
    const x_min = Math.min(...x_list),
        y_min = Math.min(...y_list)
    const x_max = Math.max(...x_list),
        y_max = Math.max(...y_list)
    // Add X axis
    const x = d3
        .scaleLinear()
        .domain([x_min, x_max])
        .range([margin.left, width - margin.right])

    // Add Y axis
    const y = d3
        .scaleLinear()
        .domain([y_min, y_max])
        .range([height - margin.bottom, margin.top])

    const dotG = g.append('g')
    // Add dots
    dot = dotG
        .selectAll('circle')
        .data(data)
        .join('circle')
        .attr('cx', function (d) {
            return x(Number(d.x))
        })
        .attr('cy', function (d) {
            return y(Number(d.y))
        })
        .attr('r', 2)
        .attr('fill', function (d) {
            return LABAL_COLOR_MAP[Number(d.label)]
        })
    // .style('opacity', 0.6)

    let transform: any = {
        x: 0,
        y: 0,
        k: 1,
    }

    function brushed({ selection }: any) {
        let value: any[] = []
        if (selection) {
            const [[x0, y0], [x1, y1]] = selection
            brushSelection = selection
            value = dot
                .attr('fill', 'gray')
                .attr('opacity', 0.5)
                .filter((d: any) => {
                    const { transformX, transformY } = transformZoomBy(
                        [x(Number(d.x)), y(Number(d.y))],
                        transform
                    )
                    return (
                        x0 <= transformX &&
                        transformX <= x1 &&
                        y0 <= transformY &&
                        transformY <= y1
                    )
                })
                .attr('fill', function (d: any) {
                    return LABAL_COLOR_MAP[Number(d.label)]
                })
                .attr('opacity', opacityHighLight)
                .data()
            if (value.length > 0) {
                scatterFilterStringNameList.value = value.map(
                    (item) => item.string_name
                )
            }
        } else {
            dot.attr('fill', function (d: any) {
                return LABAL_COLOR_MAP[Number(d.label)]
            }).attr('opacity', opacityHighLight)
        }
        svg.property('value', value).dispatch('input')
    }

    let zoom: any
    let brushSelection: any
    brush = d3.brush().on('start brush end', brushed)
    var scaleFactor = 1
    const zoomUnit = 1
    bindZoom()
    function bindZoom() {
        zoom = d3
            .zoom()
            .scaleExtent([minZoomScale, maxZoomScale])
            .on('zoom', function () {
                transform = d3.zoomTransform(this as any)

                scaleFactor = transform.k
                g.attr('transform', transform)
                g.attr('stroke-width', 1 / transform.k)
                if (brushG) {
                    const [[x0, x1], [y0, y1]] = brushSelection
                    const newExtent = [
                        [x0, x1],
                        [y0, y1],
                    ]
                    brushG.call(brush.move, newExtent)
                }
            })
        svg.call(zoom)
    }
    function bindBrush() {
        brushG = svg
            .append('g')
            .attr('class', 'brush')
            .on('pointerenter pointermove', pointermoved)
            .on('pointerleave', pointerleft)
        brushG.call(brush)
    }
    function stopBrush() {
        brushG.call(brush.clear)
        brushG.remove()
        scatterFilterStringNameList.value = undefined
        brushG = null
    }

    function stopZoom() {
        svg.on('mousedown.zoom', null)
        svg.on('mousemove.zoom', null)
        svg.on('dblclick.zoom', null)
        svg.on('touchstart.zoom', null)
        // svg.on('wheel.zoom', null)
    }

    function zoomIn() {
        const svgWidth = Number(svg.attr('width'))
        const svgHeight = Number(svg.attr('height'))
        const centerX = svgWidth / 2
        const centerY = svgHeight / 2

        if (scaleFactor + zoomUnit <= maxZoomScale) {
            scaleFactor += zoomUnit
            const curTrans: any = d3.zoomIdentity
                .translate(transform.x - centerX, transform.y - centerY)
                .scale(scaleFactor)
            svg.transition().duration(750).call(zoom.transform, curTrans)
        }
    }

    function zoomOut() {
        const svgWidth = Number(svg.attr('width'))
        const svgHeight = Number(svg.attr('height'))
        const centerX = svgWidth / 2
        const centerY = svgHeight / 2
        if (scaleFactor - zoomUnit >= minZoomScale) {
            scaleFactor -= zoomUnit
            const curTrans: any = d3.zoomIdentity
                .translate(transform.x + centerX, transform.y + centerY)
                .scale(scaleFactor)
            svg.transition().duration(750).call(zoom.transform, curTrans)
        }
    }

    dotG.insert('circle', '.brush')
        .attr('class', 'highlight-circle')
        .attr('r', 2 + 0.5) // slightly larger than our points
        .attr('fill', 'none')
        .attr('display', 'none')
        .attr('cx', x(data[0].x))
        .attr('cy', y(data[0].y))

    function pointermoved(event: MouseEvent) {
        const mouse = d3.pointer(event)
        const dist = data.map((item) => {
            const dx = mouse[0] - x(item.x)
            const dy = mouse[1] - y(item.y)
            return dx * dx + dy * dy
        })
        const minDist = Math.min(...dist)
        const index = dist.indexOf(minDist)

        const target = data[index]
        if (
            scatterFilterStringNameList.value !== undefined &&
            !scatterFilterStringNameList.value.includes(target.string_name)
        ) {
            console.log(scatterFilterStringNameList.value, target.string_name)
            return
        }
        d3.select('.highlight-circle')
            .style('stroke', '#373D3B')
            .attr('display', '')
            .attr('cx', x(target.x))
            .attr('cy', y(target.y))
        toolTipVisible.value = true
        // console.log(event)
        toolTipContent.string_name = target.string_name
        toolTipContent.label = target.label
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
        d3.select('.highlight-circle').attr('display', 'none')
        // highlightOutput.text('')
    }

    d3.select('#brushIcon').on('click', () => {
        if (currentMode.value !== 'brush') {
            currentMode.value = 'brush'
            bindBrush()
            stopZoom()
        } else {
            currentMode.value = 'default'
            stopBrush()
            bindZoom()
        }
        // console.log(currentMode.value)
    })

    d3.select('#zoomInIcon').on('click', () => {
        zoomIn()
    })

    d3.select('#zoomOutIcon').on('click', () => {
        zoomOut()
    })

    d3.select('#resetIcon').on('click', () => {
        if (currentMode.value !== 'default') {
            currentMode.value = 'default'
            stopBrush()
            bindZoom()
        }
        const curTrans: any = d3.zoomIdentity.translate(0, 0).scale(1)
        svg.transition().duration(750).call(zoom.transform, curTrans)
    })

    drawLegend()
}

const drawLegend = () => {
    const container_width = (LegendContainer.value as HTMLDivElement)
        .clientWidth
    const container_height = (LegendContainer.value as HTMLDivElement)
        .clientHeight
    const width = container_width
    const height = container_height

    // clear
    d3.select(LegendContainer.value).selectAll('*').remove()
    const svg = d3
        .select(LegendContainer.value)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .attr('viewBox', [0, 0, width, height])
        .style('overflow', 'visible')
        .style('display', 'block')

    // 创建图例容器
    const legend = svg
        .append('g')
        .attr('transform', `translate(${width - 15}, ${0})`) // 定位到 SVG 的右侧

    legend
        .append('g')
        .append('text')
        .attr('x', 0)
        .attr('y', -10)
        .style('font-size', '10px')
        .style('fill', '#666')
        .attr('dy', '0.35em') // 调整文本垂直对齐
        .text('cluster')
    // 为每个类别添加一个矩形和文本标签
    LABAL_COLOR_MAP.forEach((color, index) => {
        if (index === 6) return
        const legendItem = legend
            .append('g')
            .attr('transform', `translate(0, ${index * 10})`)

        legendItem
            .append('rect')
            .attr('width', 10)
            .attr('height', 10)
            .attr('fill', color)

        legendItem
            .append('text')
            .attr('x', 15)
            .attr('y', 5)
            .style('font-size', '10px')
            .style('fill', '#666')
            .attr('dy', '0.35em') // 调整文本垂直对齐
            .text(index)
    })
}

const addRasterTileLayer = (
    map: Map,
    url: string,
    sourceId: string,
    layerId: string
) => {
    map.addSource(sourceId, {
        type: 'raster',
        tiles: [url],
        tileSize: 256,
    })
    map.addLayer({
        id: layerId,
        type: 'raster',
        source: sourceId,
    })
}

const initMap = () => {
    const { lng, lat, bearing, pitch, zoom } = modelValue
    //天地图的token
    const tiandituToken = 'dc59de8bf86902093bd4edb1b2777dde'

    //矢量底图
    const vecwUrl =
        'https://t0.tianditu.gov.cn/vec_w/wmts?' +
        'SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=vec&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&' +
        'TILECOL={x}&TILEROW={y}&TILEMATRIX={z}&tk=' +
        tiandituToken
    //矢量注记
    const cvawUrl =
        'https://t3.tianditu.gov.cn/cva_w/wmts?' +
        'SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=cva&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&' +
        'TILECOL={x}&TILEROW={y}&TILEMATRIX={z}&tk=' +
        tiandituToken

    // const gaodeToken = 'ffad9fed9880dc1c86a0294f2f0f63ab'
    // const gaodeUrl =
    //     'http://wprd04.is.autonavi.com/appmaptile?x={x}&y={y}&z={z}&lang=zh_cn&size=1&scl=2&style=7&key=' +
    //     gaodeToken

    // //影像底图
    // const imgwUrl =
    //     'https://t0.tianditu.gov.cn/img_w/wmts?' +
    //     'SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=vec&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&' +
    //     'TILECOL={x}&TILEROW={y}&TILEMATRIX={z}&tk=' +
    //     tiandituToken
    // //影像注记
    // const ciawUrl =
    //     'https://t3.tianditu.gov.cn/cia_w/wmts?' +
    //     'SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=cva&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&' +
    //     'TILECOL={x}&TILEROW={y}&TILEMATRIX={z}&tk=' +
    //     tiandituToken

    mapboxgl.accessToken =
        'pk.eyJ1IjoiZ3VndWR1ZHUiLCJhIjoiY2xzMmw5cWMzMGN0ZTJsbjI0cWo3MWE2byJ9.IApkEpat6fEs_UL2fi-nPg'
    map = new mapboxgl.Map({
        container: mapContainer.value as HTMLElement,
        style: 'mapbox://styles/mapbox/streets-v12', // Replace with your preferred map style
        // style: {
        //     version: 8,
        //     layers: [],
        //     sources: {},
        //     glyphs: 'mapbox://fonts/mapbox/{fontstack}/{range}.pbf',
        // },
        // center: [-68.137343, 45.137451],
        center: [lng, lat],
        bearing,
        pitch,
        zoom,
    })

    map.on('load', function () {
        // 加载矢量底图及其标注
        addRasterTileLayer(map, vecwUrl, 'vecw', 'vecw')
        addRasterTileLayer(map, cvawUrl, 'cvaw', 'cvaw')

        //加载影响地图及其标注
        // addRasterTileLayer(map, imgwUrl, 'vecw', 'vecw')
        // addRasterTileLayer(map, ciawUrl, 'cvaw', 'cvaw')
        addPanelData()
    })
    map.on('move', getLocation)
    map.on('zoom', getLocation)
    map.on('rotate', getLocation)
    map.on('pitch', getLocation)
    map.on('mouseenter', 'panel', (e) => {
        // Change the cursor style as a UI indicator.
        map.getCanvas().style.cursor = 'pointer'
        const features = e.features as any
        const target = features[0]

        toolTipVisible.value = true
        toolTipContent.string_name = target.properties.string_name
        toolTipContent.label = target.properties.label
        const rect = map.getCanvas().getBoundingClientRect()
        toolTipPosition.value = DOMRect.fromRect({
            width: 0,
            height: 0,
            x: e.point.x + rect.x,
            y: e.point.y + rect.y,
        })
    })
    const draw = new MapboxDraw({
        displayControlsDefault: false,
        // Select which mapbox-gl-draw control buttons to add to the map.
        controls: {
            polygon: true,
            trash: true,
        },
        styles: mapdrawStyles,
        // Set mapbox-gl-draw to draw by default.
        // The user does not have to click the polygon control button first.
        defaultMode: 'draw_polygon',
    })
    map.addControl(draw)
    map.on('mouseleave', 'panel', () => {
        toolTipVisible.value = false
    })
    map.on('draw.delete', function () {
        const allFeatureIds = map
            .querySourceFeatures('panel')
            .map((item) => item.id)

        allFeatureIds.map((id) => {
            map.setFeatureState(
                {
                    source: 'panel',
                    id: id,
                },
                { unselect: false }
            )
        })
        mapFilterStringNameList.value = undefined
    })

    map.on('draw.create', function (e) {
        if (
            e.features.length > 0 &&
            e.features[0].geometry.type === 'Polygon'
        ) {
            const polygon = e.features[0]
            const polygonBoudingBox = turf.bbox(polygon)
            const bb1: any = [polygonBoudingBox[0], polygonBoudingBox[1]]
            const bb2: any = [polygonBoudingBox[2], polygonBoudingBox[3]]
            const pointPixel1 = map.project(bb1)
            const pointPixel2 = map.project(bb2)

            const allFeatureIds = map
                .querySourceFeatures('panel')
                .map((item) => item.id)

            // 使用绘制的多边形查询地图上的要素
            var insideFeautures = map.queryRenderedFeatures(
                [pointPixel1, pointPixel2],
                {
                    layers: ['panel'], // 指定要查询的图层 ID
                } as any
            )

            allFeatureIds.map((id) => {
                map.setFeatureState(
                    {
                        source: 'panel',
                        id: id,
                    },
                    { unselect: true }
                )
            })

            mapFilterStringNameList.value = insideFeautures.map(
                (item: any) => item['properties']['string_name']
            )

            if (!brushG && typeof brushG !== 'undefined') {
                brushG.call(brush.clear)
                brushG.remove()
                scatterFilterStringNameList.value = undefined
                brushG = null
            }

            insideFeautures.map((item) => {
                map.setFeatureState(
                    {
                        source: 'panel',
                        id: item.id,
                    },
                    { unselect: false }
                )
            })
        }
    })
}

const updateScatterHighlight = () => {
    if (mapFilterStringNameList.value === undefined) {
        dot.attr('fill', function (d: any) {
            return LABAL_COLOR_MAP[Number(d.label)]
        }).attr('opacity', opacityHighLight)
    } else {
        const stringNameList = mapFilterStringNameList.value as string[]
        dot.attr('fill', 'gray')
            .attr('opacity', 0.5)
            .filter((d: any) => stringNameList.includes(d.string_name))
            .attr('fill', function (d: any) {
                return LABAL_COLOR_MAP[Number(d.label)]
            })
            .attr('opacity', opacityHighLight)
    }
}
const updateMapHighlight = () => {
    const allFeatures = map.querySourceFeatures('panel')
    if (scatterFilterStringNameList.value === undefined) {
        allFeatures.map((item) => {
            map.setFeatureState(
                {
                    source: 'panel',
                    id: item.id,
                },
                { unselect: false }
            )
        })
    } else {
        const selectedNames = scatterFilterStringNameList.value as string[]
        const selectedFeatures = allFeatures.filter((item: any) =>
            selectedNames.includes(item['properties']['string_name'])
        )
        allFeatures.map((item) => {
            map.setFeatureState(
                {
                    source: 'panel',
                    id: item.id,
                },
                { unselect: true }
            )
        })
        selectedFeatures.map((item) => {
            map.setFeatureState(
                {
                    source: 'panel',
                    id: item.id,
                },
                { unselect: false }
            )
        })
    }
}

const handleSwitch = () => {
    if (status.value === true) {
        setTimeout(() => {
            map.resize()
        }, 10)
    }
}

watch(modelValue, (nextValue) => {
    const curr = getLocation()
    if (curr.lng != nextValue.lng || curr.lat != nextValue.lat)
        map.setCenter({ lng: nextValue.lng, lat: nextValue.lat })
    if (curr.pitch != nextValue.pitch) map.setPitch(nextValue.pitch)
    if (curr.bearing != nextValue.bearing) map.setBearing(nextValue.bearing)
    if (curr.zoom != nextValue.zoom) map.setZoom(nextValue.zoom)
})

watch(
    () => [
        stringStore.mapViewData.geo_map_data,
        stringStore.mapViewData.scatter_data,
    ],
    () => {
        drawscatterChart()
        initMap()
    }
)

watch(
    () => mapFilterStringNameList.value,
    () => {
        updateScatterHighlight()
    }
)

watch(
    () => scatterFilterStringNameList.value,
    () => {
        updateMapHighlight()
    }
)

onUnmounted(() => {
    map.remove()
})
</script>

<template>
    <div class="h-full w-full relative">
        <div
            :class="[
                'bg-theme-dark absolute  h-8 absolute font-bold text-center text-lg text-theme-light z-10 content-center',
                LANG_TYPE ? 'w-28' : 'w-28',
            ]"
        >
            {{ LANG_TYPE ? 'Map View' : '映射视图' }}
        </div>
        <el-switch
            class="right-5 z-10"
            v-model="status"
            :onChange="handleSwitch"
            inline-prompt
            style="--el-switch-on-color: #373d3b; --el-switch-off-color: #ccc"
            :inactive-text="LANG_TYPE ? 'Scatter' : '散点图'"
            :active-text="LANG_TYPE ? 'Map' : '地图'"
        />
        <div class="absolute right-5 top-10 z-10" v-show="status == false">
            <i-ant-design-zoom-in-outlined
                id="zoomInIcon"
                class="text-gray-400 hover:text-theme-dark"
            />
            <i-ant-design-zoom-out-outlined
                id="zoomOutIcon"
                class="text-gray-400 hover:text-theme-dark"
            />
            <i-ant-design-clear-outlined
                id="resetIcon"
                class="text-gray-400 hover:text-theme-dark"
            />
            <i-mdi-SelectDrag
                id="brushIcon"
                :class="[
                    'hover:text-theme-dark',
                    currentMode === 'brush'
                        ? 'text-theme-dark'
                        : 'text-gray-400',
                ]"
            />
        </div>
        <div
            class="absolute right-5 bottom-10 z-10 h-10 w-32"
            ref="LegendContainer"
        ></div>
        <div
            v-show="status"
            ref="mapContainer"
            class="map-container h-full w-full"
        ></div>
        <div
            v-show="status == false"
            id="scatterContainer"
            ref="scatterContainer"
            class="h-full w-full"
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
                <div>
                    <div
                        class="w-1 h-2"
                        :style="{
                            backgroundColor:
                                LABAL_COLOR_MAP[toolTipContent.label],
                        }"
                    ></div>
                    {{ LANG_TYPE ? 'cluster' : '类别' }} :
                    {{ toolTipContent.label }}
                </div>
            </template>
        </el-tooltip>
    </div>
</template>

<style scoped>
.map-container {
    flex: 1;
}
.el-switch {
    position: absolute;
}
:deep(.mapboxgl-ctrl-logo) {
    height: 10px;
}
:deep(.mapboxgl-ctrl-attrib.mapboxgl-compact) {
    display: none !important;
}
.read-the-docs {
    color: #888;
}

:deep(.mapboxgl-ctrl-group) {
    margin-top: 40px;
}
</style>
