import re
import json
import random
import asyncio
import traceback

import aiohttp
import python_socks
import telebot

from modules import Logger
from aiohttp import ClientSession
from utils.networks import EthereumRPC
from web3 import AsyncWeb3, AsyncHTTPProvider
from functions import get_network_by_chain_id
from modules.interfaces import SoftwareException, CriticalException
from config import ACCOUNT_NAMES, PRIVATE_KEYS, PROXIES, CHAIN_NAME
from utils.route_generator import AVAILABLE_MODULES_INFO, get_func_by_name
from utils.tools import clean_gwei_file
from general_settings import (USE_PROXY, SLEEP_MODE, SLEEP_TIME_MODULES, SOFTWARE_MODE, TG_ID, TG_TOKEN, MOBILE_PROXY,
                              MOBILE_PROXY_URL_CHANGER, WALLETS_TO_WORK, TELEGRAM_NOTIFICATIONS,
                              SAVE_PROGRESS, ACCOUNTS_IN_STREAM, SLEEP_TIME_ACCOUNTS, SHUFFLE_WALLETS, BREAK_ROUTE,
                              STOP_SOFTWARE)


class Runner(Logger):
    @staticmethod
    def get_wallets_batch(account_list: tuple = None):
        range_count = range(account_list[0], account_list[1])
        account_names = [ACCOUNT_NAMES[i - 1] for i in range_count]
        accounts = [PRIVATE_KEYS[i - 1] for i in range_count]
        return zip(account_names, accounts)

    @staticmethod
    def get_wallets():
        if WALLETS_TO_WORK == 0:
            accounts_data = zip(ACCOUNT_NAMES, PRIVATE_KEYS)

        elif isinstance(WALLETS_TO_WORK, int):
            accounts_data = zip([ACCOUNT_NAMES[WALLETS_TO_WORK - 1]], [PRIVATE_KEYS[WALLETS_TO_WORK - 1]])

        elif isinstance(WALLETS_TO_WORK, tuple):
            account_names = [ACCOUNT_NAMES[i - 1] for i in WALLETS_TO_WORK]
            accounts = [PRIVATE_KEYS[i - 1] for i in WALLETS_TO_WORK]
            accounts_data = zip(account_names, accounts)

        elif isinstance(WALLETS_TO_WORK, list):
            range_count = range(WALLETS_TO_WORK[0], WALLETS_TO_WORK[1] + 1)
            account_names = [ACCOUNT_NAMES[i - 1] for i in range_count]
            accounts = [PRIVATE_KEYS[i - 1] for i in range_count]
            accounts_data = zip(account_names, accounts)
        else:
            accounts_data = []

        accounts_data = list(accounts_data)

        if SHUFFLE_WALLETS:
            random.shuffle(accounts_data)

        return accounts_data

    @staticmethod
    async def make_request(method: str = 'GET', url: str = None, headers: dict = None):

        async with ClientSession() as session:
            async with session.request(method=method, url=url, headers=headers) as response:
                if response.status == 200:
                    return True
                return False

    @staticmethod
    def load_routes():
        with open('./data/services/wallets_progress.json', 'r') as f:
            return json.load(f)

    async def smart_sleep(self, account_name, account_number, accounts_delay=False):
        if SLEEP_MODE and account_number:
            if accounts_delay:
                duration = random.randint(*tuple(x * account_number for x in SLEEP_TIME_ACCOUNTS))
            else:
                duration = random.randint(*SLEEP_TIME_MODULES)
            self.logger_msg(account_name, None, f"💤 Sleeping for {duration} seconds\n")
            await asyncio.sleep(duration)

    async def send_tg_message(self, account_name, message_to_send, disable_notification=False):
        try:
            await asyncio.sleep(1)
            str_send = '*' + '\n'.join([re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', message)
                                       for message in message_to_send]) + '*'
            bot = telebot.TeleBot(TG_TOKEN)
            bot.send_message(TG_ID, str_send, parse_mode='MarkdownV2', disable_notification=disable_notification)
            print()
            self.logger_msg(account_name, None, f"Telegram message sent", 'success')
        except Exception as error:
            self.logger_msg(account_name, None, f"Telegram | API Error: {error}", 'error')

    def update_step(self, account_name, step):
        wallets = self.load_routes()
        wallets[str(account_name)]["current_step"] = step
        with open('./data/services/wallets_progress.json', 'w') as f:
            json.dump(wallets, f, indent=4)

    @staticmethod
    def collect_bad_wallets(account_name, module_name):
        try:
            with open('./data/bad_wallets.json', 'r') as file:
                data = json.load(file)
        except (FileNotFoundError, json.JSONDecodeError):
            data = {}

        data.setdefault(str(account_name), []).append(module_name)

        with open('./data/bad_wallets.json', 'w') as file:
            json.dump(data, file, indent=4)

    async def change_ip_proxy(self):
        for index, proxy_url in enumerate(MOBILE_PROXY_URL_CHANGER, 1):
            while True:
                try:
                    self.logger_msg(None, None, f'Trying to change IP №{index} address\n', 'info')

                    await self.make_request(url=proxy_url)

                    self.logger_msg(None, None, f'IP №{index} address changed!\n', 'success')
                    await asyncio.sleep(5)
                    break

                except Exception as error:
                    self.logger_msg(None, None, f'Bad URL for change IP №{index}. Error: {error}', 'error')
                    await asyncio.sleep(15)

    async def check_proxies_status(self):
        tasks = []
        for proxy in PROXIES:
            tasks.append(self.check_proxy_status(None, proxy=proxy))
        await asyncio.gather(*tasks)

    async def check_proxy_status(self, account_name: str = None, proxy: str = None, silence: bool = False):
        try:
            w3 = AsyncWeb3(AsyncHTTPProvider(random.choice(EthereumRPC.rpc),
                                             request_kwargs={"proxy": f"http://{proxy}"}))
            if await w3.is_connected():
                if not silence:
                    info = f'Proxy {proxy[proxy.find("@"):]} successfully connected to Ethereum RPC'
                    self.logger_msg(account_name, None, info, 'success')
                return True
            self.logger_msg(account_name, None, f"Proxy: {proxy} can`t connect to Ethereum RPC", 'error')
            return False
        except Exception as error:
            self.logger_msg(account_name, None, f"Bad proxy: {proxy} | Error: {error}", 'error')
            return False

    def get_proxy_for_account(self, account_name):
        if USE_PROXY:
            try:
                account_number = ACCOUNT_NAMES.index(account_name)
                num_proxies = len(PROXIES)
                return PROXIES[account_number % num_proxies]
            except Exception as error:
                self.logger_msg(account_name, None, f"Bad data in proxy, but you want proxy! Error: {error}", 'error')
                raise SoftwareException("Proxy error")

    async def run_account_modules(
            self, account_name:str, private_key:str, network, proxy:str | None, index:int, parallel_mode: bool = False
    ):
        message_list, result_list, used_modules, route_paths, break_flag, module_counter = [], [], [], [], False, 0
        try:
            route_data = self.load_routes().get(str(account_name), {}).get('route', [])
            route_modules = [[i.split()[0], 0] for i in route_data]

            current_step = 0
            used_modules.extend(route_modules)

            if SAVE_PROGRESS:
                current_step = self.load_routes()[str(account_name)]["current_step"]

            module_info = AVAILABLE_MODULES_INFO
            info = CHAIN_NAME[13]

            message_list.append(
                f'⚔️ {info} | Account name: "{account_name}"\n \n{len(route_modules)} module(s) in route\n')

            if current_step >= len(route_modules):
                self.logger_msg(
                    account_name, None, f"All modules were completed", type_msg='warning')
                return False

            while current_step < len(route_modules):
                module_counter += 1
                module_name = route_modules[current_step][0]
                module_func = get_func_by_name(module_name)
                module_name_tg = AVAILABLE_MODULES_INFO[module_func][2]

                if parallel_mode and module_counter == 1:
                    await self.smart_sleep(account_name, index, accounts_delay=True)

                self.logger_msg(account_name, None, f"🚀 Launch module: {module_info[module_func][2]}\n")

                module_input_data = [account_name, private_key, network, proxy]

                result = False
                while True:
                    try:
                        result = await module_func(*module_input_data)
                        break
                    except KeyError as error:
                        msg = f"Setting '{error}' for this module is not exist in software!"
                        self.logger_msg(account_name, None, msg=msg, type_msg='error')
                        result = False
                        break

                    except (aiohttp.client_exceptions.ClientProxyConnectionError, asyncio.exceptions.TimeoutError,
                            aiohttp.client_exceptions.ClientHttpProxyError, python_socks.ProxyError):
                        self.logger_msg(
                            account_name, None,
                            msg=f"Connection to RPC is not stable. Will try again in 1 min...",
                            type_msg='warning'
                        )
                        await asyncio.sleep(60)
                        continue

                    except CriticalException as error:
                        if not STOP_SOFTWARE:
                            self.logger_msg(account_name, None, msg=f"{error}", type_msg='error')
                            result = False
                            break
                        raise error
                    except Exception as error:
                        info = f"Module name: {module_info[module_func][2]} | Error {error}"
                        self.logger_msg(
                            account_name, None, f"Module crashed during the route: {info}", type_msg='error')
                        traceback.print_exc()
                        result = False
                        break

                if result:
                    self.update_step(account_name, current_step + 1)
                    if not (current_step + 2) > (len(route_modules)):
                        await self.smart_sleep(account_name, account_number=1)
                else:
                    self.collect_bad_wallets(account_name, module_name)
                    result = False
                    if BREAK_ROUTE:
                        message_list.extend([f'❌   {module_name_tg}\n', f'💀   The route was stopped!\n'])
                        account_progress = (False, module_name, account_name)
                        result_list.append(account_progress)
                        break

                current_step += 1
                message_list.append(f'{"✅" if result else "❌"}   {module_name_tg}\n')
                account_progress = (result, module_name, account_name)
                result_list.append(account_progress)

            success_count = len([1 for i in result_list if i[0]])
            errors_count = len(result_list) - success_count
            message_list.append(f'Total result:    ✅   —   {success_count}    |    ❌   —   {errors_count}')

            if TELEGRAM_NOTIFICATIONS:
                if errors_count > 0:
                    disable_notification = False
                else:
                    disable_notification = True
                await self.send_tg_message(account_name, message_to_send=message_list,
                                           disable_notification=disable_notification)

            if not SOFTWARE_MODE:
                self.logger_msg(None, None, f"Start running next wallet!\n", 'info')
            else:
                self.logger_msg(account_name, None, f"Wait for other wallets in stream!\n", 'info')

            return True
        except CriticalException as error:
            raise error
        except Exception as error:
            self.logger_msg(account_name, None, f"Error during the route! Error: {error}\n", 'error')
            traceback.print_exc()

    async def run_parallel(self):
        selected_wallets = list(self.get_wallets())
        num_accounts = len(selected_wallets)
        accounts_per_stream = ACCOUNTS_IN_STREAM
        num_streams, remainder = divmod(num_accounts, accounts_per_stream)

        for stream_index in range(num_streams + (remainder > 0)):
            start_index = stream_index * accounts_per_stream
            end_index = (stream_index + 1) * accounts_per_stream if stream_index < num_streams else num_accounts

            accounts = selected_wallets[start_index:end_index]

            tasks = []

            for index, data in enumerate(accounts):
                account_name, private_key = data
                tasks.append(asyncio.create_task(
                    self.run_account_modules(
                        account_name, private_key, get_network_by_chain_id(13),
                        self.get_proxy_for_account(account_name), index, parallel_mode=True)))

            result_list = await asyncio.gather(*tasks, return_exceptions=True)

            for result in result_list:
                if isinstance(result, Exception):
                    raise result

            if MOBILE_PROXY:
                await self.change_ip_proxy()

            self.logger_msg(None, None, f"Wallets in stream completed their tasks, launching next stream\n", 'success')

        self.logger_msg(None, None, f"All wallets completed their tasks!\n", 'success')

    async def run_consistently(self):

        accounts_data = self.get_wallets()

        for account_name, private_key in accounts_data:

            result = await self.run_account_modules(account_name, private_key, get_network_by_chain_id(13),
                                                    self.get_proxy_for_account(account_name), index=1)

            if len(accounts_data) > 1 and result:
                await self.smart_sleep(account_name, account_number=1, accounts_delay=True)

            if MOBILE_PROXY:
                await self.change_ip_proxy()

        self.logger_msg(None, None, f"All accounts completed their tasks!\n",
                        'success')

    async def run_accounts(self):
        clean_gwei_file()

        try:
            if SOFTWARE_MODE:
                await self.run_parallel()
            else:
                await self.run_consistently()
        except SoftwareException as error:
            self.logger_msg(None, None, msg=error, type_msg='error')
        except Exception as error:
            self.logger_msg(None, None, msg=error, type_msg='error')
            if not isinstance(error, CriticalException):
                traceback.print_exc()
