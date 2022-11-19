#!/usr/bin/env python3

from src.AlertFile import AlertFile
from src.config.config import config
from src.utils.utils import bannerAlerts
from src.NewRelic import NewRelic
import sys
import yaml

#############################################################################
######                             main                               #######
#############################################################################

bannerAlerts()

config = config()

# Check first argument, it should be a file
if len(sys.argv) < 2:
    print("Please supply the Prometheus alert file to convert as the first argument.")
    print("> python3 prometheus.py [alert file]")
    sys.exit(1)

# Load file
with open(sys.argv[1]) as file:
    # The FullLoader parameter handles the conversion from YAML
    # scalar values to Python the dictionary format
    prometheusData = yaml.load(file, Loader=yaml.FullLoader)
    print("File loaded, converting alerts")

# Start conversion process
alertFile = AlertFile(config, prometheusData)
for alert in alertFile.getAlerts():
    print(alert.failed)
