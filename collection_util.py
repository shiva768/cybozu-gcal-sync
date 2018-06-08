from itertools import groupby
from operator import itemgetter


def list2group_dict(_list):
    result = {}
    sorted_list = sorted(_list, key=lambda k: k['groupId'])
    for (group_key, values) in groupby(sorted_list, key=itemgetter('groupId')):
        result.update({group_key: list2dict(values)})
    return result


def list2dict(values):
    return {item['id']: item for item in values}
