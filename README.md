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

## Repository Setup:

### Step 1: Clone the Repository
```bash
git clone https://github.com/dhairya-1105/qr_code_cso332
cd qr_code_cso332
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Generate Encrypted QR Codes
Open and run the notebook `encrypted_qr_generator.ipynb`. Inside the notebook, update the students list with your own student entries (e.g., name, roll number, contact details, etc.). After execution, encrypted QR codes will be generated inside a new directory called `qrcodes`. Make sure to save the KEY generated in this notebook, as it'll be used later.

### Step 4: Prepare Sample Images
Create a new directory named `sample_images`. Inside it, create subdirectories using the naming format `name_imgs` where name corresponds to the student's name. Place 3 face images for each student inside their respective folder.

### Step 5: Generate Face Embeddings
Run the notebook `face_recog.ipynb`. Make sure to replace the roll numbers in the last cell with your own roll numbers stored in the db, as well as change the student names in the directories passed to the update_student_embeddings function. This will generate and store face embeddings for each student inside the students.db SQLite database in blob format.

### Step 6: Update Keys in the app
Open `app.py` and replace the placeholder AES key named as KEY with your own key generated during the execution of `encrypted_qr_generator.ipynb`. Next, replace the Twilio SMS API credentials with your own:
```python
account_sid = "my_sid"
auth_token = "my_auth_token"
verify_sid = "my_verify_sid"
```

### Step 7: Launching the Application
Execute the following command in bash:
```bash
streamlit run app.py
```
The application will open in your browser. You can now test the complete workflow and check the logs table in students.db afterwards to ensure entries are being made.

**NOTE:** Using the OTP service requires an active internet connection.
