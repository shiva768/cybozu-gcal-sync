from setting_manager import PLACE_FACILITY_ID
from util import list2dict, list2group_dict


def login():
    return {'AGSESSID': '38cd000266a467bf333e24b2349c9ff52b7a02fc0bceac46', 'AGLOGINID': '1'}


def get_token():
    return 'f869282bae2674feca84251a5892edb9'


def __get_holiday_list():
    return [{"date": "2018-02-12", "name": "振替休日"}, {"date": "2018-03-21", "name": "春分の日"},
            {"date": "2018-04-30", "name": "振替休日"}, {"date": "2018-05-03", "name": "憲法記念日"},
            {"date": "2018-05-04", "name": "みどりの日"}, {"date": "2018-05-05", "name": "こどもの日"},
            {"date": "2018-07-16", "name": "海の日"}, {"date": "2018-08-11", "name": "山の日"},
            {"date": "2018-09-17", "name": "敬老の日"}, {"date": "2018-09-23", "name": "秋分の日"},
            {"date": "2018-09-24", "name": "振替休日"}, {"date": "2018-10-08", "name": "体育の日"},
            {"date": "2018-11-03", "name": "文化の日"}, {"date": "2018-11-23", "name": "勤労感謝の日"},
            {"date": "2018-12-23", "name": "天皇誕生日"}, {"date": "2018-12-24", "name": "振替休日"},
            {"date": "2018-12-29", "name": "年末年始休暇"},
            {"date": "2018-12-30", "name": "年末年始休暇"},
            {"date": "2018-12-31", "name": "年末年始休暇"}]


def __get_facility_list():
    group_dict = list2group_dict([{"id": 1, "groupId": 28, "name": "会議室1", "body": "\r\n"},
                                  {"id": 2, "groupId": 28, "name": "会議室2", "body": "\r\n"},
                                  {"id": 3, "groupId": 29, "name": "つくえ", "body": "\r\n"}
                                  ])
    place_dict = group_dict.pop(PLACE_FACILITY_ID)
    other_dict = {}
    for v in group_dict.values():
        other_dict.update(v)
    return {'place': place_dict, 'other': other_dict}


if __name__ == '__main__':
    print(__get_facility_list())


def __get_user_list():
    return list2dict([{"id": 1, "code": "hoge1", "name": "ほげ １", "nameReading": "",
                       "email": "hoge1@hogehoge11.com", "url": "", "phone": ""},
                      {"id": 2, "code": "hoge2", "name": "ほげ ２", "nameReading": "",
                       "email": "hoge2@hogehoge11.com", "url": "", "phone": ""},
                      {"id": 3, "code": "hoge3", "name": "ほげ ３", "nameReading": "",
                       "email": "hoge3@hogehoge11.com", "url": "", "phone": ""},
                      ])


def get_schedule_list():
    return [
        {"id": 1200, "private": False, "allDay": True, "banner": True, "start": "2018-06-01", "end": "2018-06-08",
         "recurrence": None, "temporary": None, "title": "よてい１", "plan": "作業", "detail": "よてい１",
         "body": "よてい１のないよう",
         "users": [1, 2], "organizations": [], "facilities": [1]},
        {"id": 1300, "private": False, "allDay": True, "banner": False, "start": "2018-06-07", "end": "2018-06-07",
         "recurrence": None, "temporary": None, "title": "", "plan": "", "detail": "", "body": "", "users": [3],
         "organizations": [], "facilities": [3]},
    ]
