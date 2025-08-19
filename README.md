# AI-Powered CIBIL Score System (Hackathon Project)

## 📌 Problem Statement — PS CredTech Hackathon

PUBLIC DEPLOYED LINK : https://citi-hack.vercel.app/

VIDEO EXPLANATION : VIDEO LINK : https://drive.google.com/file/d/1_eOmskEt8ApQt7vPql3zY5LZKIuDb-1Q/view?usp=sharing

In the **macro-finance industry**, traditional CIBIL score systems often fail to accurately assess the creditworthiness of **MSMEs, startups, and emerging enterprises** due to their limited credit history. This creates barriers to financial inclusion and increases risk for lenders.

The challenge is to build an **AI-powered CIBIL-like credit scoring system** that leverages **alternative data, predictive analytics, and explainable AI** to:

* Enhance credit scoring accuracy
* Enable **real-time credit evaluation**
* Predict **loan default risks**
* Ensure **regulatory compliance** (RBI, SEBI, FSB guidelines)
* Improve **financial inclusion** for businesses without traditional credit history

---

## 🎯 Solution Overview — AI-Powered CIBIL Score System

We propose a **comprehensive, AI-driven credit scoring platform** tailored for macro-finance businesses. The solution combines structured financial data, unstructured behavioral insights, and real-time analytics into a **transparent and explainable score**.

### ✅ Core Features

1. **AI-Powered Credit Scoring Engine**

   * ML models: **Random Forest, XGBoost, Neural Networks**
   * Clustering for risk segmentation (low/medium/high risk)
   * Dynamic, real-time scoring

2. **Alternative Data Utilization**

   * GST filings, e-commerce transactions, supplier payments, invoices
   * Banking & UPI transactions
   * Social media, online reviews, and contract analysis via **NLP**

3. **Risk Assessment Dashboard**

   * Visualizations of **financial health, trends, and risks**
   * Instant **credit report generation**
   * Alerts for risk changes

4. **Explainable AI (XAI) Module**

   * Transparent scoring decisions
   * Key indicator highlights
   * Regulatory-ready explanations

5. **Integration APIs**

   * REST APIs for **banks, NBFCs, and fintechs**
   * Seamless embedding into loan approval workflows

---

## 🏗️ System Architecture

```
          ┌───────────────────────┐
          │  Data Sources         │
          │  (Banking, GST, etc.) │
          └──────────┬────────────┘
                     │
             ┌───────▼────────┐
             │ Data Ingestion │
             │ (ETL + APIs)   │
             └───────┬────────┘
                     │
        ┌────────────▼─────────────┐
        │ Feature Engineering      │
        │ (Structured + NLP-based) │
        └────────────┬─────────────┘
                     │
        ┌────────────▼─────────────┐
        │ AI Credit Scoring Engine │
        │ (ML + Predictive Models) │
        └────────────┬─────────────┘
                     │
        ┌────────────▼─────────────┐
        │ Explainable AI (XAI)     │
        │ Justification Layer      │
        └────────────┬─────────────┘
                     │
        ┌────────────▼─────────────┐
        │ Risk Dashboard + APIs    │
        │ (Banks / NBFCs / Fintech)│
        └──────────────────────────┘
```

---
<img width="1824" height="637" alt="Screenshot 2025-03-06 122949" src="https://github.com/user-attachments/assets/1c807176-d5bc-4d74-9ee3-5753593492f1" />


## ⚖️ Key Trade-offs

* **Accuracy vs Explainability**: Neural Networks offer high accuracy but require XAI methods (SHAP, LIME) for transparency.
* **Real-time vs Batch Processing**: Real-time scoring for small enterprises vs batch for large institutional lenders.
* **Data Privacy vs Inclusivity**: Ensure compliance with **RBI & GDPR** while still using alternative data sources.

---

## 📊 Model Comparisons

| Model          | Accuracy | ROC-AUC | Explainability |
| -------------- | -------- | ------- | -------------- |
| Random Forest  | 86%      | 0.89    | High           |
| XGBoost        | 90%      | 0.93    | Medium         |
| Neural Network | 92%      | 0.95    | Low (XAI req.) |

---

## 📈 Impact & Benefits

* ⚡ **Faster Loan Approvals** – Automated decision-making
* 🌍 **Financial Inclusion** – Credit access for underserved MSMEs/startups
* 🛡️ **Reduced Defaults** – Predictive risk monitoring
* 📡 **Scalability** – Usable across banks, NBFCs, and fintechs

<img width="489" height="336" alt="Screenshot 2025-03-07 064644" src="https://github.com/user-attachments/assets/1392461f-9c81-46c6-9ab8-e8288810a5b4" />
---

## 🖥️ Risk Dashboard UI (Prototype)

* Business profile overview
* Credit score visualization (gauge/meter)
* Risk segmentation (low/medium/high)
* Historical trend graph
* Justification panel (key indicators driving score)

---

## 📑 Final Deliverables (Hackathon)

* 🔹 AI-powered CIBIL score system **prototype**
* 🔹 Trained models + evaluation metrics (**ROC-AUC, F1, MAE**)
* 🔹 Risk assessment dashboard (UI + backend)
* 🔹 API documentation (Swagger/OpenAPI)
* 🔹 Hackathon presentation deck + demo
<img width="557" height="646" alt="Screenshot 2025-03-07 065052" src="https://github.com/user-attachments/assets/dcb0ccef-f954-4118-beb7-69aa627580ee" />

---

## 📚 References

1. CIBIL Scoring System – TransUnion CIBIL
2. Alternative Credit Scoring – World Bank Report
3. AI in Financial Risk Management – MIT Sloan
4. Digital Lending Guidelines – RBI
5. Open Banking & Credit Models – FSB
