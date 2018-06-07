import sys
from datetime import datetime, timedelta, timezone

import yaml


def load():
    global cybozu_url
    with open('setting.yml') as f:
        _settings = yaml.load(f)
    settings = _settings['app']
    _cybozu = settings['cybozu']
    base_url = _cybozu['base_url']
    cybozu_url = base_url.format(_cybozu['basic_auth']['username'], _cybozu['basic_auth']['password'])
    return {
        'cybozu_url': cybozu_url,
        'google_scope': settings['google']['scope'],
        'sync_users': settings['sync_users'],
        'hash': _cybozu['hash']
    }


def save_hash(_hash):
    with open('setting.yml', 'w') as f:
        _settings = yaml.load(f)
        _settings['app']['cybozu']['hash'] = _hash
        yaml.dump(_settings, f)


public_values = load()
now = datetime.now(timezone(timedelta(hours=+9), 'JST'))
MOCK_PARAM = "mock"
MOCK_FLAG = False
if len(sys.argv) > 1 and sys.argv[1] == MOCK_PARAM:
    MOCK_FLAG = True
