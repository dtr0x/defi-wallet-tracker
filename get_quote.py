from Transaction import *

def get_quote(token, pair):
    i = 0
    has_more = True
    while has_more:
        txs = get_transactions(token, page_number=i, n_transactions=100)
        tx_items = txs['items']
        transactions = [Transaction(t) for t in tx_items]
        for t in transactions:
            swap = t.get_swap(pair)
            if swap:
                if swap['received_token_address'] == token:
                    # buy
                    base = swap['received_amount']
                    quote = swap['sent_amount']
                else:
                    # sell
                    base = swap['sent_amount']
                    quote = swap['received_amount']

                return quote/base
        i += 1
        has_more = txs['pagination']['has_more']


token = '0x22d4002028f537599bE9f666d1c4Fa138522f9c8'.lower()
pair = '0xCDFD91eEa657cc2701117fe9711C9a4F61FEED23'.lower()

print(get_quote(token, pair))
