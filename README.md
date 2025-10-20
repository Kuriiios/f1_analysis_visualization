🏎️ F1 Report Suite — Automated Session & Season Analysis Generator

This repository hosts the code for an automated Formula 1 Report Suite, built entirely in Python and powered by FastF1 and python-pptx.
The suite’s goal is to generate detailed analytical reports and visual JPEG cards for every aspect of an F1 weekend and beyond — from Free Practice to full Quarter-Season summaries.

Each module automatically fetches, processes, visualizes, and formats telemetry and timing data into professional-grade reports in .pptx, .pdf, and .jpeg formats, combining data precision with clean, F1-style design.

🚨 PROJECT STATUS: MULTI-MODULE PROTOTYPE — ACTIVE DEVELOPMENT 🚧

✅ Prototype Status: Validated Across Multiple Report Types

The architecture and generation logic have been validated across all five modules, confirming that the system can automatically produce accurate and visually consistent reports for each supported session type.

🧩 Available Report Modules
Report Type	Script	Description
🧠 Practice Report Generator	practice_generator.py	Analyzes protocols, pace evolution, tyre degradation, and stint consistency during FP1–FP3.
⚡ Qualifying Report Generator	qualifying_generator.py	Focuses on sector performance, track evolution, lap deltas, and Q1–Q3 time comparisons.
🏁 Race Report Generator	race_generator.py	Produces full race summaries with lap charts, strategy breakdowns, and teammate comparisons.
📊 Quarter-Season Report Generator	quarter_season_generator.py	Aggregates team and driver stats over multiple rounds for medium-term performance insights.
Each generator produces:

.pptx PowerPoint reports

.pdf documents (auto-converted)

.jpeg race cards suitable for sharing or media embedding

🚀 Getting Started
Prerequisites

You’ll need Python ≥ 3.9 and the following packages:
System Requirements

LibreOffice (lowriter) – for .pptx → .pdf conversion

Poppler – for .pdf → .jpeg conversion via pdf2image

⚙️ Workflow Overview

Each generator follows a common data pipeline:

1. Session Selection
Prompts for the year, race round, and session type (FP1, Q, R, or S).

2. Data Retrieval
Fetches all session telemetry via FastF1, using caching for faster re-runs.

3. Analysis Computation
Custom logic modules (utils/race/lap_info.py, utils/race/plots.py) handle:

.Lap filtering and correction

.Pit stop detection

.Pace delta calculation

.Session bests and outliers

4. Figure Generation
Matplotlib is used to create race-style charts for lap time trends, pace comparisons, and tyre usage.

5. Report Assembly
Using python-pptx, each report slide is dynamically built with:

.Team branding and logos

.Driver stats and metrics

.F1-style visual hierarchy and layout

6. Conversion & Export
The system converts .pptx → .pdf → .jpeg via LibreOffice and pdf2image, generating clean, high-resolution cards.

📂 Folder Structure

f1_analysis_visualization/
│
├── data/
│   ├── raw/                    # Login, team colors, raw reference data
│   ├── processed/              # CSV exports
│   └── external/team_logos/
│
├── figures/                    # Session charts
├── reports/                    # Generated .pptx/.pdf/.jpeg outputs
├── cache_folder/               # FastF1 cache
│
├── models_auto/                # Trying to automate the process
├── models/
│   ├── utils/
│   │   ├── practice
│   │   │   ├── lap_info.py
│   │   │   └── plots.py
│   │   ├── qual
│   │   │   ├── lap_info.py
│   │   │   └── plots.py
│   │   ├── race
│   │   │   ├── lap_info.py
│   │   │   └── plots.py
│   │   ├── utils.py
│   │   └── __init__.py
│   │
│   ├── practice_generator.py
│   ├── qualifying_generator.py
│   ├── race_generator.py
│   ├── head2head_generator.py
│   └── quarter_season_generator.py
│
├── LICENSE
├── README.md
└── requirements.txt


📈 Example Usage

python race_generator.py

Prompted workflow:

Year ? 2025
Race Number ? (1-24) 6
Session ? (R, S) R

Output Example:

reports/
└── 06_Monaco_GP_2025/
    └── 06_Race/
        ├── 06_Race0.jpeg
        ├── 06_Race1.jpeg

🔍 Analytical Focus by Module

Module	Focus Area
Practice	Pace evolution, stint analysis, fuel load correction
Qualifying	Sector deltas, Q session comparison, theoretical best laps
Race	Tyre strategy, driver comparison, pit stop breakdowns
Head-to-Head	Driver-vs-driver lap-by-lap performance
Quarter-Season	Multi-event averages, trends, cumulative scoring

🌈 Visual Design Highlights

Official F1 color palette per team

Consistent Formula1 Display typography

Transparent overlay blocks for clean data presentation

Auto-scaled charts and figure placement

High-resolution JPEG exports for social sharing

👨‍💻 Author

Cyril Leconte 📍 Créteil, France
📧 cyril.leconte@proton.me