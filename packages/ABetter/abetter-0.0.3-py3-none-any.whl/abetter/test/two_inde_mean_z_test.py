"""
z检验：两独立样本均值之差Z检验
"""

from scipy.stats import norm
import numpy as np
from abetter.io.format import significance_type


# 两独立样本均值之差的z检验
def mean_z_test_two_ind(n1: int, mean1: float, std1: float,
                        n2: int, mean2: float, std2: float,
                        delta: float = 0.0,
                        h0: str = '==', alpha: float = 0.05, beta: float = 0.20) -> dict:
    """
    独立样本均值z检验
    H0: mean1 - mean2 - delta 与 0 的关系（==, <=, >=）
    :param n1: 左侧样本量
    :param mean1: 左侧样本均值
    :param std1: 左侧样本标准差
    :param n2: 右侧样本量
    :param mean2: 右侧样本均值
    :param std2: 右侧样本标准差
    :param delta: 原假设中两均值的差值δ
    :param h0: 原假设中的关系：μ1 - μ2 == δ, μ1 - μ2 <= δ, μ1 - μ2 >= δ
    :param alpha: α，第Ⅰ类错误概率（= 1 - 置信水平）
    :param beta: β，第Ⅱ类错误概率（= 1 - 功效）
    :return: Z检验结果（dict）
    """
    # 上分位点
    z_upp_2tail_alpha = norm.isf(alpha / 2)
    z_upp_1tail_alpha = norm.isf(alpha)
    z_upp_1tail_beta = norm.isf(beta)
    # SEM 样本均值的标准误
    sem = np.sqrt(std1 ** 2 / n1 + std2 ** 2 / n2)
    # 合并标准差
    std = np.sqrt(((n1 - 1) * std1 ** 2 + (n2 - 1) * std2 ** 2) / (n1 - 1 + n2 - 1))
    # 均值差
    diff_mean = mean1 - mean2
    # z 统计量
    z = (diff_mean - delta) / sem
    # P值（z落在拒绝域的概率）
    if h0 in ('=', '=='):
        p_value = norm.sf(abs(z)) * 2
    elif h0 in ('<', '<='):
        p_value = norm.sf(z)
    elif h0 in ('>', '>='):
        p_value = norm.cdf(z)
    else:
        p_value = 'error'
    # 置信区间半径
    ci_diff_mean_radius = z_upp_2tail_alpha * sem
    ci_diff_mean = list(diff_mean + np.array([-1, 1]) * ci_diff_mean_radius)
    # MDE
    mde_mean = (z_upp_2tail_alpha + z_upp_1tail_beta) * sem
    # effect_size
    effect_size = abs(diff_mean) / std
    return {
        'method': 'mean_z_test',
        'method_name': '[独立样本][z检验]',
        'field_type': '均值型',
        'statistic': z,
        'p_value': p_value,
        'significance': significance_type(p_value),

        'diff': diff_mean,  # 均值的增量 = mean1 - mean2
        'incr_mean': diff_mean,  # 均值的增量 = mean1 - mean2
        'incr_group1': diff_mean * n1,           # 组1的增量 = (mean1 - mean2) * n1
        'incr_group2': diff_mean * n2,           # 组2的增量 = (mean1 - mean2) * n2，如果组2也做干预的话
        'mde': mde_mean,  # 均值增量MDE
        'ci': ci_diff_mean,  # 均值增量的置信区间（双尾α）
        'ci_radius': ci_diff_mean_radius,  # 均值增量的置信区间半径（双尾α）
        'effect_size': effect_size,  # 效应量（Cohen's d）

        'std': std,  # 池化标准差（两标准差的加权平均值）
        'sem': sem,  # 均值的标准误

        'n1': n1,
        'n2': n2,
        'mean1': mean1,
        'mean2': mean2,
        'std1': std1,
        'std2': std2,

        'test': f'({mean1:.4f}) - ({mean2:.4f}) {h0} {delta:.4f}',
        'h0': h0,
        'alpha': alpha,
        'beta': beta
    }
