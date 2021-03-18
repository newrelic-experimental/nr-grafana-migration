import requests
import json

class PromQL2NrqlService:

    def __init__(self, username, password, accountId):
        self.username = username
        self.password = password
        self.accountId = accountId

        # Create local cache to store queries, this will speed up testing
        self.cache = self.loadCache()

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

    def loadCache(self):
        try:
            f = open("cache.json", "r")
            content = json.load(f)
        except FileNotFoundError as e: #code to run if error occurs
            content = []

        return content

    def saveCache(self):
        data = json.dumps(self.cache)
        f = open("cache.json","w")
        f.write(data)
        f.close()

    def convertQuery(self, promql, range=True, clean=True):
        custom_headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json"
        }

        if promql not in self.cache:
            nrql = self.session.post("https://promql-gateway.service.newrelic.com/api/v1/translate", headers=custom_headers, json={
                "promql": promql,
                "account_id": self.accountId,
                "isRange": range,
                "startTime": "null",
                "endTime": "null",
                "step": 30
            })
            self.cache[promql] = nrql.json()['nrql']

        return self.cache[promql]

