# Licensing

> [!NOTE]
> This page explains how the project is licensed. It is **not legal advice**. If your use matters commercially or legally, check with a lawyer and, ideally, with the Ministry of Education.

## The short version

| What | Licence |
|---|---|
| Code (`build_ics.py`, workflows) | [MIT](../blob/main/LICENSE) |
| The compiled data and graphics | [CC BY 4.0](../blob/main/DATA-LICENSE.md): use it, change it, share it, give credit |
| The Ministry's own publications | Not licensed here. They belong to the Ministry |

## How to give credit

> Maldives Academic Calendar, https://github.com/grootismore/mv-academic-calendar. Compiled from calendars published by the Ministry of Education, Republic of Maldives. Unofficial.

Putting that line in your app's "about" or credits screen is enough. Please also keep it clear that the data is **unofficial**.

## What is stored, and what is not

- **Not stored:** any Ministry document. No PDF, scan, image or copy of a page is in this repository, and none has ever been in its history.
- **Stored:** the data read from those documents. That is dates, short event names and a category, in JSON and iCalendar form, plus a link to the original document (`source_url`) and a checksum of it so you can find and compare the original.

## Where the data comes from

The dates and holidays are read from calendars that the Ministry of Education publishes. The Ministry's website carries the notice
"© Copyright 2026 Ministry of Education, Republic of Maldives. All Rights Reserved" and does not publish a reuse or open-data policy.

That means:

- This project releases **its own work** (selecting, cleaning, structuring and identifying the entries, and the generated files) under CC BY 4.0, **to the extent the maintainer holds rights in it**.
- It does **not** redistribute the Ministry's documents, it does **not** claim to license them, and it does not claim the Ministry's permission.
- A calendar is a list of public dates that the Ministry publishes for everyone to follow, and this dataset is a restructured list of those facts. Whether and how they may be reused is still for the rights holder to say. If you build something commercial, consider asking the Ministry in writing.

## If you represent the Ministry

Please [open an issue](../issues/new) or start a [discussion](../discussions). Anything you ask to be changed or removed will be dealt with promptly.

## No warranty

The data is provided as is. It is read from PDFs, may contain mistakes, and tentative years can change. For anything that matters, check the Ministry's own calendar.

---
[← Contributing](Contributing) · [Home](Home)
