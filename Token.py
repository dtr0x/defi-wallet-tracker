from util import *

class Token():
    def __init__(self, address):
        self.address = address.lower()

        # initialize pools
        x = get_pools_for_token(self.address)
        q = get_quote_currency_addresses()
        pool_data = [i for i in x if (i['token_0']['contract_address'] in q) \
            or (i['token_1']['contract_address'] in q)]

        # get ticker from pool_data
        self.ticker = ''

        for p in pool_data:
            if p['token_0']['contract_address'] == self.address:
                self.ticker = p['token_0']['contract_ticker_symbol']
                break
            if p['token_1']['contract_address'] == self.address:
                self.ticker = p['token_1']['contract_ticker_symbol']
                break

        # include pools if sufficient liquidity
        pools = [(p['exchange'], p['total_liquidity_quote']) for p in pool_data]
        pools = sorted(pools, key=lambda q: q[1], reverse=True)
        total_liquidity = np.sum([p[1] for p in pools])
        liquidity_coverage = 0
        included_pools = []

        for p in pools:
            if liquidity_coverage < 0.99:
                included_pools.append(p[0])
                liquidity_coverage += p[1]/total_liquidity

        self.pools = included_pools


    def get_address(self):
        return self.address

    def get_ticker(self):
        return self.ticker

    def get_pools(self):
        return self.pools

    # Get average quote from included liquidity pools
    def get_quote(self):
        quotes = []

        for p in self.pools:
            z = get_pool_by_address(p)
            tokens = [z[i] for i in ['token_0', 'token_1']]
            quote = [t['quote_rate'] for t in tokens if \
                t['contract_address'] == self.address][0]
            quotes.append(quote)

        return np.mean(quotes)
