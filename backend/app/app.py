from flask import Flask, request, jsonify
from flask_cors import CORS
from werkzeug.utils import secure_filename
from pydub import AudioSegment
import os
from joblib import load
import pandas as pd
from Get_Feature import extract_mfcc_features,extract_formants,extract_phonation_features
from collections import Counter
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy


def record_history(user_name, upload_time, prediction):
    new_history = History(user_name=user_name, upload_time =upload_time, prediction=prediction)
    db.session.add(new_history)
    db.session.commit()
    pass


def load_preprocessing_resources():
    # 加载移除的高度相关特征列表
    with open('/mnt/d/大学材料/毕设/project/results//to_drop_features.txt', 'r') as f:
        to_drop = [line.strip() for line in f.readlines()]

    # 加载StandardScaler对象
    scaler = load('/mnt/d/大学材料/毕设/project/results/standard_scaler.joblib')
    return to_drop, scaler


def allowed_file(filename):
    """检查文件扩展名是否允许上传"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def convert_to_wav(audio_path):
    """如果文件是MP3格式，将其转换为WAV格式"""
    sound = AudioSegment.from_file(audio_path)
    wav_path = audio_path.rsplit('.', 1)[0] + '.wav'
    sound.export(wav_path, format='wav')
    return wav_path


def preprocess_data(df):
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


def integrated_prediction(preprocessed_data):
    models = [model1, model2, model3, model4, model5]
    predictions = []

    # 对每个模型进行预测并收集结果
    for model in models:
        if model==model2:
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


app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///history.db'  # 配置数据库
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav', 'mp3'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
model1 = load('/mnt/d/大学材料/毕设/project/results/best_cudatrain_LR_model.joblib')
model2 = load('/mnt/d/大学材料/毕设/project/results/best_cudatrain_MBSGD_model.joblib')
model3 = load('/mnt/d/大学材料/毕设/project/results/best_cudatrain_RF_model.joblib')
model4 = load('/mnt/d/大学材料/毕设/project/results/best_cudatrain_SVM_model.joblib')
model5 = load('/mnt/d/大学材料/毕设/project/results/best_cudatrain_KNN_model.joblib')
feature_extractors = [extract_mfcc_features,extract_formants,extract_phonation_features]
to_drop, scaler = load_preprocessing_resources()


class History(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_name = db.Column(db.String(80), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    prediction = db.Column(db.String(80), nullable=False)

    def __repr__(self):
        return f'<History {self.user_name}>'

# 创建数据库表格（如果它们还不存在的话）
with app.app_context():
    db.create_all()


@app.route('/upload', methods=['POST'])
def upload_file():
    """处理上传的音频文件"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    user_name = request.form['userName']
    upload_time = datetime.now()

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        # 确保上传文件夹存在
        upload_folder = app.config['UPLOAD_FOLDER']
        if not os.path.exists(upload_folder):
            os.makedirs(upload_folder)  # 如果不存在，则创建文件夹
        file_path = os.path.join(upload_folder, filename)
        file.save(file_path)

        try:
            # 如果文件是MP3格式，将其转换为WAV
            if filename.endswith('.mp3'):
                file_path = convert_to_wav(file_path)

            # 使用特征提取函数提取特征
            features_df = extract_and_merge_features(file_path, feature_extractors)  # 假设的特征提取函数调用

            # 数据预处理
            preprocessed_data = preprocess_data(features_df)

            # 使用模型进行预测
            prediction = integrated_prediction(preprocessed_data)

            #保存到数据库
            record_history(user_name, upload_time, prediction)

            return jsonify({'message': 'File uploaded and processed successfully', 'prediction': prediction})
        finally:
            os.remove(file_path)
            if filename.endswith('.mp3'):
                os.remove(os.path.join(upload_folder, filename))

@app.route('/history', methods=['GET'])
def get_history():
    histories = History.query.all()
    history_list = []
    for h in histories:
        history_item = {
            'user_name': h.user_name,
            'upload_time': h.upload_time.strftime('%Y-%m-%d %H:%M:%S'),  # 格式化日期时间为字符串
            'prediction': h.prediction
        }
        history_list.append(history_item)

    return jsonify(history_list)

if __name__ == '__main__':
    app.run(debug=True)