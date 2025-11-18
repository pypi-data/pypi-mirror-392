"""
SRM检验：检验每组样本量实际分布与预期是否一致
"""

import numpy as np
from scipy.stats import chisquare
from abetter.io.format import significance_type


# SRM检验
def srm(obs_sample_size: list[int], exp_ratio: list[float], group_name_list: list[str] = None) -> dict:
    """
    SRM检验：检验每组样本量实际分布与预期是否一致
    示例：srm([20, 41, 39], [0.2, 0.4, 0.4])
    :param obs_sample_size: 每组实际观测样本量规模（整数）
    :param exp_ratio: 每组预期样本量比例（之和为100%）
    :param group_name_list: 每组名称
    :return: dict
    """
    n = sum(obs_sample_size)
    f_obs = np.array(obs_sample_size)
    f_exp = np.array(exp_ratio) * n
    test = chisquare(f_obs=f_obs, f_exp=f_exp)

    str_obs_ratio = ', '.join([f'{s:.0f}' for s in obs_sample_size])
    str_obs_ratio = '[' + str_obs_ratio + '] / ' + f'{n:.0f}'
    str_exp_ratio = ', '.join([f'{100 * r:.1f}%' for r in exp_ratio])
    str_exp_ratio = '[' + str_exp_ratio + ']'
    return {
        'method': 'chi_t_test',
        'method_name': '[样本比例][卡方检验]',
        'field_type': '均值型',
        'statistic': test.statistic,
        'p_value': test.pvalue,
        'significance': significance_type(test.pvalue),
        'diff_size': f_obs - f_exp,  # 均值的增量 mean1 - mean2
        'diff_ratio': (f_obs - f_exp) / n,

        'test': f'{str_obs_ratio} == {str_exp_ratio}',
        'h0': '==',

        'obs_sample_size': obs_sample_size,
        'obs_sample_size_sum': n,
        'exp_ratio': exp_ratio,
        'group_name_list': list(range(1, len(obs_sample_size) + 1)) if group_name_list is None else group_name_list
    }
