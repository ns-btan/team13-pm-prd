---
title: Process & Metadata Schema
---

# Process & Metadata Schema

How the 4 PM owners add, maintain, and promote PRDs in this repo.

## Metadata schema

Every per-PRD `docs/nplan-XXXX/index.md` starts with YAML frontmatter:

```yaml
---
nplan: 7523                                   # required — just the number
title: Scope as Object                        # required
status: active                                # required — see lifecycle below
phase: Concept                                # optional — Concept | Definition | Development | Rollout
domain: Admin Console / RBAC & Identity       # required
version: 0.4                                  # required — document version (semver-ish)
owner: jadrian                                # required — PM GitHub handle
updated: 2026-04-17                           # required — YYYY-MM-DD, keep fresh
shipped: 2026-06-15                           # set ONLY when moving to ga status
---
```

The home page scans all `docs/nplan-*/index.md` files and auto-groups them by `status`. **Do not** manually edit `docs/index.md` — it is generated.

## Lifecycle statuses

| status | Meaning | When to use |
|---|---|---|
| `active` | Currently being developed, PRD is the source of truth | The default — set when you create a new PRD |
| `beta` | Feature shipped to limited customers, PRD still iterating | When Limited Availability begins |
| `ga` | Generally available, PRD preserved for reference | When the feature ships to all customers; also set `shipped: YYYY-MM-DD` |
| `shelved` | Paused, may return | When work is deprioritized |
| `archived` | Will not be built / superseded by another PRD | When abandoning or consolidating |

## Adding a new PRD

1. Create the content folder at the repo root: `NPLAN-XXXX/`, containing the PRD MD, any linked MD, `assets/`, `mockup/`.
2. Create the Pages directory: `pages-preview/docs/nplan-xxxx/` (lowercase).
3. Inside it, create four symlinks:
   ```
   ln -s ../../../NPLAN-XXXX/NPLAN-XXXX-<Name>-PRD.md prd.md
   ln -s ../../../NPLAN-XXXX/NPLAN-XXXX-<Name>-Design-Spec.md ui-spec.md
   ln -s ../../../NPLAN-XXXX/assets assets
   ln -s ../../../NPLAN-XXXX/mockup mockup
   ```
4. Create `index.md` with the frontmatter above and a brief overview.
5. Add the section to `mkdocs.yml` nav.
6. Commit to a feature branch, open a PR.
7. Once merged, rebuild and push to `gh-pages` (see deployment below).

## Promoting a PRD through the lifecycle

Single-file change in the PRD's `index.md` frontmatter:

```diff
- status: active
+ status: ga
+ shipped: 2026-06-15
```

Commit, rebuild, push `gh-pages`. The home page automatically moves the entry from **Active** to **Shipped**. URL stays the same, so all existing links still work.

## Deployment

Until automated via GitHub Actions, the manual deploy is:

```bash
cd pages-preview
.venv/bin/mkdocs build --clean

cd ..
git worktree add /tmp/gh-pages gh-pages
cd /tmp/gh-pages
find . -mindepth 1 -maxdepth 1 ! -name '.git' ! -name '.nojekyll' -exec rm -rf {} +
cp -R /path/to/pages-preview/site/. .
git add -A && git commit -m "Rebuild site" && git push origin gh-pages
cd - && git worktree remove /tmp/gh-pages --force
```

## Conventions

- NPLAN numbers are always 4 digits (`7523`, not `07523`).
- PRD URLs are stable forever — once a PRD is published at `/nplan-7523/`, do not rename its folder even across lifecycle changes.
- Keep `updated:` fresh on every non-trivial edit — it's shown in the catalog.
- Owner is the single DRI. Co-authors are named inside the PRD content.
