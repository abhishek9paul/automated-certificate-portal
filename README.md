# Author
Tushar 24BCE5552

# Serverless Certificate Generator & Verification Portal

A fully serverless, end-to-end cloud application that generates, emails, and cryptographically verifies digital certificates. Built entirely on AWS native services, this project demonstrates event-driven architecture, RESTful API design, and cloud database management.

## 🚀 Live Demo
- **Frontend:** Hosted on AWS S3 *(Note: Live AWS resources will be spun down after academic grading to prevent cloud charges.)*
- **API Endpoint:** AWS API Gateway

## 🏗️ Architecture & Tech Stack

**Frontend:** HTML5, CSS3 (Inter Font, CSS Gradients), Vanilla JavaScript (Fetch API)
**Backend / Cloud:**
- **AWS API Gateway:** REST API routing and CORS management.
- **AWS Lambda:** Serverless compute executing Python backend logic (Pillow for PDF/Image manipulation).
- **Amazon S3:** Static website hosting for the frontend and secure blob storage for generated PDF certificates.
- **Amazon DynamoDB:** NoSQL database tracking certificate metadata and SHA-256 hashes for cryptographic verification.
- **Amazon SES:** Automated transactional email delivery with attached PDFs.

## 📂 Repository Structure

    ├── frontend/               # S3 Static Website UI (HTML/CSS/JS)
    ├── backend/
    │   ├── issue_cert/         # Lambda function & base template for generation
    │   └── verify_cert/        # Lambda function for DynamoDB verification
    ├── lambda_layer/           # Python dependencies (Pillow, reportlab, qrcode)
    └── README.md               # Project documentation

## ⚙️ How It Works

### 1. Generation Pipeline
1. User submits their details via the S3-hosted web interface.
2. The frontend sends a `POST` request to API Gateway, triggering the `IssueCertificate` Lambda function.
3. Lambda generates a custom certificate using Python's Pillow library, embeds a unique QR code, and calculates a SHA-256 hash.
4. The PDF is saved to an S3 bucket, metadata is written to DynamoDB, and the certificate is emailed to the user via SES.

### 2. Verification Pipeline
1. Anyone can scan the QR code on the certificate or paste the Certificate ID into the web portal.
2. The frontend sends a `GET` request to API Gateway.
3. Lambda queries the DynamoDB table using the ID.
4. If a match is found, the system returns the original timestamp, recipient details, and secure hash to prove authenticity.

## 🛠️ Setup & Deployment

**1. AWS IAM Roles**
- Configured a custom IAM Execution Role for Lambda, granting it `s3:PutObject`, `s3:GetObject`, `dynamodb:PutItem`, `dynamodb:GetItem`, and `ses:SendEmail` permissions to securely interact with the other AWS services.

**2. Amazon S3 Configuration**
- **Frontend Bucket:** Enabled Static Website Hosting and applied a public-read bucket policy to allow global access to the web interface.
- **Storage Bucket:** Configured as a private bucket strictly for storing the generated PDF certificates.

**3. API Gateway Integration**
- Created a REST API utilizing Lambda Proxy Integration.
- Configured CORS (Cross-Origin Resource Sharing) with wildcard origins to allow secure fetch requests directly from the browser.

**4. Amazon DynamoDB**
- Provisioned a NoSQL table named `Certificates` using `cert_id` as the primary Partition Key (String) to guarantee rapid lookup speeds during the verification phase.

**5. Lambda Layers & Dependencies**
- Packaged heavy third-party Python libraries (`Pillow`, `reportlab`, `qrcode`) into a `.zip` file and deployed them as a Lambda Layer. This kept the core function code lightweight and editable within the AWS Console.

**6. Amazon SES**
- Verified the sender identity in the Simple Email Service console to authorize automated outbound email delivery.