import os
import json

from utils.tools import clean_progress_file
from functions import *
from config import ACCOUNT_NAMES
from modules import Logger
from modules.interfaces import SoftwareException
from general_settings import SHUFFLE_ROUTE
from settings import (CLASSIC_ROUTES_MODULES_USING)

GSHEET_CONFIG = "./data/services/service_account.json"
os.environ["GSPREAD_SILENCE_WARNINGS"] = "1"


AVAILABLE_MODULES_INFO = {
    # module_name                       : (module name, priority, tg info, can be help module, supported network)
    okx_withdraw                        : (okx_withdraw, -3, 'OKX withdraw', 0, []),
    bingx_withdraw                      : (bingx_withdraw, -3, 'BingX withdraw', 0, []),
    binance_withdraw                    : (binance_withdraw, -3, 'Binance withdraw', 0, []),
    bitget_withdraw                     : (bitget_withdraw, -3, 'Bitget withdraw', 0, []),
    make_balance_to_average             : (make_balance_to_average, -2, 'Check and make wanted balance', 0, []),
    bridge_rhino                        : (bridge_rhino, 1, 'Rhino bridge', 0, [2, 3, 4, 8, 9, 11, 12]),
    bridge_relay2                       : (bridge_relay2, 1, 'Relay2 bridge', 0, [2, 3, 4, 8, 9, 11, 12]),
    bridge_orbiter                      : (bridge_orbiter, 1, 'Orbiter bridge', 0, [2, 3, 4, 8, 9, 11, 12]),
    bridge_across                       : (bridge_across, 1, 'Across bridge', 0, [2, 3, 11, 12]),
    bridge_bungee                       : (bridge_bungee, 1, 'Bungee bridge', 0, [2, 3, 11, 12]),
    bridge_owlto                        : (bridge_owlto, 1, 'Owlto bridge', 0, [2, 3, 11, 12]),
    bridge_relay                        : (bridge_relay, 1, 'Relay bridge', 0, [2, 3, 11, 12]),
    bridge_nitro                        : (bridge_nitro, 1, 'Nitro bridge', 0, [2, 3, 11, 12]),
    bridge_native                       : (bridge_native, 1, 'Native bridge', 0, [2, 3, 4, 8, 9, 11, 12]),
    bridge_zora                         : (bridge_zora, 1, 'Zora instant bridge', 0, [2, 3, 4, 8, 9, 11, 12]),
    withdraw_txsync                     : (withdraw_txsync, 1, 'Withdraw txSync', 0, [2, 3, 4, 8, 9, 11, 12]),
    swap_izumi                          : (swap_izumi, 2, 'iZumi swap', 1, [3, 4, 8, 11]),
    swap_odos                           : (swap_odos, 2, 'ODOS swap', 1, [3, 11]),
    swap_oneinch                        : (swap_oneinch, 2, '1inch swap', 1, [3, 11]),
    swap_uniswap                        : (swap_uniswap, 2, 'Uniswap swap', 1, [3]),
    mint_mintfun                        : (mint_mintfun, 2, 'Mint NFT on mint.fun', 1, [3]),
    wrap_eth                            : (wrap_eth, 2, 'Wrap ETH', 0, []),
    unwrap_eth                          : (unwrap_eth, 2, 'Unwrap ETH', 0, []),
    random_approve                      : (random_approve, 2, 'Random approve', 0, []),
    refuel_bungee                       : (refuel_bungee, 3, 'Bungee refuel', 0, []),
    bingx_transfer                      : (bingx_transfer, 2, 'BingX transfer', 0, []),
    transfer_eth                        : (transfer_eth, 2, 'Transfer ETH', 0, []),
    transfer_eth_to_myself              : (transfer_eth_to_myself, 2, 'Transfer ETH to myself', 0, []),
    okx_deposit                         : (okx_deposit, 5, 'OKX deposit', 0, []),
    bingx_deposit                       : (bingx_deposit, 5, 'Bingx deposit', 0, []),
    binance_deposit                     : (binance_deposit, 5, 'Binance deposit', 0, []),
    bitget_deposit                      : (bitget_deposit, 5, 'BitGet deposit', 0, []),
}


def get_func_by_name(module_name, help_message:bool = False):
    for k, v in AVAILABLE_MODULES_INFO.items():
        if k.__name__ == module_name:
            if help_message:
                return v[2]
            return v[0]


class RouteGenerator(Logger):
    def __init__(self, silent:bool = True):
        Logger.__init__(self)
        self.modules_names_const = [module.__name__ for module in list(AVAILABLE_MODULES_INFO.keys())]

    @staticmethod
    def classic_generate_route():
        route = []
        for i in CLASSIC_ROUTES_MODULES_USING:
            module_name = random.choice(i)
            if module_name is None:
                continue
            module = get_func_by_name(module_name)
            if module:
                route.append(module.__name__)
            else:
                raise SoftwareException(f'There is no module with the name "{module_name}" in the software.')
        return route

    @staticmethod
    def sort_classic_route(route):
        modules_dependents = {
            'okx_withdraw': 0,
            'bingx_withdraw': 0,
            'binance_withdraw': 0,
            'make_balance_to_average': 1,
            'bridge_rhino': 1,
            'bridge_layerswap': 1,
            'bridge_nitro': 1,
            'bridge_orbiter': 1,
            'bridge_across': 1,
            'bridge_owlto': 1,
            'bridge_relay': 1,
            'bridge_native': 1,
            'bridge_zora': 1,
            'okx_deposit': 4,
            'bingx_deposit': 4,
            'binance_deposit': 4,
        }

        new_route = []
        classic_route = []
        for module_name in route:
            if module_name in modules_dependents:
                classic_route.append((module_name, modules_dependents[module_name]))
            else:
                new_route.append((module_name, 2))

        random.shuffle(new_route)
        classic_route.extend(new_route)
        route_with_priority = [module[0] for module in sorted(classic_route, key=lambda x: x[1])]

        return route_with_priority

    def classic_routes_json_save(self):
        clean_progress_file()
        with open('./data/services/wallets_progress.json', 'w') as file:
            accounts_data = {}
            for account_name in ACCOUNT_NAMES:
                if isinstance(account_name, (str, int)):
                    classic_route = self.classic_generate_route()
                    if SHUFFLE_ROUTE:
                        classic_route = self.sort_classic_route(route=classic_route)
                    account_data = {
                        "current_step": 0,
                        "route": classic_route
                    }
                    accounts_data[str(account_name)] = account_data
            json.dump(accounts_data, file, indent=4)
        self.logger_msg(
            None, None,
            f'Successfully generated {len(accounts_data)} classic routes in data/services/wallets_progress.json\n',
            'success')

    def smart_routes_json_save(self, account_name:str, route:list):
        progress_file_path = './data/services/wallets_progress.json'

        try:
            with open(progress_file_path, 'r+') as file:
                data = json.load(file)
        except json.JSONDecodeError:
            data = {}

        data[account_name] = {
            "current_step": 0,
            "route": ([" ".join(item) for item in route] if isinstance(route[0], tuple) else route) if route else []
        }

        with open(progress_file_path, 'w') as file:
            json.dump(data, file, indent=4)

        self.logger_msg(
            None, None,
            f'Successfully generated smart routes for {account_name}', 'success')
