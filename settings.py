"""
----------------------------------------------------CEX CONTROL---------------------------------------------------------
    Выберите сети/суммы для вывода и ввода с CEX. Не забудьте вставить API ключи в general_settings.py.
    Депозиты и выводы работают только со спотовым балансом на бирже.

    1 - ETH-ERC20                10 - CELO-CELO           19 - USDT-Arbitrum One       29 - USDC-Optimism (Bridged)
    2 - ETH-Arbitrum One         11 - GLMR-Moonbeam       20 - USDT-Avalanche          30 - USDC-Polygon (Bridged)
    3 - ETH-Optimism             12 - MOVR-Moonriver      21 - USDT-Optimism           31 - USDC-BSC
    4 - ETH-zkSync Era           13 - METIS-Metis         22 - USDT-Polygon            32 - USDC-ERC20
    5 - ETH-Linea                14 - CORE-CORE           23 - USDT-BSC                33 - STG-Arbitrum One
    6 - ETH-Base                 15 - CFX-CFX_EVM         24 - USDT-ERC20              34 - STG-BSC
    7 - AVAX-Avalanche C-Chain   16 - KLAY-Klaytn         25 - USDC-Arbitrum One       35 - STG-Avalanche C-Chain
    8 - BNB-BSC                  17 - FTM-Fantom          26 - USDC-Avalanche C-Chain  36 - STG-Fantom
    9 - BNB-OPBNB                18 - MATIC-Polygon       27 - USDC-Optimism           37 - USDV-BSC
                                                          28 - USDC-Polygon            38 - ARB-Arbitrum One

    ⚠️ Софт сам отнимает комиссию от суммы депозита, при работе с нативными токенами ⚠️

    Сумма в количестве  - (0.01, 0.02)
    Сумма в процентах   - ("10", "20") ⚠️ Значения в кавычках.

    OKX_WITHDRAW_DATA | Каждый список - один модуль для вывода из биржи. Примеры работы указаны ниже:
                        Для каждого вывода указывайте [сеть вывода, (мин и макс сумма)]

    OKX_DEPOSIT_DATA | Каждый список - один модуль для депозита на биржу. Примеры работы указаны ниже:
                       Для каждого вывода указывайте [сеть депозита, (мин и макс сумма)]

    Примеры рандомизации:

    [[17, (1, 1.011)], None] | Пример установки None, для случайного выбора (выполнение действия или его пропуск)
    [[2, (0.48, 0.5)], [3, (0.48, 0.5)]] | Пример установки двух сетей, софт выберет одну случайную.

    Дополнительно к верхним примерам, для депозита на биржу поддерживается режим поиска баланса:
        [(2, 3, 4), (0.001, 0.002)] | Пример указания нескольких сетей, cофт выберет сеть с наибольшим балансом.

    CEX_DEPOSIT_LIMITER | Настройка лимитного вывода на биржу. Указывать в $USD
                          1 значение - это минимальный баланс на аккаунте, чтобы софт начал процесс вывода
                          2 значение - это мин. и макс. сумма, которая должна остаться на балансе после вывода.
                          Если сумма депозита будет оставлять баланс на аккаунте больше 2-го значения, софт не будет
                          пытать сделать сумму депозита больше или меньше указанной в DEPOSIT_DATA

    CEX_BALANCER_CONFIG = [
        [Х, Y, Z, (A, B)],
    ]

    «Х» - Софт проверит количество этого токена в этой сети, согласно списку в группе «CEX CONTROL»
    Если оно меньше значения «Y», то происходит вывод с биржи «Z» токена «Х» в количестве от «A» до «B».
    «Z» значение - биржа для вывода. 1 - OKX, 2 - BingX, 3 - Binance, 4 - Bitget. Модуль (make_balance_to_average).

    Пример:
    CEX_BALANCER_CONFIG = [
        [20, 5, 1, (30, 40)],
    ]

    Софт проверяет USDT в сети Avalanche. Если меньше 5, то докидывает с биржи от 30 до 40 USDT
"""
'--------------------------------------------------------OKX-----------------------------------------------------------'

OKX_WITHDRAW_DATA = [
    [8, (0.004, 0.00411)],
]

OKX_DEPOSIT_DATA = [
    [8, (0.004, 0.00411)],
]

'--------------------------------------------------------BingX---------------------------------------------------------'

BINGX_WITHDRAW_DATA = [
    [8, (0.004, 0.00411)],
]

BINGX_DEPOSIT_DATA = [
    [8, (0.004, 0.00411)],
]

'-------------------------------------------------------Binance--------------------------------------------------------'

BINANCE_WITHDRAW_DATA = [
    [8, (0.004, 0.00411)],
]

BINANCE_DEPOSIT_DATA = [
    [8, (0.004, 0.00411)],
]

'--------------------------------------------------------BitGet--------------------------------------------------------'

BITGET_WITHDRAW_DATA = [
    [37, ('100', '100')],
]

BITGET_DEPOSIT_DATA = [
    [37, ('100', '100')],
]

'-------------------------------------------------------Control--------------------------------------------------------'

CEX_BALANCER_CONFIG = [
    [1, 0.005, 3, (0.01, 0.01)]
]

CEX_DEPOSIT_LIMITER = 0, (0, 0)         # (Ограничитель баланса, (мин. сумма, макс. сумма для остатка на балансе))

"""
-----------------------------------------------------BRIDGE CONTROL-----------------------------------------------------
    Проверьте руками, работает ли сеть на сайте. (Софт сам проверит, но зачем его напрягать?)
    Для каждого моста поддерживается уникальная настройка
       
        Arbitrum = 1                    zkSync Era = 11     
        Arbitrum Nova = 2               Zora = 12 
        Base = 3                        Ethereum = 13
        Linea = 4                       Avalanche = 14
        Manta = 5                       BNB Chain = 15
        Polygon = 6                     Metis = 26        
        Optimism = 7                    OpBNB = 28
        Scroll = 8                      Mantle = 29
        Starknet = 9                    ZKFair = 45
        Polygon ZKEVM = 10              Blast = 49
                                           
    Сумма в количестве  - (0.01, 0.02)
    Сумма в процентах   - ("10", "20") ⚠️ Значения в кавычках
    
    NATIVE_CHAIN_ID_FROM(TO) = [2, 4, 16] | Одна из сетей будет выбрана. Применимо для bridge_zora (instant), 
                                            остальные бриджи в L2 будут из Ethereum, а выводы в Ethereum
    NATIVE_DEPOSIT_AMOUNT | Настройка для вывода из нативного моста (withdraw_native_bridge)
    ACROSS_TOKEN_NAME | Укажите токен для бриджа. Поддерживаются: ETH, BNB, MATIC, USDC, USDC.e (Bridged), USDT. 
                        Если у бриджа указано 2 токена в скобках см. BUNGEE_TOKEN_NAME, то бридж сможет делать бриджи
                        между разными токенами. Справа от параметра, для каждого бриджа указаны доступные токены.
                        
    BRIDGE_AMOUNT_LIMITER | Настройка лимитных бриджей. Указывать в $USD
                            1 значение - это минимальный баланс на аккаунте, чтобы софт начал процесс бриджа
                            2 значение - это мин. и макс. сумма, которая должна остаться на балансе после бриджа
                            Если сумма для бриджа будет оставлять баланс на аккаунте больше второго значения,
                            софт не будет пытать сделать сумму бриджа больше или меньше указанной
                            
    BUNGEE_ROUTE_TYPE | Установка своего роута для совершения транзакции, по умолчанию (0) - самый лучший. 
                        1-Across   3-Celer     5-Stargate   7-Synapse      9-Hop
                        2-CCTP     4-Connext   6-Socket     8-Symbiosis    10-Hyphen   
                                                      
"""

'-----------------------------------------------------Native Bridge----------------------------------------------------'

NATIVE_CHAIN_ID_FROM = [1]                 # Исходящая сеть. Применимо ТОЛЬКО для bridge_zora.
NATIVE_CHAIN_ID_TO = [12]                  # Входящая сеть
NATIVE_DEPOSIT_AMOUNT = (0.001, 0.001)     # (минимум, максимум) (% или кол-во)
NATIVE_WITHDRAW_AMOUNT = (0.0001, 0.0002)  # (минимум, максимум) (% или кол-во)

'--------------------------------------------------------Across--------------------------------------------------------'

ACROSS_CHAIN_ID_FROM = [9]                # Исходящая сеть
ACROSS_CHAIN_ID_TO = [4]                  # Входящая сеть
ACROSS_BRIDGE_AMOUNT = (0.002, 0.002)     # (минимум, максимум) (% или кол-во)
ACROSS_TOKEN_NAME = 'ETH'

'--------------------------------------------------------Bungee--------------------------------------------------------'

BUNGEE_CHAIN_ID_FROM = [3]                  # Исходящая сеть
BUNGEE_CHAIN_ID_TO = [1]                    # Входящая сеть
BUNGEE_BRIDGE_AMOUNT = (0.001, 0.001)       # (минимум, максимум) (% или кол-во)
BUNGEE_TOKEN_NAME = ('ETH', 'ETH')          # ETH, BNB, MATIC, USDC, USDC.e, USDT
BUNGEE_ROUTE_TYPE = 5                       # см. BUNGEE_ROUTE_TYPE

'--------------------------------------------------------Nitro---------------------------------------------------------'

NITRO_CHAIN_ID_FROM = [1]                   # Исходящая сеть
NITRO_CHAIN_ID_TO = [11]                    # Входящая сеть
NITRO_BRIDGE_AMOUNT = (0.001, 0.001)        # (минимум, максимум) (% или кол-во)
NITRO_TOKEN_NAME = ('ETH', 'USDC')          # ETH, USDC, USDT

'-------------------------------------------------------Orbiter--------------------------------------------------------'

ORBITER_CHAIN_ID_FROM = [7, 3, 5]           # Исходящая сеть
ORBITER_CHAIN_ID_TO = [6]                   # Входящая сеть
ORBITER_BRIDGE_AMOUNT = (8, 9)              # (минимум, максимум) (% или кол-во)
ORBITER_TOKEN_NAME = 'USDC'

'--------------------------------------------------------Owlto---------------------------------------------------------'

OWLTO_CHAIN_ID_FROM = [11]                 # Исходящая сеть
OWLTO_CHAIN_ID_TO = [4]                    # Входящая сеть
OWLTO_BRIDGE_AMOUNT = (0.002, 0.003)       # (минимум, максимум) (% или кол-во)
OWLTO_TOKEN_NAME = 'ETH'

'--------------------------------------------------------Relay---------------------------------------------------------'

RELAY_CHAIN_ID_FROM = [11]                # Исходящая сеть
RELAY_CHAIN_ID_TO = [7]                   # Входящая сеть
RELAY_BRIDGE_AMOUNT = (0.001, 0.001)      # (минимум, максимум) (% или кол-во)
RELAY_TOKEN_NAME = 'ETH'

'--------------------------------------------------------Relay2--------------------------------------------------------'

RELAY2_CHAIN_ID_FROM = [8]               # Исходящая сеть
RELAY2_CHAIN_ID_TO = [1]                 # Входящая сеть
RELAY2_BRIDGE_AMOUNT = (0.003, 0.003)    # (минимум, максимум) (% или кол-во)
RELAY2_TOKEN_NAME = ('ETH', 'ETH')       # ETH, USDC, USDC.e


'--------------------------------------------------------Rhino---------------------------------------------------------'

RHINO_CHAIN_ID_FROM = [7]                # Исходящая сеть
RHINO_CHAIN_ID_TO = [11]                 # Входящая сеть
RHINO_BRIDGE_AMOUNT = (1, 1.8)           # (минимум, максимум) (% или кол-во)
RHINO_TOKEN_NAME = ('USDC', 'ETH')       # ETH, BNB, MATIC, USDC, USDT

'-------------------------------------------------------Control--------------------------------------------------------'

BRIDGE_AMOUNT_LIMITER = 0, (0, 0)  # (Ограничитель баланса, (мин. сумма, макс. сумма для остатка на балансе))

"""
---------------------------------------------OMNI-CHAIN CONTROL---------------------------------------------------------
    Проверьте руками, работают ли сети на сайте. (Софт сам проверит, но зачем его напрягать?)
       
        Arbitrum = 1                  Goerli = 16                        Optimism = 31
        Arbitrum Nova = 2             Gnosis = 17                        Orderly = 32
        Astar = 3                     Harmony = 18                       Polygon = 33  
        Aurora = 4                    Horizen = 19                       Polygon zkEVM = 34
        Avalanche = 5                 Kava = 20                          Scroll = 35
        BNB = 6                       Klaytn = 21                        ShimmerEVM = 36
        Base = 7                      Linea = 22                         Telos = 37
        Canto = 8                     Loot = 23                          TomoChain = 38 
        Celo = 9                      Manta = 24                         Tenet = 39
        Conflux = 10                  Mantle = 25                        XPLA = 40
        CoreDAO = 11                  Meter = 26                         Zora = 41  
        DFK = 12                      Metis = 27                         opBNB = 42
        Ethereum = 13                 Moonbeam = 28                      zkSync = 43
        Fantom = 14                   Moonriver = 29                     Beam = 44
        Fuse = 15                     OKX = 30                           inEVM = 45
                                                                         Rarible = 46
    
    SRC_CHAIN_BUNGEE = [27, 29] | Одна из сетей будет выбрана 

    DST_CHAIN_BUNGEE_REFUEL = {
        1: (0.0016, 0.002), # Chain ID: (минимум, максимум) в нативном токене входящей сети**
        2: (0.0002, 0.0005) 
    } 
"""

SRC_CHAIN_BUNGEE = [43]          # Исходящая сеть для Bungee
DST_CHAIN_BUNGEE_REFUEL = {
    5: (0.0003, 0.00031),  # Chain ID: (минимум, максимум) в нативном токене исходящей сети (кол-во)
}

"""
---------------------------------------------------------OTHER----------------------------------------------------------
    MINTFUN_CONTRACTS | Список контрактов для минта в выбранной сети (GLOBAL NETWORK)

"""

MINTFUN_CONTRACTS = [
    '0x123'
]

"""
-------------------------------------------------CLASSIC-ROUTES CONTROL-------------------------------------------------

--------------------------------------------------------HELPERS---------------------------------------------------------        

    okx_withdraw                     # смотри CEX CONTROL
    bingx_withdraw                   # смотри CEX CONTROL
    binance_withdraw                 # смотри CEX CONTROL
    bitget_withdraw                  # смотри CEX CONTROL
    
    bridge_across                    # смотри BRIDGE CONTROL
    bridge_bungee                    # смотри BRIDGE CONTROL
    bridge_nitro                     # смотри BRIDGE CONTROL
    bridge_owlto                     # смотри BRIDGE CONTROL
    bridge_orbiter                   # смотри BRIDGE CONTROL
    bridge_zora                      # смотри BRIDGE CONTROL. см. NATIVE_CHAIN_ID_FROM, NATIVE_DEPOSIT_AMOUNT
    bridge_relay                     # смотри BRIDGE CONTROL
    bridge_relay2                    # смотри BRIDGE CONTROL. Модуль для возможности второго бриджа через Relay
    bridge_rhino                     # смотри BRIDGE CONTROL
    bridge_native                    # смотри BRIDGE CONTROL (кол-во из NATIVE_DEPOSIT_AMOUNT)
    withdraw_txsync                  # вывод через txSync (кол-во из NATIVE_WITHDRAW_AMOUNT)
    
    okx_deposit                      # ввод средств на биржу + сбор средств на субАккаунтов на основной счет
    bingx_deposit                    # ввод средств на биржу + сбор средств на субАккаунтов на основной счет
    binance_deposit                  # ввод средств на биржу + сбор средств на субАккаунтов на основной счет
    bitget_deposit                   # ввод средств на биржу + сбор средств на субАккаунтов на основной счет
        
    make_balance_to_average          # уравнивает ваши балансы на аккаунтах (см. CEX_BALANCER_CONFIG) 
        
--------------------------------------------------------Ethereum--------------------------------------------------------            
    
    refuel_bungee                    # смотри OMNI-CHAIN CONTROL
    swap_izumi                       # делает случайный свап токенов на AMOUNT_PERCENT для ETH и на 100% для других.
    swap_oneinch                       пары выбираются случайно, с учетом баланса на кошельке. Свапы работаю по
    swap_uniswap                       следующим направлениям: ETH -> Token, Token -> ETH. Token -> Token не будет, во
    swap_odos                          избежания проблем с платой за газ.
    mint_mintfun                     # mint NFT на сайте https://mint.fun/feed/trending
    wrap_eth                         # wrap ETH через офф. контракт
    unwrap_eth                       # unwrap ETH через офф. контракт
    random_approve                   # рандомный апрув на случайны контракт агрегатора
    refuel_bungee                    # рефьел через Bungee. см. OMNI-CHAIN CONTROL
    transfer_eth                     # трансфер эфира на СЛУЧАЙНЫЙ адрес. см. TRANSFER_AMOUNT
    transfer_eth_to_myself           # трансфер эфира на СВОЙ адрес. см. TRANSFER_AMOUNT
    
    Роуты для настоящих древлян (Машина - зло).
    Выберите необходимые модули для взаимодействия
    Вы можете создать любой маршрут, софт отработает строго по нему. Для каждого списка будет выбран один модуль в
    маршрут, если софт выберет None, то он пропустит данный список модулей. 
    Список модулей сверху.
    
    CLASSIC_ROUTES_MODULES_USING = [
        ['okx_withdraw'],
        ['bridge_layerswap', 'bridge_native'],
        ['swap_mute', 'swap_izumi', 'mint_domain_ens', None],
        ...
    ]
"""

CLASSIC_ROUTES_MODULES_USING = [
    ['okx_withdraw'],
    ['bridge_relay'],
    ['refuel_bungee', 'bridge_relay2', 'transfer_eth', 'transfer_eth_to_myself'],
]
