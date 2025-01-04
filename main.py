# Export schedule builder input
from pathlib import Path
import tempfile, os
from icalendar import Calendar, Event
from typing import NamedTuple
from datetime import datetime, timedelta
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
# maps format from response to python datetime standard
DATETIME_MAPPING = {
    'M': 0,
    'T': 1,
    'W': 2,
    'R': 3,
    'F': 4,
}

export_path = Path("exported.ics")

courses = [
        '[{"courseDepartmentNotes":[],"courseSubjectNotes":[],"icmsData":{"newDescription":"Overview of computer networks, TCP/IP protocol suite, computer-networking applications and protocols, transport-layer protocols, network architectures, Internet Protocol (IP), routing, link-layer protocols, local area and wireless networks, medium access control, physical aspects of data transmission, and network-performance analysis. ","creditLimit":"Only 2 units of credit for students who have taken ECS 157.","ge3":"SE","crossListing":"EEC 173A.","prereq":" (ECS 032B or ECS 036C);  (ECS 132 or EEC 161 or MAT 135A or STA 032 or STA 035B or STA 100 or STA 131A)"},"finalExam":{"examDate":"March, 20 2025 10:30:00"},"meeting":[{"thursday":false,"sunday":false,"startDate":"January, 06 2025 00:00:00","endTime":"0950","tuesday":false,"friday":true,"endDate":"March, 14 2025 00:00:00","daysString":"F","wednesday":false,"monday":false,"meetCode":"D","startTime":"0900","building":"Olson Hall","description":"Discussion","buildingCode":"OLSON","saturday":false,"type":"DIS","room":"00147"},{"thursday":true,"sunday":false,"startDate":"January, 06 2025 00:00:00","endTime":"1330","tuesday":true,"friday":false,"endDate":"March, 14 2025 00:00:00","daysString":"TR","wednesday":false,"monday":false,"meetCode":"A","startTime":"1210","building":"Everson Hall","description":"Lecture","buildingCode":"EVERSN","saturday":false,"type":"LEC","room":"00176"}],"crnNotes":[],"importantNotes":[],"course":{"termCode":"202501","dropDesc":"10 Day Drop","unitsLow":4,"reservedSeating":false,"shortDesc":"ECS 152A A03","gradeMode":"","unitsInd":"","seqNum":"A03","printCRN":"19818","unitsHigh":0,"dropDate":"January, 17 2025 00:00:00","title":"Computer Networks","subjectDesc":"Engineering Computer Science","courseNum":"152A","hidCRN":"19818","crn":"19818","subjectCode":"ECS"},"instructor":[{"lastName":"Gamero Garrido","instructorName":"A. Gamero Garrido","firstName":"Alexander","instructorEmail":"agamerog@ucdavis.edu","fullName":"Alexander Gamero Garrido"}]}]',
    '[{"courseDepartmentNotes":[],"courseSubjectNotes":[],"icmsData":{"newDescription":"Theory and practice of hard problems, and problems with complex algorithm solutions. NP-completeness, approximation algorithms, randomized algorithms, dynamic programming and branch and bound. Theoretical analysis, implementation and practical evaluations. Examples from parallel, string, graph, and geometric algorithms.","creditLimit":"","ge3":"QL,SE","crossListing":"","prereq":" ECS 122A;  (ECS 060 or ECS 034 or ECS 036C)"},"finalExam":{"examDate":"March, 19 2025 18:00:00"},"meeting":[{"thursday":false,"sunday":false,"startDate":"January, 06 2025 00:00:00","endTime":"1150","tuesday":false,"friday":true,"endDate":"March, 14 2025 00:00:00","daysString":"MWF","wednesday":true,"monday":true,"meetCode":"A","startTime":"1100","building":"Walker Hall","description":"Lecture","buildingCode":"WALKER","saturday":false,"type":"LEC","room":"01310"},{"thursday":false,"sunday":false,"startDate":"January, 06 2025 00:00:00","endTime":"0950","tuesday":false,"friday":false,"endDate":"March, 14 2025 00:00:00","daysString":"W","wednesday":true,"monday":false,"meetCode":"D","startTime":"0900","building":"Teaching and Learning Complex","description":"Discussion","buildingCode":"TLC","saturday":false,"type":"DIS","room":"01218"}],"crnNotes":[],"importantNotes":[],"course":{"termCode":"202501","dropDesc":"10 Day Drop","unitsLow":4,"reservedSeating":false,"shortDesc":"ECS 122B A01","gradeMode":"","unitsInd":"","seqNum":"A01","printCRN":"19808","unitsHigh":0,"dropDate":"January, 17 2025 00:00:00","title":"Algorithm Design & Analysis","subjectDesc":"Engineering Computer Science","courseNum":"122B","hidCRN":"19808","crn":"19808","subjectCode":"ECS"},"instructor":[{"lastName":"Rafatirad","instructorName":"S. Rafatirad","firstName":"Setareh","instructorEmail":"srafatirad@ucdavis.edu","fullName":"Setareh Rafatirad"}]}]',
    '[{"courseDepartmentNotes":[],"courseSubjectNotes":[],"icmsData":{"newDescription":"Syntactic definition of programming languages. Introduction to programming language features including variables, data types, data abstraction, object-orientedness, scoping, parameter disciplines, exception handling. Non-imperative programming languages. Comparative study of several high-level programming languages.","creditLimit":"","ge3":"SE","crossListing":"","prereq":" ECS 050;  ECS 020;  (ECS 034 or ECS 036C);  ECS 150 recommended."},"finalExam":{"examDate":"March, 21 2025 08:00:00"},"meeting":[{"thursday":false,"sunday":false,"startDate":"January, 06 2025 00:00:00","endTime":"1500","tuesday":false,"friday":false,"endDate":"March, 14 2025 00:00:00","daysString":"M","wednesday":false,"monday":true,"meetCode":"D","startTime":"1410","building":"Medical Science C","description":"Discussion","buildingCode":"MDSC C","saturday":false,"type":"DIS","room":"00180"},{"thursday":false,"sunday":false,"startDate":"January, 06 2025 00:00:00","endTime":"1300","tuesday":false,"friday":true,"endDate":"March, 14 2025 00:00:00","daysString":"MWF","wednesday":true,"monday":true,"meetCode":"A","startTime":"1210","building":"Wellman Hall","description":"Lecture","buildingCode":"WELLMN","saturday":false,"type":"LEC","room":"00002"}],"crnNotes":[],"importantNotes":[],"course":{"termCode":"202501","dropDesc":"10 Day Drop","unitsLow":4,"reservedSeating":false,"shortDesc":"ECS 140A 001","gradeMode":"","unitsInd":"","seqNum":"001","printCRN":"19814","unitsHigh":0,"dropDate":"January, 17 2025 00:00:00","title":"Programming Languages ","subjectDesc":"Engineering Computer Science","courseNum":"140A","hidCRN":"19814","crn":"19814","subjectCode":"ECS"},"instructor":[{"lastName":"Thakur","instructorName":"A. Thakur","firstName":"Aditya","instructorEmail":"avthakur@ucdavis.edu","fullName":"Aditya Thakur"}]}]',
    '[{"courseDepartmentNotes":[],"courseSubjectNotes":[],"icmsData":{"newDescription":"Theory, application, and design of analog circuits. Methods of analysis including frequency response, SPICE simulation, and Laplace transform. Operational amplifiers and design of active filters.  ","creditLimit":"Students who have completed ENG 100 may receive 3.5 units of credit.","ge3":"QL,SE,VL","crossListing":"","prereq":" ENG 017 C- or better;  (MAT 022B or MAT 027B)"},"finalExam":{"examDate":"March, 19 2025 13:00:00"},"meeting":[{"thursday":false,"sunday":false,"startDate":"January, 06 2025 00:00:00","endTime":"2100","tuesday":true,"friday":false,"endDate":"March, 14 2025 00:00:00","daysString":"T","wednesday":false,"monday":false,"meetCode":"C","startTime":"1810","building":"Kemper Hall","description":"Laboratory","buildingCode":"KEMPER","saturday":false,"type":"LAB","room":"02161"},{"thursday":true,"sunday":false,"startDate":"January, 06 2025 00:00:00","endTime":"1730","tuesday":true,"friday":false,"endDate":"March, 14 2025 00:00:00","daysString":"TR","wednesday":false,"monday":false,"meetCode":"A","startTime":"1610","building":"Olson Hall","description":"Lecture","buildingCode":"OLSON","saturday":false,"type":"LEC","room":"00006"},{"thursday":true,"sunday":false,"startDate":"January, 06 2025 00:00:00","endTime":"1800","tuesday":true,"friday":false,"endDate":"March, 14 2025 00:00:00","daysString":"TR","wednesday":false,"monday":false,"meetCode":"D","startTime":"1740","building":"Olson Hall","description":"Discussion","buildingCode":"OLSON","saturday":false,"type":"DIS","room":"00217"}],"crnNotes":[],"importantNotes":[],"course":{"termCode":"202501","dropDesc":"10 Day Drop","unitsLow":5,"reservedSeating":false,"shortDesc":"EEC 100 A02","gradeMode":"","unitsInd":"","seqNum":"A02","printCRN":"20411","unitsHigh":0,"dropDate":"January, 17 2025 00:00:00","title":"Circuits II","subjectDesc":"Engineering Electrical & Compu","courseNum":"100","hidCRN":"20411","crn":"20411","subjectCode":"EEC"},"instructor":[{"lastName":"Kolner","instructorName":"B. Kolner","firstName":"Brian","instructorEmail":"bhkolner@ucdavis.edu","fullName":"Brian Kolner"}]}]']

courses = [json.loads(course_info) for course_info in courses]

def next_weekday(d, weekdays):
    """Change `d` to the next weekday in `weekdays`. If currenday matches,
    return `d` without modification"""
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
            byday.append(BYDAY_MAPPING[c])
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
            byday.append(DATETIME_MAPPING[c])
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

    f = tempfile.NamedTemporaryFile(prefix=str(datetime.now()), suffix='.ics',
                                    delete=False)
    f.write(cal.to_ical())
    f.close()
#    parsed_class_info = parse(class_info)
#    calendar = get_calendar(parsed_class_info)
#    write_export(path, calendar)
