# Questions: uvx PyPI Publishing Enablement

## Core Understanding

### 1. PyPI Account Setup

Do you already have a PyPI account set up, or should the spec include instructions for creating one?

**Options:**

- [ ] 1. **Yes, I have a PyPI account** - Spec should assume account exists and focus on publishing workflow
- [x] 2. **No, I need to create one** - Spec should include account creation steps
- [ ] 3. **Not sure** - Spec should include account creation steps as a prerequisite

### 2. PyPI Publishing Method

Which method should we use for publishing to PyPI?

**Options:**

- [ ] 1. **Manual publishing** - Use `twine upload` command locally (simpler, but requires manual steps)
- [ ] 2. **GitHub Actions with Trusted Publishing (OIDC)** - Automated publishing on release (recommended, secure, no secrets needed)
- [x] 3. **Both** - Support manual publishing initially, then add GitHub Actions automation

### 3. GitHub Actions Automation

Should the spec include automated publishing via GitHub Actions?

**Options:**

- [x] 1. **Yes, include GitHub Actions workflow** - Automate publishing when creating GitHub releases
- [ ] 2. **No, manual publishing only** - Keep it simple, just enable manual publishing
- [ ] 3. **Separate spec later** - Focus on manual publishing now, automation in a follow-up spec

### 4. Testing Strategy

How should we verify that the package works correctly with `uvx`?

**Options:**

- [ ] 1. **Manual testing instructions** - Provide commands for manual verification after publishing
- [ ] 2. **Automated testing** - Include GitHub Actions workflow to test `uvx` installation before/after publishing
- [x] 3. **Both** - Manual instructions plus optional automated verification. we can potentially update the existing integration tests to handle this, or at least build off of them.

### 5. Version Management

The current version in `pyproject.toml` is `0.1.0`. How should version updates be handled?

**Options:**

- [ ] 1. **Manual version updates** - Developer manually updates version in `pyproject.toml` before publishing
- [x] 2. **Automated versioning** - Update the existing semantic-release setup to properly version all necessary files.
- [ ] 3. **Document versioning process** - Include clear instructions for manual version management

## Success & Boundaries

### 6. Success Criteria

What defines success for this feature?

**Options:**

- [ ] 1. **Basic functionality** - Users can run `uvx slash-man --help` successfully
- [x] 2. **Full CLI functionality** - Users can run all `slash-man` commands via `uvx`
- [x] 3. **Complete workflow** - Package can be built, published, and used via `uvx` end-to-end

### 7. Out of Scope

What should this spec explicitly NOT include?

**Options:**

- [x] 1. **Homebrew/Scoop/Winget** - Only focus on PyPI/uvx (as requested)
- [ ] 2. **Version automation** - Keep version management manual for now
- [ ] 3. **PyPI Test instance** - Only publish to production PyPI (not test.pypi.org)

## Technical Considerations

### 8. Build System

The project uses `hatchling` as the build backend. Should we verify compatibility or make any changes?

**Options:**

- [x] 1. **Verify hatchling works** - Test that `python -m build` works correctly with current config
- [ ] 2. **No changes needed** - Assume current `pyproject.toml` is sufficient
- [x] 3. **Document build process** - Include build verification steps

### 9. Package Metadata

Should we verify or enhance package metadata (description, keywords, classifiers) for PyPI?

**Options:**

- [x] 1. **Verify current metadata** - Ensure existing metadata is appropriate for PyPI
- [x] 2. **Enhance metadata** - Add more classifiers, improve description, etc.
- [ ] 3. **No changes** - Use existing metadata as-is

## Demo & Proof

### 10. Proof Artifacts

What proof should we provide to demonstrate this works?

**Options:**

- [ ] 1. **CLI output screenshots** - Show `uvx slash-man --help` working
- [ ] 2. **PyPI package page** - Link to published package on pypi.org
- [ ] 3. **GitHub Actions run logs** - Show successful automated publish workflow
- [x] 4. **All of the above** - Comprehensive proof of end-to-end functionality
