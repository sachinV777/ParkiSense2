import streamlit as st
import plotly.graph_objects as go
import pandas as pd

def render_radar_chart(results):
    """Renders a Plotly radar chart of the 4 screening dimensions."""
    categories = ['Symptom Checklist', 'Voice/Speech', 'Handwriting/Writing', 'Gait/Walking']
    
    # Extract scores or default to 0
    scores = [
        results.get("symptom_score", 0.0),
        results.get("voice_score", 0.0) if results.get("voice_score") is not None else 0.0,
        results.get("writing_score", 0.0) if results.get("writing_score") is not None else 0.0,
        results.get("gait_score", 0.0) if results.get("gait_score") is not None else 0.0
    ]
    
    # Close the radar loop
    categories = [*categories, categories[0]]
    scores = [*scores, scores[0]]
    
    fig = go.Figure()
    
    # Add Patient Path
    fig.add_trace(go.Scatterpolar(
        r=scores,
        theta=categories,
        fill='toself',
        fillcolor='rgba(13, 148, 136, 0.2)',
        line=dict(color='#0f766e', width=2),
        name='Patient Risk Profile'
    ))
    
    # Add Normal Baseline (e.g. general population low-risk baseline)
    baseline_scores = [20.0, 20.0, 20.0, 20.0, 20.0]
    fig.add_trace(go.Scatterpolar(
        r=baseline_scores,
        theta=categories,
        fill='none',
        line=dict(color='#94a3b8', width=1.5, dash='dash'),
        name='Low-Risk Reference'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(size=9),
                gridcolor='#f1f5f9'
            ),
            angularaxis=dict(
                gridcolor='#f1f5f9'
            )
        ),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=-0.15, xanchor="center", x=0.5),
        margin=dict(l=30, r=30, t=30, b=30),
        height=280
    )
    return fig

def render_contribution_chart(results):
    """Renders a horizontal bar chart showing how each modality contributes to the final score."""
    # Weights
    w_sym = 0.40
    w_voc = 0.20
    w_wri = 0.15
    w_gai = 0.25
    
    s_score = results.get("symptom_score", 0.0)
    v_score = results.get("voice_score", 0.0) if results.get("voice_score") is not None else 0.0
    w_score = results.get("writing_score", 0.0) if results.get("writing_score") is not None else 0.0
    g_score = results.get("gait_score", 0.0) if results.get("gait_score") is not None else 0.0
    
    # Calculate contributions (weighted scores)
    contribs = [
        s_score * w_sym,
        v_score * w_voc,
        w_score * w_wri,
        g_score * w_gai
    ]
    
    labels = ['Symptom Checklist', 'Voice/Speech', 'Handwriting/Writing', 'Gait/Walking']
    max_contribs = [100.0 * w_sym, 100.0 * w_voc, 100.0 * w_wri, 100.0 * w_gai]
    
    fig = go.Figure()
    
    # Background representing maximum contribution
    fig.add_trace(go.Bar(
        y=labels,
        x=max_contribs,
        name='Max Potential Weight',
        orientation='h',
        marker=dict(
            color='rgba(226, 232, 240, 0.5)',
            line=dict(color='rgba(226, 232, 240, 1.0)', width=1)
        )
    ))
    
    # Foreground showing patient actual contribution
    fig.add_trace(go.Bar(
        y=labels,
        x=contribs,
        name='Patient Risk Contribution',
        orientation='h',
        marker=dict(
            color='#0d9488',
            line=dict(color='#0f766e', width=1)
        ),
        text=[f"{val:.1f} pts" for val in contribs],
        textposition='inside',
        insidetextanchor='end',
        textfont=dict(color='white', size=11, family='Outfit')
    ))
    
    fig.update_layout(
        barmode='overlay',
        xaxis=dict(
            title='Point Contribution to Final Score (out of 100)',
            range=[0, 45],
            gridcolor='#f1f5f9'
        ),
        yaxis=dict(autorange="reversed"),
        showlegend=False,
        margin=dict(l=20, r=20, t=10, b=30),
        height=200,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)'
    )
    return fig

def render_explainability_section(results):
    st.markdown("<h4 style='color: #0f766e; margin-top: 20px;'>Explainable AI (XAI) Risk Breakdown</h4>", unsafe_allow_html=True)
    
    col1, col2 = st.columns([1.1, 0.9])
    
    with col1:
        st.markdown("<p style='font-size: 0.9rem; color: #475569;'><strong>Point Contribution Analysis</strong></p>", unsafe_allow_html=True)
        fig_contrib = render_contribution_chart(results)
        st.plotly_chart(fig_contrib, use_container_width=True)
        
    with col2:
        st.markdown("<p style='font-size: 0.9rem; color: #475569;'><strong>Multimodal Signature Radar</strong></p>", unsafe_allow_html=True)
        fig_radar = render_radar_chart(results)
        st.plotly_chart(fig_radar, use_container_width=True)
        
    # Textual explainability narrative
    st.markdown("<p style='font-size: 1rem; font-weight: 600; color: #0f172a; margin-top: 15px;'>Diagnostic Explanation & Feature Correlation</p>", unsafe_allow_html=True)
    
    narratives = []
    
    # 1. Symptoms narrative
    s_score = results["symptom_score"]
    if s_score > 60:
        narratives.append("🔴 **High Symptom Burden**: The symptom survey reports significant motor impairment (rest tremors, bradykinesia, balance difficulties) alongside autonomic non-motor signs (anosmia, sleep disorders), establishing a highly correlated Parkinsonian baseline.")
    elif s_score > 30:
        narratives.append("🟡 **Moderate Symptom Burden**: Patient reports intermittent motor stiffness and early autonomic signs (e.g. sleep issues, constipation) representing a mild-to-moderate clinical symptom presentation.")
    else:
        narratives.append("🟢 **Low Symptom Burden**: The patient's reported symptoms are minor and match baseline non-pathological expectations.")
        
    # 2. Voice narrative
    if results.get("voice_score") is not None:
        v_score = results["voice_score"]
        if v_score > 60:
            v_stability = st.session_state["voice"].get("stability", 50.0)
            v_jitter = st.session_state["voice"].get("jitter", 0.02)
            narratives.append(f"🔴 **Vocal Dysarthria Markers**: Voice stability is low ({v_stability}%) and frequency perturbation (Jitter: {v_jitter:.4f}) is elevated. Cycle-to-cycle variability matches vocal micro-tremors typical of hypokinetic dysarthria in basal ganglia disorders.")
        elif v_score > 30:
            narratives.append("🟡 **Mild Speech Changes**: Mild acoustic frequency fluctuations are present in the sustained phonation test, although amplitude remains relatively stable.")
            
    # 3. Writing narrative
    if results.get("writing_score") is not None:
        w_score = results["writing_score"]
        if w_score > 60:
            w_tremor = st.session_state["writing"].get("tremor_index", 50)
            w_size = st.session_state["writing"].get("size_consistency", 80)
            micro_warn = " and micrographia indicators (abnormally small tracing size)" if w_size < 60 else ""
            narratives.append(f"🔴 **Motor Tremor Irregularity**: Archimedean spiral tracing shows severe contour deviations (Tremor Index: {w_tremor}%){micro_warn}. Radial residual variance is elevated, signifying action tremor and fine-motor incoordination.")
        elif w_score > 30:
            narratives.append("🟡 **Mild Drawing Hesitancy**: Spiral tracing displays minor stroke thickness variations and trace deviations, indicating mild motor hesitancy.")
            
    # 4. Gait narrative
    if results.get("gait_score") is not None:
        g_score = results["gait_score"]
        if g_score > 60:
            g_sym = st.session_state["gait"].get("symmetry", 80)
            g_sway = st.session_state["gait"].get("postural_sway", 10)
            narratives.append(f"🔴 **Gait Instability**: Walk kinetics show significant left-right stance phase asymmetry (Symmetry: {g_sym}%) and increased trunk sway ({g_sway}%). Stride regularity is disrupted, correlating with clinical shuffling and freezing risks.")
        elif g_score > 30:
            narratives.append("🟡 **Subtle Gait Deviations**: Minor spatiotemporal rhythm changes are noted, though general cadence and step symmetry remain close to healthy baselines.")
            
    st.markdown(
        f"""
        <div class="medical-card-neutral" style="border-left: 4px solid #0d9488;">
            <p style="margin: 0; font-size: 0.9rem; line-height: 1.6;">
                {"<br><br>".join(narratives)}
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )
