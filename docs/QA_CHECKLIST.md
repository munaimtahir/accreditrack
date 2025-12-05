# QA_CHECKLIST.md – Release Checklist

Before any tagged release, confirm:

## Backend

- [ ] All migrations are committed and applied in staging.
- [ ] `pytest` passes with no failures.
- [ ] API endpoints documented or consistent with `API_INTERFACES.md`.
- [ ] Permission logic for each role (SuperAdmin, QAAdmin, Coordinator, Viewer) is verified.
- [ ] File upload size limits and allowed types tested.

## Frontend

- [ ] `npm run lint` passes.
- [ ] `npm test` passes (where tests exist).
- [ ] Main flows tested manually:
  - [ ] Login/logout.
  - [ ] Proforma template list and detail view.
  - [ ] Assignment creation.
  - [ ] Department coordinator workflow: updating statuses, uploading evidence, adding comments.
  - [ ] QAAdmin workflow: reviewing and verifying items.
  - [ ] Dashboard charts render without errors.

## UX / UI

- [ ] Pages work on common screen sizes (laptop, tablet width).
- [ ] No obvious layout breakages.
- [ ] Buttons and links are clearly labeled.
- [ ] Basic keyboard navigation works.

## Security

- [ ] No hardcoded secrets in repo.
- [ ] Auth is required for protected endpoints.
- [ ] Role‑restricted pages are not accessible by direct URL for unauthorized users.

## Documentation

- [ ] README and `docs/SETUP.md` are up to date.
- [ ] Any major architectural changes reflected in `docs/ARCHITECTURE.md` and `docs/DATA_MODEL.md`.
