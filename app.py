import streamlit as st
import sqlite3
import cv2
import numpy as np
import random, time
from datetime import datetime
from pyzbar.pyzbar import decode
from insightface.app import FaceAnalysis
import base64, secrets
import os
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from twilio.rest import Client

# Replace with key loaded from secure location
KEY = b'\x16\xb3z\xfc>\xfa2\xf5\xe1T\xc3/!\x95\xcbq\x07\xde\xd3;\xad\x9bJ\xe3^\x04\x0ca\xd5\x86f\x83'
account_sid = "my_sid"
auth_token = "my_auth_token"
verify_sid = "my_verify_sid"


# Twilio OTP functions
def send_otp(phone_number, client):
    verification = client.verify.v2.services(verify_sid).verifications.create(
        to=phone_number,
        channel="sms"
    )
    return verification.status

def verify_otp(phone_number, code, client):
    verification_check = client.verify.v2.services(verify_sid).verification_checks.create(
        to=phone_number,
        code=code
    )
    return verification_check.status == "approved"

# db setup
def get_conn():
    conn = sqlite3.connect('students.db', check_same_thread=False)
    return conn

# entry logger
def log_entry(qr_token, roll_no, name):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO logs (qr_token, roll_no, name, timestamp) VALUES (?, ?, ?, ?)",
                   (qr_token, roll_no, name, datetime.now().isoformat(sep=' ', timespec='seconds')))
    conn.commit()
    conn.close()

def decrypt_blob(blob_b64u: str) -> str:
    # restore padding if stripped
    blob_b64u += "=" * ((4 - len(blob_b64u) % 4) % 4)
    raw = base64.urlsafe_b64decode(blob_b64u)
    iv, ct = raw[:12], raw[12:]
    aesgcm = AESGCM(KEY)
    qr_token = aesgcm.decrypt(iv, ct, b"college-qr-v1").decode()
    return qr_token

# fetch student details
def get_student(qr_token):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT roll_no, name, contact_no, aadhar_no FROM students WHERE qr_token = ?", (qr_token,))
    student = cursor.fetchone()
    conn.close()
    return student

def cosine_sim(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

# ------------------------------------------------
# Streamlit App
# ------------------------------------------------
st.title("College Entry Verification System")

if "step" not in st.session_state:
    st.session_state.step = 0
if "qr_token" not in st.session_state:
    st.session_state.qr_token = None
if "otp" not in st.session_state:
    st.session_state.otp = None

# Step 0: Start button
if st.session_state.step == 0:
    if st.button("Start Scanning"):
        st.session_state.step = 1
        st.rerun()

# Step 1: QR Scan
elif st.session_state.step == 1:
    st.header("Step 1: QR Scan")
    if st.button("Scan QR"):
        try:
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                raise Exception("Could not open camera")
            
            print("Hold the QR code in front of the camera...")
            print("Press 'q' to quit")

            student = None
            found = False

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                for barcode in decode(frame):
                    try:
                        blob = barcode.data.decode("utf-8")
                        qr_token = decrypt_blob(blob)
                        student = get_student(qr_token)
                        found = True
                        break
                    except:
                        found = True
                        break

                if found:
                    break

                try:
                    cv2.imshow("QR Scanner", frame)
                    key = cv2.waitKey(1) & 0xFF
                    if key == ord('q'):
                        break
                except:
                    pass

        finally:
            cap.release()
            try:
                cv2.destroyAllWindows()
            except:
                pass

            if student:
                st.session_state.qr_token = qr_token
                st.success(f"Found: Roll {student[0]}, Name {student[1]}")
                time.sleep(1)
                st.session_state.step = 2
                st.rerun()
            elif not found:
                st.warning("No QR detected!")
                print("No QR detected.")
            else:
                st.warning("Student not found in database!")
                print("Student not found in database.")


# Step 2: Basic Info
elif st.session_state.step == 2:
    st.header("Step 2: Student Info")
    student = get_student(st.session_state.qr_token)
    if student:
        st.write(f"**Roll:** {student[0]}")
        st.write(f"**Name:** {student[1]}")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Confirm Entry"):
            if student:
                log_entry(st.session_state.qr_token, student[0], student[1])
                st.success("Entry confirmed & logged.")
                time.sleep(1.5)
            else:
                st.error("Student not found. Cannot log entry.")
            st.session_state.step = 1
            st.session_state.qr_token = None
            st.session_state.otp = None
            st.success("Ready for next scan.")
            time.sleep(1.5)
            st.rerun()
    with col2:
        if st.button("Check Further (OTP)"):
            if student:
                twilio_client = Client(account_sid, auth_token)
                contact_number = student[2]  # phone number at index 3
                status = send_otp(contact_number, twilio_client)
                if status == "pending":
                    st.success(f"OTP sent to {contact_number}")
                    st.session_state.step = 3
                    st.session_state.contact_number = contact_number
                    st.rerun()
                else:
                    st.error("Failed to send OTP.")


# Step 3: OTP
elif st.session_state.step == 3:
    st.header("Step 3: OTP Verification")
    student = get_student(st.session_state.qr_token)
    entered = st.text_input("Enter OTP", type="password")
    
    if st.button("Verify OTP"):
        twilio_client = Client(account_sid, auth_token)
        if verify_otp(st.session_state.contact_number, entered, twilio_client):
            st.session_state.otp_verified = True
            st.rerun()
        else:
            st.error("Invalid OTP")
    
    # Show options only after OTP is verified
    if st.session_state.get("otp_verified", False):
        st.success(f"OTP verified! Aadhar: {student[3]}, Phone: {student[2] } \n Name: {student[1]}, Roll: {student[0]}")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm Entry"):
                if student:
                    log_entry(st.session_state.qr_token, student[0], student[1])
                    st.success("Ready for next scan.")
                    time.sleep(1.5)
                else:
                    st.error("Student not found. Cannot log entry.")
                st.session_state.step = 1
                st.session_state.qr_token = None
                st.session_state.otp = None
                st.session_state.otp_verified = False
                time.sleep(1)
                st.rerun()
        with col2:
            if st.button("Check Further (Face Match)"):
                st.session_state.otp_verified = False
                st.session_state.step = 4
                st.rerun()

# Step 4: Face Verification
elif st.session_state.step == 4:
    st.header("Step 4: Face Verification")
    
    # Initialize face_app if not already done
    if "face_app" not in st.session_state:
        st.session_state.face_app = FaceAnalysis(
            name="auraface",
            providers=["CPUExecutionProvider"],
            root=".",
        )
        st.session_state.face_app.prepare(ctx_id=0)
    
    if st.button("Capture Face"):
        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()
        cap.release()
        if ret:
            img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            faces = st.session_state.face_app.get(img_rgb)
            if faces:
                live_emb = faces[0].normed_embedding
                conn = get_conn()
                cur = conn.cursor()
                cur.execute("SELECT embedding1, embedding2, embedding3 FROM students WHERE qr_token=?", (st.session_state.qr_token,))
                row = cur.fetchone()
                conn.close()
                if row and any(row):
                    sims = []
                    for emb_blob in row:
                        if emb_blob:
                            stored_emb = np.frombuffer(emb_blob, dtype=np.float32)
                            sim = cosine_sim(live_emb, stored_emb)
                            sims.append(sim)
                    if sims:
                        avg_sim = sum(sims) / len(sims)
                        st.session_state.face_match_score = avg_sim
                        st.session_state.face_captured = True
                        st.rerun()
                else:
                    st.error("No face embedding found in database.")
            else:
                st.error("No face detected in image.")
        else:
            st.error("Failed to capture image.")
    
    # Show match results and options only after face is captured
    if st.session_state.get("face_captured", False):
        sim = st.session_state.face_match_score
        st.write(f"Match Score: {sim:.3f}")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Confirm Entry"):
                student = get_student(st.session_state.qr_token)
                if student:
                    log_entry(st.session_state.qr_token, student[0], student[1])
                    st.success("Entry confirmed & logged.")
                    time.sleep(1)
                else:
                    st.error("Student not found. Cannot log entry.")
                st.session_state.clear()
                time.sleep(1)
                st.rerun()
        with col2:
            if st.button("Deny Entry"):
                st.error("Entry denied.")
                st.session_state.clear()
                time.sleep(1)
                st.rerun()