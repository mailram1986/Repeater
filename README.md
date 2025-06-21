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

