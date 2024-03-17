import asyncio
import os
import random

import pandas as pd
from aiohttp import ClientSession

from termcolor import cprint
from web3 import AsyncWeb3, AsyncHTTPProvider
from prettytable import PrettyTable
from config import PRIVATE_KEYS, PROXIES
from utils.networks import EthereumRPC

from modules.interfaces import get_user_agent, SoftwareException


FILTER_SYMBOLS = ['ETH']
FIELDS = [
    '#', 'Wallet', 'Balance', 'ETH', 'TX Count'
]

table = PrettyTable()
table.field_names = FIELDS


class TxChecker:
    async def make_request(self, method: str = 'GET', url: str = None, headers: dict = None, params: dict = None,
                           data: str = None, json: dict = None):

        proxy = random.choice(PROXIES)
        headers = (headers or {}) | {'User-Agent': get_user_agent()}

        async with ClientSession() as session:
            async with session.request(method=method, url=url, headers=headers, data=data,
                                       params=params, json=json, proxy=f"http://{proxy}" if proxy else "") as response:
                data = await response.json()
                if response.status == 200:
                    return data
                await self.make_request(method=method, url=url, headers=headers, data=data, params=params, json=json)

    async def get_eth_price(self):
        url = 'https://api.coingecko.com/api/v3/simple/price'

        params = {
            'ids': 'ethereum',
            'vs_currencies': 'usd'
        }

        return (await self.make_request('GET', url=url, params=params))['ethereum']['usd']

    @staticmethod
    async def get_wallet_balance(wallet):
        proxy = random.choice(PROXIES)
        request_kwargs = {"proxy": f"http://{proxy}"} if proxy else {}
        rpc = random.choice(EthereumRPC.rpc)
        w3 = AsyncWeb3(AsyncHTTPProvider(rpc, request_kwargs=request_kwargs))
        balance_in_wei = await w3.eth.get_balance(wallet)
        balance = round(balance_in_wei / 10 ** 18, 5)
        tx_count = await w3.eth.get_transaction_count(wallet)

        return balance, tx_count

    async def fetch_wallet_data(self, wallet, index, eth_price):
        balance, tx_count = await self.get_wallet_balance(wallet)

        return {
            '#'                     : index + 1,
            'Wallet'                : f'{wallet}',
            'Balance'               : f'{(balance * eth_price):.2f}$',
            'ETH'                   : f"{balance:.4f}",
            'TX Count'              : tx_count,
        }


async def main():
        try:
            wallets = [AsyncWeb3().eth.account.from_key(private_key).address for private_key in PRIVATE_KEYS]
        except Exception as error:
            cprint('\n⚠️⚠️⚠️Put your wallets into data/accounts_data.xlsx first!⚠️⚠️⚠️\n', color='light_red', attrs=["blink"])
            raise SoftwareException(f"{error}")

        tx_checker = TxChecker()

        eth_price = await tx_checker.get_eth_price()
        tasks = [tx_checker.fetch_wallet_data(wallet, index, eth_price) for index, wallet in enumerate(wallets, 0)]
        wallet_data = await asyncio.gather(*tasks)

        cprint('✅ Data successfully load to /data/accounts_stats/wallets_stats.xlsx (Excel format)\n',
               'light_yellow', attrs=["blink"])
        await asyncio.sleep(1)
        xlsx_data = pd.DataFrame(wallet_data)
        directory = './data/accounts_stats/'
        if not os.path.exists(directory):
            os.makedirs(directory)
        xlsx_data.to_excel('./data/accounts_stats/wallets_stats.xlsx', index=False)

        [table.add_row(data.values()) for data in wallet_data]

        print(table)
