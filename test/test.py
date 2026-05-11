from joblib import load
import pandas as pd
from Get_Feature import extract_formants,extract_mfcc_features,extract_phonation_features
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from utils_data_preprocessing import load_and_split_data
from collections import Counter

def load_and_split_data(file_path, test_size=0.2, random_state=1):
    """读取数据并分割为训练集和测试集"""
    parkinson = cudf.read_csv(file_path)
    features = parkinson.columns.tolist()
    predictors = features[0:-1]

    x = parkinson[predictors]
    y = parkinson['ifPD']

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=test_size, random_state=random_state)
    return x_train, x_test, y_train, y_test

def preprocess_data(df):
    """数据预处理，移除高度相关的特征并应用特征标准化"""
    df = df.drop(columns=to_drop)  # 移除高度相关的特征
    standardized_features = scaler.transform(df)  # 应用特征标准化
    return standardized_features

def load_preprocessing_resources():
    # 加载移除的高度相关特征列表
    with open('/mnt/d/大学材料/毕设/project/results//to_drop_features.txt', 'r') as f:
        to_drop = [line.strip() for line in f.readlines()]

    # 加载StandardScaler对象
    scaler = load('/mnt/d/大学材料/毕设/project/results/standard_scaler.joblib')
    return to_drop, scaler

def integrated_prediction(preprocessed_data):
    models = [model1, model2, model3, model4, model5]
    predictions = []

    # 对每个模型进行预测并收集结果
    for model in models:
    #    if model==model2:
    #       additional_data = create_additional_data(preprocessed_data)
    #        pred = model.predict(additional_data)
    #    else:
        pred = model.predict(preprocessed_data)
        pred = pred.drop_duplicates()
        predictions.append(pred[0])

    # 计算最常见的预测结果（投票机制）
    most_common_pred, _ = Counter(predictions).most_common(1)[0]

    return most_common_pred

def create_additional_data(original_data):
    # 复制原始数据的第一行，创建额外的数据
    additional_data = pd.concat([original_data.iloc[[0]], original_data.iloc[[0]]], ignore_index=True)
    return additional_data

X_train, X_test, Y_train, Y_test = load_and_split_data('data.csv')
threshold = 0.88


to_drop, scaler = load_preprocessing_resources()
file_path = 'dataset/ReadText/PD/ID02_pd_2_0_0.wav'


if __name__ == '__main__':
    # 使用特征提取函数提取特征
    # 计算相关矩阵
    corr_matrix = X_train.to_pandas().corr().abs()
    high_corr_var = np.where(corr_matrix > threshold)

    to_drop = set()
    for i, j in zip(*high_corr_var):
        if i != j and i < j:  # 避免自身比较和重复对
            to_drop.add(corr_matrix.columns[i])

    X_train = X_train.drop(list(to_drop), axis=1)
    X_test = X_test.drop(list(to_drop), axis=1)

    # 绘制并保存热力图
    plt.figure(figsize=(12, 10))
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', cbar=True)
    plt.title('Feature Correlation Matrix')
    plt.subplots_adjust(bottom=0.2, left=0.2)
    plt.savefig('results/feature_correlation_matrix.jpg')
    plt.close()
