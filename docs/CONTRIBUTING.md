# CONTRIBUTING.md

Thanks for contributing to AccrediTrack!

## Branching

- `main` – stable, deployable.
- Feature branches: `feature/<short-description>`.
- Bugfix branches: `fix/<short-description>`.

## Workflow

1. Create an issue or pick one from the board.
2. Create a feature/bugfix branch.
3. Implement changes with tests.
4. Run backend and frontend tests locally.
5. Open a PR with:
   - Summary of changes.
   - Screenshots or curl examples where helpful.
   - Checklist of impacted areas.

## Coding Standards

- **Backend (Python)**:
  - Follow PEP 8.
  - Use type hints where practical.
  - Keep business logic in services, not views.

- **Frontend (TypeScript)**:
  - Use functional components and hooks.
  - Keep components small; extract reusable pieces into `components/`.
  - Use Tailwind utility classes and shadcn/ui primitives.

## Commit Messages

Use descriptive commit messages, e.g.:

- `feat: add assignment creation endpoint`
- `fix: correct completion percentage calculation`
- `chore: update dependencies`

## Tests

- Add tests for any non-trivial logic.
- Do not significantly reduce test coverage without a reason documented in the PR.
