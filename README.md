# CALI Schools Multi-Term Result Portal 🎓🇳🇬

A secure, multi-tier school management and terminal result portal designed for Nigerian primary and secondary institutions, built with **Django 5**, **HTMX**, **Alpine.js**, and **Tailwind CSS**.

---

## 🏛️ Educational Levels Covered

- **Early Years Foundation Stage**: Pre-Nursery, Nursery 1, Nursery 2, Nursery 3/KG
  - Developmental milestones (Affective/Psychomotor star ratings) + Cognitive numeric scores.
  - Custom Cheerful Report Card with developmental progress observations.
- **Primary Section**: Basic 1 to 6
  - Continuous Assessment format (CA1 10, CA2 10, Exam 80 = 100).
  - Configurable A–F grade scale with remarks and class ranking.
- **Junior Secondary (JSS 1–3 / BECE)**:
  - Revised 9-Year Basic Education Curriculum:
    - **Intermediate Science** *(replaces separate Basic Science & Basic Technology)*
    - **Digital Technology** *(replaces legacy Computer Studies)*
    - **Pre-Vocational Studies (PVS)** *(integrates Agriculture & Home Economics)*
    - Business Studies, Social Studies, Civic Education, CCA, PHE, Nigerian Languages, CRS/IRS, French.
- **Senior Secondary (SS 1–3 / WASSCE & NECO)**:
  - Full **WAEC Standard 9-Point Scale** (`A1` to `F9`).
  - Core Compulsory: English Language, General Mathematics, Civic Education.
  - WAEC Trade / Entrepreneurship Subjects (Data Processing, Catering Craft, Garment Making, Animal Husbandry, Fisheries, Marketing, Electrical Installation).
  - Departmental Tracks: **Science**, **Arts & Humanities**, **Commercial / Business**.

---

## 🚀 Key Features

1. **Multi-Ward Parent Access**: Parents log in once via Phone or Admission Number + PIN to access all their children across Nursery, Primary, and Secondary.
2. **Strict School Fees Paywall**: Report cards are locked until school fees are cleared; includes direct **Paystack** checkout and bank transfer payment details.
3. **HTMX Real-Time Gradebook**: Autosaving score entry tables with debounce, instant grade calculations, and offline network loss detection.
4. **Nigerian National Subject Bank**: Pre-seeded catalog with 82 official curriculum subjects that school administrators can toggle on/off with 1-click.
5. **Security & NDPA 2023 Compliance**: `django-axes` brute-force lockout, 30-minute inactivity timeouts, child data privacy protection, and state-machine score locking (`Draft` $\rightarrow$ `Submitted` $\rightarrow$ `Reviewed` $\rightarrow$ `Approved & Locked`).
6. **Bespoke Nigerian UI & Print Engine**: Anti-counterfeiting guilloche certificate borders, animated Aurora mesh gradients, Alpine data-saver toggle (< 150 KB budget), and WeasyPrint A4 PDF compilation.

---

## 🛠️ Quickstart Installation

### 1. Clone repository & setup virtual environment
```bash
git clone https://github.com/Richseun186/C.A.L.I.git
cd C.A.L.I
python -m venv .venv

# On Windows:
.\.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run database migrations
```bash
python manage.py migrate
```

### 4. Seed initial academic data & Nigerian subject bank
```bash
# Seed school classes, sample staff, parent, and pupils
python manage.py seed_cali_school

# Seed official Nigerian National Subject Bank (82 subjects)
python manage.py seed_nigerian_subject_bank
```

### 5. Launch the development server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/` in your browser.

---

## 🔑 Demo & Test Credentials

| Role | Username / Identifier | Password / PIN | Description |
| :--- | :--- | :--- | :--- |
| **Super Admin** | `admin@calischools.ng` | `AdminPass123!` | Access to `/admin/` and `/academics/subject-bank/` |
| **Parent (3 Wards)** | `08031234567` | `123456` | Single login viewing 3 wards across Nursery, Primary, and SS |
| **Nursery Teacher** | `nursery.teacher@calischools.ng` | `TeachPass123!` | Nursery 2 Rainbow score entry gradebook |
| **Primary Teacher** | `primary.teacher@calischools.ng` | `TeachPass123!` | Primary 4 Gold score entry gradebook |
| **Secondary Teacher** | `secondary.teacher@calischools.ng` | `TeachPass123!` | SS 2 Science Physics gradebook |
| **Pupil 1 (Nursery)** | `CALI/2026/001` | `123456` | Fees Cleared &bull; Cheerful Early Years Progress Card |
| **Pupil 2 (Primary)** | `CALI/2024/042` | `123456` | Fees Outstanding &bull; Fee Paywall Screen & Paystack |
| **Student 3 (SS 2)** | `CALI/2021/108` | `123456` | Fees Cleared &bull; WAEC A1-F9 Card with Class Rank & Confetti |

---

## 🧪 Running Automated Tests
```bash
python manage.py test tests
```
Runs test cases verifying authentication, HTMX inline score editing, grading algorithms, and fee-gated report access.

---

## 📄 License
Proprietary software for CALI Schools Nigeria. Compliant with Nigeria Data Protection Act (NDPA 2023).
