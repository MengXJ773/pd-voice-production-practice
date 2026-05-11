import disvoice
import sys
from disvoice.phonation.phonation import Phonation
import pandas as pd

path_audio_ReadText_PD = "../dataset/ReadText/PD/"
path_audio_ReadText_HC = "../dataset/ReadText/HC/"
path_audio_SpontaneousDialogue_PD = "../dataset/SpontaneousDialogue/PD/"
path_audio_SpontaneousDialogue_HC = "../dataset/SpontaneousDialogue/HC/"
phonationf = Phonation()


if __name__ == '__main__':
    featuresl_SD_PD = phonationf.extract_features_path(path_audio_SpontaneousDialogue_PD, static=True, plots=False, fmt="csv")
    df_SD_PD = pd.DataFrame(featuresl_SD_PD)
    df_SD_PD.to_csv("SD_PD_phonation.csv", index=True)

    featuresl_SD_HC = phonationf.extract_features_path(path_audio_SpontaneousDialogue_HC, static=True, plots=False, fmt="csv")
    df_SD_HC = pd.DataFrame(featuresl_SD_HC)
    df_SD_HC.to_csv("SD_HC_phonation.csv", index=True)

    featuresl_RT_PD = phonationf.extract_features_path(path_audio_ReadText_PD, static=True, plots=False, fmt="csv")
    df_RT_PD = pd.DataFrame(featuresl_RT_PD)
    df_RT_PD.to_csv("RT_PD_phonation.csv", index=True)

    featuresl_RT_HC = phonationf.extract_features_path(path_audio_ReadText_HC, static=True, plots=False, fmt="csv")
    df_RT_HC = pd.DataFrame(featuresl_RT_HC)
    df_RT_HC.to_csv("RT_HC_phonation.csv", index=True)

