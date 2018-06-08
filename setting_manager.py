import sys
from datetime import datetime, timedelta, timezone

import yaml


def load() -> dict:
    _settings = file_load()
    settings = _settings['app']
    _cybozu = settings['cybozu']
    base_url = _cybozu['base_url']
    cybozu_url = base_url.format(_cybozu['basic_auth']['username'], _cybozu['basic_auth']['password'])
    return {
        'cybozu_url': cybozu_url,
        'google_scope': settings['google']['scope'],
        'sync_users': settings['sync_users'],
        'common_hash': _cybozu['common_hash'],
        'template': settings['event_template']
    }


def file_load():
    with open('setting.yml') as f:
        _settings = yaml.load(f)
    return _settings


def save_hash(_hash: str) -> None:
    _settings = file_load()
    with open('setting.yml', 'w') as f:
        _settings['app']['cybozu']['common_hash'] = _hash
        yaml.dump(_settings, f, default_flow_style=False)


public_values = load()
now = datetime.now(timezone(timedelta(hours=+9), 'Asia/Tokyo'))
PLACE_FACILITY_ID = 28
MOCK_PARAM = "mock"
MOCK_FLAG = False
if len(sys.argv) > 1 and sys.argv[1] == MOCK_PARAM:
    MOCK_FLAG = True
