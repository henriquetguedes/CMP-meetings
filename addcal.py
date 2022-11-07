# -*- coding: utf-8 -*-
from __future__ import print_function
import datetime
import pickle
import os.path
import smtplib
from email.message import EmailMessage
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from pathlib import Path

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar']
idcal = "6so8m41445fnt1hfhla5r3c13k@group.calendar.google.com"

def adiciona(nome, desc, dataini):
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(Path(__file__).absolute().resolve().parent.parent / 'credenciais'/ 'token.pickle'):
        with open(Path(__file__).absolute().resolve().parent.parent / 'credenciais'/ 'token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(Path(__file__).absolute().resolve().parent.parent / 'credenciais'/ 'CMPcal.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(Path(__file__).absolute().resolve().parent.parent / 'credenciais'/ 'token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Call the Calendar API
    #now = datetime.datetime.utcnow().isoformat() + 'Z' # 'Z' indicates UTC time
    #print('Getting the upcoming 10 events')
    #events_result = service.events().list(calendarId=idcal, timeMin=now, maxResults=10, singleEvents=True, orderBy='startTime').execute()
    #events = events_result.get('items', [])
#
    #if not events:
    #    print('No upcoming events found.')
    #for event in events:
    #    start = event['start'].get('dateTime', event['start'].get('date'))
    #    print(start, event['summary'])

    event = {
      'summary': nome,
      'location': 'Câmara Municipal do Porto, R. Clube dos Fenianos 5, 4000-407 Porto, Portugal',
      'description': desc,
      'start': {
        'dateTime': str(datetime.datetime.strptime(dataini, "%Y-%m-%d")).replace(" ","T"),
        'timeZone': 'Europe/Lisbon',
      },
      'end': {
        'dateTime': str(datetime.datetime.strptime(dataini, "%Y-%m-%d") + datetime.timedelta(1)).replace(" ","T"),
        'timeZone': 'Europe/Lisbon',
      },
      'recurrence': [
      ],
      'attendees': [
      ],
      'reminders': {
        'useDefault': True,
        'overrides': [
        ],
      },
    }

    event = service.events().insert(calendarId=idcal, body=event).execute()
    print ('Event created: %s' % (event.get('htmlLink')))
    return(event.get('htmlLink'))

#msg = EmailMessage()
#msg.set_content("shjdbjhsbfdjhdbjhfbdjhfbgjhdbfg")
#
#msg['Subject'] = "teste"
#msg['From'] = "henriquetguedes+t@teste.com"
#msg['To'] = "henriquetguedes@gmail.com"
#
## Send the message via our own SMTP server.
#s = smtplib.SMTP('localhost')
#s.send_message(msg)
#s.quit()