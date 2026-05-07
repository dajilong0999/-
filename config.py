"""内容自动化配置 - 所有敏感信息通过环境变量传入"""
import os

# DeepSeek API（你聊天用的那个）
DEEPSEEK_API_KEY = os.environ.get("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL = os.environ.get("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL = os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")

# 内容三线
CONTENT_LINES = {
    "ai_knowledge": "AI知识科普 - 用大白话讲AI技术、工具、趋势，让普通人也能看懂",
    "ai_character": "AI角色创作 - AI生成角色设计、漫画、IP形象",
    "ai_visual": "AI视觉创作 - AI生成图片、海报、视频等视觉内容",
}

# 草稿箱路径
DRAFTS_DIR = "drafts"
XHS_DIR = f"{DRAFTS_DIR}/xiaohongshu"
DY_DIR = f"{DRAFTS_DIR}/douyin"
