# mv-academic-calendar

Machine-readable Maldives school academic calendar (JSON + iCalendar), parsed from the
Ministry of Education's published calendars. **Unofficial.** Always check the
[MoE site](https://www.moe.gov.mv/en/academic-calendar) for the authoritative version.
Parsed from PDFs, so some entry names may contain stray characters; treat dates as the reliable part.

## Use it (no install, no key)

Base URL: `https://raw.githubusercontent.com/grootismore/mv-academic-calendar/main/`

| File | What |
|---|---|
| `data/index.json` | list of available years: status, entry count, paths |
| `data/all.json` | every event from every year in one flat list |
| `data/<year>.json` | one year, with source and status |
| `data/<year>.ics` | the same as iCalendar, subscribe in any calendar app |
| `data/schema.json` | JSON Schema for the year files |
| `llms.txt` | short pointer file for AI tools |

```sh
curl -s https://raw.githubusercontent.com/grootismore/mv-academic-calendar/main/data/2026.json
```
```python
import requests
B = "https://raw.githubusercontent.com/grootismore/mv-academic-calendar/main/"
events = requests.get(B + "data/all.json").json()["events"]
holidays = [e for e in events if e["category"] == "public_holiday" and e["calendar"] == 2026]
```
```js
const B = "https://raw.githubusercontent.com/grootismore/mv-academic-calendar/main/";
const { events } = await (await fetch(B + "data/all.json")).json();
```

Calendar subscription: add `…/data/2026.ics` as a URL calendar.

## Format

Each event: `start` (ISO date), optional `end` (inclusive ISO date; absent means one day), `name`, `category`.
In `all.json` each event also has a stable `id`, `calendar` (the year file it came from) and `status`.

- `category`: `public_holiday`, `school_days`, `exam_days`, `term_holidays`, `other` (MoE's own)
- `status`: `final` (MoE final) > `current` (taken from the MoE page, no status stated) > `tentative` (MoE draft; may change)

## Seed your own app or database

Fetch `data/all.json` and upsert each event by its `id`. The `id` is stable: it only changes if an event's
name or start date changes. Use `index.json` (`retrieved` per year) to see whether anything changed since your last sync.

Suggested table:

```sql
CREATE TABLE academic_events (
  id        text PRIMARY KEY,      -- from all.json
  calendar  integer NOT NULL,      -- year file
  status    text NOT NULL,         -- final | current | tentative
  category  text NOT NULL,
  name      text NOT NULL,
  start_date date NOT NULL,
  end_date   date                  -- inclusive; NULL = one day
);
```

**Push to a REST endpoint** (any language; here with `curl` + `jq`):

```sh
B=https://raw.githubusercontent.com/grootismore/mv-academic-calendar/main
curl -s $B/data/all.json | jq -c '.events[]' | while read -r ev; do
  curl -s -X PUT "https://your-api.example.com/academic-events/$(echo "$ev" | jq -r .id)" \
done
```
Or send the whole list in one request: `curl -s $B/data/all.json | curl -X POST https://your-api.example.com/academic-events/bulk -H "Content-Type: application/json" --data-binary @-`

**Node / TypeScript (Postgres, upsert):**

```js
import pg from "pg";
const { events } = await (await fetch("https://raw.githubusercontent.com/grootismore/mv-academic-calendar/main/data/all.json")).json();
const db = new pg.Client({ connectionString: process.env.DATABASE_URL }); await db.connect();
for (const e of events)
  await db.query(
    `INSERT INTO academic_events (id, calendar, status, category, name, start_date, end_date)
     VALUES ($1,$2,$3,$4,$5,$6,$7)
     ON CONFLICT (id) DO UPDATE SET status=$3, category=$4, name=$5, start_date=$6, end_date=$7`,
    [e.id, e.calendar, e.status, e.category, e.name, e.start, e.end ?? null]);
```

**Python (any HTTP API):**

```python
import requests
B = "https://raw.githubusercontent.com/grootismore/mv-academic-calendar/main/"
for e in requests.get(B + "data/all.json").json()["events"]:
    requests.put(f"https://your-api.example.com/academic-events/{e['id']}", json=e, headers={"Authorization": "Bearer …"})
```

**Keeping in sync / removals.** Events can be removed or renamed upstream. To handle that, sync one year at a time:
delete your rows where `calendar = <year>`, then insert that year's events (inside one transaction), or delete ids that are no longer in the feed.
Run it on a schedule (cron, a GitHub Action, a cloud scheduler); once a day is plenty.

**Mobile apps.** Don't ship the raw GitHub URL as your only source:
- Bundle a copy of `all.json` in the app so it works offline, then refresh it from your own backend (seeded as above) or from the raw URL with an `If-None-Match` header (the raw host sends an `ETag`; a `304` means nothing changed).
- Dates are plain `YYYY-MM-DD` with no time zone: parse them as local dates (Maldives is UTC+5), not as UTC instants, or events will shift a day.
- For calendar apps (iOS/Android), subscribe to `data/<year>.ics` instead of importing events.

## Files and updating

`data/<year>.json` is the source of truth. `*.ics`, `index.json` and `all.json` are generated by
`python build_ics.py` (stdlib only), and a GitHub Action regenerates them whenever a year file changes.

Maintained by the repo owner. For questions or inquiries, please [open an issue](../../issues/new).
