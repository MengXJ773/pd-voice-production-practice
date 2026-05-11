import os
from joblib import load
import pandas as pd
from pydub import AudioSegment
from Get_Feature import extract_mfcc_features, extract_formants, extract_phonation_features
from collections import Counter

def load_preprocessing_resources():
    # 加载移除的高度相关特征列表
    with open('/mnt/d/大学材料/毕设/project/results//to_drop_features.txt', 'r') as f:
        to_drop = [line.strip() for line in f.readlines()]

    # 加载StandardScaler对象
    scaler = load('/mnt/d/大学材料/毕设/project/results/standard_scaler.joblib')
    return to_drop, scaler

def allowed_file(filename):
    """检查文件扩展名是否允许处理"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def convert_to_wav(audio_path):
    """如果文件是MP3格式，将其转换为WAV格式"""
    sound = AudioSegment.from_file(audio_path)
    wav_path = audio_path.rsplit('.', 1)[0] + '.wav'
    sound.export(wav_path, format='wav')
    return wav_path

def preprocess_data(df, to_drop, scaler):
    """数据预处理，移除高度相关的特征并应用特征标准化"""
    df = df.drop(columns=to_drop)  # 移除高度相关的特征
    standardized_features = scaler.transform(df)  # 应用特征标准化
    return standardized_features

def extract_and_merge_features(audio_file, feature_extractors):
    features_df = pd.DataFrame()
    features = {}
    for extractor in feature_extractors:
        features.update(extractor(audio_file))
    features_df = pd.concat([features_df, pd.DataFrame([features])], ignore_index=True)
    return features_df

def create_additional_data(original_data):
    # 复制原始数据的第一行，创建额外的数据
    additional_data = pd.concat([original_data.iloc[[0]], original_data.iloc[[0]]], ignore_index=True)
    return additional_data

def integrated_prediction(preprocessed_data, models):
    predictions = []

    # 对每个模型进行预测并收集结果
    for model in models:
        if model == model2:
            additional_data = create_additional_data(preprocessed_data)
            pred = model.predict(additional_data)
        else:
            pred = model.predict(preprocessed_data)
        pred = pred.drop_duplicates()
        predictions.append(pred[0])

    # 计算最常见的预测结果（投票机制）
    most_common_pred, _ = Counter(predictions).most_common(1)[0]
    if most_common_pred == 1:
        prediction_result = '是'
    else:
        prediction_result = '否'
    return prediction_result

# 配置
#UPLOAD_FOLDER = 'dataset/ReadText/PD'  # 替换为音频文件夹路径
#UPLOAD_FOLDER = 'dataset/ReadText/HC'
#UPLOAD_FOLDER = 'dataset/SpontaneousDialogue/HC'
UPLOAD_FOLDER = 'dataset/SpontaneousDialogue/PD'
ALLOWED_EXTENSIONS = {'wav', 'mp3'}
feature_extractors = [extract_mfcc_features, extract_formants, extract_phonation_features]
to_drop, scaler = load_preprocessing_resources()

# 加载模型
model1 = load('/mnt/d/大学材料/毕设/project/results/best_cudatrain_LR_model.joblib')
model2 = load('/mnt/d/大学材料/毕设/project/results/best_cudatrain_MBSGD_model.joblib')
model3 = load('/mnt/d/大学材料/毕设/project/results/best_cudatrain_RF_model.joblib')
model4 = load('/mnt/d/大学材料/毕设/project/results/best_cudatrain_SVM_model.joblib')
model5 = load('/mnt/d/大学材料/毕设/project/results/best_cudatrain_KNN_model.joblib')
models = [model5]


if __name__ == '__main__':
# 遍历文件夹中的所有音频文件
    for filename in os.listdir(UPLOAD_FOLDER):
        if allowed_file(filename):
            file_path = os.path.join(UPLOAD_FOLDER, filename)

            try:
            # 如果文件是MP3格式，将其转换为WAV
                if filename.endswith('.mp3'):
                   file_path = convert_to_wav(file_path)

            # 使用特征提取函数提取特征
                features_df = extract_and_merge_features(file_path, feature_extractors)

            # 数据预处理
                preprocessed_data = preprocess_data(features_df, to_drop, scaler)

            # 使用模型进行预测
                prediction = integrated_prediction(preprocessed_data, models)

                print(f'文件: {filename}, 预测结果: {prediction}')

            finally:
                if filename.endswith('.mp3'):
                    os.remove(file_path)
