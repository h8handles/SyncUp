# SyncUp

Coordinate group scheduling without the back-and-forth.

## Overview
SyncUp is a lightweight scheduling app designed to help groups quickly identify shared availability. Instead of relying on scattered messages, manual tracking, or repeated follow-ups, it gives organizers a simple flow for creating a group, inviting participants, collecting availability, and reviewing the best time options in one place.

This project is intentionally focused on the core scheduling workflow. It is built as a clean MVP(Minimum Viable Product) that demonstrates product thinking, usability, and practical full-stack implementation.

## The Problem SyncUp Solves
Scheduling is a small problem that creates a lot of unnecessary friction. Teams, clubs, student groups, project partners, and community organizers often lose time trying to answer basic questions:

- Who is available?
- When does the group overlap?
- What is the best time to meet?

SyncUp reduces that coordination overhead by making the process clearer and more structured.

## Key Features
- Create a scheduling group with a shareable invite code
- Join an existing group with a simple participant flow
- Submit availability by day and time range
- View the strongest overlap windows for a group
- Move through a consistent, easy-to-follow interface from setup to scheduling

## Who It Is For
SyncUp is well suited for groups that need a straightforward way to coordinate time without introducing unnecessary complexity.

- Small teams planning internal meetings
- Student groups and project teams
- Clubs, volunteer groups, and community organizers
- Founders or operators coordinating recurring sessions
- Anyone who wants a lightweight scheduling workflow for group availability

## Why It Matters
Even simple coordination problems affect momentum. When scheduling is unclear, meetings happen later, decisions slow down, and organizers spend time chasing responses instead of moving work forward.

SyncUp focuses on practical value:

- less manual follow-up
- clearer group coordination
- faster visibility into overlap windows
- a more organized experience than ad hoc chat threads

For a portfolio reviewer or prospective client, the project shows a product-minded approach to solving a common operational pain point with a focused and usable MVP.

## Current MVP Scope
SyncUp currently delivers the essential scheduling flow:

- group creation
- participant join flow
- availability submission
- best-time review by group
- shared interface styling across the main pages

This is an MVP, not a finished production platform. The current version is designed to prove the workflow, usability, and overall product direction with a clean end-to-end implementation.

## Portfolio Value
SyncUp works well as a portfolio project because it demonstrates more than just CRUD screens. It shows:

- a clear product concept with a real-world use case
- business-friendly UX thinking
- server-rendered application structure
- data-backed user and group flows
- a practical feature set that can be expanded over time

It is the kind of project that is easy for non-technical stakeholders to understand while still giving technical reviewers something concrete to evaluate.

## Technical Notes
SyncUp is currently built with:

- FastAPI
- Jinja templates
- SQLAlchemy
- SQLite
- Python

The application uses server-rendered templates for the UI and a lightweight relational database for MVP data storage. To run it locally:

`python -m uvicorn main:app --reload`
