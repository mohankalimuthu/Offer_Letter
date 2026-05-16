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
# LOAD ENV
# ======================================

load_dotenv()

# ======================================
# FLASK APP
# ======================================

app = Flask(__name__)

CORS(app)

# ======================================
# ENV VARIABLES
# ======================================

ADMIN_USERNAME = os.getenv(
    "ADMIN_USERNAME",
    "admin"
)

ADMIN_PASSWORD = os.getenv(
    "ADMIN_PASSWORD",
    "admin123"
)

# ======================================
# BASE DIRECTORY
# ======================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

# ======================================
# HOME
# ======================================

@app.route("/")
def home():

    return jsonify({
        "success": True,
        "message": "Flask Backend Running"
    })

# ======================================
# ADMIN LOGIN
# ======================================

@app.route(
    "/admin-login",
    methods=["POST"]
)
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

            "message":
            "Invalid Username or Password"

        })

    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500

# ======================================
# GENERATE PDF
# ======================================

@app.route(
    "/generate-pdf",
    methods=["POST"]
)
def generate_pdf():

    try:

        data = request.get_json()

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
            not ref_id or
            not candidate_name or
            not email_id or
            not college_name or
            not start_date_raw or
            not end_date_raw
        ):

            return jsonify({

                "success": False,

                "message":
                "All Fields Required"

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
        # TEMPLATE PDF
        # ======================================

        template_path = os.path.join(
            BASE_DIR,
            "OfferLetter.pdf"
        )

        if not os.path.exists(
            template_path
        ):

            return jsonify({

                "success": False,

                "message":
                "OfferLetter.pdf Not Found"

            }), 404

        existing_pdf = PdfReader(
            template_path
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
        # EMAIL + COLLEGE
        # ======================================

        can.setFont(
            "Times-Roman",
            14
        )

        can.drawString(
            72,
            590,
            candidate_name
        )

        can.drawString(
            72,
            570,
            email_id
        )

        can.drawString(
            72,
            550,
            college_name
        )

        # ======================================
        # START / END DATE
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

        can.drawString(
            458,
            395,
            end_date
        )

        can.save()

        packet.seek(0)

        overlay_pdf = PdfReader(
            packet
        )

        # ======================================
        # MERGE FIRST PAGE
        # ======================================

        first_page = existing_pdf.pages[0]

        first_page.merge_page(
            overlay_pdf.pages[0]
        )

        output.add_page(first_page)

        # ======================================
        # REMAINING PAGES
        # ======================================

        for page_num in range(
            1,
            len(existing_pdf.pages)
        ):

            output.add_page(
                existing_pdf.pages[page_num]
            )

        # ======================================
        # SAVE OUTPUT
        # ======================================
        pdf_buffer = io.BytesIO()

        output.write(pdf_buffer)

        pdf_buffer.seek(0)

        return send_file(

            pdf_buffer,

            as_attachment=True,

            download_name="OfferLetter.pdf",

            mimetype="application/pdf"

        )

    except Exception as e:

        print("ERROR :", str(e))

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500

# ======================================
# VERIFY CERTIFICATE
# ======================================

@app.route(
    "/verify-certificate",
    methods=["POST"]
)
def verify_certificate():

    try:

        data = request.get_json()

        ref_id = data.get(
            "ref_id",
            ""
        )

        if ref_id:

            return jsonify({

                "success": True,

                "ref_id": ref_id

            })

        return jsonify({

            "success": False

        })

    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500

# ======================================
# DOWNLOAD CERTIFICATE
# ======================================

@app.route(
    "/download-certificate",
    methods=["POST"]
)
def download_certificate():

    try:

        pdf_path = os.path.join(
            BASE_DIR,
            "Generated_Offer_Letter.pdf"
        )

        if not os.path.exists(
            pdf_path
        ):

            return jsonify({

                "success": False,

                "message":
                "Certificate Not Found"

            }), 404

        return send_file(

            pdf_path,

            as_attachment=True

        )

    except Exception as e:

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500

# ======================================
# RUN
# ======================================

if __name__ == "__main__":

    port = int(
        os.environ.get("PORT", 5000)
    )

    app.run(
        host="0.0.0.0",
        port=port
    )