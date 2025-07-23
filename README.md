# Nairobi Hospital Disease Prediction System

**School of Technology**  
**Bachelor of Science in Data Science**  
**NAME:** Cherotich Laura  
**REG NO:** 23/08450  
**SUPERVISOR:** Ernest Madara

---

## Project Overview
This web application predicts the likelihood of several diseases (Diabetes, Heart Disease, Parkinson's Disease) using machine learning models. It is designed to support healthcare workers at Nairobi Hospital by suggesting likely conditions based on patient symptoms, saving time and improving decision-making.

## Table of Contents
- [Background](#background)
- [Problem Statement](#problem-statement)
- [Objectives](#objectives)
- [Literature Review](#literature-review)
- [Methodology](#methodology)
- [Development Methodology](#development-methodology)
- [Budget and Resources](#budget-and-resources)
- [Project Schedule](#project-schedule)
- [References](#references)
- [Usage](#usage)
- [Installation](#installation)

## Background
Nairobi Hospital is a leading healthcare facility in East Africa, but faces challenges in diagnosing many patients quickly and accurately due to high patient numbers and complex diseases. This system uses data science and machine learning to analyze symptoms and predict possible diseases, supporting healthcare workers in diagnosis.

## Problem Statement
Many diseases share similar symptoms, making diagnosis difficult, especially in high-pressure environments. This can lead to misdiagnosis, delayed treatment, and increased patient risk. There is a need for a smart tool to assist medical staff in predicting diseases quickly and accurately.

## Objectives
**Main Objective:**
- Develop a machine learning-based system to predict diseases from patient symptoms for Nairobi Hospital.

**Specific Objectives:**
- Collect and prepare patient data
- Identify patterns between symptoms and diseases
- Train/test ML models for prediction
- Build an interactive interface for symptom entry and predictions
- Evaluate system accuracy and usefulness

## Literature Review
- Machine learning has been used globally for disease prediction (e.g., IBM Watson, DeepMind).
- In Kenya, AI in hospitals is growing, but local disease prediction tools are rare.
- This project uses local data and focuses on diseases relevant to Nairobi Hospital.

## Methodology
- **Data Collection:** Anonymized patient records from Nairobi Hospital
- **Preprocessing:** Clean and prepare data
- **EDA:** Analyze symptom-disease relationships
- **Model Training:** Use algorithms like Decision Trees, Random Forest
- **Evaluation:** Metrics like accuracy, precision, recall
- **Interface:** Simple front-end for symptom input and predictions

## Development Methodology
Agile approach in four phases:
1. Data gathering and cleaning
2. Model development and testing
3. User interface building
4. Final integration, testing, documentation

## Budget and Resources
| Item                      | Description                  | Estimated Cost | Actual Cost |
|---------------------------|------------------------------|---------------|-------------|
| Laptop (existing)         | Development/testing          | Ksh.0         | Ksh.0       |
| Internet access           | Research/development         | Ksh.          | Ksh.        |
| External storage/backup   | Flash drive/cloud storage    | Ksh.          | Ksh.        |
| Software (Python, Jupyter)| Free open-source tools       | Ksh.0         | Ksh.0       |
| Printing & Binding        | Final report                 | Ksh.          | Ksh.        |
| **Total**                 |                              | Ksh.          | Ksh.        |

## Project Schedule
| Task No. | Description                              | Start Date | Completion Date |
|----------|------------------------------------------|------------|-----------------|
| 1        | Proposal writing and submission           |            |                 |
| 2        | Approval and planning                    |            |                 |
| 3        | Data collection from Nairobi Hospital     |            |                 |
| 4        | Data cleaning and preprocessing          |            |                 |
| 5        | Exploratory Data Analysis                |            |                 |
| 6        | Software Requirement Specification (SRS) |            |                 |
| 7        | Software Design Specification (SDS)      |            |                 |
| 8        | Model development and training           |            |                 |
| 9        | Model evaluation and refinement          |            |                 |
| 10       | User Interface design and development    |            |                 |
| 11       | System integration and final testing     |            |                 |
| 12       | Report writing, documentation, submission|            |                 |

## References
- Shrestha & Chatterjee (2019): HDP model for disease prediction
- Srivastava & Singh (2022): ML framework for common diseases
- Jindal et al. (2021): Model for effective treatment with fewer tests
- Heller et al. (1984): Predictive value in coronary heart disease
- Cáceres & Paccanaro (2019): ChADoGAN for disease gene prediction

## Usage
1. Activate your virtual environment:
   ```
   .\venv\Scripts\activate
   ```
2. Install requirements:
   ```
   pip install -r requirements.txt
   ```
3. Run the app:
   ```
   streamlit run src/app.py
   ```

## Installation
See [Usage](#usage) above.


