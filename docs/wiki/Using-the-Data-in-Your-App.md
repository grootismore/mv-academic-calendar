# Using the data in your app

## The quickest way: a package

If you work in JavaScript or Python, skip the files and install a package. Both work offline, have no dependencies and share one API.

```sh
npm install mv-academic-calendar     # JavaScript and TypeScript
pip install mv-academic-calendar     # Python 3.11 or newer
```

```js
import { isPublicHoliday, eventsOn, nextEvent, events, calendars } from "mv-academic-calendar";
isPublicHoliday("2026-01-01");                               // true
nextEvent("2026-02-01", { category: "public_holiday" });
events({ year: 2026, category: "exam_days" });
```

```python
import mv_academic_calendar as mv
mv.is_public_holiday("2026-01-01")                           # True
mv.next_event("2026-02-01", category="public_holiday")
mv.events(year=2026, category="exam_days")
```

> [!NOTE]
> A package is a snapshot of the data at its release. For the very latest, fetch `data/all.json` from the repository instead, or update the package.

Prefer to load the data into your own database or API? Read on.

> [!NOTE]
> Load `data/all.json` and **upsert each event by its `id`**. That is all most apps need.

## Table

```sql
CREATE TABLE academic_events (
  id         text PRIMARY KEY,
  calendar   integer NOT NULL,
  file       text NOT NULL,
  status     text NOT NULL,
  category   text NOT NULL,
  name       text NOT NULL,
  start_date date NOT NULL,
  end_date   date            -- inclusive; NULL means one day
);
```

## Keeping it in sync

Events can be renamed or removed when the Ministry revises a calendar. To handle that, sync one calendar at a time:
delete your rows for that `file`, then insert its events, inside one transaction. Running it once a day is plenty.

## Mobile apps

- Bundle a copy of `all.json` so the app works offline, then refresh it from your own backend.
- Parse dates as local dates, not UTC.
- For phone calendars, subscribe to the `.ics` file instead of importing events.

## Node and PostgreSQL

```js
import pg from "pg";
const { events } = await (await fetch("https://raw.githubusercontent.com/grootismore/mv-academic-calendar/main/data/all.json")).json();
const db = new pg.Client({ connectionString: process.env.DATABASE_URL }); await db.connect();
for (const e of events)
  await db.query(
    `INSERT INTO academic_events (id, calendar, file, status, category, name, start_date, end_date)
     VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
     ON CONFLICT (id) DO UPDATE SET status=$4, category=$5, name=$6, start_date=$7, end_date=$8`,
    [e.id, e.calendar, e.file, e.status, e.category, e.name, e.start, e.end ?? null]);
```

---
[← Calendars and years](Calendars-and-Years) · Next: [FAQ →](FAQ)
