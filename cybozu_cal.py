import datetime
import json
from functools import wraps

import requests

from cybozu_gcal_sync import MOCK_FLAG
from setting import CGI_URL, today


def main():
    login_info = login()
    token = get_token(login_info)
    holiday_list = get_holiday_list(login_info, token, today)
    facility_list = get_facillity_list(login_info, token)
    user_list = get_user_list(login_info, token)
    schedule_list = get_schedule_list(login_info, token, today)
    return dict(holiday=holiday_list,
                facility=facility_list,
                user=user_list,
                schedule=schedule_list)


def conditionally_mock_decorator(func):
    if MOCK_FLAG:
        # noinspection PyUnresolvedReferences
        import mock
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = func.__name__
            return eval('mock.' + name)()

        return wrapper
    return func


@conditionally_mock_decorator
def login():
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    data = '_System=login&_Login=1&LoginMethod=2&_Account=shibata&Password=&Submit=%E3%83%AD%E3%82%B0%E3%82%A4%E3%83%B3'
    url = "{0}?page=mobile".format(CGI_URL)
    result = requests.post(url=url, data=data, headers=headers)
    print("SSID:{0}, ID:{1}".format(result.cookies['AGSESSID'], result.headers['X-Cybozu-User']))
    return dict(AGSESSID=result.cookies['AGSESSID'], AGLOGINID=result.headers['X-Cybozu-User'])


@conditionally_mock_decorator
def get_token(login_info):
    url = "{0}/v1/auth/context".format(CGI_URL)
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    result = requests.post(url=url, headers=headers, cookies=login_info)
    print(json.loads(result.text)['context']['requestToken'])
    return json.loads(result.text)['context']['requestToken']


@conditionally_mock_decorator
def get_holiday_list(login_info, token, today):
    url = "{0}/v1/schedule/holiday/list".format(CGI_URL)
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    data = dict(requestToken=token, year=today.year)
    result = requests.post(url=url, data=data, headers=headers, cookies=login_info)
    print(result.text)
    return json.loads(result.text)['rows']


@conditionally_mock_decorator
def get_facillity_list(login_info, token):
    url = "{0}/v1/schedule/facility/list".format(CGI_URL)
    return common_request(login_info, token, url)


@conditionally_mock_decorator
def get_user_list(login_info, token):
    url = "{0}/v1/base/user/list".format(CGI_URL)
    return common_request(login_info, token, url)


def common_request(login_info, token, url):
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    data = dict(requestToken=token)
    result = requests.post(url=url, data=data, headers=headers, cookies=login_info)
    print(result.text)
    return json.loads(result.text)['rows']


@conditionally_mock_decorator
def get_schedule_list(login_info, token, today):
    url = "{0}/v1/schedule/event/list".format(CGI_URL)
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    end = today + datetime.timedelta(days=360)
    data = dict(requestToken=token, start=today, end=end, userId=login_info['AGLOGINID'])
    result = requests.post(url=url, data=data, headers=headers, cookies=login_info)
    print(result.text)
    return json.loads(result.text)['rows']
