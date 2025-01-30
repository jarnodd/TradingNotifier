import requests
import pandas as pd
from datetime import datetime
from io import StringIO

class EconomicCalendar():
    def __init__(self) -> None:
        self.EC_LINK = 'https://nfs.faireconomy.media/ff_calendar_thisweek.csv'        


    def getEconomicCalendar(self) -> pd.core.frame.DataFrame:
        s = requests.Session()
        data = s.get(self.EC_LINK)
        
        # decode data to utf-8 and trasform with StringIO
        data = StringIO(data.content.decode('utf-8'))

        df = pd.read_csv(data)
        return df


    def filterEconomicEvents(self, df: pd.core.frame.DataFrame, market: str = 'USD', impact: str = 'High') -> pd.core.frame.DataFrame:
        # filter to get only specific market, impact event and todays event 
        return df[(df['Country'] == market) & (df['Impact'] == impact) & (df['Date'] == datetime.now().strftime('%m-%d-%Y'))]
        

    def listEconomicEventsForHour(self, df: pd.core.frame.DataFrame) -> list:
        eventsTitle = []
        hours = df['Time'].unique()
        for hour in hours:
            # filter by hour -> get title event -> to csv -> split to dict -> remove first and last item
            news = df[df['Time'] == hour]['Title'].to_csv(index=False).split('\n')[1::][:-1]
            hour = str(int(hour.split(':')[0])+1)+':'+hour.split(':')[1] # +1 for GMT+1 Europe/Rome
            eventsTitle.append({hour:news})
        return eventsTitle


if __name__ == '__main__':
    ec = EconomicCalendar()
    df = ec.getEconomicCalendar()
    df = ec.filterEconomicEvents(df)
    events = ec.listEconomicEventsForHour(df)

    for event in events:
        for key, item in event.items():
            print('At ' + key + ':')
            print('\r\n'.join(i for i in item))
