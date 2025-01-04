# Export schedule builder input
from pathlib import Path
from icalendar import Calendar, Event
from datetime import datetime, timedelta
import json

export_path = Path("exported.ics")

courses: list[str] = [
    # Paste the jsons here, each response being a string.
    #'[{"courseDepartmentNotes":[],"courseSubjectNotes":[], ...]'
]
courses = [json.loads(course_info) for course_info in courses]

# maps weekdays from response to ics standard
WKDAY_TO_ICS = {
    'M': 'MO',
    'T': 'TU',
    'W': 'WE',
    'R': 'TH',
    'F': 'FR',
}
# maps weekdays from response to python datetime standard
WKDAY_TO_DATETIME = {
    'M': 0,
    'T': 1,
    'W': 2,
    'R': 3,
    'F': 4,
}


def next_weekday(d, weekdays):
    """Change `d`'s date to the next weekday in `weekdays`. If current day is in
    weekdays, return `d` without modification"""
    min_days_ahead = 8
    for weekday in weekdays:
        days_ahead = weekday - d.weekday()
        if days_ahead < min_days_ahead:
            min_days_ahead = days_ahead
    return d + timedelta(min_days_ahead)

def parse(classinfo) -> list[Event]:
    """Parse classinfo into a list of events

    Args:
    classinfo - Dictionary containing information of one class. Format follows
    the search.cfc request.
    """

    events: list[Event] = []

    classname = classinfo['course']['shortDesc']
    desc = classinfo['icmsData']['newDescription']

    for meeting in classinfo['meeting']:
        event = Event()
        event.add('description', desc)
        event.add('summary', f'{classname} - {meeting['description']}')

        # Recurrence
        until = datetime.strptime(meeting['endDate'], '%B, %d %Y %H:%M:%S')
        byday = []
        for c in meeting['daysString']:
            byday.append(WKDAY_TO_ICS[c])
        #byday = ','.join(byday)
        event.add('rrule', {
            'freq': 'weekly',
            'interval': 1,
            'byday': byday,
            'until': until
        })

        # First occurrence start/end datetime
        byday = []
        for c in meeting['daysString']:
            byday.append(WKDAY_TO_DATETIME[c])
        # dtstart and end has the same date but not the same time; endDate
        # refers to the last class, accounting for repetition
        dtstart = datetime.strptime(meeting['startDate'], '%B, %d %Y %H:%M:%S')
        dtstart = next_weekday(dtstart, byday)
        dtend = dtstart
        dtstart = dtstart.replace(hour=int(meeting['startTime'][:2]),
                        minute=int(meeting['startTime'][2:4]))
        dtend = dtend.replace(hour=int(meeting['endTime'][:2]),
                        minute=int(meeting['endTime'][2:4]))
        event.add('dtstart', dtstart)
        event.add('dtend', dtend)
        event.add('dtstamp', datetime.now())

        event.add('location', f'{meeting['room']} {meeting['building']}')

        events.append(event)

    # Final exam
    event = Event()
    event.add('description', desc)
    event.add('summary', f'{classname} - Final')
    dtstart = datetime.strptime(classinfo['finalExam']['examDate'],
                                '%B, %d %Y %H:%M:%S')
    dtend = dtstart + timedelta(hours = 2)
    event.add('dtstart', dtstart)
    event.add('dtend', dtend)
    event.add('dtstamp', datetime.now())
    events.append(event)
    return events

def make_cal(courses: list[str]) -> Calendar:
    cal = Calendar()
    cal.add('prodid', '-//My calendar product//mxm.dk//')
    cal.add('version', '2.0')
    for course in courses:
        events = parse(course[0])
        for event in events:
            cal.add_component(event)
    return cal

if __name__ == "__main__":
    cal = make_cal(courses)
    with open(export_path, 'wb') as f:
        f.write(cal.to_ical())
        f.close()
