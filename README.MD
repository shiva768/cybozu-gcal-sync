cybozu-google-calendar-sync
====

cybozuのスケジュールを、google calendarに同期するツール

## Description
cybozuの内部APIからデータを取得してgoogle calendarに登録する  
なんらかの事情で、cybozu、garoon連携が出来ない時のためのツール  
内部APIを利用しているため、アップデート次第で使えなくなります

## Requirement
### packages
- PyYAML/3.12
- google-api-python-client-py3/1.2
- requests/2.19.1
### environment
サイボウズ Office Version 10.5.0 20160310092917

## Usage
1. setting.ymlを設定する  
2. `python ./cybozu_gcal_sync.py`  
3. 初回起動時に、googleの認証があるので承認する

## Install
git clone https://github.com/shiva768/cybozu-gcal-sync.git

## Licence

[MIT](https://github.com/tcnksm/tool/blob/master/LICENCE)

## Author

[shiva768](https://github.com/shiva768)
