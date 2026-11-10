# Sales Operations Intelligence | Executive demonstration guide

**Portfolio project, Human Systems.** All company names, opportunities, sellers, budgets and outcomes are fictional. The decision engine is rule-based; it is not a trained AI model.

## 5-minute walkthrough

1. **Business question (30 seconds):** A fictional global commercial organization needs to meet a $30M quarterly bookings target while managing uneven seller performance, contract approval delays and constrained investment capacity.
2. **Revenue forecast (60 seconds):** Show closed-won bookings versus projected bookings. Emphasize that actual attainment (87.28%) is grounded in simulated closed-won records; projected attainment (200.83%) is not calibrated and must not be described as a dependable prediction.
3. **Quota and compensation (60 seconds):** Explain seller-level quota allocation, attainment, and the commission accelerator scenario. Discuss why compensation crediting, ramp, clawbacks and payout approvals would be necessary in production.
4. **Contract operations (60 seconds):** Demonstrate synthetic approval routing, review delays and bottleneck detection. Show the decision trade-off between reducing approval time and maintaining legal/finance controls.
5. **Executive trade-off (60 seconds):** Compare investments under a fixed budget and explain how assumptions, downside risks, and approval requirements shape recommendations.
6. **Governance (30 seconds):** Show human review statuses and rationale. Explain that approvals do not execute real business actions.

## Leadership decision prompt

**Question:** Should leadership prioritize deal desk redesign or seller enablement this quarter?

**Approach:** Establish baseline metrics; identify root causes and affected segments; estimate cost, implementation capacity and impact ranges; stress-test scenarios; propose a controlled pilot; obtain legal/finance/business-owner approval; define leading and lagging KPIs; review results before scaling.

**Caveat:** Illustrative impact ranges are assumptions, not measured ROI.

## Interview positioning

This project demonstrates applied knowledge of sales operations mechanics and analytical judgment. It does not replace professional experience in a live sales operations organization. Professional achievements at SoundCloud, Meta, consulting and No Shade must be presented separately.

## Technical verification

From this directory run `python verify_project.py`. To launch the optional interface, install `pip install -r requirements.txt` and run `streamlit run app.py`. Interactive browser testing, security testing, historical backtesting and cloud deployment are not yet complete.
