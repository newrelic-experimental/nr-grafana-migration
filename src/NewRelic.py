import json
import os
from src.PromQL2NrqlService import PromQL2NrqlService
from src.Dashboard import Dashboard
import src.utils.constants as constants
from python_graphql_client import GraphqlClient

class NewRelic:

    def __init__(self, config):

        self.config = config
        self.userKey = config['api']['userKey'] 
        self.accountId = config['api']['accountId'] 
        
        self.createOutputDir()
    
    def createOutputDir(self):
        # Create output directory if it doesn't exist
        if not os.path.exists(constants.OUTPUT_DIR):
            os.makedirs(constants.OUTPUT_DIR)

        if not os.path.exists(constants.NEWRELIC_OUTPUT_DIR):
            os.makedirs(constants.NEWRELIC_OUTPUT_DIR)

    def convert(self, grafanaDashboard):

        # Read file
        with open(grafanaDashboard, 'r') as f:
            data = json.load(f)
        
        # Conversion service
        variables = Dashboard.getVariables(data)
        promQL2NrqlService = PromQL2NrqlService(self.config, variables)

        # Create and parse dashboard
        print(f"Starting Conversion: {grafanaDashboard}")
        dashboard = Dashboard(promQL2NrqlService, data)

        # Create pretty json
        output = json.dumps(dashboard.toJSON(), indent=4, sort_keys=True)

        # Write out file
        filePath = f"{constants.NEWRELIC_OUTPUT_DIR}/newrelic-%s" % os.path.basename(grafanaDashboard) 
        f = open(filePath, "w")
        f.write(output)
        f.close()

        # Close query cache
        promQL2NrqlService.saveCache()

        return filePath

    def importDashboard(self, file):

        print(f"Importing Dashboard: {file}")
        # Read dashboard json file
        with open(file, 'r') as f:
            dashboard = json.load(f)

        # Instantiate the client with an endpoint.
        client = GraphqlClient(endpoint=constants.GRAPHQL_URL, headers={ "API-Key": self.userKey })

        # Create the query string and variables required for the request.
        query = constants.CREATE_DASHBOARD_MUTATION
        variables = {
            "accountId": self.accountId,
            "dashboard": dashboard,
        }

        # Synchronous request
        data = client.execute(query=query, variables=variables)
        print(json.dumps(data, indent = 3))
