
from datetime import datetime,date
from blog.settings import settings

def json_serial(obj):
    if isinstance(obj, (datetime,date)):
        return obj.isoformat()
    raise TypeError("Type {}s not serializable".format(obj))


def get_page(count):
    '''
    获取分页信息
    :param count: 总数
    :return: 总页数
    '''
    MAX_PER_PAGE = settings['MAX_PER_PAGE']
    page = 1
    if count > MAX_PER_PAGE:
        page = count // MAX_PER_PAGE
        if count % MAX_PER_PAGE:
            page += 1
    return page


def get_next_pre_page(current_api_path, current_page, page):
    '''
    获取上一页和下一页的url
    :param current_api_path: 当前api相对路径
    :param current_page: 当前页码
    :param page: 总页码
    :return: (previous, next)
    '''
    previous = None
    next = None
    err = None
    current_base_url = settings['SITE_URL'] + current_api_path
    param = settings['PAGINATE_PARAM']
    if current_page < page:
        next = current_base_url + '?{}={}'.format(param, current_page + 1)
        if current_page == 1:
            previous = None
        else:
            previous = current_base_url + '?{}={}'.format(param, current_page - 1)
    elif current_page == page:
        next = None
        if current_page == 1:
            previous = None
        else:
            previous = current_base_url + '?{}={}'.format(param, current_page - 1)

    else:
        err = '无效页面。'

    return (previous, next, err)