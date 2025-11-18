"""
单指标样本及差值
"""
import pandas as pd

from .sample_basic import Sample, SS
from .test import prop_z_test, prop_fisher_test
from .io import ss_2_html, df_wide_2_df_stack


class SampleProp(Sample):
    """
    均值类型单指标样本
    """

    def __init__(self, n, k, alpha=0.05, beta=0.20, h0='==', days=None,
                 field_type='Prop', field_name=None, group_ratio=None, group_name=None, report_title="AB实验结果"):
        super().__init__(n=n, k=k, alpha=alpha, beta=beta, h0=h0, days=days,
                         field_type=field_type, field_name=field_name, group_ratio=group_ratio, group_name=group_name, report_title=report_title)
        self.n = n
        self.k = k
        self.mean = k / n

    def __sub__(self, other):
        if isinstance(other, SampleProp):
            return SSProp(self, other)
        elif isinstance(other, float):
            return '单样本检验，待补充'
        else:
            raise Exception("Invalid object!", other)


class SSProp(SS):
    """
    两个比率型指标样本的差
    """

    def __init__(self, s1: SampleProp, s2: SampleProp):
        super().__init__(s1, s2)
        self.dict_test_z = {}
        self.dict_test_fisher = {}
        self.dict_test_best = {}
        self.data_best = None
        self.data_flat = None
        self.data_all = None
        self.html_test_z = ''
        self.html_test_fisher = ''
        self.html_test_best = ''
        self.test()

    def test(self):
        self.dict_test_z = prop_z_test(s1=self.s1, s2=self.s2, alpha=self.s1.alpha, beta=self.s1.beta, h0=self.s1.h0, delta=0.0)
        self.dict_test_fisher = prop_fisher_test(s1=self.s1, s2=self.s2, alpha=self.s1.alpha, beta=self.s1.beta, h0=self.s1.h0, delta=0.0)

        if self.s1.k >= 10 and self.s1.n - self.s1.k >= 10 and self.s2.k >= 10 and self.s2.n - self.s2.k >= 10:
            self.dict_test_z.update({'最佳检验法': '是'})
            self.dict_test_fisher.update({'最佳检验法': '否'})
            self.dict_test_best = self.dict_test_z
            self.data_best = df_wide_2_df_stack(self.s1, self.s2, self.dict_test_z)
        else:
            self.dict_test_z.update({'最佳检验法': '不满足检验条件'})
            self.dict_test_fisher.update({'最佳检验法': '是'})
            self.dict_test_best = self.dict_test_fisher
            self.data_best = df_wide_2_df_stack(self.s1, self.s2, self.dict_test_fisher)
        self.data_flat = pd.DataFrame([self.dict_test_z, self.dict_test_fisher])
        self.data_all = pd.concat([
            df_wide_2_df_stack(s1=self.s1, s2=self.s2, test_data=self.dict_test_z),
            df_wide_2_df_stack(s1=self.s1, s2=self.s2, test_data=self.dict_test_fisher)
        ], axis=0)
        self.html_test_z = ss_2_html(s1=self.s1, s2=self.s2, test_data=self.dict_test_z)
        self.html_test_fisher = ss_2_html(s1=self.s1, s2=self.s2, test_data=self.dict_test_fisher)
        self.html_test_best = ss_2_html(s1=self.s1, s2=self.s2, test_data=self.dict_test_best)

    def _repr_html_(self):
        return self.html_test_best


__all__ = ['SampleProp', 'SSProp']
