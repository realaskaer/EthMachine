import random

from modules import *
from utils.networks import *
from config import LAYERZERO_WRAPED_NETWORKS
from settings import (SRC_CHAIN_BUNGEE, NATIVE_CHAIN_ID_FROM, NATIVE_CHAIN_ID_TO)


def get_client(account_name, private_key, network, proxy) -> Client:
    return Client(account_name, private_key, network, proxy)


def get_interface_by_chain_id(chain_id):
    return {
        2: ArbitrumNova,
        3: Base,
        4: Linea,
        8: Scroll,
        11: ZkSync,
        12: Zora,
        13: Ethereum,
    }[chain_id]


def get_network_by_chain_id(chain_id):
    return {
        0: ArbitrumRPC,
        1: ArbitrumRPC,
        2: Arbitrum_novaRPC,
        3: BaseRPC,
        4: LineaRPC,
        5: MantaRPC,
        6: PolygonRPC,
        7: OptimismRPC,
        8: ScrollRPC,
        # 9: StarknetRPC,
        10: Polygon_ZKEVM_RPC,
        11: zkSyncEraRPC,
        12: ZoraRPC,
        13: EthereumRPC,
        14: AvalancheRPC,
        15: BSC_RPC,
        16: MoonbeamRPC,
        17: HarmonyRPC,
        18: TelosRPC,
        19: CeloRPC,
        20: GnosisRPC,
        21: CoreRPC,
        22: TomoChainRPC,
        23: ConfluxRPC,
        24: OrderlyRPC,
        25: HorizenRPC,
        26: MetisRPC,
        27: AstarRPC,
        28: OpBNB_RPC,
        29: MantleRPC,
        30: MoonriverRPC,
        31: KlaytnRPC,
        32: KavaRPC,
        33: FantomRPC,
        34: AuroraRPC,
        35: CantoRPC,
        36: DFK_RPC,
        37: FuseRPC,
        38: GoerliRPC,
        39: MeterRPC,
        40: OKX_RPC,
        41: ShimmerRPC,
        42: TenetRPC,
        43: XPLA_RPC,
        44: LootChainRPC,
        45: ZKFairRPC,
        46: BeamRPC,
        47: InEVM_RPC,
        48: RaribleRPC,
        49: BlastRPC,
    }[chain_id]


async def cex_deposit_util(current_client, dapp_id:int, deposit_data:tuple):
    class_name = {
        1: OKX,
        2: BingX,
        3: Binance,
        4: Bitget
    }[dapp_id]

    return await class_name(current_client).deposit(deposit_data=deposit_data)


async def okx_deposit(account_name, private_key, network, proxy):
    worker = Custom(get_client(account_name, private_key, network, proxy))
    return await worker.smart_cex_deposit(dapp_id=1)


async def bingx_deposit(account_name, private_key, network, proxy):
    worker = Custom(get_client(account_name, private_key, network, proxy))
    return await worker.smart_cex_deposit(dapp_id=2)


async def binance_deposit(account_name, private_key, network, proxy):
    worker = Custom(get_client(account_name, private_key, network, proxy))
    return await worker.smart_cex_deposit(dapp_id=3)


async def bitget_deposit(account_name, private_key, network, proxy):
    worker = Custom(get_client(account_name, private_key, network, proxy))
    return await worker.smart_cex_deposit(dapp_id=4)


async def bridge_utils(current_client, dapp_id, chain_from_id, bridge_data, need_fee=False):

    class_bridge = {
        1: Across,
        2: Bungee,
        3: Relay,
        4: Nitro,
        5: Orbiter,
        6: Owlto,
        7: Relay,
        8: Rhino,
    }[dapp_id]

    return await class_bridge(current_client).bridge(chain_from_id, bridge_data, need_check=need_fee)


async def bridge_across(account_name, private_key, network, proxy):
    worker = Custom(get_client(account_name, private_key, network, proxy))
    return await worker.smart_bridge(dapp_id=1)


async def bridge_bungee(account_name, private_key, network, proxy):
    worker = Custom(get_client(account_name, private_key, network, proxy))
    return await worker.smart_bridge(dapp_id=2)


async def bridge_relay2(account_name, private_key, network, proxy):
    worker = Custom(get_client(account_name, private_key, network, proxy))
    return await worker.smart_bridge(dapp_id=3)


async def bridge_nitro(account_name, private_key, network, proxy):
    worker = Custom(get_client(account_name, private_key, network, proxy))
    return await worker.smart_bridge(dapp_id=4)


async def bridge_orbiter(account_name, private_key, network, proxy):
    worker = Custom(get_client(account_name, private_key, network, proxy))
    return await worker.smart_bridge(dapp_id=5)


async def bridge_owlto(account_name, private_key, network, proxy):
    worker = Custom(get_client(account_name, private_key, network, proxy))
    return await worker.smart_bridge(dapp_id=6)


async def bridge_relay(account_name, private_key, network, proxy):
    worker = Custom(get_client(account_name, private_key, network, proxy))
    return await worker.smart_bridge(dapp_id=7)


async def bridge_rhino(account_name, private_key, network, proxy):
    worker = Custom(get_client(account_name, private_key, network, proxy))
    return await worker.smart_bridge(dapp_id=8)


async def okx_withdraw(account_name, private_key, network, proxy):
    worker = Custom(get_client(account_name, private_key, network, proxy))
    return await worker.smart_cex_withdraw(dapp_id=1)


async def bingx_withdraw(account_name, private_key, network, proxy):
    worker = Custom(get_client(account_name, private_key, network, proxy))
    return await worker.smart_cex_withdraw(dapp_id=2)


async def binance_withdraw(account_name, private_key, network, proxy):
    worker = Custom(get_client(account_name, private_key, network, proxy))
    return await worker.smart_cex_withdraw(dapp_id=3)


async def bitget_withdraw(account_name, private_key, network, proxy):
    worker = Custom(get_client(account_name, private_key, network, proxy))
    return await worker.smart_cex_withdraw(dapp_id=4)


async def bridge_native(account_name, private_key, _, proxy, *args, **kwargs):
    network = get_network_by_chain_id(13)
    blockchain = get_interface_by_chain_id(random.choice(NATIVE_CHAIN_ID_TO))

    worker = blockchain(get_client(account_name, private_key, network, proxy))
    return await worker.deposit(*args, **kwargs)


async def transfer_eth(account_name, private_key, network, proxy):
    blockchain = get_interface_by_chain_id(13)

    worker = blockchain(get_client(account_name, private_key, network, proxy))
    return await worker.transfer_eth()


async def transfer_eth_to_myself(account_name, private_key, network, proxy):
    blockchain = get_interface_by_chain_id(13)

    worker = blockchain(get_client(account_name, private_key, network, proxy))
    return await worker.transfer_eth_to_myself()


async def wrap_eth(account_name, private_key, network, proxy, *args):
    worker = SimpleEVM(get_client(account_name, private_key, network, proxy))
    return await worker.wrap_eth(*args)


async def unwrap_eth(account_name, private_key, network, proxy, *args):
    worker = SimpleEVM(get_client(account_name, private_key, network, proxy))
    return await worker.unwrap_eth(*args)


# async  def mint_deployed_token(account_name, private_key, network, proxy, *args, **kwargs):
#     mint = ZkSync(account_name, private_key, network, proxy)
#     await mint.mint_token()


async def swap_odos(account_name, private_key, network, proxy, **kwargs):
    worker = Odos(get_client(account_name, private_key, network, proxy))
    return await worker.swap(**kwargs)


async def swap_oneinch(account_name, private_key, network, proxy, **kwargs):
    worker = OneInch(get_client(account_name, private_key, network, proxy))
    return await worker.swap(**kwargs)


async def swap_izumi(account_name, private_key, network, proxy, **kwargs):
    worker = Izumi(get_client(account_name, private_key, network, proxy))
    return await worker.swap(**kwargs)


async def refuel_bungee(account_name, private_key, _, proxy):
    chain_from_id = LAYERZERO_WRAPED_NETWORKS[random.choice(SRC_CHAIN_BUNGEE)]
    network = get_network_by_chain_id(chain_from_id)

    worker = Bungee(get_client(account_name, private_key, network, proxy))
    return await worker.refuel()


async def swap_uniswap(account_name, private_key, network, proxy, **kwargs):
    worker = Uniswap(get_client(account_name, private_key, network, proxy))
    return await worker.swap(**kwargs)


async def mint_mintfun(account_name, private_key, network, proxy):
    worker = MintFun(get_client(account_name, private_key, network, proxy))
    return await worker.mint_mintfun()


async def random_approve(account_nameaccount_name, private_key, network, proxy):
    blockchain = get_interface_by_chain_id(13)

    worker = blockchain(get_client(account_nameaccount_name, private_key, network, proxy))
    return await worker.random_approve()


async def make_balance_to_average(account_name, private_key, network, proxy):

    worker = Custom(get_client(account_name, private_key, network, proxy))
    return await worker.balance_average()


async def okx_withdraw_util(current_client, **kwargs):
    worker = OKX(current_client)
    return await worker.withdraw(**kwargs)


async def bingx_withdraw_util(current_client, **kwargs):
    worker = BingX(current_client)
    return await worker.withdraw(**kwargs)


async def binance_withdraw_util(current_client, **kwargs):
    worker = Binance(current_client)
    return await worker.withdraw(**kwargs)


async def bitget_withdraw_util(current_client, **kwargs):
    worker = Bitget(current_client)
    return await worker.withdraw(**kwargs)


async def bingx_transfer(account_name, private_key, network, proxy):
    worker = BingX(get_client(account_name, private_key, network, proxy))
    return await worker.withdraw(transfer_mode=True)


async def bridge_zora(account_name, private_key, _, proxy):
    network = get_network_by_chain_id(random.choice(NATIVE_CHAIN_ID_FROM))

    worker = Zora(get_client(account_name, private_key, network, proxy))
    return await worker.bridge()
