# Data format

## Calendar file (`data/<name>.json`)

| Field | Meaning |
|---|---|
| `year` | The year the calendar starts in |
| `source` | Who published it |
| `source_url` | The published document it was read from |
| `status` | `final`, `current` or `tentative` (see [Calendars and years](Calendars-and-Years)) |
| `retrieved` | Date the data was last checked |
| `note` | Free text |
| `events` | The list of events |

## Event

| Field | Meaning |
|---|---|
| `start` | First day, ISO date (`2026-05-27`) |
| `end` | Last day, **inclusive**. Missing means a single day |
| `name` | What it is |
| `category` | `public_holiday`, `school_days`, `exam_days`, `term_holidays` or `other` |

Dates are plain `YYYY-MM-DD` with no time zone. Parse them as local dates (Maldives is UTC+5), not as UTC instants, or events shift by a day.

## In `all.json`

Each event also carries:

| Field | Meaning |
|---|---|
| `id` | Stable identifier. It only changes if the event's name or start date changes |
| `calendar` | The year the file starts in |
| `file` | The file name without extension, such as `2026` or `2023-2024` |
| `status` | The calendar's status |

A JSON Schema for the calendar files is in `data/schema.json`.

## iCalendar (`.ics`)

One all-day event per entry. Time zone `Indian/Maldives`, event ids are stable, and long lines are folded as the standard requires.
