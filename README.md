# 龙哥内容自动化

每天12:07自动执行：
1. 搜索今日AI热点
2. 匹配三条内容线（AI科普/AI角色/AI视觉）
3. 生成小红书草稿 + 抖音脚本
4. 保存到 `drafts/` 目录

## 使用方式

### 本地测试
```bash
export DEEPSEEK_API_KEY=sk-your-key
python content_agent.py
```

### 自动发布（用OpenCLI）
```bash
# 发布小红书草稿
opencli xiaohongshu publish --file drafts/xiaohongshu/2026-05-07_标题.md

# 发布抖音视频
opencli douyin publish drafts/douyin/2026-05-07_标题.mp4
```

## 目录结构
```
├── content_agent.py       # 主程序
├── config.py              # 配置
├── requirements.txt       # 依赖
├── .github/workflows/     # 定时任务（每天12:07）
└── drafts/
    ├── xiaohongshu/       # 小红书草稿
    └── douyin/            # 抖音脚本
```
