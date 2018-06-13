from __future__ import print_function

# noinspection PyProtectedMember
from apiclient.discovery import Resource, build
from httplib2 import Http
from oauth2client import client, file, tools

from setting_manager import now, public_values, start as _start

scope = public_values['google_scope']
MANAGED_CALENDAR_NAME = ''


def register_schedule(cal_service: Resource, target_id: str, schedules: dict, common: dict):
    for schedule in schedules:
        # noinspection PyDictCreation
        body = {}
        body['summary'] = schedule['title']
        body.update(get_times(schedule))
        for facility in schedule['facilities']:
            if facility in common['facility']['place']:
                body['location'] = common['facility']['place'][facility]['name']
                schedule['facilities'].remove(facility)
                break
        description = public_values['template'].format(
            schedule['body'],
            resolve_id(common['user'], schedule['users']),
            resolve_id(common['facility']['other'], schedule['facilities'])
        )
        body['description'] = description
        print(body)
        # noinspection PyUnresolvedReferences
        cal_service.events().insert(calendarId=target_id, body=body).execute()


def get_times(schedule: dict):
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


def resolve_id(master: dict, targets: dict):
    result = []
    for target in targets:
        name = master[target]['name']  # type: str
        result.append(str(name.replace('　', ' ')))
    return '\n'.join(result)


def update_schedule(schedule: dict, common: dict, prefix: str, calendar_name: str):
    cal_service = get_service(prefix)
    target_id = get_target_id(cal_service, calendar_name)

    # noinspection PyTypeChecker
    clear_events(cal_service, target_id)
    register_schedule(cal_service, target_id, schedule, common)


def clear_events(cal_service, target_id):
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


def get_service(prefix: str) -> Resource:
    store = file.Storage('credential/{0}_credential.json'.format(prefix))
    creds = store.get()
    # noinspection PyUnresolvedReferences
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', scope)
        flags = tools.argparser.parse_args(args=[])
        creds = tools.run_flow(flow, store, flags)
    return build('calendar', 'v3', http=creds.authorize(Http()))


# noinspection PyUnresolvedReferences
def get_target_id(service: Resource, calendar_name: str):
    target = filter(lambda i: (i['summary'] if 'summary' in i else None) == calendar_name,
                    service.calendarList().list().execute()['items'])
    result = next(target, None)
    if result is None:
        return service.calendars() \
            .insert(body={'summary': calendar_name, 'timeZone': 'Asia/Tokyo'}) \
            .execute()['id']
    return result['id']
