"""
单指标样本及差值
"""

from .test import srm
from .io import srm_2_html


class SRM:
    def __init__(self, test):
        self.test = test
        self.statistic = test.get('statistic')
        self.p_value = test.get('p_value')
        self.significance = test.get('significance')

        self.diff_size = test.get('diff_size')
        self.diff_ratio = test.get('diff_ratio')

        self.obs_sample_size = test.get('obs_sample_size')
        self.obs_sample_size_sum = test.get('obs_sample_size_sum')
        self.exp_ratio = test.get('exp_ratio')
        self.group_name_list = test.get('group_name_list')

    def _repr_html_(self):
        return srm_2_html(self.test)

# SRM检验
def srm_test(obs_sample_size: list[int], exp_ratio: list[float], group_name_list: list[str] = None) -> SRM:
    """
    SRM检验：检验每组样本量实际分布与预期是否一致
    示例：srm([20, 41, 39], [0.2, 0.4, 0.4])
    :param obs_sample_size: 每组实际观测样本量规模（整数）
    :param exp_ratio: 每组预期样本量比例（之和为100%）
    :param group_name_list: 每组名称
    :return: dict
    """
    test = srm(obs_sample_size, exp_ratio, group_name_list)
    test = SRM(test)
    return test

__all__ = ['srm_test', 'srm']
