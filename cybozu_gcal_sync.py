import datetime
import hashlib
import pickle
import sys

import cybozu_cal as cybozu
import google_cal as google
from setting_manager import public_values, save_common_hash, save_hash

today = datetime.datetime.today()
MOCK_PARAM = "mock"
MOCK_FLAG = False
args = sys.argv
if len(args) > 1 and args[1] == MOCK_PARAM:
    MOCK_FLAG = True


# def cybozu_data():
#     _cybozu_data = cybozu.update_schedule()
#     hash = hashlib.sha256(pickle.dumps(_cybozu_data))
#     if hash == public_values['hash']:
#         return {}
#     save_common_hash(hash)
#     return _cybozu_data
#
#
# def update_google_cal(cybozu_data):
#     google.update_schedule(cybozu_data)


def main() -> None:
    login_info = cybozu.login({'cybozu_username': 'shibata', 'cybozu_password': ''})
    token = cybozu.get_token(login_info)
    common = cybozu.get_commons(login_info, token)
    current_common_hash = hash(common)
    common_diff = public_values['common_hash'] != current_common_hash
    if common_diff:
        save_common_hash(current_common_hash)

    for index, sync_user in enumerate(public_values['sync_users']):  # type: (int, dict)
        login_info = cybozu.login(sync_user)
        token = cybozu.get_token(login_info)
        schedule_list = cybozu.get_schedule_list(login_info, token)
        _hash = hash(schedule_list)
        if common_diff or _hash != sync_user['hash']:
            google.update_schedule(schedule_list, common, sync_user['google_credential_prefix'],
                                   sync_user['google_managed_calendar_name'])
        save_hash(index, _hash)


def hash(target: object) -> str:
    return hashlib.sha256(pickle.dumps(target)).hexdigest()


if __name__ == '__main__':
    main()

# TODO cybozu, googleはクラス使ってなんとかしたほうがさっぱりするかもしれない
