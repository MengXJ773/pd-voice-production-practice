import os
import numpy as np
import cudf
from cuml.model_selection import train_test_split
from cuml.preprocessing import StandardScaler
import joblib


def create_file_name(file_path = __file__):
    """创建文件名"""
    base_name = os.path.basename(file_path)
    file_name_without_extension = os.path.splitext(base_name)[0]
    return file_name_without_extension


def load_and_split_data(file_path, test_size=0.2, random_state=1):
    """读取数据并分割为训练集和测试集"""
    parkinson = cudf.read_csv(file_path)
    features = parkinson.columns.tolist()
    predictors = features[0:-1]

    x = parkinson[predictors]
    y = parkinson['ifPD']

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=test_size, random_state=random_state)
    return x_train, x_test, y_train, y_test


def remove_highly_correlated_features(x_train, x_test, threshold=0.88):
    """移除高度相关的特征"""
    corr_matrix = x_train.to_pandas().corr().abs()
    high_corr_var = np.where(corr_matrix > threshold)

    to_drop = set()
    for i, j in zip(*high_corr_var):
        if i != j and i < j:  # 避免自身比较和重复对
            to_drop.add(corr_matrix.columns[i])

    x_train = x_train.drop(list(to_drop), axis=1)
    x_test = x_test.drop(list(to_drop), axis=1)
    with open('results/to_drop_features.txt', 'w') as f:
        for feature in to_drop:
            f.write(f"{feature}\n")
    return x_train, x_test


def standardize_features(x_train, x_test):
    """特征标准化"""
    sc = StandardScaler()
    x_train = sc.fit_transform(x_train)
    x_test = sc.transform(x_test)
    joblib.dump(sc, 'results/standard_scaler.joblib')
    return x_train, x_test


def convert_to_numpy(x_train, x_test, y_train, y_test):
    """将数据从cudf或cupy转换为numpy数组，并确保数据类型为float32"""
    x_train_np = x_train.to_pandas().values.astype(np.float32)
    y_train_np = y_train.to_pandas().values.astype(np.float32)
    x_test_np = x_test.to_pandas().values.astype(np.float32)
    y_test_np = y_test.to_pandas().values.astype(np.float32)
    return x_train_np, x_test_np, y_train_np, y_test_np
