# Environment Setup & Dependency Instructions

## 1. Prerequisites

- **Python**: Python 3.11.x (tested on Python 3.11.9)
- **Operating System**: Windows 10/11 (fully offline compatible)
- **SQLite3**: Built into Python standard library (no external installation required)

---

## 2. Setting Up the Virtual Environment

Open a terminal (PowerShell or Command Prompt) and navigate to the project root:

```powershell
cd "c:\Users\kamal\Documents\TQM Project\inv_mng_sys"
```

### Create the Virtual Environment:
```powershell
python -m venv .venv
```

### Activate the Virtual Environment:

- **Windows (PowerShell)**:
  ```powershell
  .venv\Scripts\Activate.ps1
  ```
  *(If execution policies restrict running scripts, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in your session)*

- **Windows (Command Prompt)**:
  ```cmd
  .venv\Scripts\activate.bat
  ```

- **Linux / macOS**:
  ```bash
  source .venv/bin/activate
  ```

---

## 3. Install Dependencies

Once the virtual environment is activated, install the required packages:

```powershell
pip install --upgrade pip
pip install -r requirements.txt
```

### Included Packages:
- `customtkinter`: Modern UI library built on Tkinter.
- `pandas`: Data manipulation and dataset operations.
- `matplotlib` & `seaborn`: SQC / TQM statistical plotting and charts.
- `pytest`: Clean test discovery and execution (alongside built-in `unittest`).

---

## 4. Running the Tests

To run the database and unit test suite:

```powershell
# Using Python's built-in unittest:
python -m unittest discover -s tests -p "test_*.py"

# Or using pytest:
pytest
```

---

## 5. Running the Application

To launch the Inventory Management System:

```powershell
python run.py
# or
python app/main.py
```
