import streamlit as st
import pandas as pd
import uuid
from datetime import datetime
import altair as alt

# ---------------- CONFIG ----------------
st.set_page_config(page_title="CTEA Concern Box", page_icon="📢", layout="wide")
DATA_FILE = "complaints.csv"

# ---------------- HELPERS ----------------
def load_data():
    try:
        return pd.read_csv(DATA_FILE)
    except:
        return pd.DataFrame(columns=["ID","Name","Batch","Category","Severity","Description","Date","Status"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

def create_ticket():
    return str(uuid.uuid4())[:8].upper()  # short unique ticket

# ---------------- UI ----------------
st.markdown("<h1 style='text-align:center; color:#004aad;'>📢 CTEA Concern Portal</h1>", unsafe_allow_html=True)

menu = st.sidebar.radio("Navigation", ["Submit Complaint", "Track Complaint", "Admin Dashboard"])

df = load_data()

# ---------------- SUBMIT COMPLAINT ----------------
if menu == "Submit Complaint":
    st.subheader("Submit Your Concern 🚀")
    with st.form("complaint_form"):
        name = st.text_input("👤 Your Name")
        batch = st.selectbox("🏫 Your Batch", ["Batch A", "Batch B", "Batch C"])
        category = st.selectbox("📂 Category", ["Food","Hostel","Laundry","Academic","Misc"])
        severity = st.radio("⚡ Severity", ["Minor","Medium","Major"])
        desc = st.text_area("📝 Describe your concern")
        submitted = st.form_submit_button("Submit 🚀")

        if submitted:
            if not name or not desc:
                st.warning("⚠ Please fill all fields")
            else:
                ticket = create_ticket()
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                new_row = {
                    "ID": ticket,
                    "Name": name,
                    "Batch": batch,
                    "Category": category,
                    "Severity": severity,
                    "Description": desc,
                    "Date": now,
                    "Status": "Submitted"
                }
                df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                save_data(df)

                st.success(f"✅ Complaint submitted successfully! Your Ticket ID is **{ticket}**")
                st.balloons()

# ---------------- TRACK COMPLAINT ----------------
elif menu == "Track Complaint":
    st.subheader("🔍 Track Your Complaint")
    ticket_id = st.text_input("Enter your Ticket ID")
    if ticket_id:
        record = df[df["ID"] == ticket_id]
        if not record.empty:
            rec = record.iloc[0]
            st.info(f"🎫 Ticket: {rec['ID']} | Status: **{rec['Status']}**")
            st.write(f"**Category:** {rec['Category']}")
            st.write(f"**Severity:** {rec['Severity']}")
            st.write(f"**Description:** {rec['Description']}")
        else:
            st.error("❌ Ticket not found!")

# ---------------- ADMIN DASHBOARD ----------------
elif menu == "Admin Dashboard":
    st.subheader("📊 Complaint Analytics")
    if df.empty:
        st.info("No complaints yet.")
    else:
        col1, col2 = st.columns(2)

        with col1:
            st.write("**Complaints by Category**")
            chart = alt.Chart(df).mark_arc().encode(
                theta="count()",
                color="Category",
                tooltip=["Category", "count()"]
            )
            st.altair_chart(chart, use_container_width=True)

        with col2:
            st.write("**Complaints by Severity**")
            chart = alt.Chart(df).mark_bar().encode(
                x="Severity",
                y="count()",
                color="Severity",
                tooltip=["Severity","count()"]
            )
            st.altair_chart(chart, use_container_width=True)

        st.write("**All Complaints Table**")
        st.dataframe(df)
