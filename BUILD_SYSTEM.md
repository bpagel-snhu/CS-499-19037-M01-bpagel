# Build Date System

This document explains how the build date system works in the batch_renamer application.

## Overview

The application displays a build date in the bottom-right corner of the main menu. This date should reflect when the application was last built/updated, not just the current date.

## How It Works

The build date system uses a multi-tier fallback approach:

1. **Build-time constant** (`__BUILD_DATE__`) - For compiled versions
2. **Generated build info** (`build_info_generated.py`) - For build scripts
3. **Git commit date** - For development versions with Git history
4. **File modification time** - Fallback using main.py modification time
5. **Current date** - Final fallback

## Development Mode

When running the application in development mode (directly with `python main.py`), the system will:

1. Try to get the date from the last Git commit
2. If no Git info is available, use the modification time of `main.py`
3. Display the date in format: `Build: 2024-01-15 (abc1234)` (with commit hash if available)
4. Include branch information if not on `main` or `master`: `Build: 2024-01-15 (abc1234) [dev]`

## Production Builds

For compiled versions (using PyInstaller, cx_Freeze, etc.), you can generate build information:

### Using the Build Utils Script

```bash
# Generate build info for compiled versions
python build_utils.py build-info

# Generate version file for other build tools
python build_utils.py version
```

This will create `batch_renamer/build_info_generated.py` with build-time constants.

### Integration with Build Tools

#### PyInstaller
Add to your `.spec` file:
```python
# In your .spec file
import build_utils
build_utils.generate_build_info_py()

# Then include the generated file
a = Analysis(
    ['main.py'],
    datas=[('batch_renamer/build_info_generated.py', 'batch_renamer')],
    # ... other options
)
```

#### cx_Freeze
Add to your `setup.py`:
```python
import build_utils
build_utils.generate_build_info_py()

# Include the generated file in your build
executables = [
    Executable('main.py', base=base)
]
```

## Build Information Display

The build information is displayed in the following formats:

- **Main branch with Git info**: `Build: 2024-01-15 (abc1234)`
- **Development branch with Git info**: `Build: 2024-01-15 (abc1234) [dev]`
- **Main branch without Git info**: `Build: 2024-01-15`
- **Development branch without Git info**: `Build: 2024-01-15 [dev]`

**Note**: Branch information is only shown when not on `main` or `master` branches.

## About Dialog

The build information is also displayed in the About dialog (accessible from Settings → About). The About dialog shows:

- Application name and description
- Developer information
- Version number
- Build date and commit information
- Branch information (when not on main/master)
- Full commit hash (when available)

This provides users with comprehensive information about the application version they're running.

## Files Involved

- `batch_renamer/build_info.py` - Main build info module
- `batch_renamer/ui/main_menu_frame.py` - Uses build info for display
- `batch_renamer/ui/main_window.py` - Displays build info in UI
- `batch_renamer/ui/settings_frame.py` - Shows build info in About dialog
- `build_utils.py` - Build utility script
- `BUILD_SYSTEM.md` - This documentation

## Best Practices

1. **Always commit your changes** before building - this ensures the build date reflects the actual last update
2. **Use the build utils script** for production builds to ensure consistent build information
3. **Test the build date** after compilation to ensure it's working correctly
4. **Consider versioning** - you can extend the system to include version numbers and release information

## Troubleshooting

### Build date shows current date instead of commit date
- Ensure you're in a Git repository
- Check that Git is installed and accessible
- Verify that you have committed your changes

### Build date not updating after commits
- The system uses the last commit date, not the current date
- Make sure to commit your changes to see the updated build date

### Build info not working in compiled version
- Ensure you're using the build utils script to generate build info
- Check that the generated file is included in your build
- Verify the import paths in the build_info.py module 