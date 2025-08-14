# [file name]: PDFGenerator.py
# [file content begin]
from xhtml2pdf import pisa
import markdown
from io import BytesIO
import re


def generate_pdf(plan_text):
    # Convert markdown to HTML
    html_content = markdown.markdown(plan_text)

    # Add custom styling
    styled_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{ font-family: Helvetica, Arial, sans-serif; line-height: 1.6; }}
            h1 {{ color: #2563eb; text-align: center; }}
            h2 {{ color: #3b82f6; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px; }}
            .activity {{ margin-bottom: 15px; }}
            .time {{ font-weight: bold; color: #0c4a6e; }}
            .transport {{ color: #64748b; }}
            .cost {{ color: #15803d; font-weight: bold; }}
            .day-total {{ color: #b91c1c; font-weight: bold; margin-top: 10px; }}
            ul {{ padding-left: 20px; }}
            li {{ margin-bottom: 8px; }}
        </style>
    </head>
    <body>
        <h1>Personalized Travel Itinerary</h1>
        {html_content}
    </body>
    </html>
    """

    # Create PDF
    pdf_bytes = BytesIO()
    pisa.CreatePDF(styled_html, dest=pdf_bytes)

    if pdf_bytes.tell() == 0:
        raise Exception("PDF generation failed - empty output")

    return pdf_bytes.getvalue()
# [file content end]