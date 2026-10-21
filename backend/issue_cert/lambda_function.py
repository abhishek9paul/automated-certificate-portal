import json
import uuid
import boto3
import hashlib
import qrcode
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, letter
from reportlab.lib.utils import ImageReader
from reportlab.lib.colors import HexColor
from datetime import datetime

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')
ses = boto3.client('ses')

# REPLACE THESE WITH YOUR ACTUAL VALUES:
BUCKET_NAME = 'tushar-certs-2026-vit'
TABLE_NAME = 'Certificates'
SENDER_EMAIL = 'aggarwaltushar9393@gmail.com'

def lambda_handler(event, context):
    try:
        body = json.loads(event.get('body', '{}')) if isinstance(event.get('body'), str) else event.get('body', {})
        name = body.get('name')
        course = body.get('course')
        email = body.get('email')

        if not all([name, course, email]):
            return {
                "statusCode": 400,
                "headers": {"Content-Type": "application/json"},
                "body": json.dumps({"error": "Missing name, course, or email"})
            }

        cert_id = str(uuid.uuid4())
        date_issued = datetime.now().strftime("%Y-%m-%d")
        
        # Placeholder verification URL (we update this once API Gateway is created)
        verify_url = f"https://p2s14v7pwa.execute-api.ap-southeast-2.amazonaws.com/verify?id={cert_id}"

        # 1. QR Code
        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data(verify_url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")
        qr_io = BytesIO()
        img.save(qr_io, format="PNG")
        qr_io.seek(0)

        # 2. Draw PDF
        pdf_io = BytesIO()
        width, height = landscape(letter)
        c = canvas.Canvas(pdf_io, pagesize=(width, height))

        # Fetch the clean image directly from S3 to Lambda's temporary storage
        s3.download_file(BUCKET_NAME, 'template.png', '/tmp/template.png')
        
        # Draw the image using the pristine file from the temp folder
        c.drawImage("/tmp/template.png", 0, 0, width=width, height=height)

        c.setFillColor(HexColor("#C19A6B"))
        c.setFont("Helvetica-Bold", 42)
        c.drawCentredString(width / 2.0, height / 2.0 + 20, name)

        c.setFillColor(HexColor("#333333"))
        c.setFont("Helvetica", 16)
        c.drawCentredString(width / 2.0, height / 2.0 - 50, "In recognition of successful completion of the course:")
        c.setFont("Helvetica-Bold", 20)
        c.drawCentredString(width / 2.0, height / 2.0 - 80, course)

        c.setFont("Helvetica", 10)
        c.setFillColor(HexColor("#777777"))
        c.drawCentredString(width / 2.0, 30, f"Issued: {date_issued}  |  Verification ID: {cert_id[:12]}")

        qr_img = ImageReader(qr_io)
        c.drawImage(qr_img, 50, 40, width=80, height=80)
        c.save()

        pdf_bytes = pdf_io.getvalue()
        pdf_hash = hashlib.sha256(pdf_bytes).hexdigest()

        # 3. Store in S3
        file_key = f"{cert_id}.pdf"
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_key,
            Body=pdf_bytes,
            ContentType='application/pdf'
        )
        s3_url = f"https://{BUCKET_NAME}.s3.amazonaws.com/{file_key}"

        # 4. Save metadata to DynamoDB
        table = dynamodb.Table(TABLE_NAME)
        table.put_item(
            Item={
                'cert_id': cert_id,
                'name': name,
                'course': course,
                'date_issued': date_issued,
                'sha256_hash': pdf_hash,
                's3_url': s3_url
            }
        )

        # 5. Send Email via SES
        ses.send_email(
            Source=SENDER_EMAIL,
            Destination={'ToAddresses': [email]},
            Message={
                'Subject': {'Data': f'Certificate of Completion: {course}'},
                'Body': {
                    'Text': {
                        'Data': f"Hello {name},\n\nYour certificate for {course} is ready!\n\nDownload Link: {s3_url}\nVerification ID: {cert_id}\nSHA-256 Hash: {pdf_hash}"
                    }
                }
            }
        )

        return {
            "statusCode": 200,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({
                "message": "Certificate issued successfully",
                "cert_id": cert_id,
                "s3_url": s3_url,
                "sha256_hash": pdf_hash
            })
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": str(e)})
        }