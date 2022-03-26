from util import *

class Transfer():
    def __init__(self, transfer_data):
        self.token_decimals = transfer_data['sender_contract_decimals']
        self.token_ticker = transfer_data['sender_contract_ticker_symbol']
        self.token_address = transfer_data['sender_address']
        self.params = transfer_data['decoded']['params']

    def get_token_decimals(self):
        return self.token_decimals

    def get_token_ticker(self):
        return self.token_ticker

    def get_token_address(self):
        return self.token_address

    def get_to_address(self):
        return [p['value'] for p in self.params if p['name'] == 'to'][0]

    def get_from_address(self):
        return [p['value'] for p in self.params if p['name'] == 'from'][0]

    def get_transfer_amount(self):
        value = [i['value'] for i in self.params if i['name'] == 'value'][0]
        return int(value) * 10**(-self.token_decimals)
