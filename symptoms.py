import streamlit as st

# Define questions and descriptions
SYMPTOM_QUESTIONS = {
    "motor": [
        ("tremor", "Rest Tremor", "Involuntary shaking or trembling of hands, limbs, or jaw when muscles are relaxed."),
        ("slowness", "Bradykinesia (Slowness of Movement)", "Slowness in executing movement, difficulty starting or completing motor tasks."),
        ("stiffness", "Rigidity (Muscle Stiffness)", "Stiffness or resistance in limbs, neck, or back, sometimes causing muscle ache."),
        ("balance", "Postural Instability (Balance Issues)", "Difficulty maintaining balance or stability when standing, turning, or walking."),
        ("walking", "Walking Difficulty / Shuffling", "Shuffling gait, taking short steps, or feeling like your feet are glued to the floor (freezing)."),
        ("arm_swing", "Reduced Arm Swing", "Reduced swinging of one or both arms when walking."),
        ("fine_motor", "Fine Motor Difficulty", "Problems with delicate tasks like buttoning shirts, using utensils, or handwriting.")
    ],
    "non_motor": [
        ("sleep", "Sleep Disturbances (RBD)", "Acting out dreams, thrashing in sleep, sleep walking, or chronic insomnia."),
        ("fatigue", "Persistent Fatigue", "A constant feeling of physical or mental exhaustion that does not improve with rest."),
        ("constipation", "Gastrointestinal Constipation", "Chronic bowel irregularity or sluggishness, a common early autonomic symptom."),
        ("smell", "Loss of Sense of Smell (Hyposmia)", "Reduced ability to detect or identify common odors (e.g. coffee, gas, flowers)."),
        ("mood", "Mood or Cognitive Changes", "Unexplained feelings of apathy, depression, anxiety, or mild memory/attention lapses."),
        ("speech", "Speech & Voice Changes", "Speaking in a softer, more monotonous voice, or occasional slurring of words.")
    ]
}

SCORE_MAP = {
    "Never": 0,
    "Rarely": 1,
    "Sometimes": 2,
    "Often": 3,
    "Severe": 4
}

INV_SCORE_MAP = {v: k for k, v in SCORE_MAP.items()}

def render_symptoms_questionnaire():
    st.markdown('<div class="title-container"><h1 class="app-title">Symptom Assessment</h1><div class="app-subtitle">Structured Symptom Questionnaire</div></div>', unsafe_allow_html=True)
    
    st.markdown(
        """
        <div class="medical-card">
            <h4>Motor & Non-Motor Symptom Checklist</h4>
            <p style="color: #64748b; font-size: 0.9rem;">
                Answer these questions based on observations over the past 3-6 months. Symptoms are categorized into motor (movement-related) and non-motor (systemic/neurological) indicators.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Initialize symptom state if empty
    all_keys = [q[0] for cat in SYMPTOM_QUESTIONS.values() for q in cat]
    for key in all_keys:
        if key not in st.session_state["symptoms"]:
            st.session_state["symptoms"][key] = "Never"
            
    # Calculate progress
    answered_count = sum(1 for k in all_keys if st.session_state["symptoms"].get(k) != "Never")
    total_questions = len(all_keys)
    progress_percentage = answered_count / total_questions
    
    # Custom progress indicator
    st.markdown(f"""
        <div style="margin-bottom: 20px;">
            <div style="display: flex; justify-content: space-between; font-size: 0.85rem; color: #475569; font-weight: 500;">
                <span>Assessment Completion</span>
                <span>Questionnaire Progress: {answered_count} / {total_questions} answered</span>
            </div>
            <div class="progress-bar-container">
                <div class="progress-bar-fill" style="width: {progress_percentage * 100}%;"></div>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    # Store temporary form values
    form_values = {}
    
    with col1:
        st.markdown("<h4 style='color: #0f766e; border-bottom: 2px solid #0d9488; padding-bottom: 5px;'>Motor Indicators</h4>", unsafe_allow_html=True)
        for key, name, desc in SYMPTOM_QUESTIONS["motor"]:
            current_val = st.session_state["symptoms"].get(key, "Never")
            # Select slider or radio
            form_values[key] = st.select_slider(
                f"**{name}**\n*{desc}*",
                options=["Never", "Rarely", "Sometimes", "Often", "Severe"],
                value=current_val,
                key=f"slider_{key}"
            )
            st.markdown("<hr style='margin: 10px 0; border: 0; border-top: 1px solid #f1f5f9;'>", unsafe_allow_html=True)
            
    with col2:
        st.markdown("<h4 style='color: #0f766e; border-bottom: 2px solid #0d9488; padding-bottom: 5px;'>Non-Motor Indicators</h4>", unsafe_allow_html=True)
        for key, name, desc in SYMPTOM_QUESTIONS["non_motor"]:
            current_val = st.session_state["symptoms"].get(key, "Never")
            form_values[key] = st.select_slider(
                f"**{name}**\n*{desc}*",
                options=["Never", "Rarely", "Sometimes", "Often", "Severe"],
                value=current_val,
                key=f"slider_{key}"
            )
            st.markdown("<hr style='margin: 10px 0; border: 0; border-top: 1px solid #f1f5f9;'>", unsafe_allow_html=True)
            
    if st.button("Save Symptoms & Continue"):
        st.session_state["symptoms"] = form_values
        
        # Calculate symptom score
        total_points = sum(SCORE_MAP[val] for val in form_values.values())
        max_points = total_questions * 4
        symptom_score = (total_points / max_points) * 100
        
        st.session_state["symptom_score_value"] = symptom_score
        st.success(f"Symptom Assessment saved successfully! Normalized Symptom Score: {symptom_score:.1f}/100")
        
        # Advance page to Voice Test
        st.session_state["current_page"] = "Voice Test"
        st.rerun()

def get_normalized_symptom_score():
    """Calculate current symptom score based on session state."""
    all_keys = [q[0] for cat in SYMPTOM_QUESTIONS.values() for q in cat]
    if not all_keys:
        return 0.0
    total_points = sum(SCORE_MAP.get(st.session_state["symptoms"].get(k, "Never"), 0) for k in all_keys)
    max_points = len(all_keys) * 4
    return (total_points / max_points) * 100
