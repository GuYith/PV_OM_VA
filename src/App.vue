<script setup lang="ts">
import MapView from '@/components/MapView.vue'
import ConfigView from '@/components/DataView.vue'
import TreeView from '@/components/TreeView.vue'
import DetailView from '@/components/DetailView.vue'
import CompareView from '@/components/CompareView.vue'
import Header from '@/components/Header.vue'
// import { TableInfo } from './common'

// const table_info = reactive<TableInfo>({
//     table_name: '',
//     rows_cnt: 0,
//     cols_cnt: 0,
//     data: [],
//     columns: [],
// })
// const handleUploadDataset = (data: TableInfo) => {
//     table_info.table_name = data.table_name
//     table_info.rows_cnt = data.rows_cnt
//     table_info.cols_cnt = data.cols_cnt
//     table_info.data = data.data // [data.data[0], data.data[1], data.data[2]]
//     table_info.columns = data.columns
// }
</script>

<template>
    <div class="flex flex-col h-full w-full text-theme-dark">
        <Header></Header>
        <div id="content" class="flex-grow w-full flex p-2 bg-gray-200">
            <div class="flex-grow flex-col container w-1/5 mr-2 mb-2">
                <div
                    class="container h-3/5 box-border mb-2 bg-white border-gray-500"
                >
                    <ConfigView></ConfigView>
                </div>
                <div
                    class="container h-2/5 box-border bg-white border-gray-500"
                >
                    <MapView></MapView>
                </div>
            </div>
            <div
                class="flex-grow flex-col container w-3/5 box-border mb-2 mr-2"
            >
                <div
                    class="container h-3/5 box-border mb-2 bg-white border-gray-500"
                >
                    <DetailView></DetailView>
                </div>
                <div
                    class="container h-2/5 box-border bg-white border-gray-500"
                >
                    <CompareView></CompareView>
                </div>
            </div>
            <div class="container w-1/5 box-border bg-white border-gray-500">
                <TreeView></TreeView>
            </div>
        </div>
    </div>
</template>

<style>
body {
    /* width: 100%;
    height: 100%; */
    font-family: 'Roboto', sans-serif;
}

/* 定义滚动条轨道的样式 */
.scrollbar::-webkit-scrollbar-track {
    background-color: #f5f5f5;
}

/* 定义滚动条滑块的样式 */
.scrollbar::-webkit-scrollbar-thumb {
    background-color: #ccc;
    border-radius: 8px;
}

/* 定义滚动条的宽度 */
.scrollbar::-webkit-scrollbar {
    height: 8px;
    width: 8px;
}
</style>
