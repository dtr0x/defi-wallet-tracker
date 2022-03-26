import covalent_api as cq
from my_session import Session
from my_classb import ClassB
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json, requests, time, argparse, re, os
from tqdm import tqdm

pd.set_option('display.max_rows', 10000)
pd.set_option('display.max_colwidth', None)
pd.set_option('display.float_format', lambda x: '%.6f' % x)

def get_api_key():
    with open('covalent_api_key.json') as f:
        return json.load(f)['key']

API_KEY = get_api_key()
CHAIN_ID = '43114'

# initialize API caller class A
session_a = Session(API_KEY)
api_a = cq.class_a.ClassA(session=session_a)

# initialize API caller class B
session_b = Session(API_KEY)
api_b = ClassB(session=session_b)

JOE_ROUTER = '0x60ae616a2155ee3d9a68541ba4544862310933d4'

# pretty print a dictionary
def pprint(dict_data):
    print(json.dumps(dict_data, sort_keys=True, indent=4))

# get unique list items (preserve order)
def unique_list(my_list):
    return pd.Series(my_list).unique().tolist()

def request_wrapper(func, kwargs={}):
    try:
        return func(**kwargs)
    except requests.exceptions.RequestException:
        print('Request error. Retrying in 30 seconds...')
        time.sleep(30)
        return request_wrapper(func, kwargs)
    except:
        print('Service error. Retrying in 30 seconds...')
        time.sleep(30)
        return request_wrapper(func, kwargs)


def get_a_transaction(tx_hash):
    kwargs = {'chain_id': CHAIN_ID,
        'tx_hash': tx_hash
        }
    t = request_wrapper(api_a.get_a_transaction, kwargs)
    return t['data']['items'][0]


def get_transactions(address, page_number=0, n_transactions=9999):
    kwargs = {'chain_id': CHAIN_ID,
        'address': address,
        'page_number': page_number,
        'page_size': n_transactions
        }
    s1 = time.time()
    t = request_wrapper(api_a.get_transactions, kwargs)
    s2 = time.time()
    print('Got {} transactions in {:.2f} seconds.'.format(len(t['data']['items']), s2-s1))
    return t['data']

def get_all_transactions(address):
    i = 0
    all_items = []
    has_more = True
    while has_more:
        txs = get_transactions(address, page_number=i)
        tx_items = txs['items']
        tx_items = [t for t in tx_items if t['successful']]
        all_items += tx_items
        print('Total successful transactions: {}'.format(len(all_items)))
        i += 1
        has_more = txs['pagination']['has_more']
    return all_items

def is_stablecoin(symbol):
    if re.search('^USD|.USD$|^MIM$|^UST$|^DAI|^FRAX', symbol):
        return True
    else:
        return False

def get_quote_currencies():
    return {
        'WAVAX': '0xb31f66aa3c1e785363f0875a1b74e27b85fd66c7',
        'MIM': '0x130966628846bfd36ff31a822705796e8cb8c18d',
        'USDT.e': '0xc7198437980c041c805a1edcba50c1ce5db95118',
        'USDC.e': '0xa7d7079b0fead91f3e65f86e8915cb59c1a4c664',
        'DAI.e': '0xd586e7f844cea2f87f50152665bcbc2c279d8d70'
    }

def get_quote_currency_addresses():
    return list(get_quote_currencies().values())

def get_pools_for_token(token_address):
    kwargs = {'chain_id': CHAIN_ID,
        'token_address': token_address,
        'dexname': 'traderjoe'
        }
    t = request_wrapper(api_b.get_pools_for_token, kwargs)
    return t['data']['items']


def get_pool_by_address(lp_address):
    kwargs = {'chain_id': CHAIN_ID,
        'lp_address': lp_address,
        'dexname': 'traderjoe'
        }
    t = request_wrapper(api_b.get_pool_by_address, kwargs)
    return t['data']['items'][0]


def get_token_transfers(token, address, page_number=0, n_transactions=9999):
    kwargs = {'chain_id': CHAIN_ID,
        'address': address,
        'contract_address': token,
        'page_number': page_number,
        'page_size': n_transactions
        }
    s1 = time.time()
    t = request_wrapper(api_a.get_erc20_token_transfers, kwargs)
    s2 = time.time()
    print('Got {} transfers in {:.2f} seconds.'.format(len(t['data']['items']), s2-s1))
    return t['data']

def get_all_token_transfers(token, address):
    i = 0
    all_items = []
    has_more = True
    while has_more:
        txs = get_token_transfers(token, address, page_number=i)
        tx_items = txs['items']
        tx_items = [t for t in tx_items if t['successful']]
        all_items += tx_items
        print('Total successful transfers: {}'.format(len(all_items)))
        i += 1
        has_more = txs['pagination']['has_more']
    return all_items
