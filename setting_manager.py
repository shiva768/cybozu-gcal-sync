import sys
from datetime import datetime, timedelta, timezone

import yaml


def load() -> dict:
    _settings = __file_load()
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


def __file_load():
    with open('setting.yml') as f:
        _settings = yaml.load(f)
    return _settings


def conditional_save_common_hash(common, prev_hash):
    _hash = __create_hash(common)
    common_diff = _hash != prev_hash
    if common_diff:
        def save(_setting):
            _setting['app']['cybozu']['common_hash'] = _hash

        __save_hash(save)
    return common_diff


def conditional_save_hash(schedule, index, prev_hash):
    _hash = __create_hash(schedule)
    diff = _hash != prev_hash
    if diff:
        def save(_setting):
            _setting['app']['sync_users'][index]['hash'] = _hash

        __save_hash(save)
    return diff


def __save_hash(save_func):
    _settings = __file_load()
    with open('setting.yml', 'w') as f:
        save_func(_settings)
        yaml.dump(_settings, f, default_flow_style=False)


def __create_hash(target: object) -> str:
    import hashlib, pickle
    return hashlib.sha256(pickle.dumps(target)).hexdigest()


public_values = load()
now = datetime.now(timezone(timedelta(hours=+9), 'Asia/Tokyo'))
today = now.today()
start = datetime(today.year, now.month, 1, 0, 0, tzinfo=now.tzinfo)
end = start + timedelta(days=365)
PLACE_FACILITY_ID = 28
MOCK_PARAM = "mock"
MOCK_FLAG = False
if len(sys.argv) > 1 and sys.argv[1] == MOCK_PARAM:
    MOCK_FLAG = True
