# 08-spec-uvx-pypi-publishing.md

## Introduction/Overview

Enable the `slash-command-manager` CLI tool to be available via `uvx`, allowing users to run `uvx slash-man --help` and all other CLI commands without requiring local installation. This feature will publish the package to PyPI and optionally automate publishing via GitHub Actions using Trusted Publishing (OIDC).

The package already has the correct script entry point configured in `pyproject.toml`, so this spec focuses on the publishing workflow, build verification, and automation setup.

## Goals

1. **Fix Semantic-Release Version Update**: Fix `.releaserc.toml` configuration to use `version_toml` instead of `version_variables` so semantic-release correctly updates `pyproject.toml:project.version`
2. **Enable PyPI Publishing**: Configure and verify the package can be built and published to PyPI successfully, including PyPI account setup instructions
3. **Automate Publishing**: Set up GitHub Actions workflow using Trusted Publishing (OIDC) to automatically publish on GitHub releases
4. **Verify uvx Compatibility**: Ensure the published package works correctly with `uvx` command execution, including integration test updates
5. **Enhance Package Metadata**: Verify and improve package metadata (classifiers, description, keywords) for optimal PyPI presentation
6. **Document Publishing Workflow**: Provide clear instructions for manual and automated publishing processes
7. **Update Documentation**: Update README.md to reflect PyPI availability and `uvx` usage instructions

## User Stories

- **As a developer**, I want to publish `slash-command-manager` to PyPI so that users can install and run it via `uvx` without cloning the repository
- **As a maintainer**, I want automated publishing via GitHub Actions so that creating a GitHub release automatically publishes to PyPI without manual steps
- **As a maintainer**, I want automated version management via semantic-release so that version numbers are updated automatically based on conventional commits
- **As an end user**, I want to run `uvx slash-man --help` and all CLI commands so that I can use the tool without installing it locally or cloning the repository
- **As a developer**, I want clear documentation on the publishing process including PyPI account setup so that I can maintain and update the package easily

## Demoable Units of Work

### [Unit 1]: Manual Package Build and Verification

**Purpose:** Verify the package can be built correctly and contains all necessary components for PyPI distribution

**Demo Criteria:**

- Run `python -m build` successfully generates both `.whl` and `.tar.gz` files in `dist/` directory
- Built wheel contains the `slash-man` script entry point
- Built package includes all required dependencies and metadata

**Proof Artifacts:**

- Terminal output showing successful build completion
- File listing of `dist/` directory showing both wheel and source distribution files
- Verification that wheel contains `slash-man` executable script

### [Unit 2]: Manual PyPI Publishing

**Purpose:** Enable manual publishing to PyPI using `twine` for initial release and testing

**Demo Criteria:**

- Package successfully uploads to PyPI using `twine upload dist/*`
- Package appears on pypi.org with correct metadata
- Package can be installed via `pip install slash-command-manager`

**Proof Artifacts:**

- Terminal output showing successful upload to PyPI
- Screenshot or link to package page on pypi.org
- Verification that `pip install slash-command-manager` installs the package correctly

### [Unit 3]: uvx Execution Verification

**Purpose:** Verify that the published package works correctly with `uvx` command execution, including automated testing

**Demo Criteria:**

- `uvx slash-man --help` displays help text correctly
- `uvx slash-man generate --list-agents` executes successfully
- All CLI commands work via `uvx` as expected
- Integration tests verify `uvx` execution (updated or new tests)

**Proof Artifacts:**

- Terminal output showing `uvx slash-man --help` working
- Terminal output showing at least one functional command execution via `uvx`
- Comparison showing `uvx` behavior matches locally installed version
- Integration test results showing uvx compatibility verification

### [Unit 4]: Package Metadata Enhancement

**Purpose:** Verify and enhance package metadata for optimal PyPI presentation

**Demo Criteria:**

- Package metadata verified for completeness and accuracy
- Additional classifiers added as appropriate (e.g., more Python versions, topics)
- Description and keywords optimized for discoverability
- Metadata displays correctly on PyPI package page

**Proof Artifacts:**

- Updated `pyproject.toml` showing enhanced metadata
- PyPI package page screenshot showing improved metadata display
- Verification that all classifiers are appropriate and accurate

### [Unit 5]: Fix Semantic-Release Version Update

**Purpose:** Fix semantic-release configuration to properly update version in `pyproject.toml`

**Demo Criteria:**

- `.releaserc.toml` uses `version_toml` instead of `version_variables` for TOML file updates
- Semantic-release correctly updates `pyproject.toml:project.version` when creating releases
- Version in `pyproject.toml` matches the GitHub release version after semantic-release runs
- No breaking changes to existing semantic-release workflow

**Proof Artifacts:**

- Updated `.releaserc.toml` showing `version_toml = ["pyproject.toml:project.version"]`
- GitHub Actions workflow run showing semantic-release updating `pyproject.toml` version
- Git commit showing version update in `pyproject.toml` matching release tag
- Verification that `pyproject.toml` version matches latest GitHub release version

### [Unit 6]: PyPI Publishing Workflow Integration

**Purpose:** Integrate PyPI publishing workflow with existing semantic-release CI flow

**Demo Criteria:**

- PyPI publishing workflow triggers automatically when semantic-release creates a GitHub release
- Workflow builds package and publishes to PyPI after release is published
- No conflicts with existing semantic-release workflow
- Version numbers match between GitHub releases, `pyproject.toml`, and PyPI packages

**Proof Artifacts:**

- GitHub Actions workflow run showing PyPI publish triggered by semantic-release release
- PyPI package page showing version matching GitHub release version
- Workflow logs showing successful integration with existing PSR flow

### [Unit 7]: GitHub Actions Automated Publishing

**Purpose:** Automate publishing to PyPI when GitHub releases are created, using Trusted Publishing (OIDC)

**Demo Criteria:**

- GitHub Actions workflow triggers on release creation
- Workflow successfully builds and publishes package to PyPI
- No secrets or API tokens required (uses OIDC Trusted Publishing)
- Published package is immediately available via `uvx`
- Workflow integrates with semantic-release for version management

**Proof Artifacts:**

- GitHub Actions workflow run showing successful completion
- PyPI package page showing new version published
- Terminal output showing `uvx slash-man --version` displaying the newly published version
- Workflow logs showing semantic-release integration

## Functional Requirements

1. **The system shall build the package** using `python -m build` to generate both wheel (`.whl`) and source distribution (`.tar.gz`) files

2. **The system shall verify the script entry point** `slash-man = "slash_commands.cli:main"` is correctly configured in `pyproject.toml` and included in the built package

3. **The system shall provide PyPI account setup instructions** including:
   - Account creation at https://pypi.org/account/register/
   - Email verification process
   - API token generation for manual publishing (optional, for `twine upload`)
   - Trusted Publishing configuration at https://pypi.org/manage/account/publishing/ for automated publishing

4. **The system shall support manual publishing** via `twine upload dist/*` command with PyPI API token authentication

5. **The system shall provide GitHub Actions workflow** that automatically builds and publishes to PyPI when a GitHub release is created (triggered by existing semantic-release flow), using the official `pypa/gh-action-pypi-publish@v1.13.0` action

6. **The system shall use Trusted Publishing (OIDC)** for GitHub Actions to avoid storing PyPI API tokens as secrets

7. **The system shall verify and enhance package metadata** including name, version, description, dependencies, and classifiers for optimal PyPI presentation

8. **The system shall enable uvx execution** so that `uvx slash-man` commands work identically to locally installed versions

9. **The system shall update integration tests** to verify `uvx` compatibility, either by updating existing tests or creating new test cases

10. **The system shall fix semantic-release version update configuration** - Update `.releaserc.toml` to use `version_toml` instead of `version_variables` so that semantic-release correctly updates `pyproject.toml:project.version` when creating releases

11. **The system shall integrate with existing semantic-release workflow** - The repository already has a working Python Semantic Release (PSR) flow that manages version numbers and creates GitHub releases. The PyPI publishing workflow should trigger after semantic-release publishes releases

12. **The system shall update README.md** with PyPI installation instructions, `uvx` usage examples, and PyPI account setup guidance

13. **The system shall document the publishing workflow** including manual publishing steps, automated publishing via GitHub releases, and PyPI account setup

14. **The system shall verify build compatibility** with the existing `hatchling` build backend and custom build hooks

15. **The system shall document the build process** including verification steps and troubleshooting guidance

## Non-Goals (Out of Scope)

1. **Homebrew, Scoop, Winget, or Chocolatey distribution** - This spec focuses exclusively on PyPI/uvx enablement

2. **Test PyPI publishing** - This spec focuses on production PyPI only (test.pypi.org is out of scope)

3. **Multi-architecture builds** - Standard Python wheel builds are sufficient (no platform-specific builds)

4. **Major refactoring of semantic-release** - Update and enable existing semantic-release configuration, but no complete rewrite

## Design Considerations

No specific UI/UX design requirements. This is a backend/infrastructure feature focused on package publishing and distribution.

## Repository Standards

Implementation should follow existing repository patterns:

- **Build System**: Use existing `hatchling` build backend (no changes to build system)
- **Python Version**: Maintain `requires-python = ">=3.12"` requirement
- **Dependencies**: Use `uv` for dependency management (as seen in existing workflows)
- **Testing**: Follow existing pytest patterns for any new tests
- **Documentation**: Update README.md following existing markdown formatting standards
- **GitHub Actions**: Follow existing workflow patterns if any exist, or create new `.github/workflows/` directory
- **Commit Messages**: Follow conventional commits format (as indicated by semantic-release config)

## Technical Considerations

1. **Build Backend**: The project uses `hatchling` as the build backend (as per [Python Packaging Tutorial](https://packaging.python.org/en/latest/tutorials/packaging-projects/)). Verify that `python -m build` works correctly with the existing `pyproject.toml` configuration, including the custom build hook (`hatch_build.py`). The build should generate both wheel (`.whl`) and source distribution (`.tar.gz`) files as recommended by PyPA

2. **Script Entry Point**: The script entry point `slash-man = "slash_commands.cli:main"` is already configured correctly. Verify it's included in the built wheel

3. **Package Name**: The package name `slash-command-manager` must be available on PyPI. If unavailable, consider alternatives or coordinate with PyPI administrators

4. **Trusted Publishing Setup**: GitHub Actions workflow requires PyPI Trusted Publishing configuration (as per [PyPI Trusted Publishing documentation](https://blog.pypi.org/posts/2023-04-20-introducing-trusted-publishers/)):
   - PyPI account must configure trusted publisher for the GitHub repository at https://pypi.org/manage/account/publishing/
   - Configure with the following values (see PyPI Trusted Publishing form below):
     - **PyPI Project Name**: `slash-command-manager`
     - **Owner**: `liatrio-labs`
     - **Repository name**: `slash-command-manager`
     - **Workflow filename**: `publish-to-pypi.yml` (or the actual workflow filename created)
     - **Environment name**: `pypi` (optional but strongly recommended)
   - Workflow must specify correct `environment: pypi` name
   - Workflow must have `id-token: write` permissions in the `permissions` section
   - Use `pypa/gh-action-pypi-publish@v1.13.0` action (latest stable version per [GitHub Marketplace](https://github.com/marketplace/actions/pypi-publish)) which automatically handles OIDC authentication

5. **Build Dependencies**: Ensure `build` and `twine` packages are available for manual publishing (already in `dependency-groups.dev`)

6. **Semantic-Release Configuration Fix**: Fix the existing semantic-release configuration in `.releaserc.toml` to properly update `pyproject.toml` version:
   - **Critical Issue**: The current `.releaserc.toml` uses `version_variables = ["pyproject.toml:project.version"]` which is incorrect
   - **Fix Required**: Change to `version_toml = ["pyproject.toml:project.version"]` (as per [Python Semantic Release documentation](https://python-semantic-release.readthedocs.io/))
   - `version_variables` is for regex substitution in non-TOML files (e.g., Python `__init__.py` files)
   - `version_toml` is specifically for TOML files like `pyproject.toml` and uses proper TOML parsing
   - This fix will ensure semantic-release correctly updates the version in `pyproject.toml` when creating releases
   - The PyPI publishing workflow should integrate with the existing semantic-release CI flow
   - Ensure the publishing workflow triggers after semantic-release creates a GitHub release

7. **Version Management**: Current version is `v0.6.0` (as per [GitHub releases](https://github.com/liatrio-labs/slash-command-manager/releases)). Semantic-release will manage version updates automatically based on conventional commits via the existing PSR workflow

8. **GitHub Release Trigger**: Workflow should trigger on `release: types: [published]` event. The existing semantic-release CI flow already creates GitHub releases automatically based on conventional commits, so the PyPI publishing workflow will trigger when semantic-release publishes a release

9. **Python Version in CI**: Use Python 3.12 in GitHub Actions to match `requires-python` requirement

10. **Integration Testing**: Update existing integration tests in `tests/integration/` to verify `uvx` compatibility, or create new test cases that can be run against published packages

11. **Package Metadata Enhancement**: Review and add appropriate classifiers following [PyPI classifier guidelines](https://packaging.python.org/en/latest/guides/making-a-pypi-friendly-readme/):
    - Additional Python version support classifiers (e.g., "Programming Language :: Python :: 3.13" if supported)
    - Topic classifiers (e.g., "Topic :: Software Development :: Build Tools", "Topic :: Utilities")
    - Development status classifiers (currently "Development Status :: 4 - Beta" - consider updating when appropriate)
    - Operating system classifiers (e.g., "Operating System :: OS Independent" if cross-platform)
    - Framework classifiers if applicable
    - Ensure all classifiers are accurate and relevant to the package

## Success Metrics

1. **Build Success Rate**: 100% successful package builds using `python -m build`

2. **Publishing Success**: Package successfully publishes to PyPI without errors

3. **uvx Compatibility**: `uvx slash-man --help` and all CLI commands execute successfully within 5 minutes of PyPI publication

4. **Full CLI Functionality**: All `slash-man` commands work identically via `uvx` as they do when locally installed

5. **Automation Success**: GitHub Actions workflow successfully publishes on 100% of release events (after initial setup)

6. **Version Management**: Semantic-release automatically updates versions based on conventional commits with 100% accuracy

7. **Metadata Quality**: Package metadata on PyPI includes appropriate classifiers and is optimized for discoverability

8. **Documentation Completeness**: README.md includes clear PyPI installation instructions, `uvx` usage examples, and PyPI account setup guidance

9. **Test Coverage**: Integration tests verify `uvx` compatibility and pass consistently

## Open Questions

1. **PyPI Account Status**: PyPI account creation steps will be included in the spec documentation
   1. I already created an account

2. **Package Name Availability**: Is `slash-command-manager` available on PyPI, or do we need an alternative name? (To be verified during implementation)

3. **Initial Version**: Should the first published version be `0.1.0` or start at a different version? (Semantic-release will handle versioning after initial setup)
   1. check the current app version history on github

4. **Semantic-Release Integration**: Should semantic-release create GitHub releases automatically, or should releases be created manually to trigger publishing? (To be determined during implementation)
   1. this is already handled by the existing semantic-release CI flow

5. **Integration Test Approach**: Should `uvx` testing be added to existing integration tests or created as separate test cases? (To be determined based on existing test structure)
   1. probably separate test cases. the tests would need to spin up a docker container with python and uv, then try to run `uvx slash-man --help` and `uvx slash-man --version`, then verify the output of both commands is accurate.

No open questions that would block implementation. Remaining questions will be resolved during task breakdown and implementation.
