import datetime
import json
import sys
from functools import wraps

import mock

import requests

""" config """
BASIC_AUTHENTICATION_USERNAME = 'shibata'
BASIC_AUTHENTICATION_PASSWORD = 'Weserve123'
USERNAME = 'shibata'
PASSWORD = ''
CGI_URL = "https://{0}:{1}@cybozu.weserve.co.jp/cgi-bin/cbag/ag.cgi" \
    .format(BASIC_AUTHENTICATION_USERNAME, BASIC_AUTHENTICATION_PASSWORD)
""" /config """
today = datetime.datetime.today()
MOCK_PARAM = "mock"
MOCK_FLAG = False
args = sys.argv
if len(args) > 1 and args[1] == MOCK_PARAM:
    MOCK_FLAG = True


def main():
    login_info = login()
    token = get_token(login_info)
    holiday_list = get_holiday_list(login_info, token, today)
    facillity_list = get_facillity_list(login_info, token)
    user_list = get_user_list(login_info, token)
    schedule_list = get_schedule_list(login_info, token, today)


def mock_decorator(func):
    if MOCK_FLAG:
        @wraps(func)
        def wrapper(*args, **kwargs):
            name = func.__name__
            return eval('mock.' + name)()

        return wrapper
    return func


@mock_decorator
def login():
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    data = '_System=login&_Login=1&LoginMethod=2&_Account=shibata&Password=&Submit=%E3%83%AD%E3%82%B0%E3%82%A4%E3%83%B3'
    url = "{0}?page=mobile".format(CGI_URL)
    result = requests.post(url=url, data=data, headers=headers)
    print("SSID:{0}, ID:{1}".format(result.cookies['AGSESSID'], result.headers['X-Cybozu-User']))
    return dict(AGSESSID=result.cookies['AGSESSID'], AGLOGINID=result.headers['X-Cybozu-User'])


@mock_decorator
def get_token(login_info):
    url = "{0}/v1/auth/context".format(CGI_URL)
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    result = requests.post(url=url, headers=headers, cookies=login_info)
    print(json.loads(result.text)['context']['requestToken'])
    return json.loads(result.text)['context']['requestToken']


@mock_decorator
def get_holiday_list(login_info, token, today):
    url = "{0}/v1/schedule/holiday/list".format(CGI_URL)
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    data = dict(requestToken=token, year=today.year)
    result = requests.post(url=url, data=data, headers=headers, cookies=login_info)
    print(result.text)
    return json.loads(result.text)['rows']


@mock_decorator
def get_facillity_list(login_info, token):
    url = "{0}/v1/schedule/facility/list".format(CGI_URL)
    return common_request(login_info, token, url)


@mock_decorator
def get_user_list(login_info, token):
    url = "{0}/v1/base/user/list".format(CGI_URL)
    return common_request(login_info, token, url)


def common_request(login_info, token, url):
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    data = dict(requestToken=token)
    result = requests.post(url=url, data=data, headers=headers, cookies=login_info)
    print(result.text)
    return json.loads(result.text)['rows']


@mock_decorator
def get_schedule_list(login_info, token, today):
    url = "{0}/v1/schedule/event/list".format(CGI_URL)
    headers = {'X-Requested-With': 'XMLHttpRequest'}
    end = today + datetime.timedelta(days=360)
    data = dict(requestToken=token, start=today, end=end, userId=login_info['AGLOGINID'])
    result = requests.post(url=url, data=data, headers=headers, cookies=login_info)
    print(result.text)
    return json.loads(result.text)['rows']


if __name__ == '__main__':
    main()
