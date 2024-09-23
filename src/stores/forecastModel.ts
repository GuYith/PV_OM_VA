import { defineStore } from 'pinia'
import { ForecastModel, RESP_ForecastModelInfo } from '@/common'

const DefaultModel: ForecastModel = {
    model_type: '',
    model_name: '',
    dataset: '',
    freq: '',
    seq_len: 0,
    label_len: 0,
    pred_len: 0,
    d_model: 0,
    d_ff: 0,
    feature_num: 0,
}

export const useforecastModelStore = defineStore('forecast_model', () => {
    const forecast_model: ForecastModel = reactive(DefaultModel)
    const mean_mse = ref(100)
    const mean_mse_str = ref('100')
    function update(data: ForecastModel | RESP_ForecastModelInfo) {
        Object.keys(forecast_model).map((key) => {
            forecast_model[key] = data[key]
        })
    }

    function updateForecastMSE(data: number) {
        mean_mse.value = data
        mean_mse_str.value = data.toExponential(3)
    }

    return { forecast_model, mean_mse, mean_mse_str, update, updateForecastMSE }
})
