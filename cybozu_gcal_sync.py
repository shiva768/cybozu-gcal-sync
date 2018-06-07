import datetime
import hashlib
import pickle
import sys

import cybozu_cal as cybozu
import google_cal as google
from setting_manager import public_values, save_hash

today = datetime.datetime.today()
MOCK_PARAM = "mock"
MOCK_FLAG = False
args = sys.argv
if len(args) > 1 and args[1] == MOCK_PARAM:
    MOCK_FLAG = True


def cybozu_data():
    _cybozu_data = cybozu.main()
    hash = hashlib.sha256(pickle.dumps(_cybozu_data))
    if hash == public_values['hash']:
        return {}
    save_hash(hash)
    return _cybozu_data


def update_google_cal(cybozu_data):
    google.main(cybozu_data)


def main():
    _cybozu_data = cybozu_data()
    if not bool(_cybozu_data):

    update_google_cal(cybozu_data)


if __name__ == '__main__':
    main()

# TODO cybozu, googleはクラス使ってなんとかしたほうがさっぱりするかもしれない
