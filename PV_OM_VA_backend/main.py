import torch
import os
import numpy as np
import pandas as pd
import json
import time
from fastapi import FastAPI 
from io import StringIO
from tslearn.preprocessing import TimeSeriesScalerMeanVariance, TimeSeriesResampler
from tslearn.clustering import TimeSeriesKMeans
from sklearn.cluster import DBSCAN
from tslearn.metrics import cdist_dtw
from common import MODEL_DIR, REDSULTS_DIR, DATASET_DIR, success, error, DecisionTree
from fastapi.middleware.cors import CORSMiddleware
from utils import generate_dataset, init_tree, generate_timeseries, generate_tree_timeseries, restruct_df2json
import uvicorn

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)
MODLE_NAME = None
KMEANS_TYPE = "kmeans"
DBSCAN_TYPE = "dbscan"
DT_dataset = {
    "X_train": None,
    "Y_train": None,
    'X_test': None,
    'Y_test': None
}


DTree = None
model_list = os.listdir(MODEL_DIR)
data_model_map = { "power_new_covariate_120_24": "all_filtered_string_power_df.csv", "power_new_covariate_120_24": "all_filtered_string_power_df.csv" }

@app.get("/model_list")
def get_model_list():
    return success(model_list) 


@app.get("/model_info/{model_name}")
def get_model_list(model_name: str):
    global MODLE_NAME, DT_dataset, DTree
 
    MODLE_NAME = model_name
    DT_dataset['X_train'] = None
    DT_dataset["Y_train"] = None
    DTree = None
    path = os.path.join(MODEL_DIR, model_name + "/model_info.json")
    if os.path.exists(path) == True:
        model_parameters = {}
        with open(path, 'r') as f:
            model_parameters = json.load(f)
        return success(model_parameters)

    else:
        return error("model not exists")
    
@app.get('/tree/dataset/{model_name}')
def get_tree_features_range(model_name: str):
    try:
        DT_dataset['X_train'], DT_dataset['Y_train']  = generate_dataset(model_name)
        # DT_dataset['X_train'], DT_dataset['Y_train'], DT_dataset['X_test'], DT_dataset['Y_test'] = generate_dataset(model_name)
        feature_ranges = {}
        feature_min = DT_dataset['X_train'].min()
        feature_max = DT_dataset['X_train'].max()
        for col in DT_dataset['X_train'].columns:
            feature_ranges[col] = {
                "min": float(feature_min[col]),
                "max": float(feature_max[col])
            }
        return success({
            "columns": list(DT_dataset['X_train'].columns.values),
            "ranges": feature_ranges
        })
    except Exception as err:
        return error(message='Meet Error: {}'.format(err))
    
        

@app.get("/string_info/{dataset}")
def get_string_info(dataset: str) :
    # dataset = 'string_info_df_raw_real'
    path = os.path.join(DATASET_DIR, "string_info_df/{}.csv".format(dataset))
    df = pd.read_csv(path)
    df_json_str = df.to_json()
    df_json = json.loads(df_json_str)
    df_json_restruct = []
    id_list = range(0, df.shape[0])
    for id in id_list:
        df_json_restruct.append({})
        df_json_restruct[id]['id'] = id
        for key in df_json.keys():
            df_json_restruct[id][key] = df_json[key][str(id)]

        string_name = df_json_restruct[id]['string_id']

        temp = string_name.split('-')
        df_json_restruct[id]["box_id"] =  temp[0]
        df_json_restruct[id]["invertor_id"] =  temp[1]
        df_json_restruct[id]["string_id"] =  temp[2]
        df_json_restruct[id]["string_name"] =  string_name
        
    return success(df_json_restruct)

@app.get("/feature_importance/{model_name}")
def get_feature_importance(model_name: str):
    path = os.path.join(REDSULTS_DIR, "{}/gradient/feature_importance.pt".format(model_name))
 
    if os.path.exists(path):
        feature_importance = torch.load(path, map_location=torch.device('cpu'))
        if type(feature_importance) != np.ndarray:
            feature_importance = list(np.float64(feature_importance.numpy()))
        else:
            feature_importance = list(np.float64(feature_importance))
        return success(feature_importance)
    else: 
        return error(message="Path does not exist")
    

@app.get("/time_series/{model_name}/{dataset}")
def get_time_series(model_name: str, dataset: str):
    results_dir = os.path.join(REDSULTS_DIR, model_name)
    string_power_dir = os.path.join(DATASET_DIR, "string_power_df/{}.csv".format(dataset))

    res = generate_timeseries(results_dir, string_power_dir, False)
    
    return success(res)

@app.get("/time_series/fast/{model_name}/{dataset}")
def get_time_series_fast(model_name: str, dataset: str):
    results_dir = os.path.join(REDSULTS_DIR, model_name)
    string_power_dir = os.path.join(DATASET_DIR, "string_power_df/{}.csv".format(dataset))

    res = generate_timeseries(results_dir, string_power_dir, True)
    
    return success(res)



@app.get("/string_select/{dataset}/{string_name}")
def string_select(dataset: str, string_name: str):
    # dataset = 'raw'
    current_path =  os.path.join(DATASET_DIR, "string_current_df/{}.csv".format(dataset))
    voltage_path = os.path.join(DATASET_DIR, "string_voltage_df/{}.csv".format(dataset))

    current_data = pd.read_csv(current_path, index_col=0)
    voltage_data = pd.read_csv(voltage_path, index_col=0)

    res = {
        "datetime": current_data.index.values.tolist(),
        "current": current_data.loc[:, string_name].values.tolist(),
        "voltage": voltage_data.loc[:, string_name].values.tolist(),
    } 

    return success(res)

@app.post("/train/decisionTree")
def train_decision_tree(model_info:DecisionTree):
    global DT_dataset, DTree
    start = time.time()
    forecast_model_name = model_info.forecast_model_name

    res = {}

    if DT_dataset['X_train'] is None:
        try:
            DT_dataset['X_train'], DT_dataset['Y_train'] = generate_dataset(forecast_model_name)
            # DT_dataset['X_train'], DT_dataset['Y_train'] , DT_dataset['X_test'], DT_dataset['Y_test'] = generate_dataset(model_name)
        except Exception as err:
            return error(message='Meet Error: {}'.format(err))
        
    
    DTree = init_tree(model_info, DT_dataset["X_train"], DT_dataset['Y_train'])

    print("cost time:", time.time() - start, flush=True)

    # generate_tree_timeseries
    results_dir = os.path.join(REDSULTS_DIR, model_info.forecast_model_name)
    string_power_dir = os.path.join(DATASET_DIR, "string_power_df/{}.csv".format(model_info.forecast_dataset))
    
    res = generate_tree_timeseries(results_dir, string_power_dir, model_info, DTree)
    
    return success(res)
    

@app.get("/geo/{dataset}")
def get_geo_data(dataset: str):
    string_geo_path = os.path.join(DATASET_DIR, "geo/{}/filtered_geo_with_kmeans_dtw_label.json".format(dataset))

    if os.path.exists(string_geo_path) == True:
        string_geo_json = {}
        with open(string_geo_path, 'r') as f:
            string_geo_json = json.load(f)
        return success(string_geo_json)

    else:
        return error("string geo data not exists")
    
@app.get("/cluster/{dataset}")
def get_cluster_data(dataset: str):
    cluster_path = os.path.join(DATASET_DIR, "cluster/{}/tsne_power_string_with_label.csv".format(dataset))
    
    df = pd.read_csv(cluster_path)
    df_json_str = df.to_json()
    df_json = json.loads(df_json_str)
    df_json_restruct = [ {} for i in range(len(df))]

    for key in df_json.keys():
        for idx in range(len(df)):
            df_json_restruct[idx][key] = df_json[key][str(idx)]
    
    return success(df_json_restruct)
   
@app.get("/map/{dataset}/{cluster_type}/{n_clusters}")
def get_map_data(dataset: str, cluster_type=str, n_clusters=str):
    n_clusters = int(n_clusters)
    raw_cluster_path = os.path.join(DATASET_DIR, "cluster/{}/tsne_power_string_with_label.csv".format(dataset))
    df = pd.read_csv(raw_cluster_path)

    string_geo_path = os.path.join(DATASET_DIR, "geo/{}/filtered_geo_with_kmeans_dtw_label.json".format(dataset))

    string_geo_json = {}
    with open(string_geo_path, 'r') as f:
        string_geo_json = json.load(f)
    # default file: kmeans_6
    res_path = os.path.join(DATASET_DIR, "cluster/{}/scatter_map_data_{}_{}.json".format(dataset, cluster_type, n_clusters))   
    if os.path.exists(res_path):
        data = {}
        with open(res_path, 'r') as file:
            data = json.load(file)
            return success(data)
    if cluster_type != 'default':
        power_data_path = os.path.join(DATASET_DIR, "string_power_df/{}.csv".format(dataset))
        power_df = pd.read_csv(power_data_path, index_col = 0)
        power_df = power_df.T
        scaler = TimeSeriesScalerMeanVariance()
        data_scaled = scaler.fit_transform(power_df)
        tsResampler = TimeSeriesResampler(sz=100)
        X = tsResampler.fit_transform(data_scaled)
        dtw_dists_path = os.path.join(DATASET_DIR, "string_power_df/dtw_dist/{}.csv".format(dataset))
        if os.path.exists(dtw_dists_path):
            dtw_dists = pd.read_csv(dtw_dists_path, index_col = 0)
            dtw_dists = dtw_dists.values
        else:
            dtw_dists = cdist_dtw(X)
            dtw_dists_df = pd.DataFrame(dtw_dists)
            dtw_dists_df.to_csv(dtw_dists_path)

        cluster_type = KMEANS_TYPE
        metric = 'dtw'
        if cluster_type == KMEANS_TYPE:
            cluster_model = TimeSeriesKMeans(n_clusters=n_clusters, random_state=10, n_init=10, verbose=False, metric=metric)
            labels = cluster_model.fit_predict(X)
        elif cluster_type == DBSCAN_TYPE:
            cluster_model = DBSCAN(n_clusters=n_clusters, random_state=10, metric="precomputed")
            labels = cluster_model.fit_predict(dtw_dists)
        df.loc[:, 'label'] = labels

        label_df = pd.DataFrame(index= df['string_name'])
        label_df['label'] = labels
        label_json = json.loads(label_df['label'].to_json())

        for i in range(len(string_geo_json['features'])):
            string_name = string_geo_json['features'][i]['properties']['string_name']
            string_geo_json['features'][i]['properties']['label'] = label_json[string_name]

    df_json_restruct = restruct_df2json(df)
    data = {
        "scatter_data": df_json_restruct,
        "geo_map_data": string_geo_json
    }
    with open(res_path, 'w') as file:
        json.dump(data, file)
    return success(data)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)