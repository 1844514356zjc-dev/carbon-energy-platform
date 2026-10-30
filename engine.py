"""碳排放核算与能效分析计算引擎。

所有因子均基于国内常用值整理，仅用于教学演示与项目展示；
正式碳盘查需按最新国家标准或地方指南核验后使用。
"""

EMISSION_FACTORS_KG = {
    "electricity_kwh": 0.5703,          # kgCO2/kWh，全国电网平均排放因子（演示值）
    "natural_gas_m3": 2.1622,           # kgCO2/m3
    "bituminous_coal_t": 1900.3,        # kgCO2/t，烟煤
    "anthracite_coal_t": 2530.0,        # kgCO2/t，无烟煤
    "gasoline_l": 2.1646,               # kgCO2/L，汽油
    "diesel_l": 2.6006,                 # kgCO2/L，柴油
}

TCE_FACTORS_KG = {
    "electricity_kwh": 0.1229,          # kgce/kWh，电力当量值折标系数
    "natural_gas_m3": 1.2143,           # kgce/m3
    "bituminous_coal_t": 714.3,         # kgce/t，烟煤
    "anthracite_coal_t": 900.0,         # kgce/t，无烟煤
    "gasoline_l": 1.0888,               # kgce/L，汽油
    "diesel_l": 1.2239,                 # kgce/L，柴油
}

SCOPE1_KEYS = {
    "natural_gas_m3",
    "bituminous_coal_t",
    "anthracite_coal_t",
    "gasoline_l",
    "diesel_l",
}

ENERGY_KEYS = [
    "electricity_kwh",
    "natural_gas_m3",
    "bituminous_coal_t",
    "anthracite_coal_t",
    "gasoline_l",
    "diesel_l",
]


def _clean(consumption):
    data = {}
    for key in ENERGY_KEYS:
        value = consumption.get(key, 0.0) or 0.0
        data[key] = max(0.0, float(value))
    return data


def compute_emissions(consumption):
    """返回各能源品种 CO2 排放量(吨)及总量与 Scope 1/2 拆分。"""
    data = _clean(consumption)
    per_source = {
        key: data[key] * EMISSION_FACTORS_KG[key] / 1000.0
        for key in ENERGY_KEYS
    }
    scope1 = sum(per_source[key] for key in SCOPE1_KEYS)
    scope2 = per_source["electricity_kwh"]
    total = sum(per_source.values())
    return {
        **per_source,
        "scope1": scope1,
        "scope2": scope2,
        "total": total,
    }


def compute_energy_tce(consumption):
    """将各类能源统一折算为吨标准煤(tce)。"""
    data = _clean(consumption)
    per_source = {
        key: data[key] * TCE_FACTORS_KG[key] / 1000.0
        for key in ENERGY_KEYS
    }
    per_source["total"] = sum(per_source.values())
    return per_source


def compute_intensity(consumption, annual_output_wan=0.0, product_output_t=0.0):
    """计算万元产值综合能耗、万元产值碳排放与单位产品碳排放强度。"""
    energy = compute_energy_tce(consumption)
    emissions = compute_emissions(consumption)
    output_wan = max(0.0, float(annual_output_wan or 0.0))
    product_t = max(0.0, float(product_output_t or 0.0))

    energy_per_wan = energy["total"] / output_wan if output_wan > 0 else 0.0
    carbon_per_wan = emissions["total"] / output_wan if output_wan > 0 else 0.0
    carbon_per_product = emissions["total"] / product_t if product_t > 0 else 0.0

    return {
        "energy_per_wan_tce": energy_per_wan,
        "carbon_per_wan_t": carbon_per_wan,
        "carbon_per_product_t": carbon_per_product,
    }


def recommendations(emissions):
    """基于各板块排放占比生成可执行的降碳建议。"""
    total = emissions.get("total", 0.0)
    if total <= 0:
        return ["请先录入能源消耗数据，系统将自动给出降碳建议。"]

    advice = []
    electricity_share = emissions.get("electricity_kwh", 0.0) / total
    gas_share = emissions.get("natural_gas_m3", 0.0) / total
    coal_share = (emissions.get("bituminous_coal_t", 0.0) + emissions.get("anthracite_coal_t", 0.0)) / total
    oil_share = (emissions.get("gasoline_l", 0.0) + emissions.get("diesel_l", 0.0)) / total

    if electricity_share > 0.6:
        advice.append("电力排放占比超过60%，建议评估屋顶分布式光伏与绿电采购，提高可再生能源占比。")
    if gas_share > 0.4:
        advice.append("天然气排放占比较高，建议评估烟气余热深度回收与冷凝锅炉改造潜力。")
    if coal_share > 0.5:
        advice.append("燃煤排放占比较高，建议开展锅炉能效诊断、优化过量空气系数并评估煤改气/电。")
    if oil_share > 0.3:
        advice.append("油品排放占比较高，建议评估场内物流电动化或车辆调度优化。")
    if not advice:
        advice.append("各能源排放相对均衡，建议优先推进能源计量精细化与重点设备能效对标。")
    return advice


def heat_recovery(flue_temp_c, flue_flow_m3h, inlet_temp_c, hours_per_year=8000.0):
    """工业余热回收潜力估算。

    假设排烟可回收温度下限取 120°C（避开酸露点），烟气密度约 1.3 kg/m3，
    定压比热约 1.05 kJ/(kg·K)。
    """
    flue_temp = float(flue_temp_c or 0.0)
    flow = max(0.0, float(flue_flow_m3h or 0.0))
    inlet_temp = float(inlet_temp_c or 0.0)
    hours = max(0.0, float(hours_per_year or 0.0))

    delta_t = max(0.0, flue_temp - 120.0)
    density = 1.3
    cp = 1.05
    recoverable_kw = flow * density * cp * delta_t / 3600.0
    annual_tce = recoverable_kw * hours / 8141.0
    annual_co2_t = annual_tce * 2.66

    if flue_temp > 400.0:
        exchanger = "热管换热器 / 高温气-液换热器"
        estimated_u = 300.0
    elif flue_temp > 200.0:
        exchanger = "翅片管换热器 / 板式换热器"
        estimated_u = 150.0
    elif flue_temp > 120.0:
        exchanger = "板式换热器 / 烟气冷凝深度回收装置"
        estimated_u = 80.0
    else:
        exchanger = "当前排烟温度已接近酸露点，建议先评估低温余热热泵方案"
        estimated_u = 0.0

    return {
        "recoverable_kw": recoverable_kw,
        "annual_tce": annual_tce,
        "annual_co2_t": annual_co2_t,
        "recommended_exchanger": exchanger,
        "estimated_u_w_m2k": estimated_u,
        "inlet_temp_c": inlet_temp,
        "hours_per_year": hours,
    }


def carbon_cost_curve(total_tco2, free_quota_t=0.0, prices=(50.0, 100.0, 200.0)):
    """不同碳价下企业碳配额履约成本或碳资产收益（万元）。"""
    total = max(0.0, float(total_tco2 or 0.0))
    free_quota = max(0.0, float(free_quota_t or 0.0))
    net_t = max(0.0, total - free_quota)
    return [
        {
            "price": float(price),
            "cost_wan": net_t * float(price) / 10000.0,
            "net_t": net_t,
        }
        for price in prices
    ]


def boiler_efficiency(
    exhaust_temp_c,
    ambient_temp_c,
    excess_air=1.2,
    chemical_incomplete_pct=0.5,
    surface_loss_pct=1.0,
    mechanical_incomplete_pct=0.0,
):
    """锅炉反平衡热效率估算（简化模型，仅用于教学演示）。

    排烟热损失 q2 采用经验式 q2 = (T_py - T_lk) * (0.051 + 0.0035 * α)，
    化学不完全燃烧损失 q3、机械不完全燃烧损失 q4、散热损失 q5 由用户给定或取默认值。
    效率 = 100 - q2 - q3 - q4 - q5。
    """
    ambient = float(ambient_temp_c or 0.0)
    exhaust = max(float(exhaust_temp_c or 0.0), ambient)
    alpha = max(1.0, float(excess_air or 1.2))

    q2 = (exhaust - ambient) * (0.051 + 0.0035 * alpha)
    q3 = max(0.0, float(chemical_incomplete_pct or 0.0))
    q4 = max(0.0, float(mechanical_incomplete_pct or 0.0))
    q5 = max(0.0, float(surface_loss_pct or 0.0))

    efficiency = max(0.0, 100.0 - q2 - q3 - q4 - q5)

    cooled_exhaust = max(ambient, exhaust - 20.0)
    q2_cooled = (cooled_exhaust - ambient) * (0.051 + 0.0035 * alpha)
    efficiency_cooled = max(0.0, 100.0 - q2_cooled - q3 - q4 - q5)

    return {
        "q2_pct": q2,
        "q3_pct": q3,
        "q4_pct": q4,
        "q5_pct": q5,
        "efficiency_pct": efficiency,
        "efficiency_if_exhaust_cooled_20_pct": efficiency_cooled,
        "efficiency_gain_pct": efficiency_cooled - efficiency,
    }


def what_if_projection(
    consumption,
    green_ratio=0.0,
    heat_recovery_ratio=0.0,
    price_per_t=80.0,
    years=(2026, 2027, 2028, 2029, 2030),
):
    """What-If 情景模拟：按绿电替代与余热回收比例估算减排与趋势。"""
    base = compute_emissions(consumption)
    green = max(0.0, min(1.0, float(green_ratio or 0.0)))
    heat = max(0.0, min(1.0, float(heat_recovery_ratio or 0.0)))

    electricity_reduction = base["electricity_kwh"] * green
    heat_reduction = base["natural_gas_m3"] * heat * 0.15
    reduction_total = electricity_reduction + heat_reduction
    adjusted_total = max(0.0, base["total"] - reduction_total)
    price = max(0.0, float(price_per_t or 0.0))

    n = len(years)
    annual = []
    for i, year in enumerate(years):
        ramp = (i + 1) / n
        emissions_year = max(0.0, base["total"] - reduction_total * ramp)
        annual.append(
            {
                "year": year,
                "emissions_t": emissions_year,
                "cost_wan": emissions_year * price / 10000.0,
            }
        )

    return {
        "base_total_t": base["total"],
        "adjusted_total_t": adjusted_total,
        "reduction_total_t": reduction_total,
        "electricity_reduction_t": electricity_reduction,
        "heat_reduction_t": heat_reduction,
        "cost_wan": adjusted_total * price / 10000.0,
        "price_per_t": price,
        "annual": annual,
    }


def optimization_strategy(projection, green_ratio, heat_recovery_ratio, price_per_t):
    """根据 What-If 参数生成结构化降碳优化建议卡片。"""
    green = max(0.0, min(1.0, float(green_ratio or 0.0)))
    heat = max(0.0, min(1.0, float(heat_recovery_ratio or 0.0)))
    price = max(0.0, float(price_per_t or 0.0))
    cards = []

    if green > 0 and projection["electricity_reduction_t"] > 0:
        cards.append(
            {
                "title": "绿电替代 / 屋顶分布式光伏",
                "priority": "高" if green > 0.3 else "中",
                "payback_years": "5–7 年",
                "reduction_t": projection["electricity_reduction_t"],
                "reason": (
                    f"将绿电占比提升至 {green:.0%}，年减排约 "
                    f"{projection['electricity_reduction_t']:,.2f} tCO₂；"
                    "优先考虑屋顶光伏与绿电采购相结合。"
                ),
            }
        )

    if heat > 0 and projection["heat_reduction_t"] > 0:
        cards.append(
            {
                "title": "烟气余热深度回收",
                "priority": "高" if heat > 0.4 else "中",
                "payback_years": "2–4 年",
                "reduction_t": projection["heat_reduction_t"],
                "reason": (
                    f"余热利用率设定为 {heat:.0%}，按可回收燃气热负荷约 15% 估算，"
                    f"年减排约 {projection['heat_reduction_t']:,.2f} tCO₂；"
                    "建议优先改造排烟温度较高的锅炉与加热炉。"
                ),
            }
        )

    if not cards:
        cards.append(
            {
                "title": "建立能源计量与能效基线",
                "priority": "高",
                "payback_years": "1–2 年",
                "reduction_t": 0.0,
                "reason": (
                    "当前未设定减排动作。建议先完善分项计量与能效对标，"
                    "再叠加绿电和余热回收等技改措施。"
                ),
            }
        )

    cards.append(
        {
            "title": "碳资产与履约成本管理",
            "priority": "中",
            "payback_years": "—",
            "reduction_t": projection["reduction_total_t"],
            "reason": (
                f"在 {price:.0f} 元/吨碳价下，优化后年履约成本约 "
                f"{projection['cost_wan']:,.2f} 万元；"
                "可通过提前锁定配额或绿证对冲碳价上行风险。"
            ),
        }
    )

    return cards


def generate_diagnosis_report(projection, strategy, green_ratio, heat_recovery_ratio, price_per_t):
    """基于本地规则引擎生成自然语言减排诊断报告。"""
    green = max(0.0, min(1.0, float(green_ratio or 0.0)))
    heat = max(0.0, min(1.0, float(heat_recovery_ratio or 0.0)))
    price = max(0.0, float(price_per_t or 0.0))

    base = projection["base_total_t"]
    adjusted = projection["adjusted_total_t"]
    reduction = projection["reduction_total_t"]
    rate = reduction / base if base > 0 else 0.0
    baseline_cost = base * price / 10000.0
    adjusted_cost = projection["cost_wan"]

    lines = [
        "## 诊断摘要",
        "",
        (
            f"当前核算口径下，基准年碳排放约 **{base:,.2f} tCO₂**。"
            f"若按绿电替代 **{green:.0%}**、余热回收利用率 **{heat:.0%}** 实施，"
            f"年排放可降至 **{adjusted:,.2f} tCO₂**，合计减排 **{reduction:,.2f} tCO₂**，"
            f"减排幅度约 **{rate:.1%}**。"
        ),
        "",
        "## 关键诊断",
        "",
    ]

    if green > 0 and projection["electricity_reduction_t"] > 0:
        lines.append(
            f"- 电力间接排放仍是可优化重点：绿电替代可贡献约 "
            f"**{projection['electricity_reduction_t']:,.2f} tCO₂** 减排，"
            f"建议优先锁定长期绿电采购协议或建设屋顶光伏。"
        )
    if heat > 0 and projection["heat_reduction_t"] > 0:
        lines.append(
            f"- 热力系统具备明显余热回收空间：按当前利用率可贡献约 "
            f"**{projection['heat_reduction_t']:,.2f} tCO₂** 减排，"
            f"宜优先对高排烟温度的锅炉与加热炉实施烟气深度回收。"
        )
    if not lines[-1].startswith("-"):
        lines.append(
            "- 当前未设置减排动作，建议先建立分项计量与能效基线，再叠加技术改造措施。"
        )

    lines.extend(
        [
            "",
            "## 技术改造与减排潜力",
            "",
        ]
    )
    for item in strategy:
        lines.append(
            f"- **{item['title']}**（优先级：{item['priority']}，"
            f"回收期：{item['payback_years']}，减排潜力：{item['reduction_t']:,.2f} tCO₂/年）"
        )

    lines.extend(
        [
            "",
            "## 碳价与财务影响",
            "",
            (
                f"在 **{price:.0f} 元/吨 CO₂** 的碳价下，优化后年履约成本约 "
                f"**{adjusted_cost:,.2f} 万元**；相比未减排的基准成本 "
                f"**{baseline_cost:,.2f} 万元**，每年可降低约 "
                f"**{reduction * price / 10000.0:,.2f} 万元**。"
                "建议通过配额提前锁定或绿证交易对冲碳价上行风险。"
            ),
            "",
            "## 实施路径建议",
            "",
            "- 短期（0–6 个月）：完善分项计量、完成能效对标与碳盘查基线校准。",
            "- 中期（6–18 个月）：优先落地余热回收改造与绿电采购，锁定主要减排量。",
            "- 长期（18 个月以上）：建设屋顶光伏、综合能源管理与碳资产管理体系。",
        ]
    )

    return "\n".join(lines)


MATERIAL_FACTORS_KG = {
    "钢材": 1.85,
    "铝材": 11.5,
    "塑料": 2.5,
    "水泥": 0.9,
    "玻璃": 1.1,
    "木材": 0.4,
}

TRANSPORT_FACTORS_KG = {
    "公路货运": 0.08,
    "铁路": 0.02,
    "海运": 0.01,
}


def vpp_optimization(
    peak_price,
    high_price,
    flat_price,
    valley_price,
    battery_capacity_kwh,
    charge_power_kw,
    discharge_power_kw,
    efficiency=0.9,
    unit_capex_cny_per_kwh=1200.0,
):
    """虚拟电厂分时电价削峰填谷经济性测算（简化模型）。"""
    eff = max(0.05, min(1.0, float(efficiency or 0.9)))
    capacity = max(0.0, float(battery_capacity_kwh or 0.0))
    charge_p = max(0.0, float(charge_power_kw or 0.0))
    discharge_p = max(0.0, float(discharge_power_kw or 0.0))
    peak = max(0.0, float(peak_price or 0.0))
    high = max(0.0, float(high_price or 0.0))
    flat = max(0.0, float(flat_price or 0.0))
    valley = max(0.0, float(valley_price or 0.0))

    stored_kwh = min(capacity, charge_p * 6.0) * eff
    peak_discharge = min(discharge_p * 2.0, stored_kwh)
    high_discharge = min(discharge_p * 2.0, max(0.0, stored_kwh - peak_discharge))

    daily_revenue = peak_discharge * (peak - valley) + high_discharge * (high - valley)
    annual_revenue = daily_revenue * 365.0
    capex = capacity * max(0.0, float(unit_capex_cny_per_kwh or 0.0))
    payback_years = capex / annual_revenue if annual_revenue > 0 else float("inf")

    peak_factor = 0.5703 * 1.15
    valley_factor = 0.5703 * 0.85
    shifted_kwh = peak_discharge + high_discharge
    co2_reduction_t = shifted_kwh * (peak_factor - valley_factor) * 365.0 / 1000.0

    schedule = []
    for hour in range(24):
        if hour in (0, 1, 2, 3, 4, 5, 6, 7, 23):
            label, price, power = "谷时", valley, charge_p
        elif hour in (8, 9, 10, 14, 15, 16, 17):
            label, price, power = "平时", flat, 0.0
        elif hour in (11, 12, 13, 21, 22):
            label, price, power = "高峰", high, -discharge_p
        else:
            label, price, power = "尖峰", peak, -discharge_p
        schedule.append(
            {
                "hour": hour,
                "label": label,
                "price": price,
                "power_kw": power,
            }
        )

    return {
        "daily_revenue": daily_revenue,
        "annual_revenue_wan": annual_revenue / 10000.0,
        "payback_years": payback_years,
        "capex_wan": capex / 10000.0,
        "shifted_kwh_per_day": shifted_kwh,
        "co2_reduction_t": co2_reduction_t,
        "daily_curve": schedule,
    }


def lca_footprint(
    material_type,
    material_kg,
    electricity_kwh,
    natural_gas_m3,
    transport_mode,
    distance_km,
    weight_kg,
    cbam_price_eur=80.0,
    eur_cny=7.8,
):
    """产品生命周期碳足迹（LCA）简易核算。"""
    material = max(0.0, float(material_kg or 0.0))
    elec = max(0.0, float(electricity_kwh or 0.0))
    gas = max(0.0, float(natural_gas_m3 or 0.0))
    distance = max(0.0, float(distance_km or 0.0))
    weight = max(0.0, float(weight_kg or 0.0))

    material_emission = material * MATERIAL_FACTORS_KG.get(material_type, 0.0)
    production_emission = elec * 0.5703 + gas * 2.1622
    transport_emission = distance * (weight / 1000.0) * TRANSPORT_FACTORS_KG.get(transport_mode, 0.0)

    stages = {
        "原材料获取": material_emission,
        "生产加工": production_emission,
        "运输与物流": transport_emission,
    }
    total = sum(stages.values())
    hotspot = max(stages, key=stages.get)
    cbam_cost_cny = total / 1000.0 * float(cbam_price_eur) * float(eur_cny)

    return {
        "stages": stages,
        "total_kg_co2e": total,
        "hotspot": hotspot,
        "cbam_cost_cny": cbam_cost_cny,
    }


def macc_curve(projects):
    """边际减排成本曲线：按单位减排成本升序排列并累计减排量。"""
    cleaned = []
    for project in projects:
        name = str(project.get("name", "")).strip() or "未命名方案"
        investment = max(0.0, float(project.get("investment_wan", 0.0) or 0.0))
        reduction = max(0.0, float(project.get("reduction_t", 0.0) or 0.0))
        unit_cost = investment * 10000.0 / reduction if reduction > 0 else float("inf")
        cleaned.append(
            {
                "name": name,
                "investment_wan": investment,
                "reduction_t": reduction,
                "unit_cost_cny_per_t": unit_cost,
            }
        )

    cleaned.sort(key=lambda item: item["unit_cost_cny_per_t"])
    cumulative = 0.0
    for item in cleaned:
        cumulative += item["reduction_t"]
        item["cumulative_reduction_t"] = cumulative
    return cleaned


def quota_position(free_quota_t, actual_emissions_t, price_per_t):
    """碳配额盈亏与履约财务风险测算。"""
    free_quota = max(0.0, float(free_quota_t or 0.0))
    actual = max(0.0, float(actual_emissions_t or 0.0))
    price = max(0.0, float(price_per_t or 0.0))
    gap = actual - free_quota

    if gap > 0:
        status = "deficit"
    elif gap < 0:
        status = "surplus"
    else:
        status = "balanced"

    return {
        "gap_t": gap,
        "status": status,
        "risk_wan": max(0.0, gap) * price / 10000.0,
        "asset_wan": max(0.0, -gap) * price / 10000.0,
    }


def scope3_breakdown(suppliers):
    """供应链上下游 Scope 3 排放穿透。"""
    rows = []
    for supplier in suppliers:
        name = str(supplier.get("name", "")).strip() or "未命名供应商"
        purchase = max(0.0, float(supplier.get("purchase_wan", 0.0) or 0.0))
        intensity = max(0.0, float(supplier.get("intensity_tco2_per_wan", 0.0) or 0.0))
        emission = purchase * intensity
        rows.append(
            {
                "name": name,
                "purchase_wan": purchase,
                "intensity_tco2_per_wan": intensity,
                "emission_t": emission,
            }
        )

    total = sum(item["emission_t"] for item in rows)
    hotspot = max(rows, key=lambda item: item["emission_t"])["name"] if rows else "—"
    return {"suppliers": rows, "total_t": total, "hotspot": hotspot}


def esg_report(
    scope1_t,
    scope2_t,
    scope3_t,
    energy_per_wan_tce,
    green_ratio,
    company="",
    industry="",
):
    """按 GHG Protocol / 港交所 ESG 指引框架生成环境绩效披露摘要。"""
    total = float(scope1_t or 0.0) + float(scope2_t or 0.0) + float(scope3_t or 0.0)
    green = max(0.0, min(1.0, float(green_ratio or 0.0)))

    return "\n".join(
        [
            "# 企业环境（E）绩效披露摘要",
            "",
            f"- 报告主体：{company or '未填写'}",
            f"- 所属行业：{industry or '未填写'}",
            f"- 编制依据：GHG Protocol 温室气体核算体系、香港联交所 ESG 报告指引（环境维度）",
            "",
            "## 温室气体排放",
            "",
            f"- Scope 1 直接排放：{float(scope1_t or 0.0):,.2f} tCO₂e",
            f"- Scope 2 间接排放：{float(scope2_t or 0.0):,.2f} tCO₂e",
            f"- Scope 3 供应链及其他间接排放：{float(scope3_t or 0.0):,.2f} tCO₂e",
            f"- 排放总量：{total:,.2f} tCO₂e",
            "",
            "## 能效与清洁能源",
            "",
            f"- 万元产值综合能耗：{float(energy_per_wan_tce or 0.0):.6f} tce/万元",
            f"- 绿电占比：{green:.1%}",
            "",
            "## 管理建议",
            "",
            "- 持续推进分项计量与能耗数据治理，提升排放数据可追溯性。",
            "- 优先实施单位减排成本较低的技术改造，优化碳资产结构。",
            "- 对上游高碳强度供应商开展绿色采购与碳绩效评估，降低 Scope 3 风险。",
        ]
    )
