import os
import io

from datetime import datetime

from flask import (
    Flask,
    request,
    jsonify,
    send_file
)

from flask_cors import CORS

from pypdf import (
    PdfReader,
    PdfWriter
)

from reportlab.pdfgen import canvas
from dotenv import load_dotenv
# ======================================
# FLASK APP
# ======================================

app = Flask(__name__)

CORS(app)

load_dotenv()
# ======================================
# ADMIN LOGIN
# ======================================

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD")

# ======================================
# HOME
# ======================================

@app.route("/")
def home():

    return "Flask Backend Running"

# ======================================
# ADMIN LOGIN API
# ======================================

@app.route("/admin-login", methods=["POST"])
def admin_login():

    try:

        data = request.get_json()

        username = data.get(
            "username",
            ""
        )

        password = data.get(
            "password",
            ""
        )

        if (
            username == ADMIN_USERNAME
            and
            password == ADMIN_PASSWORD
        ):

            return jsonify({
                "success": True,
                "message": "Login Successful"
            })

        return jsonify({
            "success": False,
            "message": "Invalid Username or Password"
        })

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

# ======================================
# PDF GENERATION API
# ======================================

@app.route("/generate-pdf", methods=["POST"])
def generate_pdf():

    try:

        # ======================================
        # GET JSON DATA
        # ======================================

        data = request.get_json()

        print("Received Data :", data)

        # ======================================
        # GET VALUES
        # ======================================

        ref_id = str(
            data.get("ref_id", "")
        )

        candidate_name = str(
            data.get("candidate_name", "")
        )

        email_id = str(
            data.get("email_id", "")
        )

        college_name = str(
            data.get("clgname", "")
        )

        start_date_raw = str(
            data.get("start_date", "")
        )

        end_date_raw = str(
            data.get("end_date", "")
        )

        # ======================================
        # VALIDATION
        # ======================================

        if (
            ref_id == "" or
            candidate_name == "" or
            email_id == "" or
            college_name == "" or
            start_date_raw == "" or
            end_date_raw == ""
        ):

            return jsonify({
                "success": False,
                "message": "All Fields Required"
            }), 400

        # ======================================
        # DATE FORMAT
        # ======================================

        start_date = datetime.strptime(
            start_date_raw,
            "%Y-%m-%d"
        ).strftime("%d-%m-%Y")

        end_date = datetime.strptime(
            end_date_raw,
            "%Y-%m-%d"
        ).strftime("%d-%m-%Y")

        current_date = datetime.now().strftime(
            "%d-%m-%Y"
        )

        # ======================================
        # LOAD PDF TEMPLATE
        # ======================================

        BASE_DIR = os.path.dirname(
            os.path.abspath(__file__)
        )

        pdf_path = os.path.join(
            BASE_DIR,
            "OfferLetter.pdf"
        )

        if not os.path.exists(pdf_path):

            return jsonify({
                "success": False,
                "message": "OfferLetter.pdf Not Found"
            }), 404

        existing_pdf = PdfReader(
            open(pdf_path, "rb")
        )

        output = PdfWriter()

        # ======================================
        # CREATE OVERLAY
        # ======================================

        packet = io.BytesIO()

        can = canvas.Canvas(packet)

        # ======================================
        # REF ID
        # ======================================

        can.setFont(
            "Times-Bold",
            13
        )

        can.drawString(
            120,
            661,
            ref_id
        )

        # ======================================
        # CURRENT DATE
        # ======================================

        can.drawString(
            105,
            634,
            current_date
        )

        # ======================================
        # CANDIDATE NAME
        # ======================================

        can.drawString(
            103,
            517,
            f"{candidate_name},"
        )

        # ======================================
        # EMAIL
        # ======================================

        can.setFont(
            "Times-Roman",
            14
        )

        can.drawString(
            72,590, candidate_name
        )
        can.drawString(
            72,
            570,
            email_id
        )

        # ======================================
        # COLLEGE NAME
        # ======================================

        can.drawString(
            72,
            550,
            college_name
        )

        # ======================================
        # START DATE
        # ======================================

        can.setFont(
            "Times-Bold",
            10
        )

        can.drawString(
            318,
            395,
            start_date
        )

        # ======================================
        # END DATE
        # ======================================

        can.drawString(
            458,
            395,
            end_date
        )

        # ======================================
        # SAVE OVERLAY
        # ======================================

        can.save()

        packet.seek(0)

        overlay_pdf = PdfReader(packet)

        # ======================================
        # MERGE FIRST PAGE
        # ======================================

        first_page = existing_pdf.pages[0]

        first_page.merge_page(
            overlay_pdf.pages[0]
        )

        output.add_page(first_page)

        # ======================================
        # ADD REMAINING PAGES
        # ======================================

        for page_num in range(
            1,
            len(existing_pdf.pages)
        ):

            output.add_page(
                existing_pdf.pages[page_num]
            )

        # ======================================
        # OUTPUT PDF PATH
        # ======================================

        output_path = os.path.join(
            BASE_DIR,
            "Generated_Offer_Letter.pdf"
        )

        # ======================================
        # SAVE PDF
        # ======================================

        with open(
            output_path,
            "wb"
        ) as outputStream:

            output.write(outputStream)

        # ======================================
        # RETURN PDF
        # ======================================

        return send_file(
            output_path,
            as_attachment=True,
            download_name="OfferLetter.pdf"
        )

    except Exception as e:

        print("ERROR :", e)

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


# ==============================
# VERIFY CERTIFICATE
# ==============================

@app.route(
    "/verify-certificate",
    methods=["POST"]
)
def verify_certificate():

    data = request.get_json()

    ref_id = data.get("ref_id")

    # DEMO VALIDATION

    if ref_id:

        return jsonify({

            "success": True,

            "ref_id": ref_id

        })

    return jsonify({

        "success": False

    })

# ==============================
# DOWNLOAD CERTIFICATE
# ==============================

@app.route(
    "/download-certificate",
    methods=["POST"]
)
def download_certificate():

    return send_file(

        "Generated_Offer_Letter.pdf",

        as_attachment=True
    )
# ======================================
# RUN APP
# ======================================

if __name__ == "__main__":

    app.run(
        debug=True
    )