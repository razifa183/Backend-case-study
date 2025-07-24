
# 🚀 Bynry Backend Engineering Case Study

This repository contains my solution to the Backend Engineering Intern Case Study provided by **Bynry Inc.** It demonstrates practical backend development skills through:

- Code debugging
- Database design
- API implementation

---

## 🧠 Case Study Breakdown

### ✅ Part 1: Code Review & Debugging
- Fixed missing validations
- Handled duplicate SKU checks
- Added transactional safety using rollback
- Improved response status codes

### ✅ Part 2: Database Design
- Designed normalized tables for:
  - Products, Warehouses, Companies
  - Inventory, Inventory Logs
  - Suppliers (many-to-many)
  - Bundled products (recursive relation)
- Used SQLAlchemy for ORM modeling

### ✅ Part 3: Low-Stock Alert API
- Returns products that are:
  - Active (recent sales)
  - Below stock threshold
- Returns supplier info and estimated days until stockout

---

## ⚙️ Tech Stack

- Python 3.11
- Flask (Micro web framework)
- Flask-SQLAlchemy (ORM)
- SQLite (for local development)
- Postman / Browser (for testing)
- Git & GitHub (for version control)

---

bynry-backend-case-study/
│
├── app/                            # 🔧 Application package
│   ├── __init__.py                 # (empty file) Makes app a Python package
│   ├── models.py                   # SQLAlchemy models (Product, Warehouse, etc.)
│   └── routes.py                   # All route handlers (API logic)
│
├── main.py                         # Flask app entry point (runs the server)
├── insert.py            # Script to populate dummy test data
├── requirements.txt                # Python dependencies
├── CASE_STUDY_RESPONSE.md          # Written answers for Part 1, 2, and 3 of the case study
├── README.md                       # Project summary, setup, API docs, and run instructions
├── .gitignore                      # Files to ignore (optional, e.g., venv, __pycache__)


