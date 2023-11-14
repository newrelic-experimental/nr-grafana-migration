import json
import math

class Widget:

    def __init__(self, conversionService, widget):
        self.conversionService = conversionService
        self.id = widget['id']
        self.title = widget.get('title', '')
        self.panelType = widget['type']

        # Coordinate conversion
        # Grafana has 24 column dashboards and New Relic has 12
        # We now divide by two and floor, but this will cause problems so a more complicate conversion method is needed
        # One height in New Relic = 3 heights in Grafana (Visually estimated)
        self.gridPosX = widget['gridPos']['x']
        self.gridPosY = widget['gridPos']['y']
        self.gridPosW = widget['gridPos']['w']
        self.gridPosH = widget['gridPos']['h']
        self.panelColumn = math.floor(self.gridPosX / 2) + 1
        self.panelWidth = math.floor(self.gridPosW / 2)
        self.panelRow = math.floor(self.gridPosY / 2) + 1 # Grafana starts at 0, New Relic at 1
        self.panelHeight = math.ceil(self.gridPosH / 2)

        # Convert visualisation if we can
        self.visualisation = None
        try:
            # Detect visualisation
            range = True
            limit = None
            if self.panelType == 'graph' or self.panelType == 'timeseries':
                self.visualisation = "viz.line"
            elif self.panelType == 'singlestat' or self.panelType == 'stat' or self.panelType == 'bargauge':
                self.visualisation = "viz.billboard"
                range = False
            elif self.panelType == 'gauge':
                self.visualisation = "viz.bullet"
                range = False

                if 'gauge' in widget and 'maxValue' in widget['gauge']:
                    limit = widget['gauge']['maxValue']

                if 'fieldConfig' in widget and 'defaults' in widget['fieldConfig'] and 'max' in widget['fieldConfig']['defaults']:
                    limit = widget['fieldConfig']['defaults']['max']

                if 'options' in widget and 'fieldOptions' in widget['options'] and 'defaults' in widget['options']['fieldOptions'] and 'max' in widget['options']['fieldOptions']['defaults']:
                    limit = widget['options']['fieldOptions']['defaults']['max']

                # HACK: insert arbitrary value for required "limit" field.
                # Grafana has an option to detect a maximum value.
                limit = limit if limit else 1000
            elif self.panelType == 'table':
                self.visualisation = "viz.table"
            elif self.panelType == 'text':
                self.visualisation = "viz.markdown"
            elif self.panelType == 'piechart':
                self.visualisation = 'viz.pie'

            if self.visualisation is None:
                # No idea what to do with this
                raise Exception('Unknown type {}'.format(widget))

            # We don't know how to convert these so just remove them
            if 'cards' in widget:
                del widget['cards']
            if 'datasource' in widget:
                del widget['datasource']

            # Parse queries
            self.rawConfiguration = {}
            if self.panelType == 'text':
                self.rawConfiguration = {
                    "text": widget['content']
                }
            else:
                self.rawConfiguration = self.convertQueries(widget['targets'], range=range)
                if limit:
                    self.rawConfiguration['limit'] = limit

        except Exception as err:
            # Nullify all except Markdown to store error
            self.visualisation = "viz.markdown"
            self.rawConfiguration = {
                "text": json.dumps({
                    "exception": type(err).__name__,
                    "arguments": err.args
                })
            }

    def convertQueries(self, targets, range=True):
        queries = []
        for target in targets:
            #if 'format' in target and target['format'] == 'time_series':
            if 'expr' in target:
                queries.append({
                    "accountId": self.conversionService.accountId,
                    "query": self.conversionService.convertQuery(target['expr'], range=range)
                })

        if len(queries) == 0:
            raise Exception('No queries found for {}'.format(targets))

        return {
            "nrqlQueries": queries
        }

    def toJSON(self):
        return {
            "id": self.id,
            "visualization": {
                "id": self.visualisation,
            },
            "layout": {
                "column": self.panelColumn,
                "row": self.panelRow,
                "height": self.panelHeight,
                "width": self.panelWidth
            },
            "title": self.title,
            "rawConfiguration": self.rawConfiguration
        }
