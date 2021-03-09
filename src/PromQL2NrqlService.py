import requests

class PromQL2NrqlService:

    def __init__(self, username, password, accountId):
        self.username = username
        self.password = password
        self.accountId = accountId

        # Login to New Relic
        self.session = requests.Session()
        self.session.hooks = {
            'response': lambda r, *args, **kwargs: r.raise_for_status()
        }

        login_data = {
            "login[email]": self.username,
            "login[password]": self.password
        }
        self.session.post("https://login.newrelic.com/login", data = login_data)

    def convertQuery(self, promql, range=True):
        custom_headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json"
        }
        nrql = self.session.post("https://promql-gateway.service.newrelic.com/api/v1/translate", headers=custom_headers, json={
            "promql": promql,
            "account_id": self.accountId,
            "isRange": range,
            "startTime": "null",
            "endTime": "null",
            "step": 30
        })
        data = nrql.json()

        return data['nrql']

