---
type: assumption
id: ASS-001
title: "Students book rooms at least a day ahead"
description: "Most users plan their study sessions and would book online the day before."
status: invalidated
timestamp: 2026-03-02T09:30:00Z
project: neighbourhood-library
area: service-design
tags: [booking, behaviour]
derives_from: []
---

## Assumption
Most people who use the study rooms plan their sessions and would book
online at least a day ahead.

## Current basis
The brief from the library management; no data. It was the assumption
the first booking decision (DEC-001) was built on.

## How to validate
Two weeks of front-desk logs: who asks for a room, when, and whether
they had a booking.

## Review trigger
If more than a third of room requests are same-day, the assumption is
invalidated. Invalidated on 2026-03-20 (see INS-001 and the log).
