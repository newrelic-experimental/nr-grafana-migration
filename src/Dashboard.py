from src.Page import Page


class Dashboard:

    def __init__(self, conversionService, json, account_id):
        self.conversionService = conversionService
        self.account_id = account_id
        self.name = ''
        self.description = ''
        self.pages = []
        self.variables = self.getVariables(json)
        self.conversionService.setVariables(self.variables)
        self.setVariableQueries()

        self.parseGrafana(json)

    def parseGrafana(self, json):
        self.name = json['dashboard']['title']
        self.parsePanels(json['dashboard']['panels'])

    # For collapse = true, you have to put rows panels inside the row definition , in panels[ ] section.
    # For collapse = false, you have to put rows panels below the row definition.
    def parsePanels(self, panels):
        page = Page(conversionService=self.conversionService, widgets=[])
        succesivePanels = False

        for panel in panels:
            if panel['type'] == 'row':
                if succesivePanels:
                    self.pages.append(page)
                    succesivePanels = False
                    page = Page(conversionService=self.conversionService, widgets=[])

                page.name = panel['title']
                if 'collapsed' in panel and panel['collapsed']:
                    for nestedPanel in panel['panels']:
                        page.addWidget(nestedPanel)
                    self.pages.append(page)
                    page = Page(conversionService=self.conversionService, widgets=[])
                else:
                    succesivePanels = True
            else:
                page.addWidget(panel)

        ## Edge cases ##
        # If last row is not collapsed don't forget to add last row's panels
        if succesivePanels:
            self.pages.append(page)
        # Don't forget to add any panel that don't belong to a row at the end of Grafana dashboard to the last NR page
        elif page.widgets:
            if self.pages:
                self.pages[-1].addWidgets(page.widgets)
            ## in case no rows in the grafana dashboard
            else:
                self.pages.append(Page(conversionService=self.conversionService, name=self.name, description='',
                                       widgets=page.widgets))

    def toJSON(self):
        return {
            "name": self.name,
            "description": self.description,
            "permissions": "PUBLIC_READ_WRITE",
            "pages": list(map(lambda page: page.toJSON(), self.pages)),
            "variables": self.variables
        }

    def getVariables(self, json):
        variables = list()
        if 'templating' in json['dashboard'] and 'list' in json['dashboard']['templating']:
            variablesList = json['dashboard']['templating']['list']
            for variableObj in variablesList:

                # get multi select option from grafana
                allow_multi_select = False
                if "multi" in variableObj:
                    if "includeAll" in variableObj and variableObj["includeAll"] is True:
                        allow_multi_select = True
                    else:
                        allow_multi_select = variableObj["multi"]

                if variableObj["type"] == "query":
                    variable = {
                        "name": variableObj["name"],
                        "title": variableObj["label"],
                        "nrqlQuery": {
                            "accountIds": [self.account_id],
                            "query": variableObj["query"]["query"],
                        },
                        "isMultiSelection": allow_multi_select,
                        "type": "NRQL",
                        "replacementStrategy": "STRING"
                    }

                    variables.append(variable)

                if variableObj["type"] == "custom" or variableObj["type"] == "constant":
                    print(variableObj["name"])
                    items, default_values = self.getCustomValues(variableObj, allow_multi_select)
                    variable = {
                        "name": variableObj["name"],
                        "title": variableObj["label"],
                        "items": items,
                        "defaultValues": default_values,
                        "isMultiSelection": allow_multi_select,
                        "type": "ENUM",
                        "replacementStrategy": "STRING"
                    }

                    variables.append(variable)

        return variables

    def getCustomValues(self, variable, allow_multi_select):
        items = list()
        default_values = list()

        custom_value = variable["query"].split(",")

        for custom_value in custom_value:
            item = {
                "value": custom_value
            }
            items.append(item)

            default_value = {
                "value": {
                    "string": custom_value
                }
            }
            default_values.append(default_value)

        if allow_multi_select is True:
            default_value = {
                "value": {
                    "string": "*"
                }
            }
            default_values.append(default_value)

        return items, default_values

    def setVariableQueries(self):
        for variable in self.variables:
            if variable["type"] == "NRQL":
                variable["nrqlQuery"]["query"] = self.conversionService.convertQuery(variable["nrqlQuery"]["query"])
