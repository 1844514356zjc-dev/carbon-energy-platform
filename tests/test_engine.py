import math
import unittest

from engine import (
    boiler_efficiency,
    compute_emissions,
    compute_energy_tce,
    compute_intensity,
    carbon_cost_curve,
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


class TestEmissions(unittest.TestCase):
    def test_electricity_and_natural_gas_emissions(self):
        consumption = {
            "electricity_kwh": 10000.0,
            "natural_gas_m3": 1000.0,
            "bituminous_coal_t": 0.0,
            "anthracite_coal_t": 0.0,
            "gasoline_l": 0.0,
            "diesel_l": 0.0,
        }
        result = compute_emissions(consumption)
        self.assertAlmostEqual(result["electricity_kwh"], 5.703, places=3)
        self.assertAlmostEqual(result["natural_gas_m3"], 2.1622, places=4)
        self.assertAlmostEqual(result["total"], 7.8652, places=4)

    def test_scope_split(self):
        consumption = {
            "electricity_kwh": 10000.0,
            "natural_gas_m3": 1000.0,
            "bituminous_coal_t": 0.0,
            "anthracite_coal_t": 0.0,
            "gasoline_l": 0.0,
            "diesel_l": 0.0,
        }
        result = compute_emissions(consumption)
        self.assertAlmostEqual(result["scope1"], 2.1622, places=4)
        self.assertAlmostEqual(result["scope2"], 5.703, places=3)


class TestEnergyTce(unittest.TestCase):
    def test_electricity_to_tce(self):
        consumption = {
            "electricity_kwh": 10000.0,
            "natural_gas_m3": 0.0,
            "bituminous_coal_t": 0.0,
            "anthracite_coal_t": 0.0,
            "gasoline_l": 0.0,
            "diesel_l": 0.0,
        }
        result = compute_energy_tce(consumption)
        self.assertAlmostEqual(result["electricity_kwh"], 1.229, places=3)
        self.assertAlmostEqual(result["total"], 1.229, places=3)


class TestIntensity(unittest.TestCase):
    def test_intensity_per_output(self):
        consumption = {
            "electricity_kwh": 10000.0,
            "natural_gas_m3": 0.0,
            "bituminous_coal_t": 0.0,
            "anthracite_coal_t": 0.0,
            "gasoline_l": 0.0,
            "diesel_l": 0.0,
        }
        result = compute_intensity(consumption, annual_output_wan=100.0, product_output_t=0.0)
        self.assertAlmostEqual(result["energy_per_wan_tce"], 0.01229, places=5)
        self.assertAlmostEqual(result["carbon_per_wan_t"], 0.05703, places=5)


class TestHeatRecovery(unittest.TestCase):
    def test_no_recovery_below_acid_dew_point(self):
        result = heat_recovery(flue_temp_c=110.0, flue_flow_m3h=10000.0, inlet_temp_c=60.0)
        self.assertEqual(result["recoverable_kw"], 0.0)
        self.assertEqual(result["annual_tce"], 0.0)

    def test_recoverable_heat_formula(self):
        flue_temp = 200.0
        flow = 3600.0
        dT = flue_temp - 120.0
        expected_kw = flow * 1.3 * 1.05 * dT / 3600.0
        result = heat_recovery(flue_temp_c=flue_temp, flue_flow_m3h=flow, inlet_temp_c=60.0)
        self.assertAlmostEqual(result["recoverable_kw"], expected_kw, places=4)
        self.assertAlmostEqual(result["annual_tce"], expected_kw * 8000 / 8141.0, places=3)


class TestCarbonCostCurve(unittest.TestCase):
    def test_curve_points(self):
        result = carbon_cost_curve(total_tco2=100.0, free_quota_t=20.0)
        self.assertAlmostEqual(result[0]["cost_wan"], (100.0 - 20.0) * 50.0 / 10000.0, places=4)
        self.assertEqual([p["price"] for p in result], [50.0, 100.0, 200.0])


class TestRecommendations(unittest.TestCase):
    def test_electricity_dominant_triggers_pv_advice(self):
        consumption = {
            "electricity_kwh": 100000.0,
            "natural_gas_m3": 0.0,
            "bituminous_coal_t": 0.0,
            "anthracite_coal_t": 0.0,
            "gasoline_l": 0.0,
            "diesel_l": 0.0,
        }
        emissions = compute_emissions(consumption)
        advice = recommendations(emissions)
        self.assertTrue(any("分布式光伏" in item for item in advice))


class TestBoilerEfficiency(unittest.TestCase):
    def test_reverse_balance_efficiency(self):
        result = boiler_efficiency(
            exhaust_temp_c=180.0,
            ambient_temp_c=20.0,
            excess_air=1.4,
            chemical_incomplete_pct=0.5,
            surface_loss_pct=1.0,
        )
        q2 = (180.0 - 20.0) * (0.051 + 0.0035 * 1.4)
        expected = 100.0 - q2 - 0.5 - 1.0
        self.assertAlmostEqual(result["q2_pct"], q2, places=4)
        self.assertAlmostEqual(result["efficiency_pct"], expected, places=4)

    def test_hotter_exhaust_lowers_efficiency(self):
        cooler = boiler_efficiency(150.0, 20.0, 1.4)
        hotter = boiler_efficiency(220.0, 20.0, 1.4)
        self.assertGreater(cooler["efficiency_pct"], hotter["efficiency_pct"])

    def test_efficiency_stays_nonnegative(self):
        result = boiler_efficiency(400.0, 20.0, 2.5, chemical_incomplete_pct=3.0, surface_loss_pct=5.0)
        self.assertGreaterEqual(result["efficiency_pct"], 0.0)


class TestWhatIfProjection(unittest.TestCase):
    def _electricity_only(self):
        return {
            "electricity_kwh": 10000.0,
            "natural_gas_m3": 0.0,
            "bituminous_coal_t": 0.0,
            "anthracite_coal_t": 0.0,
            "gasoline_l": 0.0,
            "diesel_l": 0.0,
        }

    def test_green_power_reduces_scope2_proportionally(self):
        projection = what_if_projection(self._electricity_only(), green_ratio=0.5)
        self.assertAlmostEqual(projection["electricity_reduction_t"], 5.703 * 0.5, places=4)
        self.assertAlmostEqual(projection["adjusted_total_t"], 5.703 * 0.5, places=4)

    def test_heat_recovery_reduces_gas_by_recoverable_fraction(self):
        consumption = {
            "electricity_kwh": 0.0,
            "natural_gas_m3": 1000.0,
            "bituminous_coal_t": 0.0,
            "anthracite_coal_t": 0.0,
            "gasoline_l": 0.0,
            "diesel_l": 0.0,
        }
        projection = what_if_projection(consumption, heat_recovery_ratio=1.0)
        self.assertAlmostEqual(projection["heat_reduction_t"], 2.1622 * 0.15, places=4)
        self.assertAlmostEqual(projection["adjusted_total_t"], 2.1622 * 0.85, places=4)

    def test_annual_trajectory_ends_at_adjusted_total(self):
        projection = what_if_projection(self._electricity_only(), green_ratio=1.0)
        self.assertEqual(len(projection["annual"]), 5)
        self.assertAlmostEqual(projection["annual"][-1]["emissions_t"], projection["adjusted_total_t"], places=4)


class TestOptimizationStrategy(unittest.TestCase):
    def test_strategy_contains_green_power_card(self):
        consumption = {
            "electricity_kwh": 10000.0,
            "natural_gas_m3": 0.0,
            "bituminous_coal_t": 0.0,
            "anthracite_coal_t": 0.0,
            "gasoline_l": 0.0,
            "diesel_l": 0.0,
        }
        projection = what_if_projection(consumption, green_ratio=0.5)
        strategy = optimization_strategy(projection, 0.5, 0.0, 100.0)
        titles = " ".join(item["title"] for item in strategy)
        self.assertIn("绿电", titles)


class TestDiagnosisReport(unittest.TestCase):
    def _consumption(self):
        return {
            "electricity_kwh": 10000.0,
            "natural_gas_m3": 1000.0,
            "bituminous_coal_t": 0.0,
            "anthracite_coal_t": 0.0,
            "gasoline_l": 0.0,
            "diesel_l": 0.0,
        }

    def test_report_is_natural_language_with_actions(self):
        projection = what_if_projection(self._consumption(), green_ratio=0.5, heat_recovery_ratio=0.6, price_per_t=100.0)
        strategy = optimization_strategy(projection, 0.5, 0.6, 100.0)
        report = generate_diagnosis_report(projection, strategy, 0.5, 0.6, 100.0)
        self.assertIn("绿电", report)
        self.assertIn("余热", report)
        self.assertIn("碳价", report)

    def test_report_mentions_baseline_number(self):
        projection = what_if_projection(self._consumption(), green_ratio=0.0, heat_recovery_ratio=0.0, price_per_t=80.0)
        strategy = optimization_strategy(projection, 0.0, 0.0, 80.0)
        report = generate_diagnosis_report(projection, strategy, 0.0, 0.0, 80.0)
        self.assertIn(f"{projection['base_total_t']:,.2f}", report)


class TestVppOptimization(unittest.TestCase):
    def test_annual_revenue_and_curve(self):
        result = vpp_optimization(
            peak_price=1.4,
            high_price=1.1,
            flat_price=0.7,
            valley_price=0.3,
            battery_capacity_kwh=500.0,
            charge_power_kw=100.0,
            discharge_power_kw=100.0,
            efficiency=0.9,
        )
        self.assertGreater(result["annual_revenue_wan"], 0.0)
        self.assertEqual(len(result["daily_curve"]), 24)
        self.assertGreater(result["co2_reduction_t"], 0.0)
        self.assertGreater(result["payback_years"], 0.0)


class TestLcaFootprint(unittest.TestCase):
    def test_stage_breakdown_and_hotspot(self):
        result = lca_footprint(
            material_type="钢材",
            material_kg=10.0,
            electricity_kwh=100.0,
            natural_gas_m3=10.0,
            transport_mode="公路货运",
            distance_km=100.0,
            weight_kg=1000.0,
        )
        self.assertAlmostEqual(result["stages"]["原材料获取"], 18.5, places=4)
        self.assertAlmostEqual(result["stages"]["生产加工"], 57.03 + 21.622, places=4)
        self.assertAlmostEqual(result["stages"]["运输与物流"], 8.0, places=4)
        self.assertEqual(result["hotspot"], "生产加工")

    def test_cbam_cost(self):
        result = lca_footprint(
            material_type="铝材",
            material_kg=10.0,
            electricity_kwh=0.0,
            natural_gas_m3=0.0,
            transport_mode="海运",
            distance_km=0.0,
            weight_kg=0.0,
            cbam_price_eur=80.0,
            eur_cny=7.8,
        )
        expected = result["total_kg_co2e"] / 1000.0 * 80.0 * 7.8
        self.assertAlmostEqual(result["cbam_cost_cny"], expected, places=4)


class TestMaccCurve(unittest.TestCase):
    def test_sorts_by_unit_cost_and_accumulates(self):
        projects = [
            {"name": "方案A", "investment_wan": 100.0, "reduction_t": 1000.0},
            {"name": "方案B", "investment_wan": 50.0, "reduction_t": 2000.0},
        ]
        result = macc_curve(projects)
        self.assertEqual(result[0]["name"], "方案B")
        self.assertAlmostEqual(result[0]["unit_cost_cny_per_t"], 250.0, places=4)
        self.assertAlmostEqual(result[1]["cumulative_reduction_t"], 3000.0, places=4)


class TestQuotaPosition(unittest.TestCase):
    def test_deficit_risk(self):
        result = quota_position(free_quota_t=10000.0, actual_emissions_t=12000.0, price_per_t=80.0)
        self.assertEqual(result["status"], "deficit")
        self.assertAlmostEqual(result["risk_wan"], 16.0, places=4)

    def test_surplus_asset(self):
        result = quota_position(free_quota_t=10000.0, actual_emissions_t=8000.0, price_per_t=80.0)
        self.assertEqual(result["status"], "surplus")
        self.assertAlmostEqual(result["asset_wan"], 16.0, places=4)


class TestScope3Breakdown(unittest.TestCase):
    def test_total_and_hotspot(self):
        suppliers = [
            {"name": "供应商A", "purchase_wan": 100.0, "intensity_tco2_per_wan": 2.0},
            {"name": "供应商B", "purchase_wan": 200.0, "intensity_tco2_per_wan": 1.0},
        ]
        result = scope3_breakdown(suppliers)
        self.assertAlmostEqual(result["total_t"], 400.0, places=4)
        self.assertIn(result["hotspot"], {"供应商A", "供应商B"})


class TestEsgReport(unittest.TestCase):
    def test_report_contains_key_metrics(self):
        report = esg_report(
            scope1_t=10.0,
            scope2_t=20.0,
            scope3_t=5.0,
            energy_per_wan_tce=0.0123,
            green_ratio=0.3,
            company="示例企业",
            industry="装备制造",
        )
        self.assertIn("Scope 1", report)
        self.assertIn("示例企业", report)
        self.assertIn("30.0%", report)


if __name__ == "__main__":
    unittest.main()
