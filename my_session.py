from covalent_api import session

class Session(session.Session):
    def __init__(self, key):
        super().__init__(api_key=key)

    def _check_params(self, params):
        params = super()._check_params(params)
        params['key'] = self.api_key
        return params
