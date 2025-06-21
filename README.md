# Repeater

# 📊 Course Outcome (CO) Attainment Calculator – Flask Web App

This Flask web application allows you to calculate and visualize the attainment of Course Outcomes (COs) based on student performance data from **Internal Assessments (IA1, IA2)**, **Assignments**, and **End Semester Exams**.

---

## 🚀 Features

- Upload Excel file with multiple sheets (IA1, IA2, Assg, ESEM, Metadata)
- Automatically parses CO marks for all students
- Calculates average CO-wise attainment across all evaluation methods
- Displays:
  - 📈 Grouped bar chart with target line
  - 🧮 Attainment level table (Level 3, 2, 1)
- Reads course metadata and shows it in the graph header

---

## 📁 Folder Structure

co-attainment-flask/
├── app.py
├── uploads/
├── templates/
│ ├── index.html
│ └── results.html
├── static/ # (Optional for CSS/images if needed)
└── README.md

## ✅ Requirements

Create a virtual environment and install:

```bash
pip install flask pandas openpyxl plotly


# 1. Clone this repo
git clone https://github.com/your-username/co-attainment-flask.git
cd co-attainment-flask

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the Flask app
python app.py

Then open your browser and go to:
http://127.0.0.1:5000/

# Command help for debugging flask web
sudo netstat -tulnp | grep :5000
sudo kill -9 <PID>

📝 Excel File Format
Your Excel file must contain 5 sheets named as follows:

1. Metadata (Required)
Field	Value
Subject Name	Bioinformatics
Faculty Coordinator	Dr. Ram K
Academic Year	2024-2025
Number of Students	30

2. IA1, IA2, Assg, ESEM (student marks)
Each should have:

One row with CO headers: Reg No, CO1, CO2, ..., CO6

Below that, 1 row per student with numeric scores

Example:

Reg No	CO1	CO2	CO3	CO4	CO5	CO6
20BTS001	72	65	78	74	80	68
20BTS002	85	70	90	88	75	72
...	...	...	...	...	...	...

📊 Attainment Table Logic
Each CO is classified into 3 levels based on average mark:

Level 3 (Score ≥ Target) → e.g., ≥ 70

Level 2 (60 ≤ Score < Target)

Level 1 (Score < 60)

🔧 Customization
Change the target score in app.py:

python
Copy
Edit
**target = 70  # Customize your threshold**
Add PO mapping logic, CSV downloads, or authentication if needed.

