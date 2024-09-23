import os
import numpy as np
import json
import torch
import pandas as pd 
from collections import deque
from sklearn.model_selection import train_test_split
from decision_tree import TreeStructure
from sklearn.tree._tree import TREE_LEAF   
from sklearn.metrics import mean_squared_error

def generate_dataset(model_name:str):
    data_path = os.path.join('./results/{}/tree_dataset/string_sample_allwithWeather_raw.npy'.format(model_name))
    if os.path.exists(data_path):
        string_sample_all = np.load(data_path)
        X, Y = string_sample_all[:, :-1], string_sample_all[:, -1]
        X_df = pd.DataFrame(X)
        Y_df = pd.DataFrame(Y)
        X_df.columns = ["raw", "month", "day", "weekday", "hour", 'temperature', 'wind_speed', 'irradiation']
        Y_df.columns = ["real_power"] 
        # 将数据集分为训练集和测试集
        # X_train, X_test, Y_train, Y_test = train_test_split(X, Y, test_size=0.2, shuffle=True)
        # X_train_df = pd.DataFrame(X_train)
        # Y_train_df = pd.DataFrame(Y_train)
        # X_test_df = pd.DataFrame(X_test)
        # Y_test_df = pd.DataFrame(Y_test)
        # X_train_df.columns = ["raw", "month", "day", "weekday", "hour"]
        # Y_train_df.columns = ["real_power"]
        # X_test_df.columns = ["raw", "month", "day", "weekday", "hour"]
        # Y_test_df.columns = ["real_power"]

        return X_df, Y_df
        # return X_train_df,Y_train_df,X_test_df,Y_test_df
    else:
        raise ValueError('Can not found the dataset')
    
def transformTree_structure2list(tree_structure):
    tree_list = []
    for node in tree_structure['nodes']:
        if node['feature_id'] != -2:
            curNode = {
                'node_idx': node['name'],
                "feature": node['feature_id'],
                "threshold": node['threshold'],
                "children_left": node['name'] * 2 + 1,
                "children_right": node['name'] * 2 + 2,
            }
            
        else:
            curNode = {
                'node_idx': node['name'],
                "feature": node['feature_id'],
                "threshold": node['threshold'],
                "children_left": TREE_LEAF,
                "children_right": TREE_LEAF
            }
        tree_list.append(curNode)
    return tree_list
    
def init_tree(model_info, X, Y):
    X = X.loc[:, model_info.features]
    if model_info.max_depth == (None,):
        model_info.max_depth = None
    if model_info.max_features == (None,):
        model_info.max_features = None
    if model_info.max_leaf_nodes == (None,):
        model_info.max_leaf_nodes = None
    if model_info.random_state == (None,):
        model_info.random_state = None

    tree_reg = TreeStructure(X, Y, criterion=model_info.criterion, splitter=model_info.splitter,min_samples_leaf=model_info.min_samples_leaf, min_samples_split=model_info.min_samples_split,min_weight_fraction_leaf=model_info.min_weight_fraction_leaf,
    min_impurity_decrease = model_info.min_impurity_decrease,
    min_impurity_split=model_info.min_impurity_split,
    max_features=model_info.max_features,
    random_state=model_info.random_state,
    max_leaf_nodes=model_info.max_leaf_nodes,
    max_depth=model_info.max_depth)

    
    if model_info.structure == None or len(model_info.structure['links']) == 0:
        tree_reg.init_tree_default()
    else:
        tree_list = transformTree_structure2list(model_info.structure)
        tree_reg.init_tree_from_draft(tree_list)
    return tree_reg


def generate_timeseries(results_dir: str, string_power_dir: str, fast: bool):
    predict_results_dir = os.path.join(results_dir, "predict_results")
    gradient_path = os.path.join(results_dir, "gradient/all_x_grad.pt")
    pred_path = os.path.join(predict_results_dir, "pred.npy")
    true_path = os.path.join(predict_results_dir, "true.npy")
    # read data
    pred_np = np.load(pred_path)
    true_np = np.load(true_path)
    gradient_data = torch.load(gradient_path, map_location=torch.device('cpu'))
    string_df_raw = pd.read_csv(string_power_dir, index_col = 0)

    columns = string_df_raw.columns
    num_train = int(len(string_df_raw) * 0.7)
    num_test = int(len(string_df_raw) * 0.2)
    num_vali = len(string_df_raw) - num_train - num_test
    seq_len = 120
    pred_len = 24

    border1s = [0, num_train - seq_len, len(string_df_raw) - num_test - seq_len]
    border2s = [num_train, num_train + num_vali, len(string_df_raw)]

    pred_series_len = ((true_np.shape[0]) // pred_len + 1) * pred_len
    grad_series_len = ((len(gradient_data)-1)*pred_len + seq_len)

    res = {
        "pred_datetime": string_df_raw.index[border2s[1]: pred_series_len + border2s[1]].values.tolist(),
        "grad_datetime": string_df_raw.index[border2s[1] - seq_len: grad_series_len - seq_len + border2s[1]].values.tolist(),
        "series": []
    }

    if fast:
        res_len = 15
    else:
        res_len = true_np.shape[-1]

    for feature_idx in range(res_len):
        true_series = []
        pred_series = []
        gradient_df = pd.DataFrame(index=range(0, seq_len + (len(gradient_data)-1) * pred_len))
        
        for i in range(len(gradient_data)):
            temp_grad = gradient_data[i].squeeze()
            gradient_df.loc[range(pred_len*i, pred_len*i + seq_len), i] = np.abs(temp_grad[:, feature_idx])
        
        for i in range(0, true_np.shape[0], 24):
            true_series.append(true_np[i, :, feature_idx])
            pred_series.append(pred_np[i, :, feature_idx])
        
        true_series = np.concatenate(true_series)
        pred_series = np.concatenate(pred_series)
        grad_series = gradient_df.mean(axis=1).values[120:].tolist()
        
        residual = np.abs(true_series - pred_series)
        residual_mean = float(residual.mean())
        residual_var = float(residual.var())
        

        res['series'].append({
            "id": feature_idx,
            "string_name": columns[feature_idx],
            "raw": true_series.tolist(),
            "pred": pred_series.tolist(),
            "time_grad": grad_series,
            'residual': residual.tolist(),
            'residual_mean': residual_mean,
            "residual_var": residual_var,
        })

    temp = json.dumps(res)
    res = json.loads(temp)
    
    
    return res


def generate_tree_timeseries(results_dir: str, string_power_dir: str, model_info, DTree):
    # results_dir = './results/power_new_covariate_120_24/'
    # string_power_dir = './dataset/string_power_df/raw.csv'

    predict_results_dir = os.path.join(results_dir, "predict_results")
    pred_path = os.path.join(predict_results_dir, "pred.npy")
    true_path = os.path.join(predict_results_dir, "true.npy")
    # read data
    pred_np = np.load(pred_path)
    true_np = np.load(true_path)
    string_df_raw = pd.read_csv(string_power_dir, index_col = 0)

    columns = string_df_raw.columns
    num_train = int(len(string_df_raw) * 0.7)
    num_test = int(len(string_df_raw) * 0.2)
    num_vali = len(string_df_raw) - num_train - num_test
    seq_len = 120
    pred_len = 24

    border1s = [0, num_train - seq_len, len(string_df_raw) - num_test - seq_len]
    border2s = [num_train, num_train + num_vali, len(string_df_raw)]

    pred_series_len = ((true_np.shape[0]) // pred_len + 1) * pred_len

    res = {
        "pred_datetime": string_df_raw.index[border2s[1]: pred_series_len + border2s[1]].values.tolist(),
        "tree_struct": generate_tree_structure(DTree),
        "series": []
    } 
    

    df_stamp = pd.DataFrame(data={ 'date': string_df_raw.index[border2s[1]: pred_series_len + border2s[1]].values })
    df_stamp.date = pd.to_datetime(df_stamp.date)
    df_stamp['month'] = df_stamp.date.apply(lambda row: row.month, 1)
    df_stamp['day'] = df_stamp.date.apply(lambda row: row.day, 1)
    df_stamp['weekday'] = df_stamp.date.apply(lambda row: row.weekday(), 1)
    df_stamp['hour'] = df_stamp.date.apply(lambda row: row.hour, 1)

    df_weather_covaraite = pd.read_csv('./dataset/irradiation_data_hour.csv')
    df_weather_covaraite = df_weather_covaraite.drop(columns=['date'])
    df_weather_covaraite = df_weather_covaraite[border2s[1]: pred_series_len + border2s[1]]
    # Env_temperature	Wind_speed	GHI
    df_stamp['temperature'] = df_weather_covaraite['Env_temperature'].values
    df_stamp['wind_speed'] = df_weather_covaraite['Wind_speed'].values
    df_stamp['irradiation'] = df_weather_covaraite['GHI'].values
    df_stamp = df_stamp.drop(columns=['date'])


    for feature_idx in range(10): # true_np.shape[-1]
        true_series = []
        pred_series = []
        
        for i in range(0, true_np.shape[0], 24):
            true_series.append(true_np[i, :, feature_idx])
            pred_series.append(pred_np[i, :, feature_idx])
        
        true_series = np.concatenate(true_series)
        pred_series = np.concatenate(pred_series) 

        # DecisionTree predict 
        features_list = model_info.features
        data_dict = {}
        for key in features_list:
            if key == 'raw':
                data_dict[key] = pred_series
            else:
                data_dict[key] = df_stamp[key]
        X = pd.DataFrame(data_dict)
        tree_pred_series = DTree.predict(X)
        
        residual = np.abs(true_series - tree_pred_series)
        residual_mean = float(residual.mean())
        residual_var = float(residual.var())
        

        res['series'].append({
            "id": feature_idx,
            "string_name": columns[feature_idx],
            "raw": true_series.tolist(),
            "pred": tree_pred_series.tolist(),
            'mse': mean_squared_error(true_series, tree_pred_series),
            'residual': residual.tolist(),
            'residual_mean': residual_mean,
            "residual_var": residual_var,
        })

    temp = json.dumps(res)
    res = json.loads(temp)
    return res

def generate_tree_structure(DTree, tree_node_len =  7):
    # name 从0开始编号
    # node_idx，feature_id, threshold
    nodes = []
    links = []
    nodeQueue = deque([{
        "name": 0,
        "node_idx": 0
    }])
    cnt = 0
    while nodeQueue and len(nodes) < tree_node_len:
        for _ in range(len(nodeQueue)):
            tNode = nodeQueue.popleft()
            curIdx = tNode['node_idx']
            curName = tNode['name']
            curNode = {
                "name": curName,
                "node_idx": int(DTree.Tree.loc[curIdx, 'node_idx']),
                "feature_id":int( DTree.Tree.loc[curIdx, 'feature']),
                "threshold": DTree.Tree.loc[curIdx, 'threshold'],
            }
    
            nodes.append(curNode)
            if curName != 0:
                fName = (curName-1) // 2
                links.append({
                    "source": fName,
                    "target": curName,
                    'value':  len(DTree.Tree.loc[curIdx, 'node_X_index'])
                })
            nodeQueue.append({
                "name": curName * 2 + 1,
                "node_idx": DTree.Tree.loc[curIdx, 'children_left']
            })
            nodeQueue.append({
                "name": curName * 2 + 2,
                "node_idx": DTree.Tree.loc[curIdx, 'children_right']
            })

    return  {
        "nodes": nodes,
        "links": links
    }


def restruct_df2json(df):
    df_json_str = df.to_json()
    df_json = json.loads(df_json_str)
    df_json_restruct = [ {} for i in range(len(df))]

    for key in df_json.keys():
        for idx in range(len(df)):
            df_json_restruct[idx][key] = df_json[key][str(idx)]

    return df_json_restruct