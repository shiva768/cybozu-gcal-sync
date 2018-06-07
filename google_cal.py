from __future__ import print_function

import datetime

from apiclient.discovery import build
from httplib2 import Http
from oauth2client import client, file, tools

from setting import MANAGED_CALENDAR_NAME, SCOPES


# Setup the Calendar API
def main():
    cal_service = get_service()
    target_id = get_target_id(cal_service)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
    print('Getting the upcoming 10 events')
    events_result = cal_service.events().list(calendarId=target_id,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
    events = events_result.get('items', [])

    if not events:
        print('No upcoming events found.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        print(start, event['summary'] if 'summary' in event else 'none')


def get_service():
    global service
    store = file.Storage('credential.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('client_secret.json', SCOPES)
        flags = tools.argparser.parse_args(args=[])
        creds = tools.run_flow(flow, store, flags)
    return build('calendar', 'v3', http=creds.authorize(Http()))


def get_target_id(service):
    target = filter(lambda i: (i['summary'] if 'summary' in i else None) == MANAGED_CALENDAR_NAME,
                    service.calendarList().list().execute()['items'])
    result = next(target, None)
    if result is None:
        return service.calendars().insert(body={'summary': MANAGED_CALENDAR_NAME, 'timeZone': 'Asia/Tokyo'}).execute()['id']
    return result['id']


if __name__ == '__main__':
    main()
