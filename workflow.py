from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import pandas as pd

from agents.insight_agent import generate_insights

from agents.json_report_agent import (
    build_json_report,
    generate_json_report,
)

from agents.optimization_agent import (
    optimize_tolerances,
    summarize_optimization,
)

from agents.report_agent import (
    generate_excel_report,
)

from agents.stackup_agent import (
    run_stackup_analysis,
)

from agents.validation_agent import (
    validate_rows,
    validate_stackup,
)

from agents.visualization_agent import (
    generate_all_visualizations,
)

from cv.extraction import (
    extract_tolerances_from_image,
)

from cv.parser import (
    load_tolerance_csv,
    save_structured_data,
)

PROJECT_ROOT = Path(__file__).resolve().parent


@dataclass
class WorkflowResult:
    structured_data: pd.DataFrame
    optimized_data: pd.DataFrame
    stackup_results: dict[str, Any]
    validation_results: dict[str, Any]
    optimization_summary: dict[str, Any]
    insights: str
    extraction_metadata: dict[str, Any]
    excel_report_path: Path
    json_report_path: Path
    json_report: dict[str, Any]
    graph_paths: dict[str, Path]


def derive_default_limits(
    stackup_results: dict[str, object],
    cushion: float = 0.10,
):

    worst_case = stackup_results["worst_case"]

    total_tolerance = (
        worst_case["total_tolerance"]
    )

    nominal = (
        worst_case["nominal_stack"]
    )

    allowance = (
        total_tolerance * (1 + cushion)
    )

    return (
        nominal - allowance,
        nominal + allowance,
    )


def load_structured_input(
    input_path: str | Path,
    llm_model: str = "qwen2.5:7b",
    use_llm_extraction: bool = True,
    default_tolerance: float | None = 0.1,
):

    path = Path(input_path)

    # ==========================================
    # CSV INPUT
    # ==========================================
    if path.suffix.lower() == ".csv":

        df = load_tolerance_csv(path)

        return (
            df,
            {
                "source_type": "csv",
                "source_path": str(path),
            },
        )

    # ==========================================
    # IMAGE INPUT
    # ==========================================
    df, metadata = (
        extract_tolerances_from_image(
            path,
            output_dir=PROJECT_ROOT / "data",
            llm_model=llm_model,
            use_llm=use_llm_extraction,
            default_tolerance=default_tolerance,
        )
    )

    if not df.empty:

        save_structured_data(
            df,
            PROJECT_ROOT
            / "data"
            / f"{path.stem}_structured.csv",
        )

    return df, metadata


def run_automated_workflow(
    input_path: str | Path,
    output_name: str = "tolerance_report",
    lower_spec: float | None = None,
    upper_spec: float | None = None,
    validation_method: str = "worst_case",
    llm_model: str = "qwen2.5:7b",
    use_llm_extraction: bool = True,
    default_tolerance: float | None = 0.1,
):

    # ==========================================
    # LOAD DATA
    # ==========================================
    df, extraction_metadata = (
        load_structured_input(
            input_path=input_path,
            llm_model=llm_model,
            use_llm_extraction=use_llm_extraction,
            default_tolerance=default_tolerance,
        )
    )

    # ==========================================
    # VALIDATE
    # ==========================================
    data_issues = validate_rows(df)

    if data_issues:

        raise ValueError(
            "Input validation failed:\n"
            + "\n".join(data_issues)
        )

    # ==========================================
    # STACKUP
    # ==========================================
    stackup_results = (
        run_stackup_analysis(df)
    )

    # ==========================================
    # VISUALIZATION
    # ==========================================
    graph_paths = (
        generate_all_visualizations(
            structured_data=df,
            stackup_results=stackup_results,
            output_dir=PROJECT_ROOT
            / "reports"
            / "graphs",
        )
    )

    # ==========================================
    # DEFAULT LIMITS
    # ==========================================
    if (
        lower_spec is None
        or upper_spec is None
    ):

        lower_spec, upper_spec = (
            derive_default_limits(
                stackup_results
            )
        )

    # ==========================================
    # OPTIMIZATION
    # ==========================================
    optimized_df = (
        optimize_tolerances(df)
    )

    optimization_summary = (
        summarize_optimization(
            optimized_df
        )
    )
    print("\nOPTIMIZATION TABLE:\n")
    print(optimized_df)
    
    # ==========================================
    # VALIDATION
    # ==========================================
    validation_results = (
        validate_stackup(
            optimized_df,
            lower_spec_limit=lower_spec,
            upper_spec_limit=upper_spec,
            method=validation_method,
        )
    )

    # ==========================================
    # INSIGHTS
    # ==========================================
    insights = generate_insights(
        stackup_results=stackup_results,
        validation_results=validation_results,
        optimization_summary=optimization_summary,
        model=llm_model,
    )

    # ==========================================
    # REPORT PATHS
    # ==========================================
    reports_dir = (
        PROJECT_ROOT / "reports"
    )

    reports_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    base_name = (
        Path(output_name).stem
    )

    excel_path = (
        reports_dir
        / f"{base_name}.xlsx"
    )

    json_path = (
        reports_dir
        / f"{base_name}.json"
    )

    # ==========================================
    # JSON REPORT
    # ==========================================
    report_json = (
        build_json_report(
            raw_data=df,
            stackup_results=stackup_results,
            optimized_data=optimized_df,
            validation_results=validation_results,
            optimization_summary=optimization_summary,
            insights=insights,
            extraction_metadata=extraction_metadata,
        )
    )

    generate_json_report(
        json_path,
        report_json,
    )

    # ==========================================
    # EXCEL REPORT
    # ==========================================
    generate_excel_report(
        output_path=excel_path,
        raw_data=df,
        stackup_results=stackup_results,
        optimized_data=optimized_df,
        validation_results=validation_results,
        insights=insights,
    )

    return WorkflowResult(
        structured_data=df,
        optimized_data=optimized_df,
        stackup_results=stackup_results,
        validation_results=validation_results,
        optimization_summary=optimization_summary,
        insights=insights,
        extraction_metadata=extraction_metadata,
        excel_report_path=excel_path,
        json_report_path=json_path,
        json_report=report_json,
        graph_paths=graph_paths,
    )