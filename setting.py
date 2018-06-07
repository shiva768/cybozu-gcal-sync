import datetime
import sys

""" config """
BASIC_AUTHENTICATION_USERNAME = 'shibata'
BASIC_AUTHENTICATION_PASSWORD = 'Weserve123'
USERNAME = 'shibata'
PASSWORD = ''
CGI_URL = "https://{0}:{1}@cybozu.weserve.co.jp/cgi-bin/cbag/ag.cgi" \
    .format(BASIC_AUTHENTICATION_USERNAME, BASIC_AUTHENTICATION_PASSWORD)
MANAGED_CALENDAR_NAME = 'from cybozu'
SCOPES = 'https://www.googleapis.com/auth/calendar'
""" /config """
today = datetime.datetime.today()
MOCK_PARAM = "mock"
MOCK_FLAG = False
args = sys.argv
if len(args) > 1 and args[1] == MOCK_PARAM:
    MOCK_FLAG = True
