import datetime
import sys

import cybozu_cal as cybozu
import google_cal as google
from setting_manager import conditional_save_common_hash, conditional_save_hash, public_values

today = datetime.datetime.today()
MOCK_PARAM = "mock"
MOCK_FLAG = False
args = sys.argv
if len(args) > 1 and args[1] == MOCK_PARAM:
    MOCK_FLAG = True


def main() -> None:
    login_info = cybozu.login({'cybozu_username': 'shibata', 'cybozu_password': ''})
    token = cybozu.get_token(login_info)
    common = cybozu.get_commons(login_info, token)
    common_diff = conditional_save_common_hash(common, public_values['common_hash'])

    for index, sync_user in enumerate(public_values['sync_users']):  # type: (int, dict)
        login_info = cybozu.login(sync_user)
        token = cybozu.get_token(login_info)
        schedule_list = cybozu.get_schedule_list(login_info, token)
        diff = conditional_save_hash(schedule_list, index, sync_user['hash'])
        if common_diff or diff:
            google.update_schedule(
                schedule_list,
                common,
                sync_user['google_credential_prefix'],
                sync_user['google_managed_calendar_name']
            )


if __name__ == '__main__':
    main()
