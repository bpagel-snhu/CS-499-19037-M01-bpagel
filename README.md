# 📂 batchRename

A Python GUI application designed to **bulk rename PDF files** based on **position-based date extraction**. Built for **legal discovery responses** or document processing where consistent renaming is required.

---

![batchRename Screenshot](batchRename_Screenshot.png)

---
## ✅ Features
- **CustomTkinter GUI** for ease of use
- **Position-based parsing** for extracting Year, Month, and optional Day from filenames
- **Textual Month normalization** (e.g., `"January"` → `"01"`)
- **Optional Day extraction toggle**
- **Filename length enforcement** to skip invalid files
- **Duplicate prevention** with auto appending (`_1`, `_2`, etc.)
- **Real-time rename preview**
- **Summary of renamed and skipped files**
- **Backup functionality**

---

## 📦 Installation
### Clone the Repository:
```bash
git clone https://github.com/BylliGoat/batchRename.git
cd batchRename
```

### Install Dependencies:
Create a virtual environment (recommended):
```bash
python -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

### Requirements:
- **python==3.12**
- **customtkinter==5.2.2**
- **pikepdf==9.10.2**
- **pytest==8.4.1**

---

## 🧪 Testing
Run the test suite:
```bash
python -m pytest
```

Run tests with coverage report:
```bash
python -m pytest --cov=batch_renamer
```

---

## 🚀 Running the Application
```bash
python main.py
```
Follow the GUI prompts to:
1. Select a target folder
   - Create a backup (saves to Downloads > Renamer Backups)
   - Unlock PDFs (flattens all PDF files in folder)
   - Select the sample file for renaming
2. Add prefix to prefix field (include spaces)
3. Normalize textual months (if prompted)
4. Adjust slider positions for Year, Month, Day
5. Run the bulk rename

---

## 🧠 Example Workflow
### Before:
```
Spend-Statement-123456789-2021-07.pdf
Spend-Statement-123456789-2022-08.pdf
```
### After:
```
202107.pdf
202208.pdf
```
or (if prefix included):
```
x1234 - 202107.pdf
x1234 - 202208.pdf
```

- Duplicate target filenames automatically renamed with `_1`, `_2`, etc.

---

## 🔨 Optional: Build Standalone Executable
```bash
pyinstaller --onefile --windowed --name batchRename main.py
```
✅ Output: `/dist/batchRename.exe`

---

## 🛠 Future Plans:
- Undo functionality
- Logging renamed files
- Drag-and-drop support
- Modularize for multi-tool support

---

## 📜 License
This project is licensed under the **MIT License**.

---

## 📬 Contact
GitHub: [https://github.com/BylliGoat/batchRename](https://github.com/BylliGoat/batchRename)