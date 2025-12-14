# 🔐 PKI-Based 2FA Authentication Microservice

This project implements a secure, containerized authentication microservice demonstrating enterprise-grade security practices using Public Key Infrastructure (PKI) and Time-based One-Time Password (TOTP) two-factor authentication.

The service securely decrypts a seed using RSA 4096-bit encryption, generates and verifies 2FA codes, and runs inside a Docker container with persistent storage and an automated cron job.

---

## 🎯 Objectives

- Secure seed transmission using RSA-based PKI
- Generate and verify TOTP-based 2FA codes
- Persist sensitive data across container restarts
- Automate 2FA code generation using cron jobs
- Containerize the application using Docker

---

## 🧠 Key Concepts Demonstrated

- RSA 4096-bit encryption
- RSA/OAEP decryption (SHA-256, MGF1)
- RSA-PSS digital signatures
- TOTP (Google Authenticator style 2FA)
- Docker multi-stage builds
- Docker volumes for persistence
- Cron jobs in containers
- Secure REST API design

---

## 🛠️ Technology Stack

- Language: Python 3.11  
- Framework: FastAPI  
- Cryptography: cryptography  
- TOTP: pyotp  
- Containerization: Docker, Docker Compose  
- Scheduler: cron  
- Timezone: UTC  

---

## 📁 Project Structure

.
├── app/
│ └── main.py
├── scripts/
│ └── log_2fa_cron.py
├── cron/
│ └── 2fa-cron
├── student_private.pem
├── student_public.pem
├── instructor_public.pem
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .gitignore
├── .gitattributes
└── README.md

yaml
Copy code

---

## 🔑 Cryptography Details

- RSA Key Size: 4096 bits  
- Public Exponent: 65537  
- Encryption Padding: OAEP  
- Hash Algorithm: SHA-256  
- MGF: MGF1(SHA-256)  

### Digital Signature
- Algorithm: RSA-PSS  
- Hash: SHA-256  
- Salt Length: Maximum  

---

## 🔐 API Endpoints

### POST /decrypt-seed
Decrypts and stores the encrypted seed.

**Request**
```json
{
  "encrypted_seed": "BASE64_STRING"
}
Response

json
Copy code
{
  "status": "ok"
}
GET /generate-2fa
Generates the current TOTP code.

Response

json
Copy code
{
  "code": "123456",
  "valid_for": 30
}
POST /verify-2fa
Verifies a TOTP code.

Request

json
Copy code
{
  "code": "123456"
}
Response

json
Copy code
{
  "valid": true
}
⏱️ TOTP Configuration
Setting	Value
Algorithm	SHA-1
Digits	6
Time Period	30 seconds
Seed Format	HEX → Base32
Verification Window	±1 period

🐳 Docker & Persistence
API runs on port 8080 inside the container

Exposed on port 9090 on the host

Persistent volumes:

/data → decrypted seed storage

/cron → cron job logs

Timezone configured to UTC

⏰ Cron Job
Executes every minute

Generates current 2FA code

Logs output to /cron/last_code.txt

Log format

ruby
Copy code
YYYY-MM-DD HH:MM:SS - 2FA Code: XXXXXX
🚀 Running the Application
bash
Copy code
docker-compose build
docker-compose up -d
Access the API:

arduino
Copy code
http://localhost:9090
🧪 Testing Flow
Call /decrypt-seed once

Call /generate-2fa to get the TOTP code

Call /verify-2fa with the generated code

Wait 70+ seconds and check cron output:

bash
Copy code
docker exec pki-2fa-service cat /cron/last_code.txt
🔒 Security Notes
student_private.pem is intentionally committed only for this assignment

Keys must not be reused in production

encrypted_seed.txt is never committed

All cryptographic parameters strictly follow the specification

📦 Submission Artifacts
GitHub Repository URL

Commit Hash

Encrypted Commit Signature

Student Public Key

Encrypted Seed

✅ Outcome
A fully functional, production-style PKI and TOTP-based authentication microservice with Docker, persistence, and automated cron execution.

👨‍💻 Author
Sameal Raju Varada
