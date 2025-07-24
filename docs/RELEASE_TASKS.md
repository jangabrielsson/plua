# GitHub Release Tasks - Usage Guide

## Available Release Tasks

### 1. **GitHub: Create Release (Interactive)** 
- **Purpose**: Full interactive release with custom options
- **Features**: 
  - Choose version bump type (patch/minor/major)
  - Enter custom release notes
- **Usage**: Run task → Select version type → Enter release notes

### 2. **GitHub: Create Patch Release (Quick)**
- **Purpose**: Quick patch release with standard message
- **Features**: 
  - Automatically bumps patch version (1.0.54 → 1.0.55)
  - Uses default message: "Patch release - bug fixes and minor improvements"
- **Usage**: Run task → Confirm release

### 3. **GitHub: Create Minor Release (Quick)**
- **Purpose**: Quick minor release with standard message  
- **Features**:
  - Automatically bumps minor version (1.0.54 → 1.1.0)
  - Uses default message: "Minor release - new features and enhancements"
- **Usage**: Run task → Confirm release

### 4. **GitHub: Create Custom Release**
- **Purpose**: Complete control over version and release notes
- **Features**:
  - Enter exact version number (e.g., 2.0.0-beta.1)
  - Custom release notes
- **Usage**: Run task → Enter version → Enter release notes

## How to Run Tasks

### Method 1: Command Palette
1. Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on macOS)
2. Type "Tasks: Run Task"
3. Select one of the GitHub release tasks

### Method 2: Terminal Menu
1. Go to **Terminal** → **Run Task...**
2. Select one of the GitHub release tasks

## Troubleshooting

### "Invalid choice" Error
- **Fixed**: Tasks now use VS Code input prompts instead of shell input
- **Solution**: Use the updated tasks that don't require terminal interaction

### Missing GitHub CLI
- **Error**: "Not authenticated with GitHub CLI"
- **Solution**: Run `gh auth login` in terminal first

### Permission Issues
- **Solution**: Make sure you have push permissions to the repository
- **Solution**: Ensure you're on the correct branch (usually `main`)

## Task Configuration Details

The tasks are configured to:
- ✅ Use proper VS Code input prompts
- ✅ Handle version bumping automatically  
- ✅ Pass arguments correctly to the script
- ✅ Show output in VS Code terminal
- ✅ Work without shell interaction issues

## Script Arguments

The release script accepts these arguments:
```bash
./scripts/create-release.sh [VERSION_TYPE] [RELEASE_NOTES]
```

Examples:
```bash
./scripts/create-release.sh patch "Bug fixes"
./scripts/create-release.sh minor "New features added"  
./scripts/create-release.sh 1.2.3 "Custom version release"
```
