"""
F检验：两独立样本方差是否相等F检验
"""

from scipy.stats import f as ff
from abetter.io.format import significance_type


# 两独立样本均值之差的z检验
def var_f_test_two_ind(n1: int, std1: float,
                       n2: int, std2: float,
                       h0: str = '==', alpha: float = 0.05) -> dict:
    """
    独立样本均值z检验
    H0: mean1 - mean2 - delta 与 0 的关系（==, <=, >=）
    :param n1: 左侧样本量
    :param std1: 左侧样本标准差
    :param n2: 右侧样本量
    :param std2: 右侧样本标准差
    :param h0: 原假设中的关系：μ1 - μ2 == δ, μ1 - μ2 <= δ, μ1 - μ2 >= δ
    :param alpha: α，第Ⅰ类错误概率（= 1 - 置信水平）
    :return: Z检验结果（dict）
    """
    # F 统计量
    f = std1 ** 2 / std2 ** 2
    # P值（z落在拒绝域的概率）
    if h0 in ('=', '=='):
        p_value = min(ff.sf(f, n1 - 1, n2 - 1), ff.cdf(f, n1 - 1, n2 - 1)) * 2
    elif h0 in ('<', '<='):
        p_value = ff.sf(f, n1 - 1, n2 - 1)
    elif h0 in ('>', '>='):
        p_value = ff.cdf(f, n1 - 1, n2 - 1)
    else:
        p_value = 'error'
    # 置信区间
    ci_f = list(ff.interval(1 - alpha / 2, n1 - 1, n2 - 1))

    return {
        'method': 'var_f_test',
        'method_name': '[独立样本][F检验]',
        'field_type': '均值型',
        'statistic': f,
        'p_value': p_value,
        'significance': significance_type(p_value),

        'diff': std1 - std2,  # 标准差的差异 = std1 - std2
        'ci_f': ci_f,         # 标准差比例的置信区间（双尾α）

        'n1': n1,
        'n2': n2,
        'std1': std1,
        'std2': std2,

        'test': f'({std1:.4f}) / ({std2:.4f}) {h0} 1',
        'h0': h0,
        'alpha': alpha
    }
