# 🗂️ Barron Pagel File Utilities

A comprehensive Python GUI suite for file processing utilities, originally developed for bulk file processing of bank statements during the discovery process in family law cases. Features a modern, branded interface with tools for **bulk renaming**, **PDF unlocking**, and **database logging** for client management.

---

![Main Menu Screenshot](BPFileUtilities_MainMenu.png)

---

## ✨ Features

### 🎯 Core Functionality
- **Modular Tool Suite**: Three main tools with unified interface
- **CustomTkinter GUI**: Modern dark theme with Barron Pagel branding
- **Main Menu Navigation**: Easy tool selection with logo integration
- **Robust Error Handling**: Comprehensive logging and user feedback
- **Cross-Platform Support**: Windows, macOS, and Linux compatibility

### 📁 Bulk Rename Tool
![Bulk Rename Screenshot](BPFileUtilities_BulkRename.png)

- **Position-based Date Extraction**: Extract Year, Month, Day from filename positions
- **Textual Month Normalization**: Automatic conversion (e.g., "January" → "01")
- **Flexible Naming Options**: Custom prefixes, length enforcement, duplicate prevention
- **Real-time Preview**: See changes before applying
- **Undo Functionality**: Revert last rename operation
- **Backup System**: Internal .zip backups (no external dependencies)
- **Smart File Handling**: Automatic skipping of invalid files and duplicate resolution

### 🔓 PDF Unlock Tool
![PDF Unlock Screenshot](BPFileUtilities_PDFUnlock.png)

- **Batch Processing**: Remove security from all PDFs in a folder
- **Comprehensive Unlocking**: Handles digital signatures, edit restrictions, permissions
- **Safe Overwriting**: Replaces originals with unlocked versions
- **Error Recovery**: Graceful handling of corrupted or protected files

### 🗄️ Database Logging Tool
- **Client Management**: Add, edit, and manage client information
- **SQLite Database**: Local storage in `~/.bpfu/database/clients.db`
- **Active/Archived Filtering**: Toggle between active and archived clients
- **Account Overview**: Track bank statements and account information
- **Statement Viewer**: View and manage imported bank statements
- **Import Manager**: Bulk import client data and statements

---

## 🚀 Quick Start

### Prerequisites
- **Python 3.12+**
- **Git** (for cloning)

### Installation

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/BylliGoat/batchRename.git
   cd batchRename
   ```

2. **Create Virtual Environment** (Recommended):
   ```bash
   python -m venv .venv
   
   # Windows
   .\.venv\Scripts\activate
   
   # macOS/Linux
   source .venv/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application**:
   ```bash
   python main.py
   ```

---

## 📋 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| `customtkinter` | 5.2.2 | Modern GUI framework |
| `pikepdf` | 9.10.2 | PDF processing and unlocking |
| `Pillow` | 11.3.0 | Image processing for UI |
| `pytest` | 8.4.1 | Testing framework |

---

## 🎮 Usage Guide

### Main Menu
- Launch the application to see the main menu with Barron Pagel branding
- Select from three available tools or access settings
- Build information is displayed at the bottom of the window

### Bulk Rename Workflow
1. **Select Target**: Choose folder and sample file
2. **Configure Options**: Set prefix, enable month normalization, adjust position sliders
3. **Preview**: Review changes in real-time
4. **Backup** (Optional): Create .zip backup before processing
5. **Execute**: Click "Rename All Files" to process
6. **Undo** (if needed): Use "Undo Last Rename" to revert

**Example Transformation**:
```
Before:
Spend-Statement-123456789-2021-07-22.pdf
Spend-Statement-123456789-2022-08-23.pdf

After (with prefix "x1234"):
x1234 - 20210722.pdf
x1234 - 20220823.pdf
```

### PDF Unlock Workflow
1. **Select Folder**: Choose directory containing PDFs
2. **Process**: Click "Unlock PDFs" to remove security
3. **Monitor**: Watch progress bar and status updates
4. **Complete**: All PDFs become fully editable

### Database Logging Workflow
1. **Add Clients**: Use dialog to add new clients
2. **Manage Data**: View, edit, and archive clients
3. **Import Statements**: Bulk import bank statements
4. **Track Accounts**: Monitor account information and statements

---

## 🧪 Testing

Run the test suite:
```bash
# Basic tests
python -m pytest

# With coverage report
python -m pytest --cov=batch_renamer

# Verbose output
python -m pytest -v
```

**Note**: The test suite was primarily for development practice and may be updated in future releases.

---

## 🛠️ Building Standalone Executable

Create a standalone executable using PyInstaller:

```bash
# Install PyInstaller (if not already installed)
pip install pyinstaller

# Build executable
pyinstaller --onefile --windowed --name BPFileUtilities main.py
```

**Output**: `dist/BPFileUtilities.exe` (Windows) or `dist/BPFileUtilities` (macOS/Linux)

---

## 🏗️ Project Structure

```
batchRename/
├── batch_renamer/
│   ├── tools/
│   │   ├── bulk_rename/          # Bulk rename functionality
│   │   ├── database_logging/     # Client and statement management
│   │   └── pdf_unlock/          # PDF security removal
│   ├── ui/                      # User interface components
│   ├── utils.py                 # Utility functions
│   └── constants.py             # Application constants
├── tests/                       # Test suite
├── main.py                      # Application entry point
└── requirements.txt             # Python dependencies
```

---

## 🔧 Configuration

The application automatically creates configuration files in:
- **Windows**: `%APPDATA%\.bpfu\`
- **macOS**: `~/Library/Application Support/.bpfu/`
- **Linux**: `~/.bpfu/`

**Note**: the application has only been tested on Windows, and other operating systems are not officially supported at this time.

Configuration includes:
- Database location
- Backup preferences
- UI settings
- Logging preferences

---

## 🚧 Future Development

### Planned Features
- **macOS Support**
- **Drag-and-Drop Support**
- **General UI Enhancements**

### Contributing
This project is actively maintained. For contributions:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

## 📜 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

---

## 📞 Support & Contact

- **GitHub Repository**: [https://github.com/BylliGoat/batchRename](https://github.com/BylliGoat/batchRename)
- **Issues**: Report bugs and feature requests via GitHub Issues
- **Pull Requests**: Welcome contributions and improvements

---

*Built with ❤️ for efficient file processing workflows*