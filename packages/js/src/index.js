// Maldives academic calendar: offline data, no dependencies. Dates are plain "YYYY-MM-DD" strings (local dates, no time zone).
import ALL from "../data/all.json";
import INDEX from "../data/index.json";

export const attribution =
  "Maldives Academic Calendar, https://github.com/grootismore/mv-academic-calendar. Compiled from calendars published by the Ministry of Education, Republic of Maldives. Unofficial.";

const EVENTS = ALL.events
  .map(e => Object.freeze({ ...e, end: e.end ?? e.start }))          // `end` is always set; it is the last day, inclusive
  .sort((a, b) => a.start.localeCompare(b.start) || a.end.localeCompare(b.end) || a.name.localeCompare(b.name));

/** The newest `retrieved` date across all calendars: when the bundled data was last checked. */
export const updated = INDEX.files.map(f => f.retrieved).sort().pop();

const pad = n => String(n).padStart(2, "0");
/** Accepts "YYYY-MM-DD" (extra time text is ignored) or a Date (read in local time). */
export function toDate(d) {
  const s = d instanceof Date ? `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}` : String(d).slice(0, 10);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(s)) throw new TypeError(`Expected a date like "2026-05-27" or a Date, got ${JSON.stringify(d)}`);
  return s;
}
const list = v => (v === undefined ? undefined : Array.isArray(v) ? v : [v]);

/** The calendars available: `file` is "2026" or "2023-2024". */
export function calendars() {
  return INDEX.files.map(({ file, year, status, events, retrieved }) => ({ file, year, status, events, retrieved }));
}

/**
 * Events, sorted by date. Every filter is optional and they combine.
 * file: "2026" | "2023-2024" (or a list)   year: the calendar's start year   category / status: one or a list
 * from / to: keep events that overlap this range (inclusive)   text: case-insensitive match on the name
 */
export function events(filter = {}) {
  const file = list(filter.file)?.map(String), category = list(filter.category), status = list(filter.status);
  const from = filter.from === undefined ? undefined : toDate(filter.from), to = filter.to === undefined ? undefined : toDate(filter.to);
  const text = filter.text?.toLowerCase();
  return EVENTS.filter(e =>
    (!file || file.includes(e.file)) && (filter.year === undefined || e.calendar === filter.year) &&
    (!category || category.includes(e.category)) && (!status || status.includes(e.status)) &&
    (!from || e.end >= from) && (!to || e.start <= to) && (!text || e.name.toLowerCase().includes(text)));
}

/** Everything happening on one day. */
export const eventsOn = date => events({ from: date, to: date });

/** True if the day falls on a public holiday. */
export const isPublicHoliday = date => eventsOn(date).some(e => e.category === "public_holiday");

/** The next event starting on or after `date` (optionally of a category), or undefined. */
export function nextEvent(date, filter = {}) {
  const d = toDate(date);
  return events(filter).find(e => e.start >= d);
}
