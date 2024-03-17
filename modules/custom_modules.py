import asyncio
import copy
import random
import aiohttp.client_exceptions
import python_socks

from modules import Logger, RequestClient, Client
from modules.interfaces import SoftwareException, CriticalException
from utils.tools import helper, gas_checker, sleep
from config import (
    TOKENS_PER_CHAIN, LAYERZERO_WRAPED_NETWORKS, CHAIN_NAME, OKX_NETWORKS_NAME, BINGX_NETWORKS_NAME,
    BINANCE_NETWORKS_NAME, CEX_WRAPPED_ID, COINGECKO_TOKEN_API_NAMES, BITGET_NETWORKS_NAME
)
from settings import (
    CEX_BALANCER_CONFIG, OKX_WITHDRAW_DATA, BINANCE_DEPOSIT_DATA,
    BINGX_WITHDRAW_DATA, BINANCE_WITHDRAW_DATA,
    CEX_DEPOSIT_LIMITER, RHINO_CHAIN_ID_FROM, ORBITER_CHAIN_ID_FROM,
    ACROSS_CHAIN_ID_FROM, BRIDGE_AMOUNT_LIMITER, RELAY_CHAIN_ID_FROM, OWLTO_CHAIN_ID_FROM, ACROSS_TOKEN_NAME,
    ORBITER_TOKEN_NAME, OWLTO_TOKEN_NAME, RELAY_TOKEN_NAME, RHINO_TOKEN_NAME, OKX_DEPOSIT_DATA,
    BINGX_DEPOSIT_DATA, BUNGEE_CHAIN_ID_FROM, BUNGEE_TOKEN_NAME, BITGET_DEPOSIT_DATA, BITGET_WITHDRAW_DATA,
    NITRO_CHAIN_ID_FROM, NITRO_TOKEN_NAME, RELAY2_TOKEN_NAME, RELAY2_CHAIN_ID_FROM
)


class Custom(Logger, RequestClient):
    def __init__(self, client: Client):
        self.client = client
        Logger.__init__(self)
        RequestClient.__init__(self, client)

    @helper
    async def balance_average(self):
        from functions import okx_withdraw_util, bingx_withdraw_util, binance_withdraw_util, bitget_withdraw

        self.logger_msg(*self.client.acc_info, msg=f"Start check all balance to make average")

        balancer_data_copy = copy.deepcopy(CEX_BALANCER_CONFIG)

        count = 0
        client = None
        for data in balancer_data_copy:
            while True:
                try:
                    cex_network, wanted_balance, cex_wanted, amount = data

                    func, cex_config = {
                        1: (okx_withdraw_util, OKX_NETWORKS_NAME),
                        2: (bingx_withdraw_util, BINGX_NETWORKS_NAME),
                        3: (binance_withdraw_util, BINGX_NETWORKS_NAME),
                        4: (bitget_withdraw, BITGET_NETWORKS_NAME),
                    }[cex_wanted]

                    dapp_tokens = [f"{cex_config[cex_network].split('-')[0]}{'.e' if cex_network in [29, 30] else ''}"]
                    dapp_chains = [CEX_WRAPPED_ID[cex_network]]

                    client, index, balance, balance_in_wei, balance_data = await self.balance_searcher(
                        chains=dapp_chains, tokens=dapp_tokens, omni_check=False, silent_mode=True
                    )

                    dep_token = dapp_tokens[index]
                    balance_in_usd, token_price = balance_data
                    wanted_amount_in_usd = float(f'{wanted_balance * token_price:.2f}')

                    if wanted_amount_in_usd > balance_in_usd:
                        need_to_withdraw = float(f"{(wanted_amount_in_usd - balance_in_usd) / token_price:.6f}")

                        self.logger_msg(
                            *self.client.acc_info, msg=f"Not enough balance on account, launch CEX withdraw module"
                        )

                        await func(client, withdraw_data=(cex_network, (need_to_withdraw, need_to_withdraw)))
                    else:
                        self.logger_msg(
                            *self.client.acc_info, msg=f"Account have enough {dep_token} balance", type_msg='success'
                        )
                        return True
                except Exception as error:
                    count += 1
                    if count == 3:
                        raise SoftwareException(f"Exception: {error}")
                    self.logger_msg(*self.client.acc_info, msg=f"Exception: {error}", type_msg='error')
                finally:
                    if client:
                        await client.session.close()
        return True

    async def balance_searcher(
            self, chains, tokens=None, omni_check:bool = True, native_check:bool = False, silent_mode:bool = False
    ):
        index = 0
        clients = []
        while True:
            try:
                clients = [await self.client.new_client(LAYERZERO_WRAPED_NETWORKS[chain] if omni_check else chain)
                           for chain in chains]

                if native_check:
                    tokens = [client.token for client in clients]

                balances = [await client.get_token_balance(token_name=token) for client, token in zip(clients, tokens)]

                if all(balance_in_wei == 0 for balance_in_wei, _, _ in balances):
                    raise SoftwareException('Insufficient balances in all networks!')

                balances_in_usd = []
                for balance_in_wei, balance, token_name in balances:
                    token_price = 1
                    if 'USD' not in token_name:
                        token_price = await self.client.get_token_price(COINGECKO_TOKEN_API_NAMES[token_name])
                    balance_in_usd = balance * token_price
                    balances_in_usd.append([balance_in_usd, token_price])

                index = balances_in_usd.index(max(balances_in_usd, key=lambda x: x[0]))

                for index_client, client in enumerate(clients):
                    if index_client != index:
                        await client.session.close()

                if not silent_mode:
                    self.logger_msg(
                        *self.client.acc_info,
                        msg=f"Detected {round(balances[index][1], 5)} {tokens[index]} in {clients[index].network.name}",
                        type_msg='success'
                    )

                return clients[index], index, balances[index][1], balances[index][0], balances_in_usd[index]

            except (aiohttp.client_exceptions.ClientProxyConnectionError, asyncio.exceptions.TimeoutError,
                    aiohttp.client_exceptions.ClientHttpProxyError, python_socks.ProxyError):
                self.logger_msg(
                    *self.client.acc_info,
                    msg=f"Connection to RPC is not stable. Will try again in 1 min...",
                    type_msg='warning'
                )
                await asyncio.sleep(60)
            except Exception as error:
                self.logger_msg(
                    *self.client.acc_info,
                    msg=f"Bad response from RPC. Will try again in 1 min... Error: {error}", type_msg='warning'
                )
                await asyncio.sleep(60)
            finally:
                for index_client, client in enumerate(clients):
                    if index_client != index:
                        await client.session.close()

    @helper
    async def smart_cex_withdraw(self, dapp_id:int):
        while True:
            try:
                from functions import okx_withdraw_util, bingx_withdraw_util, binance_withdraw_util, bitget_withdraw_util

                func, withdraw_data = {
                    1: (okx_withdraw_util, OKX_WITHDRAW_DATA),
                    2: (bingx_withdraw_util, BINGX_WITHDRAW_DATA),
                    3: (binance_withdraw_util, BINANCE_WITHDRAW_DATA),
                    4: (bitget_withdraw_util, BITGET_WITHDRAW_DATA)
                }[dapp_id]

                withdraw_data_copy = copy.deepcopy(withdraw_data)

                random.shuffle(withdraw_data_copy)
                result_list = []

                for index, data in enumerate(withdraw_data_copy, 1):
                    current_data = data
                    if isinstance(data[0], list):
                        current_data = random.choice(data)
                        if not current_data:
                            continue

                    network, amount = current_data

                    if isinstance(amount[0], str):
                        amount = f"{round(random.uniform(float(amount[0]), float(amount[1])), 6) / 100}"

                    result_list.append(await func(self.client, withdraw_data=(network, amount)))

                    if index != len(withdraw_data_copy):
                        await sleep(self)

                return all(result_list)
            except CriticalException as error:
                raise error
            except Exception as error:
                self.logger_msg(self.client.account_name, None, msg=f'{error}', type_msg='error')
                msg = f"Software cannot continue, awaiting operator's action. Will try again in 1 min..."
                self.logger_msg(self.client.account_name, None, msg=msg, type_msg='warning')
                await asyncio.sleep(60)

    @helper
    @gas_checker
    async def smart_cex_deposit(self, dapp_id:int):
        from functions import cex_deposit_util

        class_id, deposit_data, cex_config = {
            1: (1, OKX_DEPOSIT_DATA, OKX_NETWORKS_NAME),
            2: (2, BINGX_DEPOSIT_DATA, BINGX_NETWORKS_NAME),
            3: (3, BINANCE_DEPOSIT_DATA, BINANCE_NETWORKS_NAME),
            4: (4, BITGET_DEPOSIT_DATA, BITGET_NETWORKS_NAME),
        }[dapp_id]

        deposit_data_copy = copy.deepcopy(deposit_data)

        client = None
        result_list = []
        for data in deposit_data_copy:
            while True:
                try:
                    current_data = data
                    if isinstance(data[0], list):
                        current_data = random.choice(data)
                        if not current_data:
                            continue

                    networks, amount = current_data
                    if isinstance(networks, tuple):
                        dapp_tokens = [f"{cex_config[network].split('-')[0]}{'.e' if network in [29, 30] else ''}"
                                       for network in networks]
                        dapp_chains = [CEX_WRAPPED_ID[chain] for chain in networks]
                    else:
                        dapp_tokens = [f"{cex_config[networks].split('-')[0]}{'.e' if networks in [29, 30] else ''}"]
                        dapp_chains = [CEX_WRAPPED_ID[networks]]

                    client, chain_index, balance, _, balance_data = await self.balance_searcher(
                        chains=dapp_chains, tokens=dapp_tokens, omni_check=False,
                    )

                    balance_in_usd, token_price = balance_data
                    dep_token = dapp_tokens[chain_index]

                    dep_network = networks if isinstance(networks, int) else networks[chain_index]
                    limit_amount, wanted_to_hold_amount = CEX_DEPOSIT_LIMITER
                    min_wanted_amount, max_wanted_amount = min(wanted_to_hold_amount), max(wanted_to_hold_amount)

                    if balance_in_usd >= limit_amount:

                        dep_amount = await client.get_smart_amount(amount, token_name=dep_token)
                        deposit_fee = await client.simulate_transfer(token_name=dep_token)
                        min_hold_balance = random.uniform(min_wanted_amount, max_wanted_amount) / token_price

                        if dep_token == client.token:
                            dep_amount = dep_amount - deposit_fee

                        if balance - dep_amount < 0:
                            raise SoftwareException('Account balance - deposit fee < 0')

                        if balance - dep_amount < min_hold_balance:
                            need_to_freeze_amount = min_hold_balance - (balance - dep_amount)
                            dep_amount = dep_amount - need_to_freeze_amount

                        if dep_amount < 0:
                            raise CriticalException(
                                f'Set CEX_DEPOSIT_LIMITER[2 value] lower than {wanted_to_hold_amount}. '
                                f'Current amount = {dep_amount:.4f} {dep_token}')

                        dep_amount_in_usd = dep_amount * token_price * 0.99

                        if balance_in_usd >= dep_amount_in_usd:

                            deposit_data = dep_network, round(dep_amount, 6)

                            if len(deposit_data_copy) == 1:
                                return await cex_deposit_util(client, dapp_id=class_id, deposit_data=deposit_data)
                            else:
                                result_list.append(
                                    await cex_deposit_util(client, dapp_id=class_id, deposit_data=deposit_data)
                                )
                                break

                        info = f"{balance_in_usd:.2f}$ < {dep_amount_in_usd:.2f}$"
                        raise CriticalException(f'Account {dep_token} balance < wanted deposit amount: {info}')

                    info = f"{balance_in_usd:.2f}$ < {limit_amount:.2f}$"
                    raise CriticalException(f'Account {dep_token} balance < wanted limit amount: {info}')

                except CriticalException as error:
                    raise error
                except Exception as error:
                    self.logger_msg(self.client.account_name, None, msg=f'{error}', type_msg='error')
                    msg = f"Software cannot continue, awaiting operator's action. Will try again in 1 min..."
                    self.logger_msg(self.client.account_name, None, msg=msg, type_msg='warning')
                    await asyncio.sleep(60)
                finally:
                    if client:
                        await client.session.close()

        return all(result_list)

    @helper
    @gas_checker
    async def smart_bridge(self, dapp_id:int = None):
        client = None
        while True:
            try:
                from functions import bridge_utils

                bridge_app_id, dapp_chains, dapp_tokens = {
                    1: (1, ACROSS_CHAIN_ID_FROM, ACROSS_TOKEN_NAME),
                    2: (2, BUNGEE_CHAIN_ID_FROM, BUNGEE_TOKEN_NAME),
                    3: (3, RELAY2_CHAIN_ID_FROM, RELAY2_TOKEN_NAME),
                    4: (4, NITRO_CHAIN_ID_FROM, NITRO_TOKEN_NAME),
                    5: (5, ORBITER_CHAIN_ID_FROM, ORBITER_TOKEN_NAME),
                    6: (6, OWLTO_CHAIN_ID_FROM, OWLTO_TOKEN_NAME),
                    7: (7, RELAY_CHAIN_ID_FROM, RELAY_TOKEN_NAME),
                    8: (8, RHINO_CHAIN_ID_FROM, RHINO_TOKEN_NAME),
                }[dapp_id]

                if len(dapp_tokens) == 2:
                    from_token_name, to_token_name = dapp_tokens
                else:
                    from_token_name, to_token_name = dapp_tokens, dapp_tokens

                dapp_tokens = [from_token_name for _ in dapp_chains]

                client, chain_index, balance, _, balance_data = await self.balance_searcher(
                    chains=dapp_chains, tokens=dapp_tokens, omni_check=False
                )

                fee_client = await client.new_client(dapp_chains[chain_index])
                chain_from_id, token_name = dapp_chains[chain_index], from_token_name

                source_chain_name, destination_chain, amount, dst_chain_id = await client.get_bridge_data(
                    chain_from_id=chain_from_id, dapp_id=bridge_app_id
                )

                from_chain_name = client.network.name
                to_chain_name = CHAIN_NAME[dst_chain_id]
                from_token_addr = TOKENS_PER_CHAIN[from_chain_name][from_token_name]
                to_token_addr = TOKENS_PER_CHAIN[to_chain_name][to_token_name]

                balance_in_usd, token_price = balance_data
                limit_amount, wanted_to_hold_amount = BRIDGE_AMOUNT_LIMITER
                min_wanted_amount, max_wanted_amount = min(wanted_to_hold_amount), max(wanted_to_hold_amount)
                fee_bridge_data = (source_chain_name, destination_chain, amount, dst_chain_id,
                                   from_token_name, to_token_name, from_token_addr, to_token_addr)

                if balance_in_usd >= limit_amount:
                    bridge_fee = await bridge_utils(
                        fee_client, bridge_app_id, chain_from_id, fee_bridge_data, need_fee=True)
                    min_hold_balance = random.uniform(min_wanted_amount, max_wanted_amount) / token_price
                    if balance - bridge_fee - min_hold_balance > 0:
                        if amount > bridge_fee:
                            bridge_amount = round(amount - bridge_fee, 6)
                        else:
                            bridge_amount = amount
                        if balance - bridge_amount < min_hold_balance:
                            need_to_freeze_amount = min_hold_balance - (balance - bridge_amount)
                            bridge_amount = round(bridge_amount - need_to_freeze_amount, 6)

                        if bridge_amount < 0:
                            raise CriticalException(
                                f'Set BRIDGE_AMOUNT_LIMITER[2 value] lower than {wanted_to_hold_amount}. '
                                f'Current amount = {bridge_amount} {from_token_name}')

                        bridge_amount_in_usd = bridge_amount * token_price

                        bridge_data = (source_chain_name, destination_chain, bridge_amount, dst_chain_id,
                                       from_token_name, to_token_name, from_token_addr, to_token_addr)

                        if balance_in_usd >= bridge_amount_in_usd:

                            return await bridge_utils(client, bridge_app_id, chain_from_id, bridge_data)

                        info = f"{balance_in_usd:.2f}$ < {bridge_amount_in_usd:.2f}$"
                        raise CriticalException(f'Account {token_name} balance < wanted bridge amount: {info}')

                    full_need_amount = round(bridge_fee + min_hold_balance, 6)
                    info = f"{balance:.2f} {token_name} < {full_need_amount:.2f} {token_name}"
                    raise CriticalException(f'Account {token_name} balance < bridge fee + hold amount: {info}')

                info = f"{balance_in_usd:.2f}$ < {limit_amount:.2f}$"
                raise CriticalException(f'Account {token_name} balance < wanted limit amount: {info}')

            except CriticalException as error:
                raise error
            except Exception as error:
                self.logger_msg(self.client.account_name, None, msg=f'{error}', type_msg='error')
                msg = f"Software cannot continue, awaiting operator's action. Will try again in 1 min..."
                self.logger_msg(self.client.account_name, None, msg=msg, type_msg='warning')
                await asyncio.sleep(60)
            finally:
                if client:
                    await client.session.close()
