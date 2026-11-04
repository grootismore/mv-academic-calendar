# mv-academic-calendar

Maldives school academic calendar data, 2015 to 2027: terms, exams, mid-term breaks and public holidays.
Works offline, no dependencies, ESM and CommonJS, TypeScript types included. **Unofficial**, compiled from calendars published by the Ministry of Education.

```sh
npm install mv-academic-calendar
```

```js
import { isPublicHoliday, eventsOn, nextEvent, events, calendars } from "mv-academic-calendar";

isPublicHoliday("2026-01-01");                                  // true
eventsOn("2026-05-27");                                         // what is happening that day
nextEvent("2026-02-01", { category: "public_holiday" });        // the next public holiday
events({ year: 2026, category: "exam_days" });                  // filter by calendar, category, status, date range, text
calendars();                                                    // which calendars exist, with their status
```

The iCalendar files are a separate entry point, so apps that don't need them stay small:

```js
import { ics } from "mv-academic-calendar/ics";
ics("2026");                                                    // iCalendar text, ready to serve or download
```

Each event is `{ id, start, end, name, category, calendar, file, status }`. Dates are plain `"YYYY-MM-DD"` strings and `end` is the
last day, inclusive (always set). `category` is `public_holiday`, `school_days`, `exam_days`, `term_holidays` or `other`; `status` is
`final`, `current` or `tentative`. Academic years that run August to June are named like `"2023-2024"`.

Dates have no time zone: pass `"YYYY-MM-DD"` or a `Date` (read in local time).

The data is bundled with the package. `updated` tells you when it was last checked. For the newest data between releases, fetch it from the repository.

## Licence

Code: MIT. The compiled data: CC BY 4.0. Please credit it, and say it is unofficial:

> Maldives Academic Calendar, https://github.com/grootismore/mv-academic-calendar. Compiled from calendars published by the Ministry of Education, Republic of Maldives. Unofficial.

(`attribution` holds that text.) The package stores no Ministry documents, only the dates and names extracted from them.

More: <https://github.com/grootismore/mv-academic-calendar>
