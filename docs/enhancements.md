---
title: Enhancements
---

# Enhancements (One Artifact, Three Categories)

All three categories are implemented within the same application, **batchRename**.

---

## 1) Software Design & Engineering

### A. Description
The artifact selected is **batchRename**, a Python-based application originally created for paralegal work to automate file renaming and PDF unlocking. During the capstone, the program was refactored from a single-purpose script into a **multi-tool suite** with a main menu built using CustomTkinter. Each tool now resides in its own logical module with consistent UI design and centralized settings.

### B. Justification
This enhancement was selected because it demonstrates my ability to apply software engineering practices to improve scalability, maintainability, and usability. By separating tools into independent modules and introducing a configurable settings system, the program became easier to extend, test, and support. Dependency on external tools (7-Zip) was removed in favor of Python’s standard `zipfile` library, improving portability across systems. These changes showcase skills in modular design, GUI development, and user-focused engineering.

### C. Reflection
Through this process, I learned how much effort is required to isolate and refactor existing functionality without breaking it. The main challenge was restructuring the code to ensure each tool operated independently while still feeling cohesive as part of the suite. Feedback from earlier iterations guided improvements to user experience, including more informative error handling and unified configuration management. This enhancement aligns with course outcomes related to professional communication, robust engineering practices, and building software that delivers value in real-world contexts.

---

## 2) Algorithms & Data Structures

### A. Description
The renaming logic in batchRename was redesigned to improve reliability and efficiency. Enhancements included implementing a **batch undo mechanism** using a stack, collision detection using a dictionary for duplicate filenames, and refactoring the rename pipeline to separate file name generation from file system operations.

### B. Justification
This enhancement was selected because it highlights algorithmic thinking applied to a practical file system problem. The undo stack ensures that renaming operations can be safely rolled back in a single session, reducing the risk of incomplete or inconsistent results. Dictionary-based lookups provide O(1) performance for duplicate detection, preventing conflicts before they occur. Refactoring the pipeline improved testability and abstraction, demonstrating clear trade-offs between efficiency, safety, and usability.

### C. Reflection
While implementing these enhancements, I realized how tightly coupled the original logic was to direct file operations. Decoupling name generation from file system calls made the program easier to test and extend. One challenge was ensuring undo operations worked correctly even when collisions or errors occurred mid-process. Incorporating feedback led to better error messages and more predictable outcomes. These improvements demonstrate mastery of data structures, algorithm design, and problem-solving strategies consistent with course outcomes.

---

## 3) Databases

### A. Description
An **SQLite database** was integrated into batchRename to log client and statement information. The application now scans target folders for statements matching predefined patterns (`x[ACCT] - YYYYMMDD.pdf` or `x[ACCT] - YYYYMM.pdf`), extracts account and date metadata, checks for duplicates, and stores results in a normalized schema with Clients and Statements tables. The interface includes the ability to view and filter statements by client or account, with options to open files directly.

### B. Justification
This enhancement was selected because it demonstrates the ability to incorporate persistent data storage into an application. SQLite was chosen for its portability and ease of integration, which fit the scope of a desktop tool. The database ensures statements are tracked consistently across sessions, avoids duplicate entries, and supports search and retrieval functionality. This work demonstrates skills in schema design, SQL query writing, and linking GUI inputs to underlying data storage.

### C. Reflection
The biggest challenge was ensuring reliable parsing of filenames and handling inconsistent inputs. Feedback emphasized the importance of validation and duplicate detection, which I implemented using parameterized queries and checks before insertion. I also learned how small-scale databases can add significant long-term value to even a single-user tool. This enhancement aligns with outcomes involving database design, software engineering practices, and the development of a security mindset by validating data and minimizing exposure of sensitive client details.

---

## Links to Code

- **Repository:** <https://github.com/BylliGoat/batchRename>  
