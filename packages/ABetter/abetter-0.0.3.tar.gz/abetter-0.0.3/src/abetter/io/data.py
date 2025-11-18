import pandas as pd
import numpy as np


def data_wide_2_data_col(data: pd.DataFrame,
                         group_name: str = 'group_name',
                         sample_size: str = 'n',
                         mean_prefix: str = 'mean_',
                         std_prefix: str = 'std_',
                         k_prefix: str = 'k_'
                         ) -> pd.DataFrame:
    """
    宽数据转为列数据
    :param data: group_name, n, mean_xx, std_xx, mean_yy, std_yy, k_zz
    :param group_name:
    :param sample_size:
    :param mean_prefix:
    :param std_prefix:
    :param k_prefix:
    :return: group_name, field_type, field_name, n, mean, std, k
    """
    cols = data.columns
    if group_name != 'group_name':
        data.rename(columns={group_name: 'group_name'}, inplace=True)
    if sample_size != 'n':
        data.rename(columns={sample_size: 'n'}, inplace=True)
    if mean_prefix != 'mean_':
        n = len(mean_prefix)
        for col in cols:
            if col.startswith(mean_prefix):
                new_name = 'mean_' + col[n:]
                data.rename(columns={col: new_name}, inplace=True)
    if std_prefix != 'std_':
        n = len(std_prefix)
        for col in cols:
            if col.startswith(std_prefix):
                new_name = 'std_' + col[n:]
                data.rename(columns={col: new_name}, inplace=True)
    if k_prefix != 'k_':
        n = len(k_prefix)
        for col in cols:
            if col.startswith(k_prefix):
                new_name = 'k_' + col[n:]
                data.rename(columns={col: new_name}, inplace=True)

    field_name = [('mean', col[5:]) if col.startswith(mean_prefix) else ('prop', col[2:])
                  for col in cols if col.startswith(mean_prefix) or col.startswith(k_prefix)]

    row_num = len(data)
    temp = [pd.DataFrame({
        'group_name': data.group_name.values,
        'field_type': [f[0]] * row_num,
        'field_name': [f[1]] * row_num,
        'n': data.n.values,
        'mean': data['mean_' + f[1]].values if f[0] == 'mean' else [np.nan] * row_num,
        'std': data['std_' + f[1]].values if f[0] == 'mean' else [np.nan] * row_num,
        'k': data['k_' + f[1]].values if f[0] == 'prop' else [np.nan] * row_num,
    }) for f in field_name]

    return pd.concat(temp, axis=0)


def data_col_2_sample(data,
                      group_name: str = 'group_name',
                      field_type: str = 'field_type',
                      field_name: str = 'field_name',
                      sample_size: str='n',
                      mean: str='mean',
                      k: str='k', ):
    """
    列数据转化为 Sample
    :param data:
    :param group_name:
    :param field_type:
    :param field_name:
    :param sample_size:
    :param mean:
    :param k:
    :return:
    """
    data.rename(columns={
        group_name: 'group_name',
        field_type: 'field_type',
        field_name: 'field_name',
        sample_size: 'n',
        mean: 'mean',
        k: 'k'
    }, inplace=True)
    field_list = data.field_name.unique().tolist()
    group_list = data.group_name.unique().tolist()
    