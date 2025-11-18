"""
单指标样本及差值
"""
import pandas as pd

from .sample_basic import Sample, SS
from .test import mean_t_test, mean_z_test, var_f_test
from .io import ss_2_html, df_wide_2_df_stack


class SampleMean(Sample):
    """
    均值类型单指标样本
    """
    def __init__(self, n, mean, std, alpha=0.05, beta=0.20, h0='==', days=None,
                 field_type='Mean', field_name=None, group_ratio=None, group_name=None, report_title="AB实验结果"):
        super().__init__(n=n, mean=mean, std=std, alpha=alpha, beta=beta, h0=h0, days=days,
                         field_type=field_type, field_name=field_name, group_ratio=group_ratio, group_name=group_name, report_title=report_title)

    def __sub__(self, other):
        if isinstance(other, SampleMean):
            return SSMean(self, other)
        elif isinstance(other, float) or isinstance(other, int):
            return '单样本检验，待补充'
        else:
            raise Exception("Invalid object!", other)


class SSMean(SS):
    """
    两个均值型单指标样本的差
    """

    def __init__(self, s1: SampleMean, s2: SampleMean):
        super().__init__(s1, s2)

        self.dict_test_best = {}
        self.dict_test_z = {}
        self.dict_test_t_eq_var = {}
        self.dict_test_t_ne_var = {}
        self.dict_equal_var = {}

        self.data_best = None
        self.data_flat = None
        self.data_all = None

        self.html_test_best = ''
        self.html_test_z = ''
        self.html_test_t_eq_var = ''
        self.html_test_t_ne_var = ''

        self.test()

    def test(self):
        self.dict_test_z = mean_z_test(s1=self.s1, s2=self.s2, alpha=self.s1.alpha, beta=self.s1.beta, h0=self.s1.h0, delta=0.0)
        self.dict_test_t_eq_var = mean_t_test(s1=self.s1, s2=self.s2, alpha=self.s1.alpha, beta=self.s1.beta, h0=self.s1.h0, delta=0.0, equal_var=True)
        self.dict_test_t_ne_var = mean_t_test(s1=self.s1, s2=self.s2, alpha=self.s1.alpha, beta=self.s1.beta, h0=self.s1.h0, delta=0.0, equal_var=False)

        self.dict_test_z.update({'最佳检验法': ''})
        self.dict_test_t_eq_var.update({'最佳检验法': ''})
        self.dict_test_t_ne_var.update({'最佳检验法': ''})
        self.dict_equal_var = var_f_test(s1=self.s1, s2=self.s2, h0='==')
        if self.s1.n > 30 and self.s2.n > 30:
            self.dict_test_z.update({'最佳检验法': '是'})
            self.dict_test_best = self.dict_test_z
        elif self.dict_equal_var.get('p_value') < self.s1.alpha:
            # 方差不相等
            self.dict_test_t_ne_var.update({'最佳检验法': '是'})
            self.dict_test_best = self.dict_test_t_ne_var
        else:
            # 方差相等
            self.dict_test_t_eq_var.update({'最佳检验法': '是'})
            self.dict_test_best = self.dict_test_t_eq_var
        self.data_best = df_wide_2_df_stack(self.s1, self.s2, self.dict_test_best)
        self.data_flat = pd.DataFrame([self.dict_test_z, self.dict_test_t_eq_var, self.dict_test_t_ne_var])
        self.data_all = pd.concat([
            df_wide_2_df_stack(s1=self.s1, s2=self.s2, test_data=self.dict_test_z),
            df_wide_2_df_stack(s1=self.s1, s2=self.s2, test_data=self.dict_test_t_eq_var),
            df_wide_2_df_stack(s1=self.s1, s2=self.s2, test_data=self.dict_test_t_ne_var)
        ], axis=0)

        self.html_test_best = ss_2_html(s1=self.s1, s2=self.s2, test_data=self.dict_test_best)
        self.html_test_z = ss_2_html(s1=self.s1, s2=self.s2, test_data=self.dict_test_z)
        self.html_test_t_eq_var = ss_2_html(s1=self.s1, s2=self.s2, test_data=self.dict_test_t_eq_var)
        self.html_test_t_ne_var = ss_2_html(s1=self.s1, s2=self.s2, test_data=self.dict_test_t_ne_var)

    def _repr_html_(self):
        return self.html_test_best


__all__ = ['SampleMean', 'SSMean']
