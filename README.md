# QR Code-Based Student Verification System

This project implements a secure and efficient student verification system using QR codes, facial recognition, and AES encryption. It was developed as part of the CSO332 course to demonstrate advanced authentication techniques and secure data handling.

## Overview

The system allows students to authenticate themselves by scanning a personalized QR code. Upon scanning, the system retrieves the student's encrypted data from an SQL database, decrypts it, and verifies the student's identity using facial recognition. This multi-layered approach ensures both security and accuracy in the verification process.

## Key Features

- **QR Code Authentication**: Each student is assigned a unique QR code containing a token for identification.
- **AES Encryption**: Sensitive student data, including personal information and facial embeddings, are securely stored in an SQL database using AES encryption.
- **OTP Verification**: The scanner can verify further details by sending an OTP to the student's contact number.
- **Facial Recognition**: The system captures the student's live facial features and compares them with stored embeddings to verify identity.
- **Cosine Similarity Matching**: Utilizes cosine similarity to measure the closeness between live and stored facial embeddings for accurate verification.

## Technologies Used

- **Python**: Programming language for backend logic.
- **OpenCV**: Library for real-time computer vision tasks, including facial recognition.
- **SQLite**: Lightweight SQL database for storing student data.
- **AES-GCM Encryption**: Advanced encryption standard (Galois Counter Mode) for securing sensitive data.
- **Streamlit**: Python module to build simple web apps.
- **Twilio API**: A popular API used to incorporate OTP and SMS services. 

## Instructions:

### Making Entries and generating QR Codes:
Run the `encrypted_qr_generator.ipynb` notebook, make sure to replace the data in the "students" list with your own data. The QRs will be generated for each student.

### Registering facial ID:
Run the `face_recog.ipynb` notebook, replace the folder paths with folders containing images of the student. And now your SQL db must have 3 face embeddings for each student

### Testing:
Run the `app.py` script, replace account_sid, auth_token and verify_sid with your Twilio API credentials.
