import streamlit as st
from datetime import datetime
from modules.symptoms import get_normalized_symptom_score
from utils.database import save_screening

# Centralized weight configurations
WEIGHTS = {
    "symptoms": 0.40,
    "voice": 0.20,
    "writing": 0.15,
    "gait": 0.25
}

def calculate_overall_risk():
    """
    Computes the weighted risk score from the four screening modalities:
    Symptoms, Voice, Writing, and Gait.
    """
    # 1. Symptom score
    symptom_score = get_normalized_symptom_score()
    
    # 2. Voice score (falls back to 0 if not completed)
    voice_score = st.session_state["voice"]["risk_score"] if st.session_state["voice"]["features_extracted"] else 0.0
    voice_completed = st.session_state["voice"]["features_extracted"]
    
    # 3. Writing score (falls back to 0 if not completed)
    writing_score = st.session_state["writing"]["risk_score"] if st.session_state["writing"]["features_extracted"] else 0.0
    writing_completed = st.session_state["writing"]["features_extracted"]
    
    # 4. Gait score (falls back to 0 if not completed)
    gait_score = st.session_state["gait"]["risk_score"] if st.session_state["gait"]["features_extracted"] else 0.0
    gait_completed = st.session_state["gait"]["features_extracted"]
    
    # Dynamic weight normalization if some tests were not completed (so risk score is always correct)
    # However, for the hackathon prototype, we want to encourage all tests.
    total_weight = 0.0
    weighted_score = 0.0
    
    # Always include symptoms (base questionnaire)
    total_weight += WEIGHTS["symptoms"]
    weighted_score += symptom_score * WEIGHTS["symptoms"]
    
    if voice_completed:
        total_weight += WEIGHTS["voice"]
        weighted_score += voice_score * WEIGHTS["voice"]
    if writing_completed:
        total_weight += WEIGHTS["writing"]
        weighted_score += writing_score * WEIGHTS["writing"]
    if gait_completed:
        total_weight += WEIGHTS["gait"]
        weighted_score += gait_score * WEIGHTS["gait"]
        
    final_score = (weighted_score / total_weight) if total_weight > 0 else 0.0
    final_score = min(100.0, max(0.0, final_score))
    
    # Classify Risk Category
    if final_score <= 50.0:
        risk_category = "Low Risk"
    elif final_score <= 70.0:
        risk_category = "Moderate Risk"
    else:
        risk_category = "High Risk"
        
    # Generate recommendations
    if risk_category == "Low Risk":
        recommendation = (
            "Current screening indicators suggest relatively low risk. Continue routine health monitoring "
            "and consult a healthcare professional if new symptoms develop or persist."
        )
    elif risk_category == "Moderate Risk":
        recommendation = (
            "Some screening indicators (such as moderate symptom burden or slight acoustic/motor changes) "
            "warrant attention. Consider scheduling a discussion with a qualified healthcare professional "
            "to monitor these signs longitudinally."
        )
    else: # High Risk
        recommendation = (
            "Several screening indicators require further clinical evaluation. It is highly recommended "
            "to consult a qualified neurologist or primary care provider for a comprehensive clinical assessment, "
            "as early intervention can significantly improve long-term management."
        )
        
    # Find contributing factors (those scores exceeding 50.0)
    contributing_factors = []
    if symptom_score > 50:
        contributing_factors.append(f"Elevated symptom checklist score ({symptom_score:.1f}/100)")
    if voice_completed and voice_score > 50:
        contributing_factors.append(f"Speech acoustic abnormalities / instability ({voice_score:.1f}/100)")
    if writing_completed and writing_score > 50:
        contributing_factors.append(f"Writing tremor / irregularity detected ({writing_score:.1f}/100)")
    if gait_completed and gait_score > 50:
        contributing_factors.append(f"Gait rhythm asymmetry / step instability ({gait_score:.1f}/100)")
        
    if not contributing_factors:
        contributing_factors.append("No specific high-risk indicators detected across modalities.")
        
    results = {
        "patient_id": st.session_state["patient_id"],
        "screening_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "symptom_score": float(round(symptom_score, 1)),
        "voice_score": float(round(voice_score, 1)) if voice_completed else None,
        "writing_score": float(round(writing_score, 1)) if writing_completed else None,
        "gait_score": float(round(gait_score, 1)) if gait_completed else None,
        "final_score": float(round(final_score, 1)),
        "risk_category": risk_category,
        "contributing_factors": contributing_factors,
        "recommendation": recommendation
    }
    
    return results

def render_risk_engine_page():
    st.markdown('<div class="title-container"><h1 class="app-title">Risk Stratification Engine</h1><div class="app-subtitle">Centralized Scoring and Assessment Weights</div></div>', unsafe_allow_html=True)
    
    st.markdown(
        """
        <div class="medical-card">
            <h4>Prototype Weighted Screening Architecture</h4>
            <p style="color: #64748b; font-size: 0.9rem;">
                ParkiSense uses a transparent weighted algorithm to consolidate multimodal inputs. 
                This design allows clinicians to adjust feature weights and audit the risk engine step-by-step.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Weight settings visualization
    st.markdown("<h5>Modal Weight Configurations</h5>", unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Symptoms Weight", f"{int(WEIGHTS['symptoms']*100)}%")
        st.caption("Subjective/Clinical Questionnaire")
    with col2:
        st.metric("Speech/Voice Weight", f"{int(WEIGHTS['voice']*100)}%")
        st.caption("Acoustic Stability")
    with col3:
        st.metric("Handwriting Weight", f"{int(WEIGHTS['writing']*100)}%")
        st.caption("Spiral Residual Tremor")
    with col4:
        st.metric("Gait/Walking Weight", f"{int(WEIGHTS['gait']*100)}%")
        st.caption("Spatiotemporal Regularity")
        
    st.markdown("<hr style='margin: 20px 0;'>", unsafe_allow_html=True)
    
    # Completion status checklist
    st.markdown("<h5>Modal Screening Status</h5>", unsafe_allow_html=True)
    
    s_score = get_normalized_symptom_score()
    v_done = st.session_state["voice"]["features_extracted"]
    w_done = st.session_state["writing"]["features_extracted"]
    g_done = st.session_state["gait"]["features_extracted"]
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.checkbox("Symptoms Checklist Completed", value=True, disabled=True)
        st.write(f"Score: **{s_score:.1f}/100**")
    with c2:
        st.checkbox("Voice Recording Processed", value=v_done, disabled=True)
        if v_done:
            st.write(f"Score: **{st.session_state['voice']['risk_score']:.1f}/100**")
        else:
            st.write("Score: *Not Done*")
    with c3:
        st.checkbox("Writing Canvas Processed", value=w_done, disabled=True)
        if w_done:
            st.write(f"Score: **{st.session_state['writing']['risk_score']:.1f}/100**")
        else:
            st.write("Score: *Not Done*")
    with c4:
        st.checkbox("Gait Video Processed", value=g_done, disabled=True)
        if g_done:
            st.write(f"Score: **{st.session_state['gait']['risk_score']:.1f}/100**")
        else:
            st.write("Score: *Not Done*")
            
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("Generate Risk Assessment Profile", type="primary"):
        with st.spinner("Compiling patient parameters and running explainability estimators..."):
            time.sleep(1.2) # Simulate processing
            results = calculate_overall_risk()
            st.session_state["calculated_results"] = results
            st.session_state["screening_completed"] = True
            
            # Save screening to database
            try:
                save_screening(results)
                st.success("Risk assessment completed and screening saved to clinical registry!")
            except Exception as e:
                st.warning(f"Assessment completed, but database persistence failed: {str(e)}")
                
            # Redirect to Results page
            st.session_state["current_page"] = "Results"
            st.rerun()
