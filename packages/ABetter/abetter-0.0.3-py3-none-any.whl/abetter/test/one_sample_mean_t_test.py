"""
t检验：单样本均值t检验
"""

from scipy.stats import t as tf
import numpy as np
from abetter.io.format import significance_type


# 单样本均值的t检验
def mean_t_test_one(n: int, mean: float, std: float,
                    mean0: float, h0: str = '==', alpha: float = 0.05, beta: float = 0.20) -> dict:
    """
    单样本均值的t检验
    :param n:
    :param mean:
    :param std:
    :param mean0:
    :param h0:
    :param alpha:
    :param beta:
    :return:
    """
    # 自由度
    df = n - 1
    # 上分位点
    t_upp_2tail_alpha = tf.isf(alpha / 2, df=df)
    t_upp_1tail_alpha = tf.isf(alpha, df=df)
    t_upp_1tail_beta = tf.isf(beta, df=df)
    # 统计量
    sem = std / np.sqrt(n)
    diff_mean = mean - mean0
    t = diff_mean / sem
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
    ci_diff_mean = list(mean + np.array([-1, 1]) * ci_diff_mean_radius)
    # MDE
    mde_mean = (t_upp_2tail_alpha + t_upp_1tail_beta) * sem
    # effect_size
    effect_size = abs(mean) / std
    return {
        'method': 't_test',
        'method_name': '[单样本][t检验]',
        'field_type': '均值型',
        'statistic': t,
        'p_value': p_value,
        'significance': significance_type(p_value),

        'diff': diff_mean,                       # 均值的增量 = mean - mean0
        'incr_mean': diff_mean,                  # 均值的增量 = mean1 - mean0
        'incr_group1': diff_mean * n,            # 组1的增量 = (mean1 - mean0) * n
        'mde': mde_mean,                         # 均值增量MDE
        'ci': ci_diff_mean,                      # 均值增量的置信区间（双尾α）
        'ci_radius': ci_diff_mean_radius,        # 均值增量的置信区间半径（双尾α）
        'effect_size': effect_size,              # 效应量（Cohen's d）

        'std': std,                              # 池化标准差（两标准差的加权平均值）
        'sem': sem,                              # 均值的标准误

        'n': n,
        'mean': mean,
        'mean0': mean0,

        'test': f'{mean:.4f} {h0} {mean0:.4f}',
        'h0': h0,
        'alpha': alpha,
        'beta': beta
    }
