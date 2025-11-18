"""
单个样本，样本之差
"""

class Sample:
    """
    单指标样本
    """
    sid = 0

    def __init__(self, n, mean=None, std=None, k=None, alpha=0.05, beta=0.20, h0='==', days=None,
                 field_type=None, field_name=None, group_ratio=None, group_name=None, report_title="AB实验结果"):
        Sample.sid += 1
        self.id = Sample.sid
        self.field_type = field_type
        self.field_name = field_name
        self.group_ratio = group_ratio  # 组分流比例
        self.group_name = group_name
        self.report_title = report_title
        self.alpha = alpha
        self.beta = beta
        self.days = days
        self.h0 = h0
        self.n = n
        self.mean = mean
        self.std = std
        self.k = k

    def set_alpha(self, alpha):
        self.alpha = alpha

    def set_beta(self, beta):
        self.beta = beta


class SS:
    """
    指标样本的差
    """

    def __init__(self, s1: Sample, s2: Sample):
        self.s1 = s1
        self.s2 = s2
        self.data_all = None
        self.data_best = None
        self.data_flat = None

    def test(self):
        pass

    def set_alpha(self, alpha):
        self.s1.set_alpha(alpha)
        self.s2.set_alpha(alpha)
        self.test()
        return self

    def set_beta(self, beta):
        self.s1.set_beta(beta)
        self.s2.set_beta(beta)
        self.test()
        return self

    def to_clipboard(self):
        self.data_best.to_clipboard()


__all__ = ['Sample', 'SS']
