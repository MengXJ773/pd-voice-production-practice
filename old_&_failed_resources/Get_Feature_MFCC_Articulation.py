import librosa
import numpy as np
import pandas as pd
import glob
from scipy.signal import lfilter
from scipy.signal.windows import hamming
from scipy.fftpack import fft

# 提取MFCC特征的函数
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

# 指定音频文件目录
path_audio_ReadText_PD = "dataset/ReadText/PD/*.wav"
audio_files = glob.glob(path_audio_ReadText_PD)

# 创建一个空的DataFrame用于存储所有特征
features_df = pd.DataFrame()

# 遍历目录，提取每个音频文件的特征
for file in audio_files:
    mfcc_features = extract_mfcc_features(file)
    formant_features = extract_formants(file)
    features = {**mfcc_features, **formant_features}
    features_df = pd.concat([features_df, pd.DataFrame([features])], ignore_index=True)

# 如果需要，可以将提取的特征保存到CSV文件中
features_df.to_csv('features.csv', index=False)

