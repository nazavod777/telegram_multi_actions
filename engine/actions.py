import asyncio
from re import match
from sys import platform, version_info, stderr

from aiofiles.os import mkdir
from aiofiles.ospath import exists
from loguru import logger
from pyrogram import Client
from pyrogram.errors import FloodWait

from errors import exceptions

if platform == "win32" and (3, 8, 0) <= version_info < (3, 9, 0):
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

logger.remove()
logger.add(stderr,
           format="<white>{time:HH:mm:ss}</white> | <level>"
                  "{level: <8}</level> | <cyan>"
                  "{line}</cyan> - <white>{message}</white>")


def type_conversion(content: any) -> any:
    try:
        content = int(content)

    except ValueError:
        pass

    return content


def get_proxy_dict(proxy_string: str) -> dict | None:
    if proxy_string is None:
        return None

    if not match(r'^[a-zA-Z]+://[a-zA-Z0-9.-]+:[a-zA-Z0-9.-]+@[a-zA-Z0-9._-]+:[0-9]{1,5}$', proxy_string) \
            and not match(r'^[a-zA-Z]+://[a-zA-Z0-9.-]+:[a-zA-Z0-9.-]$', proxy_string):
        raise exceptions.WrongProxyFormat(f'The string {proxy_string} does not match the proxy format')

    proxy_type = proxy_string.split(':')[0]
    proxy_host, proxy_port = proxy_string.split('://')[-1].split('@')[0].split(':')
    proxy_username = None
    proxy_password = None

    if '@' in proxy_string:
        proxy_username, proxy_password = proxy_string.split('://')[-1].split('@')[-1].split(':')

    proxy_dict = {
        "scheme": proxy_type,
        "hostname": proxy_host,
        "port": proxy_port,
        "username": proxy_username,
        "password": proxy_password
    }

    return proxy_dict


class Actions:
    @staticmethod
    async def create_sessions(api_id: int,
                              api_hash: str) -> None:
        proxy = None

        session_name = input('Введите название сессии: ')
        use_proxy = input('Использовать Proxy при создании? (y/N): ').lower()

        if use_proxy == 'y':
            proxy_type = input('Введите тип Proxy (http; socks4; socks5): ')
            proxy_host = input('Введите Proxy IP: ')
            proxy_port = int(input('Введите Proxy Port: '))
            proxy_username = input('Введите Proxy User (если установлена авторизация, либо оставьте пустым): ')
            proxy_password = input('Введите Proxy Password (если установлена авторизация, либо оставьте пустым): ')

            if not proxy_username or not proxy_password:
                proxy_username = None
                proxy_password = None

            proxy = {
                "scheme": proxy_type,
                "hostname": proxy_host,
                "port": proxy_port,
                "username": proxy_username,
                "password": proxy_password
            }

        if not await exists('sessions'):
            await mkdir('sessions')

        app = Client(name=session_name,
                     workdir='sessions',
                     api_hash=api_hash,
                     api_id=api_id,
                     proxy=proxy)

        async with app:
            pass

        logger.success(f'Сессия под названием {session_name}.session успешно создана')

    @staticmethod
    async def join_chat(session_name: str,
                        session_proxy_string: str | None,
                        targets: list,
                        api_id: int,
                        api_hash: str) -> None:
        proxy_dict = get_proxy_dict(session_proxy_string)

        app = Client(name=session_name,
                     workdir='sessions',
                     api_hash=api_hash,
                     api_id=api_id,
                     proxy=proxy_dict)

        async with app:
            for i, current_target in enumerate(targets):
                current_target_formatted = type_conversion(content=current_target)

                while True:
                    try:
                        await app.join_chat(chat_id=current_target_formatted)

                    except FloodWait as error:
                        logger.info(f'{session_name} | FloodWait: {error.value} сек.')
                        await asyncio.sleep(error.value)

                    else:
                        logger.success(f'{session_name} | Успешно вступил в чат/канал {current_target} '
                                       f'| [{i + 1}/{len(targets)}]')
                        break

    @staticmethod
    async def send_message(session_name: str,
                           message_text: str | None,
                           message_folder: str | None,
                           message_target: int | str,
                           session_proxy_string: str | None,
                           api_id: int,
                           api_hash: str):
        proxy_dict = get_proxy_dict(session_proxy_string)
        message_target_formatted = type_conversion(content=message_target)

        app = Client(name=session_name,
                     workdir='sessions',
                     api_hash=api_hash,
                     api_id=api_id,
                     proxy=proxy_dict)

        async with app:
            if message_folder:
                if message_folder.split('.')[-1] in ['png',
                                                     'jpg',
                                                     'jpeg']:
                    while True:
                        try:
                            await app.send_photo(chat_id=message_target_formatted,
                                                 photo=message_folder,
                                                 caption=message_text)

                        except FloodWait as error:
                            await asyncio.sleep(error.value)

                        else:
                            logger.success(f'{session_name} | Изображение успешно отправлено')
                            return

                else:
                    while True:
                        try:
                            await app.send_document(chat_id=message_target_formatted,
                                                    document=message_folder,
                                                    caption=message_text)

                        except FloodWait as error:
                            await asyncio.sleep(error.value)

                        else:
                            logger.success(f'{session_name} | Файл успешно отправлен')
                            return

            else:
                while True:
                    try:
                        await app.send_message(chat_id=message_target_formatted,
                                               text=message_text)

                    except FloodWait as error:
                        await asyncio.sleep(error.value)

                    else:
                        logger.success(f'{session_name} | Сообщение успешно отправлено')
                        return

    @staticmethod
    async def click_button(session_name: str,
                           button_target: int | str,
                           button_id: int,
                           session_proxy_string: str | None,
                           api_id: int,
                           api_hash: str):
        proxy_dict = get_proxy_dict(session_proxy_string)
        button_target_formatted = type_conversion(content=button_target)

        app = Client(name=session_name,
                     workdir='sessions',
                     api_hash=api_hash,
                     api_id=api_id,
                     proxy=proxy_dict)

        async with app:
            async for message in app.get_chat_history(button_target_formatted,
                                                      limit=1,
                                                      offset_id=-1):
                while True:
                    try:
                        await message.click(button_id)

                    except FloodWait as error:
                        await asyncio.sleep(error.value)

                    except TimeoutError:
                        logger.info(f'{session_name} | TimeOut при нажатии кнопки (возможно она была успешно нажата)')
                        return

                    else:
                        logger.success(f'{session_name} | Кнопка успешно нажата')
                        return

    @staticmethod
    async def click_start_button(session_name: str,
                                 referral_bot_username: str,
                                 referral_bot_ref_code: str,
                                 session_proxy_string: str | None,
                                 api_id: int,
                                 api_hash: str):
        proxy_dict = get_proxy_dict(session_proxy_string)

        app = Client(name=session_name,
                     workdir='sessions',
                     api_hash=api_hash,
                     api_id=api_id,
                     proxy=proxy_dict)

        async with app:
            while True:
                try:
                    await app.send_message(chat_id=referral_bot_username,
                                           text=f'/start {referral_bot_ref_code}')

                except FloodWait as error:
                    await asyncio.sleep(error.value)

                else:
                    logger.success(f'{session_name} | Команда /start с реф. кодом '
                                   f'{referral_bot_ref_code} успешно отправлена')
                    return
