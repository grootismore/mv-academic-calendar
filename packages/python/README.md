# mv-academic-calendar

Maldives school academic calendar data, 2015 to 2027: terms, exams, mid-term breaks and public holidays.
Works offline, no dependencies. **Unofficial**, compiled from calendars published by the Ministry of Education.

```sh
pip install mv-academic-calendar
```

```python
import mv_academic_calendar as mv

mv.is_public_holiday("2026-01-01")                       # True
mv.events_on("2026-05-27")                               # what is happening that day
mv.next_event("2026-02-01", category="public_holiday")   # the next public holiday
mv.events(year=2026, category="exam_days")               # filter by calendar, category, status, date range, text
mv.calendars()                                           # which calendars exist, with their status
mv.ics("2026")                                           # the iCalendar file as text
```

Events are frozen dataclasses with real `date` objects (`start`, `end` inclusive), a `name`, a `category`
(`public_holiday`, `school_days`, `exam_days`, `term_holidays`, `other`), and the calendar's `status`
(`final`, `current`, `tentative`). Academic years that run August to June are named like `"2023-2024"`.

Dates have no time zone: pass a `date`, or a `datetime` (read as the local date it shows), or `"YYYY-MM-DD"`.

The data is bundled with the package. `mv_academic_calendar.updated` tells you when it was last checked.
For the newest data between package releases, fetch it from the repository.

## Licence

Code: MIT. The compiled data: CC BY 4.0. Please credit it, and say it is unofficial:

> Maldives Academic Calendar, https://github.com/grootismore/mv-academic-calendar. Compiled from calendars published by the Ministry of Education, Republic of Maldives. Unofficial.

(`mv_academic_calendar.attribution` holds that text.) The package stores no Ministry documents, only the dates and names extracted from them.

More: <https://github.com/grootismore/mv-academic-calendar>
