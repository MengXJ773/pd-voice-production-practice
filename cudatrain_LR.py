from utils_training import train_and_evaluate_simple_model
from cuml.linear_model import LogisticRegression
from utils_data_preprocessing import create_file_name, load_and_split_data, remove_highly_correlated_features, standardize_features, convert_to_numpy

# 创建文件名
file_name_without_extension = create_file_name(file_path=__file__)

# 读取数据并分割为训练集和测试集
X_train, X_test, Y_train, Y_test = load_and_split_data('data.csv')

# 移除高度相关的特征
X_train, X_test = remove_highly_correlated_features(X_train, X_test)

# 特征标准化
X_train, X_test = standardize_features(X_train, X_test)

# 将数据从cudf或cupy转换为numpy数组
X_train_np, X_test_np, Y_train_np, Y_test_np = convert_to_numpy(X_train, X_test, Y_train, Y_test)


if __name__ == '__main__':
    model = LogisticRegression(fit_intercept=True, normalize=False)

    train_and_evaluate_simple_model(model, X_train_np, Y_train_np, X_test_np, Y_test_np, file_name_without_extension)