import pandas as pd
from sklearn.tree import DecisionTreeRegressor
from sklearn.tree._tree import TREE_LEAF         
from sklearn.tree._tree import TREE_UNDEFINED 
from collections import deque

class TreeStructure:
    '''
        Description:
        This class will calculate and store the basic attributes of the Tree:
        1) Number of nodes appearing in the classified Tree
        2) The right children of the tree
        3) The left children of the tree
        4) The thresholds (split points) of each node
        5) The ids of the features that were used for splitting in each node
        6) The ids of the nodes that are parents in the tree
        7) The ids of the nodes that are leaves in the tree
        8) The links (relationship: which are the children of each parent node) of the tree
    
        
        
        Inputs: 
        X:                             The Input data that were used to classify the tree
        Y:                             The output data (classes)
       
                    
    '''
    def __init__(self, X, Y, criterion='squared_error', splitter='best',min_samples_leaf=1, min_samples_split=2,min_weight_fraction_leaf=0,
    min_impurity_decrease = 0,
    min_impurity_split=0,
    max_features=None,
    random_state=None,
    max_leaf_nodes=None,
    max_depth=None):                    
        
        self.X=X                               #Pandas data frame object which contains the input data used to classify the tree (most of the times it will be the
                                               #training dataset)
        self.Y=Y                               #Pandas Dataframe (series) containing the whole output dataset
        self.feature_names=self.X.columns.values  #A list containing the names of the various features as strings
        self.criterion = criterion
        self.splitter = splitter
        self.min_samples_leaf = min_samples_leaf
        self.min_samples_split = min_samples_split
        self.min_weight_fraction_leaf = min_weight_fraction_leaf
        self.min_impurity_decrease = min_impurity_decrease
        self.min_impurity_split = min_impurity_split
        self.max_features = max_features
        self.random_state = random_state
        self.max_leaf_nodes = max_leaf_nodes
        self.max_depth = max_depth

    def generate_Tree(self, DTree, X, Y, offset=0):
        # BFS, 计算每个节点的data，存储到dict中
        node_X_index = [None for _ in range(0, DTree.tree_.node_count)]
        node_rules = [None for _ in range(0, DTree.tree_.node_count)] 

        feature_label=["Leaf_Node" if DTree.tree_.feature[i] < 0 else DTree.feature_names_in_ [DTree.tree_.feature[i]] for i in range(DTree.tree_.node_count)]
        parents = [index for index, value in enumerate(DTree.tree_.feature != TREE_UNDEFINED) if value]
        nodeQueue = deque([0])
        node_X_index[0] = X.index
        node_rules[0] = ""

        test_string_left= '{} <= {}'
        test_string_right= '{} > {}'
        
        # No Leaf
        if DTree.tree_.feature[0] != TREE_UNDEFINED:
            while nodeQueue:
                for _ in range(len(nodeQueue)):
                    curIdx = nodeQueue.popleft()
                    if not isinstance(node_X_index[curIdx], pd.Index):
                        print("error")
                        break
                    
                    lIdx = DTree.tree_.children_left[curIdx]
                    rIdx = DTree.tree_.children_right[curIdx]

                    feature_idx = DTree.tree_.feature[curIdx]
                    feature_name = DTree.feature_names_in_[feature_idx]
                    threshold = DTree.tree_.threshold[curIdx]

                    string_left = test_string_left.format(feature_name, threshold)
                    string_right = test_string_right.format(feature_name, threshold)

                    if curIdx != 0:
                        string_left = " and " + string_left
                        string_right = " and " + string_right

                    node_rules[lIdx] = node_rules[curIdx] + string_left
                    node_rules[rIdx] = node_rules[curIdx] + string_right
                    # DataFrame
                    temp_X_df = X.loc[node_X_index[curIdx]]
                    node_X_index[lIdx] = temp_X_df[temp_X_df[feature_name] <= threshold].index
                    node_X_index[rIdx] = temp_X_df[temp_X_df[feature_name] > threshold].index

                    if lIdx in parents:
                        nodeQueue.append(lIdx)
                    if rIdx in parents:
                        nodeQueue.append(rIdx)
       
        tree_df = pd.DataFrame({"node_idx": range(0, DTree.tree_.node_count), "feature": DTree.tree_.feature, "feature_label": feature_label, "threshold": DTree.tree_.threshold, 
                                  "impurity": DTree.tree_.impurity, "children_left":DTree.tree_.children_left, "children_right": DTree.tree_.children_right, 
                                  "node_X_index": node_X_index, "node_rules": node_rules, 
                                  "value": [DTree.tree_.value[i][0][0] for i in range(0, DTree.tree_.node_count)]})
        
        if offset != 0:
            tree_df.loc[:, 'children_left'] = tree_df['children_left'].apply(lambda x: x if x == -1 else x + offset)
            tree_df.loc[:, 'children_right'] = tree_df['children_right'].apply(lambda x: x if x == -1 else x + offset)
            tree_df.loc[:, "node_idx"]= range(offset, DTree.tree_.node_count + offset)
            
        tree_df.index = tree_df.node_idx
        
        return tree_df
    def update_tree_attributes(self):
        self.node_count = len(self.Tree)
        self.parents = [index for index, value in enumerate(self.Tree.feature != TREE_UNDEFINED) if value]
        self.leaves = [index for index, value in enumerate(self.Tree.feature  == TREE_UNDEFINED) if value]
        self.links = {}
        for idx in self.Tree.index:
            if self.Tree.loc[idx, "feature"] != TREE_UNDEFINED:
                self.links[idx] = [self.Tree.loc[idx, "children_left"], self.Tree.loc[idx, "children_right"]]
    
    def predict(self, X):
        if isinstance(X, pd.DataFrame):
            X = X.copy()
            for leaf in self.leaves:
                rule = self.Tree.loc[leaf, "node_rules"]
                x_index = X.query(rule).index
                if len(x_index) != 0:
                    X.loc[x_index, "predict"] = self.Tree.loc[leaf, "value"]
            return X['predict'].values
        else:
            raise ValueError("X need to be pamdas.DataFrame")
        
    def export_text(self):
        prefixStr = "|--- "
        self.printTree(0, prefixStr)

    def printTree(self, root, prefixStr):
        feature = self.Tree.loc[root, "feature"]
        if feature == TREE_UNDEFINED:
            print(prefixStr + " value: {:.2f}".format(self.Tree.loc[root, "value"]))
        else:
            threshold = self.Tree.loc[root, "threshold"]
            # impurity = regTree.tree_.impurity[root]
            l = self.Tree.loc[root, "children_left"]
            r = self.Tree.loc[root, "children_right"]
            l_str = "feature_{} <= {:.2f} ".format(feature, threshold)
            r_str = "feature_{} > {:.2f} ".format(feature, threshold)
            print(prefixStr + l_str)
            self.printTree(l, "|   " + prefixStr)
            print(prefixStr + r_str)
            self.printTree(r, "|   " + prefixStr)

    def get_subTreeNodes(self, root):
        subTreeIdxs = []
        # bfs
        nodeQueue = deque([root])
        while nodeQueue:
            for _ in range(len(nodeQueue)):
                curIdx = nodeQueue.popleft()
                l = self.Tree.loc[curIdx, "children_left"]
                r = self.Tree.loc[curIdx, "children_right"]

                if l != TREE_LEAF:
                    subTreeIdxs.append(l)
                if r != TREE_LEAF:
                    subTreeIdxs.append(r)

                if l in self.parents:
                    nodeQueue.append(l)
                if r in self.parents:
                    nodeQueue.append(r)
        return subTreeIdxs
    
    # 剪枝给定的以root为根的子树，root不能为0
    def prune(self, root):
        if root == 0:
            raise ValueError("Couldn't prune the DT root!")
        elif root in self.leaves:
            raise ValueError("Prune the leaf node is meaningless!")
        
        subTreeNodes = self.get_subTreeNodes(root)
        remain_df = self.Tree[~self.Tree.node_idx.isin(subTreeNodes)]
        
        # set root to leaf node
        remain_df.loc[root, "children_left"] = TREE_LEAF
        remain_df.loc[root, 'children_right'] = TREE_LEAF
        remain_df.loc[root, 'feature_label'] = "Leaf_Node"
        remain_df.loc[root, 'feature'] = TREE_UNDEFINED
        remain_df.loc[root, "threshold"] = TREE_UNDEFINED

        idx_list = list(remain_df.node_idx)
        # update node index
        remain_df.loc[:, 'children_left'] = remain_df['children_left'].apply(lambda x: x if x == -1 else idx_list.index(x))
        remain_df.loc[:, 'children_right'] = remain_df['children_right'].apply(lambda x: x if x == -1 else idx_list.index(x))
        remain_df.loc[:, "node_idx"]= range(0, len(idx_list))
        remain_df.index = remain_df["node_idx"]

        # update Tree, parents and leaves
        self.Tree = remain_df
        self.update_tree_attributes()
    
    def find_node_parents(self, nIdx):
        left_df = self.Tree[self.Tree["children_left"] == nIdx]
        right_df = self.Tree[self.Tree["children_right"] == nIdx]
        if len(left_df):
            return left_df.node_idx.iloc[0], 0
        if len(right_df):
            return right_df.node_idx.iloc[0], 1
        return -1, -1


    # 对某个节点的子树进行重训，用重训得到的子树替换root
    def retrain_node(self, root):
        # prepare data for subTree
        node_X_index = self.Tree.loc[root, "node_X_index"]
        temp_X_df = self.X.loc[node_X_index]
        temp_Y_df = self.Y.loc[node_X_index]
        # 选择的节点为根节点，直接重训既可
        if root == 0:
            temp_tree = DecisionTreeRegressor(criterion=self.criterion, splitter=self.splitter, max_depth=self.max_depth, min_samples_split=self.min_samples_split,
                                              min_samples_leaf=self.min_samples_leaf, min_weight_fraction_leaf=self.min_weight_fraction_leaf, max_features=self.max_features,
                                              random_state=self.random_state, max_leaf_nodes=self.max_leaf_nodes, min_impurity_decrease=self.min_impurity_decrease)
            temp_tree.fit(temp_X_df, temp_Y_df)
            self.Tree = self.generate_Tree(temp_tree, temp_X_df, temp_Y_df)
            self.update_tree_attributes()
            return
        

        # 选择的节点不为叶子节点的时候，需要删除子树；若为叶子节点，这部分操作只会替换节点本身
        subTreeNodes = self.get_subTreeNodes(root) 
        # get parentIdx and lrType 
        string_prefix = self.Tree.loc[root, "node_rules"]
    
        # 删除子树的所有节点
        remain_df = self.Tree[~self.Tree.node_idx.isin(subTreeNodes)]
        # temporily set children TREE_LEAF
        remain_df.loc[root, "children_left"] = TREE_LEAF
        remain_df.loc[root, 'children_right'] = TREE_LEAF
        idx_list = list(remain_df.node_idx)
        # update node index
        remain_df.loc[:, 'children_left'] = remain_df['children_left'].apply(lambda x: x if x == -1 else idx_list.index(x))
        remain_df.loc[:, 'children_right'] = remain_df['children_right'].apply(lambda x: x if x == -1 else idx_list.index(x))
        remain_df.loc[:, "node_idx"]= range(0, len(idx_list))
        remain_df.index = remain_df["node_idx"]
       
        # retrain the tree
        temp_tree = DecisionTreeRegressor(criterion=self.criterion, splitter=self.splitter, max_depth=self.max_depth, min_samples_split=self.min_samples_split,
                                              min_samples_leaf=self.min_samples_leaf, min_weight_fraction_leaf=self.min_weight_fraction_leaf, max_features=self.max_features,
                                              random_state=self.random_state, max_leaf_nodes=self.max_leaf_nodes, min_impurity_decrease=self.min_impurity_decrease)
        temp_tree.fit(temp_X_df, temp_Y_df)

        # generate tree
        tree_df = self.generate_Tree(temp_tree, temp_X_df, temp_Y_df, offset=len(remain_df))
        tree_df.loc[:, "node_rules"] = string_prefix + " and " + tree_df.loc[:, "node_rules"]
        tree_df.loc[len(remain_df), "node_rules"] = string_prefix
        # 替换root内容为新生成子树的根节点
        tree_df.loc[len(remain_df), "node_idx"] = remain_df.loc[root,"node_idx"]
        remain_df.loc[root] = tree_df.loc[len(remain_df)]
        tree_df = tree_df.drop(index=len(remain_df))
            
        remain_df = pd.concat([remain_df, tree_df])
        # update Tree, parents and leaves
        self.Tree = remain_df
        self.update_tree_attributes()

    # 修改某个节点的feature, threshold，重新生成左右子树
    def modify_and_split_node(self, root, new_feature, new_threshold):
        subTreeNodes = self.get_subTreeNodes(root)
        remain_df = self.Tree[~self.Tree.node_idx.isin(subTreeNodes)]

        # prepare data for left/right branch
        node_X_index = remain_df.loc[root, "node_X_index"]
        temp_X_df = self.X.loc[node_X_index]
        temp_Y_df = self.Y.loc[node_X_index]
        feature_name = remain_df.loc[root, "feature_label"]
        # generate left branch dataset and right branch dataset
        left_X = temp_X_df[temp_X_df[feature_name] <= new_threshold]
        left_Y = temp_Y_df[left_X.index]
        right_X = temp_X_df[temp_X_df[feature_name] > new_threshold]
        right_Y = temp_Y_df[right_X.index]

        if len(left_X) == 0 or len(right_X) == 0:
            raise ValueError("Invalid threshold, the data point of the subtree cannot be 0!")
        
        # update root new_threshold
        remain_df.loc[root, "threshold"] = new_threshold
        if new_feature != remain_df.loc[root, "feature"]:
            remain_df.loc[root, "feature"] = new_feature
            remain_df.loc[root, "feature_label"] = self.feature_names[new_feature]

        # temporily set children TREE_LEAF
        remain_df.loc[root, "children_left"] = TREE_LEAF
        remain_df.loc[root, 'children_right'] = TREE_LEAF
        

        idx_list = list(remain_df.node_idx)
        # update node index
        remain_df.loc[:, 'children_left'] = remain_df['children_left'].apply(lambda x: x if x == -1 else idx_list.index(x))
        remain_df.loc[:, 'children_right'] = remain_df['children_right'].apply(lambda x: x if x == -1 else idx_list.index(x))
        # root index不会被修改，因为删除的节点序号肯定在root后面
        remain_df.loc[:, "node_idx"]= range(0, len(idx_list))
        remain_df.index = remain_df["node_idx"]

        left_tree = DecisionTreeRegressor(criterion=self.criterion, splitter=self.splitter, max_depth=self.max_depth, min_samples_split=self.min_samples_split,
                                              min_samples_leaf=self.min_samples_leaf, min_weight_fraction_leaf=self.min_weight_fraction_leaf, max_features=self.max_features,
                                              random_state=self.random_state, max_leaf_nodes=self.max_leaf_nodes, min_impurity_decrease=self.min_impurity_decrease)
        left_tree.fit(left_X, left_Y)
        right_tree = DecisionTreeRegressor(criterion=self.criterion, splitter=self.splitter, max_depth=self.max_depth, min_samples_split=self.min_samples_split,
                                              min_samples_leaf=self.min_samples_leaf, min_weight_fraction_leaf=self.min_weight_fraction_leaf, max_features=self.max_features,
                                              random_state=self.random_state, max_leaf_nodes=self.max_leaf_nodes, min_impurity_decrease=self.min_impurity_decrease)
        right_tree.fit(right_X, right_Y)

        # add a space
        test_string_left= '{} <= {} '
        test_string_right= '{} > {} '
        string_left = test_string_left.format(feature_name, new_threshold)
        string_right = test_string_right.format(feature_name, new_threshold)

        if root != 0:
            string_left = " and " + string_left
            string_right = " and " + string_right

        # generate left tree
        left_tree_df = self.generate_Tree(left_tree, left_X, left_Y, offset=len(remain_df))
        left_tree_df.loc[:, "node_rules"] = remain_df.loc[root, "node_rules"] + string_left + " and " + left_tree_df.loc[:, "node_rules"]
        left_tree_df.loc[len(remain_df), "node_rules"] = remain_df.loc[root, "node_rules"] + string_left
        # add left tree
        remain_df.loc[root, "children_left"] = len(remain_df)
        remain_df = pd.concat([remain_df, left_tree_df])
        
        # generate right tree
        right_tree_df = self.generate_Tree(right_tree, right_X, right_Y, offset=len(remain_df))
        right_tree_df.loc[:, "node_rules"] = remain_df.loc[root, "node_rules"] + string_right + " and " +  right_tree_df.loc[:, "node_rules"]
        right_tree_df.loc[len(remain_df), "node_rules"] = remain_df.loc[root, "node_rules"] + string_right
        # add right tree
        remain_df.loc[root, "children_right"] = len(remain_df)
        remain_df = pd.concat([remain_df, right_tree_df])

        # update Tree, parents and leaves
        self.Tree = remain_df
        self.update_tree_attributes()
     
    def init_tree_default(self):
        # 初始化树
        origin_Tree = DecisionTreeRegressor(criterion=self.criterion, splitter=self.splitter, max_depth=self.max_depth, min_samples_split=self.min_samples_split,
                                              min_samples_leaf=self.min_samples_leaf, min_weight_fraction_leaf=self.min_weight_fraction_leaf, max_features=self.max_features,
                                              random_state=self.random_state, max_leaf_nodes=self.max_leaf_nodes, min_impurity_decrease=self.min_impurity_decrease)  #The Regressor tree. Object of cass sklearn.tree.DecisionTreeRegressor, sklearn.tree.fit             
        origin_Tree.fit(self.X, self.Y)
        self.origin_Tree = origin_Tree
        self.node_count = origin_Tree.tree_.node_count
        self.criterion = origin_Tree.criterion
        self.max_depth = origin_Tree.tree_.max_depth
        
        self.Tree = self.generate_Tree(origin_Tree, self.X, self.Y)
        self.update_tree_attributes()

    def init_tree_from_draft(self, tree_list):
        # BFS, 计算每个节点的data，存储到dict中
        node_X_index = [None for i in range(0, len(tree_list))]
        node_rules = [None for i in range(0, len(tree_list))] 
        node_values = [None for i in range(0, len(tree_list))]

        feature_label=["Leaf_Node" if tree_list[i]["feature"] < 0 else self.feature_names[tree_list[i]["feature"]] for i in range(len(tree_list))]
        parents = [i for i in range(len(tree_list)) if tree_list[i]["feature"] != TREE_UNDEFINED]
        leaves = [i for i in range(len(tree_list)) if tree_list[i]["feature"] == TREE_UNDEFINED]
        nodeQueue = deque([0])

        node_X_index[0] = self.X.index
        node_rules[0] = ""
        node_values[0] = self.Y.mean()

        test_string_left= '{} <= {}'
        test_string_right= '{} > {}'

        # No Leaf
        if tree_list[0]["feature"] != TREE_UNDEFINED:
            while nodeQueue:
                for _ in range(len(nodeQueue)):
                    curIdx = nodeQueue.popleft()
                    if not isinstance(node_X_index[curIdx], pd.Index):
                        print("error")
                        break
                    
                    lIdx = tree_list[curIdx]["children_left"]
                    rIdx = tree_list[curIdx]["children_right"]

                    feature_idx = tree_list[curIdx]["feature"]
                    feature_name = self.feature_names[feature_idx]
                    threshold = tree_list[curIdx]["threshold"]

                    string_left = test_string_left.format(feature_name, threshold)
                    string_right = test_string_right.format(feature_name, threshold)

                    if curIdx != 0:
                        string_left = " and " + string_left
                        string_right = " and " + string_right

                    node_rules[lIdx] = node_rules[curIdx] + string_left
                    node_rules[rIdx] = node_rules[curIdx] + string_right
                    # DataFrame
                    temp_X_df = self.X.loc[node_X_index[curIdx]]
                    temp_Y_df = self.Y.loc[node_X_index[curIdx]]
                    node_X_index[lIdx] = temp_X_df[temp_X_df[feature_name] <= threshold].index
                    node_values[lIdx] = temp_Y_df.loc[node_X_index[lIdx]].mean()
                    
                    node_X_index[rIdx] = temp_X_df[temp_X_df[feature_name] > threshold].index
                    node_values[rIdx] = temp_Y_df.loc[node_X_index[rIdx]].mean()
                    if lIdx in parents:
                        nodeQueue.append(lIdx)
                    if rIdx in parents:
                        nodeQueue.append(rIdx)

        self.Tree = pd.DataFrame({"node_idx": [x["node_idx"] for x in tree_list], "feature": [x["feature"] for x in tree_list], "feature_label": feature_label, "threshold": [x["threshold"] for x in tree_list], 
                                  "impurity": 0, "children_left": [x["children_left"] for x in tree_list], "children_right": [x["children_right"] for x in tree_list], 
                                  "node_X_index": node_X_index, "node_rules": node_rules, 
                                  "value": node_values})
        self.update_tree_attributes()

        # 扩展叶子结点
        for leafIdx in leaves:
            self.retrain_node(leafIdx)
        # 扩展所有的Leaf

        # self.node_count = origin_Tree.tree_.node_count
        # self.criterion = origin_Tree.criterion
        # self.max_depth = origin_Tree.tree_.max_depth
        