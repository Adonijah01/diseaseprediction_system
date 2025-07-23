# Nairobi Hospital Disease Prediction System

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


