import requests
import json
import src.utils.constants as constants
import browser_cookie3
import re

class PromQL2NrqlService:

    def __init__(self, config, variables):

        self.accountId = config['api']['accountId']
        self.grafanaVariables = variables

        # Create local cache to store queries, this will speed up testing
        self.cache = self.loadCache()

        # Login to New Relic
        self.session = requests.Session()
        self.authenticate(config, self.session)
    
    def loadCache(self):
        try:
            f = open(constants.CACHE_FILE_NAME, "r")
            content = json.load(f)
        except FileNotFoundError: #code to run if error occurs
            content = {}

        return content

    def saveCache(self):
        data = json.dumps(self.cache)
        f = open(constants.CACHE_FILE_NAME,"w")
        f.write(data)
        f.close()

    def convertQuery(self, query, range=True, clean=True):
        custom_headers = {
            "X-Requested-With": "XMLHttpRequest",
            "Accept": "application/json"
        }
        promql = re.sub(r'(?<=\{)(.*?)(?=\})', self.removeVariables, query)
        if promql not in self.cache:
            nrql = self.session.post(constants.PROMQL_TRANSLATE_URL, headers=custom_headers, json={
                "promql": promql,
                "account_id": self.accountId,
                "isRange": range,
                "startTime": "null",
                "endTime": "null",
                "step": 30
            })
            # Remove `Facet Dimensions()`
            newNrql = self.removeDimensions(nrql.json()['nrql'])
            self.cache[promql] = newNrql

        return self.cache[promql]

    def authenticate(self,configuration, session):

        self.session.hooks = {
                'response': lambda r, *args, **kwargs: r.raise_for_status()
            }
        if configuration['auth']['ssoEnabled']:
            browser = configuration['auth']['sso']['browserCookie'] 
            if browser == 'Chrome':
                cookies = browser_cookie3.chrome(domain_name='.newrelic.com')
            elif browser == 'Opera':
                cookies = browser_cookie3.opera(domain_name='.newrelic.com')
            elif browser == 'FireFox':
                cookies = browser_cookie3.firefox(domain_name='.newrelic.com')
            elif browser == 'Edge':
                cookies = browser_cookie3.edge(domain_name='.newrelic.com')
            
            for cookie in cookies:
                if cookie.domain == '.newrelic.com':  # remove .blog.newreli.com and other domains
                    self.session.cookies[cookie.name] = cookie.value
        else:
            login_data = {
                "login[email]": configuration['auth']['nonSso']['username'],
                "login[password]": configuration['auth']['nonSso']['password']
            }
            self.session.post(constants.LOGIN_URL, data = login_data)
    
    def removeVariables(self,matchedObj):
        newDimensions = []
        for dimension in matchedObj[0].split(','):
            if not any(variable in dimension for variable in self.grafanaVariables):
                newDimensions.append(dimension)
        return ",".join(newDimensions)
    
    @staticmethod
    def removeDimensions(nrqlQuery):
        pattern = re.compile(" facet dimensions\(\)", re.IGNORECASE)
        return pattern.sub("", nrqlQuery)