import librosa
import numpy as np
import pandas as pd
import glob
from scipy.signal import lfilter
from scipy.signal.windows import hamming
from disvoice.phonation.phonation import Phonation
import os

os.environ['KALDI_ROOT'] = '/root/kaldi-master'

# 定义提取MFCC特征的函数
def extract_mfcc_features(audio_path, n_mfcc=13):
    y, sr = librosa.load(audio_path)
    mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
    mfccs_mean = np.mean(mfccs, axis=1)
    mfccs_std = np.std(mfccs, axis=1)
    features = {}
    for i, (mean, std) in enumerate(zip(mfccs_mean, mfccs_std), 1):
        features[f'mfcc_{i}_mean'] = mean
        features[f'mfcc_{i}_std'] = std
    return features

# 提取共振峰特征的函数
def extract_formants(audio_path):
    y, sr = librosa.load(audio_path)
    # 预加重
    y = lfilter([1., -0.63], 1, y)
    # 分帧
    frames = librosa.util.frame(y, frame_length=int(sr*0.025), hop_length=int(sr*0.01))
    # 加窗
    windowed = frames * hamming(int(sr*0.025), sym=False)[:, None]
    # LPC分析
    n_formant = 4
    formants_mean = np.zeros(n_formant)
    formants_std = np.zeros(n_formant)
    for frame in windowed.T:
        a_lpc = librosa.lpc(frame, order=8)#对每帧信号执行线性预测编码（LPC），以估计声道的谐振特性。
        roots = np.roots(a_lpc)#计算LPC多项式的根。这些根代表了系统的谐振点，与共振峰频率相关。
        roots = [r for r in roots if np.imag(r) >= 0]#筛选出具有正虚部的根。因为在物理上，只有这些根代表了实际的共振频率。
        angz = np.arctan2(np.imag(roots), np.real(roots))#计算每个根的相位角度，这些角度与共振峰频率成正比。
        frqs = sorted(angz * (sr / (2 * np.pi)))#将角度转换为频率（单位：Hz），并排序。
        #选取前4个共振峰，用累加帮助后续计算平均值和标准差
        formants = frqs[:n_formant]
        formants_mean += np.array(formants)
        formants_std += np.array(formants)**2
    formants_mean /= windowed.shape[1]
    formants_std = np.sqrt(formants_std/windowed.shape[1] - formants_mean**2)
    features = {}
    for i, (mean, std) in enumerate(zip(formants_mean, formants_std), 1):
        features[f'formant_{i}_mean'] = mean
        features[f'formant_{i}_std'] = std
    return features

phonationf = Phonation()
# 定义用DisVoice提取Phonation特征的函数
def extract_phonation_features(audio_path):
    features_df = phonationf.extract_features_file(audio_path, static=True, plots=False, fmt="dataframe")
    # 将DataFrame转换为简化的字典格式
    simplified_features = {}
    for col in features_df.columns:
        # 直接获取每列的第一个值，并去除索引和数据类型的部分
        simplified_features[col] = features_df[col].iloc[0]
    return simplified_features

# 定义来提取并合并多种音频特征的函数
def extract_and_merge_features(audio_files, feature_extractors):
    features_df = pd.DataFrame()
    for file in audio_files:
        features = {}
        for extractor in feature_extractors:#使用给定的每种特征提取函数分别对数据进行相应特征提取
            features.update(extractor(file))
        features_df = pd.concat([features_df, pd.DataFrame([features])], ignore_index=True)
    return features_df

# 定义要提取特征的音频文件夹
audio_folders = {
    "SD_PD": "dataset/SpontaneousDialogue/PD/*.wav",
    "SD_HC": "dataset/SpontaneousDialogue/HC/*.wav",
    "RT_PD": "dataset/ReadText/PD/*.wav",
    "RT_HC": "dataset/ReadText/HC/*.wav"
}

if __name__ == '__main__':
    result_folder = 'result'
    os.environ['KALDI_ROOT'] = '/root/kaldi-master'
    for label, path in audio_folders.items():
        audio_files = glob.glob(path)
        features_df = extract_and_merge_features(audio_files,
                                                 [extract_mfcc_features, extract_formants, extract_phonation_features])
        features_df.to_csv(f'{label}_features.csv', index=False)