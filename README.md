# 📦 Inventory Management System

**BBAT104 — Fundamentals of Total Quality Management**  
**Quality Goal: Q13 — Faster Search & Retrieval**

An offline desktop-based Inventory Management System developed as a TQM course project. The system focuses on managing inventory efficiently while improving the speed and accuracy of inventory data retrieval.

## 🎯 Core Objective

The primary quality objective is **Faster Search & Retrieval**.

The MVP focuses on:

- 🔎 Dashboard Quick-Search
- 🎛️ Search Filters
- ↕️ Sorting Options
- ⚡ SQLite Database Query Optimization

## ✨ Features

### 🔐 Local Authentication
- First-run account setup
- User name and Store/Warehouse/Business name
- Password-based login
- **Keep Me Logged In** option
- Profile and preference management through Settings

### 📦 Inventory Management
- Add inventory items
- View inventory
- Update inventory
- Delete inventory
- Persistent local data storage

### ⚡ Fast Retrieval
- Quick-search from the dashboard
- Multiple search filters
- Ascending/descending sorting
- Optimized SQLite queries and indexing

### 📴 Offline First
The application does not require:
- Internet
- Cloud services
- Online authentication
- External APIs

All application data is stored locally.

## 🛠️ Tech Stack

| Component | Technology |
|---|---|
| Language | Python 3.11.9 |
| GUI | CustomTkinter |
| Database | SQLite3 |
| Data Processing | Pandas |
| SQC & Charts | Matplotlib / Seaborn |
| Version Control | Git + GitHub |

This stack follows the BBAT104 project guidelines.

## 🏗️ Architecture

```text
User
 │
 ▼
CustomTkinter GUI
 │
 ▼
Python Application
 │
 ├── Authentication
 ├── CRUD Operations
 ├── Search & Filters
 ├── Sorting
 └── Query Optimization
 │
 ▼
SQLite3 Database
```

## 🚀 Setup

### 1. Clone

```bash
git clone <repository-url>
cd Inventory-Management-System
```

### 2. Create Virtual Environment

```bash
python -m venv .venv
```

**Windows:**
```bash
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run

```bash
python app/main.py
```

On first launch, the application will guide the user through account and organization setup.

## 📊 TQM Focus

The project will evaluate the Q13 objective using measurable retrieval performance.

Planned quality activities include:

- FMEA
- SIPOC
- CTQ analysis
- Defect logging
- Pareto analysis
- Fishbone analysis
- PDCA

These activities are part of the BBAT104 project evaluation requirements.

## 📌 Project Status

**🚧 Under Development — Review 1**

- [x] SRS
- [x] Scope Definition
- [ ] System Architecture
- [ ] SQLite Database
- [ ] Authentication
- [ ] CRUD Modules
- [ ] Q13 Search Features
- [ ] Performance Optimization
- [ ] TQM/SQC Analysis
- [ ] Final Demonstration

## 👨‍💻 Developer

**Lokesh Paneru**  
BBAT104 — Fundamentals of TQM  
Academic Session: **2026–27**

---

> **Q13 — Faster Search & Retrieval**  
> *Store inventory efficiently. Find what you need faster.*