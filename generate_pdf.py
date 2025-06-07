
from fpdf import FPDF

# Function to generate and download a PDF
def generate_pdf(drug_name, abstracts):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(200, 10, f"Research Summary for {drug_name}", ln=True, align="C")

    pdf.set_font("Arial", "", 12)
    for abstract in abstracts:
        pdf.multi_cell(0, 10, abstract)
        pdf.ln(5)

    pdf_filename = f"{drug_name}_summary.pdf"
    pdf.output(pdf_filename)
    return pdf_filename
