"""Model Analysis - Detailed agent findings and recommendations."""

import streamlit as st
import json

st.set_page_config(
    page_title="Autonomic - Model Analysis",
    page_icon="🔬",
    layout="wide"
)

st.title("🔬 Detailed Model Analysis")
st.caption("Complete findings from all six governance agents")

st.divider()

# Create tabs for each agent
tabs = st.tabs([
    "🎯 Bias Detection",
    "🔐 Privacy",
    "⚖️ Compliance",
    "🛡️ Security",
    "💡 Explainability",
    "🔮 Risk Prediction"
])

# ==================== BIAS DETECTION ====================
with tabs[0]:
    st.subheader("Bias Detection Agent")
    st.metric("Score", "92/100", "+3")
    
    st.write("### Key Findings")
    st.info(
        "✅ **Minimal demographic bias detected**\n\n"
        "- Gender parity ratio: 0.94 (acceptable range: 0.9-1.0)\n"
        "- Race disparities within threshold\n"
        "- Age groups fairly represented"
    )
    
    st.write("### Disparities by Group")
    disparities = {
        "Group": ["Male", "Female", "White", "Black", "Asian"],
        "Approval Rate": ["85%", "68%", "88%", "62%", "81%"],
        "Disparity": ["0%", "-17%", "+3%", "-27%", "-4%"],
        "Status": ["✅", "⚠️", "✅", "🔴", "✅"]
    }
    st.table(disparities)
    
    st.write("### Recommendations")
    st.warning(
        "Address -27% disparity in Black applicant approval rates. "
        "Consider: (1) Fairness constraints in loss function, (2) Collect more diverse training data, "
        "(3) Add human review for borderline cases."
    )

# ==================== PRIVACY ====================
with tabs[1]:
    st.subheader("Privacy Detection Agent")
    st.metric("Score", "84/100", "-2")
    
    st.write("### Privacy Vulnerabilities Detected")
    st.error(
        "⚠️ **Model vulnerable to membership inference attacks**\n\n"
        "- Attack success rate: 42%\n"
        "- Confidence scores leak gender information\n"
        "- PII reconstruction possible for age/location"
    )
    
    st.write("### Test Results")
    privacy_tests = {
        "Test": [
            "Membership Inference",
            "Confidence Leakage",
            "PII Reconstruction",
            "Differential Privacy Gap"
        ],
        "Result": ["42% success", "2.1 bits leaked", "2 fields", "ε=3.5"],
        "Threshold": ["<35%", "<1.5 bits", "0 fields", "ε≤2.0"],
        "Status": ["🔴", "🔴", "🔴", "🟠"]
    }
    st.table(privacy_tests)
    
    st.write("### Immediate Actions")
    st.warning(
        "1. Implement differential privacy (ε=2.0 target)\n"
        "2. Add noise to confidence scores\n"
        "3. Limit feature exposure in API"
    )

# ==================== COMPLIANCE ====================
with tabs[2]:
    st.subheader("Compliance Agent")
    st.metric("Score", "85/100", "+2")
    
    st.write("### Regulatory Frameworks")
    frameworks = {
        "Framework": ["EU AI Act", "GDPR Art. 22", "SEC AI Rules", "California Law"],
        "Status": ["⚠️ Needs Action", "⚠️ Needs Action", "✅ Compliant", "⚠️ Needs Action"],
        "Gap": [
            "Missing risk assessment doc",
            "Missing human review trigger",
            "Complete",
            "Missing opt-out mechanism"
        ]
    }
    st.table(frameworks)
    
    st.write("### Compliance Roadmap")
    st.info(
        "**Est. time to full compliance: 3-4 weeks**\n\n"
        "Week 1: Complete EU AI Act risk assessment\n"
        "Week 2: Implement GDPR Art. 22 human review\n"
        "Week 3: Add California opt-out UI\n"
        "Week 4: Legal review and certification"
    )

# ==================== SECURITY ====================
with tabs[3]:
    st.subheader("Security Agent")
    st.metric("Score", "88/100", "+5")
    
    st.write("### Security Testing Results")
    security = {
        "Test": [
            "Adversarial Robustness",
            "Data Poisoning",
            "Model Extraction",
            "Input Validation"
        ],
        "Success Rate": ["38%", "25%", "82%", "15%"],
        "Threshold": ["<10%", "<10%", "<50%", "<5%"],
        "Status": ["🔴", "🟠", "🔴", "🟠"]
    }
    st.table(security)
    
    st.write("### Hardening Recommendations")
    st.warning(
        "1. Adversarial training needed\n"
        "2. Input sanitization required\n"
        "3. Model obfuscation for extraction defense\n"
        "4. Rate limiting on inference API"
    )

# ==================== EXPLAINABILITY ====================
with tabs[4]:
    st.subheader("Explainability Agent")
    st.metric("Score", "91/100", "+1")
    
    st.write("### Feature Importance")
    importance = {
        "Feature": ["Age", "Income", "Credit History", "Employment", "Debt Ratio"],
        "Importance": [0.32, 0.28, 0.25, 0.12, 0.03],
        "Interpretability": ["✅ High", "✅ High", "✅ High", "✅ Medium", "⚠️ Low"]
    }
    st.table(importance)
    
    st.write("### Legal Explainability")
    st.success(
        "✅ **GDPR Article 22 Compliant**\n\n"
        "- SHAP explanations provided\n"
        "- Counterfactual explanations available\n"
        "- User-friendly explanation templates created"
    )

# ==================== RISK PREDICTION ====================
with tabs[5]:
    st.subheader("Risk Prediction Agent")
    st.metric("Score", "83/100", "+3")
    
    st.write("### 30-Day Risk Forecast")
    risks = {
        "Risk": [
            "Fairness Drift",
            "Data Drift",
            "Accuracy Drop",
            "Regulatory Action"
        ],
        "Probability": ["18%", "35%", "22%", "8%"],
        "Severity": ["Medium", "High", "High", "Critical"],
        "Action": [
            "Monitor demographics",
            "Prepare retraining",
            "Collect validation data",
            "Maintain documentation"
        ]
    }
    st.table(risks)
    
    st.write("### Financial Impact Estimate")
    st.info(
        "💰 **If model fails in production:**\n\n"
        "- Regulatory fines: $10M - $50M\n"
        "- Reputational damage: High\n"
        "- Customer churn: 25-40%\n\n"
        "✅ **Recommended preventive investment: $500K**\n"
        "ROI: 20x-100x by avoiding potential losses"
    )
    
    st.write("### Recommended Monitoring")
    st.success(
        "Set up continuous monitoring with automated alerts for:\n\n"
        "- Weekly fairness audits\n"
        "- Daily data distribution checks\n"
        "- Real-time accuracy tracking\n"
        "- Monthly re-certification cycle"
    )

st.divider()

if st.button("← Back to Dashboard"):
    st.switch_page("pages/1_Dashboard.py")
