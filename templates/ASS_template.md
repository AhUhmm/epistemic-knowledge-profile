---
type: assumption
id: ASS-XXX
title: ""
description: ""
status: open                   # open | partially_validated | validated | invalidated
timestamp: YYYY-MM-DDTHH:MM:SSZ
project: PROJECT_NAME
area:                          # optional
tags: []
resource:                      # optional
derives_from: []
risk:                          # optional — high | medium | low; only if a rule branches on it
semantic_tags: []
---

## Assumption
[What we treat as true in order to proceed.]

## Current basis
[Why we believe it — sources, signals, or explicit absence of data.]

## How to validate
[Concrete verification routes: interviews, logs, tests.]

## Review trigger
[The evidence threshold that flips this to validated or invalidated.
A validation/invalidation is a status transition logged in log.md;
if a commitment follows, it is a NEW decision with `derives_from`
pointing here.]
