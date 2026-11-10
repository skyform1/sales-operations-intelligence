# Sales Operations Intelligence

Synthetic, reproducible revenue-operations prototype for the Human Systems GTM Intelligence portfolio.

## Run

```bash
python generate_data.py
python forecast.py
python -m unittest discover -s tests -v
```

Requires Python 3.9+; standard library only. Outputs are generated in `data/` and `outputs/`.

## Model

- Opportunity expected bookings = amount_usd × stage probability, only for open deals with expected close dates in the quarter.
- Closed-won bookings are counted at full value if actual close date is in the quarter.
- Closed-lost deals contribute zero.
- Forecast = closed-won bookings + expected open bookings.
- Targets are quarterly bookings targets, not recognized revenue.
- No double-counting of closed-won deals in open pipeline.

All data and company names are fictional. Probabilities are assumptions, not empirically calibrated forecasts.

## Phase 2: Quotas, territories and compensation

```bash
python sales_planning.py
python -m unittest discover -s tests -v
```

Optional interactive dashboard (requires `pip install streamlit pandas`):

```bash
streamlit run app.py
```

- `sales_planning.py` allocates quarterly bookings quota across sellers by synthetic regional territory potential and capacity, reconciles allocations to the total target, calculates actual vs projected attainment, and simulates commissions on **closed-won bookings only**.
- `app.py` is an interactive Streamlit dashboard with target, territory potential, commission rate, and accelerator controls.
- `outputs/sales_planning.json` and `outputs/seller_performance.csv` contain example results.
- Default commission is 8% through quota and 12% above quota. This is an **illustrative** compensation plan, not Google's policy.

**Limitations:** The synthetic pipeline was generated without calibrated stage probabilities, regional market sizes, time-in-role, ramp schedules, cancellations, clawbacks, multi-year contracts, or actual seller compensation contracts. Quota allocation uses assumed regional indices, not measured territory opportunity. This is a scenario engine, not a validated predictive model or payroll system. A complete production compensation system would need eligibility, crediting, approval and dispute rules.

## Phase 3: Contracting and seller operations

```bash
python contract_ops.py
python -m unittest discover -s tests -v
streamlit run app.py
```

- `contract_ops.py`: deterministic, synthetic contracting scenarios linked to existing opportunities; manager, finance, and legal approval routing; simulated review times and bottleneck metrics.
- `outputs/contracts.csv`, `outputs/contract_ops.json`, `outputs/seller_productivity.csv`: reproducible operational outputs.
- `app.py`: contracting queue, review delays, approval flags, and seller conversion/productivity metrics.
- Contract status, review durations, discount assumptions, and approval flags are **synthetic** and do not represent real contracts, a live workflow, or legal advice. Win rate is calculated on closed opportunities only. The current prototype does not execute approvals or track actual seller tool usage.

## Phase 4: Executive decision intelligence and human review

```bash
python decision_intelligence.py
python -m unittest discover -s tests -v
streamlit run app.py
```

- `decision_intelligence.py` creates an evidence-linked executive brief, regional performance reviews, contract delay triage, commission cost analysis and four scenario comparisons.
- `outputs/executive_brief.json` and `outputs/scenario_comparison.json` are reproducible examples.
- The dashboard allows reviewers to classify recommendations as *Approved for further review*, *Needs evidence*, or *Rejected*, with a mandatory rationale. Reviews are session-only unless exported.
- **This is a deterministic rule-based prototype, not an LLM or trained AI model.** All recommendations require human validation and never trigger external actions.
- **Data-quality warning:** synthetic bookings and quota assumptions produce unrealistically high attainment. Calibrate data, probabilities, and targets before presenting findings as realistic.

## Phase 5: portfolio validation and packaging

The synthetic deal size range is recalibrated to $15k–$95k (previously $10k–$250k), reducing unrealistic quota overattainment. This is **illustrative scenario calibration**, not historical or empirical probability calibration. The generated fixtures and all downstream outputs must be regenerated together.

```bash
python generate_data.py
python forecast.py
python sales_planning.py
python contract_ops.py
python decision_intelligence.py
python quality.py
python -m unittest discover -s tests -v
# Optional UI: pip install -r requirements.txt && streamlit run app.py
```

See `PORTFOLIO_CASE_STUDY.md` for executive framing, evidence boundaries and production gaps. `outputs/quality_report.json` checks IDs, seller references, statuses, positive amounts, quota reconciliation and forecast agreement. No live deployment or production-grade audit trail is claimed.

## Phase 6: forecast stress testing and portfolio credibility

`forecast_risk.py` adds downside/base/upside **sensitivity scenarios**, adjusting uncalibrated stage probabilities and in-quarter close assumptions. This is a transparent business stress test, **not** empirically calibrated probability modeling, confidence intervals, or evidence of forecast accuracy. It prevents a single highly optimistic forecast from being mistaken for a dependable target projection. The Streamlit dashboard includes scenario comparisons and JSON export.

```bash
python forecast_risk.py
python -m unittest discover -s tests -v
streamlit run app.py
```

**Next empirical validation requirements:** Obtain authorized historical CRM snapshots, measure conversion and slippage by stage/region/age, use time-based holdouts, compare forecast error against a simple baseline, and validate with commercial owners. No real customer data is used in this project.

## Phase 7: Executive business simulation and resource trade-offs

Run `python executive_simulation.py`, then `python -m unittest discover -s tests -v`, or launch `streamlit run app.py`.

The executive simulation models five hypothetical interventions with explicit pilot costs, low/high impact assumptions, operational owners, and execution risks. An exhaustive, budget-constrained portfolio comparison ranks feasible combinations using a selectable downside-vs-upside weighting. The dashboard supports scenario exploration and exports a decision pack with approval gates, a measurement plan, and forecast sensitivity from Phase 6.

**Evidence boundaries:** Impact bands are **invented business-case assumptions**, not statistically estimated incremental revenue, actual client results, or Google policies. Portfolio scoring assumes additive effects and ignores implementation dependencies. It is not a causal model. Recommendations do not execute spend or approvals. The decision exercise is designed to demonstrate executive framing and explicit trade-offs, not validated ROI.

## Phase 8: portfolio readiness and verification

Run `python verify_project.py` to regenerate all synthetic data and outputs, execute all 33 unit tests, and display the quality report. See `DEMO_GUIDE.md` for a five-minute executive demonstration and `PHASE8_RELEASE_NOTES.md` for verified and outstanding release gates. Streamlit has **not** been browser-tested or deployed in this release.

## Phase 9: Offline interactive executive demo

Open `executive_demo.html` directly in a browser. See `PHASE9_RELEASE_NOTES.md` for verification status and limitations.
