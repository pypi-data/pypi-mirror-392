"""
t检验：两独立样本均值之差t检验
"""

from scipy.stats import t as tf
import numpy as np
from abetter.io.format import significance_type


# 两独立样本均值之差的t检验
def mean_t_test_two_ind(n1: int, mean1: float, std1: float,
                        n2: int, mean2: float, std2: float,
                        delta: float = 0.0,
                        h0='==', alpha: float = 0.05, beta: float = 0.20, equal_var: bool = True) -> dict:
    """
    独立样本均值t检验
    :param n1: 左侧样本量
    :param mean1: 左侧样本均值
    :param std1: 左侧样本标准差
    :param n2: 右侧样本量
    :param mean2: 右侧样本均值
    :param std2: 右侧样本标准差
    :param delta: 原假设中两均值的差值δ=0.0 float, optional
    :param h0: 原假设中的关系：string, optional {'==','<=','>='} μ1 - μ2 == δ, μ1 - μ2 <= δ, μ1 - μ2 >= δ
    :param equal_var: 方差是否相等：bool, optional {True, False}
    :param alpha: α，第Ⅰ类错误概率（= 1 - 置信水平） float, optional
    :param beta:  β，第Ⅱ类错误概率（= 1 - 统计功效） float, optional
    :return: t检验结果（dict）
    """
    # Pooled 标准差
    std = np.sqrt(((n1 - 1) * std1 ** 2 + (n2 - 1) * std2 ** 2) / (n1 - 1 + n2 - 1))
    # SEM 样本均值的标准误
    if equal_var:
        # degrees of freedom
        df = n1 + n2 - 2
        # pooled sem
        sem = np.sqrt(1 / n1 + 1 / n2) * std
    else:
        # degrees of freedom
        df = (std1 ** 2 / n1 + std2 ** 2 / n2) ** 2 / (
                (std1 ** 2 / n1) ** 2 / (n1 - 1) + (std2 ** 2 / n2) ** 2 / (n2 - 1)
        )
        # separate sem
        sem = np.sqrt(std1 ** 2 / n1 + std2 ** 2 / n2)
    # 上分位点
    t_upp_2tail_alpha = tf.isf(alpha / 2, df=df)
    t_upp_1tail_alpha = tf.isf(alpha, df=df)
    t_upp_1tail_beta = tf.isf(beta, df=df)
    # 均值差异
    diff_mean = mean1 - mean2
    # t 统计量
    t = (diff_mean - delta) / sem
    # P值（z落在拒绝域的概率）
    if h0 in ('=', '=='):
        p_value = tf.sf(abs(t), df=df) * 2
    elif h0 in ('<', '<='):
        p_value = tf.sf(t, df=df)
    elif h0 in ('>', '>='):
        p_value = tf.cdf(t, df=df)
    else:
        p_value = '错误'
    # 置信区间半径
    ci_diff_mean_radius = t_upp_2tail_alpha * sem
    ci_diff_mean = list(diff_mean + np.array([-1, 1]) * ci_diff_mean_radius)
    # MDE
    mde_mean = (t_upp_2tail_alpha + t_upp_1tail_beta) * sem
    # effect_size
    effect_size = abs(diff_mean) / std
    return {
        'method': 'mean_t_test',
        'method_name': f'[独立样本][t检验][{'方差相等' if equal_var else '方差不等'}]',
        'field_type': '均值型',
        'statistic': t,
        'p_value': p_value,
        'significance': significance_type(p_value),
        'diff': diff_mean,                       # 均值的增量 mean1 - mean2
        'incr_mean': diff_mean,                  # 均值的增量 = mean1 - mean2
        'incr_group1': diff_mean * n1,           # 组1的增量 = (mean1 - mean2) * n1
        'incr_group2': diff_mean * n2,           # 组2的增量 = (mean1 - mean2) * n2，如果组2也做干预的话
        'mde': mde_mean,                         # 均值增量MDE
        'ci': ci_diff_mean,                      # 均值增量的置信区间（双尾α）
        'ci_radius': ci_diff_mean_radius,        # 均值增量的置信区间半径（双尾α）
        'effect_size': effect_size,              # 效应量（Cohen's d）

        'std': std,                              # 池化标准差（两标准差的加权平均值）
        'sem': sem,                              # 均值的标准误
        'df': df,                                # 自由度

        'n1': n1,
        'n2': n2,
        'mean1': mean1,
        'mean2': mean2,
        'std1': std1,
        'std2': std2,

        'test': f'({mean1:.4f}) - ({mean2:.4f}) {h0} {delta:.4f}',
        'h0': h0,
        'alpha': alpha,
        'beta': beta,
        'equal_var': equal_var
    }
