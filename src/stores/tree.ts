import { defineStore } from 'pinia'
import {
    TreeModel,
    FormNode,
    RangesObject,
    TreeFeatureInfo,
    TreeStructure,
    TreeLink,
    TreeNode,
    Series,
} from '@/common'
import { mode } from 'd3-array'

export const useTreeStore = defineStore('treeList', () => {
    const treeList: Ref<TreeModel[]> = ref([])
    const treeFeaturesLabel: Ref<string[]> = ref([])
    const treeFeaturesRange: Ref<RangesObject> = ref({})
    const treeNodeEditorVisible = ref(false)
    const curNode: FormNode = reactive({
        name: 0,
        feature_id: -2,
        threshold: -2,
    })
    const activeTree = ref(false)

    const treePredictResults: Ref<{
        pred_datetime: any[]
        tree_struct: TreeStructure
        series: Series[]
    }> = ref({
        pred_datetime: [],
        tree_struct: {
            nodes: [] as TreeNode[],
            links: [] as TreeLink[],
        },
        series: [],
    })
    const curTreeStruct: TreeStructure = reactive({
        nodes: [{ name: 0, feature_id: -2, threshold: -2 }],
        links: [],
    })
    function updateTreeFeatureInfo(data: TreeFeatureInfo) {
        treeFeaturesLabel.value = data.columns
        treeFeaturesRange.value = data.ranges
        console.log('TreeFeatureInfo', data)
    }

    function clearTreeStruct() {
        curTreeStruct.nodes = [{ name: 0, feature_id: -2, threshold: -2 }]
        curTreeStruct.links = []
    }

    function updateTreeStruct(tree_struct: TreeStructure) {
        curTreeStruct.links = [...tree_struct.links]
        curTreeStruct.nodes = [...tree_struct.nodes]
        console.log('updateTreeStruct')
    }

    function appendTreeModel(tree: TreeModel) {
        treeList.value.push(tree)
    }

    function deleteTreeModel(model_name: string) {
        treeList.value = treeList.value.filter(
            (item) => item.model_name != model_name
        )
    }

    function openEditor(idx: number) {
        curNode.name = idx
        curNode.feature_id = curTreeStruct.nodes[idx].feature_id
        curNode.threshold = curTreeStruct.nodes[idx].threshold
        treeNodeEditorVisible.value = true
    }

    function closeEditor() {
        treeNodeEditorVisible.value = false
    }

    function confirmEditor() {
        if (curNode.feature_id === -2) {
            ElMessage.error('Please select a feature first')
            return
        }
        const lIdx = curNode.name * 2 + 1,
            rIdx = curNode.name * 2 + 2

        const { nodes, links } = curTreeStruct

        nodes[curNode.name].feature_id = curNode.feature_id
        nodes[curNode.name].threshold = curNode.threshold

        if (nodes.length <= lIdx) {
            nodes.push({
                name: lIdx,
                feature_id: -2,
                threshold: -2,
            } as TreeNode)

            nodes.push({
                name: rIdx,
                feature_id: -2,
                threshold: -2,
            })

            links.push({
                source: curNode.name,
                target: lIdx,
                value: 1,
            })

            links.push({
                source: curNode.name,
                target: rIdx,
                value: 1,
            })
        } else {
            nodes[lIdx].feature_id = -2
            nodes[lIdx].threshold = -2
            nodes[rIdx].feature_id = -2
            nodes[rIdx].threshold = -2
        }

        curTreeStruct.nodes = [...nodes]
        curTreeStruct.links = [...links]
        closeEditor()
        // console.log('confirmEditor')
    }

    function updateTreePredictResults(data: any) {
        treePredictResults.value = data
        updateTreeStruct(treePredictResults.value.tree_struct)
    }

    return {
        treeList,
        curTreeStruct,
        treeNodeEditorVisible,
        treeFeaturesRange,
        treeFeaturesLabel,
        curNode,
        treePredictResults,
        activeTree,
        updateTreePredictResults,
        clearTreeStruct,
        updateTreeStruct,
        appendTreeModel,
        deleteTreeModel,
        openEditor,
        confirmEditor,
        closeEditor,
        updateTreeFeatureInfo,
    }
})
