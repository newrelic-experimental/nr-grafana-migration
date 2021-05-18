from pyfiglet import Figlet

def isNumber(input):
    isNummber = False
    try:
        int(input)
        isNummber = True
    except: 
        pass
    return isNummber

def banner():
    print('''
            This tool exports a list of Grafana Dashboards based on PromQL queries to New Relic.
            If you need support please contact: 

                        Samuel Vandamme (svandamme@newrelic.com) 
                                        or 
                        Amine Benzaied (abenzaied@newrelic.com)
        ''')
    f = Figlet(font='slant', width=200)
    print (f.renderText('Grafana Dashboards Migration Tool'))