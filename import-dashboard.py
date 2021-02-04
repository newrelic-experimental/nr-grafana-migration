#!/usr/bin/env python3

from python_graphql_client import GraphqlClient
import json

# Read config file
with open('config.json', 'r') as f:
    config = json.load(f)

apiAccountId = config['api']['accountId']
apiToken = config['api']['token']

# Read dashboard json file
with open('export.json', 'r') as f:
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
