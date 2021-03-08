#!/usr/bin/env python3
from python_graphql_client import GraphqlClient
import json
import argparse

# Parse arguments
parser = argparse.ArgumentParser(description='Convert Grafana dashboards to import into New Relic')
parser.add_argument('dashboard', metavar='path', type=str, help='Grafana json file you want to convert to New Relic')
parser.add_argument('-v', '--verbose', action="store_true", help='Run in verbose mode')
args = parser.parse_args()

# Read config file
with open('config.json', 'r') as f:
    config = json.load(f)

apiAccountId = config['api']['accountId']
apiToken = config['api']['token']

# Read dashboard json file
with open(args.dashboard, 'r') as f:
    dashboard = json.load(f)

# Instantiate the client with an endpoint.
client = GraphqlClient(endpoint="https://api.newrelic.com/graphql", headers={ "API-Key": apiToken })

# Create the query string and variables required for the request.
query = """
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
variables = {
    "accountId": apiAccountId,
    "dashboard": dashboard,
}

# Synchronous request
data = client.execute(query=query, variables=variables)
print(json.dumps(data, indent = 3))
