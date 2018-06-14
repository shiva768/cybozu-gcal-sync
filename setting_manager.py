import sys
from datetime import datetime, timedelta, timezone

import yaml

from util import create_hash


def load() -> dict:
    _settings = __file_load()
    settings = _settings['app']
    _cybozu = settings['cybozu']
    base_url = _cybozu['base_url']
    cybozu_url = base_url.format(_cybozu['basic_auth']['username'], _cybozu['basic_auth']['password'])
    common_hash = __load_cache()
    return {
        'cybozu_url': cybozu_url,
        'google_scope': settings['google']['scope'],
        'sync_users': settings['sync_users'],
        'common_hash': common_hash,
        'template': settings['event_template']
    }


def __file_load() -> dict:
    with open('setting.yml') as f:
        _settings = yaml.load(f)
    return _settings


def __load_cache() -> str:
    from os.path import exists
    if not exists('.cache'):
        return ''
    with open('.cache', 'r') as f:
        return f.readlines()[0]


def __write_cache(_hash) -> None:
    with open('.cache', 'w') as f:
        f.write(_hash)
        f.flush()


def conditional_save_common_hash(common: dict, prev_hash: str) -> bool:
    """
    パラメータcommonのhash値と、パラメータprev_hashが一致していなければ保存する
    一致、不一致を result として返す

    :param dict common: hash生成元dict
    :param str prev_hash: 前回のhash
    :return: common.__hash__ != prev_hash
    :rtype: bool
    """
    _hash = create_hash(common)
    common_diff = _hash != prev_hash
    if common_diff:
        __write_cache(_hash)
    return common_diff


def __save_hash(save_func) -> None:
    _settings = __file_load()
    with open('setting.yml', 'w') as f:
        save_func(_settings)
        yaml.dump(_settings, f, default_flow_style=False)


public_values = load()
now = datetime.now(timezone(timedelta(hours=+9), 'Asia/Tokyo'))
today = now.today()
start = datetime(today.year, now.month, 1, 0, 0, tzinfo=now.tzinfo)
end = start + timedelta(days=365)
PLACE_FACILITY_ID = 28
MOCK_PARAM = "mock"
CALENDAR_META_HASH_BASE = 'meta:{0}'
MOCK_FLAG = False
if len(sys.argv) > 1 and sys.argv[1] == MOCK_PARAM:
    MOCK_FLAG = True
