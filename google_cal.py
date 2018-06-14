from __future__ import print_function

# noinspection PyProtectedMember
from apiclient.discovery import Resource, build
from httplib2 import Http
from oauth2client import client, file, tools

from judgement_type import JudgementType
from setting_manager import CALENDAR_META_HASH_BASE, now, public_values, start as _start
from util import create_hash

scope = public_values['google_scope']


def __update_target_hash(cal_service, target_id, _hash):
    calendar = cal_service.calendars().get(calendarId=target_id).execute()
    calendar['description'] = CALENDAR_META_HASH_BASE.format(_hash)
    cal_service.calendars().update(calendarId=target_id, body=calendar).execute()


def __get_judgement_status(cal_service, target_id, schedule) -> tuple:
    equal_hash = __search_events(cal_service, target_id, lambda: 'hash=' + create_hash(schedule))
    if equal_hash:
        return JudgementType.EQUAL_HASH, equal_hash[0]['id']
    equal_id = __search_events(cal_service, target_id, lambda: 'cybozu_id=' + str(schedule['id']))
    if equal_id:
        return JudgementType.EQUAL_ID, equal_id[0]['id']
    return JudgementType.NONE, ''


def __search_events(cal_service, target_id, value_func):
    return cal_service.events().list(
        calendarId=target_id,
        timeMin=_start.isoformat(),
        maxResults=10,
        privateExtendedProperty=value_func()
    ).execute() \
        .get('items', [])


def __delete_schedule(cal_service, target_id, gcal_event_id):
    cal_service.events().delete(calendarId=target_id, eventId=gcal_event_id).execute()


def __delete_deleted_cybozu_schedule(cal_service, target_id, matching_id):
    events_result = cal_service \
        .events() \
        .list(calendarId=target_id,
              timeMin=_start.isoformat(),
              maxResults=999
              ) \
        .execute()
    events = events_result.get('items', [])  # type: list
    if events:
        for event in filter(lambda e: e['id'] not in matching_id, events):
            cal_service.events().delete(calendarId=target_id, eventId=event['id']).execute()


def update_schedule(schedules: dict, common: dict, prefix: str, calendar_name: str, common_diff: bool):
    cal_service = __get_service(prefix)
    target = __get_target(cal_service, calendar_name)

    _hash = create_hash(schedules)
    if _hash == __get_target_hash(target) and not common_diff:
        print("{0}:difference none.".format(prefix))
        return
    target_id = target['id']

    matching_id = []
    for schedule in schedules:
        _judgement_status, gcal_event_id = __get_judgement_status(cal_service, target_id, schedule)
        if _judgement_status != JudgementType.EQUAL_HASH:
            if _judgement_status == JudgementType.EQUAL_ID:
                __delete_schedule(cal_service, target_id, gcal_event_id)
            gcal_event_id = __register_schedule__(cal_service, common, schedule, target_id)
        matching_id.append(gcal_event_id)
    print('deleted cybozu schedule')
    __delete_deleted_cybozu_schedule(cal_service, target_id, matching_id)
    print('update hash')
    __update_target_hash(cal_service, target_id, _hash)


def __get_service(prefix: str) -> Resource:
    store = file.Storage('credential/{0}_credential.json'.format(prefix))
    creds = store.get()
    # noinspection PyUnresolvedReferences
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', scope)
        flags = tools.argparser.parse_args(args=[])
        creds = tools.run_flow(flow, store, flags)
    return build('calendar', 'v3', http=creds.authorize(Http()))


# noinspection PyUnresolvedReferences
def __get_target(service: Resource, calendar_name: str):
    target = filter(lambda i: (i['summary'] if 'summary' in i else None) == calendar_name,
                    service.calendarList().list().execute()['items'])
    result = next(target, None)
    if result is None:
        return service.calendars() \
            .insert(body={'summary': calendar_name, 'timeZone': 'Asia/Tokyo'}) \
            .execute()
    return result


def __get_target_hash(target: dict) -> str:
    import re
    desc = target.get('description')
    if desc is None:
        return None
    regex = re.compile(CALENDAR_META_HASH_BASE.format("([A-z0-9]+)"))
    matcher = regex.search(desc)
    return matcher.group(1)


def __clear_events(cal_service, target_id):
    events_result = cal_service \
        .events() \
        .list(calendarId=target_id,
              timeMin=_start.isoformat(),
              maxResults=999
              ) \
        .execute()
    events = events_result.get('items', [])  # type: list
    if events:
        for event in events:
            cal_service.events().delete(calendarId=target_id, eventId=event['id']).execute()


def __register_schedule(cal_service: Resource, target_id: str, schedules: dict, common: dict):
    for schedule in schedules:
        # noinspection PyDictCreation
        __register_schedule__(cal_service, common, schedule, target_id)


def __register_schedule__(cal_service, common, schedule, target_id):
    body = {}
    body['summary'] = schedule['title']
    body.update(__get_times(schedule))
    for facility in schedule['facilities']:
        if facility in common['facility']['place']:
            body['location'] = common['facility']['place'][facility]['name']
            schedule['facilities'].remove(facility)
            break
    description = public_values['template'].format(
        schedule['body'],
        __resolve_id(common['user'], schedule['users']),
        __resolve_id(common['facility']['other'], schedule['facilities'])
    )
    body['description'] = description
    body['extendedProperties'] = dict(private=dict(hash=create_hash(schedule), cybozu_id=schedule['id']))
    print(body)
    # noinspection PyUnresolvedReferences
    return cal_service.events().insert(calendarId=target_id, body=body).execute()['id']


def __get_times(schedule: dict):
    time_key = 'date' if schedule['allDay'] else 'dateTime'
    start = schedule['start']
    end = schedule['end']
    if end is None:  # allDayではありえないはず
        from datetime import datetime, timedelta
        date = datetime.strptime(start, '%Y-%m-%dT%H:%M:%SZ') + timedelta(days=1)
        end = datetime.strftime(
            datetime(date.year,
                     date.month,
                     date.day, 0, 0,
                     tzinfo=now.tzinfo),
            '%Y-%m-%dT%H:%M:%S+09:00'
        )
    return {
        'start': {'timeZone': now.tzinfo.__str__(), time_key: start},
        'end': {'timeZone': now.tzinfo.__str__(), time_key: end}
    }


def __resolve_id(master: dict, targets: dict):
    result = []
    for target in targets:
        name = master[target]['name']  # type: str
        result.append(str(name.replace('　', ' ')))
    return '\n'.join(result)
