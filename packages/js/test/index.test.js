import test from "node:test";
import assert from "node:assert/strict";
import { createRequire } from "node:module";
import { calendars, events, eventsOn, isPublicHoliday, nextEvent, updated, attribution, toDate } from "../dist/index.js";
import { ics, files } from "../dist/ics.js";

test("calendars lists every year with a status", () => {
  const c = calendars();
  assert.ok(c.length >= 12);
  assert.ok(c.every(x => x.file && ["final", "current", "tentative"].includes(x.status) && x.events > 0));
  assert.ok(c.some(x => x.file === "2023-2024"));
});

test("events: filters combine and results are sorted", () => {
  const all = events();
  assert.ok(all.length > 400);
  assert.ok(all.every((e, i) => i === 0 || all[i - 1].start <= e.start));
  assert.ok(all.every(e => e.end >= e.start));
  const hol = events({ year: 2026, category: "public_holiday" });
  assert.ok(hol.length > 3 && hol.every(e => e.calendar === 2026 && e.category === "public_holiday"));
  assert.ok(events({ file: "2023-2024" }).every(e => e.file === "2023-2024"));
  assert.ok(events({ text: "ramadan" }).length > 0);
  assert.deepEqual(events({ category: ["exam_days", "other"], year: 2026 }).map(e => e.category).filter(c => c !== "exam_days" && c !== "other"), []);
});

test("eventsOn, isPublicHoliday and nextEvent", () => {
  assert.ok(isPublicHoliday("2026-01-01"));
  assert.ok(isPublicHoliday(new Date(2026, 0, 1)));                       // a Date is read as a local date
  assert.ok(eventsOn("2026-05-27").some(e => /adha/i.test(e.name)));
  assert.equal(isPublicHoliday("2026-03-02"), false);
  const n = nextEvent("2026-01-02", { category: "public_holiday" });
  assert.ok(n && n.start >= "2026-01-02" && n.category === "public_holiday");
});

test("bad dates are rejected, helpers exist", () => {
  assert.throws(() => eventsOn("tomorrow"), TypeError);
  assert.equal(toDate("2026-05-27T10:00:00Z"), "2026-05-27");
  assert.match(updated, /^\d{4}-\d{2}-\d{2}$/);
  assert.match(attribution, /Unofficial/);
});

test("ics entry point returns iCalendar text", () => {
  assert.ok(files().includes("2026"));
  assert.match(ics("2026"), /^BEGIN:VCALENDAR/);
  assert.throws(() => ics("1999"), RangeError);
});

test("CommonJS build works too", () => {
  const require = createRequire(import.meta.url);
  const cjs = require("../dist/index.cjs");
  assert.equal(cjs.events({ year: 2026 }).length, events({ year: 2026 }).length);
  assert.match(require("../dist/ics.cjs").ics(2026), /VCALENDAR/);
});
