import cybozu_cal as cybozu
from google_cal import GoogleCalendar
from setting_manager import conditional_save_common_hash, public_values


def main() -> None:
    print('getting cybozu common.')
    login_info = cybozu.login({'cybozu_username': 'shibata', 'cybozu_password': ''})
    token = cybozu.get_token(login_info)
    common = cybozu.get_commons(login_info, token)
    common_diff = conditional_save_common_hash(common, public_values['common_hash'])
    for index, sync_user in enumerate(public_values['sync_users']):  # type: (int, dict)
        print("start sync process. user {0}.".format(sync_user['google_credential_prefix']))
        print('getting cybozu schedule.')
        login_info = cybozu.login(sync_user)
        token = cybozu.get_token(login_info)
        schedules = cybozu.get_schedule_list(login_info, token)
        exclude = sync_user.get('cybozu_exclude_schedule')  # type: str
        if exclude is not None:
            excludes = exclude.split(',')

            def exclude_filter(value: dict):
                for e in excludes:
                    if value['title'].find(e) >= 0:
                        return False
                return True

            schedules = list(filter(exclude_filter, schedules))
        print('syncing cybozu to google schedule.')
        gcal = GoogleCalendar(
            sync_user['google_managed_calendar_name'],
            sync_user['google_credential_prefix'],
            schedules,
            common,
            common_diff
        )
        gcal.update_schedule()
        print("end sync process. user {0}.".format(sync_user['google_credential_prefix']))

if __name__ == '__main__':
    main()
