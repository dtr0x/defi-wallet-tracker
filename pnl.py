from util import *

# Profit and loss analysis

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-ticker', type=str, help='Token ticker to get trades', required=True)
    args = parser.parse_args()
    token_ticker = args.ticker

    swaps = pd.read_csv('data/token_trades/{}.csv'.format(token_ticker))
    swaps['block_time'] = pd.to_datetime(swaps['block_time'])

    trading = []

    for address in tqdm(swaps['address'].unique()):
        t = swaps[swaps['address'] == address]
        buys = t[t['side'] == 'BUY']
        sells = t[t['side'] == 'SELL']

        purchased_amount = buys['received_amount'].sum()
        sold_amount = sells['sent_amount'].sum()

        # For now assume that as long as tokens purchased, any inflow/outflow due to staking
        if purchased_amount != 0 and sold_amount != 0:
            avg_buy_price = buys['sent_amount'].sum()/purchased_amount
            avg_sell_price = sells['received_amount'].sum()/sold_amount

            token_yield = max(0, sold_amount - purchased_amount)

            profit_from_yield = avg_sell_price * token_yield

            realized_profit = (avg_sell_price - avg_buy_price) * (sold_amount - token_yield) \
                + profit_from_yield


            pnl = realized_profit/(sold_amount * avg_buy_price) * 100

            # uPnL
            latest_price = swaps.loc[0]['token_price']
            held_amount = max(0, purchased_amount - sold_amount)
            unrealized_profit = held_amount * (latest_price - avg_buy_price)
            if held_amount == 0:
                upnl = 0
            else:
                upnl = unrealized_profit/(held_amount * avg_buy_price) * 100


            combined_profit = realized_profit + unrealized_profit


            trading.append((address, purchased_amount, sold_amount, avg_buy_price, \
                avg_sell_price, token_yield, profit_from_yield, realized_profit, \
                pnl, unrealized_profit, upnl, combined_profit))



    trading = pd.DataFrame(trading, columns=['address', 'purchased_amount', 'sold_amount', \
    'avg_buy_price', 'avg_sell_price', 'token_yield', 'profit_from_yield', 'realized_profit', \
    'pnl', 'unrealized_profit', 'upnl', 'combined_profit']).sort_values(by=\
        'realized_profit', ascending=False).reset_index(drop=True)

    trading.to_csv('data/PnL/{}.csv'.format(token_ticker), index=False)

    print('Top 20 wallets by realized gains from {}:'.format(token_ticker))
    print(trading.head(20))
