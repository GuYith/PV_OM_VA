from fastapi import status
from fastapi.responses import JSONResponse, Response  
from typing import Union
from pydantic import BaseModel

class DecisionTree(BaseModel):
    forecast_model_name: str
    forecast_dataset: str
    model_name:str
    max_depth: Union[int, None] = None,
    criterion: str
    splitter: str
    min_samples_split: Union[int, float] = 2,
    min_samples_leaf: Union[int, float] = 1,
    min_weight_fraction_leaf: float = 0,
    min_impurity_decrease: float = 0,
    min_impurity_split: float = 0,
    max_features: Union[int, float, str, None] = None,
    random_state: Union[int, None]= None,
    max_leaf_nodes: Union[int, None] = None,
    features: list[str]
    structure: object
    status: float
    
 
MODEL_DIR = "./forecast_model"
REDSULTS_DIR = './results'
DATASET_DIR  = './dataset'
FORECAST_MODLE_REGEX =  "(.*)_(.*)_(.*)_ft(.*)_co(.*)_scale(.*)_sl(.*)_ll(.*)_pl(.*)_dm(.*)_nh(.*)_el(.*)_dl(.*)_df(.*)_fc(.*)_eb(.*)_dt(.*)_(.*)_(.*)_(.*)"

MODLE_PARMETER_LIST = [
    'model_name','model_type',
    'data',
    'features',
    'with_covariate',
    'scale_type',
    'seq_len',
    'label_len',
    'pred_len',
    'd_model',
    'n_heads',
    'e_layers',
    'd_layers',
    'd_ff',
    'factor',
    'embed',
    'distil',
    'des',
    'class_strategy',
    'iter',
]

def success(data: Union[list, dict, str]) -> Response:
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={
            'code': 200,
            'msg': "Success",
            'data': data,
        }
    )  
def error(data: str = None, message: str="BAD REQUEST") -> Response:
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            'code': 400,
            'msg': message,
            'data': data,
        }
    )