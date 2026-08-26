import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import os
from datetime import datetime

# Set page configuration first
st.set_page_config(
    page_title="ParkiSense - Parkinson's Screening Platform",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Imports from custom modules
from utils.helpers import inject_custom_css, init_session_state, load_demo_data
from utils.database import init_db, get_screening_history, get_all_patients
from modules.patient import render_patient_profile
from modules.symptoms import render_symptoms_questionnaire, get_normalized_symptom_score
from modules.voice import render_voice_page
from modules.writing import render_writing_page
from modules.gait import render_gait_page
from modules.risk_engine import render_risk_engine_page, calculate_overall_risk
from modules.explainability import render_explainability_section
from modules.report import generate_report_html

# Initialize DB on load
init_db()

# Initialize session state variables
init_session_state()

# Inject styling
inject_custom_css()

# Sidebar Layout & Demo Mode Control Panel
st.sidebar.markdown("""
<div class="sidebar-header">
    🧬 ParkiSense
</div>
<p style="font-size: 0.85rem; color: #64748b; margin-top: -15px; margin-bottom: 20px;">
    Multimodal Early Parkinson's Screening Platform
</p>
""", unsafe_allow_html=True)

# Demo Mode Section (Sticky at the top)
st.sidebar.markdown("<h5 style='color: #0f766e;'>Demo Control Panel</h5>", unsafe_allow_html=True)
demo_col1, demo_col2 = st.sidebar.columns(2)
with demo_col1:
    if st.button("🔴 Demo High Risk", key="btn_demo_high", help="Instant load of high risk patient simulation"):
        load_demo_data("High")
        # Run calculation immediately for demo
        results = calculate_overall_risk()
        st.session_state["calculated_results"] = results
        st.session_state["screening_completed"] = True
        st.session_state["current_page"] = "Results"
        st.success("Loaded High Risk Demo Profile")
        st.rerun()
with demo_col2:
    if st.button("🟡 Demo Mod Risk", key="btn_demo_mod", help="Instant load of moderate risk patient simulation"):
        load_demo_data("Moderate")
        results = calculate_overall_risk()
        st.session_state["calculated_results"] = results
        st.session_state["screening_completed"] = True
        st.session_state["current_page"] = "Results"
        st.success("Loaded Moderate Risk Profile")
        st.rerun()

if st.session_state["demo_mode"]:
    st.sidebar.markdown("""
        <div style="background-color: #fee2e2; border: 1px solid #ef4444; color: #991b1b; padding: 8px 12px; border-radius: 6px; font-size: 0.8rem; font-weight: 600; margin-bottom: 15px; text-align: center;">
            ⚠️ DEMO MODE ACTIVE (Synthetic Data)
        </div>
    """, unsafe_allow_html=True)
    if st.sidebar.button("Clear Demo Data", key="btn_reset"):
        st.session_state.clear()
        init_session_state()
        st.success("Demo data reset successfully.")
        st.rerun()

st.sidebar.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)

# Check Completion Statuses for Navigation Display
p_filled = bool(st.session_state["patient_profile"]["name"])
sym_filled = bool(st.session_state["symptoms"])
v_filled = st.session_state["voice"]["features_extracted"]
w_filled = st.session_state["writing"]["features_extracted"]
g_filled = st.session_state["gait"]["features_extracted"]

# Sidebar Navigation Options
pages = [
    "Home",
    "Patient Profile",
    "Symptoms",
    "Voice Test",
    "Writing Test",
    "Gait Test",
    "Risk Analysis",
    "Results",
    "History"
]

# Style navigation links with indicators
st.sidebar.markdown("<h5 style='color: #0f766e;'>Platform Modules</h5>", unsafe_allow_html=True)
for page_name in pages:
    indicator = ""
    if page_name == "Patient Profile" and p_filled:
        indicator = "✅"
    elif page_name == "Symptoms" and sym_filled:
        indicator = "✅"
    elif page_name == "Voice Test" and v_filled:
        indicator = "✅"
    elif page_name == "Writing Test" and w_filled:
        indicator = "✅"
    elif page_name == "Gait Test" and g_filled:
        indicator = "✅"
    elif page_name == "Results" and st.session_state["screening_completed"]:
        indicator = "📊"
        
    btn_label = f"{page_name} {indicator}"
    
    # Active tab styling
    is_active = st.session_state["current_page"] == page_name
    button_type = "primary" if is_active else "secondary"
    
    if st.sidebar.button(btn_label, key=f"nav_{page_name}", use_container_width=True, type=button_type):
        st.session_state["current_page"] = page_name
        st.rerun()

st.sidebar.markdown("<hr style='margin: 15px 0;'>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div style="font-size: 0.75rem; color: #94a3b8; text-align: center;">
    <strong>ParkiSense v1.0.0</strong><br>
    sih-hackathon-prototype<br>
    Privacy-first Local Processing
</div>
""", unsafe_allow_html=True)

# ----------------- PAGE ROUTING -----------------

def render_home_page():
    col1, col2 = st.columns([1.2, 0.8])
    with col1:
        st.markdown("""
        <div class="title-container" style="border-bottom: none; margin-bottom: 5px;">
            <h1 class="app-title" style="font-size: 3.5rem;">ParkiSense</h1>
            <div class="app-subtitle" style="font-size: 1.2rem; letter-spacing: 0.1em;">
                Parkinson’s Disease Risk Stratification & Explainable Screening
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <p style="font-size: 1.1rem; color: #475569; margin-top: 15px; line-height: 1.6;">
            ParkiSense is a multi-modal, privacy-first screening platform designed for early identification of 
            Parkinsonian biomarkers. By consolidating subjective symptom assessments, vocal acoustic analyses, 
            fine-motor writing metrics, and computer vision-assisted gait kinematics, the platform generates 
            an audited, explainable risk score to guide clinical decisions.
        </p>
        """, unsafe_allow_html=True)
        
        st.markdown("### Key Technical Differentiators")
        
        # Grid of features
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("""
            <div class="medical-card-neutral">
                <strong>🎙️ Acoustic Voice Profiling</strong><br>
                Extracts cycle-to-cycle frequency variations (jitter, shimmer, and vocal stability) from sustained vowel sounds, detecting hypokinetic dysarthria indications.
            </div>
            <div class="medical-card-neutral">
                <strong>✍️ Fine Motor Spiral Drawing</strong><br>
                Computes spatial deviation from idealized Archimedean spiral coordinates to detect sub-visual tremor frequencies and handwriting micrographia.
            </div>
            """, unsafe_allow_html=True)
        with c2:
            st.markdown("""
            <div class="medical-card-neutral">
                <strong>🚶 Stride Cycle Kinematics</strong><br>
                Evaluates joint angles, spatiotemporal cadence rhythm, and step symmetry ratios using browser walking videos or manual checklists.
            </div>
            <div class="medical-card-neutral">
                <strong>📊 Explainable AI (XAI)</strong><br>
                Decoupled scoring mechanics with horizontal point contribution analysis and multi-dimensional radar plots, making risk factors transparent.
            </div>
            """, unsafe_allow_html=True)
            
        if st.button("Start Screening Protocol", type="primary"):
            st.session_state["current_page"] = "Patient Profile"
            st.rerun()
            
    with col2:
        # Visual branding mock / image or illustration using custom HTML styling
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0f766e 0%, #0d9488 100%); padding: 40px; border-radius: 16px; color: white; box-shadow: 0 10px 30px rgba(13,148,136,0.3); margin-top: 40px; text-align: center;">
            <div style="font-size: 4rem; margin-bottom: 20px;">🧬</div>
            <h3 style="margin-top: 0; color: white; font-weight: 700; font-size: 1.5rem;">Clinical Audit Registry</h3>
            <p style="font-size: 0.9rem; opacity: 0.9; line-height: 1.5;">
                ParkiSense compiles local database records enabling longitudinal disease trend monitoring. Screenings can be exported as printable PDF diagnostic reports.
            </p>
            <div style="background: rgba(255,255,255,0.1); border-radius: 8px; padding: 15px; margin-top: 25px; text-align: left; font-size: 0.8rem;">
                <strong>Local Database Status:</strong> Active<br>
                <strong>Security:</strong> AES/Local SQLite<br>
                <strong>Network Transmission:</strong> None (Off-line Safe)
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("""
    <div class="disclaimer-box">
        <strong>IMPORTANT MEDICAL SAFETY DISCLAIMER:</strong> ParkiSense is a preliminary AI-assisted screening and 
        risk-stratification prototype designed for clinical validation studies. It is <strong>NOT a replacement for a 
        neurological diagnosis</strong>. All scores are statistical correlation indicators of motor and non-motor 
        abnormalities and must be verified by a qualified physician or clinical neurologist.
    </div>
    """, unsafe_allow_html=True)

def render_results_dashboard():
    st.markdown('<div class="title-container"><h1 class="app-title">Screening Results</h1><div class="app-subtitle">Multi-Modal Risk Stratification Dashboard</div></div>', unsafe_allow_html=True)
    
    # Check if calculation is completed
    if not st.session_state["screening_completed"]:
        st.warning("Please complete the symptom assessment and at least one motor screening module before viewing results.")
        if st.button("Complete intake now"):
            st.session_state["current_page"] = "Patient Profile"
            st.rerun()
        return
        
    res = st.session_state["calculated_results"]
    p = st.session_state["patient_profile"]
    
    # Large score block and gauge
    col_score, col_gauge = st.columns([1, 1])
    
    # Determine badge color and risk classification
    cat = res["risk_category"]
    badge_style = "badge-low" if cat == "Low Risk" else "badge-moderate" if cat == "Moderate Risk" else "badge-high"
    
    with col_score:
        st.markdown(f"""
        <div class="medical-card" style="border-left-width: 8px; border-left-color: { '#10b981' if cat == 'Low Risk' else '#f59e0b' if cat == 'Moderate Risk' else '#ef4444' };">
            <span style="font-size: 0.85rem; color: #64748b; text-transform: uppercase; font-weight: 600;">Overall Risk Score</span>
            <div style="font-size: 4rem; font-weight: 800; color: #0f172a; line-height: 1.1; margin: 10px 0;">
                {res['final_score']} <span style="font-size: 1.8rem; font-weight: 400; color: #64748b;">/ 100</span>
            </div>
            <div style="margin-bottom: 20px;">
                <span class="badge {badge_style}" style="font-size: 1.1rem; padding: 8px 18px;">{cat}</span>
            </div>
            <h5 style="margin-top: 0; color: #475569;">Clinical Summary:</h5>
            <p style="font-size: 0.95rem; line-height: 1.5; color: #334155;">
                {res['recommendation']}
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col_gauge:
        # Plotly Gauge Chart
        fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=res["final_score"],
            domain={'x': [0, 1], 'y': [0, 1]},
            gauge={
                'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569"},
                'bar': {'color': "#0f766e", 'thickness': 0.25},
                'bgcolor': "white",
                'borderwidth': 1,
                'bordercolor': "#cbd5e1",
                'steps': [
                    {'range': [0, 50], 'color': '#d1fae5'},
                    {'range': [50, 70], 'color': '#fef3c7'},
                    {'range': [70, 100], 'color': '#fee2e2'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 3},
                    'thickness': 0.75,
                    'value': res["final_score"]
                }
            }
        ))
        fig.update_layout(
            height=260, 
            margin=dict(l=20, r=20, t=40, b=20),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig, use_container_width=True)
        
    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
    
    # Render XAI section (Stacked bars + Radar + text description)
    render_explainability_section(res)
    
    st.markdown("<hr style='margin: 25px 0;'>", unsafe_allow_html=True)
    
    # Patient History Longitudinal Trend
    history = get_screening_history(p["patient_id"])
    if len(history) > 1:
        st.markdown("<h5>Longitudinal Parkinsonian Risk Trend</h5>", unsafe_allow_html=True)
        dates = [datetime.strptime(x["screening_date"], "%Y-%m-%d %H:%M:%S").strftime("%b %d, %Y") for x in history]
        scores = [x["final_score"] for x in history]
        
        fig_trend = go.Figure()
        fig_trend.add_trace(go.Scatter(
            x=dates, 
            y=scores, 
            mode="lines+markers", 
            line=dict(color="#0f766e", width=3),
            marker=dict(size=10, color="#0d9488", line=dict(color="white", width=2)),
            name="Risk Score Trend"
        ))
        fig_trend.update_layout(
            xaxis_title="Date of Assessment",
            yaxis_title="Risk Index (0-100)",
            yaxis=dict(range=[0, 100]),
            height=200,
            margin=dict(l=20, r=20, t=10, b=20),
            plot_bgcolor='rgba(0,0,0,0)',
            paper_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_trend, use_container_width=True)
    else:
        st.markdown(
            """
            <div class="medical-card-neutral">
                <strong>Longitudinal Tracking:</strong> This is the patient's first recorded screening in our database. 
                Future screening runs using the same Patient ID will automatically generate a progress timeline chart 
                comparing scores to monitor disease progression.
            </div>
            """, 
            unsafe_allow_html=True
        )
        
    # Actions & Printable Reports
    st.markdown("<h5>Clinical Documentation Actions</h5>", unsafe_allow_html=True)
    report_html = generate_report_html(p, res)
    
    st.download_button(
        label="📥 Download Clinical Screening Report (HTML/Print Ready)",
        data=report_html,
        file_name=f"parkisense_report_{p['patient_id']}.html",
        mime="text/html",
        use_container_width=True
    )
    
    st.markdown("""
    <div class="disclaimer-box">
        <strong>SAFETY COMPLIANCE AUDIT DISCLOSURE:</strong> The calculations shown here represent a weighted summation of 
        symptomatic and physical proxies. Changes in voice (shimmer/jitter), motor tremor (Archimedean deviations), and gait 
        kinematic characteristics can occur due to age, environment, arthritis, or other non-parkinsonian variables. 
        <strong>Clinical verification via DaTscan, MRI, or specialized MDS-UPDRS scoring is mandatory.</strong>
    </div>
    """, unsafe_allow_html=True)

def render_history_page():
    st.markdown('<div class="title-container"><h1 class="app-title">Clinical Registry</h1><div class="app-subtitle">Screening Logs & Database History</div></div>', unsafe_allow_html=True)
    
    st.markdown(
        """
        <div class="medical-card">
            <h4>Clinical Registry Audit Log</h4>
            <p style="color: #64748b; font-size: 0.9rem;">
                Below is a log of all patients registered in the local SQLite database. 
                Select a patient to view their screening trend history.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    patients = get_all_patients()
    
    if not patients:
        st.info("No records found. Complete a screening or run Demo Mode to populate patient history.")
        return
        
    df_patients = pd.DataFrame(patients)
    df_patients.rename(columns={
        "patient_id": "Patient ID",
        "name": "Name",
        "age": "Age",
        "gender": "Gender",
        "location": "Location",
        "created_at": "Date Created"
    }, inplace=True)
    
    st.dataframe(df_patients[["Patient ID", "Name", "Age", "Gender", "Location", "Date Created"]], use_container_width=True)
    
    # Dropdown to load patient history
    patient_ids = [p["patient_id"] for p in patients]
    patient_names = [f"{p['name']} ({p['patient_id']})" for p in patients]
    
    st.markdown("<h5>Load Longitudinal Patient Record</h5>", unsafe_allow_html=True)
    selected_idx = st.selectbox("Select Patient to inspect history trend", range(len(patient_names)), format_func=lambda i: patient_names[i])
    
    if selected_idx is not None:
        p_id = patient_ids[selected_idx]
        history = get_screening_history(p_id)
        
        if history:
            st.markdown(f"**Screening logs for patient ID: {p_id}**")
            
            history_records = []
            for record in history:
                history_records.append({
                    "Date": record["screening_date"],
                    "Symptom Score": f"{record['symptom_score']:.1f}/100",
                    "Voice Score": f"{record['voice_score']:.1f}/100" if record['voice_score'] is not None else "N/A",
                    "Writing Score": f"{record['writing_score']:.1f}/100" if record['writing_score'] is not None else "N/A",
                    "Gait Score": f"{record['gait_score']:.1f}/100" if record['gait_score'] is not None else "N/A",
                    "Final Risk": f"{record['final_score']:.1f}/100",
                    "Category": record["risk_category"]
                })
            st.table(history_records)
            
            # Trend plot
            dates = [datetime.strptime(x["screening_date"], "%Y-%m-%d %H:%M:%S").strftime("%b %d, %Y") for x in history]
            scores = [x["final_score"] for x in history]
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=dates, y=scores, mode="lines+markers", line=dict(color="#0f766e", width=2)))
            fig.update_layout(
                title=f"Disease Progression Risk Trend - ID: {p_id}",
                xaxis_title="Date",
                yaxis_title="Risk Index",
                yaxis=dict(range=[0, 100]),
                height=220,
                margin=dict(l=20,r=20,t=40,b=20),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig, use_container_width=True)
            
        else:
            st.write("No screening runs recorded for this patient.")

# --- RENDERING ROUTED PAGE ---
if st.session_state["current_page"] == "Home":
    render_home_page()
elif st.session_state["current_page"] == "Patient Profile":
    render_patient_profile()
elif st.session_state["current_page"] == "Symptoms":
    render_symptoms_questionnaire()
elif st.session_state["current_page"] == "Voice Test":
    render_voice_page()
elif st.session_state["current_page"] == "Writing Test":
    render_writing_page()
elif st.session_state["current_page"] == "Gait Test":
    render_gait_page()
elif st.session_state["current_page"] == "Risk Analysis":
    render_risk_engine_page()
elif st.session_state["current_page"] == "Results":
    render_results_dashboard()
elif st.session_state["current_page"] == "History":
    render_history_page()
