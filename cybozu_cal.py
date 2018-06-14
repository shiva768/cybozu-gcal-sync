import collections
import json
from datetime import datetime
from functools import wraps

import requests

# noinspection PyUnresolvedReferences
import mock
from cybozu_gcal_sync import MOCK_FLAG
from setting_manager import PLACE_FACILITY_ID, end, public_values, start, today
from util import list2dict, list2group_dict

cybozu_url = public_values['cybozu_url']


def get_commons(login_info: dict, token: str) -> dict:
    holiday_list = __get_holiday_list(login_info, token, today)
    facility_list = __get_facility_list(login_info, token)
    user_list = __get_user_list(login_info, token)
    return collections.OrderedDict([('facility', facility_list), ('holiday', holiday_list), ('user', user_list)])


def __conditionally_mock_decorator(func):
    if MOCK_FLAG:
        # noinspection PyUnusedLocal
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = func.__name__
            return eval('mock.' + name)()

        return wrapper
    return func


@__conditionally_mock_decorator
def login(sync_user: dict) -> dict:
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    data = "_System=login&_Login=1&LoginMethod=2&_Account={0}&Password={1}&Submit=%E3%83%AD%E3%82%B0%E3%82%A4%E3%83%B3" \
        .format(sync_user['cybozu_username'],
                sync_user['cybozu_password'] if sync_user['cybozu_password'] is not None else '')
    url = "{0}?page=mobile".format(cybozu_url)
    result = requests.post(url=url, data=data, headers=headers)
    print("SSID:{0}, ID:{1}".format(result.cookies['AGSESSID'], result.headers['X-Cybozu-User']))
    return dict(AGSESSID=result.cookies['AGSESSID'], AGLOGINID=result.headers['X-Cybozu-User'])


@__conditionally_mock_decorator
def get_token(login_info: dict) -> str:
    url = "{0}/v1/auth/context".format(cybozu_url)
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    result = requests.post(url=url, headers=headers, cookies=login_info)
    print(json.loads(result.text)['context']['requestToken'])
    return json.loads(result.text)['context']['requestToken']


@__conditionally_mock_decorator
def __get_holiday_list(login_info: dict, token: str, _today: datetime):
    url = "{0}/v1/schedule/holiday/list".format(cybozu_url)
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    data = dict(requestToken=token, year=_today.year)
    result = requests.post(url=url, data=data, headers=headers, cookies=login_info)
    print(result.text)
    return json.loads(result.text, object_pairs_hook=collections.OrderedDict)['rows']


@__conditionally_mock_decorator
def __get_facility_list(login_info: dict, token: str):
    url = "{0}/v1/schedule/facility/list".format(cybozu_url)
    group_dict = list2group_dict(__common_request(login_info, token, url))
    place_dict = group_dict.pop(PLACE_FACILITY_ID)
    other_dict = {}
    for v in group_dict.values():
        other_dict.update(v)
    return collections.OrderedDict([('place', place_dict), ('other', collections.OrderedDict(other_dict.items()))])


@__conditionally_mock_decorator
def __get_user_list(login_info: dict, token: str):
    url = "{0}/v1/base/user/list".format(cybozu_url)
    return list2dict(__common_request(login_info, token, url))


def __common_request(login_info: dict, token: str, url: str):
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    data = dict(requestToken=token)
    result = requests.post(url=url, data=data, headers=headers, cookies=login_info)
    print(result.text)
    return json.loads(result.text, object_pairs_hook=collections.OrderedDict)['rows']


@__conditionally_mock_decorator
def get_schedule_list(login_info: dict, token: str):
    url = "{0}/v1/schedule/event/list".format(cybozu_url)
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    data = dict(requestToken=token, start=datetime.strftime(start, '%Y-%m-%dT%H:%M:%SZ'),
                end=datetime.strftime(end, '%Y-%m-%dT%H:%M:%SZ'), userId=login_info['AGLOGINID'])
    result = requests.post(url=url, data=data, headers=headers, cookies=login_info)
    print(result.text)
    return json.loads(result.text, object_pairs_hook=collections.OrderedDict)['rows']
