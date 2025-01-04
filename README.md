# Schedule Builder Export

UC Davis' Schedule Builder is a website where students register for courses.
Schedule Builder Export takes information from that site and return an `ics`
calendar file to be imported to Google Calendar.

## Features
The calendar contains:
* Recurring class events with auto-configured start and end date.
* Copies most useful information
    + Class name and section number
    + Class description
    + Event type (Lecture,discussion,...)
    + Location
* Final exam schedules

## How to use

First, log onto [Schedule Builder](https://my.ucdavis.edu/schedulebuilder) and
select the appropriate quarter. You should see your class schedule on this page.

Next, open the *Networks* console on your browser.
* On Firefox, press `Ctrl + Shift + E`
* On Google Chrome, press `f12` and select the `Network` tab on the newly
  appeared sidebar. If you can't see it, try expanding the sidebar.

Now, with the console opened, press `Ctrl + Shift + R` to fully refresh Schedule
Builder.

On the sidebar, you'll see all of the requests and responses. Several
consecutive entries are titled `search.cfc`. Locate them.

For each request, copy the response and paste the response into `courses`
variable of [main.py](main.py).
* On Firefox, to copy the response, right click the entry, hover over `Copy
Value`, and select `Copy Response`

Lastly, set up the appropriate path and run the script.
