# PyPI Automation with GitHub Releases

This setup provides automated PyPI publishing through GitHub Releases, giving you better version control and release management.

## How It Works

1. **Create a GitHub Release** → **Automatic PyPI Publication**
2. GitHub Actions detects the new release
3. Extracts version from the release tag
4. Updates `__init__.py` with the version
5. Builds and publishes to PyPI automatically

## Setup Required

### 1. GitHub CLI Installation
```bash
brew install gh
gh auth login
```

### 2. PyPI Trusted Publishing (Recommended)
1. Go to [PyPI Trusted Publishers](https://pypi.org/manage/account/publishing/)
2. Add a new trusted publisher:
   - **Owner**: `jangabrielsson`
   - **Repository**: `plua`
   - **Workflow**: `publish-to-pypi.yml`
   - **Environment**: `pypi` (optional)

### 3. Alternative: PyPI API Token
If you prefer API tokens:
1. Create a PyPI API token at https://pypi.org/manage/account/token/
2. Add it as a GitHub secret: `PYPI_API_TOKEN`
3. Update the workflow to use `password: ${{ secrets.PYPI_API_TOKEN }}`

## Usage Options

### VS Code Tasks (Recommended)
Use **Cmd+Shift+P** → **"Tasks: Run Task"**:

- **GitHub: Create Patch Release** - Auto patch bump + release
- **GitHub: Create Release (Interactive)** - Choose version type interactively  
- **GitHub: Create Custom Release** - Enter custom version and notes

### Command Line
```bash
# Interactive mode (choose patch/minor/major)
./scripts/create-release.sh

# Quick patch release
./scripts/create-release.sh patch

# Custom version with notes
./scripts/create-release.sh "1.2.3" "Fixed critical bug in timer handling"

# Custom version with interactive notes
./scripts/create-release.sh "2.0.0"
```

### Manual GitHub Release
1. Go to https://github.com/jangabrielsson/plua/releases
2. Click "Create a new release"
3. Create a tag like `v1.0.54`
4. Add release notes
5. Publish the release
6. GitHub Actions will automatically publish to PyPI

## Release Tag Format

The system expects tags in format: `v1.2.3` or `1.2.3`
- `v1.0.54` → PyPI version `1.0.54`
- `1.0.54` → PyPI version `1.0.54`

## Workflow Status

Monitor the automation at:
- **GitHub Actions**: https://github.com/jangabrielsson/plua/actions
- **PyPI Releases**: https://pypi.org/project/plua/

## Benefits

✅ **Version Control Integration** - Releases are tied to Git tags  
✅ **Release Notes** - Document changes for each version  
✅ **Automatic Publishing** - No manual PyPI uploads needed  
✅ **Rollback Capability** - Easy to track and revert versions  
✅ **Professional Workflow** - Standard practice for open source projects  
✅ **Security** - Uses trusted publishing (no API keys needed)

## Troubleshooting

### Release Failed
- Check GitHub Actions logs in the Actions tab
- Ensure PyPI trusted publishing is configured correctly
- Verify the tag format is correct

### Script Permissions
```bash
chmod +x scripts/create-release.sh
```

### GitHub CLI Not Authenticated
```bash
gh auth login
gh auth status
```
