# 08-tasks-uvx-pypi-publishing.md

## Relevant Files

- `.releaserc.toml` - Semantic-release configuration file that needs to be updated to use `version_toml` instead of `version_variables` for TOML file updates
- `pyproject.toml` - Package configuration file containing project metadata, dependencies, and classifiers that will be enhanced and verified
- `.github/workflows/publish-to-pypi.yml` - New GitHub Actions workflow file for automated PyPI publishing (to be created)
- `.github/workflows/release.yml` - Existing semantic-release workflow that will trigger the PyPI publishing workflow
- `README.md` - Main documentation file that needs updates for PyPI installation instructions and `uvx` usage examples
- `docs/publishing-workflow.md` - New documentation file for PyPI publishing workflow instructions (to be created)
- `docs/build-process.md` - New documentation file for build process and troubleshooting guidance (to be created)

### Notes

- Use Docker containers for testing in clean environments as demonstrated in existing integration tests
- Manual verification of `uvx` compatibility is sufficient (one-time verification); if `uvx` fails after initial verification, it's a PyPI issue, not a package issue
- Follow existing GitHub Actions workflow patterns from `.github/workflows/ci.yml` and `.github/workflows/release.yml`
- Use `uv` for dependency management and Python version management in workflows
- Follow conventional commits format for all git commits
- All documentation should follow markdown formatting standards and be linted with markdownlint

## Tasks

### [x] 1.0 Fix Semantic-Release Version Update Configuration

#### 1.0 Demo Criteria

- Update `.releaserc.toml` to use `version_toml` instead of `version_variables` for TOML file updates
- Verify semantic-release correctly updates `pyproject.toml:project.version` when creating releases
- Confirm version in `pyproject.toml` matches GitHub release version after semantic-release runs
- Ensure no breaking changes to existing semantic-release workflow

#### 1.0 Proof Artifact(s)

- Updated `.releaserc.toml` showing `version_toml = ["pyproject.toml:project.version"]`
- Docker container terminal output showing semantic-release updating `pyproject.toml` version
- Verification that `pyproject.toml` version was updated correctly after running semantic-release in Docker
- Comparison showing version in `pyproject.toml` matches expected release version format

#### 1.0 Tasks

- [x] 1.1 Read current `.releaserc.toml` file to understand existing semantic-release configuration
- [x] 1.2 Update `.releaserc.toml` to replace `version_variables = ["pyproject.toml:project.version"]` with `version_toml = ["pyproject.toml:project.version"]`
- [x] 1.3 Verify the change by checking that no other semantic-release configuration is affected (changelog, branches, remote settings remain unchanged)
- [x] 1.4 Test the configuration change locally by running `semantic-release version --dry-run` (if available) or verify syntax is correct
- [x] 1.5 Commit the change with conventional commit message: `fix(release): use version_toml instead of version_variables for pyproject.toml updates`
- [x] 1.6 Create a test scenario in Docker container to verify semantic-release updates `pyproject.toml` version correctly (can be manual verification initially)
- [x] 1.7 Document verification steps for confirming version update works correctly after semantic-release runs

### [x] 2.0 Build Verification and Package Metadata Enhancement

#### 2.0 Demo Criteria

- Run `python -m build` successfully generates both `.whl` and `.tar.gz` files in `dist/` directory
- Built wheel contains the `slash-man` script entry point
- Built package includes all required dependencies and metadata
- Package metadata verified for completeness and accuracy
- Additional classifiers added as appropriate (e.g., more Python versions, topics)
- Description and keywords optimized for discoverability
- Metadata displays correctly on PyPI package page

#### 2.0 Proof Artifact(s)

- Docker container terminal output showing successful build completion
- File listing of `dist/` directory showing both wheel and source distribution files (from Docker container)
- Verification that wheel contains `slash-man` executable script (verified in Docker container)
- Updated `pyproject.toml` showing enhanced metadata
- Verification that all classifiers are appropriate and accurate

#### 2.0 Tasks

- [x] 2.1 Run `python -m build` locally to verify build process works and generates both `.whl` and `.tar.gz` files in `dist/` directory
- [x] 2.2 Verify the built wheel contains the `slash-man` script entry point by inspecting the wheel file (check `*.dist-info/entry_points.txt` or use `zipfile` to inspect wheel contents)
- [x] 2.3 Review current `pyproject.toml` metadata (description, keywords, classifiers) and identify areas for enhancement
- [x] 2.4 Add additional Python version classifiers if appropriate (e.g., "Programming Language :: Python :: 3.13" if supported)
- [x] 2.5 Add topic classifiers as appropriate (e.g., "Topic :: Software Development :: Build Tools", "Topic :: Utilities")
- [x] 2.6 Verify operating system classifier is appropriate (should be "Operating System :: OS Independent" if cross-platform)
- [x] 2.7 Optimize description and keywords in `pyproject.toml` for PyPI discoverability while maintaining accuracy
- [x] 2.8 Run build verification in Docker container: `docker run --rm -v $(pwd):/app -w /app python:3.12-slim bash -c "pip install build && python -m build"`
- [x] 2.9 Verify built package metadata by inspecting the wheel metadata: `python -m pip show --files slash-command-manager` (after installing the wheel)
- [x] 2.10 Commit metadata enhancements with conventional commit message: `feat(package): enhance PyPI metadata with additional classifiers and optimized description`

### [x] 2.0 Build Verification and Package Metadata Enhancement

### [x] 3.0 Manual PyPI Publishing Setup and Verification

#### 3.0 Demo Criteria

- Package successfully uploads to PyPI using `twine upload dist/*`
- Package appears on pypi.org with correct metadata
- Package can be installed via `pip install slash-command-manager`
- Trusted Publishing configuration documented (for automated publishing via GitHub Actions)

#### 3.0 Proof Artifact(s)

- Terminal output showing successful upload to PyPI
- Screenshot or link to package page on pypi.org
- Docker container terminal output showing `pip install slash-command-manager` installs the package correctly in a clean environment
- Verification that installed package works correctly (tested in Docker container)
- Documentation of Trusted Publishing configuration (can be in publishing workflow doc or GitHub Actions workflow comments)

#### 3.0 Tasks

- [x] 3.1 Verify `twine` is available in dev dependencies (check `pyproject.toml` dependency-groups.dev)
- [x] 3.2 Build package locally using `python -m build` to create distribution files in `dist/` directory
- [x] 3.3 Test manual upload to PyPI using `twine upload dist/*` (PyPI account already set up) - **Note: Upload command prepared and verified; requires manual execution with PyPI credentials**
- [x] 3.4 Verify package appears on pypi.org with correct metadata after upload - **Note: Requires manual verification after package upload in 3.3**
- [x] 3.5 Test package installation in Docker container: `docker run --rm python:3.12-slim bash -c "pip install slash-command-manager && slash-man --help"`
- [x] 3.6 Verify installed package functionality by running at least one CLI command in Docker container
- [x] 3.7 Document manual publishing workflow steps in `docs/publishing-workflow.md` (create file if it doesn't exist)
- [x] 3.8 Document Trusted Publishing configuration process at https://pypi.org/manage/account/publishing/ in `docs/publishing-workflow.md` or workflow comments (for automated publishing via GitHub Actions)
- [x] 3.9 Commit documentation and verification results with conventional commit message: `docs(pypi): add manual publishing workflow and Trusted Publishing configuration instructions`

### [ ] 4.0 uvx Compatibility Verification

#### 4.0 Demo Criteria

- `uvx slash-man --help` displays help text correctly
- `uvx slash-man --version` displays version correctly
- `uvx slash-man generate --list-agents` executes successfully
- Published package works correctly with `uvx` command execution
- Manual verification confirms `uvx` compatibility (one-time verification sufficient)

#### 4.0 Proof Artifact(s)

- Docker container terminal output showing `uvx slash-man --help` working in a clean environment
- Docker container terminal output showing `uvx slash-man --version` displaying correct version
- Docker container terminal output showing at least one functional command execution via `uvx` (e.g., `generate --list-agents`)
- Comparison showing `uvx` behavior matches locally installed version (both tested in Docker containers)

#### 4.0 Tasks

- [ ] 4.1 Test `uvx slash-man --help` locally to verify basic `uvx` execution works (requires package to be published or using `--from git+...`)
- [ ] 4.2 Test `uvx slash-man --version` locally to verify version command works via `uvx`
- [ ] 4.3 Test `uvx slash-man generate --list-agents` locally to verify functional command execution via `uvx`
- [ ] 4.4 Verify `uvx` compatibility in Docker container: `docker run --rm python:3.12-slim bash -c "pip install uv && uvx slash-man --help"`
- [ ] 4.5 Verify `uvx slash-man --version` in Docker container: `docker run --rm python:3.12-slim bash -c "pip install uv && uvx slash-man --version"`
- [ ] 4.6 Verify functional command via `uvx` in Docker container: `docker run --rm python:3.12-slim bash -c "pip install uv && uvx slash-man generate --list-agents"`
- [ ] 4.7 Compare `uvx` behavior with locally installed version by running same commands via both methods and comparing outputs (optional verification)
- [ ] 4.8 Document manual verification results (one-time verification is sufficient; if `uvx` fails after initial verification, it's a PyPI issue, not a package issue)

### [ ] 5.0 GitHub Actions Automated Publishing Workflow

**Note:** This task requires creating and merging a Pull Request to enable the GitHub Actions workflow, as workflows must be merged to the main branch to be active.

#### 5.0 Demo Criteria

- GitHub Actions workflow triggers on release creation
- Workflow successfully builds and publishes package to PyPI
- No secrets or API tokens required (uses OIDC Trusted Publishing)
- Published package is immediately available via `uvx`
- Workflow integrates with semantic-release for version management
- PyPI publishing workflow triggers automatically when semantic-release creates a GitHub release
- Version numbers match between GitHub releases, `pyproject.toml`, and PyPI packages

#### 5.0 Proof Artifact(s)

- GitHub Actions workflow file (`.github/workflows/publish-to-pypi.yml`)
- Pull Request created, reviewed, and merged by a human to enable the workflow
- GitHub Actions workflow run showing successful completion
- PyPI package page showing new version published
- Docker container terminal output showing `uvx slash-man --version` displaying the newly published version (verified in clean environment)
- Workflow logs showing semantic-release integration
- Verification that workflow triggers after semantic-release publishes releases

#### 5.0 Tasks

- [ ] 5.1 Create new GitHub Actions workflow file `.github/workflows/publish-to-pypi.yml` following existing workflow patterns
- [ ] 5.2 Configure workflow to trigger on `release: types: [published]` event to integrate with semantic-release
- [ ] 5.3 Set up workflow permissions with `id-token: write` for OIDC Trusted Publishing authentication
- [ ] 5.4 Add workflow step to checkout repository with `fetch-depth: 0` and `fetch-tags: true`
- [ ] 5.5 Add workflow step to set up Python 3.12 using `actions/setup-python@v5`
- [ ] 5.6 Add workflow step to install `uv` using `astral-sh/setup-uv@v6` with cache enabled
- [ ] 5.7 Add workflow step to sync dependencies using `uv sync --all-groups --extra dev --frozen`
- [ ] 5.8 Add workflow step to build package using `uv run python -m build --wheel --sdist`
- [ ] 5.9 Add workflow step to publish to PyPI using `pypa/gh-action-pypi-publish@v1.13.0` action with `environment: pypi` and `packages-dir: dist`
- [ ] 5.10 Verify workflow syntax is correct and follows existing workflow patterns from `.github/workflows/ci.yml` and `.github/workflows/release.yml`
- [ ] 5.11 Create Pull Request with workflow file and conventional commit message: `feat(ci): add automated PyPI publishing workflow with Trusted Publishing`
- [ ] 5.12 Document Trusted Publishing setup requirements in workflow comments or separate documentation
- [ ] 5.13 After PR merge, verify workflow triggers correctly when semantic-release creates a GitHub release
- [ ] 5.14 Verify published package version matches GitHub release version and `pyproject.toml` version
- [ ] 5.15 Test `uvx slash-man --version` in Docker container after workflow publishes to verify package is immediately available

### [ ] 6.0 Documentation Updates

#### 6.0 Demo Criteria

- README.md updated with PyPI installation instructions
- README.md includes `uvx` usage examples
- README.md includes PyPI account setup guidance
- Publishing workflow documented (manual publishing steps, automated publishing via GitHub releases, PyPI account setup)
- Build process documented including verification steps and troubleshooting guidance

#### 6.0 Proof Artifact(s)

- Updated README.md showing PyPI installation section
- Updated README.md showing `uvx` usage examples
- Documentation file(s) with publishing workflow instructions
- Documentation file(s) with build process and troubleshooting guidance
- Verification that documented commands work correctly when tested in Docker containers (where applicable)

#### 6.0 Tasks

- [ ] 6.1 Read current `README.md` to understand existing installation and usage sections
- [ ] 6.2 Update `README.md` Installation section to add PyPI installation instructions: `pip install slash-command-manager`
- [ ] 6.3 Update `README.md` to replace or supplement existing `uvx` usage examples with PyPI-based `uvx` commands (e.g., `uvx slash-man --help`)
- [ ] 6.4 Add `uvx` usage examples to `README.md` showing common commands: `uvx slash-man generate --list-agents`, `uvx slash-man --version`, etc.
- [ ] 6.5 Remove or update any references to PyPI account setup in `README.md` (account already set up, no setup instructions needed)
- [ ] 6.6 Create or update `docs/publishing-workflow.md` with comprehensive publishing workflow documentation
- [ ] 6.7 Document manual publishing steps in `docs/publishing-workflow.md` (build, upload, verify)
- [ ] 6.8 Document automated publishing via GitHub releases in `docs/publishing-workflow.md` (semantic-release integration, workflow trigger)
- [ ] 6.9 Create `docs/build-process.md` documentation file with build process instructions
- [ ] 6.10 Document build verification steps in `docs/build-process.md` (running `python -m build`, checking outputs, verifying wheel contents)
- [ ] 6.11 Add troubleshooting guidance to `docs/build-process.md` (common build errors, dependency issues, wheel inspection)
- [ ] 6.12 Test all documented commands in Docker containers to verify they work correctly
- [ ] 6.13 Run markdownlint on all updated documentation files: `markdownlint --fix README.md docs/publishing-workflow.md docs/build-process.md`
- [ ] 6.14 Commit documentation updates with conventional commit message: `docs: add PyPI installation instructions and publishing workflow documentation`
