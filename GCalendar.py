from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from email.mime.text import MIMEText
from google.oauth2.credentials import Credentials
import os
import datetime

SCOPES=['https://www.googleapis.com/auth/calendar']

class GCalendar():
    def __init__(self):
        self.creds = None
        # Il file token.json salva i token di accesso e aggiornamento dell'utente.
        # Se già esiste, carica le credenziali.
        if os.path.exists('token.json'):
            self.creds = Credentials.from_authorized_user_file('token.json', scopes=SCOPES)
        
        # Se non ci sono credenziali valide disponibili, richiedi l'autenticazione.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', scopes=SCOPES)
                self.creds = flow.run_local_server(port=0)
            # Salva le credenziali per le esecuzioni future.
            with open('token.json', 'w') as token:
                token.write(self.creds.to_json())

        self.service = build('calendar', 'v3', credentials=self.creds)

        # Check if "TradingNotifier" calendar has already been created
        if os.path.exists('calendarId.txt'):
            f = open('calendarId.txt','r')
            self.calendarId = f.readline().strip('\n')
            f.close()
        else:
            self.calendarId = self.initTradingCalendar()


    # Create "TradingNotifier" calendar
    def initTradingCalendar(self) -> str:
        calendar = {
            'summary': 'TradingNotifier',
            'timeZone': 'Europe/Rome'
        }
        createdId = self.service.calendars().insert(body=calendar).execute()
        f = open('calendarId.txt','w+')
        f.write(createdId['id'])
        return createdId['id']



    def getUpComingEvents(self):
        try:
            # Call the Calendar API
            now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
            print("Getting the upcoming 10 events")
            events_result = (
                self.service.events()
                .list(
                calendarId="primary",
                timeMin=now,
                maxResults=10,
                singleEvents=True,
                orderBy="startTime",
            ).execute())
            events = events_result.get("items", [])
            print(events)
            if not events:
                print("No upcoming events found.")
            return

            # Prints the start and name of the next 10 events
            for event in events:
                start = event["start"].get("dateTime", event["start"].get("date"))
                print(start, event["summary"])

        except HttpError as error:
            print(f"An error occurred: {error}")



    def createEvent(self, title: str, desc: str, hour: str, minutesReminder: int):
        today = datetime.datetime.utcnow().strftime("%Y-%m-%d")
        event = {
            'summary': title,
            'description': desc,
            'start': {
                'dateTime': today+'T'+hour,
                'timeZone': 'Europe/Rome',
            },
            'end': {
                'dateTime': today+'T'+hour,
                'timeZone': 'Europe/Rome',
            },
            #'recurrence': [
            #    'RRULE:FREQ=DAILY;COUNT=2'
            #],
            #'attendees': [
            #    {'email': 'lpage@example.com'},
            #    {'email': 'sbrin@example.com'},
            #],
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': minutesReminder},
                ],
            },
        }

        event = self.service.events().insert(calendarId=self.calendarId, body=event).execute()
        print('Event created: %s' % (event.get('htmlLink')))



if __name__ == '__main__':
    gcalendar = GCalendar()
