# Sales Operations Intelligence | Human Systems

## Executive summary
A functional, **synthetic** revenue operations decision-support prototype for a fictional global B2B technology company. It explores how a commercial organization can connect pipeline forecasting, seller quotas, commission economics, contracting bottlenecks and executive recommendations in one governed workflow.

## Business problem
Revenue operations teams often work across fragmented CRM records, quota spreadsheets, compensation policies and deal-desk queues. Leaders need a consistent definition of bookings, transparent assumptions, evidence-linked decisions and an explicit review path.

## Scope and methods
- 80 fictional sellers across North America, EMEA, APAC and LATAM; 2,400 fictional opportunities.
- Quarterly bookings target: $30 million; annual illustrative target: $120 million.
- Deterministic opportunity-level forecast: realized closed-won bookings plus stage-weighted open pipeline, constrained to Q4 2026.
- Capacity/territory-weighted quota allocation; attainment and commission scenarios.
- Synthetic contract approval routing, delays and seller productivity analytics.
- Rule-based recommendations with evidence, caveats and reviewer decisions.
- Reproducible quality checks, automated unit tests and Streamlit dashboard.

## Leadership decisions demonstrated
1. Evaluate pipeline coverage and the sensitivity of target attainment to assumed conversion rates.
2. Assess territory capacity and quota fairness before interpreting low seller attainment.
3. Compare commission accelerator costs without paying commissions on unclosed pipeline.
4. Prioritize delayed contract reviews using documented thresholds and manual validation.
5. Require a human reviewer and rationale before any proposed intervention proceeds.

## Evidence boundaries
**This is a self-initiated portfolio simulation, not professional client delivery.** No Google, SoundCloud or other employer data is used. All company names, sellers, transactions, compensation policies and approval events are fictional. Forecast probabilities are illustrative rather than statistically calibrated. The rules are not a trained AI model; no real contracts are approved and no payments are issued.

## Architecture
`generate_data.py` → CSV fixtures → `forecast.py`, `sales_planning.py`, `contract_ops.py` → `decision_intelligence.py` → `app.py`; `quality.py` audits data integrity and reconciles forecast totals.

## Next production requirements
Historical forecast backtesting and probability calibration; real CRM/HRIS access controls; SSO/RBAC; data contracts and freshness monitoring; signed approval logs; financial/legal review of compensation policies; rollout/adoption metrics; deployment security and observability.
