# Maldives Academic Calendar for Python

**`mv-academic-calendar`** gives you the Maldives school academic calendar and public holidays as a small, offline Python library:
terms, exams, mid-term breaks and holidays for every year from 2015 to 2027, plus the iCalendar (ICS) file for each calendar.

- **Works offline.** The data ships inside the package. No API key, no network calls, no dependencies.
- **Ready to use.** Check a public holiday, list a day's events, find the next holiday, or filter by year, category and dates.
- **Typed.** Events are frozen dataclasses with real `date` objects, and the package ships type hints.
- **Python 3.11 or newer.**

> **Unofficial.** The data is compiled from calendars published by the Ministry of Education of the Maldives. Always check the [Ministry's site](https://www.moe.gov.mv/en/academic-calendar) for the authoritative version.

## Install

```sh
pip install mv-academic-calendar
```

## Quick start

```python
import mv_academic_calendar as mv

mv.is_public_holiday("2026-01-01")                       # True
mv.events_on("2026-05-27")                               # what is happening on that day
mv.next_event("2026-02-01", category="public_holiday")   # the next Maldives public holiday
mv.events(year=2026, category="exam_days")               # exam periods in 2026
mv.calendars()                                           # every calendar with its status
```

### Get the Maldives public holidays for a year

```python
for h in mv.events(year=2026, category="public_holiday"):
    print(h.start, h.end, h.name)
```

### Is today a school holiday?

```python
from datetime import date

off = [e for e in mv.events_on(date.today()) if e.category in ("public_holiday", "term_holidays")]
print(f"No school: {off[0].name}" if off else "Normal day")
```

### Get the iCalendar (ICS) file

```python
mv.ics_files()      # ["2015", "2017", ..., "2023-2024", ..., "2027"]
mv.ics("2026")      # iCalendar text: serve it, save it, or subscribe to it
```

## API

| Function | Returns |
|---|---|
| `is_public_holiday(day)` | `True` if the day falls on a public holiday |
| `events_on(day)` | every event happening on that day |
| `next_event(day, **filters)` | the next event starting on or after the day, or `None` |
| `events(**filters)` | events sorted by date. Filter by `year`, `file`, `category`, `status`, `start`, `end`, `text` |
| `calendars()` | the available calendars: `file`, `year`, `status`, `events`, `retrieved` |
| `ics(file)` / `ics_files()` | the iCalendar text for a calendar, and the available names |
| `updated` | the date the bundled data was last checked |
| `attribution` | a ready-made credit line |

An `Event` has `id`, `start`, `end`, `name`, `category`, `calendar`, `file` and `status`.

- **Dates** have no time zone. Pass a `date`, a `datetime` (read as the local date it shows) or `"YYYY-MM-DD"`. `end` is the last day, inclusive.
- **`category`** is `public_holiday`, `school_days`, `exam_days`, `term_holidays` or `other`.
- **`status`** is `final`, `current` or `tentative`. Tentative calendars can still change.
- **`file`** is `"2026"`, or `"2023-2024"` for the academic years that run August to June.

## About the data

Calendars cover 2015, 2017 to 2020, the academic years 2021-2022, 2022-2023 and 2023-2024, and 2024 to 2027. Each is the newest version the Ministry has published.
The package is a snapshot: a new version is released whenever the calendars change. See the [changelog](https://github.com/grootismore/mv-academic-calendar/blob/main/CHANGELOG.md).
For the very latest data between releases, fetch [`data/all.json`](https://raw.githubusercontent.com/grootismore/mv-academic-calendar/main/data/all.json) from the repository.

## Also available

- **JavaScript and TypeScript:** [`npm install mv-academic-calendar`](https://www.npmjs.com/package/mv-academic-calendar), with the same API
- **Raw JSON and ICS files:** [the repository](https://github.com/grootismore/mv-academic-calendar), no install needed
- **Guides:** the [wiki](https://github.com/grootismore/mv-academic-calendar/wiki), including how to load the data into a database

## Licence

Code: MIT. The compiled data: CC BY 4.0. Please credit it, and say it is unofficial:

> Maldives Academic Calendar, https://github.com/grootismore/mv-academic-calendar. Compiled from calendars published by the Ministry of Education, Republic of Maldives. Unofficial.

`mv_academic_calendar.attribution` holds that text. The package stores no Ministry documents, only the dates and names extracted from them.

Questions, ideas or a wrong date? [Open a discussion or an issue](https://github.com/grootismore/mv-academic-calendar).
