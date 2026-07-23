# AI-Assisted Automated Tolerance Stack-Up Analysis and Optimization System

## Overview

The AI-Assisted Automated Tolerance Stack-Up Analysis and Optimization System is an intelligent manufacturing analysis platform that automates engineering tolerance analysis, stack-up calculations, tolerance optimization, validation, and report generation.

The system combines Computer Vision (OCR), AI Agents, engineering calculations, statistical stack-up analysis, visualization, and Local Large Language Models (LLMs) to analyze engineering drawings or structured CSV files and generate comprehensive engineering reports with optimization recommendations.

---

# Features

## Input Support

- Engineering Drawing Images (PNG, JPG, JPEG)
- Structured CSV Files
- Automatic OCR-based Dimension Extraction
- Manual Dimension Correction
- Local LLM Assisted Extraction (Ollama)

---

## Computer Vision Module

The Computer Vision module automatically extracts engineering dimensions and tolerances from technical drawings.

### Supported OCR Backends

- EasyOCR
- PaddleOCR (Optional)

### Functions

- Image preprocessing
- Noise removal
- OCR extraction
- Dimension detection
- Tolerance parsing
- Structured data generation

---

# AI Agents

## 1. Insight Agent

### Responsibilities

- Generates engineering insights
- Explains stack-up results
- Explains optimization decisions
- Uses Local LLM (Ollama)

---

## 2. Stack-Up Agent

### Performs

- Worst Case Stack-Up Analysis
- Root Sum Square (RSS) Analysis
- Contribution Ranking
- Stack-Up Calculations

### Outputs

- Total Nominal Stack
- Total Worst Case Stack
- RSS Stack-Up
- Individual Dimension Contributions

---

## 3. Optimization Agent

Automatically

- Identifies high-contribution dimensions
- Suggests tolerance tightening
- Suggests tolerance relaxation
- Generates optimized tolerances
- Creates engineering recommendations for every dimension

### Output

Each dimension includes

- Dimension Name
- Nominal Value
- Current Tolerance
- Upper Limit
- Lower Limit
- Tolerance Range
- Optimization Recommendation
- Suggested Optimized Tolerance
- Priority Level

---

## 4. Validation Agent

### Validates

- Input dimensions
- Missing values
- Invalid tolerances
- Engineering limits
- Optimized stack-up

### Supports

- Worst Case Validation
- RSS Validation

---

## 5. JSON Report Agent

Creates machine-readable reports containing

- Extraction Metadata
- Structured Dimensions
- Stack-Up Analysis
- Validation Results
- Contribution Ranking
- Dimension-wise Optimization Recommendations
- Engineering Insights

---

## 6. Excel Report Agent

Generates a professional engineering report containing

- Structured Data
- Stack-Up Summary
- Contribution Ranking
- Dimension Optimization Table
- Validation Results
- Engineering Insights
- Graph References

---

## 7. Visualization Agent

Automatically generates

- Worst Case vs RSS Comparison Graph
- Contribution Ranking Graph
- Stack-Up Analysis Visualization
- Optimization Recommendation Graphs

---

# Workflow

```
Engineering Drawing / CSV

        │

        ▼

Input Validation

        │

        ▼

OCR Extraction (if image)

        │

        ▼

Dimension Parsing

        │

        ▼

Structured Engineering Data

        │

        ▼

Worst Case Stack-Up Analysis

        │

        ▼

RSS Stack-Up Analysis

        │

        ▼

Contribution Ranking

        │

        ▼

Tolerance Optimization

        │

        ▼

Engineering Validation

        │

        ▼

LLM Engineering Insights

        │

        ▼

Excel Report
JSON Report
Visualization Graphs
```

---

# Project Structure

```
tolerance_ai_project/

│

├── agents/

│   ├── insight_agent.py

│   ├── stackup_agent.py

│   ├── optimization_agent.py

│   ├── validation_agent.py

│   ├── report_agent.py

│   ├── json_report_agent.py

│   └── visualization_agent.py

│

├── cv/

│   ├── extraction.py

│   ├── preprocess.py

│   ├── parser.py

│   └── ocr.py

│

├── data/

│   ├── uploads/

│   └── processed/

│

├── reports/

│   ├── graphs/

│   ├── *.xlsx

│   └── *.json

│

├── workflow.py

├── app.py

├── requirements.txt

└── README.md
```

---

# Technologies Used

### Programming

- Python

### Computer Vision

- OpenCV
- EasyOCR
- PaddleOCR

### Data Processing

- Pandas
- NumPy

### Visualization

- Matplotlib

### Excel Reports

- OpenPyXL

### User Interface

- Streamlit

### Artificial Intelligence

- Ollama
- Qwen 2.5
- Llama 3

---

# Installation

Clone the repository

```bash
git clone <repository_url>
cd tolerance_ai_project
```

Create Virtual Environment

```bash
python -m venv venv
```

Activate Environment

Windows

```bash
venv\Scripts\activate
```

Linux / macOS

```bash
source venv/bin/activate
```

Install Dependencies

```bash
pip install -r requirements.txt
```

Install EasyOCR

```bash
pip install easyocr
```

(Optional)

Install PaddleOCR

```bash
pip install paddleocr paddlepaddle
```

Install Ollama

Download from

https://ollama.com

Pull Model

```bash
ollama pull qwen2.5:7b
```

Run Ollama

```bash
ollama serve
```

---

# Running the Project

```bash
streamlit run app.py
```

Open

```
http://localhost:8501
```

---

# Supported Inputs

## CSV

Required Columns

| Column | Description |
|----------|-------------|
| feature | Dimension Name |
| nominal | Nominal Value |
| tolerance | Symmetric Tolerance |
| direction | +1 / -1 |

---

## Engineering Drawings

Supported Formats

- PNG
- JPG
- JPEG

---

# Generated Reports

## Excel Report

Contains

- Structured Engineering Data
- Worst Case Summary
- RSS Summary
- Contribution Ranking
- Dimension Optimization Table
- Validation Results
- Engineering Insights
- Generated Graphs

---

## JSON Report

Contains

- Metadata
- Structured Dimensions
- Stack-Up Results
- Validation Results
- Contribution Ranking
- Optimization Recommendations
- Engineering Insights

---

# Optimization Strategy

Each engineering dimension is evaluated individually.

For every dimension, the system calculates

- Nominal Dimension
- Current Tolerance
- Upper Limit
- Lower Limit
- Total Range
- Contribution Percentage
- Priority
- Suggested Optimized Tolerance
- Engineering Recommendation

Possible recommendations include

- Tighten tolerance
- Relax tolerance
- Maintain current tolerance

---

# Stack-Up Analysis Methods

## Worst Case Method

Assumes every dimension reaches its maximum allowable tolerance simultaneously.

Used for

- Aerospace
- Medical Devices
- Critical Manufacturing

---

## RSS Method

Uses Root Sum Square statistical analysis assuming independent dimensional variation.

Used for

- Automotive Manufacturing
- High Volume Production
- Consumer Electronics

---

# Future Enhancements

- GD&T Symbol Recognition
- PDF Drawing Support
- CAD Model Integration
- Multi-page Engineering Drawings
- Deep Learning OCR Models
- Reinforcement Learning Optimization
- Digital Twin Integration
- Manufacturing Cost Prediction
- ERP Integration
- Cloud Deployment

---

# Authors

Developed by M Himesh Reddy **B.Tech Artificial Intelligence Major Project**

**Project Title**

**AI-Assisted Automated Tolerance Stack-Up Analysis and Optimization System**

---

# License

This project is intended for **academic, research, and educational purposes only.**
