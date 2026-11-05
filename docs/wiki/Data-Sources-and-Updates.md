# Where the data comes from

All data is read from calendars published by the Maldives Ministry of Education at
[moe.gov.mv](https://www.moe.gov.mv/en/academic-calendar).

Each calendar file records the document it came from (`source_url`) and when it was published.
When the Ministry releases a newer version, the data is updated to follow it.

The JavaScript and Python packages are updated automatically too: once a day the data is compared with the last release, and a new package version is cut only when the calendars have changed.

Because the source documents are PDFs, entries are read automatically and then cleaned. Names can still contain small errors;
dates are the reliable part. If you find a mistake, please [report it](Contributing).

This project is not affiliated with or endorsed by the Ministry of Education.

---
[← FAQ](FAQ) · Next: [Contributing →](Contributing)
