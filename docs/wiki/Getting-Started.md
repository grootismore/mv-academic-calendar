# Getting started

Base URL: `https://raw.githubusercontent.com/grootismore/mv-academic-calendar/main/`

No key, no install.

## Everything in one request

```sh
curl -s https://raw.githubusercontent.com/grootismore/mv-academic-calendar/main/data/all.json
```

`all.json` holds every event from every calendar. Each event has a stable `id`, so you can load it into a database and update it later.

## One calendar

```sh
curl -s https://raw.githubusercontent.com/grootismore/mv-academic-calendar/main/data/2026.json
```

## What is available

`data/index.json` lists every calendar with its status, number of events and file paths. Start there if your code needs to discover the years.

## Subscribe in a calendar app

Add `data/2026.ics` as a **URL calendar** (Apple Calendar: File → New Calendar Subscription. Google Calendar: Other calendars → From URL).
The file asks apps to refresh once a day.

## Examples

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
