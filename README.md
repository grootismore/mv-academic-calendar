# mv-academic-calendar

Machine-readable Maldives school academic calendar (JSON + iCalendar), parsed from the
Ministry of Education's published calendars. **Unofficial.** Always check the
[MoE site](https://www.moe.gov.mv/en/academic-calendar) for the authoritative version.

## Files

- `data/<year>.json` – source of truth
- `build_ics.py` – JSON → ICS


## Schema

Each file: `year`, `source`, `source_url`, `status` (`tentative` | `final` | `current`),
`retrieved`, `note`, `events[]`.

Each event: `start` (ISO date), optional `end` (inclusive ISO date), `name`, `category`
(MoE's own: `public_holiday`, `school_days`, `exam_days`, `term_holidays`, `other`).
Files imported from a PDF also carry `pdf_sha256` (used to skip unchanged PDFs).

## Updating

The MoE publishes tentative and revised calendars. Update the JSON, set `status` and
`retrieved`, run `python build_ics.py`, commit.

## Coverage

2015, 2017–2027 (see `data/`).
