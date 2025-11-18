"""
输出HTML表格
"""

def html_td(data: str, element: str = 'td', row: int = None, col: int = None, style: str = None, cls: str = None):
    """
    生成1个单元格
    :param data: 已经格式化好的字符串（可以包含HTML标签）
    :param element: td 或 th，如果是 None 使用 td
    :param row: 跨行行数
    :param col: 跨列列数
    :param style: 指定单元格 样式
    :param cls: 指定单元格 class
    :return:
    """
    _html = f"""<{element or 'td'}
{' rowspan="' + str(row) + '"' if row else ''}
{' colspan="' + str(col) + '"' if col else ''}
{' class="' + cls + '"' if cls else ''}
{' style="' + style + '"' if style else ''}
>{data}</{element or 'td'}>
"""
    return _html.replace('\n', '')


def html_tr(data: list[dict], style=None, cls=None):
    """
    生成1行tr
    :param data: 列表，每个元素是一个td数据
     例如：[{'data': 'xxx', 'element': 'td', 'row': 2, 'col': None, 'cls': 'c1.c2.c3', 'style': 'color: #F00; background: #FFF;'},...]
    :param style: 指定 tr 样式
    :param cls: 指定 tr 类
    :return:
    """
    if data is None:
        return ''
    _html = ''
    for da in data:
        _td = html_td(element=da.get('element'), data=da.get('data'), row=da.get('row'), col=da.get('col'), cls=da.get('cls'), style=da.get('style'))
        _html += _td + '\n'
    return f"""<tr{' class="' + cls + '"' if cls else ''}{' style="' + style + '"' if style else ''}>{_html}</tr>"""


def html_caption(data: list[dict], cls=None, style=None):
    """
    生成表标题
    :param data:
    :param cls:
    :param style:
    :return:
    """
    _caption = ''
    _row = ''
    for da in data:
        _row += f"""<p{' class="' + da.get('cls') + '"' if da.get('cls') else ''}{' style="' + da.get('style') + '"'}>{da.get('data')}</p>"""
    if _row != '':
        _caption += f"""<caption{' class="' + cls + '"' if cls else ''}{' style="' + style + '"' if style else ''}>{_row}</caption>"""
    return _caption


def html_body(element: str = 'tbody', data: list[dict] = None, cls=None, style=None):
    """
    生成多行tr，即：thaed, tbody, tfoot内部HTML
    :param element: thaed, tbody, tfoot
    :param data: 列表，每个元素是一个tr数据，例如：[{'data': 'xxx', 'cls': 'c1.c2.c3', 'style': 'color: #F00; background: #FFF;'},...]
    :param cls:
    :param style:
    :return:
    """
    _body = ''
    _row = ''
    for da in data:
        _row += html_tr(data=da.get('data'), cls=da.get('cls'), style=da.get('style')) + '\n'
    if _row != '':
        _body += f"""<{element}{' class="' + cls + '"' if cls else ''}{' style="' + style + '"' if style else ''}>{_row}</{element}>"""
    return _body


def html_table(caption: dict = None,
               head: dict = None,
               body: dict = None,
               foot: dict = None,
               css: str = None, cls: str = None, style: str = 'border="1" class="dataframe"'):
    """
    生成Table
    :param caption: 字典，例如：{'data': 'xxx', 'cls': 'c1.c2.c3', 'style': 'color: #F00; background: #FFF;'}
    :param head: 字典，例如：{'data': 'xxx', 'cls': 'c1.c2.c3', 'style': 'color: #F00; background: #FFF;'}。
    其中data是一个列表，每个元素是一个tr数据，例如：[{'data': 'xxx', 'cls': 'c1.c2.c3', 'style': 'color: #F00; background: #FFF;'},...]
    :param body: 字典，同上
    :param foot: 字典，同上
    :param css: 指定 CSS
    :param cls: 指定 table 类
    :param style: 指定 table 样式
    :return:
    """
    # 标题
    _css = css or """<style scoped>
th.ba, td.ba {border: 1px solid #ccc}
th.blr, td.blr {border-left: 1px solid #ccc; border-right: 1px solid #ccc;}
th.btb, td.btb {border-top: 1px solid #ccc; border-bottom: 1px solid #ccc;}
th.bl, td.bl {border-left: 1px solid #ccc}
th.br, td.br {border-right: 1px solid #ccc}
th.bt, td.bt {border-top: 1px solid #ccc}
th.bb, td.bb {border-bottom: 1px solid #ccc}

th.bg0, td.bg0 {background-color: #cccccc}
th.bg1, td.bg1 {background-color: #fcf6bd}
th.bg2, td.bg2 {background-color: #ffcb05}
th.c, td.c {text-align: center}
</style>"""
    # 表 caption
    _caption = ''
    if caption is not None:
        _caption = html_caption(data=caption.get('data'), cls=caption.get('cls'), style=caption.get('style'))
    # 表 head
    _head = ''
    if head is not None:
        _head = html_body(element='thead', data=head.get('data'), cls=head.get('cls'), style=head.get('style'))

    # 表 body
    _body = ''
    if body is not None:
        _body = html_body(element='tbody', data=body.get('data'), cls=body.get('cls'), style=body.get('style'))

    # 表 foot
    _foot = ''
    if foot is not None:
        _foot = html_body(element='tfoot', data=foot.get('data'), cls=foot.get('cls'), style=foot.get('style'))
    # 整合

    # 返回结果
    return f"""<div>
{_css}
<table {'class="' + cls + '"' if cls else ''} {'style="' + style + '"' if style else ''}>
{_caption}
{_head}
{_body}
{_foot}
</table></div>
"""
