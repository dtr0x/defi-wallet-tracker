from util import *
from Token import Token
from Transaction import Transaction

class TokenTradeHistory():
    def __init__(self, address):
        self.token = Token(address)

    def get_token(self):
        return self.token

    def get_token_address(self):
        return self.token.get_address()

    def get_token_ticker(self):
        return self.token.get_ticker()

    def get_token_lps(self):
        return self.token.get_pools()

    def get_token_price(self):
        return self.token.get_quote()

    def get_token_trades(self, update=True):
        token_ticker = self.get_token_ticker()
        token_address = self.get_token_address()

        path = 'data/token_trade_history/{}_{}.csv'.format(\
            token_ticker, token_address)
        file_exists = os.path.isfile(path)

        if update or not file_exists:
            swaps = []

            for lp in self.get_token_lps():
                print('Getting transactions for pool {}...'.format(lp))
                transaction_data = get_all_transactions(lp)
                transactions = [Transaction(t) for t in transaction_data]
                swaps_for_lp = [t.get_swap(lp) for t in transactions if t.get_swap(lp)]
                print('Got {} swaps.'.format(len(swaps_for_lp)))
                swaps += swaps_for_lp

            trades = {}

            trades['date'] = [t['block_time'] for t in swaps]
            trades['tx_hash'] = [t['tx_hash'] for t in swaps]
            trades['address'] = [t['address'] for t in swaps]
            trades['side'] = np.where([t['received_token_address'] == token_address \
                for t in swaps], 'BUY', 'SELL').tolist()

            trades['price'] = []
            trades['amount'] = []
            trades['total'] = []
            for t in swaps:
                if t['received_token_address'] == token_address:
                    token_amount = t['received_amount']
                    quote_currency_total = t['sent_amount']
                    quote_currency_address = t['sent_token_address']
                else:
                    token_amount = t['sent_amount']
                    quote_currency_total = t['received_amount']
                    quote_currency_address = t['received_token_address']

                if quote_currency_address == get_quote_currencies()['WAVAX']:
                    quote_currency_total *= t['avax_price']

                trades['price'].append(quote_currency_total/token_amount)
                trades['amount'].append(token_amount)
                trades['total'].append(quote_currency_total)

            df = pd.DataFrame(trades)

            df.to_csv(path, index=False)

        else:
            df = pd.read_csv(path)
            df['date'] = pd.to_datetime(df['date'])

        return df


    def get_token_profit_and_loss(self, update=False):
        trades = self.get_token_trades(update)
