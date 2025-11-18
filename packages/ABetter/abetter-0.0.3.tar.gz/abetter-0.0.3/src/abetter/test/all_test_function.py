from .two_inde_mean_z_test import mean_z_test_two_ind
from .two_inde_prop_z_test import prop_z_test_two_ind
from .two_inde_mean_t_test import mean_t_test_two_ind
from .two_inde_var_f_test import var_f_test_two_ind
from .two_inde_prop_fisher_exact_test import prop_fisher_exact_test_two_ind
from .srm_test import srm


def mean_z_test(s1, s2, alpha: float=None, beta: float=None, h0: str='==', delta: float=0.0) -> dict:
    """
    均值Z检验
    :param s1: 均值型样本
    :param s2: 均值型样本
    :param alpha: α，第Ⅰ类错误概率（= 1 - 置信水平）
    :param beta: β，第Ⅱ类错误概率（= 1 - 功效）
    :param h0: 原假设中的关系：μ1 - μ2 == δ, μ1 - μ2 <= δ, μ1 - μ2 >= δ
    :param delta: 原假设中两均值的差值δ
    :return: 均值Z检验结果（dict）
    """
    _alpha = alpha or s1.alpha
    _beta = beta or s1.beta

    return mean_z_test_two_ind(
        n1=s1.n, mean1=s1.mean, std1=s1.std,
        n2=s2.n, mean2=s2.mean, std2=s2.std,
        alpha=_alpha, beta=_beta,
        h0=h0,
        delta=delta
    )


def prop_z_test(s1, s2, alpha: float=None, beta: float=None, h0: str='==', delta: float=0.0) -> dict:
    """
    比率Z检验
    :param s1: 均值型样本
    :param s2: 均值型样本
    :param alpha: α，第Ⅰ类错误概率（= 1 - 置信水平）
    :param beta: β，第Ⅱ类错误概率（= 1 - 功效）
    :param h0: 原假设中的关系：μ1 - μ2 == δ, μ1 - μ2 <= δ, μ1 - μ2 >= δ
    :param delta: 原假设中两均值的差值δ
    :return: 比率Z检验结果（dict）
    """
    _alpha = alpha or s1.alpha
    _beta = beta or s1.beta

    return prop_z_test_two_ind(
        n1=s1.n, k1=s1.k,
        n2=s2.n, k2=s2.k,
        alpha=_alpha, beta=_beta,
        h0=h0,
        delta=delta
    )

def prop_fisher_test(s1, s2, alpha: float=None, beta: float=None, h0: str='==', delta: float=0.0) -> dict:
    """
    比率Z检验
    :param s1: 均值型样本
    :param s2: 均值型样本
    :param alpha: α，第Ⅰ类错误概率（= 1 - 置信水平）
    :param beta: β，第Ⅱ类错误概率（= 1 - 功效）
    :param h0: 原假设中的关系：μ1 - μ2 == δ, μ1 - μ2 <= δ, μ1 - μ2 >= δ
    :param delta: 原假设中两均值的差值δ
    :return: 比率Z检验结果（dict）
    """
    _alpha = alpha or s1.alpha
    _beta = beta or s1.beta

    return prop_fisher_exact_test_two_ind(
        n1=s1.n, k1=s1.k,
        n2=s2.n, k2=s2.k,
        alpha=_alpha, beta=_beta,
        h0=h0,
        delta=delta
    )

def mean_t_test(s1, s2, alpha: float=None, beta: float=None, h0: str='==', delta: float=0.0, equal_var: bool=True) -> dict:
    """
    均值t检验
    :param s1: 均值型样本
    :param s2: 均值型样本
    :param alpha: α，第Ⅰ类错误概率（= 1 - 置信水平）
    :param beta: β，第Ⅱ类错误概率（= 1 - 功效）
    :param h0: 原假设中的关系：μ1 - μ2 == δ, μ1 - μ2 <= δ, μ1 - μ2 >= δ
    :param delta: 原假设中两均值的差值δ
    :param equal_var: 方差是否相等（默认True）
    :return: 均值t检验结果（dict）
    """
    _alpha = alpha or s1.alpha
    _beta = beta or s1.beta

    return mean_t_test_two_ind(
        n1=s1.n, mean1=s1.mean, std1=s1.std,
        n2=s2.n, mean2=s2.mean, std2=s2.std,
        alpha=_alpha, beta=_beta,
        h0=h0,
        delta=delta,
        equal_var=equal_var
    )


def var_f_test(s1, s2, h0: str='==') -> dict:
    """
    方差齐性检验
    :param s1: 均值型样本
    :param s2: 均值型样本
    :param h0: 原假设中的关系：μ1 - μ2 == δ, μ1 - μ2 <= δ, μ1 - μ2 >= δ
    :return: 方差F检验结果（dict）
    """
    return var_f_test_two_ind(
        n1=s1.n, std1=s1.std,
        n2=s2.n, std2=s2.std,
        h0=h0
    )
