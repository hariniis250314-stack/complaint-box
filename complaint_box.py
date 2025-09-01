import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
from textblob import TextBlob   # simple sentiment analysis

# ---------------- CONFIG ----------------
st.set_page_config(page_title="CTEA AI Complaint Box", page_icon="🤖", layout="wide")
DATA_FILE = "complaints_ai.csv"

# ---------------- HELPERS ----------------
def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except:
        return pd.DataFrame(columns=["ID","Name","Batch","AI_Category","Urgency","Description","Date","Status"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def create_ticket():
    return str(uuid.uuid4())[:8].upper()

def ai_classify(text):
    # Very simple keyword-based AI (replace with ML model later)
    text_lower = text.lower()
    if any(word in text_lower for word in ["hostel","room","water","wifi","electricity"]):
        category = "Hostel"
    elif any(word in text_lower for word in ["laundry","clothes","washing"]):
        category = "Laundry"
    elif any(word in text_lower for word in ["class","teacher","exam","study"]):
        category = "Academic"
    else:
        category = "Misc"

    # Sentiment analysis (using TextBlob)
    polarity = TextBlob(text).sentiment.polarity
    if polarity < -0.3 or "harass" in text_lower or "unsafe" in text_lower:
        urgency = "High"
    elif polarity < 0:
        urgency = "Medium"
    else:
        urgency = "Low"

    return category, urgency

# ---------------- UI ----------------
st.markdown("<h1 style='text-align:center; color:#004aad;'>🤖 AI-Powered Complaint & Concern Portal</h1>", unsafe_allow_html=True)

menu = st.sidebar.radio("Navigation", ["Submit Complaint", "Track Complaint", "Admin Dashboard"])
df = load_data()

# ---------------- SUBMIT ----------------
if menu == "Submit Complaint":
    st.subheader("Submit Your Concern 📝")
    with st.form("complaint_form"):
        name = st.text_input("👤 Your Name")
        batch = st.selectbox("🏫 Your Batch", ["Batch A","Batch B","Batch C"])
        desc = st.text_area("📝 Describe your concern")
        submitted = st.form_submit_button("Submit 🚀")

        if submitted:
            if not name or not desc:
                st.warning("⚠ Please fill all fields")
            else:
                ticket = create_ticket()
                category, urgency = ai_classify(desc)
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                new_row = {
                    "ID": ticket,
                    "Name": name,
                    "Batch": batch,
                    "AI_Category": category,
                    "Urgency": urgency,
                    "Description": desc,
                    "Date": now,
                    "Status": "Submitted"
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)

                st.success(f"✅ Complaint submitted! Ticket ID: **{ticket}** | Category: {category} | Urgency: {urgency}")
                st.balloons()

# ---------------- TRACK ----------------
elif menu == "Track Complaint":
    st.subheader("🔍 Track Your Complaint")
    ticket_id = st.text_input("Enter Ticket ID")
    if ticket_id:
        record = df[df["ID"] == ticket_id]
        if not record.empty:
            rec = record.iloc[0]
            st.info(f"🎫 Ticket: {rec['ID']} | Status: **{rec['Status']}** | Urgency: {rec['Urgency']}")
            st.write(f"**Category (AI-detected):** {rec['AI_Category']}")
            st.write(f"**Description:** {rec['Description']}")
        else:
            st.error("❌ Ticket not found!")

# ---------------- DASHBOARD ----------------
elif menu == "Admin Dashboard":
    st.subheader("📊 AI Complaint Dashboard")
    if df.empty:
        st.info("No complaints yet.")
    else:
        st.write("**Complaints Overview**")
        st.dataframe(df)

        # Category distribution
        st.bar_chart(df["AI_Category"].value_counts())

        # Urgency distribution
        st.bar_chart(df["Urgency"].value_counts())

