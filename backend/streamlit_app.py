import streamlit as st
import os
import tempfile
import pandas as pd
import plotly.graph_objects as go
from app import MedicalReportProcessor, rag_system, db
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(
    page_title="Medical Report Simplifier",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for aesthetics
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stButton>button {
        width: 100%;
        border-radius: 10px;
        height: 3em;
        background-color: #007bff;
        color: white;
    }
    .report-card {
        background-color: white;
        padding: 20px;
        border-radius: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        border-left: 5px solid #007bff;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    </style>
""", unsafe_allow_html=True)

# Initialize Processor
@st.cache_resource
def get_processor():
    return MedicalReportProcessor()

processor = get_processor()

# Sidebar
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3004/3004458.png", width=100)
    st.title("MediSimple")
    st.markdown("### Simplifier for Rural Patients")
    st.info("Upload your medical lab report to get a simple, easy-to-understand explanation in your local language context.")
    
    st.markdown("---")
    st.markdown("### Features")
    st.markdown("✅ OCR Text Extraction")
    st.markdown("✅ Lab Value Parsing")
    st.markdown("✅ AI-Powered Explanation")
    st.markdown("✅ RAG Medical Knowledge")

dashboard_tab, history_tab = st.tabs(["📄 New Report", "🕒 History"])

with dashboard_tab:
    st.title("🏥 Medical Report Analyzer")
    st.markdown("Upload your medical report (Image or PDF) below.")

    uploaded_file = st.file_uploader("Choose a file", type=['png', 'jpg', 'jpeg', 'pdf'])

    if uploaded_file is not None:
        try:
            # Save temp file
            suffix = os.path.splitext(uploaded_file.name)[1]
            with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                tmp_path = tmp_file.name

            col1, col2 = st.columns([1, 1])

            with col1:
                st.subheader("Preview")
                if suffix.lower() in ['.png', '.jpg', '.jpeg']:
                    st.image(uploaded_file, caption='Uploaded Report', use_column_width=True)
                else:
                    st.info("PDF Preview not supported yet, but processing will work.")

            with st.spinner('Analyzing report... This may take a moment.'):
                # Process File
                if suffix.lower() == '.pdf':
                    extracted_text = processor.extract_text_from_pdf(tmp_path)
                else:
                    extracted_text = processor.extract_text_from_image(tmp_path)

                # Cleanup
                os.unlink(tmp_path)
                
                # Parse Values
                lab_values = processor.parse_lab_values(extracted_text)
                
                # Generate Explanation
                explanation = processor.generate_explanation_with_rag(lab_values, extracted_text)

            # --- Results Display ---
            st.success("Analysis Complete!")

            # 1. Summary Section and Risk Level
            st.markdown(f"""
            <div class="report-card">
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <h2>📋 Summary</h2>
                </div>
                <p style="font-size: 1.1em;">{explanation.get('summary', 'No summary available.')}</p>
            </div>
            """, unsafe_allow_html=True)

            # Risk Level Indicator
            risk_level = explanation.get('risk_level', 'Unknown')
            risk_color = "#28a745"  # Green
            if risk_level == "Medium":
                risk_color = "#ffc107"  # Orange/Yellow
            elif risk_level == "High":
                risk_color = "#dc3545"  # Red
            
            st.markdown(f"""
            <div style="background-color: {risk_color}; padding: 20px; border-radius: 10px; color: white; text-align: center; margin-bottom: 20px;">
                <h2 style="margin:0;">Risk Level: {risk_level}</h2>
            </div>
            """, unsafe_allow_html=True)

            # 2. Lab Values & Visuals
            st.subheader("🔬 Lab Values Detected")
            
            if lab_values:
                # Create metrics grid
                cols = st.columns(3)
                for idx, (test, value) in enumerate(lab_values.items()):
                    with cols[idx % 3]:
                        st.markdown(f"""
                        <div class="metric-card">
                            <strong>{test.replace('_', ' ').title()}</strong>
                            <h3 style="margin:0; color: #007bff;">{value}</h3>
                        </div>
                        <br>
                        """, unsafe_allow_html=True)
            else:
                st.warning("No specific lab values detected automatically.")

            # 3. Detailed Explanations
            with st.expander("🩺 Detailed Test Explanations", expanded=True):
                for test, text in explanation.get('test_explanations', {}).items():
                    st.markdown(f"**{test.replace('_', ' ').title()}**: {text}")

            # 4. Lifestyle Tips
            st.markdown("""
            <div class="report-card" style="border-left: 5px solid #28a745;">
                <h3>🌱 Lifestyle Recommendations</h3>
                <ul>
            """, unsafe_allow_html=True)
            for tip in explanation.get('lifestyle_tips', []):
                st.markdown(f"- {tip}")
            st.markdown("</ul></div>", unsafe_allow_html=True)

            # 5. Doctor Advice
            st.info(f"**Doctor's Note**: {explanation.get('when_to_see_doctor', 'Consult a doctor.')}")

            # 6. Raw Data (Expandable)
            with st.expander("🔍 View Raw Extracted Text"):
                st.text(extracted_text)

        except Exception as e:
            st.error(f"An error occurred: {str(e)}")

with history_tab:
    st.header("Previous Reports")
    if db:
        reports = db.get_recent_reports()
        if reports:
            for report in reports:
                with st.expander(f"Report: {report.get('filename', 'Unknown')} - {report.get('created_at', 'Date N/A')}"):
                    st.write(report.get('summary_json', {}))
        else:
            st.info("No history found in database.")
    else:
        st.error("Database connection not available.")

