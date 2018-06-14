from itertools import groupby
from operator import itemgetter


def list2group_dict(_list: list, key='groupId'):
    """
    dictのlist list[dict]をgroupIdでsortして、groupIdでグループ化する

    :return: { groupId: value, groupId: value ...} の形式
    """
    result = {}
    sorted_list = sorted(_list, key=lambda k: k[key])
    for (group_key, values) in groupby(sorted_list, key=itemgetter(key)):
        result.update({group_key: list2dict(values)})
    return result


def list2dict(_list: list, key='id'):
    return {item[key]: item for item in _list}


def create_hash(target: object) -> str:
    import hashlib, pickle
    return hashlib.sha256(pickle.dumps(target)).hexdigest()
