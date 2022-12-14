import getopt
import glob
import os
import sys

from src.Crossplane import Crossplane
from src.Grafana import Grafana
from src.NewRelic import NewRelic
from src.config.config import config, defaultConfig
from src.utils.utils import banner
import src.utils.constants as constants

#############################################################################
######                             main                               #######
#############################################################################

banner()

options, remainder = getopt.getopt(sys.argv[1:], 'l:c', ['local',
                                                         'crossplane',
                                                         ])
for opt, arg in options:
    if opt in ('-l', '--local'):
        # In local mode we just read the grafana files from a directory
        # instead of downloading them from the grafana api
        token = os.getenv('NEW_RELIC_API_TOKEN')
        accountId = os.getenv('NEW_RELIC_ACCOUNT_ID')
        localConfig = defaultConfig()
        localConfig['api']['userKey'] = token
        localConfig['api']['accountId'] = accountId
        # New Relic
        newRelic = NewRelic(localConfig)
        # Process the dashboard files on disk
        grafanaDashboardsFiles = glob.glob(os.path.join(constants.GRAFANA_OUTPUT_DIR, "*.json"))
        for file in grafanaDashboardsFiles:
            nrDashboard = newRelic.convert(file)
    elif opt in ('-c', '--crossplane'):
        # In crossplane mode we read newrelic dashboard files and convert them to
        # the format required by the crossplane newrelic operator
        # https://marketplace.upbound.io/providers/smcavallo/provider-newrelic/v0.1.0
        crossplane = Crossplane()
        nrDashboardsFiles = glob.glob(os.path.join(constants.NEWRELIC_OUTPUT_DIR, "*.json"))
        for file in nrDashboardsFiles:
            crossplane.convert(file)

if not options:
    config = config()

    # Grafana
    grafana = Grafana(config)
    grafanaDashboardsFiles = grafana.selectGrafanaDashboards()

    # New Relic
    newRelic = NewRelic(config)
    for file in grafanaDashboardsFiles:
        nrDashboard = newRelic.convert(file)
        newRelic.importDashboard(nrDashboard)
