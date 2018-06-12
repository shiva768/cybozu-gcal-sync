import datetime
import hashlib
import pickle
import sys

import cybozu_cal as cybozu
from setting_manager import public_values, save_common_hash, save_hash

today = datetime.datetime.today()
MOCK_PARAM = "mock"
MOCK_FLAG = False
args = sys.argv
if len(args) > 1 and args[1] == MOCK_PARAM:
    MOCK_FLAG = True


# def cybozu_data():
#     _cybozu_data = cybozu.update_schedule()
#     create_hash = hashlib.sha256(pickle.dumps(_cybozu_data))
#     if create_hash == public_values['create_hash']:
#         return {}
#     save_common_hash(create_hash)
#     return _cybozu_data
#
#
# def update_google_cal(cybozu_data):
#     google.update_schedule(cybozu_data)


def main() -> None:
    login_info = cybozu.login({'cybozu_username': 'shibata', 'cybozu_password': ''})
    token = cybozu.get_token(login_info)
    common = cybozu.get_commons(login_info, token)
    current_common_hash = create_hash(common)
    print('result:' + current_common_hash)
    common_diff = public_values['common_hash'] != current_common_hash
    if common_diff:
        save_common_hash(current_common_hash)

    for index, sync_user in enumerate(public_values['sync_users']):  # type: (int, dict)
        login_info = cybozu.login(sync_user)
        token = cybozu.get_token(login_info)
        schedule_list = cybozu.get_schedule_list(login_info, token)
        _hash = create_hash(schedule_list)
        # if common_diff or _hash != sync_user['create_hash']:
        #     google.update_schedule(schedule_list, common, sync_user['google_credential_prefix'],
        #                            sync_user['google_managed_calendar_name'])
        save_hash(index, _hash)


recursive_idx = 0


def create_hash(target):
    global recursive_idx
    if type(target) is dict:
        _list = sorted(target.items(), key=lambda t: t[0])
        for v in _list:
            recursive_idx = recursive_idx + 1
            print('level:' + str(recursive_idx) + ',' + str(v))
            if type(v) in (dict, tuple):
                v[1] = create_hash(v[1])
            else:
                v = hashlib.sha256(pickle.dumps(v)).hexdigest()
    recursive_idx = recursive_idx - 1
    print('level:' + str(recursive_idx) + ',' + str(target))
    return hashlib.sha256(pickle.dumps(target)).hexdigest()


#
# def create_hash(target: object) -> str:
#     return recursive_hash(target)
#
#
# def recursive_hash(target):
#     print('outer:' + str(target))
#     if type(target) is dict:
#         return hashlib.sha256(pickle.dumps(sorted(target.items(), key=lambda v: inner(v)))).hexdigest()
#     return hashlib.sha256(pickle.dumps(target)).hexdigest()
#
#
# def inner(target):
#     print('inner:' + str(target))
#     t = target.get['id'] if type(target) is dict and 'id' in target else target[1]
#     m = recursive_hash(t)
#     print(str(type(m)) + ',  ' + str(target))
#     print('hash:' + m)
#     return m


if __name__ == '__main__':
    main()

# TODO cybozu, googleはクラス使ってなんとかしたほうがさっぱりするかもしれない
