import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from engine import (
    EMISSION_FACTORS_KG,
    MATERIAL_FACTORS_KG,
    TCE_FACTORS_KG,
    TRANSPORT_FACTORS_KG,
    boiler_efficiency,
    carbon_cost_curve,
    compute_emissions,
    compute_energy_tce,
    compute_intensity,
    esg_report,
    generate_diagnosis_report,
    heat_recovery,
    lca_footprint,
    macc_curve,
    optimization_strategy,
    quota_position,
    recommendations,
    scope3_breakdown,
    vpp_optimization,
    what_if_projection,
)


st.set_page_config(
    page_title="企业碳排放与能效管理计算平台",
    page_icon="🌱",
    layout="wide",
)

ENERGY_LABELS = {
    "electricity_kwh": "工业用电（kWh）",
    "natural_gas_m3": "天然气（m³）",
    "bituminous_coal_t": "烟煤（吨）",
    "anthracite_coal_t": "无烟煤（吨）",
    "gasoline_l": "汽油（升）",
    "diesel_l": "柴油（升）",
}

SCOPE_LABELS = {
    "natural_gas_m3": "天然气",
    "bituminous_coal_t": "烟煤",
    "anthracite_coal_t": "无烟煤",
    "gasoline_l": "汽油",
    "diesel_l": "柴油",
}


st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, 'Segoe UI', 'Microsoft YaHei', sans-serif;
    }

    .stApp {
        background: #FAFAFA;
        color: #333333;
    }

    #MainMenu, footer,
    [data-testid="stDecoration"],
    [data-testid="stDeployButton"] {
        visibility: hidden;
        display: none;
    }
    header[data-testid="stHeader"] {
        background: transparent;
        border-bottom: none;
        box-shadow: none;
    }

    section[data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E5E7EB;
    }
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: #2E7D32;
    }

    h1, h2, h3 {color: #2E7D32; letter-spacing: -0.01em;}
    p, label, .stCaption {color: #6B7280;}

    .block-container {padding-top: 2rem; padding-bottom: 3rem; max-width: 1200px;}

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 12px;
        border-radius: 8px;
        border: 1px solid #D7E9D8;
        background: #F0F7F0;
        color: #2E7D32;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .status-dot {
        width: 7px; height: 7px; border-radius: 50%;
        background: #2E7D32;
    }

    .kpi-card {
        background: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 10px;
        padding: 18px 20px 16px;
        min-height: 128px;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04), 0 8px 24px rgba(16, 24, 40, 0.04);
    }
    .kpi-label {
        color: #6B7280;
        font-size: 0.8rem;
        font-weight: 600;
        margin-bottom: 8px;
    }
    .kpi-value {
        color: #111827;
        font-size: 1.7rem;
        font-weight: 700;
        line-height: 1.15;
        letter-spacing: -0.01em;
    }
    .kpi-unit {
        color: #9CA3AF;
        font-size: 0.78rem;
        font-weight: 500;
        margin-left: 4px;
    }
    .kpi-delta {
        margin-top: 10px;
        font-size: 0.76rem;
        font-weight: 500;
        color: #6B7280;
    }
    .kpi-delta.up {color: #2E7D32;}
    .kpi-delta.down {color: #B45309;}

    div[data-testid="stMetricValue"] {color: #2E7D32;}
    div[data-testid="stMetricLabel"] {color: #6B7280;}

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        border-bottom: none;
        flex-wrap: wrap !important;
        height: auto !important;
        max-height: none !important;
        overflow: visible !important;
        white-space: normal !important;
        margin-top: 8px;
        padding-top: 18px;
        border-top: 1px solid #E5E7EB;
    }
    [data-baseweb="tab-list"],
    [role="tablist"] {
        flex-wrap: wrap !important;
        height: auto !important;
        max-height: none !important;
        overflow: visible !important;
        white-space: normal !important;
    }
    [data-baseweb="tabs"],
    [data-testid="stTabs"],
    [data-testid="stTabs"] > div {
        overflow: visible !important;
    }
    .stTabs [data-baseweb="tab-list"] > button,
    [role="tablist"] > button {
        flex: 0 0 auto !important;
        white-space: nowrap !important;
    }
    .stTabs [data-baseweb="tab"] {
        color: #6B7280;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        background: #FFFFFF;
        padding: 8px 16px;
        margin: 0 0 6px;
        box-shadow: 0 1px 2px rgba(16, 24, 40, 0.04);
        transition: background-color 0.15s ease, color 0.15s ease, transform 0.08s ease;
    }
    .stTabs [data-baseweb="tab"]:hover {
        background: #F0F7F0;
        color: #2E7D32;
    }
    .stTabs [data-baseweb="tab"]:active {
        transform: scale(0.97);
    }
    .stTabs [aria-selected="true"] {
        color: #2E7D32;
        background: #F0F7F0;
        border-color: #2E7D32;
    }

    .stButton > button {
        border-radius: 6px;
        border: 1px solid #E5E7EB;
        background: #FFFFFF;
        color: #374151;
        transition: all 0.15s ease;
    }
    .stButton > button:hover {
        border-color: #A5C9A8;
        color: #2E7D32;
    }
    .stButton > button:active {
        transform: translateY(1px) scale(0.99);
        background: #F0F7F0;
        border-color: #2E7D32;
    }

    div[data-baseweb="input"] > div,
    div[data-baseweb="select"] > div {
        background: #FFFFFF;
        border-color: #E5E7EB;
        border-radius: 6px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _kpi_card(label, value, unit="", delta="", trend=""):
    delta_html = ""
    if delta:
        if trend == "up":
            arrow = "▲"
        elif trend == "down":
            arrow = "▼"
        else:
            arrow = "•"
        delta_html = f'<div class="kpi-delta {trend}">{arrow} {delta}</div>'
    return st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}<span class="kpi-unit">{unit}</span></div>
            {delta_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def _sample_values():
    return {
        "company": "示例制造企业",
        "industry": "装备制造",
        "electricity_kwh": 4200000.0,
        "natural_gas_m3": 260000.0,
        "bituminous_coal_t": 0.0,
        "anthracite_coal_t": 0.0,
        "gasoline_l": 38000.0,
        "diesel_l": 65000.0,
        "annual_output_wan": 18500.0,
        "product_output_t": 9000.0,
    }


PRESETS = {
    "典型燃气热电厂": {
        "company": "某燃气热电厂",
        "industry": "其他",
        "electricity_kwh": 8600000.0,
        "natural_gas_m3": 4800000.0,
        "bituminous_coal_t": 0.0,
        "anthracite_coal_t": 0.0,
        "gasoline_l": 9000.0,
        "diesel_l": 15000.0,
        "annual_output_wan": 42000.0,
        "product_output_t": 0.0,
    },
    "电子制造工厂": {
        "company": "某电子制造工厂",
        "industry": "通用制造",
        "electricity_kwh": 6200000.0,
        "natural_gas_m3": 420000.0,
        "bituminous_coal_t": 0.0,
        "anthracite_coal_t": 0.0,
        "gasoline_l": 22000.0,
        "diesel_l": 8000.0,
        "annual_output_wan": 26000.0,
        "product_output_t": 3500.0,
    },
    "大型商场": {
        "company": "某大型商业综合体",
        "industry": "其他",
        "electricity_kwh": 3800000.0,
        "natural_gas_m3": 180000.0,
        "bituminous_coal_t": 0.0,
        "anthracite_coal_t": 0.0,
        "gasoline_l": 5000.0,
        "diesel_l": 3000.0,
        "annual_output_wan": 12000.0,
        "product_output_t": 0.0,
    },
}


def _build_consumption():
    return {
        "electricity_kwh": st.session_state.get("electricity_kwh", 0.0),
        "natural_gas_m3": st.session_state.get("natural_gas_m3", 0.0),
        "bituminous_coal_t": st.session_state.get("bituminous_coal_t", 0.0),
        "anthracite_coal_t": st.session_state.get("anthracite_coal_t", 0.0),
        "gasoline_l": st.session_state.get("gasoline_l", 0.0),
        "diesel_l": st.session_state.get("diesel_l", 0.0),
    }


def _clear_data():
    for key in [
        "electricity_kwh",
        "natural_gas_m3",
        "bituminous_coal_t",
        "anthracite_coal_t",
        "gasoline_l",
        "diesel_l",
        "annual_output_wan",
        "product_output_t",
    ]:
        st.session_state[key] = 0.0


def _load_preset():
    choice = st.session_state.get("preset_choice", "自定义")
    if choice in PRESETS:
        for key, value in PRESETS[choice].items():
            st.session_state[key] = value


with st.sidebar:
    st.header("企业基础信息")
    company = st.text_input("企业名称", value=st.session_state.get("company", ""))
    industry = st.selectbox(
        "所属行业",
        ["通用制造", "装备制造", "食品饮料", "化工", "建材", "纺织", "其他"],
        index=0,
        key="industry",
    )

    st.header("生产规模")
    annual_output_wan = st.number_input(
        "企业年产值（万元）",
        min_value=0.0,
        step=100.0,
        key="annual_output_wan",
    )
    product_output_t = st.number_input(
        "产品产量（吨）",
        min_value=0.0,
        step=10.0,
        key="product_output_t",
    )

    st.header("能源消耗数据")
    st.caption("单位：按侧边栏标注填写，按年统计")
    energy_widgets = {
        "electricity_kwh": st.number_input(
            "工业用电（kWh）",
            min_value=0.0,
            step=1000.0,
            key="electricity_kwh",
        ),
        "natural_gas_m3": st.number_input(
            "天然气（m³）",
            min_value=0.0,
            step=100.0,
            key="natural_gas_m3",
        ),
        "bituminous_coal_t": st.number_input(
            "烟煤（吨）",
            min_value=0.0,
            step=1.0,
            key="bituminous_coal_t",
        ),
        "anthracite_coal_t": st.number_input(
            "无烟煤（吨）",
            min_value=0.0,
            step=1.0,
            key="anthracite_coal_t",
        ),
        "gasoline_l": st.number_input(
            "汽油（升）",
            min_value=0.0,
            step=100.0,
            key="gasoline_l",
        ),
        "diesel_l": st.number_input(
            "柴油（升）",
            min_value=0.0,
            step=100.0,
            key="diesel_l",
        ),
    }

    st.selectbox(
        "场景预设（Demo）",
        ["自定义"] + list(PRESETS.keys()),
        index=0,
        key="preset_choice",
    )
    col_a, col_b = st.columns(2)
    col_a.button("载入预设", on_click=_load_preset, width="stretch")
    col_b.button("清空数据", on_click=_clear_data, width="stretch")


consumption = _build_consumption()
emissions = compute_emissions(consumption)
energy = compute_energy_tce(consumption)
intensity = compute_intensity(consumption, annual_output_wan, product_output_t)
advice = recommendations(emissions)

st.markdown(
    """
    <div style="display:flex; align-items:flex-start; justify-content:space-between; gap:16px; flex-wrap:wrap;">
        <div>
            <div style="color:#2E7D32; font-size:0.76rem; font-weight:600; letter-spacing:0.14em; margin-bottom:6px;">ECO-TECH CARBON SUITE</div>
            <h1 style="margin:0; color:#111827; font-size:1.85rem;">企业碳排放与能效管理计算平台</h1>
            <p style="margin:8px 0 24px; color:#6B7280;">碳排放自动核算 · 能效对标 · 余热回收潜力 · 碳价敏感性分析</p>
        </div>
        <div class="status-pill"><span class="status-dot"></span>系统运行正常 · 碳核算引擎 v2.1</div>
    </div>
    """,
    unsafe_allow_html=True,
)

tab_account, tab_heat, tab_boiler, tab_carbon, tab_sandbox, tab_vpp, tab_lca, tab_esg, tab_docs = st.tabs(
    [
        "碳盘查与能效分析",
        "工业余热回收与热力学诊断",
        "锅炉反平衡热效率计算器",
        "碳价敏感性分析",
        "What-If 减排决策沙盘",
        "⚡ VPP 削峰填谷",
        "🌱 LCA 碳足迹沙盘",
        "🏢 企业碳资产与 ESG 决策中心",
        "说明与公式",
    ]
)


def _report_df():
    rows = []
    for key, label in ENERGY_LABELS.items():
        rows.append(
            {
                "能源品种": label,
                "消耗量": f"{consumption[key]:,.2f}",
                "CO2排放量(t)": round(emissions[key], 4),
                "折标准煤(tce)": round(energy[key], 4),
            }
        )
    rows.append(
        {
            "能源品种": "合计",
                "消耗量": "—",
            "CO2排放量(t)": round(emissions["total"], 4),
            "折标准煤(tce)": round(energy["total"], 4),
        }
    )
    return pd.DataFrame(rows)


def _report_text():
    lines = [
        "企业碳盘查与能效分析报告",
        "=" * 30,
        f"企业名称：{company or '未填写'}",
        f"所属行业：{industry}",
        f"年产值（万元）：{annual_output_wan}",
        f"产品产量（吨）：{product_output_t}",
        "",
        f"总碳排放量（tCO2）：{emissions['total']:.4f}",
        f"直接排放 Scope 1（tCO2）：{emissions['scope1']:.4f}",
        f"间接排放 Scope 2（tCO2）：{emissions['scope2']:.4f}",
        f"综合能耗（tce）：{energy['total']:.4f}",
        f"万元产值综合能耗（tce/万元）：{intensity['energy_per_wan_tce']:.6f}",
        f"万元产值碳排放（tCO2/万元）：{intensity['carbon_per_wan_t']:.6f}",
        f"单位产品碳排放（tCO2/t）：{intensity['carbon_per_product_t']:.6f}",
        "",
        "降碳建议：",
    ]
    for i, item in enumerate(advice, 1):
        lines.append(f"{i}. {item}")
    return "\n".join(lines)


def _report_markdown():
    return "\n".join(
        [
            "# 企业碳盘查与能效分析报告",
            "",
            f"- 企业名称：{company or '未填写'}",
            f"- 所属行业：{industry}",
            f"- 年产值（万元）：{annual_output_wan:,.2f}",
            f"- 产品产量（吨）：{product_output_t:,.2f}",
            "",
            "## 核心指标",
            "",
            f"- 总碳排放量：{emissions['total']:,.4f} tCO₂",
            f"- 直接排放 Scope 1：{emissions['scope1']:,.4f} tCO₂",
            f"- 间接排放 Scope 2：{emissions['scope2']:,.4f} tCO₂",
            f"- 综合能耗：{energy['total']:,.4f} tce",
            f"- 万元产值综合能耗：{intensity['energy_per_wan_tce']:.6f} tce/万元",
            f"- 万元产值碳排放：{intensity['carbon_per_wan_t']:.6f} tCO₂/万元",
            f"- 单位产品碳排放：{intensity['carbon_per_product_t']:.6f} tCO₂/t",
            "",
            "## 能源明细",
            "",
            "| 能源品种 | 消耗量 | CO₂排放(t) | 折标准煤(tce) |",
            "| --- | --- | --- | --- |",
        ]
        + [
            f"| {ENERGY_LABELS[key]} | {consumption[key]:,.2f} | {emissions[key]:,.4f} | {energy[key]:,.4f} |"
            for key in ENERGY_LABELS
        ]
        + [
            f"| 合计 | — | {emissions['total']:,.4f} | {energy['total']:,.4f} |",
            "",
            "## 降碳建议",
            "",
        ]
        + [f"{i}. {item}" for i, item in enumerate(advice, 1)]
    )


with tab_account:
    if emissions["total"] <= 0:
        st.info("请在左侧录入能源消耗数据，或点击“载入示例数据”查看演示结果。")
    else:
        kpi1, kpi2, kpi3, kpi4 = st.columns(4)
        with kpi1:
            scope1_share = emissions["scope1"] / emissions["total"] if emissions["total"] else 0.0
            _kpi_card(
                "总碳排放量",
                f"{emissions['total']:,.2f}",
                "tCO₂",
                f"直接排放占比 {scope1_share:.1%}",
            )
        with kpi2:
            _kpi_card(
                "综合能耗",
                f"{energy['total']:,.2f}",
                "tce",
                "当量值折标口径",
            )
        with kpi3:
            _kpi_card(
                "万元产值碳排放",
                f"{intensity['carbon_per_wan_t']:.4f}",
                "t/万元",
                f"能耗强度 {intensity['energy_per_wan_tce']:.4f} tce/万元",
            )
        with kpi4:
            _kpi_card(
                "单位产品碳排放",
                f"{intensity['carbon_per_product_t']:.4f}",
                "t/t",
                f"产品产量 {product_output_t:,.0f} t" if product_output_t > 0 else "尚未录入产品产量",
            )

        chart1, chart2 = st.columns(2)

        source_items = [
            (SCOPE_LABELS.get(key, ENERGY_LABELS[key]), emissions[key])
            for key in SCOPE_LABELS
            if emissions[key] > 0
        ]
        if source_items:
            pie_df = pd.DataFrame(source_items, columns=["排放源", "排放量(tCO2)"])
            fig_pie = px.pie(
                pie_df,
                names="排放源",
                values="排放量(tCO2)",
                hole=0.42,
                color_discrete_sequence=["#7A9E7E", "#A3B18A", "#C2B8A3", "#D4A5A5", "#9BA6A5"],
            )
            fig_pie.update_traces(textinfo="label+percent", textposition="inside", pull=[0.02] * len(pie_df))
            fig_pie.update_layout(
                margin=dict(t=40, b=20),
                title="各能源碳排放占比",
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#333333"),
                showlegend=True,
            )
            chart1.plotly_chart(fig_pie, width="stretch")
        else:
            chart1.info("暂无能源消耗数据。")

        scope_df = pd.DataFrame(
            {
                "排放范围": ["直接排放 Scope 1", "间接排放 Scope 2"],
                "排放量(tCO2)": [emissions["scope1"], emissions["scope2"]],
            }
        )
        fig_scope = px.bar(
            scope_df,
            x="排放范围",
            y="排放量(tCO2)",
            color="排放范围",
            text_auto=".2s",
            color_discrete_sequence=["#4F7A5D", "#A3B18A"],
        )
        fig_scope.update_layout(
            showlegend=False,
            margin=dict(t=40, b=20),
            title="Scope 1 vs Scope 2",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#333333"),
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=False, zeroline=False),
        )
        fig_scope.update_traces(marker=dict(line=dict(width=0)), hovertemplate="%{x}<br>%{y:,.2f} tCO2<extra></extra>")
        chart2.plotly_chart(fig_scope, width="stretch")

        st.subheader("智能减排建议")
        for item in advice:
            st.markdown(f"- {item}")

        st.subheader("核算明细")
        st.dataframe(_report_df(), width="stretch", hide_index=True)

        st.subheader("导出报告")
        dl1, dl2, dl3 = st.columns(3)
        dl1.download_button(
            "下载核算数据（CSV）",
            data=_report_df().to_csv(index=False).encode("utf-8-sig"),
            file_name="carbon_accounting.csv",
            mime="text/csv",
            width="stretch",
        )
        dl2.download_button(
            "下载诊断报告（Markdown）",
            data=_report_markdown().encode("utf-8"),
            file_name="carbon_diagnosis_report.md",
            mime="text/markdown",
            width="stretch",
        )
        dl3.download_button(
            "下载报告摘要（TXT）",
            data=_report_text().encode("utf-8"),
            file_name="carbon_report.txt",
            mime="text/plain",
            width="stretch",
        )


with tab_heat:
    st.subheader("工业余热回收节能潜力计算器")
    st.caption(
        "基于排烟热损失公式 Q = ṁ · cp · ΔT 估算可回收热量；"
        "默认按烟气密度 1.3 kg/m³、比热 1.05 kJ/(kg·K)、可回收下限温度 120°C 计算。"
    )
    h1, h2, h3, h4 = st.columns(4)
    flue_temp = h1.number_input(
        "排烟温度（℃）",
        min_value=0.0,
        value=180.0,
        step=5.0,
        key="flue_temp",
    )
    flue_flow = h2.number_input(
        "排烟量（m³/h）",
        min_value=0.0,
        value=12000.0,
        step=100.0,
        key="flue_flow",
    )
    inlet_temp = h3.number_input(
        "冷却介质入口温度（℃）",
        min_value=0.0,
        value=60.0,
        step=1.0,
        key="inlet_temp",
    )
    run_hours = h4.number_input(
        "年运行小时数（h）",
        min_value=0.0,
        value=8000.0,
        step=100.0,
        key="run_hours",
    )

    heat = heat_recovery(flue_temp, flue_flow, inlet_temp, run_hours)
    r1, r2, r3, r4 = st.columns(4)
    with r1:
        _kpi_card("可回收热量", f"{heat['recoverable_kw']:,.1f}", "kW", "基于排烟热损失公式")
    with r2:
        _kpi_card("年节约标准煤", f"{heat['annual_tce']:,.2f}", "tce", f"年运行 {run_hours:,.0f} h")
    with r3:
        _kpi_card("年减少碳排放", f"{heat['annual_co2_t']:,.2f}", "tCO₂", "按 2.66 tCO₂/tce 折算")
    with r4:
        _kpi_card("综合换热系数估算", f"{heat['estimated_u_w_m2k']:,.0f}", "W/(m²·K)", "与推荐换热器匹配的典型值")

    st.info(f"推荐换热器类型：{heat['recommended_exchanger']}")
    st.markdown(
        "计算说明：ΔT = max(0, 排烟温度 − 120℃)；"
        "可回收热量（kW）= 排烟量 × 1.3 × 1.05 × ΔT ÷ 3600；"
        "年节约标准煤（tce）≈ 可回收热量 × 年运行小时数 ÷ 8141；"
        "综合换热系数按换热器类型取工程常用经验值，实际设计需结合冷热侧流量与物性校核。"
    )


with tab_boiler:
    st.subheader("锅炉反平衡热效率计算器")
    st.caption(
        "采用简化反平衡模型：η = 100 − q2 − q3 − q4 − q5，"
        "其中 q2 排烟热损失按经验式 q2 = (T排烟 − T环境) × (0.051 + 0.0035·α) 估算。"
    )
    b1, b2, b3, b4 = st.columns(4)
    boiler_exhaust = b1.number_input(
        "排烟温度（℃）",
        min_value=0.0,
        value=180.0,
        step=5.0,
        key="boiler_exhaust",
    )
    boiler_ambient = b2.number_input(
        "环境温度（℃）",
        min_value=-20.0,
        value=20.0,
        step=1.0,
        key="boiler_ambient",
    )
    boiler_excess_air = b3.number_input(
        "排烟处过量空气系数 α",
        min_value=1.0,
        value=1.4,
        step=0.05,
        key="boiler_excess_air",
    )
    boiler_surface_loss = b4.number_input(
        "散热损失 q5（%）",
        min_value=0.0,
        value=1.0,
        step=0.1,
        key="boiler_surface_loss",
    )
    boiler_q3 = st.slider(
        "化学不完全燃烧损失 q3（%）",
        min_value=0.0,
        max_value=5.0,
        value=0.5,
        step=0.1,
        key="boiler_q3",
    )

    boiler_result = boiler_efficiency(
        boiler_exhaust,
        boiler_ambient,
        boiler_excess_air,
        chemical_incomplete_pct=boiler_q3,
        surface_loss_pct=boiler_surface_loss,
    )
    e1, e2, e3, e4 = st.columns(4)
    with e1:
        _kpi_card("锅炉热效率", f"{boiler_result['efficiency_pct']:.2f}", "%", "反平衡法估算")
    with e2:
        _kpi_card("排烟热损失 q2", f"{boiler_result['q2_pct']:.2f}", "%", "最大单项损失")
    with e3:
        _kpi_card("化学+机械+散热损失", f"{boiler_result['q3_pct'] + boiler_result['q4_pct'] + boiler_result['q5_pct']:.2f}", "%", "q3 + q4 + q5")
    with e4:
        _kpi_card("排烟降温 20℃ 后效率", f"{boiler_result['efficiency_if_exhaust_cooled_20_pct']:.2f}", "%", f"提升 {boiler_result['efficiency_gain_pct']:.2f} 个百分点")

    st.info(
        "专业提示：排烟温度每下降约 20℃，排烟热损失显著降低，"
        "对应效率约提升 %.2f 个百分点，可作为烟气余热回收改造的节能空间依据。"
        % boiler_result["efficiency_gain_pct"]
    )


with tab_carbon:
    st.subheader("碳价敏感性分析")
    st.caption("估算企业在不同碳市场价格下，超出免费配额部分的潜在履约成本。")
    c1, c2 = st.columns(2)
    current_price = c1.slider(
        "当前碳市场价格（元/吨 CO₂）",
        min_value=10.0,
        max_value=300.0,
        value=80.0,
        step=5.0,
        key="current_price",
    )
    free_quota = c2.number_input(
        "免费配额（吨 CO₂）",
        min_value=0.0,
        value=0.0,
        step=100.0,
        key="free_quota",
    )

    total_co2 = emissions["total"]
    current = carbon_cost_curve(total_co2, free_quota, prices=(current_price,))
    _kpi_card(
        "当前碳价下的潜在履约成本",
        f"{current[0]['cost_wan']:,.2f}",
        "万元",
        f"净配额缺口 {current[0]['net_t']:,.0f} tCO₂",
    )

    price_grid = [0.0, 50.0, 100.0, 150.0, 200.0, 250.0, 300.0]
    curve = carbon_cost_curve(total_co2, free_quota, prices=price_grid)
    curve_df = pd.DataFrame(curve)
    fig_cost = px.line(
        curve_df,
        x="price",
        y="cost_wan",
        markers=True,
        labels={"price": "碳价（元/吨 CO₂）", "cost_wan": "履约成本（万元）"},
        color_discrete_sequence=["#4F7A5D"],
    )
    fig_cost.update_layout(
        margin=dict(t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#333333"),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=False, zeroline=False),
    )
    fig_cost.update_traces(line=dict(width=2.5), marker=dict(size=6))
    st.plotly_chart(fig_cost, width="stretch")
    st.caption(
        "净配额缺口 = max(0, 总排放量 − 免费配额)；履约成本 = 净配额缺口 × 碳价 ÷ 10000。"
    )


with tab_sandbox:
    st.subheader("What-If 减排决策沙盘")
    st.caption(
        "拖动参数实时模拟减排效果：绿电替代按比例抵消电力 Scope 2 排放，"
        "余热回收按利用率 × 天然气排放 × 15%（可回收热负荷占比）估算减排量。"
    )
    s1, s2, s3 = st.columns(3)
    green_ratio_pct = s1.slider(
        "绿电替代比例",
        min_value=0,
        max_value=100,
        value=30,
        step=5,
        key="sandbox_green",
    )
    heat_ratio_pct = s2.slider(
        "余热回收利用率",
        min_value=0,
        max_value=100,
        value=40,
        step=5,
        key="sandbox_heat",
    )
    future_price = s3.slider(
        "未来碳价预测（元/吨 CO₂）",
        min_value=50,
        max_value=300,
        value=100,
        step=10,
        key="sandbox_price",
    )

    sandbox = what_if_projection(
        consumption,
        green_ratio=green_ratio_pct / 100.0,
        heat_recovery_ratio=heat_ratio_pct / 100.0,
        price_per_t=future_price,
    )

    w1, w2, w3, w4 = st.columns(4)
    with w1:
        _kpi_card("基准排放总量", f"{sandbox['base_total_t']:,.2f}", "tCO₂", "未实施减排")
    with w2:
        _kpi_card("优化后排放总量", f"{sandbox['adjusted_total_t']:,.2f}", "tCO₂", f"减排 {sandbox['reduction_total_t']:,.2f} t")
    with w3:
        _kpi_card("年履约成本", f"{sandbox['cost_wan']:,.2f}", "万元", f"碳价 {future_price:.0f} 元/吨")
    with w4:
        reduction_rate = (sandbox["reduction_total_t"] / sandbox["base_total_t"]) if sandbox["base_total_t"] > 0 else 0.0
        _kpi_card("减排比例", f"{reduction_rate:.1%}", "", "相对基准排放")

    trend_df = pd.DataFrame(sandbox["annual"])
    fig_trend = go.Figure()
    fig_trend.add_trace(
        go.Scatter(
            x=trend_df["year"],
            y=trend_df["emissions_t"],
            mode="lines+markers",
            name="优化后排放",
            line=dict(color="#4F7A5D", width=3),
            marker=dict(size=8, color="#4F7A5D"),
        )
    )
    fig_trend.add_hline(
        y=sandbox["base_total_t"],
        line_dash="dot",
        line_color="#9CA3AF",
        annotation_text="基准排放",
        annotation_position="top right",
    )
    fig_trend.update_layout(
        margin=dict(t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#333333"),
        xaxis=dict(title="年份", showgrid=False, zeroline=False),
        yaxis=dict(title="碳排放（tCO₂）", showgrid=False, zeroline=False),
        hovermode="x unified",
    )
    st.plotly_chart(fig_trend, width="stretch")

    if st.button("生成综合优化策略", type="primary", width="stretch"):
        st.session_state["show_strategy"] = True

    if st.session_state.get("show_strategy", False):
        strategy = optimization_strategy(
            sandbox,
            green_ratio=green_ratio_pct / 100.0,
            heat_recovery_ratio=heat_ratio_pct / 100.0,
            price_per_t=future_price,
        )
        for idx, card in enumerate(strategy, 1):
            st.markdown(
                f"""
                <div style="background:#FFFFFF; border:1px solid #E5E7EB; border-radius:10px;
                            padding:16px 18px; margin:10px 0; box-shadow:0 1px 2px rgba(16,24,40,0.04);">
                    <div style="display:flex; justify-content:space-between; align-items:center;">
                        <strong style="color:#111827; font-size:1rem;">{idx}. {card['title']}</strong>
                        <span style="color:#2E7D32; font-weight:600; font-size:0.82rem;">优先级：{card['priority']}</span>
                    </div>
                    <div style="color:#6B7280; font-size:0.85rem; margin-top:6px;">{card['reason']}</div>
                    <div style="color:#9CA3AF; font-size:0.78rem; margin-top:8px;">
                        预计投资回收期：{card['payback_years']} · 减排潜力：{card['reduction_t']:,.2f} tCO₂/年
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        report = generate_diagnosis_report(
            sandbox,
            strategy,
            green_ratio=green_ratio_pct / 100.0,
            heat_recovery_ratio=heat_ratio_pct / 100.0,
            price_per_t=future_price,
        )
        st.markdown("---")
        st.markdown(report)
        st.download_button(
            "下载自然语言诊断报告（Markdown）",
            data=report.encode("utf-8"),
            file_name="carbon_ai_diagnosis.md",
            mime="text/markdown",
            width="stretch",
        )


with tab_vpp:
    st.subheader("虚拟电厂与分时电价削峰填谷")
    st.caption("按“谷/平时充电、尖/高峰放电”的典型策略估算套利收益与间接减排，模型为简化版。")

    p1, p2, p3, p4 = st.columns(4)
    peak_price = p1.number_input("尖峰电价（元/kWh）", min_value=0.0, value=1.4, step=0.05, key="vpp_peak")
    high_price = p2.number_input("高峰电价（元/kWh）", min_value=0.0, value=1.1, step=0.05, key="vpp_high")
    flat_price = p3.number_input("平时电价（元/kWh）", min_value=0.0, value=0.7, step=0.05, key="vpp_flat")
    valley_price = p4.number_input("谷时电价（元/kWh）", min_value=0.0, value=0.3, step=0.05, key="vpp_valley")

    v1, v2, v3, v4 = st.columns(4)
    battery_capacity = v1.number_input("储能电池容量（kWh）", min_value=0.0, value=500.0, step=50.0, key="vpp_capacity")
    charge_power = v2.number_input("充电功率（kW）", min_value=0.0, value=100.0, step=10.0, key="vpp_charge_power")
    discharge_power = v3.number_input("放电功率（kW）", min_value=0.0, value=100.0, step=10.0, key="vpp_discharge_power")
    vpp_efficiency = v4.slider("充放电效率", min_value=80, max_value=100, value=90, step=1, key="vpp_efficiency") / 100.0

    vpp = vpp_optimization(
        peak_price,
        high_price,
        flat_price,
        valley_price,
        battery_capacity,
        charge_power,
        discharge_power,
        vpp_efficiency,
    )

    k1, k2, k3, k4 = st.columns(4)
    with k1:
        _kpi_card("预计年节约电费", f"{vpp['annual_revenue_wan']:,.2f}", "万元", "峰谷差价套利")
    with k2:
        payback_text = f"{vpp['payback_years']:.1f} 年" if vpp["payback_years"] != float("inf") else "—"
        _kpi_card("储能投资回收期", payback_text, "", f"储能投资约 {vpp['capex_wan']:,.1f} 万元")
    with k3:
        _kpi_card("年间接减排", f"{vpp['co2_reduction_t']:,.2f}", "tCO₂", "谷电更清洁的加权效应")
    with k4:
        _kpi_card("每日转移电量", f"{vpp['shifted_kwh_per_day']:,.0f}", "kWh", "尖峰+高峰放电量")

    curve_df = pd.DataFrame(vpp["daily_curve"])
    fig_vpp = go.Figure()
    fig_vpp.add_trace(
        go.Bar(
            x=curve_df["hour"],
            y=curve_df["power_kw"],
            name="充放电功率",
            marker_color=["#4F7A5D" if p >= 0 else "#C2B8A3" for p in curve_df["power_kw"]],
        )
    )
    fig_vpp.add_trace(
        go.Scatter(
            x=curve_df["hour"],
            y=curve_df["price"],
            name="分时电价",
            yaxis="y2",
            line=dict(color="#D4A5A5", width=2),
        )
    )
    fig_vpp.update_layout(
        margin=dict(t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#333333"),
        xaxis=dict(title="小时", showgrid=False, zeroline=False),
        yaxis=dict(title="功率（kW）", showgrid=False, zeroline=False),
        yaxis2=dict(title="电价（元/kWh）", overlaying="y", side="right", showgrid=False),
        hovermode="x unified",
    )
    st.plotly_chart(fig_vpp, width="stretch")


with tab_lca:
    st.subheader("产品生命周期碳足迹（LCA）沙盘")
    st.caption("按原材料、生产加工、运输三段累加单件产品碳足迹，并给出欧盟 CBAM 碳关税预警。")

    l1, l2 = st.columns(2)
    material_type = l1.selectbox("主料类型", list(MATERIAL_FACTORS_KG.keys()), key="lca_material")
    material_kg = l2.number_input("主料用量（kg）", min_value=0.0, value=10.0, step=1.0, key="lca_material_kg")

    p1, p2 = st.columns(2)
    lca_elec = p1.number_input("生产耗电量（kWh/件）", min_value=0.0, value=20.0, step=1.0, key="lca_elec")
    lca_gas = p2.number_input("生产耗天然气（m³/件）", min_value=0.0, value=2.0, step=0.5, key="lca_gas")

    t1, t2, t3 = st.columns(3)
    transport_mode = t1.selectbox("运输方式", list(TRANSPORT_FACTORS_KG.keys()), key="lca_transport")
    distance_km = t2.number_input("运输距离（km）", min_value=0.0, value=500.0, step=10.0, key="lca_distance")
    weight_kg = t3.number_input("货物重量（kg）", min_value=0.0, value=1000.0, step=10.0, key="lca_weight")

    lca = lca_footprint(
        material_type,
        material_kg,
        lca_elec,
        lca_gas,
        transport_mode,
        distance_km,
        weight_kg,
    )

    c1, c2, c3 = st.columns(3)
    with c1:
        _kpi_card("单件产品碳足迹", f"{lca['total_kg_co2e']:,.2f}", "kg CO₂e", "三段合计")
    with c2:
        _kpi_card("碳排放热点环节", lca["hotspot"], "", "对总足迹贡献最大")
    with c3:
        _kpi_card("CBAM 碳关税预警", f"{lca['cbam_cost_cny']:,.2f}", "元/件", "按 80 欧元/吨、7.8 元/欧元")

    lca_df = pd.DataFrame(
        [{"阶段": key, "排放(kg CO₂e)": value} for key, value in lca["stages"].items()]
    )
    fig_lca = px.pie(
        lca_df,
        names="阶段",
        values="排放(kg CO₂e)",
        hole=0.42,
        color_discrete_sequence=["#7A9E7E", "#A3B18A", "#C2B8A3"],
    )
    fig_lca.update_traces(textinfo="label+percent", textposition="inside")
    fig_lca.update_layout(
        margin=dict(t=40, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#333333"),
    )
    st.plotly_chart(fig_lca, width="stretch")
    st.warning(
        f"碳排放热点环节为「{lca['hotspot']}」。若出口至欧盟，按当前 80 欧元/吨碳价估算，"
        f"单件产品预计增加约 {lca['cbam_cost_cny']:.2f} 元碳关税成本。"
    )


with tab_esg:
    st.subheader("企业碳资产与 ESG 商业决策中心")
    esg_t1, esg_t2, esg_t3, esg_t4 = st.tabs(
        ["📊 MACC 曲线", "⚖️ 配额盈亏雷达", "🌐 Scope 3 穿透", "📄 ESG 报告"]
    )

    with esg_t1:
        st.caption("动态录入拟选技改方案，按单位减排成本从小到大排序，判断“先改哪个最划算”。")
        default_macc = pd.DataFrame(
            {
                "方案名称": ["屋顶分布式光伏", "烟气余热回收", "高效电机改造", "绿电采购"],
                "总投资额(万元)": [800.0, 300.0, 120.0, 200.0],
                "年减排量(tCO2)": [1200.0, 800.0, 300.0, 600.0],
            }
        )
        macc_input = st.data_editor(
            default_macc,
            num_rows="dynamic",
            width="stretch",
            key="macc_editor",
        )
        projects = [
            {
                "name": str(row["方案名称"]),
                "investment_wan": float(row["总投资额(万元)"] or 0.0),
                "reduction_t": float(row["年减排量(tCO2)"] or 0.0),
            }
            for _, row in macc_input.iterrows()
            if str(row.get("方案名称", "")).strip()
        ]
        macc = [item for item in macc_curve(projects) if item["unit_cost_cny_per_t"] != float("inf")]

        if macc:
            fig_macc = go.Figure(
                go.Bar(
                    x=[item["unit_cost_cny_per_t"] for item in macc],
                    y=[item["name"] for item in macc],
                    orientation="h",
                    text=[f"{item['cumulative_reduction_t']:,.0f} t" for item in macc],
                    textposition="outside",
                    customdata=[f"投资 {item['investment_wan']:,.0f} 万元 · 年减排 {item['reduction_t']:,.0f} t" for item in macc],
                    hovertemplate="%{y}<br>单位减排成本 %{x:,.0f} 元/吨<br>%{customdata}<extra></extra>",
                    marker_color="#4F7A5D",
                )
            )
            fig_macc.update_layout(
                margin=dict(t=40, b=20),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#333333"),
                xaxis=dict(title="单位减排成本（元/吨）", showgrid=False, zeroline=False),
                yaxis=dict(title="", showgrid=False, zeroline=False),
            )
            st.plotly_chart(fig_macc, width="stretch")
            st.dataframe(
                pd.DataFrame(
                    [
                        {
                            "方案": item["name"],
                            "投资(万元)": item["investment_wan"],
                            "年减排(tCO2)": item["reduction_t"],
                            "单位减排成本(元/吨)": round(item["unit_cost_cny_per_t"], 2),
                            "累计减排(tCO2)": round(item["cumulative_reduction_t"], 2),
                        }
                        for item in macc
                    ]
                ),
                width="stretch",
                hide_index=True,
            )

    with esg_t2:
        st.caption("对比免费配额与实际排放，测算履约缺口或碳资产价值。")
        q1, q2, q3 = st.columns(3)
        free_quota = q1.number_input("免费碳配额（吨）", min_value=0.0, value=10000.0, step=100.0, key="quota_free")
        actual_emissions = q2.number_input("实际总排放量（吨）", min_value=0.0, value=float(emissions["total"]), step=100.0, key="quota_actual")
        quota_price = q3.number_input("碳市场挂牌均价（元/吨）", min_value=0.0, value=80.0, step=5.0, key="quota_price")
        quota = quota_position(free_quota, actual_emissions, quota_price)

        if quota["status"] == "deficit":
            st.markdown(
                f"""
                <div style="background:#FDF2F2; border:1px solid #F3C6C6; border-radius:10px; padding:14px 18px;">
                    <strong style="color:#B42318;">配额缺口：{quota['gap_t']:,.0f} 吨 CO₂</strong>
                    <div style="color:#B42318; margin-top:4px;">本年度潜在购碳履约财务风险：{quota['risk_wan']:,.2f} 万元</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        elif quota["status"] == "surplus":
            st.markdown(
                f"""
                <div style="background:#F0F7F0; border:1px solid #C8E6C9; border-radius:10px; padding:14px 18px;">
                    <strong style="color:#2E7D32;">配额盈余：{-quota['gap_t']:,.0f} 吨 CO₂</strong>
                    <div style="color:#2E7D32; margin-top:4px;">碳资产增值价值：{quota['asset_wan']:,.2f} 万元</div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.info("当前实际排放与免费配额持平。")

    with esg_t3:
        st.caption("录入上游核心供应商采购额与碳强度，识别供应链碳瓶颈。")
        default_suppliers = pd.DataFrame(
            {
                "供应商名称": ["钢材供应商", "铝材供应商", "包装供应商"],
                "采购额(万元)": [1200.0, 600.0, 300.0],
                "碳强度(tCO2/万元)": [1.5, 4.0, 0.8],
            }
        )
        supplier_input = st.data_editor(
            default_suppliers,
            num_rows="dynamic",
            width="stretch",
            key="scope3_editor",
        )
        suppliers = [
            {
                "name": str(row["供应商名称"]),
                "purchase_wan": float(row["采购额(万元)"] or 0.0),
                "intensity_tco2_per_wan": float(row["碳强度(tCO2/万元)"] or 0.0),
            }
            for _, row in supplier_input.iterrows()
            if str(row.get("供应商名称", "")).strip()
        ]
        scope3 = scope3_breakdown(suppliers)

        s_kpi1, s_kpi2 = st.columns(2)
        with s_kpi1:
            _kpi_card("Scope 3 总排放", f"{scope3['total_t']:,.2f}", "tCO₂", "上游供应链合计")
        with s_kpi2:
            _kpi_card("供应链碳瓶颈", scope3["hotspot"], "", "排放占比最高")

        scope_pie_df = pd.DataFrame(
            {
                "范围": ["Scope 1", "Scope 2", "Scope 3"],
                "排放(tCO2)": [emissions["scope1"], emissions["scope2"], scope3["total_t"]],
            }
        )
        fig_scope_pie = px.pie(
            scope_pie_df,
            names="范围",
            values="排放(tCO2)",
            hole=0.42,
            color_discrete_sequence=["#4F7A5D", "#A3B18A", "#C2B8A3"],
        )
        fig_scope_pie.update_traces(
            textinfo="label+percent",
            textposition="outside",
            pull=[0.02, 0.0, 0.0],
        )
        fig_scope_pie.update_layout(
            title="Scope 1 / 2 / 3 排放占比",
            margin=dict(t=60, b=20, l=20, r=20),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#333333"),
            legend=dict(orientation="h", yanchor="bottom", y=-0.2, xanchor="center", x=0.5),
        )
        st.plotly_chart(fig_scope_pie, width="stretch")

    with esg_t4:
        st.caption("自动联动前面模块指标，生成符合 GHG Protocol / 港交所 ESG 指引的环境披露摘要。")
        green_pct = st.slider("绿电占比", min_value=0, max_value=100, value=0, step=5, key="esg_green")
        if st.button("生成 ESG 环境绩效披露摘要", type="primary", width="stretch"):
            report = esg_report(
                scope1_t=emissions["scope1"],
                scope2_t=emissions["scope2"],
                scope3_t=scope3["total_t"],
                energy_per_wan_tce=intensity["energy_per_wan_tce"],
                green_ratio=green_pct / 100.0,
                company=company,
                industry=industry,
            )
            st.session_state["esg_report"] = report
        if st.session_state.get("esg_report"):
            st.markdown(st.session_state["esg_report"])
            st.download_button(
                "下载 ESG 披露摘要（Markdown）",
                data=st.session_state["esg_report"].encode("utf-8"),
                file_name="esg_disclosure_summary.md",
                mime="text/markdown",
                width="stretch",
            )


with tab_docs:
    st.subheader("计算依据与公式")
    st.markdown(
        "**碳排放量**：排放量(kgCO₂) = 活动数据 × 排放因子；结果换算为吨 CO₂。"
        "其中电力计入 Scope 2，化石燃料燃烧计入 Scope 1。"
    )
    st.markdown(
        "**综合能耗**：折标准煤量(kgce) = 活动数据 × 折标系数；"
        "1 tce = 1000 kgce，1 tce ≈ 29307.6 MJ。"
    )
    st.markdown(
        "**强度指标**：万元产值综合能耗 = 综合能耗 ÷ 年产值（万元）；"
        "单位产品碳排放 = 总排放量 ÷ 产品产量（吨）。"
    )
    st.markdown(
        "**余热回收**：Q = ṁ · cp · ΔT，ΔT 以 120℃ 作为可回收下限；"
        "年节约标准煤按回收热量与运行小时数折算。"
    )

    factor_df = pd.DataFrame(
        {
            "能源品种": [ENERGY_LABELS[key] for key in EMISSION_FACTORS_KG],
            "排放因子": [f"{EMISSION_FACTORS_KG[key]:.4f} kgCO₂/单位" for key in EMISSION_FACTORS_KG],
            "折标系数": [f"{TCE_FACTORS_KG[key]:.4f} kgce/单位" for key in TCE_FACTORS_KG],
        }
    )
    st.subheader("内置排放因子与折标系数")
    st.dataframe(factor_df, width="stretch", hide_index=True)
    st.warning(
        "以上因子基于国内常用值整理，仅用于教学演示与项目展示。"
        "正式碳盘查、核查或碳交易，请按生态环境主管部门发布的最新指南、"
        "地方标准或企业实测数据核验后使用。"
    )


with st.expander(
    "💡 热能工程师提示：本算法依据 IPCC 2006 国家温室气体清单指南及 GB/T 32150 编制",
    expanded=False,
):
    st.markdown(
        "- 化石燃料燃烧排放采用“活动数据 × 排放因子”法，电力消费计入间接排放（Scope 2）。\n"
        "- 折标系数采用当量值口径，用于能耗统计与强度对标；等价值口径适用于地区能源核算，两者不可混用。\n"
        "- 余热回收计算中的 120℃ 下限是基于烟气酸露点保护的经验值，实际工程应以烟气成分与材质腐蚀裕量校核。\n"
        "- 本平台用于教学演示与项目展示，正式碳盘查请以最新国家标准、地方指南和企业实测数据为准。"
    )
