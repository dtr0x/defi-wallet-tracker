from covalent_api import class_b

class ClassB(class_b.ClassB):
    def __init__(self, session):
        super().__init__(session)


    def get_xyk_transactions_for_account_address(
        self, chain_id, address, dexname, page_number=None, page_size=None):

        method_url = (
            '/v1/{chain_id}/xy=k/{dexname}/address/{address}/transactions/'.format(
                chain_id=chain_id,
                dexname=dexname,
                address=address
            )
        )
        params = {
            'quote-currency':'USD',
            'page-number':page_number,
            'page-size':page_size
        }

        result = self.session.query(method_url, params, decode=True)
        return result


    def get_xyk_transactions_for_token_address(
        self, chain_id, token_address, dexname, page_number=None, page_size=None):

        method_url = (
            '/v1/{chain_id}/xy=k/{dexname}/tokens/address/{address}/transactions/'.format(
                chain_id=chain_id,
                dexname=dexname,
                address=token_address
            )
        )
        params = {
            'quote-currency':'USD',
            'page-number':page_number,
            'page-size':page_size
        }

        result = self.session.query(method_url, params, decode=True)
        return result


    def get_pools_for_token(self, chain_id, token_address, dexname):
        method_url = (
            '/v1/{chain_id}/xy=k/{dexname}/pools/'.format(
                chain_id=chain_id,
                dexname=dexname
            )
        )
        params = {
            'quote-currency':'USD',
            'contract-addresses':token_address
        }

        result = self.session.query(method_url, params, decode=True)
        return result


    def get_pool_by_address(self, chain_id, lp_address, dexname):
        method_url = (
            '/v1/{chain_id}/xy=k/{dexname}/pools/address/{address}/'.format(
                chain_id=chain_id,
                dexname=dexname,
                address=lp_address
            )
        )
        params = {
            'quote-currency':'USD'
        }

        result = self.session.query(method_url, params, decode=True)
        return result
