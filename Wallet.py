from util import *
from Transfer import Transfer
from Transaction import Transaction

class Wallet():
    def __init__(self, address):
            self.address = address
            transaction_data = get_all_transactions(address)
            self.transactions = [Transaction(t) for t in transaction_data]

    def get_address(self):
        return self.address

    def get_transactions(self):
        return self.transactions

    def get_swap_txs(self):
        return [t for t in self.get_transactions() if t.is_swap()]

    def get_token_swaps(self):
        swap_txs = self.get_swap_txs()
        swaps = []
        for tx in swap_txs:
            lps = tx.get_all_swap_lps()
            for lp in lps:
                s = tx.get_swap(lp)
                if s:
                    s.pop('address')
                    s['pair'] = lp
                    swaps.append(s)
        return pd.DataFrame(swaps)

    def get_token_trades(self):
        swaps = self.get_swap_txs()
        trades = [s.get_trade() for s in swaps if s.get_trade() is not None]
        [t.pop('address') for t in trades]
        return pd.DataFrame(trades)

    def get_purchased_tokens(self):
        trades = self.get_token_trades()
        purchased = trades[['received_token_ticker', 'received_token_address']]
        purchased = purchased.drop_duplicates().dropna()
        purchased.columns = ['ticker', 'address']
        include = [p for p in purchased['ticker'] if not is_stablecoin(p) and p != 'WAVAX']
        return purchased[purchased['ticker'].isin(include)].reset_index(drop=True)


    # Get token inflow amount from other wallets
    def get_token_inflow(self, token_address):
        inflow = 0
        for tx in self.get_transactions():
            if tx.get_from_address() != self.address:
                logs = tx.get_log_events()
                transfers = tx.get_transfers()
                if len(logs) == 1 and len(transfers) == 1:
                    t = transfers[0]
                    if t.get_token_address() == token_address and t.get_to_address() == self.address:
                            inflow += t.get_transfer_amount()
        return inflow


    # get tokens purchased outside Trader Joe, which will be ignored for now
    def get_token_buys_other_exchange(self):
        swap_log_names = ['Transfer', 'Sync', 'Swap', 'Approval', 'Withdrawal', 'Deposit']

        transactions = self.get_transactions()
        swap_txs = [t for t in transactions if \
        'Swap' in t.get_log_names() and t.get_to_address() != JOE_ROUTER]

        tokens_bought_other_exchange = []

        for s in swap_txs:
            l = s.get_log_names()
            non_swap_logs = [i for i in l if i not in swap_log_names]
            if len(non_swap_logs) == 0:
                for t in s.get_transfers():
                    if t.get_to_address() == self.get_address():
                        tokens_bought_other_exchange.append((t.get_token_ticker(), t.get_token_address()))

        df = pd.DataFrame(tokens_bought_other_exchange).drop_duplicates().reset_index(drop=True)
        df.columns = ['ticker', 'address']

        return df

    def get_bought_tokens_primary_exchange(self):
        bought = self.get_purchased_tokens()
        bought_oe = self.get_token_buys_other_exchange()
        return bought[~bought['address'].isin(\
        bought_oe['address'])].reset_index(drop=True)


    def get_profit_and_loss(self):
        p = self.get_purchased_tokens()
        include = [a for a in p['address'] if w.get_token_inflow(a) == 0 and not w.has_token_swaps_on_other_exchange(a)]

        s = self.get_token_swaps()
