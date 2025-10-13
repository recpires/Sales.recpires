---
name: Add generated diagrams
about: Generate PlantUML diagrams via GitHub Actions and add generated PNGs
---

## Goal

This PR brings generated PNGs for the PlantUML diagrams under `docs/diagrams/generated/` so they're visible in the repository browsing UI.

## What I changed
- Added generated PNGs produced by the `Render PlantUML diagrams` workflow.

## How to reproduce (if needed)
1. Create a branch and open a PR — the workflow `Render PlantUML diagrams` will run automatically.
2. Download the `diagrams` artifact from the Action run.
3. Commit the PNGs to `docs/diagrams/generated/` and push to the branch.

## Notes
- Source `.puml` files are in `docs/diagrams/` and remain authoritative.
- If diagrams change, re-run the workflow and update the PNGs.

---

/cc @team
