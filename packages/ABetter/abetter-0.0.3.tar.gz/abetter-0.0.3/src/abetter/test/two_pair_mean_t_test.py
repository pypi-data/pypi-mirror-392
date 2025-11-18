"""
t检验：两配对样本均值之差t检验
"""

from scipy.stats import t as tf
import numpy as np
from abetter.io.format import significance_type


# 配对样本均值的t检验
def mean_t_test_two_pair(n: int, diff: float, diff_std: float,
                         diff0: float, h0: str = '==', alpha=0.05, beta=0.20) -> dict:
    # 自由度
    df = n - 1
    # 上分位点
    t_upp_2tail_alpha = tf.isf(alpha / 2, df=df)
    t_upp_1tail_alpha = tf.isf(alpha, df=df)
    t_upp_1tail_beta = tf.isf(beta, df=df)
    # 统计量
    sem = diff_std / np.sqrt(n)
    diff_mean = diff - diff0
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
    ci_diff_mean = list(diff + np.array([-1, 1]) * ci_diff_mean_radius)
    # MDE
    mde_mean = (t_upp_2tail_alpha + t_upp_1tail_beta) * sem
    # effect_size
    effect_size = abs(diff) / diff_std
    return {
        'method': 'mean_pair_t_test',
        'method_name': '[配对样本][t检验]',
        'field_type': '均值型',
        't': t,
        'p_value': p_value,
        'significance': significance_type(p_value),
        'diff': diff,                            # 均值的增量
        'incr_mean': diff,                       # 均值的增量 = mean1 - mean2
        'incr_group1': diff * n,                 # 组1的增量 = (mean1 - mean2) * n，这里n1=n2
        'incr_group2': diff * n,                 # 组1的增量 = (mean1 - mean2) * n，这里n1=n2

        'mde': mde_mean,                         # 均值增量MDE
        'ci': ci_diff_mean,                      # 均值增量的置信区间（双尾α）
        'ci_radius': ci_diff_mean_radius,        # 均值增量的置信区间半径（双尾α）
        'effect_size': effect_size,              # 效应量（Cohen's d）

        'std': diff_std,                         # 标准差（复制一份）
        'sem': sem,                              # 均值的标准误

        'n': n,
        'diff0': diff0,
        'diff_std': diff_std,

        'test': f'{diff:.4f} {h0} {diff0:.4f}',
        'h0': h0,
        'mean0': diff0,
        'alpha': alpha,
        'beta': beta
    }
