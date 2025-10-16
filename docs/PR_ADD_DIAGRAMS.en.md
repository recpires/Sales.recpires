# Suggested PR: Add generated PlantUML PNGs

Use this template as the PR body when opening a Pull Request to add generated diagram PNGs.

Title: Add generated PlantUML diagram PNGs

Description:

- This PR adds generated PNGs for the PlantUML diagrams located in `docs/diagrams/`.
- The PNGs were produced by the `Render PlantUML diagrams` GitHub Actions workflow and added to `docs/diagrams/generated/`.

How the images were produced:
- The workflow `Render PlantUML diagrams` executes on GitHub and produces an artifact named `diagrams`. I downloaded the artifact and committed the PNGs to this branch.

Files added:
- `docs/diagrams/generated/*.png`

Notes for reviewers:
- The source `.puml` files remain the source of truth. The generated PNGs are convenience artifacts for quick browsing in the repository.
- If the PNGs need to be updated, re-run the workflow by pushing a new commit or running the workflow manually.

Commands I ran locally (if applicable):

```powershell
# Download artifact using gh CLI
gh run download --name diagrams -D docs/diagrams/generated
# Commit the files
git add docs/diagrams/generated/*.png
git commit -m "Add generated PlantUML PNGs"
git push origin add/generated-diagrams
```

If you want me to handle the PR creation and merging, grant me permission to push a branch or tell me to proceed and I'll prepare the branch and PR body (you'll still need to review/merge).
