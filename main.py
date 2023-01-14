import asyncio
from json import load
from json.decoder import JSONDecodeError
from multiprocessing.dummy import Pool
from os import listdir, stat
from os.path import exists
from random import randint
from sys import stderr, platform, version_info, exit

from loguru import logger

from engine.actions import Actions

if platform == "win32" and (3, 8, 0) <= version_info < (3, 9, 0):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logger.remove()
logger.add(stderr,
           format="<white>{time:HH:mm:ss}</white> | <level>"
                  "{level: <8}</level> | <cyan>"
                  "{line}</cyan> - <white>{message}</white>")


class Main:
    @staticmethod
    def create_sessions_wrapper() -> None:
        while True:
            asyncio.run(Actions().create_sessions(api_id=API_ID,
                                                  api_hash=API_HASH))

            continue_creating_sessions = input('Продолжить создание сессий? (y/N): ').lower()

            if continue_creating_sessions != 'y':
                return

    @staticmethod
    def join_chat_wrapper(session_name: str) -> None:
        proxy = None

        if proxies_json and proxies_json.get(session_name):
            proxy = proxies_json[session_name]

        else:
            if proxies_list:
                proxy = proxies_list.pop(randint(0, len(proxies_list)))
                proxies_list.append(proxy)

        asyncio.run(Actions().join_chat(session_name=session_name,
                                        session_proxy_string=proxy,
                                        targets=join_chat_data,
                                        api_id=API_ID,
                                        api_hash=API_HASH))

    @staticmethod
    def send_message_wrapper(session_name: str):
        proxy = None

        if message_source_type == 1:
            message_local_file = messages_data.split('||')[0]
            message_local_text = messages_data.split('||')[1]

        else:
            if messages_data_json.get(session_name):
                message_local_file = messages_data_json[session_name]['message_folder']
                message_local_text = messages_data_json[session_name]['message_text']

            else:
                message_local_data = other_messages_data.pop()
                other_messages_data.append(message_local_data)

                message_local_file = message_local_data.split('||')[0]
                message_local_text = message_local_data.split('||')[1]

        if not message_local_file:
            message_local_file = None

        if not message_local_text:
            message_local_text = None

        if proxies_json and proxies_json.get(session_name):
            proxy = proxies_json[session_name]

        else:
            if proxies_list:
                proxy = proxies_list.pop(randint(0, len(proxies_list)))
                proxies_list.append(proxy)

        asyncio.run(Actions().send_message(session_name=session_name,
                                           session_proxy_string=proxy,
                                           message_target=message_target,
                                           message_folder=message_local_file,
                                           message_text=message_local_text,
                                           api_id=API_ID,
                                           api_hash=API_HASH))

    @staticmethod
    def click_button_wrapper(session_name: str):
        proxy = None

        if proxies_json and proxies_json.get(session_name):
            proxy = proxies_json[session_name]

        else:
            if proxies_list:
                proxy = proxies_list.pop(randint(0, len(proxies_list)))
                proxies_list.append(proxy)

        asyncio.run(Actions().click_button(session_name=session_name,
                                           button_target=button_target,
                                           button_id=button_id,
                                           session_proxy_string=proxy,
                                           api_id=API_ID,
                                           api_hash=API_HASH))

    @staticmethod
    def click_start_button_wrapper(session_name: str):
        proxy = None

        if proxies_json and proxies_json.get(session_name):
            proxy = proxies_json[session_name]

        else:
            if proxies_list:
                proxy = proxies_list.pop(randint(0, len(proxies_list)))
                proxies_list.append(proxy)

        asyncio.run(Actions().click_start_button(session_name=session_name,
                                                 referral_bot_ref_code=referral_bot_ref_code,
                                                 referral_bot_username=referral_bot_username,
                                                 session_proxy_string=proxy,
                                                 api_id=API_ID,
                                                 api_hash=API_HASH))


if __name__ == '__main__':
    print('Telegram channel - https://t.me/n4z4v0d\n'
          'Donate (any evm network): 0xDEADf12DE9A24b47Da0a43E1bA70B8972F5296F2\n')

    proxies_json = None
    proxies_list = None
    threads = None

    session_files = [current_file[:-8] for current_file in listdir('sessions')
                     if current_file[-8:] == '.session']

    logger.info(f'Успешно загружно {len(session_files)} сессий')

    with open('settings.json', 'r', encoding='utf-8-sig') as file:
        try:
            settings_json = load(file)

        except JSONDecodeError:
            logger.error('Ошибка при чтении settings.json файла')
            input('Press Any Key To Exit..')
            exit()

    API_ID = settings_json['api_id']
    API_HASH = settings_json['api_hash']

    if exists('proxies.json') and stat('proxies.json').st_size > 0:
        with open('proxies.json', 'r', encoding='utf-8-sig') as file:
            try:
                proxies_json = load(file)

            except JSONDecodeError:
                logger.error('Ошибка при чтении proxies.json файла')
                input('Press Any Key To Exit..')
                exit()

    if not proxies_json:
        logger.info('Не удалось обнаружить ни 1 прокси в `proxies.json`, ищу в `proxies.txt`')

        if exists('proxies.txt') and stat('proxies.txt').st_size > 0:
            with open('proxies.txt', 'r', encoding='utf-8-sig') as file:
                proxies_list = [row.strip() for row in file]

        else:
            logger.info('Не удалось обнаружить ни 1 прокси в `proxies.txt`, работаю без прокси')

    user_action = int(input('1. Создать Pyrogram сессии\n'
                            '2. Telegram Mass Joiner\n'
                            '3. Telegram Mass Message Sender\n'
                            '4. Telegram Mass Click Inline Buttons\n'
                            '5. Telegram Send Start Command With Referral Link\n'
                            'Выберите ваше действие: '))

    if user_action not in [1]:
        threads = int(input('Threads: '))

    print('')

    match user_action:
        case 1:
            Main().create_sessions_wrapper()

        case 2:
            join_chat_target = input('Перетяните .txt, в котором с новой строки указаны '
                                     'username\'s / join link\'s чатов/каналов: ')

            with open(join_chat_target, 'r', encoding='utf-8-sig') as file:
                join_chat_data = [row.strip() for row in file]

            with Pool(processes=threads) as executor:
                executor.map(Main().join_chat_wrapper, session_files)

        case 3:
            messages_data_json = {}
            other_messages_data = []
            message_target = input('Введите userid/username человека/бота, которому необходимо отправить сообщения: ')
            message_source_type = int(input('1. Отправка одного сообщения с каждого аккаунта\n'
                                            '2. Отправка разных сообщений с каждого аккаунта\n'
                                            'Выберите способ загрузки сообщений: '))

            if message_source_type == 1:
                messages_data = input('Введите сообщение в следующем формате: \n'
                                      'folder||content\n'
                                      'folder - путь до файла, при необходимости его отправки, может быть пустым\n'
                                      'content - содержимое сообщения (либо описание к прикрепленному файлу, '
                                      'при наличии файла может быть пустым)\n'
                                      'Пример для отправки фотографии с описанием: image.png||описание123\n'
                                      'Пример для отправки обычного сообщения без фотографии: ||сообщение\n'
                                      'Пример для отправки фотографии без описания: image.png||\n'
                                      'Введите сообщение: ')

            else:
                message_data_folder = input('Перетяните .txt с параметрами сообщения с каждого сообщения '
                                            'в следующем формате: '
                                            'folder||content\n'
                                            'folder - при необходимости отправка файла, может быть пустым\n'
                                            'content - содержимое сообщения (либо описание к прикрепленному файлу, '
                                            'при наличии файла может быть пустым)\n'
                                            'Пример для отправки фотографии с описанием: image.png||описание123\n'
                                            'Пример для отправки обычного сообщения без фотографии: ||сообщение\n'
                                            'Пример для отправки фотографии без описания: image.png||\n'
                                            '\nВ случае, если вам необходимо отправить каждое сообщение с определенной '
                                            'сессии, указывайте сообщение в следующем формате: \n'
                                            'session_name||folder||content\n'
                                            'Пример для отправки фотографии с описанием с определенной сессии: '
                                            'main_session||image.png||описание123\n'
                                            'Пример для отправки обычного сообщения без фотографии с определенной '
                                            'сессии: main_session||||сообщение\n'
                                            'Пример для отправки фотографии без описания с определенной сессии: '
                                            'main_session||image.png||\n'
                                            'Перетяните .txt файл: ')

                with open(message_data_folder, 'r', encoding='utf-8-sig') as file:
                    messages_data = [row.strip() for row in file]

            for current_message_data in messages_data:
                if len(current_message_data.split('||')) > 2:
                    messages_data_json[current_message_data.split('||')[0]] = {
                        'message_folder': current_message_data.split('||')[1],
                        'message_text': current_message_data.split('||')[2]
                    }

                else:
                    other_messages_data.append(current_message_data)

            with Pool(processes=threads) as executor:
                executor.map(Main().send_message_wrapper, session_files)

        case 4:
            button_target = input('Введите userid/username человека/бота, кнопку в '
                                  'диалоге которого необходимо нажать: ')
            button_id = int(input('Введите порядковый номер кнопки, которую необходимо нажать: ')) - 1

            with Pool(processes=threads) as executor:
                executor.map(Main().click_button_wrapper, session_files)

        case 5:
            referral_bot_link = input('Введите реферальную ссылку на бота: ').replace('https://',
                                                                                      '').replace('t.me/',
                                                                                                  '')
            referral_bot_username = referral_bot_link.split('?start=')[0]
            referral_bot_ref_code = referral_bot_link.split('?start=')[1]

            with Pool(processes=threads) as executor:
                executor.map(Main().click_start_button_wrapper, session_files)

        case _:
            logger.error('Такой функции не обнаружено')
            input('Press Any Key To Exit..')
            exit()

    print('')
    logger.info('Работа успешно завершена')
    input('Press Any Key To Exit..')
