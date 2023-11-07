import requests
import json
import src.utils.constants as constants
import browser_cookie3
import os
import re


class PromQL2NrqlService:

    def __init__(self, config):

        self.accountId = config['api']['accountId']

        # Create local cache to store queries, this will speed up testing
        self.cache = self.loadCache()

        # Login to New Relic
        # Use an API key if provided, else get a new session
        token = os.getenv('NEW_RELIC_API_TOKEN')
        self.session = requests.Session()
        if token:
            self.token = token
        else:
            self.token = None
            self.authenticate(config, self.session)

        self.grafanaVariables = None


    def loadCache(self):
        try:
            f = open(constants.CACHE_FILE_NAME, "r")
            content = json.load(f)
        except FileNotFoundError: #code to run if error occurs
            content = {}

        return content

    def setVariables(self, variables):
        self.grafanaVariables = variables

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
        if self.token:
            custom_headers['Api-Key'] = self.token

        promql = query

        # if promql not in self.cache:
        nrql = self.session.post(constants.PROMQL_TRANSLATE_URL, headers=custom_headers, json={
            "promql": query,
            "account_id": self.accountId,
            "isRange": range,
            "startTime": "null",
            "endTime": "null",
            "step": 30
        })

        if nrql.status_code == 200:
            # Remove `Facet Dimensions()`
            newNrql = self.removeDimensions(nrql.json()['nrql'])
            newNrql = self.replaceGrafanaVariables(newNrql)
            self.cache[promql] = newNrql
        else:
            # Print the error to console
            print('{}:\n    {}'.format(nrql.json()['message'], promql))
            self.cache[promql] = promql

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
    
    def replaceGrafanaVariables(self,nrqlQuery):
        new_nrql_query = nrqlQuery
        for variable in self.grafanaVariables:
            variable_name = variable['name']
            new_nrql_query = new_nrql_query.replace('\'$' + variable_name + '\'', '{{' + variable_name + '}}')

        return new_nrql_query
    
    @staticmethod
    def removeDimensions(nrqlQuery):
        pattern = re.compile(" facet dimensions\(\)", re.IGNORECASE)
        return pattern.sub("", nrqlQuery)