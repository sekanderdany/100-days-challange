# How Not to Break Production

## Option 1: Delete & Recreate the Working Branch

**Best for:** Solo developers or personal feature branches after successful PR merge

This is the cleanest and most professional solution for keeping your working branch synchronized with main after your changes are merged.

### Workflow

After your PR is merged into main:

```bash
# Switch to main and get latest changes
git checkout main
git pull origin main

# Delete your old feature branch (locally and remotely)
git branch -D works-on-my-machine
git push origin --delete works-on-my-machine

# Create fresh branch from updated main
git checkout -b works-on-my-machine
git push -u origin works-on-my-machine
```

### Why This Works

- `works-on-my-machine` is always based on latest main
- No rebasing needed
- No "behind/ahead" confusion
- GitHub history stays readable
- Zero chance of accidentally pushing old/conflicting code
- Fresh start eliminates merge artifacts

### ⚠️ Important Notes

- **Only use on personal/feature branches**, never on `main`, `production`, or shared branches
- **Ensure your PR is fully merged** before deleting the branch
- **Save any uncommitted work** before deleting (use `git stash` if needed)
- **Not suitable** if others are working on the same branch

💡 **Pro Tip:** This is how many senior engineers work on personal projects - clean slate after each PR merge.


---

## Option 2: Stash → Fetch → Merge → Apply → Commit

**Best for:** Working across multiple devices on the same feature branch

This approach safely synchronizes your work-in-progress code across devices without losing uncommitted changes.

### When to Use This

✅ **Use when:**
- Switching between work laptop and home desktop
- Working on a personal feature branch
- You have uncommitted changes you want to preserve
- The branch is not shared with other developers

❌ **Don't use when:**
- Working on `main`, `production`, or any shared branch
- Multiple team members are working on the same branch
- You're ready to commit and push normally

### Workflow

```bash
# Check current status and what's uncommitted
git status
git diff  # Review your changes

# Stash your work in progress
git stash push -m "WIP before syncing from other device"

# Fetch and merge remote changes
git fetch origin
git merge origin/works-on-my-machine  # Sync your feature branch
git merge origin/main                 # Get latest from main

# Apply your stashed changes back
git stash pop
```

### Handling Conflicts

If `git stash pop` results in conflicts:

```bash
# Check conflicted files
git status

# Open conflicted files and resolve conflicts manually:
# <<<<<<< HEAD
# (remote version)
# =======
# (your local version)
# >>>>>>> stash

# After resolving conflicts
git add .
git commit -m "Continue work after syncing from other device"

# TEST before pushing!
npm test        # or: pytest, go test, etc.
npm run build   # ensure no build errors

# If tests pass, push
git push
```

### 🛡️ Production Safety Tips

1. **Always test after resolving conflicts** - conflicts can introduce bugs
2. **Review your changes** with `git diff` before committing
3. **Use descriptive commit messages** for audit trail
4. **Never skip tests** even for "small" conflicts
5. **This is for feature branches only** - never on production branches

---

## Option 2A: Multiple Developers on Same Feature Branch

**Best for:** Pair programming, collaborative feature development

When multiple developers need to work on the same feature branch simultaneously, communication and coordination are critical.

### When This Happens

✅ **Valid scenarios:**
- Pair programming on complex features
- Team working on large feature requiring multiple skillsets
- Temporary collaboration on urgent feature
- Mob programming sessions

⚠️ **Warning signs you need separate branches:**
- Frequent merge conflicts
- Developers stepping on each other's code
- Different features being built simultaneously
- Consider splitting into `feature/main-feature` and `feature/main-feature-subpart`

### Safe Workflow for Shared Branches

#### Before Starting Work Each Day

```bash
# 1. Always pull latest changes first
git checkout feature/shared-branch
git pull origin feature/shared-branch

# 2. Check what changed
git log --oneline -5  # See recent commits
git diff HEAD~1      # Review latest changes
```

#### During Work - Frequent Communication

```bash
# 3. Pull frequently (every 30-60 minutes)
git pull origin feature/shared-branch

# 4. Push small, working commits frequently
git add .
git commit -m "feat: complete user validation logic"
git pull origin feature/shared-branch  # Pull again before push!
git push origin feature/shared-branch
```

#### Handling Conflicts with Team Members

If `git pull` results in conflicts:

```bash
# 1. Check which files conflict
git status

# 2. Communicate with team immediately!
# → Slack/Teams: "Hey @teammate, we have conflicts in UserService.java"
# → Decide together who resolves what

# 3. Resolve conflicts in files
# Open file and look for:
# <<<<<<< HEAD (your changes)
# =======
# >>>>>>> origin/feature/shared-branch (their changes)

# 4. After resolving, test thoroughly
git add .
npm test              # or: pytest, go test, mvn test
npm run build

# 5. Commit the merge
git commit -m "merge: resolve conflicts with @teammate changes"

# 6. Inform team it's resolved
git push origin feature/shared-branch
```

### 🛡️ Production Safety Rules

1. **Communicate constantly** - Use Slack/Teams to announce:
   - "Working on UserService.java for next 2 hours"
   - "About to push changes to database layer"
   - "Just pushed, please pull before continuing"

2. **Pull before every push**
   ```bash
   git pull && git push  # Make this a habit
   ```

3. **Keep commits small and atomic** - easier to merge
   - ✅ "feat: add email validation"
   - ❌ "update everything" (50 files changed)

4. **Test after every pull** - their changes might break your code
   ```bash
   git pull
   npm test  # Always!
   ```

5. **Work on different files when possible**
   - Developer A: frontend components
   - Developer B: backend API
   - Reduces conflicts

6. **Use feature flags for incomplete work**
   ```javascript
   if (config.ENABLE_NEW_FEATURE) {
     // New code being developed
   }
   ```

7. **Pair program on conflict-prone areas**
   - Screen share when working on same file
   - Reduces conflicts before they happen

### Alternative: Use Separate Branches (Recommended)

For most cases, it's better to split the work:

```bash
# Instead of everyone on feature/user-management
# Create sub-branches:

git checkout -b feature/user-management-auth      # Developer A
git checkout -b feature/user-management-profile   # Developer B  
git checkout -b feature/user-management-api       # Developer C

# Each developer:
# 1. Works independently
# 2. Creates PR to feature/user-management
# 3. Team reviews and merges
# 4. Finally, feature/user-management → main
```

### Why This Works

- Frequent pulls keep everyone synchronized
- Small commits reduce conflict complexity
- Communication prevents surprise conflicts
- Testing after pulls catches integration issues early
- Clear ownership reduces stepping on toes

💡 **Pro Tip:** If you're getting conflicts more than once a day, consider splitting into separate branches.

---

## Option 3: Feature Branch + Pull Request with Reviews

**Best for:** Team collaboration, production-ready code

**Industry Standard for Team Collaboration**

Never push directly to `main` or `production`. Always use feature branches and require code reviews before merging.

### Workflow

```bash
# Start from latest main
git checkout main
git pull origin main

# Create a feature branch
git checkout -b feature/add-user-authentication

# Work on your feature
# ... make changes ...
git add .
git commit -m "feat: implement user authentication"

# Push feature branch
git push -u origin feature/add-user-authentication

# Create Pull Request on GitHub/GitLab
# Wait for CI/CD tests to pass
# Request code review from team members
# Address review comments
# Only merge after approval
```

### GitHub Branch Protection Rules

Enable these settings to prevent breaking production:

1. **Require pull request reviews** (minimum 1-2 approvals)
2. **Require status checks to pass** (CI/CD pipelines)
3. **Require branches to be up to date** before merging
4. **Include administrators** (no one bypasses rules)
5. **Do not allow force push** to protected branches
6. **Require linear history** (optional, for cleaner git log)

### Why This Works

- Code review catches bugs before production
- CI/CD tests run automatically on every PR
- No one can accidentally break production
- Full audit trail of who changed what and why
- Rollback is easy (revert the PR)

---

## Option 4: Test Locally + CI/CD Pipeline

**Best for:** Ensuring code quality before merging

**Always test before pushing to shared branches**

### Pre-Push Checklist

```bash
# 1. Run tests locally
npm test           # or: pytest, go test, mvn test
npm run lint       # check code quality
npm run build      # ensure build succeeds

# 2. Test the application manually
npm start          # verify functionality works

# 3. Check what you're committing
git status
git diff           # review changes

# 4. Write meaningful commit message
git add .
git commit -m "fix: resolve null pointer exception in user service"

# 5. Push and monitor CI/CD
git push
# → Watch GitHub Actions/Jenkins/CircleCI
# → Don't merge if CI fails
```

### CI/CD Pipeline Configuration

Example GitHub Actions (`.github/workflows/ci.yml`):

```yaml
name: CI Pipeline

on:
  pull_request:
    branches: [main, production]
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Install dependencies
        run: npm install
      - name: Run tests
        run: npm test
      - name: Run linter
        run: npm run lint
      - name: Build
        run: npm run build
```

### Why This Works

- Automated tests catch regressions immediately
- Linters enforce code quality standards
- Build failures are caught before deployment
- Failed CI = PR cannot be merged
- Production only receives tested, working code

---

## Option 5: Rebase for Clean History

**Best for:** Solo feature branches, maintaining clean Git history

**For maintaining a linear, professional Git history**

### When to Use

Use rebase when:
- Your feature branch is behind `main`
- You want a clean, linear commit history
- Working on a feature branch (not shared with others)

**Never rebase shared branches like `main` or `production`**

### Workflow

```bash
# Update your feature branch with latest main
git checkout feature/my-feature
git fetch origin

# Rebase instead of merge
git rebase origin/main

# If conflicts occur:
# 1. Fix conflicts in files
# 2. Stage the resolved files
git add .
git rebase --continue

# If you need to abort
git rebase --abort

# Force push to your feature branch (only your branch!)
git push --force-with-lease origin feature/my-feature
```

### Rebase vs Merge

| Aspect | Rebase | Merge |
|--------|--------|-------|
| History | Linear, clean | Shows all branch points |
| Use case | Feature branches | Main/production branches |
| Safety | Riskier (rewrites history) | Safer (preserves history) |
| Team work | Solo or small teams | Large teams |

### Why This Works

- Clean, linear Git history
- Easier to understand what happened
- Easier to revert specific changes
- Professional appearance in Git log
- Reduces merge commits clutter

💡 **Pro Tip:** Use `git pull --rebase` for your daily workflow instead of `git pull` (which does merge)

---

## Option 6: Hotfix Workflow for Production Emergencies

**Best for:** Critical production bugs requiring immediate fix

**When production breaks and you need immediate fix**

### Emergency Hotfix Process

```bash
# 1. Create hotfix branch from production
git checkout production
git pull origin production
git checkout -b hotfix/critical-bug-fix

# 2. Fix the issue (minimal changes only!)
# ... edit files ...
git add .
git commit -m "hotfix: fix critical payment processing bug"

# 3. Push and create emergency PR
git push -u origin hotfix/critical-bug-fix

# 4. Fast-track review (1 senior engineer approval)
# 5. Merge to production immediately
# 6. Deploy to production

# 7. IMPORTANT: Backport to main
git checkout main
git pull origin main
git merge hotfix/critical-bug-fix
git push origin main

# 8. Delete hotfix branch
git branch -D hotfix/critical-bug-fix
git push origin --delete hotfix/critical-bug-fix
```

### Hotfix Best Practices

1. **Keep changes minimal** - fix only what's broken
2. **Get fast but thorough review** - 1 senior engineer minimum
3. **Test in staging first** if time permits
4. **Document the incident** - what broke, why, how fixed
5. **Always backport to main** - don't let branches diverge
6. **Create post-mortem** - prevent similar issues

### Why This Works

- Fixes production without breaking main branch
- Maintains proper Git workflow even in emergencies
- All changes are reviewed (even if expedited)
- Main branch stays synchronized
- Audit trail is preserved

---

## Best Practices Summary

### ✅ DO

- Always work on feature branches
- Write descriptive commit messages
- Run tests before pushing
- Request code reviews
- Keep commits small and focused
- Pull latest changes frequently
- Use branch protection rules
- Monitor CI/CD pipelines
- Delete merged branches

### ❌ DON'T

- Push directly to `main` or `production`
- Force push to shared branches
- Commit broken code
- Skip tests "just this once"
- Ignore CI/CD failures
- Leave merge conflicts unresolved
- Rebase shared branches
- Commit secrets or credentials
- Use `--no-verify` to skip hooks

---

## Quick Reference Commands

```bash
# Safe daily workflow
git checkout main && git pull                    # Update main
git checkout -b feature/my-work                  # New feature branch
# ... work ...
git add . && git commit -m "feat: description"   # Commit
git push -u origin feature/my-work               # Push feature
# Create PR → Review → Merge → Delete branch

# Sync with main (while on feature branch)
git fetch origin
git rebase origin/main                           # or: git merge origin/main

# Emergency rollback
git revert <commit-hash>                         # Safer than reset
git push

# Check what changed
git log --oneline --graph --all                  # Visual history
git diff origin/main..HEAD                       # Your changes vs main
```

---

## Additional Resources

- [Git Flow](https://nvie.com/posts/a-successful-git-branching-model/) - Popular branching model
- [Trunk-Based Development](https://trunkbaseddevelopment.com/) - Modern alternative
- [Conventional Commits](https://www.conventionalcommits.org/) - Commit message standard
- [GitHub Flow](https://guides.github.com/introduction/flow/) - Simplified workflow