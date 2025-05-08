from fpdf import FPDF
from datetime import datetime

def generate_pdf(user_details, college_list):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)

    # Title
    pdf.cell(200, 10, "College Predictor Report", ln=True, align="C")
    pdf.ln(10)

    # User details
    pdf.set_font("Arial", "", 12)
    for key, value in user_details.items():
        pdf.cell(200, 10, f"{key}: {value}", ln=True)

    pdf.ln(10)
    pdf.cell(200, 10, "Predicted Colleges:", ln=True)
    pdf.ln(5)

    # College details
    for idx, college in enumerate(college_list, 1):
        pdf.cell(200, 10, f"{idx}. {college['college_name']} - {college['branch']} ({college['branch_code']})", ln=True)

    # Save PDF
    filename = f"static/reports/college_report_{datetime.now().strftime('%Y%m%d%H%M%S')}.pdf"
    pdf.output(filename)
    return filename
