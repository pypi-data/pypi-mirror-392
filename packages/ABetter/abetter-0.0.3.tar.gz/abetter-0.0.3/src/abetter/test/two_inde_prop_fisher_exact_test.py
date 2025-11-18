"""
z检验：两独立样本比率之差Z检验
"""

from scipy.stats import fisher_exact
import numpy as np
from abetter.io.format import significance_type


# 两独立样本均值之差的z检验
def prop_fisher_exact_test_two_ind(n1: int, k1: float,
                                   n2: int, k2: float,
                                   delta: float = 0.0,
                                   h0: str = '==', alpha: float = 0.05, beta: float = 0.20) -> dict:
    """
    独立样本均值z检验
    H0: mean1 - mean2 - delta 与 0 的关系（==, <=, >=）
    :param n1: 左侧样本量
    :param k1: 左侧样本均值
    :param n2: 右侧样本量
    :param k2: 右侧样本均值
    :param delta: 原假设中两均值的差值δ
    :param h0: 原假设中的关系：μ1 - μ2 == δ, μ1 - μ2 <= δ, μ1 - μ2 >= δ
    :param alpha: α，第Ⅰ类错误概率（= 1 - 置信水平）
    :param beta: β，第Ⅱ类错误概率（= 1 - 功效）
    :return: Z检验结果（dict）
    """
    table = [[k1, n1-k1], [k2, n2-k2]]
    p, p1, p2 = (k1 + k2) / (n1 + n2), k1 / n1, k2 / n2
    # 均值差
    diff_mean = k1 / n1 - k2 / n2
    # P值（z落在拒绝域的概率）
    if h0 in ('=', '=='):
        statistic, p_value = fisher_exact(table, alternative='two-sided')
    elif h0 in ('<', '<='):
        statistic, p_value = fisher_exact(table, alternative='greater')
    elif h0 in ('>', '>='):
        statistic, p_value = fisher_exact(table, alternative='less')
    else:
        statistic, p_value = None, None

    return {
        'method': 'fisher_exact_test',
        'method_name': '[独立样本][Fisher精确检验]',
        'field_type': '比率型',
        'statistic': statistic,
        'p_value': p_value,
        'significance': significance_type(p_value),

        'diff': diff_mean,  # 均值的增量 = mean1 - mean2
        'incr_mean': diff_mean,  # 均值的增量 = mean1 - mean2
        'incr_group1': diff_mean * n1,           # 组1的增量 = (mean1 - mean2) * n1
        'incr_group2': diff_mean * n2,           # 组2的增量 = (mean1 - mean2) * n2，如果组2也做干预的话
        'mde': '后续版本补充',  # 均值增量MDE
        'ci': ('后续版本补充', '后续版本补充'),  # 均值增量的置信区间（双尾α）
        'ci_radius': '后续版本补充',  # 均值增量的置信区间半径（双尾α）
        'effect_size': '后续版本补充',  # 效应量（Cohen's d）

        'std': '',  # 池化标准差（两标准差的加权平均值）
        'sem': '',  # 均值的标准误
        'sem0': '',  # 均值的标准误（假设比率相同）
        'sem1': '',  # 均值的标准误（假设比率不同）

        'n1': n1,
        'n2': n2,
        'k1': k1,
        'k2': k2,
        'mean1': k1 / n1,
        'mean2': k2 / n2,

        'test': f'({k1/n1:.4f}) - ({k2/n2:.4f}) {h0} {delta:.4f}',
        'h0': h0,
        'alpha': alpha,
        'beta': beta
    }
