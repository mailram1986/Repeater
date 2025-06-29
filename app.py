from flask import Flask, render_template, request
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio
import os

app = Flask(__name__)
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            filepath = os.path.join(UPLOAD_FOLDER, 'uploaded_file.xlsx')
            file.save(filepath)
            return process_file(filepath)
    return render_template('index.html')

def extract_co_scores(df):
    if df is None:
        return None
    for i in range(10):
        candidate_header = df.iloc[i]
        df_trimmed = df[i + 1:].copy()
        df_trimmed.columns = candidate_header.values
        df_trimmed = df_trimmed.reset_index(drop=True)
        reg_col = next((col for col in df_trimmed.columns if 'reg' in str(col).lower()), None)
        co_columns = [col for col in df_trimmed.columns if str(col).strip().upper().startswith("CO")]
        if reg_col and co_columns:
            df_trimmed = df_trimmed[[reg_col] + co_columns].dropna(subset=[reg_col])
            for col in co_columns:
                df_trimmed[col] = pd.to_numeric(df_trimmed[col], errors='coerce')
            return df_trimmed.set_index(reg_col)
    raise ValueError("Unable to detect valid header row with 'Reg. No.' and CO columns")

def process_file(filepath):
    target = 70  # 🎯 Target score
    try:
        excel_file = pd.ExcelFile(filepath)
        metadata_df = excel_file.parse('Metadata')
        ia1_df = excel_file.parse('IA1')
        ia2_df = excel_file.parse('IA2')
        assg_df = excel_file.parse('Assg')
        esem_df = excel_file.parse('ESEM')
        practical_df = excel_file.parse('Practical') if 'Practical' in excel_file.sheet_names else None
    except Exception as e:
        return f"<h3>Error reading sheets: {e}</h3>"

    # Extract metadata
    metadata = {}
    try:
        cols = [col.strip().lower() for col in metadata_df.columns]
        if "field" in cols and "value" in cols:
            metadata_df.columns = [col.strip().title() for col in metadata_df.columns]
            metadata = metadata_df.set_index('Field')['Value'].to_dict()
        else:
            return "<h3>⚠️ Metadata sheet must have 'Field' and 'Value' columns.</h3>"
    except Exception as e:
        return f"<h3>Error reading Metadata: {e}</h3>"

    subject = metadata.get("Subject Name", "Unknown Subject")
    faculty = metadata.get("Faculty Coordinator", "N/A")
    academic_year = metadata.get("Academic Year", "N/A")
    total_students = int(metadata.get("Number of Students", 0))

    # Dynamic weight from metadata (default fallback)
    try:
        theory_percent = float(metadata.get("Theory %", 100))
        practical_percent = float(metadata.get("Practical %", 0))
        total = theory_percent + practical_percent
        if total != 100:
            raise ValueError("Theory % + Practical % must sum to 100")
        theory_weight = theory_percent / 100
        practical_weight = practical_percent / 100
    except Exception:
        theory_weight = 1.0
        practical_weight = 0.0

    practical_exists = practical_weight > 0 and practical_df is not None

    try:
        ia1_scores = extract_co_scores(ia1_df)
        ia2_scores = extract_co_scores(ia2_df)
        assg_scores = extract_co_scores(assg_df)
        esem_scores = extract_co_scores(esem_df)
        practical_scores = extract_co_scores(practical_df) if practical_exists else None
    except Exception as e:
        return f"<h3>Header Detection Error: {e}</h3>"

    internal_avg = ia1_scores.add(ia2_scores, fill_value=0) / 2
    internal_mean = internal_avg.mean()
    assignment_mean = assg_scores.mean()
    esem_mean = esem_scores.mean()
    practical_mean = practical_scores.mean() if practical_exists else None

    co_labels = internal_mean.index.tolist()

    # Chart
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Internal', x=co_labels, y=internal_mean.values, marker_color='steelblue'))
    fig.add_trace(go.Bar(name='Assignment', x=co_labels, y=assignment_mean.values, marker_color='orange'))
    fig.add_trace(go.Bar(name='End Semester', x=co_labels, y=esem_mean.values, marker_color='seagreen'))
    if practical_exists:
        fig.add_trace(go.Bar(name='Practical', x=co_labels, y=practical_mean.values, marker_color='mediumvioletred'))

    fig.add_shape(type='line', x0=-0.5, x1=len(co_labels) - 0.5,
                  y0=target, y1=target,
                  line=dict(color='red', width=2, dash='dash'))
    fig.add_annotation(x=len(co_labels) - 1, y=target + 1,
                       text=f"Target ({target})", showarrow=False,
                       font=dict(color='red'))

    fig.update_layout(
        title=f"Course Attainment – {subject}",
        xaxis_title="Course Outcomes",
        yaxis_title="Average Score",
        barmode='group',
        legend_title="Method",
        height=500
    )

    chart_html = pio.to_html(fig, full_html=False)

    # Weighted score calculation
    theory_score = (internal_avg.add(assg_scores, fill_value=0)
                                .add(esem_scores, fill_value=0)) / 3
    if practical_exists:
        final_score = theory_score * theory_weight + practical_scores * practical_weight
    else:
        final_score = theory_score

    # Attainment table
    attainment_table = []
    attainment_levels = []
    gap_analysis_table = []

    for co in co_labels:
        co_values = final_score[co].dropna()
        count = len(co_values)
        level3 = (co_values >= target * 0.65).sum()
        level2 = ((co_values >= target * 0.55) & (co_values < target * 0.65)).sum()
        level1 = ((co_values >= target * 0.50) & (co_values < target * 0.55)).sum()
        level0 = (co_values < target * 0.50).sum()

        attainment_table.append({
            "Course Outcome": co,
            "Level 3 (≥65%)": int(level3),
            "Level 2 (55–64%)": int(level2),
            "Level 1 (50–54%)": int(level1),
            "Level 0 (<50%)": int(level0),
            "Total Students": int(count)
        })

        percent_attained = (level3 / count) * 100 if count else 0
        level = 3 if percent_attained >= 65 else 2 if percent_attained >= 55 else 1 if percent_attained >= 50 else 0
        attainment_levels.append({"CO": co, "Attainment Level": level})

        attained = co_values.mean() if count else 0
        gap = round(target - attained, 2)
        gap_analysis_table.append({"CO": co, "Target": target, "Attained": round(attained, 2), "Gap": gap})

    return render_template("results.html",
                           chart_html=chart_html,
                           subject=subject,
                           faculty=faculty,
                           academic_year=academic_year,
                           total_students=total_students,
                           attainment_table=attainment_table,
                           attainment_levels=attainment_levels,
                           gap_analysis_table=gap_analysis_table,
                           practical_exists=practical_exists,
                           theory_percent=round(theory_weight * 100),
                           practical_percent=round(practical_weight * 100))

if __name__ == '__main__':
    app.run(debug=True)
