from util import *


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-ticker', type=str, help='Token ticker to get trades', required=True)
    args = parser.parse_args()
    token_ticker = args.ticker

    token_pairs = pd.read_csv('token_pairs.csv')

    print('Getting transactions for token {}...'.format(token_ticker))
    token_info = token_pairs[token_pairs['token'] == token_ticker]

    if len(token_info) != 1:
        print('Pair not found for {}'.format(token_ticker))
        exit()

    t = token_info.iloc[0]

    pair_token = t.pair_token
    token_address = t.token_address
    pair = t.pair_address

    # Trade analysis

    transaction_data = get_all_transactions(token_address)

    transactions = [Transaction(t) for t in transaction_data]

    swaps = []

    for t in transactions:
        s = t.get_swap(pair)
        if s is not None:
            swaps.append(s)

    swaps = pd.DataFrame(swaps)

    swaps['side'] = ['BUY' if p else 'SELL' for p in swaps['received_token'] == token_ticker]


    swaps = swaps.assign(token_price=np.nan)

    buy_idx = swaps[swaps['side'] == 'BUY'].index
    sell_idx = swaps[swaps['side'] == 'SELL'].index

    swaps.loc[buy_idx, 'token_price'] = \
        swaps.loc[buy_idx, 'sent_amount']/swaps.loc[buy_idx, 'received_amount']

    swaps.loc[sell_idx, 'token_price'] = \
        swaps.loc[sell_idx, 'received_amount']/swaps.loc[sell_idx, 'sent_amount']


    swaps.to_csv('data/token_trades/{}.csv'.format(token_ticker), index=False)
