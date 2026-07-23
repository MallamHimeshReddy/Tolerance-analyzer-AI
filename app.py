from __future__ import annotations

import json
import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# ---------------------------------------------------
# FIX IMPORT PATH
# ---------------------------------------------------
if __package__ in {None, ""}:
    sys.path.insert(
        0,
        str(Path(__file__).resolve().parent),
    )

# ---------------------------------------------------
# IMPORTS
# ---------------------------------------------------
from agents.insight_agent import (
    list_ollama_models,
)

from workflow import (
    PROJECT_ROOT,
    run_automated_workflow,
)

from cv.ocr import (
    extract_text_from_image,
)

from cv.parser import (
    clean_ocr_dimension_text,
    parse_tolerances_from_text,
)

# ---------------------------------------------------
# PATHS
# ---------------------------------------------------
UPLOAD_DIR = (
    PROJECT_ROOT
    / "data"
    / "uploads"
)

# ---------------------------------------------------
# SAVE UPLOADED FILE
# ---------------------------------------------------
def save_upload(uploaded_file) -> Path:

    UPLOAD_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = (
        UPLOAD_DIR
        / uploaded_file.name
    )

    output_path.write_bytes(
        uploaded_file.getbuffer()
    )

    return output_path

# ---------------------------------------------------
# BUILD DATAFRAME
# ---------------------------------------------------
def build_manual_dataframe(
    dimensions,
    tolerance,
):

    rows = []

    for idx, dim in enumerate(
        dimensions,
        start=1,
    ):

        rows.append(
            {
                "feature": f"dimension_{idx}",
                "nominal": float(dim),
                "tolerance": float(tolerance),
                "direction": 1,
                "lower_limit": (
                    float(dim)
                    - float(tolerance)
                ),
                "upper_limit": (
                    float(dim)
                    + float(tolerance)
                ),
            }
        )

    return pd.DataFrame(rows)

# ---------------------------------------------------
# PAGE CONFIG
# ---------------------------------------------------
st.set_page_config(
    page_title="Tolerance AI Analyzer",
    page_icon="⚙️",
    layout="wide",
)

# ---------------------------------------------------
# CSS
# ---------------------------------------------------
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        max-width: 1200px;
    }

    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------
# TITLE
# ---------------------------------------------------
st.title(
    "⚙️ AI-Assisted Tolerance Stack-Up Analyzer"
)

st.caption(
    """
Upload engineering drawings or CSV files
to perform:

- OCR extraction
- tolerance parsing
- stack-up analysis
- optimization
- validation
- report generation
"""
)

# ---------------------------------------------------
# SIDEBAR
# ---------------------------------------------------
with st.sidebar:

    st.header(
        "⚙️ Run Settings"
    )

    available_models = (
        list_ollama_models()
    )

    if available_models:

        st.success(
            "Ollama connected"
        )

        default_index = (
            available_models.index(
                "qwen2.5:7b"
            )
            if "qwen2.5:7b"
            in available_models
            else 0
        )

        llm_model = st.selectbox(
            "Ollama model",
            available_models,
            index=default_index,
        )

    else:

        st.warning(
            "Ollama not detected"
        )

        llm_model = st.text_input(
            "Ollama model",
            value="qwen2.5:7b",
        )

    validation_method = st.selectbox(
        "Validation method",
        [
            "worst_case",
            "rss",
        ],
    )

    ocr_backend = st.selectbox(
        "OCR backend",
        [
            "easyocr",
        ],
    )

    use_llm_extraction = st.toggle(
        "Use Ollama fallback",
        value=False,
    )

    default_tolerance = st.number_input(
        "Default tolerance",
        min_value=0.001,
        value=0.10,
        step=0.01,
        format="%.3f",
    )

    use_custom_limits = st.toggle(
        "Use custom limits",
        value=True,
    )

    lower_spec = st.number_input(
        "Lower spec limit",
        value=63.0,
        disabled=(
            not use_custom_limits
        ),
    )

    upper_spec = st.number_input(
        "Upper spec limit",
        value=66.0,
        disabled=(
            not use_custom_limits
        ),
    )

    output_name = st.text_input(
        "Report name",
        value="ui_tolerance_report",
    )

# ---------------------------------------------------
# FILE UPLOADER
# ---------------------------------------------------
uploaded_file = st.file_uploader(
    "📤 Upload engineering drawing or CSV",
    type=[
        "csv",
        "png",
        "jpg",
        "jpeg",
        "bmp",
        "tif",
        "tiff",
        "webp",
    ],
)

# ---------------------------------------------------
# RUN BUTTON
# ---------------------------------------------------
run_clicked = st.button(
    "🚀 Run Automated Analysis",
    type="primary",
    use_container_width=True,
)

# ---------------------------------------------------
# MAIN EXECUTION
# ---------------------------------------------------
if run_clicked:

    # ---------------------------------------------------
    # VALIDATE INPUT
    # ---------------------------------------------------
    if uploaded_file is None:

        st.error(
            "Upload a CSV or image first."
        )

        st.stop()

    # ---------------------------------------------------
    # SAVE FILE
    # ---------------------------------------------------
    input_path = save_upload(
        uploaded_file
    )

    # ---------------------------------------------------
    # DISPLAY IMAGE
    # ---------------------------------------------------
    is_csv = (
        input_path.suffix.lower()
        == ".csv"
    )

    if not is_csv:

        st.image(
            str(input_path),
            caption="Uploaded Drawing",
            use_container_width=True,
        )

    # ---------------------------------------------------
    # DEBUG SECTION
    # ---------------------------------------------------
    st.subheader(
        "🔍 Input Processing"
    )

    debug_df = pd.DataFrame()

    # ===================================================
    # CSV INPUT
    # ===================================================
    if is_csv:

        st.success(
            "CSV detected. OCR skipped."
        )

        try:

            debug_df = pd.read_csv(
                input_path
            )

        except Exception as exc:

            st.error(
                f"Could not read CSV:\n\n{exc}"
            )

            st.stop()

        st.subheader(
            "📋 CSV Data"
        )

        st.dataframe(
            debug_df,
            use_container_width=True,
        )

    # ===================================================
    # IMAGE INPUT
    # ===================================================
    else:

        st.success(
            "Image detected. Running OCR."
        )

        # ---------------------------------------------------
        # OCR
        # ---------------------------------------------------
        try:

            raw_text = (
                extract_text_from_image(
                    str(input_path)
                )
            )

        except Exception as exc:

            st.error(
                f"OCR failed:\n\n{exc}"
            )

            st.stop()

        st.subheader(
            "📝 Raw OCR Text"
        )

        st.code(raw_text)

        # ---------------------------------------------------
        # CLEAN OCR
        # ---------------------------------------------------
        cleaned_text = (
            clean_ocr_dimension_text(
                raw_text
            )
        )

        st.subheader(
            "🧹 Cleaned OCR Text"
        )

        st.code(cleaned_text)

        # ---------------------------------------------------
        # PARSE
        # ---------------------------------------------------
        debug_df = (
            parse_tolerances_from_text(
                cleaned_text,
                default_tolerance=default_tolerance,
            )
        )

        # ---------------------------------------------------
        # EXTRACT DIMENSIONS
        # ---------------------------------------------------
        extracted_dimensions = []

        if (
            not debug_df.empty
            and "nominal"
            in debug_df.columns
        ):

            extracted_dimensions = (
                sorted(
                    debug_df["nominal"]
                    .dropna()
                    .astype(float)
                    .unique()
                    .tolist()
                )
            )

        st.subheader(
            "📏 Extracted Dimensions"
        )

        st.write(
            extracted_dimensions
        )

        # ---------------------------------------------------
        # MANUAL EDIT
        # ---------------------------------------------------
        st.subheader(
            "✍️ Manual Dimension Correction"
        )

        default_text = ",".join(
            str(x)
            for x in extracted_dimensions
        )

        manual_text = st.text_area(
            "Add/edit dimensions",
            value=default_text,
            height=120,
        )

        try:

            corrected_dimensions = (
                sorted(
                    list(
                        set(
                            float(x.strip())
                            for x in (
                                manual_text.split(",")
                            )
                            if x.strip()
                        )
                    )
                )
            )

        except Exception:

            st.error(
                "Invalid dimension format."
            )

            st.stop()

        st.success(
            f"{len(corrected_dimensions)} dimensions ready."
        )

        # ---------------------------------------------------
        # REBUILD DATAFRAME
        # ---------------------------------------------------
        debug_df = (
            build_manual_dataframe(
                corrected_dimensions,
                default_tolerance,
            )
        )

        st.subheader(
            "📋 Structured Tolerance Data"
        )

        st.dataframe(
            debug_df,
            use_container_width=True,
        )

    # ---------------------------------------------------
    # RUN WORKFLOW
    # ---------------------------------------------------
    with st.spinner(
        "Running tolerance analysis..."
    ):

        try:

            result = (
                run_automated_workflow(
                    input_path=input_path,
                    output_name=output_name,
                    lower_spec=(
                        lower_spec
                        if use_custom_limits
                        else None
                    ),
                    upper_spec=(
                        upper_spec
                        if use_custom_limits
                        else None
                    ),
                    validation_method=validation_method,
                    llm_model=llm_model,
                    use_llm_extraction=use_llm_extraction,
                    default_tolerance=default_tolerance,
                    ocr_backend=ocr_backend,
                )
            )

        except Exception as exc:

            st.error(
                f"Analysis failed:\n\n{exc}"
            )

            st.stop()

    # ---------------------------------------------------
    # SUCCESS
    # ---------------------------------------------------
    st.success(
        "Analysis completed successfully."
    )

    # ---------------------------------------------------
    # METRICS
    # ---------------------------------------------------
    col1, col2, col3, col4 = (
        st.columns(4)
    )

    col1.metric(
        "Features",
        len(result.structured_data),
    )

    col2.metric(
        "Worst-case Tol.",
        f"{result.stackup_results['worst_case']['total_tolerance']:.4g}",
    )

    col3.metric(
        "RSS Tol.",
        f"{result.stackup_results['rss']['total_tolerance']:.4g}",
    )

    col4.metric(
        "Within Limits",
        (
            "Yes"
            if result.validation_results.get(
                "within_limits",
                False,
            )
            else "No"
        ),
    )

    # ---------------------------------------------------
    # VISUALIZATIONS
    # ---------------------------------------------------
    st.subheader(
        "📊 Analysis Visualizations"
    )

    try:

        graph_paths = (
            result.graph_paths
        )

        graph_configs = [

            (
                "worst_case_vs_rss",
                "Worst-Case vs RSS Comparison",
            ),

            (
                "contribution_ranking",
                "Contribution Ranking Graph",
            ),

            (
                "stackup_analysis",
                "Stack-Up Analysis Visualization",
            ),
        ]

        for key, caption in graph_configs:

            if key in graph_paths:

                st.image(
                    str(graph_paths[key]),
                    caption=caption,
                    use_container_width=True,
                )

    except Exception as exc:

        st.warning(
            f"Could not load graphs:\n{exc}"
        )

    # ---------------------------------------------------
    # STACK-UP RESULTS
    # ---------------------------------------------------
    st.subheader(
        "📐 Stack-Up Results"
    )

    st.json(
        result.stackup_results
    )

    # ---------------------------------------------------
    # OPTIMIZATION
    # ---------------------------------------------------
    st.subheader(
        "⚙️ Optimization Recommendations"
    )

    st.dataframe(
        result.optimized_data,
        use_container_width=True,
    )

    # ---------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------
    st.subheader(
        "✅ Validation"
    )

    st.json(
        result.validation_results
    )

    # ---------------------------------------------------
    # JSON REPORT
    # ---------------------------------------------------
    st.subheader(
        "🧾 JSON Report"
    )

    st.json(
        result.json_report
    )

    # ---------------------------------------------------
    # DOWNLOADS
    # ---------------------------------------------------
    download_col1, download_col2 = (
        st.columns(2)
    )

    with download_col1:

        st.download_button(
            "⬇️ Download JSON Report",
            data=json.dumps(
                result.json_report,
                indent=2,
                default=str,
            ),
            file_name=(
                result.json_report_path.name
            ),
            mime="application/json",
            use_container_width=True,
        )

    with download_col2:

        st.download_button(
            "⬇️ Download Excel Report",
            data=result.excel_report_path.read_bytes(),
            file_name=(
                result.excel_report_path.name
            ),
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

# ---------------------------------------------------
# INITIAL PAGE
# ---------------------------------------------------
else:

    st.info(
        "Upload a tolerance CSV or engineering drawing image to begin."
    )