# PyPI Publishing Workflow

This document describes the workflow for publishing the `slash-command-manager` package to PyPI, including both manual and automated publishing methods.

## Prerequisites

- PyPI account with appropriate permissions
- `twine` installed (included in dev dependencies)
- `build` package installed (included in dev dependencies)
- Package built and ready for distribution

## Manual Publishing

### Step 1: Build the Package

Build both wheel and source distribution files:

```bash
python -m build
```

This creates distribution files in the `dist/` directory:

- `slash_command_manager-<version>-py3-none-any.whl` (wheel)
- `slash_command_manager-<version>.tar.gz` (source distribution)

### Step 2: Verify Package Quality

Before uploading, verify the package quality using `twine check`:

```bash
twine check dist/*
```

This checks for common issues with package metadata and file structure.

### Step 3: Upload to PyPI

Upload the distribution files to PyPI:

```bash
twine upload dist/*
```

You will be prompted for your PyPI credentials (username and password or API token).

**Note:** For production uploads, use the production PyPI URL. For testing, use TestPyPI:

```bash
# TestPyPI (for testing)
twine upload --repository-url https://test.pypi.org/legacy/ dist/*

# Production PyPI
twine upload dist/*
```

### Step 4: Verify Upload

After uploading, verify the package appears on PyPI:

1. Visit https://pypi.org/project/slash-command-manager/
2. Confirm the version number matches your release
3. Verify metadata displays correctly (description, classifiers, etc.)
4. Test installation in a clean environment:

```bash
docker run --rm python:3.12-slim bash -c "pip install slash-command-manager && slash-man --version"
```

## Automated Publishing via GitHub Actions

The repository includes automated PyPI publishing via GitHub Actions using OIDC Trusted Publishing. This eliminates the need for API tokens or secrets.

### Trusted Publishing Setup

To enable automated publishing, configure Trusted Publishing on PyPI:

1. **Navigate to PyPI Trusted Publishing Settings**

   Visit https://pypi.org/manage/account/publishing/

2. **Add a New Trusted Publisher**

   - **PyPI project name:** `slash-command-manager`
   - **Owner:** Your GitHub organization or username (e.g., `liatrio-labs`)
   - **Workflow filename:** `.github/workflows/publish-to-pypi.yml`
   - **Environment name (optional):** `pypi` (if using GitHub Environments)

3. **Save Configuration**

   PyPI will generate a trusted publisher configuration that allows the GitHub Actions workflow to publish without API tokens.

### Workflow Integration

The automated publishing workflow (`.github/workflows/publish-to-pypi.yml`) is configured to:

- Trigger automatically when semantic-release creates a GitHub release
- Build the package using `uv` and `python -m build`
- Publish to PyPI using the `pypa/gh-action-pypi-publish` action
- Use OIDC authentication (no secrets required)

### Workflow Trigger

The publishing workflow triggers on the `release: types: [published]` event, which is fired when semantic-release creates a GitHub release. This ensures:

- Version numbers match between GitHub releases, `pyproject.toml`, and PyPI packages
- Publishing only occurs for valid releases
- Integration with the existing semantic-release workflow

### Verification After Automated Publishing

After the workflow completes:

1. Check GitHub Actions workflow run for successful completion
2. Verify package appears on PyPI with the new version
3. Test installation:

   ```bash
   docker run --rm python:3.12-slim bash -c "pip install slash-command-manager && slash-man --version"
   ```

4. Verify `uvx` compatibility:

   ```bash
   docker run --rm python:3.12-slim bash -c "pip install uv && uvx slash-man --version"
   ```

## Version Management

Package versions are managed by semantic-release:

- Versions follow [Semantic Versioning](https://semver.org/)
- Version updates are committed to `pyproject.toml` automatically
- GitHub releases are created automatically
- PyPI publishing follows GitHub releases

## Troubleshooting

### Build Failures

If the build fails:

1. Verify all dependencies are listed in `pyproject.toml`
2. Check that `pyproject.toml` syntax is correct
3. Ensure `uv.lock` is up to date: `uv lock`
4. Review build output for specific errors

### Upload Failures

If upload fails:

1. Verify PyPI credentials are correct
2. Check that the version doesn't already exist on PyPI
3. Ensure package name matches PyPI project name exactly
4. Verify network connectivity to PyPI

### Trusted Publishing Issues

If Trusted Publishing fails:

1. Verify Trusted Publisher configuration on PyPI matches workflow details exactly
2. Check GitHub Actions workflow permissions include `id-token: write`
3. Ensure workflow file path matches configuration: `.github/workflows/publish-to-pypi.yml`
4. Verify repository owner matches Trusted Publisher owner setting

## Related Documentation

- [Build Process Documentation](build-process.md) - Detailed build process and troubleshooting
- [Semantic Release Configuration](.releaserc.toml) - Version management configuration
- [GitHub Actions Workflows](.github/workflows/) - CI/CD workflow definitions
