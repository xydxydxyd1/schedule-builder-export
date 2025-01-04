# Export schedule builder input
from pathlib import Path
from icalendar import Event, vText
from typing import NamedTuple
from datetime import datetime
import json
import pprint

# maps format from response to ics standard
BYDAY_MAPPING = {
    'M': 'MO',
    'T': 'TU',
    'W': 'WE',
    'R': 'TH',
    'F': 'FR',
}

export_path = Path("exported.ics")

course_info = '[{"courseDepartmentNotes":[],"courseSubjectNotes":[],"icmsData":{"newDescription":"Theory, application, and design of analog circuits. Methods of analysis including frequency response, SPICE simulation, and Laplace transform. Operational amplifiers and design of active filters.  ","creditLimit":"Students who have completed ENG 100 may receive 3.5 units of credit.","ge3":"QL,SE,VL","crossListing":"","prereq":" ENG 017 C- or better;  (MAT 022B or MAT 027B)"},"finalExam":{"examDate":"March, 19 2025 13:00:00"},"meeting":[{"thursday":false,"sunday":false,"startDate":"January, 06 2025 00:00:00","endTime":"2100","tuesday":true,"friday":false,"endDate":"March, 14 2025 00:00:00","daysString":"T","wednesday":false,"monday":false,"meetCode":"C","startTime":"1810","building":"Kemper Hall","description":"Laboratory","buildingCode":"KEMPER","saturday":false,"type":"LAB","room":"02161"},{"thursday":true,"sunday":false,"startDate":"January, 06 2025 00:00:00","endTime":"1730","tuesday":true,"friday":false,"endDate":"March, 14 2025 00:00:00","daysString":"TR","wednesday":false,"monday":false,"meetCode":"A","startTime":"1610","building":"Olson Hall","description":"Lecture","buildingCode":"OLSON","saturday":false,"type":"LEC","room":"00006"},{"thursday":true,"sunday":false,"startDate":"January, 06 2025 00:00:00","endTime":"1800","tuesday":true,"friday":false,"endDate":"March, 14 2025 00:00:00","daysString":"TR","wednesday":false,"monday":false,"meetCode":"D","startTime":"1740","building":"Olson Hall","description":"Discussion","buildingCode":"OLSON","saturday":false,"type":"DIS","room":"00217"}],"crnNotes":[],"importantNotes":[],"course":{"termCode":"202501","dropDesc":"10 Day Drop","unitsLow":5,"reservedSeating":false,"shortDesc":"EEC 100 A02","gradeMode":"","unitsInd":"","seqNum":"A02","printCRN":"20411","unitsHigh":0,"dropDate":"January, 17 2025 00:00:00","title":"Circuits II","subjectDesc":"Engineering Electrical & Compu","courseNum":"100","hidCRN":"20411","crn":"20411","subjectCode":"EEC"},"instructor":[{"lastName":"Kolner","instructorName":"B. Kolner","firstName":"Brian","instructorEmail":"bhkolner@ucdavis.edu","fullName":"Brian Kolner"}]}]'
course_info = json.loads(course_info)

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

        dtstart = datetime.strptime(meeting['startDate'], '%B, %d %Y %H:%M:%S')
        dtstart.replace(hour=int(meeting['startTime'][:2]),
                        minute=int(meeting['startTime'][2:4]))
        event.add('dtstart', dtstart)
        dtend = datetime.strptime(meeting['endDate'], '%B, %d %Y %H:%M:%S')
        dtend.replace(hour=int(meeting['endTime'][:2]),
                        minute=int(meeting['endTime'][2:4]))
        event.add('dtend', dtend)
        event.add('dtstamp', datetime.now())

        byday = []
        for c in meeting['daysString']:
            byday.append(BYDAY_MAPPING[c])
        byday = ','.join(byday)
        event.add('rrule', {
            'freq': 'weekly',
            'interval': 1,
            'byday': byday
        })

        event.add('location', f'{meeting['room']} {meeting['building']}')

        pprint.pp(meeting)
        print(event)
        events.append(event)
    return events

if __name__ == "__main__":
    pprint.pp(course_info)
    parse(course_info[0])
#    parsed_class_info = parse(class_info)
#    calendar = get_calendar(parsed_class_info)
#    write_export(path, calendar)
