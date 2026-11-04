---
type: insight
id: INS-001
title: "Two thirds of room requests are walk-ins"
description: "Front-desk logs show most requests come from people already in the library, without a booking."
status: active
timestamp: 2026-03-20T17:00:00Z
project: neighbourhood-library
area: service-design
tags: [booking, research]
resource: research/front-desk-log-summary.md
derives_from:
  - concept/gaps/GAP-001_peak-demand.md
---

## Insight
Two thirds of study-room requests come from people already in the
library, deciding on the spot. Demand peaks between 15:00 and 18:00 on
weekdays, when secondary schools close.

## Evidence
Two weeks of front-desk logs (412 requests), summarised in the
`resource` document. Synthetic data for this example.

## Implications
An online-only, book-ahead service would turn away most of the people
who actually use the rooms.

## Review trigger
A new log after the redesign: if the share of walk-ins changes by more
than 15 points, this insight should be superseded.
