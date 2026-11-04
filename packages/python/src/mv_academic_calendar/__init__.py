"""Maldives academic calendar: offline data, no dependencies.

>>> import mv_academic_calendar as mv
>>> mv.is_public_holiday("2026-01-01")
True

Dates are plain local dates (no time zone). Functions accept ``datetime.date``, ``datetime.datetime`` or "YYYY-MM-DD" strings.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, datetime
from functools import lru_cache
from importlib import resources
from typing import Iterable, List, Optional, Union

__all__ = ["Event", "Calendar", "attribution", "updated", "calendars", "events", "events_on",
           "is_public_holiday", "next_event", "ics", "ics_files", "to_date"]

attribution = ("Maldives Academic Calendar, https://github.com/grootismore/mv-academic-calendar. "
               "Compiled from calendars published by the Ministry of Education, Republic of Maldives. Unofficial.")

DateLike = Union[str, date, datetime]
OneOrMany = Union[str, Iterable[str]]


@dataclass(frozen=True)
class Event:
    id: str           # stable across updates; only changes if the name or start date changes
    start: date       # first day
    end: date         # last day, inclusive (equals start for a single day)
    name: str
    category: str     # public_holiday | school_days | exam_days | term_holidays | other
    calendar: int     # the year the calendar starts in
    file: str         # "2026" or "2023-2024"
    status: str       # final | current | tentative


@dataclass(frozen=True)
class Calendar:
    file: str
    year: int
    status: str
    events: int
    retrieved: date   # when this calendar was last checked


def _load(name: str):
    return json.loads(resources.files(__package__).joinpath("_data", name).read_text(encoding="utf-8"))


@lru_cache(maxsize=None)
def _events() -> List[Event]:
    out = [Event(id=e["id"], start=date.fromisoformat(e["start"]), end=date.fromisoformat(e.get("end", e["start"])),
                 name=e["name"], category=e["category"], calendar=e["calendar"], file=e["file"], status=e["status"])
           for e in _load("all.json")["events"]]
    return sorted(out, key=lambda e: (e.start, e.end, e.name))


@lru_cache(maxsize=None)
def _calendars() -> List[Calendar]:
    return [Calendar(f["file"], f["year"], f["status"], f["events"], date.fromisoformat(f["retrieved"])) for f in _load("index.json")["files"]]


def to_date(d: DateLike) -> date:
    """Turn a string, date or datetime into a ``date`` (a datetime is read as the local date it shows)."""
    if isinstance(d, datetime):
        return d.date()
    if isinstance(d, date):
        return d
    try:
        return date.fromisoformat(str(d)[:10])
    except ValueError:
        raise TypeError(f'Expected a date like "2026-05-27", a date or a datetime, got {d!r}') from None


def _many(v: Optional[OneOrMany]) -> Optional[List[str]]:
    return None if v is None else [v] if isinstance(v, str) else [str(x) for x in v]


updated: date = max(c.retrieved for c in _calendars())     # when the bundled data was last checked


def calendars() -> List[Calendar]:
    """The calendars available. ``file`` is "2026" or "2023-2024"."""
    return list(_calendars())


def events(*, file: Optional[OneOrMany] = None, year: Optional[int] = None, category: Optional[OneOrMany] = None,
           status: Optional[OneOrMany] = None, start: Optional[DateLike] = None, end: Optional[DateLike] = None,
           text: Optional[str] = None) -> List[Event]:
    """Events sorted by date. Every filter is optional and they combine.

    ``start``/``end`` keep events that overlap that range (inclusive); ``text`` is a case-insensitive match on the name.
    """
    files, cats, stats = _many(file), _many(category), _many(status)
    lo, hi = (to_date(start) if start is not None else None), (to_date(end) if end is not None else None)
    needle = text.lower() if text else None
    return [e for e in _events()
            if (files is None or e.file in files) and (year is None or e.calendar == year)
            and (cats is None or e.category in cats) and (stats is None or e.status in stats)
            and (lo is None or e.end >= lo) and (hi is None or e.start <= hi)
            and (needle is None or needle in e.name.lower())]


def events_on(day: DateLike) -> List[Event]:
    """Everything happening on one day."""
    return events(start=day, end=day)


def is_public_holiday(day: DateLike) -> bool:
    """True if the day falls on a public holiday."""
    return any(e.category == "public_holiday" for e in events_on(day))


def next_event(day: DateLike, **filters) -> Optional[Event]:
    """The next event starting on or after ``day`` (accepts the same filters as ``events``), or None."""
    d = to_date(day)
    return next((e for e in events(**filters) if e.start >= d), None)


def ics_files() -> List[str]:
    """The names of the bundled iCalendar files."""
    return sorted(_load("ics.json"))


def ics(file: Union[str, int]) -> str:
    """The iCalendar text for a calendar, such as "2026" or "2023-2024"."""
    data = _load("ics.json")
    try:
        return data[str(file)]
    except KeyError:
        raise KeyError(f'No calendar named "{file}". Available: {", ".join(sorted(data))}') from None
