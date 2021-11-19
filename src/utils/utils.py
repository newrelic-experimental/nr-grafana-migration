from pyfiglet import Figlet

def isNumber(input):
    isNummber = False
    try:
        int(input)
        isNummber = True
    except:
        pass
    return isNummber

def bannerDashboards():
    print('''
            This tool exports a list of Grafana Dashboards based on PromQL queries to New Relic.
            If you need support please contact:

                        Samuel Vandamme (svandamme@newrelic.com)
                                        or
                        Amine Benzaied (abenzaied@newrelic.com)
        ''')
    f = Figlet(font='slant', width=200)
    print (f.renderText('Grafana Dashboards Migration Tool'))

def bannerAlerts():
    print('''
            This tool converts a list of Prometheus alerts to New Relic
            If you need support please contact:

                        Samuel Vandamme (svandamme@newrelic.com)
                                        or
                        Amine Benzaied (abenzaied@newrelic.com)
        ''')
    f = Figlet(font='slant', width=200)
    print (f.renderText('Prometheus Migration Tool'))
