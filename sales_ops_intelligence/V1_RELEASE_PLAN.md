# Sales Operations Intelligence v1.0 — Release candidate

## Portfolio release scope
- Executive overview: synthetic KPI cards, grouped regional comparison, regional table.
- Revenue & planning: downside/base/upside stress tests and export.
- Sales compensation: attainment and commission scenarios.
- Contracts & sellers: approval routing, queue analysis, productivity.
- Decision intelligence: rule-based recommendations, human review (session-only), investment allocation.

## Verification performed
- Python compilation: passed.
- Existing automated unit tests: 33 passed.
- Streamlit deployment and browser interaction of this release candidate: NOT YET VERIFIED. Do not call this production-ready.

## Deploy update
Upload the CONTENTS of this directory to the GitHub repository root, replacing the existing app.py and requirements.txt. Keep all Python modules and data directories together. Streamlit entry point: app.py, branch: main. Verify app in Firefox and Chrome; test all five tabs, sliders, downloads, chart, approval flow and calculation updates.

## Known limitations
Synthetic CRM data and illustrative probabilities; forecasts not calibrated or backtested. Executive impact estimates are hypothetical. No production persistence, authentication, real CRM integration, or trained AI model. Session-only approval logs.

## Future phase (post portfolio release)
- Production infrastructure: durable storage, auth, observability, CI/CD, security and governance.
- Real CRM integrations: Salesforce/HubSpot or other authorized sources, consent, data mapping and reconciliation.
- Sophisticated AI: validated predictive forecasts, evaluation, model monitoring, explainable interventions and human oversight.

## Release gate
Do not publish final portfolio claims until the updated deployment has been tested end-to-end and screenshots captured.
