from matplotlib import pyplot as plt
from scipy.stats import norm
import numpy as np
import pandas as pd
from abetter import SampleMean
from abetter.sample_mean import SSMean
from abetter.io.format import to_str
from abetter.test.two_inde_mean_t_test import mean_t_test_two_ind
from abetter.test.two_inde_mean_z_test import mean_z_test_two_ind
from abetter.test.two_inde_prop_z_test import prop_z_test_two_ind


def plot_two_mean(s1: SampleMean, s2: SampleMean, points: int = 200) -> tuple[plt.Figure, plt.Axes]:
    """
    绘制两个均值型样本的总体均值分布
    :param s1: 样本1
    :param s2: 样本2
    :param points: 绘图精度，越大精度越高，默认200
    :return: fig, ax
    """
    with plt.ioff():
        c1, c2 = '#118ab2', '#bc4749'
        # 计算
        std1, std2 = s1.std / np.sqrt(s1.n), s2.std / np.sqrt(s2.n)
        x_min = min(s1.mean - std1 * 5, s2.mean - std2 * 5)
        x_max = max(s1.mean + std1 * 5, s2.mean + std2 * 5)
        x = np.linspace(x_min, x_max, points)
        y1 = norm.pdf(x, loc=s1.mean, scale=std1)
        y2 = norm.pdf(x, loc=s2.mean, scale=std2)
        y_max = np.max([y1, y2]) * 1.1

        # 绘图
        fig, ax = plt.subplots(figsize=(7, 5))
        ax.plot(x, 0 * x, c='k', lw=1)

        sd1, = ax.plot(x, y1, c=c1, label=r'$\overline{X}_1$')
        sd2, = ax.plot(x, y2, c=c2, label=r'$\overline{X}_2$')
        ax.set_xlim(x_min, x_max)

        # 绘制辅助线
        ax.vlines(s1.mean, 0, y_max, lw=0.5, ls='-', color='k', alpha=0.5)
        ax.vlines(s2.mean, 0, y_max, lw=0.5, ls='-', color='k', alpha=0.5)
        ax.hlines(y_max * 0.95, s1.mean, s2.mean, lw=1, ls='-', color='k', alpha=0.5)
        ax.text((s1.mean + s2.mean) / 2, y_max * 0.95, f'Diff={to_str(s2.mean - s1.mean)}', ha='center', va='bottom')

        # 填充
        alpha = 0.05 if s1.alpha is None else s1.alpha
        label1, label2 = f'{100 * (1 - alpha):.0f}%' + r' CI of $\overline{X}_1$', f'{100 * (1 - alpha):.0f}%' + r' CI of $\overline{X}_2$'
        z = norm.isf(alpha / 2)
        x1 = np.linspace(s1.mean - std1 * z, s1.mean + std1 * z, points)
        y1 = norm.pdf(x1, loc=s1.mean, scale=std1)
        x2 = np.linspace(s2.mean - std2 * z, s2.mean + std2 * z, points)
        y2 = norm.pdf(x2, loc=s2.mean, scale=std2)
        f1 = ax.fill_between(x1, y1, 0, color=c1, alpha=0.5, label=label1)
        f2 = ax.fill_between(x2, y2, 0, color=c2, alpha=0.5, label=label2)
        ax.text(s1.mean, np.max(y1) * 0.3, '95%', ha='center', va='center')
        ax.text(s2.mean, np.max(y2) * 0.3, '95%', ha='center', va='center')

        # 坐标刻度
        ax.set_frame_on(False)
        ax.set_axis_off()

        ax.vlines(s1.mean, 0 - y_max * 0.02, 0, lw=0.5, ls='-', color='k', alpha=0.5)
        ax.text(s1.mean, 0 - y_max * 0.02, to_str(s1.mean), ha='center', va='top')

        ax.vlines(s2.mean, 0 - y_max * 0.06, 0, lw=0.5, ls='-', color='k', alpha=0.5)
        ax.text(s2.mean, 0 - y_max * 0.06, to_str(s2.mean), ha='center', va='top')

        # 设置
        plt.title('Distributions of 2 Sample Means')
        ax.legend([sd1, sd2, f1, f2], [r'$\overline{X}_1$', r'$\overline{X}_2$', label1, label2])

        return fig, ax


def plot_diff_mean(ss: SSMean, points: int = 200) -> tuple[plt.Figure, plt.Axes]:
    """
    绘制两个均值型样本之差的总体均值分布
    :param ss: SSMean 类型，即两个 SampleMean 的差
    :param points: 绘图精度，越大精度越高，默认200
    :return: fig, ax
    """
    with plt.ioff():
        c1, c2 = '#118ab2', '#bc4749'
        # 计算
        sem = ss.dict_test_best.get('sem')
        mde = ss.dict_test_best.get('mde')
        alpha = 0.05 if ss.s1.alpha is None else ss.s1.alpha
        beta = 0.20 if ss.s1.beta is None else ss.s1.beta
        z = norm.isf(alpha / 2)

        x_min, x_max = -sem * 5, mde + sem * 5
        x = np.linspace(x_min, x_max, points)
        y1 = norm.pdf(x, loc=0.0, scale=sem)
        y2 = norm.pdf(x, loc=mde, scale=sem)
        y_max = np.max([y1, y2])

        # 绘制密度函数
        fig, ax = plt.subplots(figsize=(8, 5))
        ax.plot(x, 0 * x, c='k', lw=1)
        sd1, = ax.plot(x, y1, c=c1, label='H0')
        sd2, = ax.plot(x, y2, c=c2, label='H1', ls='--')

        # 绘制辅助线
        ax.vlines(0.0, 0, y_max, lw=0.5, ls='-', color='k', alpha=0.5)
        ax.vlines(mde, 0, y_max, lw=0.5, ls='-', color='k', alpha=0.5)
        ax.vlines(sem * z, 0, y_max * 1.05, lw=0.5, ls='-', color='k', alpha=0.5)
        ax.text(sem * z, y_max * 1.05, f'c={to_str(sem * z)}', ha='center', va='bottom')

        # 填充
        label1, label2 = r'Error Ⅰ: $\alpha={alpha}$'.format(alpha=f'{alpha: .2f}'), r'Error Ⅱ: $\beta={beta}$'.format(beta=f'{beta: .2f}')
        x1 = np.linspace(sem * z, sem * z * 5, points)
        y1 = norm.pdf(x1, loc=0, scale=sem)
        x2 = np.linspace(-sem * z * 5, sem * z, points)
        y2 = norm.pdf(x2, loc=mde, scale=sem)
        f1 = ax.fill_between(x1, y1, 0, color=c1, alpha=0.5, label=label1)
        f2 = ax.fill_between(x2, y2, 0, color=c2, alpha=0.5, label=label2)

        # 坐标刻度
        ax.set_frame_on(False)
        ax.set_axis_off()
        ax.vlines(0, 0 - y_max * 0.02, 0, lw=0.5, ls='-', color='k', alpha=0.5)
        ax.text(0, 0 - y_max * 0.02, '0', ha='center', va='top')

        ax.vlines(mde, 0 - y_max * 0.06, 0, lw=0.5, ls='-', color='k', alpha=0.5)
        ax.text(mde, 0 - y_max * 0.06, f'MDE={to_str(mde)}', ha='center', va='top')
        ax.text(sem * z + mde * 0.05, y_max * 0.03, r'$\alpha=${alpha}%'.format(alpha=f'{100 * alpha:.0f}'), ha='left', va='center')
        ax.text(sem * z - mde * 0.05, y_max * 0.03, r'$\beta=${beta}%'.format(beta=f'{100 * beta:.0f}'), ha='right', va='center')

        # 设置
        plt.title('Distribution of the Difference Between 2 Sample Means')
        ax.set_xlim(x_min, x_max)
        ax.set_ylim(-y_max * 0.06, y_max * 1.15)
        ax.legend([sd1, sd2, f1, f2], [
            r'$H_0: \overline{X}_2$ - $\overline{X}_1 = 0$',
            r'$H_1: \overline{X}_2$ - $\overline{X}_1 \geqslant MDE$',
            r'Error Ⅰ: $\alpha=${alpha}'.format(alpha=f'{100*alpha:.0f}%'),
            r'Error Ⅱ: $\beta=${beta}'.format(beta=f'{100*beta:.0f}%')
        ])
        return fig, ax


def plot_mde_mean_sample(std1: float, std2: float,
                         n_ratio: tuple[int]=(20, 80),
                         n_min_range: tuple[int]=(5, 100),
                         points: int=100,
                         alpha_beta: tuple[tuple[float]]=((0.05, 0.20), (0.05, 0.10), (0.05, 0.05)),
                         test: str="t",
                         equal_var: bool=True):
    """
    绘制均值型样本的MDE
    :param std1: 第1组样本标准差
    :param std2: 第2组样本标准差
    :param n_ratio: 两组样本比例，默认值 (20, 80)
    :param n_min_range: 最小那一组样本的样本量范围，默认值 (5, 100)
    :param points: 绘图精度，越大精度越高，默认值 100
    :param alpha_beta: α和β的取值对，默认值 ((0.05, 0.20), (0.05, 0.10), (0.05, 0.05))
    :param test: 检验方法，t检验和z检验，取值 't' 或 'z'
    :param equal_var: 方差是否相等，仅对 t检验 有效
    :return: fig, ax, mde
    """
    color_list = ['#' + _ for _ in '03045e-023e8a-0077b6-0096c7-00b4d8-48cae4-90e0ef-ade8f4-caf0f8'.split('-')]
    ratio = max(n_ratio) / min(n_ratio)
    mde = []
    # 计算MDE ------------------------------------------------------------------------------------------------------------------------
    if test in ('t', 'T'):
        # t 检验
        for i in range(*n_min_range, max(1, np.floor((n_min_range[1] - n_min_range[0]) / points).astype('int64'))):
            n1, n2 = np.floor((i, i * ratio)).astype('int64')
            nn = {'n1': n1, 'n2': n2}
            mm = {f'mde_alpha_{a:.4f}_beta_{b:.4f}': mean_t_test_two_ind(
                n1=n1, mean1=1, std1=std1,
                n2=n2, mean2=2, std2=std2,
                alpha=a, beta=b, h0='==',
                equal_var=equal_var).get('mde')
                  for a, b in alpha_beta}
            mde.append(nn | mm)
    elif test in ('z', 'Z'):
        # Z 检验
        for i in range(*n_min_range, max(1, np.floor((n_min_range[1] - n_min_range[0]) / points).astype('int64'))):
            n1, n2 = np.floor((i, i * ratio)).astype('int64')
            nn = {'n1': n1, 'n2': n2}
            mm = {f'mde_alpha_{a:.4f}_beta_{b:.4f}': mean_z_test_two_ind(
                n1=n1, mean1=1, std1=std1,
                n2=n2, mean2=2, std2=std2,
                alpha=a, beta=b, h0='==').get('mde')
                  for a, b in alpha_beta}
            mde.append(nn | mm)
    else:
        raise ValueError("test 取值只有 z 和 t 两种")
    # 转为 DataFrame
    mde = pd.DataFrame(mde)
    # 绘图 ------------------------------------------------------------------------------------------------------------------------
    # 关闭输出
    with plt.ioff():
        # 绘制密度函数
        fig, ax = plt.subplots(figsize=(7, 5))
        # 遍历所有的 alpha_beta 组合
        alpha_beta = mde.columns[2:]
        axs = [ax.plot(mde.n1, mde[c], c=color_list[i % 9], label=r'$\overline{X}_1$') for i, c in enumerate(alpha_beta)]
        ax.set_xlim(min(mde.n1), max(mde.n1))

        # 坐标刻度
        ax.grid()

        # 设置
        plt.title('MDE on the sample size of the smallest group', fontsize=12, fontweight='bold', pad=20)
        sub_title = 'MeanSample: Z-Test' if test not in ('t', 'T') else f'MeanSample: t-Test, {"Equal" if equal_var else "Unequal"} var'
        plt.text(
            0.5, 1,  # 位置（相对坐标，0.5是水平中心）
            sub_title,
            fontsize=10,
            ha='center',  # 水平居中
            va='bottom',
            transform=plt.gca().transAxes  # 使用轴坐标系统
        )
        alpha_beta = [_.replace('mde_alpha_', r'$\alpha$=').replace('_beta_', r', $\beta$=') for _ in alpha_beta]
        ax.legend([_[0] for _ in axs], alpha_beta)
        # 轴标签
        plt.xlabel("Sample Size of the smallest group")
        plt.ylabel("MDE")

    return fig, ax, mde


def plot_mde_prop_sample(prop: float,
                         n_ratio: tuple[int]=(20, 80),
                         n_min_range: tuple[int]=(5, 100),
                         points: int=100,
                         alpha_beta: tuple[tuple[float]]=((0.05, 0.20), (0.05, 0.10), (0.05, 0.05))):
    """
    绘制比率型样本的MDE
    提示：由于本工具使用Z检验计算比率型样本的MDE，当阳性样本占比太小或太大时，要求样本量足够大（**每一组的阳性样本和阴性样本都不能低于10个**），否则比率并不服从正态分布，MDE曲线会呈现锯齿状，结果不可信！这时需要使用其他检验方法（例如 Fisher 精确检验），或者提高 n_min_range 的取值范围。
    :param prop: 阳性样本占比（根据经验估计），并认为原假设成立（H0: prop1 == prop2）
    :param n_ratio: 两组样本比例，默认值 (20, 80)
    :param n_min_range: 最小那一组样本的样本量范围，默认值 (5, 100)
    :param points: 绘图精度，越大精度越高，默认值 100
    :param alpha_beta: α和β的取值对，默认值 ((0.05, 0.20), (0.05, 0.10), (0.05, 0.05))
    :return:
    """
    color_list = ['#' + _ for _ in '03045e-023e8a-0077b6-0096c7-00b4d8-48cae4-90e0ef-ade8f4-caf0f8'.split('-')]
    ratio = max(n_ratio) / min(n_ratio)
    mde = []
    # 计算MDE ------------------------------------------------------------------------------------------------------------------------
    # Z 检验
    for i in range(*n_min_range, max(1, np.floor((n_min_range[1] - n_min_range[0]) / points).astype('int64'))):
        n1, n2 = np.floor([i, i * ratio]).astype('int64')
        k1, k2 = np.floor([n1 * prop, n2 * prop]).astype('int64')
        nn = {'n1': n1, 'n2': n2}
        mm = {f'mde_alpha_{a:.4f}_beta_{b:.4f}': prop_z_test_two_ind(
            n1=n1, k1=k1,
            n2=n2, k2=k2,
            alpha=a, beta=b, h0='==').get('mde')
              for a, b in alpha_beta}
        mde.append(nn | mm)
    # 转为 DataFrame
    mde = pd.DataFrame(mde)
    # 绘图 ------------------------------------------------------------------------------------------------------------------------
    # 关闭输出
    with plt.ioff():
        # 绘制密度函数
        fig, ax = plt.subplots(figsize=(7, 5))
        # 遍历所有的 alpha_beta 组合
        alpha_beta = mde.columns[2:]
        axs = [ax.plot(mde.n1, mde[c], c=color_list[i % 9], label=r'$\overline{X}_1$') for i, c in enumerate(alpha_beta)]
        ax.set_xlim(min(mde.n1), max(mde.n1))

        # 坐标刻度
        ax.grid()

        # 设置
        plt.title('MDE on the sample size of the smallest group', fontsize=12, fontweight='bold', pad=20)
        sub_title = 'PropSample: Z-Test'
        plt.text(
            0.5, 1,  # 位置（相对坐标，0.5是水平中心）
            sub_title,
            fontsize=10,
            ha='center',  # 水平居中
            va='bottom',
            transform=plt.gca().transAxes  # 使用轴坐标系统
        )
        alpha_beta = [_.replace('mde_alpha_', r'$\alpha$=').replace('_beta_', r', $\beta$=') for _ in alpha_beta]
        ax.legend([_[0] for _ in axs], alpha_beta)
        # 轴标签
        plt.xlabel("Sample Size of the smallest group")
        plt.ylabel("MDE (unit: pp)")

    return fig, ax, mde