# 企业碳排放与能效管理计算平台

一个面向能源动力/热能专业项目展示的 Streamlit Web 应用。输入企业能源消耗数据后，自动完成碳排放核算、综合能耗折算、强度对标、余热回收潜力估算与碳价敏感性分析。

## 功能

- 碳排放自动核算：内置国内常用排放因子，拆分直接排放（Scope 1）与间接排放（Scope 2）。
- 能效与热力学指标：折算吨标准煤（tce），计算万元产值综合能耗、单位产品碳排放强度。
- 数据可视化：KPI 看板、能源碳排放占比饼图、Scope 1/2 柱状图。
- 智能减排建议：按排放结构自动给出分布式光伏、烟气余热回收、锅炉能效诊断等建议。
- 工业余热回收与热力学诊断：基于 Q = ṁ · cp · ΔT 估算可回收热量、年节约标准煤与减排量，估算综合换热系数并推荐换热器类型。
- 锅炉反平衡热效率计算器：按 η = 100 − q2 − q3 − q4 − q5 估算实时效率，并给出排烟降温节能空间。
- 碳价敏感性分析：生成不同碳价下的履约成本曲线。
- What-If 减排决策沙盘：绿电替代、余热回收利用率、未来碳价三个滑块实时联动排放总量、履约成本与 2026–2030 降碳趋势；内置本地规则引擎，可生成结构化优化策略与自然语言诊断报告。
- 虚拟电厂（VPP）削峰填谷：按分时电价与储能/蓄热配置测算峰谷差价收益、投资回收期、间接减排，并绘制典型日 24 小时充放电与电价双轴曲线。
- 产品生命周期碳足迹（LCA）沙盘：按原材料、生产加工、运输三段核算单件产品碳足迹，识别碳排放热点并给出欧盟 CBAM 碳关税预警。
- 企业碳资产与 ESG 决策中心：MACC 边际减排成本曲线、碳配额盈亏与履约财务风险、ESG 环境披露摘要生成、Scope 3 供应链穿透分析。
- 场景预设：一键加载燃气热电厂、电子制造工厂、大型商场等高仿真演示数据。
- 报告导出：一键导出 CSV 核算数据、Markdown 诊断报告与文本摘要报告。

## 快速开始

```bash
cd carbon-platform
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py
```

macOS / Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

浏览器打开 Streamlit 提示的本地地址即可使用，可点击侧边栏“载入示例数据”查看完整演示。

## 运行测试

```bash
python -m unittest discover -s tests -t . -v
```

## 项目结构

```text
carbon-platform/
├── app.py                 # Streamlit 主程序
├── engine.py              # 可独立测试的核算引擎
├── requirements.txt
├── README.md
├── DEPLOY.md              # 部署上线步骤
├── RESUME_BULLETS.md      # 可直接参考的简历表述
├── .streamlit/config.toml # 主题配置
└── tests/test_engine.py   # 单元测试
```

## 免责声明

内置排放因子与折标系数基于国内常用值整理，仅用于教学演示与项目展示。正式碳盘查、核查或碳交易，请按最新国家标准、地方指南或企业实测数据核验后使用。
