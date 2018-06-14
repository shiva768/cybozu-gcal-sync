from __future__ import print_function

from collections import OrderedDict

from apiclient.discovery import Resource, build
from httplib2 import Http
from oauth2client import client, file, tools

from judgement_type import JudgementType
from setting_manager import CALENDAR_META_HASH_BASE, now, public_values, start as _start
from util import create_hash

CREDENTIAL_JSON = 'credential/{0}_credential.json'


# noinspection PyUnresolvedReferences,PyMethodMayBeStatic
class GoogleCalendar:
    scope = public_values['google_scope']

    def __init__(self, calendar_name: str, prefix: str, schedules: dict, common: dict, common_diff: bool):
        self.prefix = prefix
        self.service = self.__create_service(prefix)
        self.target_calendar = self.__get_target(calendar_name)
        self.schedules = schedules
        self.common = common
        self.common_diff = common_diff

    def __create_service(self, prefix: str) -> Resource:
        store = file.Storage(CREDENTIAL_JSON.format(prefix))
        creds = store.get()
        if not creds or creds.invalid:
            flow = client.flow_from_clientsecrets('client_secret.json', self.scope)
            flags = tools.argparser.parse_args(args=[])
            creds = tools.run_flow(flow, store, flags)
        return build('calendar', 'v3', http=creds.authorize(Http()))

    def __get_target(self, calendar_name: str):
        target = filter(lambda i: (i['summary'] if 'summary' in i else None) == calendar_name,
                        self.service.calendarList().list().execute()['items'])
        result = next(target, None)
        if result is None:
            return self.service.calendars() \
                .insert(body={'summary': calendar_name, 'timeZone': 'Asia/Tokyo'}) \
                .execute()
        return result

    def update_schedule(self):

        _hash = create_hash(self.schedules)
        if _hash == self.__get_target_hash() and not self.common_diff:
            print("{0}:difference none.".format(self.prefix))
            return

        target_id = self.target_calendar['id']
        matching_id = []
        for schedule in self.schedules:
            schedule_hash = create_hash(schedule)
            _judgement_status, gcal_event_id = self.__get_judgement_status(target_id, schedule, schedule_hash)
            if _judgement_status != JudgementType.EQUAL_HASH:
                if _judgement_status == JudgementType.EQUAL_ID:
                    self.__delete_schedule(target_id, gcal_event_id)
                gcal_event_id = self.__register_schedule(schedule, target_id, schedule_hash)
            matching_id.append(gcal_event_id)
        print('deleted cybozu schedule')
        self.__delete_deleted_cybozu_schedule(target_id, matching_id)
        print('update hash')
        self.__update_target_hash(target_id, _hash)

    def __get_target_hash(self):
        import re
        desc = self.target_calendar.get('description')
        if desc is None:
            return
        regex = re.compile(CALENDAR_META_HASH_BASE.format("([A-z0-9]+)"))
        matcher = regex.search(desc)
        return matcher.group(1)

    def __update_target_hash(self, target_id, _hash):
        calendar = self.service.calendars().get(calendarId=target_id).execute()
        calendar['description'] = CALENDAR_META_HASH_BASE.format(_hash)
        self.service.calendars().update(calendarId=target_id, body=calendar).execute()

    def __get_judgement_status(self, target_id: str, schedule: dict, schedule_hash) -> tuple:
        equal_hash = self.__search_events(target_id, lambda: 'hash=' + schedule_hash)
        if equal_hash:
            return JudgementType.EQUAL_HASH, equal_hash[0]['id']
        equal_id = self.__search_events(target_id, lambda: 'cybozu_id=' + str(schedule['id']))
        if equal_id:
            return JudgementType.EQUAL_ID, equal_id[0]['id']
        return JudgementType.NONE, ''

    def __search_events(self, target_id, value_func):
        return self.service.events().list(
            calendarId=target_id,
            timeMin=_start.isoformat(),
            maxResults=10,
            privateExtendedProperty=value_func()
        ).execute() \
            .get('items', [])

    def __delete_schedule(self, target_id, gcal_event_id):
        self.service.events().delete(calendarId=target_id, eventId=gcal_event_id).execute()

    def __delete_deleted_cybozu_schedule(self, target_id, matching_id):
        events_result = self.service \
            .events() \
            .list(calendarId=target_id,
                  timeMin=_start.isoformat(),
                  maxResults=999
                  ) \
            .execute()
        events = events_result.get('items', [])  # type: list
        if events:
            for event in filter(lambda e: e['id'] not in matching_id, events):
                self.service.events().delete(calendarId=target_id, eventId=event['id']).execute()

    def __register_schedule(self, schedule, target_id, schedule_hash):
        body = OrderedDict()
        body['summary'] = schedule['title']
        body.update(self.__get_times(schedule))
        for facility in schedule['facilities']:
            if facility in self.common['facility']['place']:
                body['location'] = self.common['facility']['place'][facility]['name']
                schedule['facilities'].remove(facility)
                break
        description = public_values['template'].format(
            schedule['body'],
            self.__resolve_id(self.common['user'], schedule['users']),
            self.__resolve_id(self.common['facility']['other'], schedule['facilities'])
        )
        body['description'] = description
        body['extendedProperties'] = dict(private=dict(hash=schedule_hash, cybozu_id=schedule['id']))
        print(body)
        return self.service.events().insert(calendarId=target_id, body=body).execute()['id']

    def __get_times(self, schedule: dict):
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

    def __resolve_id(self, master: dict, targets: dict):
        result = []
        for target in targets:
            name = master[target]['name']  # type: str
            result.append(str(name.replace('　', ' ')))
        return '\n'.join(result)
