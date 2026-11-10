"""Optional interactive UI: pip install streamlit pandas; streamlit run app.py"""
import pandas as pd
import streamlit as st
from sales_planning import read_csv, allocate_quotas, performance, summarize, commission, REGION_POTENTIAL, QUARTER_TARGET
from generate_data import ROOT

st.set_page_config(page_title='Sales Operations Intelligence', layout='wide')
st.title('Sales Operations Intelligence')
st.caption("Synthetic Data | Q4 2026 Sales Operations & Revenue Planning")
sellers = read_csv(ROOT / 'data/sellers.csv')
opps = read_csv(ROOT / 'data/opportunities.csv')
st.sidebar.header('Planning assumptions')
target = st.sidebar.number_input('Quarterly bookings target ($M)', min_value=1.0, value=30.0, step=1.0) * 1_000_000
weights = {r: st.sidebar.slider(f'{r} potential', 0.25, 2.0, float(w), 0.05) for r, w in REGION_POTENTIAL.items()}
rate = st.sidebar.slider('Commission rate (%)', 0.0, 20.0, 8.0, 0.5) / 100
accel = st.sidebar.slider('Above-quota accelerator', 1.0, 3.0, 1.5, 0.1)
planned = allocate_quotas(sellers, weights, target)
rows = performance(sellers, opps, planned)
df = pd.DataFrame(rows)
regional = pd.DataFrame.from_dict(summarize(rows), orient='index').reset_index().rename(columns={'index': 'region'})
a, b, c, d = st.columns(4)
a.metric('Quarterly target', f'${target/1e6:,.1f}M')
b.metric('Closed-won bookings', f'${df.actual_bookings_usd.sum()/1e6:,.1f}M')
c.metric('Projected bookings', f'${df.projected_bookings_usd.sum()/1e6:,.1f}M')
d.metric('Actual quota attainment', f'{df.actual_bookings_usd.sum()/target*100:,.1f}%')
st.subheader('Regional quota and bookings')
st.bar_chart(regional.set_index('region')[['quota_usd','actual_bookings_usd','projected_bookings_usd']])
st.dataframe(regional, hide_index=True, use_container_width=True)
st.subheader('Sales compensation scenarios')
comp = pd.DataFrame([{'seller_id': r['seller_id'], 'region': r['region'], 'actual_bookings_usd': r['actual_bookings_usd'],
                      'quota_usd': r['planned_quota_usd'], 'commission_usd': commission(r['actual_bookings_usd'], r['planned_quota_usd'], rate, accel)} for r in rows])
st.metric('Total commission expense (closed-won only)', f'${comp.commission_usd.sum():,.0f}')
st.dataframe(comp, hide_index=True, use_container_width=True)
st.download_button('Download seller performance CSV', df.to_csv(index=False), 'seller_performance.csv', 'text/csv')
st.info('Scenario planning only. Stage probabilities and territory potential are illustrative, not empirically calibrated. Actual bookings are synthetic.')

st.subheader('Contract operations and seller productivity (Phase 3)')
from contract_ops import generate_contracts, analyze_contracts, seller_productivity, route_approval
contracts = generate_contracts(opps)
contract_summary = analyze_contracts(contracts)
x,y,z = st.columns(3)
x.metric('Contracts in workflow', f"{contract_summary['count']:,}")
y.metric('Review duration (synthetic)', f"{contract_summary['avg_review_days']:.1f} days")
z.metric('Blocked contracts', f"{contract_summary['blocked_count']:,}")
st.caption('Contract rules and durations are synthetic, not actual approval events. Thresholds are illustrative.')
st.bar_chart(pd.DataFrame.from_dict(contract_summary['regional'],orient='index')[['avg_review_days']])
st.write('Pending approval queue by function')
st.dataframe(pd.DataFrame([{'approval_step':k,'pending_items':v} for k,v in contract_summary['approval_queue'].items()]),hide_index=True)
contracts_df = pd.DataFrame(contracts)
st.dataframe(contracts_df[['contract_id','region','deal_value_usd','discount_pct','status','review_days','manager_required','finance_required','legal_required']],hide_index=True)
st.download_button('Download synthetic contracts CSV',contracts_df.to_csv(index=False),'contracts.csv','text/csv')
st.subheader('Seller productivity')
productivity_df = pd.DataFrame(seller_productivity(opps,contracts))
st.dataframe(productivity_df,hide_index=True)
st.download_button('Download seller productivity CSV',productivity_df.to_csv(index=False),'seller_productivity.csv','text/csv')

st.subheader('Executive decision intelligence (Phase 4)')
from decision_intelligence import decision_brief, scenario_comparison, approval_record
brief = decision_brief(sellers, opps, contracts, target=target, weights=weights,
                       commission_rate=rate, accelerator=accel)
st.caption('Explainable deterministic decision rules; not a trained AI model. All results are synthetic.')
k = brief['kpis']
e1,e2,e3 = st.columns(3)
e1.metric('Projected attainment',f"{k['projected_attainment_pct']:.1f}%")
e2.metric('Delayed unsigned contracts',str(k['delayed_unsigned_contracts']))
e3.metric('Commission scenario expense',f"${k['commission_expense_usd']/1e6:.2f}M")
st.write('Executive recommendations and evidence')
for rec in brief['recommendations']:
    with st.expander(f"{rec['priority']} | {rec['id']} | {rec['title']}"):
        st.write(rec['rationale'])
        st.json(rec['evidence'])
        st.write('Proposed action:',rec['proposed_action'])
        st.caption('Uncertainty: '+rec['uncertainty'])
st.write('Scenario trade-offs')
st.dataframe(pd.DataFrame(scenario_comparison(sellers,opps,contracts,target=target)),hide_index=True)
st.download_button('Download executive brief JSON',__import__('json').dumps(brief,indent=2),'executive_brief.json','application/json')
st.write('Human decision review (session only)')
selected=st.selectbox('Recommendation', [r['id'] for r in brief['recommendations']])
decision=st.selectbox('Review decision',['Needs evidence','Approved for further review','Rejected'])
reviewer=st.text_input('Reviewer name')
reason=st.text_area('Decision rationale')
if 'decision_reviews' not in st.session_state:
    st.session_state.decision_reviews=[]
if st.button('Record review (no operational action)'):
    try:
        event=approval_record(selected,decision,reviewer,reason,{r['id'] for r in brief['recommendations']})
        st.session_state.decision_reviews.append(event)
        st.success('Review recorded in this session. No action executed.')
    except ValueError as exc:
        st.error(str(exc))
if st.session_state.decision_reviews:
    st.dataframe(pd.DataFrame(st.session_state.decision_reviews),hide_index=True)
    st.download_button('Export review log',__import__('json').dumps(st.session_state.decision_reviews,indent=2),'review_log.json','application/json')
st.warning('Human review logs persist only within the current Streamlit session unless exported. No production audit log or live CRM integration exists.')

st.subheader('Forecast risk stress test (Phase 6)')
from forecast_risk import analyze as forecast_stress_test
st.caption('Hypothetical probability and close-timing adjustments. These are NOT calibrated confidence intervals.')
risk = forecast_stress_test(opps, target=target)
risk_df = pd.DataFrame([{'scenario': name, **values} for name, values in risk['results'].items()])
st.dataframe(risk_df, hide_index=True, use_container_width=True)
st.bar_chart(risk_df.set_index('scenario')[['projected_bookings_usd']])
st.download_button('Download forecast risk report', __import__('json').dumps(risk, indent=2), 'forecast_risk.json', 'application/json')
st.warning('Forecast uncertainty remains unresolved without historical opportunity snapshots, observed conversion outcomes, and backtesting. Do not interpret scenarios as statistical confidence intervals.')

st.subheader('Executive allocation simulation (Phase 7)')
st.caption('Hypothetical initiative costs and impact bands; not measured incremental revenue or causal estimates.')
from executive_simulation import optimize, INITIATIVES, board_pack
budget = st.slider('Discretionary pilot budget ($000)', 0, 800, 350, 10) * 1000
risk_aversion = st.slider('Downside emphasis (0 = upside, 100 = downside)', 0, 100, 50, 5) / 100
allocation = optimize(budget, risk_weight=risk_aversion)
st.dataframe(pd.DataFrame(INITIATIVES),hide_index=True,use_container_width=True)
st.write('Illustrative recommended portfolio:', ', '.join(allocation['recommended']['initiative_ids']) or 'No initiatives')
st.metric('Selected pilot cost',f"${allocation['recommended']['cost_usd']:,.0f}")
st.metric('Assumed impact band',f"${allocation['recommended']['assumed_low_impact_usd']:,.0f} – ${allocation['recommended']['assumed_high_impact_usd']:,.0f}")
st.dataframe(pd.DataFrame([allocation['recommended']]+allocation['alternatives']),hide_index=True,use_container_width=True)
pack=board_pack(opps,budget,risk_aversion)
st.download_button('Download executive decision pack (JSON)',__import__('json').dumps(pack,indent=2),'executive_simulation.json','application/json')
st.warning('Human approval required. Do not add hypothetical intervention uplift to the uncalibrated forecast or treat this as an investment recommendation.')
