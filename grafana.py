from src.config.config import config
from src.utils.utils import banner
from src.Grafana import Grafana
from src.NewRelic import NewRelic

#############################################################################
######                             main                               #######
#############################################################################

banner()

config = config()

# Grafana
grafana = Grafana(config)
grafanaDashboardsFiles = grafana.selectGrafanaDashboards()

# New Relic
newRelic = NewRelic(config)
for file in grafanaDashboardsFiles:
    nrDashboard = newRelic.convert(file)
    newRelic.importDashboard(nrDashboard)
