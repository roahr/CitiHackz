# AI‑Powered CIBIL Score System for Macro‑Finance Businesses

> **Private Repository** — keep this codebase private. 

A production‑ready prototype that evaluates the creditworthiness of MSMEs, startups, and high‑risk enterprises using alternative data, real‑time scoring, and explainable AI. Built for banks, NBFCs and fintechs operating in India and similar markets.

---

## Table of Contents

* [Key Features](#key-features)
* [System Architecture](#system-architecture)
* [Models & Comparisons](#models--comparisons)
* [Explainability (XAI)](#explainability-xai)
* [Regulatory, Ethics & Security](#regulatory-ethics--security)
* [Configuration](#configuration)
* [Running the Services](#running-the-services)
* [Sample Dataset & Seeding](#sample-dataset--seeding)
* [Evaluation & Metrics](#evaluation--metrics)
* [Risk Dashboard (UI)](#risk-dashboard-ui)
* [API Reference](#api-reference)
* [Key Trade‑offs](#key-trade-offs)
* [Testing, Linting & QA](#testing-linting--qa)
* [Reproducibility & Experiment Tracking](#reproducibility--experiment-tracking)
* [Repo Privacy & Access](#repo-privacy--access)
* [Atomic Commits & Branching](#atomic-commits--branching)
* [Roadmap](#roadmap)
* [Contributing](#contributing)
* [License](#license)
* [References](#references)

---

## Key Features

* **AI‑Powered Credit Scoring Engine** using tabular ML (XGBoost/LightGBM/RandomForest) and optional DNNs for sequence features.
* **Alternative Data Ingestion**: banking transactions, GST filings, e‑commerce sales, supplier payments, digital invoices, and public business signals (social/business listings).
* **Real‑time Scoring** via streaming features (Kafka) and in‑memory feature store (Redis/Feast option).
* **Explainable AI**: SHAP‑based global/local attributions, feature contribution charts, reason codes.
* **Risk Segmentation**: clustering (K‑Means/HDBSCAN) for low/medium/high‑risk cohorts.
* **Risk Dashboard**: interactive UI (Streamlit) with trends, score justifications, and alerts.
* **API for Integrations**: RESTful JSON (FastAPI), bearer auth, rate limiting.
* **Compliance‑aware**: RBI digital lending points, model governance artifacts, PII minimization, audit logging.

---

## System Architecture

```
                         +---------------------------+
                         |   External Data Sources   |
                         |  (Banks, GSTN, E‑comm,   |
                         |   Invoices, Suppliers,   |
                         |   Public Business Data)  |
                         +-------------+-------------+
                                       |
                                       v
+------------------+        +---------------------+        +--------------------+
| Ingestion Adapters|-----> |  Raw Data Lake (S3) | -----> |  Feature Pipeline  |
|   ETL)|       |  + PII Vault (KMS)  |        |  (Spark/DBT/SQL)   |
+---------+--------+        +----------+----------+        +---------+----------+
          |                              |                            |
          v                              v                            v
   +------+-------+              +-------+------+             +-------+-------+
   | Validation   |              | Metadata/     |            | Feature Store |
   | (GreatExpect)|              | Lineage (MLMD)|            | (Feast/Redis) |
   +------+-------+              +-------+------+             +-------+-------+
          |                              |                            |
          v                              v                            v
   +------+----------------------+  +-----+------------------+  +-----+------------------+
   |  Training Jobs (MLFlow)     |  |  Registry (Models)    |  |  Real‑time Scoring API |
   |  XGBoost/LGBM/DNN + SHAP    |  |  Versioning & Metrics |  |  (FastAPI, Uvicorn)    |
   +------+----------------------+  +-----+------------------+  +-----+------------------+
          |                                                        |
          v                                                        v
   +------+----------------------+                         +------+-----------------+
   | Batch Scoring (Airflow)     |                         | Risk Dashboard (UI)   |
   | & Monitoring (Evidently)    |                         | Streamlit + REST      |
   +-----------------------------+                         +-----------------------+
```

**Tech choices (default implementation):**

* **API**: FastAPI (Python 3.11)
* **Modeling**: scikit‑learn, xgboost, lightgbm, pytorch (optional)
* **Explainability**: shap
* **Pipelines**: Airflow for batch, lightweight Kafka for stream demo
* **Storage**: Postgres (OLTP), MinIO/S3 (artifacts), Redis (features/cache)
* **Observability**: MLflow (experiments), Evidently (drift), Prometheus/Grafana

---

## Models & Comparisons

We ship baseline models and a comparison harness.

| Family        | Model                         | Typical Use              | Pros                                             | Cons                                      |
| ------------- | ----------------------------- | ------------------------ | ------------------------------------------------ | ----------------------------------------- |
| Tree‑Boosting | **XGBoost** / LightGBM        | Primary score            | High AUC/PR, robust to heterogenous tabular data | Can overfit on leakage; careful CV needed |
| Ensembles     | RandomForest                  | Baseline/benchmark       | Stable, interpretable at feature level           | Larger inference cost                     |
| Linear        | Logistic/ElasticNet           | Challenger, reason codes | Fast, transparent                                | Lower ceiling on complex patterns         |
| Deep          | Simple DNN w/ temporal blocks | Sequences of tx          | Captures dynamics                                | Heavier infra, harder to explain          |

**Default KPIs**

* Discrimination: ROC‑AUC, PR‑AUC
* Calibration: Brier Score, Calibration Curve
* Business: KS\@K, Recall\@Fixed‑FPR, Expected Loss, Approval Uplift
* Regression targets (optional): MAE/RMSE for PD/LGD/EL estimates

---

## Explainability (XAI)

* **Global**: SHAP summary (top features), partial dependence for key drivers.
* **Local**: per‑entity SHAP values with top contributors → exposed via API as *reason codes*.
* **Audit**: store SHAP vectors and model version with the score payload.
* **Fairness checks**: optional parity/dP metrics on proxy groups; flag and document mitigations.

---

## Regulatory, Ethics & Security

* **RBI Digital Lending guidance** alignment (consent, purpose limitation, transparency, grievance redressal).
* **SEBI‑inspired** model governance artifacts (model card, validation report, periodic review).
* **Data**: encryption at rest (S3‑KMS/pgcrypto), TLS in transit, least‑privilege IAM, breach logging.
* **Policy**: no social data without explicit consent; no individual‑level psychometrics; opt‑out pathways.

> ⚠️ This repo is for **research & prototype** use. Production deployment requires formal legal review.

---

## Configuration

All configuration is via environment variables.

`.env.example`

```
APP_ENV=dev
SECRET_KEY=change_me
POSTGRES_URL=postgresql://postgres:postgres@db:5432/score
REDIS_URL=redis://redis:6379/0
S3_ENDPOINT=http://minio:9000
S3_ACCESS_KEY=minio
S3_SECRET_KEY=minio123
MLFLOW_TRACKING_URI=http://mlflow:5000
RATELIMIT_PER_MIN=120
```

---

## Running the Services

**Docker Compose services**

* `api` (FastAPI), `dashboard` (Streamlit), `worker` (batch/cron), `db` (Postgres), `redis`, `minio`, `mlflow`, `evidently`, `grafana`.

Common tasks:

```bash
make up           # start stack
make down         # stop
make seed         # load sample dataset & features
make train        # run training pipeline
make batch_score  # score all entities as of today
make test         # run unit & integration tests
```

---

## Sample Dataset & Seeding

* A synthetic dataset is provided under `data/sample/` with realistic distributions.
* Seed script generates features (rolling cashflow, DSCR proxy, volatility, on‑time pay rate, GST compliance score, returns rate, seasonality indices, sentiment signals).

```bash
python scripts/seed_data.py --entities 5000 --start 2022-01-01 --end 2025-06-30
python scripts/build_features.py --as-of 2025-06-30
```

---

## Evaluation & Metrics

Run the comparison harness:

```bash
python experiments/run_benchmarks.py \
  --models xgb,rf,logreg,lgbm \
  --target default_12m \
  --cv 5 --scoring roc_auc pr_auc ks brier
```

Artifacts:

* `mlruns/` (MLflow): params, metrics, plots, confusion matrices
* `reports/` (Markdown/HTML): model cards, calibration curves, drift checks

**Demo baseline target**: `default_12m` (binary) derived from synthetic repayment flags.

---

## Risk Dashboard (UI)

Launch via Streamlit:

```bash
streamlit run dashboard/App.py
```

Features:

* Portfolio overview (approval rate, PD distribution, losses).
* Entity detail page with **score timeline**, **reason codes**, and **what‑if** feature sliders.
* Monitoring: drift/quality alerts, data freshness, model version banner.

---

## API Reference

OpenAPI docs at `/docs`.

**Score an entity**

```bash
curl -X POST http://localhost:8000/score \
  -H "Authorization: Bearer <token>" \
  -H 'Content-Type: application/json' \
  -d '{"entity_id":"E123", "as_of":"2025-06-30"}'
```

**Batch score**

```bash
curl -X POST http://localhost:8000/score/batch -d '{"as_of":"2025-06-30"}'
```

**Explanations**

```bash
curl http://localhost:8000/explain/E123?as_of=2025-06-30
```

**Clusters**

```bash
curl http://localhost:8000/segments?as_of=2025-06-30
```

**Auth**: Bearer tokens (JWT) with `READ:score` / `WRITE:score` scopes. Rotate keys via env.

---

## Key Trade‑offs

* **Accuracy vs Explainability**: Tree boosting offers strong AUC; linear baselines supply clearer reason codes. We expose both and log explanations per prediction.
* **Real‑time vs Cost**: Redis/Feast + Kafka enables instant scoring; batch Airflow reduces infrastructure cost. Choose per use‑case.
* **Data Breadth vs Privacy**: Alternative data improves coverage but raises compliance burden. Enforce consent and minimization.
* **Generalization vs Tailoring**: Global model is fast to roll out; industry‑specific challengers can improve lift at the cost of complexity.

---

## Testing, Linting & QA

```bash
pytest -q            # tests
ruff check .         # lint
mypy .               # type checks
pre-commit run -a    # all hooks
```

CI (GitHub Actions) runs tests, lint, and builds Docker images on PRs to `main`.

---

## Reproducibility & Experiment Tracking

* **MLflow** for experiments & artifacts
* **Data versioning** via DVC (optional) or dataset snapshot tags
* **Deterministic seeds**: `PYTHONHASHSEED`, `numpy`, `xgboost` seeded
* **Model cards** under `reports/model_cards/` with validation summary

---

## Repo Privacy & Access

* Set repo **Private**: *Settings → General → Danger Zone → Change visibility → Private*.
* Restrict access to specific collaborators and enable **branch protection** on `main`.
* Require PR reviews + passing CI for merges. Disable forking if policy requires.

---

## Atomic Commits & Branching

**Branching model**: trunk‑based with short‑lived feature branches: `feat/xai-shap`, `fix/seed-null`, `exp/xgb-l1`.

**Conventional Commits** (atomic, one logical change per commit):

* `feat(api): add /explain endpoint returning SHAP reason codes`
* `fix(pipeline): guard against null gst_paid in feature builder`
* `perf(model): switch to histogram grower for faster XGBoost`
* `docs(readme): add Windows/WSL notes`
* `test(api): add contract tests for /score`

**PR template** enforces: scope, screenshots, metrics deltas, risk & rollback, checklist.

---

## Roadmap

* [ ] Add LightGBM + CatBoost challengers
* [ ] Add online learning via River for small drifts
* [ ] Integrate Feast as optional feature store module
* [ ] Bias & fairness dashboards with counterfactual tests
* [ ] Model monitoring webhooks to Slack/Teams

---

## Contributing

1. Create a branch from `main`.
2. Ensure atomic commits with Conventional Commit messages.
3. Run tests and linters locally.
4. Open a PR; attach metric deltas & screenshots.

---

## License

Proprietary © YOUR\_ORG. All rights reserved. Not for public redistribution.

---

## References

* TransUnion CIBIL (conceptual reference)
* World Bank: Alternative Credit Scoring (report)
* MIT Sloan: AI in Financial Risk Management
* RBI: India’s Digital Lending Guidelines
* FSB: Open Banking & Credit Models

> See `docs/` for detailed notes and links to the above references, plus regulatory mapping and model cards.
