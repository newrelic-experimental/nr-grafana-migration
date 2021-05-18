CONFIG_FILE_NAME = 'config.json'
GRAPHQL_URL = 'https://api.newrelic.com/graphql'
OUTPUT_DIR = 'output'
NEWRELIC_OUTPUT_DIR = 'output/newrelic'
GRAFANA_OUTPUT_DIR = 'output/grafana'
GRAFANA_DASHBOARD_LIST_CSV = f'{OUTPUT_DIR}/dashboards.csv'
GRAFANA_DASHBOARD_LIST_JSON = f'{OUTPUT_DIR}/dashboards.json'
LOGIN_URL = 'https://login.newrelic.com/login'
CACHE_FILE_NAME = 'cache.json'
PROMQL_TRANSLATE_URL = 'https://promql-gateway.service.newrelic.com/api/v1/translate'

CREATE_DASHBOARD_MUTATION = """
            mutation($accountId: Int!, $dashboard: DashboardInput!) {
                dashboardCreate(accountId: $accountId, dashboard: $dashboard) {
                    errors {
                        description
                        type
                    }
                    entityResult {
                        guid
                    }
                }
            }
        """


