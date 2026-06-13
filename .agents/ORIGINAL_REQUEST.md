# Original User Request

## Initial Request — 2026-06-10T18:36:28Z

# Teamwork Project Prompt — Draft

Build a "Deal of the Day" section that displays the top 5 absolute best car deals. This requires a new backend endpoint to fetch the data and a frontend component to display it on the homepage.

Working directory: /Users/robert/car-sniper

Integrity mode: development

## Requirements

### R1. Top Deals Backend Endpoint
Create a FastAPI endpoint (e.g., `/api/deals/top`) that fetches the top 5 car deals from the database. The deals must be `active`, added within the last 48 hours, and sorted by their calculated Deal Score (highest first).

### R2. Deal of the Day UI Component
Create a `DealOfTheDay` React component and integrate it into the homepage. The component must display the 5 cars using a modern glassmorphism aesthetic (e.g., sleek dark mode cards, `backdrop-filter: blur`, and micro-animations on hover).

### R3. Data Safety Constraint
Do not modify the existing database schema, drop tables, or delete any data. Only write read-only queries for fetching the deals.

## Acceptance Criteria

### Backend Functionality
- [ ] A programmatic test script can hit the new endpoint and verify it returns a valid JSON list of up to 5 cars.
- [ ] The returned cars strictly have `active = TRUE` and a creation/update timestamp within the last 48 hours.

### Frontend Integration & Aesthetics
- [ ] The `DealOfTheDay` component is successfully imported and rendered on the main homepage.
- [ ] An agent-as-judge can verify the CSS code includes glassmorphism properties (e.g., `backdrop-filter`, semi-transparent backgrounds) and hover transitions.
