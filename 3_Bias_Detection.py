import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from fairlearn.metrics import (
    MetricFrame,
    selection_rate,
    demographic_parity_difference,
    demographic_parity_ratio,
    equalized_odds_difference,
)

# ----------------------------------------------------
# Page Configuration
# ----------------------------------------------------

st.set_page_config(
    page_title="Bias Detection",
    page_icon="⚖️",
    layout="wide",
)

st.title("⚖️ Bias Detection")

st.write(
    "Upload a binary classification dataset and evaluate fairness across a protected group using Fairlearn metrics."
)


def load_dataset(uploaded_file):
    suffix = uploaded_file.name.split(".")[-1].lower()
    if suffix == "csv":
        return pd.read_csv(uploaded_file)
    if suffix in ["xlsx", "xls"]:
        return pd.read_excel(uploaded_file)
    if suffix == "json":
        return pd.read_json(uploaded_file)
    raise ValueError("Unsupported file type. Upload CSV, Excel, or JSON.")


uploaded_file = st.file_uploader(
    "Upload dataset",
    type=["csv", "xlsx", "xls", "json"],
    help="The dataset must include a binary target column and a protected attribute.",
)

if uploaded_file is None:
    st.info("Please upload a dataset to run bias detection.")
    st.stop()

try:
    df = load_dataset(uploaded_file)
except Exception as error:
    st.error(f"Unable to load dataset: {error}")
    st.stop()

if df.empty:
    st.error("Uploaded dataset is empty.")
    st.stop()

st.write("### Dataset sample")
st.dataframe(df.head(), use_container_width=True)

columns = list(df.columns)

target_column = st.selectbox("Select the binary target column", columns)
protected_column = st.selectbox("Select the protected attribute column", columns)

if target_column == protected_column:
    st.error("Target column and protected attribute must be different.")
    st.stop()

if df[target_column].nunique() != 2:
    st.error("Target column must be binary.")
    st.stop()

protected_values = df[protected_column].unique()
if len(protected_values) < 2:
    st.error("Protected attribute must contain at least two groups.")
    st.stop()

feature_columns = [c for c in columns if c not in [target_column, protected_column]]

if len(feature_columns) == 0:
    st.error("Dataset must include at least one feature column besides target and protected attribute.")
    st.stop()

features = st.multiselect("Select feature columns", feature_columns, default=feature_columns)

if not features:
    st.error("Select at least one feature column.")
    st.stop()

with st.spinner("Training model and computing fairness metrics..."):
    X = df[features].copy()
    y = df[target_column]
    sensitive = df[protected_column]

    # one-hot encode categorical features
    categorical_cols = X.select_dtypes(include=["object", "category"]).columns.tolist()
    if categorical_cols:
        encoder = OneHotEncoder(sparse_output=False, handle_unknown="ignore")
        encoded = encoder.fit_transform(X[categorical_cols])
        encoded_cols = encoder.get_feature_names_out(categorical_cols)
        encoded_df = pd.DataFrame(encoded, columns=encoded_cols, index=X.index)
        X = pd.concat([X.drop(columns=categorical_cols), encoded_df], axis=1)

    X = X.fillna(0)
    y = y.astype(int)
    sensitive = sensitive.astype(str)

    X_train, X_test, y_train, y_test, s_train, s_test = train_test_split(
        X, y, sensitive, test_size=0.3, random_state=42, stratify=sensitive
    )

    model = LogisticRegression(max_iter=500)
    model.fit(X_train, y_train)
    predictions = model.predict(X_test)

    metric_frame = MetricFrame(
        metrics={"Selection Rate": selection_rate},
        y_true=y_test,
        y_pred=predictions,
        sensitive_features=s_test,
    )

    dp_difference = demographic_parity_difference(
        y_true=y_test, y_pred=predictions, sensitive_features=s_test
    )
    dp_ratio = demographic_parity_ratio(
        y_true=y_test, y_pred=predictions, sensitive_features=s_test
    )
    eo_difference = equalized_odds_difference(
        y_true=y_test, y_pred=predictions, sensitive_features=s_test
    )

fairness_score = max(0, round((1 - abs(dp_difference)) * 100, 2))

st.divider()

c1, c2, c3, c4 = st.columns(4)

c1.metric("Demographic Parity Difference", round(dp_difference, 4))
c2.metric("Parity Ratio", round(dp_ratio, 4))
c3.metric("Equalized Odds Difference", round(eo_difference, 4))
c4.metric("Fairness Score", f"{fairness_score}%")

st.divider()

if fairness_score >= 90:
    risk = "LOW"
    color = "green"
elif fairness_score >= 75:
    risk = "MEDIUM"
    color = "orange"
else:
    risk = "HIGH"
    color = "red"

st.subheader("Bias Risk Assessment")
st.markdown(f"### Risk Level: <span style='color:{color}'>{risk}</span>", unsafe_allow_html=True)
st.progress(fairness_score / 100)

st.divider()

selection_df = metric_frame.by_group.reset_index()
selection_df.columns = ["Group", "Selection Rate"]

st.subheader("Selection Rate by Group")
st.dataframe(selection_df, use_container_width=True, hide_index=True)

fig = px.bar(
    selection_df,
    x="Group",
    y="Selection Rate",
    text="Selection Rate",
    title="Selection Rate Across Protected Groups",
)
fig.update_traces(texttemplate="%{text:.2f}", textposition="outside")
fig.update_layout(height=500)
st.plotly_chart(fig, use_container_width=True)

st.divider()

summary = pd.DataFrame(
    {
        "Metric": [
            "Demographic Parity Difference",
            "Parity Ratio",
            "Equalized Odds Difference",
            "Fairness Score",
        ],
        "Value": [
            round(dp_difference, 4),
            round(dp_ratio, 4),
            round(eo_difference, 4),
            fairness_score,
        ],
    }
)

st.subheader("Metric Summary")
st.dataframe(summary, use_container_width=True, hide_index=True)
