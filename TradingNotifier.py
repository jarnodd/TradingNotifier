import GCalendar
import EconomicCalendar

class TradingNotifier():
    def __init__(self, gc: GCalendar.GCalendar, ec: EconomicCalendar.EconomicCalendar):
        self.gc = gc
        self.ec = ec

        df = ec.getEconomicCalendar()
        self.df = ec.filterEconomicEvents(df)

    # Function to format time from economic calendar like: 7:00pm to 19:00:00
    def formatTime(self, time: str) -> str:
        time_shift = time[-2:]
        hour = time.split(':')[0]
        minute = time.split(':')[1][:-2]
        
        if time_shift == 'pm':
            hour = str(int(hour)+12)
        elif time_shift == 'am' and hour == '12':
            hour = '00'
        
        if len(hour) == 1:
            hour = '0'+hour

        formatted_time = hour + ':' + minute + ':00'
        return formatted_time



    def run(self):
        
        events = ec.listEconomicEventsForHour(self.df)
        for event in events:
            for key, item in event.items():
                time = self.formatTime(key)
                newsInline = '\n'.join( n for n in item)

                gc.createEvent(key+' News', newsInline, time, 5)




if __name__ == '__main__':
    # Init Google Calendar class
    gc = GCalendar.GCalendar()
    
    # Init Economic Calendar class
    ec = EconomicCalendar.EconomicCalendar()
    
    # Init TradingNotifier class with default options
    tn = TradingNotifier(gc, ec)

    tn.run()


