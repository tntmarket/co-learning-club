---
name: land
description: >-
  Commit and push changes in co-learning-club. Invoke only when the user
  explicitly requests landing, including /land, not for review, preparation,
  passing checks, or skill installation.
disable-model-invocation: true
metadata:
  delta-action: land
---

# Land

Carry out the requested commit and push. The invocation supplies landing
permission; do not ask for it again.

1. Read applicable repository instructions and inspect `git status`, the diff,
   current branch, and remotes. This project initially has an unborn `main`,
   `origin` pointing to `https://github.com/tntmarket/co-learning-club.git`, and
   no configured tests or contribution policy. Recheck current configuration;
   do not assume those facts remain unchanged. Publish to `origin/main`, never
   the `local` remote. Stop if the destination or intended change scope is
   unclear. Preserve unrelated work and never commit secrets.
2. Check applicable destination protections and repository requirements before
   pushing, using authenticated hosting tooling where needed. All required
   checks must have passed for the exact changes being landed. Pending, failing,
   missing, or unverifiable required checks are blockers. Do not invent test
   commands where none exist. If direct pushes are prohibited or required
   reviews are unmet, report the blocker rather than bypassing it.
3. Stage only the intended files with `git add -- <paths>` and create a concise
   descriptive commit with `GIT_EDITOR=true git commit -m "<message>"`.
   Create the initial commit when the repository has no commits. If no intended
   changes need committing, use the existing commit; if no commit exists and
   there is nothing to commit, report that there is nothing to land.
4. Fetch `origin` and inspect whether `origin/main` exists. If it exists,
   incorporate it without rewriting history, using a non-interactive merge
   (`GIT_EDITOR=true git merge --no-edit origin/main`) when needed. Resolve
   clear conflicts automatically only when the intended result is evident,
   preserving unrelated work. Stop and describe ambiguous conflicts; never
   guess, discard work, or automatically combine unrelated histories. Recheck
   applicable verification requirements after any merge or resolution.
5. Push the prepared commit with `git push origin HEAD:refs/heads/main`. Never
   force-push. On a concurrent remote update, fetch and incorporate it under
   the same conflict and verification rules before retrying. Stop for
   authentication, permission, protection, or verification blockers.
6. Verify with `git ls-remote origin refs/heads/main` that the destination
   contains the landed commit. If the remote advanced after the push, fetch
   and verify the landed commit is an ancestor of the remote tip. Report the
   commit and destination only after this verification. A commit, attempted
   push, or checks merely started are not landing success; explicitly report
   that changes have not landed when blocked.
