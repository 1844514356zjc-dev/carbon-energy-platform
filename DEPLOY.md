# Streamlit 部署上线步骤

本项目可免费部署到 Streamlit Community Cloud，生成一个可公开访问的网址，方便放入简历和作品集。

## 1. 初始化 Git 仓库并上传 GitHub

```bash
cd carbon-platform
git init
git add .
git commit -m "init: 企业碳排放与能效管理计算平台"
```

在 GitHub 新建一个仓库（例如 `carbon-energy-platform`），然后：

```bash
git remote add origin https://github.com/<你的用户名>/carbon-energy-platform.git
git branch -M main
git push -u origin main
```

## 2. 部署到 Streamlit Community Cloud

1. 打开 https://share.streamlit.io/ 并用 GitHub 账号登录。
2. 点击 “Create app” → “Deploy a public app from GitHub”。
3. Repository 选择 `carbon-energy-platform`，Branch 选择 `main`，Main file path 填 `app.py`。
4. 点击 Deploy，等待构建完成即可获得 `https://<app-name>.streamlit.app` 的公开链接。

## 3. 本地局域网演示（可选）

```bash
streamlit run app.py --server.address 0.0.0.0 --server.port 8501
```

同网络设备可通过 `http://<电脑局域网IP>:8501` 访问，适合面试现场演示。

## 4. 上线前检查

- 确认 `requirements.txt` 与代码实际依赖一致。
- 确认侧边栏“载入示例数据”可正常展示结果。
- 确认 CSV 与 TXT 下载按钮可正常下载。
- 因子为演示值，页面内已添加免责声明，避免误用为正式盘查结论。
