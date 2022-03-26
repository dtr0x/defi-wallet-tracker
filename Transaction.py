from util import *
from Transfer import Transfer

class Transaction():
    def __init__(self, transaction_data):
        self.tx_hash = transaction_data['tx_hash']
        self.block_time = transaction_data['block_signed_at']
        self.from_address = transaction_data['from_address']
        self.to_address = transaction_data['to_address']
        self.log_events = transaction_data['log_events']
        self.gas_quote = transaction_data['gas_quote_rate']

        transfer_data = [t for t in self.log_events if t['decoded'] and t['decoded']['name'] == 'Transfer']
        self.transfers = [Transfer(t) for t in transfer_data]

    def get_tx_hash(self):
        return self.tx_hash

    def get_block_time(self):
        block_time = ' '.join(self.block_time[:-1].split('T'))
        block_time = datetime.strptime(block_time, '%Y-%m-%d %H:%M:%S') - timedelta(hours=5)
        return block_time

    def get_from_address(self):
        return self.from_address

    def get_to_address(self):
        return self.to_address

    # if sort, ascending by log_offset
    def get_log_events(self, sort=False):
        logs = self.log_events
        if sort:
            logs = sorted(logs, key=lambda l: l['log_offset'])
        return logs

    def get_avax_price(self):
        return self.gas_quote

    def get_transfers(self):
        return self.transfers

    def get_log_names(self):
        return [t['decoded']['name'] for t in self.get_log_events() if \
            t['decoded'] and t['decoded']['name']]

    def is_swap(self):
        if self.get_to_address() == JOE_ROUTER and 'Swap' in self.get_log_names():
            return True
        else:
            return False

    def get_sent_tokens(self, lp_address):
        if self.is_swap():
            sent = [t for t in self.get_transfers() if t.get_to_address() == lp_address]
            if len(sent) == 1:
                sent = sent[0]
                token = sent.get_token_ticker()
                token_address = sent.get_token_address()
                amount = sent.get_transfer_amount()
                return (token, token_address, amount)

    def get_received_tokens(self, lp_address):
        if self.is_swap():
            received = [t for t in self.get_transfers() if t.get_from_address() == lp_address]
            if len(received) == 1:
                received = received[0]
                token = received.get_token_ticker()
                token_address = received.get_token_address()
                amount = received.get_transfer_amount()
                return (token, token_address, amount)

    def get_swap(self, lp_address):
        sent = self.get_sent_tokens(lp_address)
        received = self.get_received_tokens(lp_address)
        if sent and received:
            return {
                'block_time': self.get_block_time(),
                'tx_hash': self.get_tx_hash(),
                'address': self.get_from_address(),
                'avax_price': self.get_avax_price(),
                'sent_token_ticker': sent[0],
                'sent_token_address': sent[1],
                'received_token_ticker': received[0],
                'received_token_address': received[1],
                'sent_amount': sent[2],
                'received_amount': received[2]
            }

    # get all LPs used in this transaction (if swap)
    def get_all_swap_lps(self):
        if self.is_swap():
            logs = self.get_log_events(sort=True)
            swaps = [l for l in logs if l['decoded'] and l['decoded']['name'] == 'Swap']
            lps = [s['sender_address'] for s in swaps if s['sender_contract_ticker_symbol'] == 'JLP']
            return unique_list(lps)

    # Find trade route for all swaps involved
    def get_trade(self):
        if self.is_swap():
            lps = self.get_all_swap_lps()
            swaps = [self.get_swap(lp) for lp in lps if self.get_swap(lp)]
            if len(swaps) == 1:
                return self.get_swap(lps[0])
            elif len(swaps) > 1:
                first = swaps[0]
                last = swaps[-1]

                trade = first.copy()
                trade['received_token_ticker'] = last['received_token_ticker']
                trade['received_token_address'] = last['received_token_address']
                trade['received_amount'] = last['received_amount']
                return trade
