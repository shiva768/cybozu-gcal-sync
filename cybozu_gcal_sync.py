import datetime
import sys

import cybozu_cal as cybozu

today = datetime.datetime.today()
MOCK_PARAM = "mock"
MOCK_FLAG = False
args = sys.argv
if len(args) > 1 and args[1] == MOCK_PARAM:
    MOCK_FLAG = True


def get_cyboze_data():
    cybozu_info = cybozu.main()
    print(cybozu_info)


def main():
    get_cyboze_data()


if __name__ == '__main__':
    main()
