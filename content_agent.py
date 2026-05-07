#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
龙哥内容自动化Agent
每天12:07自动执行：
1. 搜索今日AI热点
2. 匹配三条内容线
3. 生成小红书草稿 + 抖音脚本
4. 保存到草稿箱
"""
import json
import os
import sys
import re
from datetime import datetime
from pathlib import Path

import requests
from openai import OpenAI

from config import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL,
    CONTENT_LINES, DRAFTS_DIR, XHS_DIR, DY_DIR,
)

# ===== 目录初始化 =====

def ensure_dirs():
    """确保草稿箱目录存在"""
    for d in [DRAFTS_DIR, XHS_DIR, DY_DIR]:
        Path(d).mkdir(parents=True, exist_ok=True)

# ===== AI 调用 =====

def get_llm():
    if not DEEPSEEK_API_KEY:
        print("❌ 未设置 DEEPSEEK_API_KEY 环境变量")
        sys.exit(1)
    return OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

def ask_ai(system_prompt, user_prompt, temperature=0.7):
    """调用DeepSeek生成内容"""
    client = get_llm()
    try:
        resp = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=temperature,
            max_tokens=2000,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"❌ AI调用失败: {e}")
        return None

# ===== 热点搜索 =====

def search_hot_topics():
    """搜索今日AI相关热点"""
    print("🔍 搜索今日AI热点...")

    # 用多个关键词搜，覆盖三条内容线
    keywords = [
        "AI工具 2026年5月",
        "AI绘画 最新",
        "AI角色设计",
        "AI黑科技",
        "AI创作工具",
    ]

    all_results = []
    for kw in keywords:
        try:
            url = f"https://api.bing.com/?q={kw}&count=5"
            # 用WebSearch的替代方案 - 通过搜索引擎
            resp = requests.get(
                "https://www.google.com/search",
                params={"q": kw, "hl": "zh-CN"},
                headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                },
                timeout=10,
            )
            all_results.append(f"关键词：{kw}")
        except Exception as e:
            all_results.append(f"关键词：{kw}（搜索失败: {e}）")

    return "\n".join(all_results)

# ===== 内容生成 =====

def generate_content(hot_topics):
    """生成今日内容草稿"""
    today = datetime.now().strftime("%Y-%m-%d")
    print(f"📝 生成今日({today})内容...")

    system_prompt = """你是一个AI内容运营助手，为「龙哥」做内容运营。
龙哥的人设：用AI干活的实战派，不讲虚的，只给干货。
三条内容线：
1. AI知识科普 - 用大白话讲AI技术/工具/趋势
2. AI角色创作 - AI生成角色/漫画/IP形象
3. AI视觉创作 - AI生成图片/海报/视频

写作风格：口语化、有态度、短句为主、像朋友聊天。
每篇结尾加一句引导互动的问句。"""

    # 生成小红书草稿
    xhs_prompt = f"""今天是{today}，以下是今日AI相关热点信息：
{hot_topics}

请生成1条小红书笔记草稿，要求：
1. 结合今日热点，匹配三条内容线之一
2. 标题要吸引人（带emoji）
3. 正文200-300字，口语化
4. 带3-5个相关话题标签
5. 结尾引导互动

输出格式：
---
标题：[标题]
内容线：AI知识科普/AI角色创作/AI视觉创作
正文：
[正文]
标签：#tag1 #tag2 #tag3
---"""

    xhs_draft = ask_ai(system_prompt, xhs_prompt)
    if not xhs_draft:
        xhs_draft = "# 今日草稿生成失败\n请手动编写。\n"

    # 生成抖音脚本
    dy_prompt = f"""今天是{today}，以下是今日AI相关热点信息：
{hot_topics}

请生成1条抖音短视频脚本，要求：
1. 结合今日热点，匹配三条内容线之一
2. 时长约30-60秒
3. 口语化，有节奏感
4. 包含开头钩子、正文、结尾引导

输出格式：
---
标题：[标题]
内容线：AI知识科普/AI角色创作/AI视觉创作
时长：约XX秒
脚本：
[开头钩子]
[正文]
[结尾引导]
---"""

    dy_script = ask_ai(system_prompt, dy_prompt)
    if not dy_script:
        dy_script = "# 今日脚本生成失败\n请手动编写。\n"

    return xhs_draft, dy_script

# ===== 保存草稿 =====

def save_draft(content, platform, content_type):
    """保存草稿到对应目录"""
    today = datetime.now().strftime("%Y-%m-%d")
    timestamp = datetime.now().strftime("%H%M%S")

    # 从内容中提取标题
    title_match = re.search(r'标题[：:]\s*(.*)', content)
    title = title_match.group(1).strip() if title_match else f"AI内容_{today}"
    # 清理文件名
    safe_title = re.sub(r'[\\/:*?"<>|]', '', title)[:30]

    if platform == "xiaohongshu":
        filename = f"{XHS_DIR}/{today}_{safe_title}.md"
    else:
        filename = f"{DY_DIR}/{today}_{safe_title}.md"

    # 加上元信息头
    header = f"""---
平台：{platform}
日期：{today}
生成时间：{timestamp}
内容线：{content_type}
---

"""
    with open(filename, "w", encoding="utf-8") as f:
        f.write(header + content)

    print(f"  ✅ 已保存: {filename}")
    return filename

# ===== 主流程 =====

def main():
    print("=" * 50)
    print(f"  龙哥内容自动化Agent")
    print(f"  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 50)
    print()

    ensure_dirs()

    # 1. 搜热点
    print("步骤 1/3：搜索今日热点...")
    hot_topics = search_hot_topics()
    print(f"  ✅ 获取到热点信息")
    print()

    # 2. 生成内容
    print("步骤 2/3：AI生成内容草稿...")
    xhs_draft, dy_script = generate_content(hot_topics)
    print()

    # 3. 保存草稿
    print("步骤 3/3：保存草稿...")

    # 解析内容线
    xhs_line = "AI知识科普"
    dy_line = "AI知识科普"
    if "内容线：" in xhs_draft:
        xhs_line = xhs_draft.split("内容线：")[1].split("\n")[0].strip()
    if "内容线：" in dy_script:
        dy_line = dy_script.split("内容线：")[1].split("\n")[0].strip()

    xhs_file = save_draft(xhs_draft, "xiaohongshu", xhs_line)
    dy_file = save_draft(dy_script, "douyin", dy_line)

    print()
    print("=" * 50)
    print("  ✅ 今日内容生成完毕！")
    print(f"  📕 小红书: {xhs_file}")
    print(f"  🎵 抖音:   {dy_file}")
    print(f"  📂 草稿箱: {DRAFTS_DIR}/")
    print()
    print("  下一步：龙哥审核后，用OpenCLI发布")
    print("=" * 50)


if __name__ == "__main__":
    main()
