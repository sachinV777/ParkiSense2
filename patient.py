import streamlit as st
from datetime import datetime
from utils.database import save_patient

def render_patient_profile():
    st.markdown('<div class="title-container"><h1 class="app-title">Patient Profile</h1><div class="app-subtitle">ParkiSense Screening Registry</div></div>', unsafe_allow_html=True)
    
    st.markdown(
        """
        <div class="medical-card">
            <h4>Demographic and Clinical Intake</h4>
            <p style="color: #64748b; font-size: 0.9rem;">
                Please record the patient's basic details and history. Clinical demographic data is used to contextualize risk assessments and establish longitudinal tracking.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Form layout
    with st.form("patient_profile_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            patient_id_input = st.text_input(
                "Patient ID / Clinical Registry Code",
                value=st.session_state["patient_profile"]["patient_id"],
                help="Unique patient identifier. A random ID has been pre-generated, but you can overwrite it."
            )
            name = st.text_input(
                "Full Name *",
                value=st.session_state["patient_profile"]["name"],
                placeholder="e.g. John Doe"
            )
            age = st.number_input(
                "Age *",
                min_value=1,
                max_value=120,
                value=st.session_state["patient_profile"]["age"]
            )
            gender = st.selectbox(
                "Biological Gender",
                ["Male", "Female", "Other"],
                index=["Male", "Female", "Other"].index(st.session_state["patient_profile"]["gender"])
            )
            location = st.text_input(
                "Geographic Location (City/State)",
                value=st.session_state["patient_profile"]["location"],
                placeholder="e.g. Mumbai, India"
            )
            
        with col2:
            family_history = st.selectbox(
                "Family History of Parkinson's Disease (PD)",
                ["No History", "First-degree Relative (Parent/Sibling)", "Second-degree Relative (Grandparent/Uncle/Aunt)", "Multiple Relatives"],
                index=["No History", "First-degree Relative (Parent/Sibling)", "Second-degree Relative (Grandparent/Uncle/Aunt)", "Multiple Relatives"].index(
                    st.session_state["patient_profile"]["family_history"]
                )
            )
            neurological_conditions = st.selectbox(
                "Existing Neurological Conditions",
                ["None", "Essential Tremor", "Alzheimer's Disease / Dementia", "Stroke / Vascular Parkinsonism", "Other"],
                index=["None", "Essential Tremor", "Alzheimer's Disease / Dementia", "Stroke / Vascular Parkinsonism", "Other"].index(
                    st.session_state["patient_profile"]["neurological_conditions"]
                )
            )
            previous_screening = st.selectbox(
                "Previous Parkinson's Screening History",
                ["No previous screening", "Screened - Low Risk", "Screened - Moderate Risk", "Screened - High Risk"],
                index=["No previous screening", "Screened - Low Risk", "Screened - Moderate Risk", "Screened - High Risk"].index(
                    st.session_state["patient_profile"]["previous_screening"]
                )
            )
            medications = st.text_area(
                "Current Medications",
                value=st.session_state["patient_profile"]["medications"],
                placeholder="e.g. Amlodipine 5mg, Metformin 500mg (Include all supplements/neurological agents)",
                height=68
            )
            medical_history = st.text_area(
                "Relevant Clinical History / Co-morbidities",
                value=st.session_state["patient_profile"]["medical_history"],
                placeholder="e.g. Hypertension for 5 years, osteoarthritis, sleep issues...",
                height=68
            )
            
        submit_btn = st.form_submit_button("Save Patient Profile")
        
        if submit_btn:
            if not name.strip():
                st.error("Validation Error: Patient Name is required.")
            elif not patient_id_input.strip():
                st.error("Validation Error: Patient ID is required.")
            else:
                profile = {
                    "patient_id": patient_id_input.strip(),
                    "name": name.strip(),
                    "age": age,
                    "gender": gender,
                    "location": location.strip(),
                    "medical_history": medical_history.strip(),
                    "medications": medications.strip(),
                    "family_history": family_history,
                    "neurological_conditions": neurological_conditions,
                    "previous_screening": previous_screening,
                    "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state["patient_profile"] = profile
                st.session_state["patient_id"] = profile["patient_id"]
                
                try:
                    save_patient(profile)
                    st.success(f"Success: Profile for {name} (ID: {profile['patient_id']}) saved successfully to database!")
                except Exception as e:
                    st.warning(f"Profile saved in session state, but database save failed: {str(e)}")
                    
    # Display Current Profile Summary Card
    p = st.session_state["patient_profile"]
    if p["name"]:
        st.markdown(f"""
        <div class="medical-card" style="border-left-color: #0d9488; margin-top: 20px;">
            <h5 style="margin-top: 0; color: #0d9488;">Active Patient Profile</h5>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 0.9rem;">
                <div><strong>ID:</strong> {p['patient_id']}</div>
                <div><strong>Name:</strong> {p['name']}</div>
                <div><strong>Age/Gender:</strong> {p['age']} yrs / {p['gender']}</div>
                <div><strong>Family History:</strong> {p['family_history']}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
