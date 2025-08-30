from xhtml2pdf import pisa
import markdown
from io import BytesIO
import re


def generate_pdf(plan_text, transport_mode="plane"):
    # Convert markdown to HTML
    html_content = markdown.markdown(plan_text)

    # Determine transportation-specific styling
    transport_style = ""
    if transport_mode.lower() != 'plane':
        transport_style = """
        .route-info {
            background-color: #e8f5e8;
            border-left: 4px solid #38a169;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }
        .transport-icon {
            color: #2d3748;
            font-weight: bold;
        }
        """
    else:
        transport_style = """
        .route-info {
            background-color: #e6f7ff;
            border-left: 4px solid #1890ff;
            padding: 15px;
            margin: 15px 0;
            border-radius: 5px;
        }
        """

    # Add custom styling with transportation-specific styles
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
            {transport_style}

            /* Route information styling */
            .route-details {{
                background-color: #f7fafc;
                padding: 12px;
                border-radius: 4px;
                margin: 10px 0;
                border-left: 3px solid #4299e1;
            }}

            /* Transportation mode specific colors */
            .car-route {{ border-left-color: #4299e1; background-color: #ebf4ff; }}
            .bike-route {{ border-left-color: #48bb78; background-color: #f0fff4; }}
            .bus-route {{ border-left-color: #ed8936; background-color: #fffaeb; }}
            .train-route {{ border-left-color: #9f7aea; background-color: #faf5ff; }}
        </style>
    </head>
    <body>
        <h1>Personalized Travel Itinerary</h1>
        {html_content}
    </body>
    </html>
    """

    # Enhance route information display if present
    if transport_mode.lower() != 'plane':
        # Add transportation mode class to route details
        route_class = f"{transport_mode.lower()}-route"
        styled_html = re.sub(
            r'(<p>.*[Rr]oute.*</p>|<h[1-6]>.*[Rr]oute.*</h[1-6]>)',
            f'<div class="route-details {route_class}">\\1</div>',
            styled_html
        )

    # Create PDF
    pdf_bytes = BytesIO()
    pisa_status = pisa.CreatePDF(styled_html, dest=pdf_bytes)

    if pdf_bytes.tell() == 0 or pisa_status.err:
        raise Exception(f"PDF generation failed: {pisa_status.err}")

    return pdf_bytes.getvalue()