# Maldives Academic Calendar for JavaScript and TypeScript

**`mv-academic-calendar`** gives you the Maldives school academic calendar and public holidays as a small, offline library:
terms, exams, mid-term breaks and holidays for every year from 2015 to 2027, plus the iCalendar (ICS) file for each calendar.

- **Works offline.** The data ships inside the package. No API key, no network calls, no dependencies.
- **Ready to use.** Check a public holiday, list a day's events, find the next holiday, or filter by year, category and dates.
- **ESM, CommonJS and TypeScript.** Types are included.
- **Small.** About 56 kB compressed.

> **Unofficial.** The data is compiled from calendars published by the Ministry of Education of the Maldives. Always check the [Ministry's site](https://www.moe.gov.mv/en/academic-calendar) for the authoritative version.

## Install

```sh
npm install mv-academic-calendar
```

## Quick start

```js
import { isPublicHoliday, eventsOn, nextEvent, events, calendars } from "mv-academic-calendar";

isPublicHoliday("2026-01-01");                                // true
eventsOn("2026-05-27");                                       // what is happening on that day
nextEvent("2026-02-01", { category: "public_holiday" });      // the next Maldives public holiday
events({ year: 2026, category: "exam_days" });                // exam periods in 2026
calendars();                                                  // every calendar with its status
```

### Get the Maldives public holidays for a year

```js
const holidays = events({ year: 2026, category: "public_holiday" });
for (const h of holidays) console.log(h.start, h.end, h.name);
```

### Is a school day a holiday?

```js
const day = new Date();                                       // a Date is read as a local date
const off = eventsOn(day).filter(e => ["public_holiday", "term_holidays"].includes(e.category));
console.log(off.length ? `No school: ${off[0].name}` : "Normal day");
```

### Get the iCalendar (ICS) file

The calendar files are a separate entry point, so apps that only need the data stay small.

```js
import { ics, files } from "mv-academic-calendar/ics";

files();            // ["2015", "2017", ..., "2023-2024", ..., "2027"]
ics("2026");        // iCalendar text: serve it, download it, or subscribe to it
```

## API

| Function | Returns |
|---|---|
| `isPublicHoliday(date)` | `true` if the day falls on a public holiday |
| `eventsOn(date)` | every event happening on that day |
| `nextEvent(date, filter?)` | the next event starting on or after the date, or `undefined` |
| `events(filter?)` | events sorted by date. Filter by `year`, `file`, `category`, `status`, `from`, `to`, `text` |
| `calendars()` | the available calendars: `file`, `year`, `status`, `events`, `retrieved` |
| `ics(file)` | the iCalendar text for a calendar (from `mv-academic-calendar/ics`) |
| `updated` | the date the bundled data was last checked |
| `attribution` | a ready-made credit line |

Each event is `{ id, start, end, name, category, calendar, file, status }`.

- **Dates** are plain `"YYYY-MM-DD"` strings with no time zone. `end` is the last day, inclusive, and is always set. Pass `"YYYY-MM-DD"` or a `Date` (read as a local date).
- **`category`** is `public_holiday`, `school_days`, `exam_days`, `term_holidays` or `other`.
- **`status`** is `final`, `current` or `tentative`. Tentative calendars can still change.
- **`file`** is `"2026"`, or `"2023-2024"` for the academic years that run August to June.

## About the data

Calendars cover 2015, 2017 to 2020, the academic years 2021-2022, 2022-2023 and 2023-2024, and 2024 to 2027. Each is the newest version the Ministry has published.
The package is a snapshot: a new version is released whenever the calendars change. See the [changelog](https://github.com/grootismore/mv-academic-calendar/blob/main/CHANGELOG.md).
For the very latest data between releases, fetch [`data/all.json`](https://raw.githubusercontent.com/grootismore/mv-academic-calendar/main/data/all.json) from the repository.

## Also available

- **Python:** [`pip install mv-academic-calendar`](https://pypi.org/project/mv-academic-calendar/), with the same API
- **Raw JSON and ICS files:** [the repository](https://github.com/grootismore/mv-academic-calendar), no install needed
- **Guides:** the [wiki](https://github.com/grootismore/mv-academic-calendar/wiki), including how to load the data into a database

## Licence

Code: MIT. The compiled data: CC BY 4.0. Please credit it, and say it is unofficial:

> Maldives Academic Calendar, https://github.com/grootismore/mv-academic-calendar. Compiled from calendars published by the Ministry of Education, Republic of Maldives. Unofficial.

The `attribution` export holds that text. The package stores no Ministry documents, only the dates and names extracted from them.

Questions, ideas or a wrong date? [Open a discussion or an issue](https://github.com/grootismore/mv-academic-calendar).
