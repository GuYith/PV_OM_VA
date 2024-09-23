import { defineStore } from 'pinia'
import {
    StringInfo,
    PredictResults,
    StringCV,
    StringCVC,
    StringPoint,
} from '@/common'
import { useTreeStore } from './tree'
import chroma from 'chroma-js'
import axios from '@/request.ts'

const color_len = 8
const colorMap = chroma
    .scale(['#bdd7e7', '#008080', '#08519c'])
    .colors(color_len)

export const useStringStore = defineStore('stringInfo', () => {
    const treeStore = useTreeStore()
    const colorList: Ref<string[]> = ref([])
    const stringInfos: Ref<StringInfo[]> = ref([])
    const stringNames: Ref<string[]> = ref([])
    const scrollDisabled = ref(false)
    const step = 10
    const sortParam = ref('')
    const anomalyThreshold = ref(3)
    const anomalyStep = ref(10)
    const sortOrder = ref('asc')
    const showNum = ref(step)
    const filterValue: Ref<string[]> = ref([] as string[])

    const predictResults: Ref<PredictResults> = ref({
        pred_datetime: [],
        grad_datetime: [],
        series: [],
    })

    const mapViewData = reactive({
        scatter_data: {},
        geo_map_data: {},
    })

    const selectedString: Ref<{
        [key: string]: StringCVC
    }> = ref({})

    const showSeries = computed(() => {
        if (predictResults.value === undefined) {
            return []
        }
        const idList: number[] = showStringInfos.value.map((item) => item.id)
        const predictIdList: number[] = predictResults.value.series.map(
            (item) => item.id
        )
        const filteredIdList: number[] = idList.filter(
            (item) => item in predictIdList
        )

        return filteredIdList.map((id) => {
            if (
                treeStore.activeTree &&
                treeStore.treePredictResults &&
                id < treeStore.treePredictResults.series.length
            ) {
                return {
                    ...predictResults.value.series[id],
                    pred: treeStore.treePredictResults.series[id].pred,
                }
            }
            return {
                ...predictResults.value.series[id],
            }
        })
        // const temp = idList.map
        // return predictResults.value.series.filter((item) => {
        //     return stringNameList.includes(item.string_name)
        // })
    })

    const showStringInfos = computed(() => {
        var temp: StringInfo[] = [...stringInfos.value]

        if (sortParam.value !== undefined && sortParam.value !== '') {
            if (sortOrder.value === 'asc') {
                temp?.sort((a, b) => {
                    if (a[sortParam.value] < b[sortParam.value]) return 1
                    else return -1
                })
            } else {
                temp?.sort((a, b) => {
                    if (a[sortParam.value] > b[sortParam.value]) return 1
                    else return -1
                })
            }
        }

        if (filterValue.value && filterValue.value !== undefined) {
            const filterStr = filterValue.value.join('-')
            temp = temp
                .filter((item: StringInfo) =>
                    item.string_name.startsWith(filterStr)
                )
                .slice(0, showNum.value)
        } else {
            temp = temp.slice(0, showNum.value)
        }
        return temp
    })

    const param_max_dict: {
        [key: string]: number
    } = reactive({
        dispersion: 0,
        power_sum: 0,
        power_mean: 0,
        day_cnt: 0,
        mse: 0,
    })

    function handleScroll() {
        addShowNum()
        scrollDisabled.value = true
        setTimeout(() => {
            scrollDisabled.value = false
        }, 5000)
        console.log('handleScroll')
    }

    function getRandomColor() {
        let randomIdx = Math.floor(Math.random() * colorMap.length)
        while (
            colorList.value.includes(colorMap[randomIdx]) &&
            colorList.value.length < colorMap.length
        ) {
            randomIdx = Math.floor(Math.random() * colorMap.length)
        }
        colorList.value.push(colorMap[randomIdx])
        return colorMap[randomIdx]
    }

    function switchSelect(dataset: string, string_name: string) {
        if (string_name in selectedString.value) {
            const newSelectedString = { ...selectedString.value }
            delete newSelectedString[string_name]
            selectedString.value = newSelectedString
        } else {
            axios
                .get('/api/string_select/' + dataset + '/' + string_name)
                // .get('/api/string_select/' + dataset + '/' + string_name)
                .then((resp) => {
                    const stringCV = resp.data as StringCV
                    // 生成一种颜色
                    const stringCVC = {
                        ...stringCV,
                        color: getRandomColor(),
                    }
                    const newSelectedString = { ...selectedString.value }
                    newSelectedString[string_name] = stringCVC
                    selectedString.value = newSelectedString
                })
        }
    }

    function clearSelectedString() {
        selectedString.value = {}
    }
    function updateStringLables(data: StringPoint[]) {
        // if (stringInfos.value === undefined || stringInfos.value.length === 0) {
        //     return
        // }
        setTimeout(() => {
            data.map((item, idx) => {
                stringInfos.value[idx].label = item.label
            })
        }, 1000)
    }

    function updateStringInfos(data: StringInfo[]) {
        stringInfos.value = data

        data.forEach((item) => {
            Object.keys(param_max_dict).forEach((key) => {
                param_max_dict[key] = Math.max(
                    item[key] as number,
                    param_max_dict[key]
                )
            })
        })

        Object.keys(param_max_dict).map((key: string) => {
            param_max_dict[key] = Math.ceil(param_max_dict[key])
        })

        // console.log(param_max_dict)

        stringNames.value = data.map((item) => item.string_name)
    }

    function updatePredictResults(data: PredictResults) {
        data.series.forEach((item, idx) => {
            item.label = stringInfos.value[idx].label
            item.mse = stringInfos.value[idx].mse
        })
        predictResults.value = data
    }

    function orderSwitch() {
        if (sortOrder.value === 'asc') {
            sortOrder.value = 'desc'
        } else {
            sortOrder.value = 'asc'
        }
        showNum.value = step
    }

    function resetShowNum() {
        showNum.value = step
    }

    function addShowNum() {
        showNum.value += step
    }

    const updateMapViewData = (data: any) => {
        mapViewData.geo_map_data = data.geo_map_data
        mapViewData.scatter_data = data.scatter_data
    }
    return {
        stringInfos,
        stringNames,
        predictResults,
        sortParam,
        sortOrder,
        filterValue,
        showNum,
        showStringInfos,
        showSeries,
        selectedString,
        scrollDisabled,
        param_max_dict,
        anomalyThreshold,
        anomalyStep,
        mapViewData,
        clearSelectedString,
        updateStringLables,
        updateStringInfos,
        updatePredictResults,
        orderSwitch,
        addShowNum,
        resetShowNum,
        switchSelect,
        handleScroll,
        updateMapViewData,
    }
})
