import questionary
import json
from pathlib import Path
from src.utils.utils import isNumber
import src.utils.constants as constants

def createConfigFile(ConfigFileName):
    config = {
        "auth": {
            "ssoEnabled": False,
            "sso":{
                "browserCookie":"",
            },
            "nonSso":{
                "username": "",
                "password": "",
            }
        },
        "api": {
            "userKey": "",
            "accountId":""
        },
        "grafana": {
            "apiKey": "",
            "host": ""
        }
    }
    
    print("")
    questionary.print("Let's get some information about New Relic (destination) 🔑", style="bold italic fg:darkred")
    ssoEnabled = questionary.confirm("Do you use SSO to login to New Relic?").ask()
    if ssoEnabled:
        questionary.text("Please open your Browser and make sure you are logged in to New Rewlic (do NOT use private window). Hit enter after completing this step").ask()
        browserCookie = questionary.select("What do you want to do?", choices=["Chrome","Opera","FireFox","Edge"]).ask()
        config['auth']['sso']['browserCookie'] = browserCookie
    else:
        username = questionary.text("Please enter your New Relic username (email used to login to NR)").ask()
        password = questionary.password("Please enter your New Relic password (password used to login to NR)").ask()
        config['auth']['nonSso']['username'] = username
        config['auth']['nonSso']['password'] = password
    userKey = questionary.text("Please enter your user API key (aka GraphQL API Key)").ask()
    accountId = questionary.text("Please enter your New Relic account Id", validate=isNumber).ask()

    print("")
    questionary.print("Let's get some information about Grafana (source) 🔑", style="bold italic fg:darkred")
    host = questionary.text("Please enter your Grafana host name (for example: 'myAccount.grafana.net')").ask()
    apiKey = questionary.text("Please enter your Grafana API Key").ask()

    config['auth']['ssoEnabled'] = ssoEnabled
    config['api']['userKey'] = userKey
    config['api']['accountId'] = int(accountId)
    config['grafana']['host'] = host
    config['grafana']['apiKey'] = apiKey

    data = json.dumps(config)
    with open(ConfigFileName,"w") as f:
        f.write(data)
    
    print("")
    questionary.print("We created your configuration file based on your entries, please update the file if needed. We will use this file if you execute this script again!")


def config():
    configFileName = constants.CONFIG_FILE_NAME
    configFile = Path(configFileName)
    if configFile.is_file():
        # file exists
        print("We found a configuration file! We will use that file!")
        print('\n')
    else: 
        # file does not exist   
        print("Let's start by creating your configuration file. We will ask you a couple of questions!")
        createConfigFile(configFileName)
        print('\n')

    # Read config file
    with open(configFileName, 'r') as f:
        config = json.load(f)
    return config