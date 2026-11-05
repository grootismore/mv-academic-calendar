# Getting started

Base URL: `https://raw.githubusercontent.com/grootismore/mv-academic-calendar/main/`

No key. No install. Pick the way that suits you.

## Everything at once

`all.json` holds every event from every calendar, each with a stable `id`.

```sh
curl -s https://raw.githubusercontent.com/grootismore/mv-academic-calendar/main/data/all.json
```

## One calendar

```sh
curl -s https://raw.githubusercontent.com/grootismore/mv-academic-calendar/main/data/2026.json
```

> [!TIP]
> `data/index.json` lists every calendar with its status, number of events and file paths. Start there if your code needs to discover the years.

## As a package

```sh
npm install mv-academic-calendar
pip install mv-academic-calendar
```

See [Using the data in your app](Using-the-Data-in-Your-App) for the functions.

## In your own code

<details>
<summary><b>Python</b></summary>

```python
import requests
B = "https://raw.githubusercontent.com/grootismore/mv-academic-calendar/main/"
events = requests.get(B + "data/all.json").json()["events"]
holidays = [e for e in events if e["category"] == "public_holiday" and e["calendar"] == 2026]
```
</details>

<details>
<summary><b>JavaScript</b></summary>

```js
const B = "https://raw.githubusercontent.com/grootismore/mv-academic-calendar/main/";
const { events } = await (await fetch(B + "data/all.json")).json();
```
</details>

## In a calendar app

Add `data/2026.ics` as a **URL calendar**.

| App | Where |
|---|---|
| Apple Calendar | File → New Calendar Subscription |
| Google Calendar | Other calendars → From URL |
| Outlook | Add calendar → Subscribe from web |

The file asks apps to refresh once a day.

---
Next: [Data format →](Data-Format)
