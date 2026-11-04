---
type: decision
id: DEC-002
title: "Two rooms bookable ahead, two only on the day"
description: "Split the study rooms between advance online booking and same-day booking at the desk or kiosk."
status: validated
timestamp: 2026-04-14T15:00:00Z
project: neighbourhood-library
area: service-design
tags: [booking, touchpoint]
resource: https://example.org/library/booking-screen-v2
supersedes: decisions/DEC-001_online-only-booking.md
derives_from:
  - concept/hypotheses/HYP-001_same-day-slots.md
  - concept/constraints/CON-001_card-number-only.md
resolves:
  - concept/gaps/GAP-001_peak-demand.md
---

## Decision
Rooms 1 and 2 stay bookable online up to seven days ahead; rooms 3 and 4
can be booked only on the day, at the desk, with the card number.

## Rationale
HYP-001 is supported by the pilot: turn-aways dropped by almost two
thirds with no increase in no-shows. CON-001 still holds: no contact
details are collected for either type of booking.

## Implications
- The booking screen (the `resource`) shows two kinds of rooms.
- It opens a new question on unused same-day slots (GAP-002).
- It enables OPP-001, the entrance screen.

## Review triggers
- If same-day rooms stay empty more than 40% of opening hours for two
  months → reconsider the split (see GAP-002).
- If the data protection policy changes (CON-001) → reminders become
  possible and no-shows may be handled differently.
