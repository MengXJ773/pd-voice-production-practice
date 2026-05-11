from sklearn.metrics import accuracy_score, roc_auc_score, roc_curve
import matplotlib.pyplot as plt
from joblib import dump
import os
from sklearn.model_selection import GridSearchCV

result_folder = 'results'

def perform_grid_search_cv(model, parameters, x_train, y_train, cv=5, verbose=3):
    """执行网格搜索和模型训练"""
    grid_search = GridSearchCV(estimator=model, param_grid=parameters, cv=cv, verbose=verbose)
    grid_search.fit(x_train, y_train)
    return grid_search.best_params_, grid_search.best_estimator_


def evaluate_and_save_results(model, x_test, y_test, file_name_without_extension, best_params=None,
                              use_decision_function=False):
    """评估模型并保存结果，根据模型类型调整评估方式"""
    y_pred = model.predict(x_test)
    acc = accuracy_score(y_test, y_pred)

    # 根据模型是否有decision_function或predict_proba选择不同的方法计算ROC AUC
    if use_decision_function:
        y_scores = model.decision_function(x_test)
    else:
        y_scores = model.predict_proba(x_test)[:, 1] if hasattr(model, 'predict_proba') else y_pred

    auc = roc_auc_score(y_test, y_scores)
    fpr, tpr, thresholds = roc_curve(y_test, y_scores)

    # 保存最佳模型
    model_file_path = os.path.join(result_folder, f'best_{file_name_without_extension}_model.joblib')
    dump(model, model_file_path)

    # 准备结果字符串
    results_str = f'准确度: {acc:.2f}\nROC AUC: {auc:.2f}'
    if best_params is not None:
        params_str = '\n'.join(f'{key}: {value}' for key, value in best_params.items())
        results_str = f'{params_str}\n{results_str}'

    # 保存结果到文本文件
    result_file_path = os.path.join(result_folder, f'best_params_{file_name_without_extension}.txt')
    with open(result_file_path, 'w', encoding='utf-8') as f:
        f.write(results_str)

    # 在控制台打印结果
    print(results_str)

    # 绘制并保存ROC曲线
    plt.figure(figsize=(8, 6))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (area = {auc:.2f})')
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver Operating Characteristic')
    plt.legend(loc="lower right")
    roc_path = os.path.join(result_folder, f'{file_name_without_extension}_roc_curve.jpg')
    plt.savefig(roc_path)
    plt.close()


def train_and_evaluate_simple_model(model, x_train, y_train, x_test, y_test, file_name_without_extension):
    """训练并评估不使用GridSearchCV的模型，如朴素贝叶斯"""
    model.fit(x_train, y_train)
    evaluate_and_save_results(model, x_test, y_test, file_name_without_extension, use_decision_function=False)
