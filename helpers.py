import streamlit as st
import uuid
from datetime import datetime

def inject_custom_css():
    """Injects custom CSS to style the Streamlit app as a premium medical dashboard."""
    css = """
    <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        /* Base typography and font family */
        html, body, [class*="css"], .stMarkdown {
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        }
        
        /* Premium Card style */
        .medical-card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 24px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
            border-left: 5px solid #0f766e;
            margin-bottom: 20px;
        }
        
        .medical-card-neutral {
            background-color: #f8fafc;
            border-radius: 12px;
            padding: 20px;
            border: 1px solid #e2e8f0;
            margin-bottom: 16px;
        }
        
        /* Metric styling */
        .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            color: #0f766e;
            line-height: 1.2;
        }
        
        .metric-label {
            font-size: 0.85rem;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        }
        
        /* Risk Badges */
        .badge {
            display: inline-block;
            padding: 6px 14px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85rem;
            text-align: center;
        }
        .badge-low {
            background-color: #d1fae5;
            color: #065f46;
            border: 1px solid #a7f3d0;
        }
        .badge-moderate {
            background-color: #fef3c7;
            color: #92400e;
            border: 1px solid #fde68a;
        }
        .badge-high {
            background-color: #fee2e2;
            color: #991b1b;
            border: 1px solid #fecaca;
        }
        
        /* ParkiSense Title */
        .title-container {
            padding: 20px 0;
            text-align: left;
            border-bottom: 1px solid #e2e8f0;
            margin-bottom: 24px;
        }
        .app-title {
            color: #0f172a;
            font-size: 2.5rem;
            font-weight: 800;
            margin-bottom: 0px;
            letter-spacing: -0.02em;
        }
        .app-subtitle {
            color: #0f766e;
            font-size: 1rem;
            font-weight: 500;
            margin-top: 4px;
            letter-spacing: 0.05em;
            text-transform: uppercase;
        }
        
        /* Medical Disclaimer box styling */
        .disclaimer-box {
            background-color: #fafafa;
            border: 1px solid #e5e5e5;
            border-radius: 8px;
            padding: 16px;
            font-size: 0.8rem;
            color: #666666;
            line-height: 1.4;
            margin-top: 24px;
            margin-bottom: 16px;
        }
        
        /* Button overrides */
        div.stButton > button:first-child {
            background-color: #0f766e;
            color: white;
            border-radius: 8px;
            border: none;
            padding: 8px 24px;
            font-weight: 500;
            transition: all 0.2s ease-in-out;
        }
        div.stButton > button:first-child:hover {
            background-color: #0d9488;
            box-shadow: 0 4px 12px rgba(13, 148, 136, 0.2);
        }
        
        /* Sidebar styling additions */
        .sidebar-header {
            font-weight: 700;
            color: #0f766e;
            font-size: 1.2rem;
            margin-bottom: 20px;
        }
        
        /* Progress tracker */
        .progress-bar-container {
            width: 100%;
            background-color: #e2e8f0;
            border-radius: 10px;
            height: 8px;
            margin: 15px 0;
            overflow: hidden;
        }
        .progress-bar-fill {
            background-color: #0f766e;
            height: 100%;
            border-radius: 10px;
            transition: width 0.3s ease;
        }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

def init_session_state():
    """Initializes all stream-state variables for routing and data management."""
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "Home"
        
    if "patient_id" not in st.session_state:
        st.session_state["patient_id"] = str(uuid.uuid4())[:8].upper()
        
    if "patient_profile" not in st.session_state:
        st.session_state["patient_profile"] = {
            "patient_id": st.session_state["patient_id"],
            "name": "",
            "age": 60,
            "gender": "Male",
            "location": "",
            "medical_history": "",
            "medications": "",
            "family_history": "No History",
            "neurological_conditions": "None",
            "previous_screening": "No previous screening"
        }
        
    if "symptoms" not in st.session_state:
        st.session_state["symptoms"] = {}
        
    if "voice" not in st.session_state:
        st.session_state["voice"] = {
            "uploaded": False,
            "recorded": False,
            "file_name": "",
            "stability": 80.0,
            "pitch_var": 1.2,
            "jitter": 0.015,
            "shimmer": 0.035,
            "hnr": 22.5,
            "energy_var": 0.45,
            "risk_score": 30.0,
            "features_extracted": False
        }
        
    if "writing" not in st.session_state:
        st.session_state["writing"] = {
            "drawn": False,
            "uploaded": False,
            "file_name": "",
            "tremor_index": 20.0,
            "smoothness": 85.0,
            "speed_index": 70.0,
            "pressure_proxy": 50.0,
            "size_consistency": 80.0,
            "risk_score": 25.0,
            "features_extracted": False
        }
        
    if "gait" not in st.session_state:
        st.session_state["gait"] = {
            "uploaded": False,
            "step_regularity": 88.0,
            "symmetry": 90.0,
            "cadence": 105.0,
            "stride_consistency": 92.0,
            "arm_swing": 85.0,
            "postural_sway": 15.0,
            "risk_score": 20.0,
            "features_extracted": False
        }
        
    if "demo_mode" not in st.session_state:
        st.session_state["demo_mode"] = False
        
    if "screening_completed" not in st.session_state:
        st.session_state["screening_completed"] = False
        
    if "calculated_results" not in st.session_state:
        st.session_state["calculated_results"] = None

def load_demo_data(risk_level="High"):
    """Loads realistic patient data corresponding to low/moderate/high risk for Demo Mode."""
    st.session_state["demo_mode"] = True
    
    if risk_level == "High":
        st.session_state["patient_profile"] = {
            "patient_id": "DEMO-HIGH-98",
            "name": "Amit Sharma (Demo Patient - High Risk)",
            "age": 68,
            "gender": "Male",
            "location": "New Delhi, India",
            "medical_history": "Mild hypertension, complains of slow handwriting and soft voice.",
            "medications": "Amlodipine 5mg daily",
            "family_history": "Paternal grandfather diagnosed with Parkinson's",
            "neurological_conditions": "None diagnosed",
            "previous_screening": "No previous screening"
        }
        
        # High symptoms questionnaire answers
        st.session_state["symptoms"] = {
            "tremor": "Often",
            "slowness": "Severe",
            "stiffness": "Often",
            "balance": "Often",
            "walking": "Often",
            "arm_swing": "Often",
            "fine_motor": "Severe",
            "sleep": "Often",
            "fatigue": "Often",
            "constipation": "Often",
            "smell": "Severe",
            "mood": "Sometimes",
            "speech": "Often"
        }
        
        st.session_state["voice"] = {
            "uploaded": True,
            "recorded": False,
            "file_name": "demo_voice_high.wav",
            "stability": 42.5,
            "pitch_var": 3.8,
            "jitter": 0.045,
            "shimmer": 0.098,
            "hnr": 12.4,
            "energy_var": 1.25,
            "risk_score": 82.0,
            "features_extracted": True
        }
        
        st.session_state["writing"] = {
            "drawn": True,
            "uploaded": False,
            "file_name": "spiral_demo_high.png",
            "tremor_index": 78.4,
            "smoothness": 32.1,
            "speed_index": 28.5,
            "pressure_proxy": 35.0,
            "size_consistency": 41.2,
            "risk_score": 76.0,
            "features_extracted": True
        }
        
        st.session_state["gait"] = {
            "uploaded": True,
            "step_regularity": 44.5,
            "symmetry": 52.0,
            "cadence": 82.0,
            "stride_consistency": 48.0,
            "arm_swing": 30.0,
            "postural_sway": 62.5,
            "risk_score": 78.0,
            "features_extracted": True
        }
        
    elif risk_level == "Moderate":
        st.session_state["patient_profile"] = {
            "patient_id": "DEMO-MOD-45",
            "name": "Rupa Sen (Demo Patient - Moderate Risk)",
            "age": 62,
            "gender": "Female",
            "location": "Kolkata, India",
            "medical_history": "Osteoarthritis in knee, sleep disturbances",
            "medications": "Calcium supplements, glucosamine",
            "family_history": "No History",
            "neurological_conditions": "None",
            "previous_screening": "No previous screening"
        }
        
        # Moderate symptoms
        st.session_state["symptoms"] = {
            "tremor": "Sometimes",
            "slowness": "Sometimes",
            "stiffness": "Sometimes",
            "balance": "Rarely",
            "walking": "Sometimes",
            "arm_swing": "Sometimes",
            "fine_motor": "Sometimes",
            "sleep": "Often",
            "fatigue": "Sometimes",
            "constipation": "Sometimes",
            "smell": "Sometimes",
            "mood": "Rarely",
            "speech": "Sometimes"
        }
        
        st.session_state["voice"] = {
            "uploaded": True,
            "recorded": False,
            "file_name": "demo_voice_mod.wav",
            "stability": 68.0,
            "pitch_var": 2.1,
            "jitter": 0.024,
            "shimmer": 0.052,
            "hnr": 18.2,
            "energy_var": 0.72,
            "risk_score": 55.0,
            "features_extracted": True
        }
        
        st.session_state["writing"] = {
            "drawn": True,
            "uploaded": False,
            "file_name": "spiral_demo_mod.png",
            "tremor_index": 45.0,
            "smoothness": 61.2,
            "speed_index": 55.0,
            "pressure_proxy": 48.0,
            "size_consistency": 64.0,
            "risk_score": 48.0,
            "features_extracted": True
        }
        
        st.session_state["gait"] = {
            "uploaded": True,
            "step_regularity": 68.5,
            "symmetry": 72.0,
            "cadence": 94.0,
            "stride_consistency": 70.0,
            "arm_swing": 62.0,
            "postural_sway": 34.0,
            "risk_score": 52.0,
            "features_extracted": True
        }
    
    st.session_state["screening_completed"] = False
    st.session_state["calculated_results"] = None
