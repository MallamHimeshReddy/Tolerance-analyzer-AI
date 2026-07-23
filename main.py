from __future__ import annotations

import argparse
import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tolerance_ai_project.workflow import PROJECT_ROOT, run_automated_workflow
from tolerance_ai_project.cv.parser import parse_tolerances_from_text, save_structured_data


def load_input(input_path: Path):
    from tolerance_ai_project.workflow import load_structured_input

    df, _metadata = load_structured_input(input_path)
    return df


def summarize_dataset_command(args: argparse.Namespace) -> Path:
    from tolerance_ai_project.cv.dataset_loader import (
        export_yolo_annotations_csv,
        summarize_dataset,
    )

    import json

    dataset_path = Path(args.dataset_summary)
    summary = summarize_dataset(dataset_path)
    print(json.dumps(summary, indent=2))

    output = Path(args.output)
    if not output.is_absolute():
        output = PROJECT_ROOT / "data" / output

    if summary["dataset_type"] == "yolo":
        return export_yolo_annotations_csv(dataset_path, output)

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return output


def parse_image_folder_command(args: argparse.Namespace) -> Path:
    from tolerance_ai_project.cv.dataset_loader import iter_image_paths

    import pandas as pd

    rows = []
    images = list(iter_image_paths(args.batch_images))
    if args.limit:
        images = images[: args.limit]

    for image_path in images:
        extracted = load_input(image_path)
        if extracted.empty:
            rows.append({"source_image": str(image_path), "feature": "", "nominal": "", "tolerance": ""})
            continue

        extracted = extracted.copy()
        extracted.insert(0, "source_image", str(image_path))
        rows.extend(extracted.to_dict(orient="records"))

    output = Path(args.output)
    if not output.is_absolute():
        output = PROJECT_ROOT / "data" / output
    output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(rows).to_csv(output, index=False)
    return output


def run_workflow(args: argparse.Namespace) -> Path:
    result = run_automated_workflow(
        input_path=args.input,
        output_name=args.output,
        lower_spec=args.lower_spec,
        upper_spec=args.upper_spec,
        validation_method=args.validation_method,
        llm_model=args.llm_model,
        use_llm_extraction=not args.no_llm_extraction,
        default_tolerance=args.default_tolerance,
        ocr_backend=args.ocr_backend,
        custom_ocr_model_path=args.custom_ocr_model,
        custom_ocr_charset_path=args.custom_ocr_charset,
        generate_excel=True,
    )
    print(f"JSON report generated: {result.json_report_path}")
    return result.excel_report_path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="AI-assisted tolerance stack-up analysis and optimization system"
    )
    parser.add_argument("--input", help="Path to an engineering drawing image or CSV")
    parser.add_argument("--dataset-summary", help="Path to an image folder or YOLO dataset to summarize")
    parser.add_argument("--batch-images", help="Path to a folder of drawing images to OCR and parse")
    parser.add_argument("--limit", type=int, default=None, help="Optional image limit for batch processing")
    parser.add_argument("--output", default="tolerance_report.xlsx", help="Excel report output path")
    parser.add_argument("--lower-spec", type=float, default=None, help="Assembly lower specification limit")
    parser.add_argument("--upper-spec", type=float, default=None, help="Assembly upper specification limit")
    parser.add_argument(
        "--validation-method",
        choices=["worst_case", "rss"],
        default="worst_case",
        help="Validation method for final optimized stack-up",
    )
    parser.add_argument(
        "--llm-model",
        default="qwen2.5:7b",
        help="Local Ollama model name, such as qwen2.5:7b or qwen2.5-coder:7b",
    )
    parser.add_argument(
        "--no-llm-extraction",
        action="store_true",
        help="Disable Ollama fallback for image extraction",
    )
    parser.add_argument(
        "--default-tolerance",
        type=float,
        default=0.1,
        help="Assumed tolerance for image dimensions when no explicit tolerance is found",
    )
    parser.add_argument(
        "--ocr-backend",
        choices=["easyocr", "custom_crnn"],
        default="easyocr",
        help="OCR backend for image input",
    )
    parser.add_argument("--custom-ocr-model", help="Path to custom Q-CRNN .pth weights")
    parser.add_argument("--custom-ocr-charset", help="Path to custom Q-CRNN charset JSON/TXT")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    if args.dataset_summary:
        output_path = summarize_dataset_command(args)
        print(f"Dataset summary exported: {output_path}")
        return
    if args.batch_images:
        output_path = parse_image_folder_command(args)
        print(f"Batch OCR data exported: {output_path}")
        return
    if not args.input:
        parser.error("--input is required unless --dataset-summary or --batch-images is used")

    report_path = run_workflow(args)
    print(f"Report generated: {report_path}")


if __name__ == "__main__":
    main()
