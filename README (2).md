# AI-Assisted Tolerance Stack-Up Analysis and Optimization System

This is a complete, achievable Python project for extracting tolerance data from a drawing image or CSV, running stack-up analysis, proposing tolerance optimization actions, validating the result, asking a local Ollama model for engineering insight, and generating a formatted Excel report.

## Project Structure

```text
tolerance_ai_project/
  agents/
    stackup_agent.py
    optimization_agent.py
    validation_agent.py
    insight_agent.py
    report_agent.py
  cv/
    preprocess.py
    ocr.py
    parser.py
  data/
    sample_tolerances.csv
  reports/
  main.py
  requirements.txt
```

## Workflow

```text
Engineering drawing image or CSV
-> OpenCV preprocessing
-> EasyOCR extraction
-> Regex extraction
-> Structured tolerance data
-> Stack-up analysis
-> Optimization
-> Validation
-> Local LLM insights
-> Formatted Excel report
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r tolerance_ai_project/requirements.txt
```

For local AI insight, install Ollama and pull a model:

```bash
ollama pull llama3
```

You can also use Phi3:

```bash
ollama pull phi3
```

## Run With CSV

```bash
python -m tolerance_ai_project.main --input tolerance_ai_project/data/sample_tolerances.csv --output sample_report.xlsx --lower-spec 63.0 --upper-spec 66.0
```

If you are inside the `tolerance_ai_project` folder itself, run:

```bash
python main.py --input data/sample_tolerances.csv --output sample_report.xlsx --lower-spec 63.0 --upper-spec 66.0
```

This now creates both:

```text
reports/sample_report.xlsx
reports/sample_report.json
```

## Run With Drawing Image

```bash
python -m tolerance_ai_project.main --input path/to/drawing.png --output drawing_report.xlsx --llm-model phi3
```

For your local Qwen setup, use:

```bash
python main.py --input path/to/drawing.png --output drawing_report.xlsx --llm-model qwen2.5
```

The image workflow is automated:

```text
image -> OpenCV preprocessing -> EasyOCR -> regex parser
      -> Ollama/Qwen fallback if OCR parsing fails
      -> structured tolerance table -> stack-up analysis
      -> optimization -> validation -> Excel and JSON reports
```

Disable LLM extraction fallback if you want OCR-only behavior:

```bash
python main.py --input path/to/drawing.png --output drawing_report.xlsx --no-llm-extraction
```

## Run The UI

Install dependencies:

```bash
pip install -r requirements.txt
```

Start the clean local web UI:

```bash
streamlit run app.py
```

Open the URL shown by Streamlit, usually:

```text
http://localhost:8501
```

In the UI you can upload a CSV or drawing image, choose spec limits, choose `qwen2.5`, run the complete workflow, then download the JSON and Excel reports.

## Optional Custom Q-CRNN OCR

Your earlier Q-CRNN + BiLSTM OCR architecture can be reused for engineering dimension OCR, but the Sanskrit-trained weights should be retrained or fine-tuned on dimension crops.

Generate synthetic dimension OCR data:

```bash
python tools/generate_dimension_ocr_dataset.py --output data/dimension_ocr_synthetic --train-count 3000 --val-count 500
```

Install optional Q-CRNN dependencies:

```bash
pip install -r requirements-custom-ocr.txt
```

Train from scratch:

```bash
python tools/train_dimension_qcrnn.py --epochs 20 --batch-size 8 --output models/best_qcrnn_dimensions.pth
```

Fine-tune from your old OCR weights where compatible:

```bash
python tools/train_dimension_qcrnn.py --pretrained path/to/best_qcrnn.pth --epochs 20 --output models/best_qcrnn_dimensions.pth
```

Test one crop:

```bash
python tools/predict_dimension_qcrnn.py --image data/dimension_ocr_synthetic/val/val_00000.png --model models/best_qcrnn_dimensions.pth
```

Use the trained model in the main project:

```bash
python main.py --input path/to/drawing_crop.png --ocr-backend custom_crnn --custom-ocr-model models/best_qcrnn_dimensions.pth --custom-ocr-charset data/dimension_ocr_synthetic/dimension_charset.json --output qcrnn_report.xlsx
```

In the Streamlit UI, select `custom_crnn` under OCR backend and provide the model and charset paths.

OCR works best when the drawing includes readable text like:

```text
Base plate length 50.0 +/- 0.20
Spacer thickness 12.0 ± 0.10
```

## CSV Format

Required columns:

```csv
feature,nominal,tolerance,direction
Base plate length,50.0,0.20,1
Bearing seat offset,8.0,0.05,-1
```

`direction` is optional and defaults to `1`. Use `-1` for dimensions that subtract from the stack.

## Using The Two Downloaded Datasets

Use both datasets, but for different jobs:

- `archive (1).zip`: full engineering drawing JPGs. Use this for OCR demonstrations and end-to-end drawing parsing.
- `archive.zip`: Roboflow YOLO annotation dataset with `dt` and `text` classes. Use this to train or evaluate a detector that finds dimension/tolerance text regions before OCR.

Recommended folder layout:

```text
data/
  raw_datasets/
    archive_1/
      Adapter 278914103838.jpg
      ...
    archive_yolo/
      Drawing_Annotation_Recognition8.v1i.yolov12/
        data.yaml
        train/
        valid/
        test/
```

Summarize the full drawing image dataset:

```bash
python main.py --dataset-summary data/raw_datasets/archive_1 --output archive_1_summary.json
```

Summarize and export the YOLO annotation dataset:

```bash
python main.py --dataset-summary data/raw_datasets/archive_yolo/Drawing_Annotation_Recognition8.v1i.yolov12 --output yolo_annotations.csv
```

Run OCR parsing over a folder of images:

```bash
python main.py --batch-images data/raw_datasets/archive_1 --output archive_1_extracted_tolerances.csv
```

Run OCR parsing over only a few images for quick testing:

```bash
python main.py --batch-images data/raw_datasets/archive_1 --output quick_ocr_test.csv --limit 2
```

Best pipeline with both datasets:

```text
YOLO dataset -> train text/dimension detector -> crop detected annotation regions
Full drawing dataset -> OCR each crop -> regex tolerance parser
Parsed CSV -> stack-up analysis -> optimization -> validation -> Excel report
```

## 4-Day Implementation Plan

Day 1: CSV workflow, stack-up math, and basic validation.

Day 2: OpenCV preprocessing, EasyOCR extraction, and regex parsing.

Day 3: Optimization rules, Ollama prompts, and Excel reporting.

Day 4: Test with real drawings, tune regex patterns, and refine report formatting.
