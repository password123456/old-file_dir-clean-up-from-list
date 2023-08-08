__author__ = 'https://github.com/password123456/'
__version__ = '1.0.0-20230808'

import os
import sys
import datetime
import shutil
import requests
import json


class Bcolors:
    Black = '\033[30m'
    Red = '\033[31m'
    Green = '\033[32m'
    Yellow = '\033[33m'
    Blue = '\033[34m'
    Magenta = '\033[35m'
    Cyan = '\033[36m'
    White = '\033[37m'
    Endc = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


def start():
    backup_list = f'{os.getcwd()}/list.txt'

    try:
        if os.path.exists(backup_list):
            with open(backup_list, 'r') as f:
                for line in f:
                    if not line.startswith('#'):
                        _category = line.split(',')[0].strip()
                        _target_directory = line.split(',')[1].strip()
                        _days_to_check = int(line.split(',')[2].strip())

                        if _category and _target_directory and _days_to_check:
                            find_cleanup_items(_category, _target_directory, _days_to_check)
                        else:
                            print(f'{Bcolors.Yellow}- list file is invalid.! check {backup_list} {Bcolors.Endc}')
                            sys.exit(1)
            f.close()
        else:
            print(f'{Bcolors.Yellow}- list file not found.! check {backup_list} {Bcolors.Endc}')
    except Exception as e:
        print(f'{Bcolors.Yellow}- ::Exception:: Func:[{start.__name__}] '
              f'Line:[{sys.exc_info()[-1].tb_lineno}] [{type(e).__name__}] {e}{Bcolors.Endc}')


def find_cleanup_items(_category, _target_directory, _days_to_check):
    target_date = datetime.date.today() - datetime.timedelta(days=_days_to_check)
    cleanup_items = []

    for root, dirs, files in os.walk(_target_directory):
        for name in dirs + files:
            path = os.path.join(root, name)
            created_date = datetime.date.fromtimestamp(os.path.getctime(path))
            if created_date and created_date <= target_date:
                cleanup_items.append(path)
                # print(path)
    if cleanup_items:
        delete_items(_category, cleanup_items, _days_to_check)
    else:
        message_title = f'old item clean up'
        message = f'>> {message_title} <<\n\n- {os.uname()[1]}\n- *{datetime.datetime.now()}*'
        message = f'*{message}\n\n*{_category}* :large_green_circle:\n ---> cleaning up {_days_to_check} days ago\n```No old item to clean up```'
        send_to_slack(message)


def delete_items(_category, cleanup_items, _days_to_check):
    success_to_delete_items = ''
    failed_to_delete_items = ''
    i = 0
    n = 0
    for item_path in cleanup_items:
        item_ctime_info = get_creation_time(item_path)
        if os.path.isfile(item_path):
            try:
                os.remove(item_path)
                i += 1
                success_to_delete_items += f'{i},success,{item_ctime_info},{item_path}\n\n'
                print(f'{Bcolors.Yellow} success to delete {item_path}{Bcolors.Endc}')
            except:
                n += 1
                failed_to_delete_items += f'{n},failed,{item_ctime_info},{item_path},{e}\n\n'
                print(f'{Bcolors.Yellow} failed to delete {item_path} >> {e} {Bcolors.Endc}')
                pass

        elif os.path.isdir(item_path):
            try:
                shutil.rmtree(item_path)
                i += 1
                success_to_delete_items += f'{i},success,{item_ctime_info},{item_path}\n\n'
                print(f'{Bcolors.Yellow} success to delete {item_path} {Bcolors.Endc}')
            except Exception as e:
                n += 1
                failed_to_delete_items += f'{n},failed,{item_ctime_info},{item_path},{e}\n\n'
                print(f'{Bcolors.Yellow} failed to delete {item_path} >> {e} {Bcolors.Endc}')
                pass


    print(f'\n>> Clean up Result')
    if success_to_delete_items:
        print(success_to_delete_items)
    if failed_to_delete_items:
        print(failed_to_delete_items)

    print(f'{Bcolors.Green}------------------------------------->{Bcolors.Endc}')

    message_title = f'old item clean up'
    message = f'>> {message_title} <<\n\n- {os.uname()[1]}\n- *{datetime.datetime.now()}*'
    message = f'*{message}\n\n*{_category}* :large_green_circle:\n  ---> cleaning up {_days_to_check} days ago \n```\n{success_to_delete_items}{failed_to_delete_items}```'
    send_to_slack(message)


def get_creation_time(item):
    try:
        creation_time = datetime.datetime.fromtimestamp(os.path.getctime(item))
        return creation_time
    except Exception as e:
        print(f'execption: {e}')
        return 'None'


def send_to_slack(message):
    webhook_url = f'##Your SLACK_WEB_HOOKS##'

    header = {
        'Content-Type': 'application/json',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/49.0.2623.112 Safari/537.36',
    }

    params = [
        {
            'type': 'section',
            'text': {
                'type': 'mrkdwn',
                'text': message
            }
        }
    ]

    try:
        r = requests.post(webhook_url, headers=header, data=json.dumps({'blocks': params}), verify=True)
        print(f'{Bcolors.Green}>> Send to Slack: {r.status_code} {r.text} { Bcolors.Endc}')
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f'{Bcolors.Yellow}>> Exception: Func:[{send_to_slack.__name__}] Line:[{sys.exc_info()[-1].tb_lineno}] [{type(e).__name__}] {e}{Bcolors.Endc}')
    else:
        r.close()


def main():
    banner = """
=======================================================
    [python] old data clean up from list
=======================================================
"""
    print(f'\n')
    print(f'{Bcolors.Cyan}{banner}{Bcolors.Endc}')

    start()


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception as e:
        print(f'{Bcolors.Yellow}- ::Exception:: Func:[{__name__.__name__}] '
              f'Line:[{sys.exc_info()[-1].tb_lineno}] [{type(e).__name__}] {e}{Bcolors.Endc}')

