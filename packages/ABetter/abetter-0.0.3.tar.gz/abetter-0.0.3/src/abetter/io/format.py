import pandas as pd
from abetter.sample_basic import Sample
from abetter.io import to_html
from abetter.sample_basic import Sample


def to_str(v, n=4) -> str:
    if v is None:
        return ''
    if isinstance(v, str):
        return v
    if abs(v) > 1000:
        return f'{v:.0f}'
    if abs(v) > 100:
        return f'{v:.1f}'
    if abs(v) > 10:
        return f'{v:.2f}'
    if abs(v) > 0:
        return f'{v:.3f}'
    if abs(v) > 0.1:
        return f'{v:.4f}'
    if abs(v) > 0.01:
        return f'{v:.5f}'
    return f'{v:.6f}'


def significance_color(pv: float) -> str:
    if pv < 0.01:
        return 'bg2'
    if pv < 0.05:
        return 'bg1'
    return 'bg0'


def significance_type(pv: float) -> str:
    if pv < 0.01:
        return '显著**'
    elif pv < 0.05:
        return '显著*'
    else:
        return '不显著'


def none_str(a, b, c=-1):
    """
    返回 a 或 a*b 或 a*b/c
    :param a:
    :param b:
    :param c:
    :return: a 或 a*b 或 a*b/c
    """
    if a == '':
        return ''
    elif isinstance(a, str):
        return a
    elif c is None:
        return '[未定义分组比例]'
    elif c > 0:
        return a * b / c
    elif c == -1:
        return a * b
    else:
        return '[未定义分组比例]'

def generate_head() -> list[dict]:
    row1 = [
        {'element': 'th', 'col': 2, 'cls': 'bt bl br', 'style': 'text-align: center', 'data': '指标'},
        {'element': 'th', 'col': 2, 'cls': 'bt bl br', 'style': 'text-align: center', 'data': '样本'},
        {'element': 'th', 'col': 2, 'cls': 'bt bl br', 'style': 'text-align: center', 'data': '实验参数'},
        {'element': 'th', 'col': 2, 'cls': 'bt bl br', 'style': 'text-align: center', 'data': '统计量'},
        {'element': 'th', 'col': 5, 'cls': 'bt bl br', 'style': 'text-align: center', 'data': '增量效果'}
    ]
    row2 = [
        {'cls': 'bl bb', 'style': 'text-align: center', 'data': '指标名称'}, {'cls': 'br bb', 'style': 'text-align: center', 'data': '指标类型'},
        {'cls': 'bl bb', 'style': 'text-align: center', 'data': '名称'}, {'cls': 'br bb', 'style': 'text-align: center', 'data': '值'},
        {'cls': 'bl bb', 'style': 'text-align: center', 'data': '名称'}, {'cls': 'br bb', 'style': 'text-align: center', 'data': '值'},
        {'cls': 'bl bb', 'style': 'text-align: center', 'data': '名称'}, {'cls': 'br bb', 'style': 'text-align: center', 'data': '值'},
        {'cls': 'bl bb', 'style': 'text-align: center', 'data': '名称'},
        {'cls': 'bb', 'style': 'text-align: center', 'data': '样本均值增量'},
        {'cls': 'bb', 'style': 'text-align: center', 'data': '左组增量'},
        {'cls': 'bb', 'style': 'text-align: center', 'data': '右组增量'},
        {'cls': 'br bb', 'style': 'text-align: center', 'data': '推全增量'}
    ]
    return [{'data': row1}, {'data': row2}]


def generate_body(s1, s2, test_data: dict) -> list[dict]:
    field_name = s1.field_name
    field_type = test_data.get('field_type')
    n1, n2, m1, m2 = s1.n, s2.n, s1.mean, s2.mean
    gr1, gr2 = s1.group_ratio, s2.group_ratio
    b_color = significance_color(test_data.get('p_value'))
    row1 = [
        {'row': 4, 'cls': f'bl br bb {b_color}', 'style': 'text-align: center', 'data': f'{field_name or ''}'},
        {'row': 4, 'cls': 'bl br bb', 'style': 'text-align: center', 'data': f'{field_type}'},
        {'cls': 'bl', 'style': 'text-align: right; color: #666', 'data': '左组样本量'}, {'cls': 'br', 'style': 'text-align: right;', 'data': f'{n1:,.0f}'},
        {'cls': 'bl', 'style': 'text-align: right; color: #666', 'data': '检验法'}, {'cls': 'br', 'style': 'text-align: right;', 'data': f'{test_data.get('method_name')}'},
        {'cls': 'bl', 'style': 'text-align: right; color: #666', 'data': '显著性'}, {'cls': f'br {b_color}', 'style': 'text-align: right;', 'data': f'{test_data.get('significance')}'},
        {'cls': 'bl', 'style': 'text-align: right; color: #666', 'data': '增量'},
        {'style': 'text-align: right;', 'data': f'{to_str(test_data.get('incr_mean'))}'},
        {'style': 'text-align: right;', 'data': f'{to_str(test_data.get('incr_group1'))}'},
        {'style': 'text-align: right;', 'data': f'{to_str(test_data.get('incr_group2'))}'},
        {'cls': 'br', 'style': 'text-align: right;', 'data': f'{to_str(none_str(test_data.get('incr_group1'), 1,  gr1))}'}
    ]
    row2 = [
        {'cls': 'bl', 'style': 'text-align: right; color: #666', 'data': '右组样本量'}, {'cls': 'br', 'style': 'text-align: right;', 'data': f'{n2:,.0f}'},
        {'cls': 'bl', 'style': 'text-align: right; color: #666', 'data': 'α'}, {'cls': 'br', 'style': 'text-align: right;', 'data': f'{to_str(test_data.get('alpha'))}'},
        {'cls': 'bl', 'style': 'text-align: right; color: #666', 'data': 'P Value'}, {'cls': 'br', 'style': 'text-align: right;', 'data': f'{to_str(test_data.get('p_value'))}'},
        {'cls': 'bl', 'style': 'text-align: right; color: #666', 'data': 'MDE'},
        {'style': 'text-align: right;', 'data': f'{to_str(test_data.get('mde'))}'},
        {'style': 'text-align: right;', 'data': f'{to_str(none_str(test_data.get('mde'), n1))}'},
        {'style': 'text-align: right;', 'data': f'{to_str(none_str(test_data.get('mde'), n2))}'},
        {'cls': 'br', 'style': 'text-align: right;', 'data': f'{to_str(none_str(test_data.get('mde') , n1 , gr1))}'}
    ]
    row3 = [
        {'cls': 'bl', 'style': 'text-align: right; color: #666', 'data': '左组均值'}, {'cls': 'br', 'style': 'text-align: right;', 'data': f'{to_str(m1)}'},
        {'cls': 'bl', 'style': 'text-align: right; color: #666', 'data': 'β'}, {'cls': 'br', 'style': 'text-align: right;', 'data': f'{to_str(test_data.get('beta'))}'},
        {'cls': 'bl', 'style': 'text-align: right; color: #666', 'data': 'Statistic'}, {'cls': 'br', 'style': 'text-align: right;', 'data': f'{to_str(test_data.get('statistic'))}'},
        {'cls': 'bl', 'style': 'text-align: right; color: #666', 'data': 'CI Lower'},
        {'style': 'text-align: right;', 'data': f'{to_str(test_data.get('ci')[0])}'},
        {'style': 'text-align: right;', 'data': f'{to_str(none_str(test_data.get('ci')[0], n1))}'},
        {'style': 'text-align: right;', 'data': f'{to_str(none_str(test_data.get('ci')[0], n2))}'},
        {'cls': 'br', 'style': 'text-align: right;', 'data': f'{to_str(none_str(test_data.get('ci')[0], n1, gr1))}'}
    ]
    row4 = [
        {'cls': 'bl bb', 'style': 'text-align: right; color: #666', 'data': '右组均值'}, {'cls': 'br bb', 'style': 'text-align: right;', 'data': f'{to_str(m2)}'},
        {'cls': 'bl bb', 'style': 'text-align: right; color: #666', 'data': '$H_0$'}, {'cls': 'br bb', 'style': 'text-align: right;', 'data': f'{test_data.get('h0')}'},
        {'cls': 'bl bb', 'style': 'text-align: right; color: #666', 'data': 'Effect Size'}, {'cls': 'br bb', 'style': 'text-align: right;', 'data': f'{to_str(test_data.get('effect_size'))}'},
        {'cls': 'bl bb', 'style': 'text-align: right; color: #666', 'data': 'CI Upper'},
        {'cls': 'bb', 'style': 'text-align: right;', 'data': f'{to_str(test_data.get('ci')[1])}'},
        {'cls': 'bb', 'style': 'text-align: right;', 'data': f'{to_str(none_str(test_data.get('ci')[1], n1))}'},
        {'cls': 'bb', 'style': 'text-align: right;', 'data': f'{to_str(none_str(test_data.get('ci')[1], n2))}'},
        {'cls': 'br bb', 'style': 'text-align: right;', 'data': f'{to_str(none_str(test_data.get('ci')[1], n1, gr1))}'}
    ]
    return [{'data': row1}, {'data': row2}, {'data': row3}, {'data': row4}]


def ss_2_html(s1: Sample, s2: Sample, test_data: dict) -> str:
    _title = s1.report_title if s1.report_title != 'AB实验结果' else s2.report_title
    _caption = {'data': [
        {'data': _title, 'style': 'text-align: center; margin: 1px; font-weight: 600;'},
        {'data': f'{s1.group_name if s1.group_name else '左组'} - {s2.group_name if s2.group_name else '右组'}', 'style': 'text-align: center; margin: 1px'}]}
    _head = {'data': generate_head()}
    _body = {'data': generate_body(s1, s2, test_data)}
    _foot = None

    return to_html.html_table(caption=_caption, head=_head, body=_body, foot=_foot)


def df_wide_2_df_stack(s1: Sample, s2: Sample, test_data: dict) -> pd.DataFrame:
    """
    df宽表 → df可读表
    :param s1: 样本1
    :param s2: 样本2
    :param test_data: 检验数据
    :return: 可读 DataFrame
    """
    _method_name = test_data.get('method_name')
    _is_beast = test_data.get('最佳检验法')
    _index = [(_method_name, _is_beast, 1), (_method_name, _is_beast, 2), (_method_name, _is_beast, 3), (_method_name, _is_beast, 4)]
    _columns = [('指标', '指标名称'), ('指标', '指标类型'),
                ('样本', '名称'), ('样本', '值'),
                ('实验参数', '名称'), ('实验参数', '值'),
                ('统计量', '名称'), ('统计量', '值'),
                ('增量效果', '名称'), ('增量效果', '样本均值增量'), ('增量效果', '左组增量'), ('增量效果', '右组增量'), ('增量效果', '推全增量')]
    _d = test_data
    _field_name, _field_type = s1.field_name if s1.field_name is not None else '[未定义指标名称]', '[均值型]' if s1.field_type=='Mean' else '[比率型]'
    _gr1, _gr2 = s1.group_ratio, s2.group_ratio
    _mde = _d.get('mde', '')
    _cil, _ciu = _d.get('ci', ('', ''))

    return pd.DataFrame([
        # 第1行
        [_field_name, _field_type, '左组样本量', s1.n, '检验法', _d.get('method_name'), '显著性', _d.get('significance'),
         '增量', _d.get('incr_mean'), _d.get('incr_group1'), _d.get('incr_group2'), none_str(_d.get('incr_group1'), 1, _gr1)],
        # 第2行
        [_field_name, _field_type, '右组样本量', s2.n, 'α', _d.get('alpha'), 'P Value', _d.get('p_value'),
         'MDE', _mde, none_str(_mde, s1.n), none_str(_mde, s2.n), none_str(_mde, s1.n, _gr1)],
        # 第3行
        [_field_name, _field_type, '左组均值', s1.mean if _field_type == '[均值型]' else s1.k / s1.n, 'β', _d.get('beta'), 'Statistic', _d.get('statistic'),
         'CI Lower', _cil, none_str(_cil, s1.n), none_str(_cil, s2.n), none_str(_cil, s1.n, _gr1)],
        # 第4行
        [_field_name, _field_type, '左组均值', s1.mean if _field_type == '[均值型]' else s1.k / s1.n, '$H_0$', _d.get('h0'), 'Effect Size', _d.get('effect_size'),
         'CI Upper', _ciu, none_str(_ciu, s1.n), none_str(_ciu, s2.n), none_str(_ciu, s1.n, _gr1)]
    ], index=pd.MultiIndex.from_tuples(_index, names=['检验法','是否最佳','序号']), columns=pd.MultiIndex.from_tuples(_columns))


def srm_2_html(srm: dict) -> str:
    """
    SRM检验结果 → HTML
    :param srm: SRM检验结果dict
    :return: HTML
    """
    # 标题
    __title = 'SRM 检验（每组样本比例的实际观测值与预期是否一致）'
    p_value = srm.get('p_value')
    if p_value<0.05:
        __sub_title = '检验结论: 【未通过】，实际与预期有显著差异**，P值=' + f'{p_value:.4f}'
        __style = 'text-align: center; color: #ff0000; margin: 1px'
    elif p_value<0.10:
        __sub_title = '检验结论: 【未通过】，实际与预期有显著差异*，P值=' + f'{p_value:.4f}'
        __style = 'text-align: center; color: #c00000; margin: 1px'
    else:
        __sub_title = '检验结论: 【通过】，实际与预期无显著差异，P值=' + f'{p_value:.4f}'
        __style = 'text-align: center; color: #333; margin: 1px'
    _caption = {'data': [
        {'data': __title, 'style': 'text-align: center; margin: 1px; font-weight: 600;'},
        {'data': __sub_title, 'style': __style}
    ]}

    # 表 Head
    __row1 = [
        {'element': 'th', 'col': 1, 'cls': 'bt bl br', 'style': 'text-align: center', 'data': '分组名称'},
        {'element': 'th', 'col': 1, 'cls': 'bt bl br', 'style': 'text-align: center', 'data': '实际样本量'},
        {'element': 'th', 'col': 1, 'cls': 'bt bl br', 'style': 'text-align: center', 'data': '实际样本比例'},
        {'element': 'th', 'col': 1, 'cls': 'bt bl br', 'style': 'text-align: center', 'data': '预期样本比例'},
        {'element': 'th', 'col': 1, 'cls': 'bt bl br', 'style': 'text-align: center', 'data': '实际比例 - 预期比例'},
        {'element': 'th', 'col': 1, 'cls': 'bt bl br', 'style': 'text-align: center', 'data': '误差：差异÷预期'}
    ]
    _head = {'data': [
        {'data': __row1}
    ]}

    # 表 Body
    obs_sample_size = srm.get('obs_sample_size')
    n = srm.get('obs_sample_size_sum')
    exp_ratio = srm.get('exp_ratio')
    group_name_list = srm.get('group_name_list')
    _body = {'data': [
        {'data':
            [
                {'row': 1, 'cls': f'bl br bt bb', 'style': 'text-align: center', 'data': f'{group_name_list[k]}'},
                {'row': 1, 'cls': f'bl br bt bb', 'style': 'text-align: center', 'data': f'{obs_sample_size[k]:.0f}'},
                {'row': 1, 'cls': f'bl br bt bb', 'style': 'text-align: center', 'data': f'{obs_sample_size[k] / n * 100:.1f}%'},
                {'row': 1, 'cls': f'bl br bt bb', 'style': 'text-align: center', 'data': f'{exp_ratio[k]*100:.1f}%'},
                {'row': 1, 'cls': f'bl br bt bb', 'style': 'text-align: center', 'data': f'{obs_sample_size[k] / n * 100 - exp_ratio[k]*100:.4f}pp'},
                {'row': 1, 'cls': f'bl br bt bb', 'style': 'text-align: center', 'data': f'{(obs_sample_size[k] / n / exp_ratio[k] - 1 )*100:.4f}%'},
            ]
         } for k in range(len(obs_sample_size))
    ]}

    # 表 Foot
    _foot = None

    return to_html.html_table(caption=_caption, head=_head, body=_body, foot=_foot)