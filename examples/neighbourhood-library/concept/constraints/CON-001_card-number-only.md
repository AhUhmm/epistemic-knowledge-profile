---
type: constraint
id: CON-001
title: "Bookings store only the library card number"
description: "The booking service cannot store names, emails or phone numbers: only the card number and the slot."
status: active
timestamp: 2026-03-05T12:00:00Z
project: neighbourhood-library
area: data
tags: [privacy]
constraint_type: legal
derives_from: []
---

## Constraint
A booking record contains only the library card number, the room and the
slot. No name, email or phone number is stored by the booking service.

## Origin
The library's data protection policy, agreed with the municipality's DPO.

## Impact on design
Reminders and confirmations cannot be sent by email or SMS from the
booking service; a solution that needs contact details violates this.

## Review conditions
Only a revised data protection policy can lift it (status → removed,
logged).
