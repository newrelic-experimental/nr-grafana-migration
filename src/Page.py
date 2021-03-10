from src.Widget import Widget

class Page:

    def __init__(self, conversionService, name = '', description = '', widgets = []):
        self.conversionService = conversionService
        self.name = name
        self.description = description
        self.widgets = widgets

    def addWidget(self, widget):
        self.widgets.append(Widget(conversionService=self.conversionService, widget=widget))

    def addWidgets(self, widgets):
        self.widgets.extend(widgets)

    def toJSON(self):
        return {
            "name": self.name,
            "description": self.description,
            "widgets": list(map(lambda widget: widget.toJSON(), self.widgets)),
        }
