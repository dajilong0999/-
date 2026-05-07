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
import io
import time
import subprocess
from datetime import datetime
from pathlib import Path

# 解决Windows GBK编码问题
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    except:
        pass

import requests
from openai import OpenAI

from config import (
    DEEPSEEK_API_KEY, DEEPSEEK_BASE_URL, DEEPSEEK_MODEL,
    CONTENT_LINES, DRAFTS_DIR, XHS_DIR, DY_DIR,
    SUPERDREAM_EMAIL, SUPERDREAM_PASSWORD,
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
    """搜索今日AI相关热点（使用DeepSeek自身的知识）"""
    print("🔍 分析今日AI热点趋势...")

    client = get_llm()
    try:
        resp = client.chat.completions.create(
            model=DEEPSEEK_MODEL,
            messages=[
                {"role": "system", "content": "你是一个AI行业分析师。列出当前（2026年5月）最热门的5个AI话题/趋势，每个带一句话说明。直接输出，不要前缀。"},
                {"role": "user", "content": "今天AI圈最火的话题是什么？"},
            ],
            temperature=0.3,
            max_tokens=500,
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        print(f"  ⚠️ 热点分析失败: {e}")
        return "2026年5月AI热点：AI绘画工具更新、大模型降价、AI角色创作工具、Sora视频生成、AI电商应用"

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

    # 4. 发布到小红书草稿箱
    print("\n步骤 4/4：发布到平台草稿箱...")
    try:
        xhs_title = ""
        xhs_body = ""
        xhs_topics = ""
        lines_parts = xhs_draft.split("\n")
        for i, line in enumerate(lines_parts):
            if line.startswith("标题") and "：" in line:
                xhs_title = line.split("：", 1)[1].strip()
            elif line.startswith("标签") and "：" in line:
                xhs_topics = line.split("：", 1)[1].strip().replace("#", "").replace(" ", ",")
            elif line.startswith("正文") and "：" in line:
                xhs_body = "\n".join(lines_parts[i+1:])
                if "标签" in xhs_body and "：" in xhs_body:
                    xhs_body = xhs_body.split("标签")[0].strip()
                xhs_body = xhs_body.strip()

        if xhs_title and xhs_body:
            # 截断标题到20字符以内（小红书限制20字符）
            xhs_title_clean = xhs_title.strip()
            # 去emoji（subprocess传emoji给.cmd文件会丢失）
            xhs_title_clean = re.sub(r'[^\x20-\x7E\xA0-ɏ一-鿿　-〿＀-￯]', '', xhs_title_clean).strip()
            while len(xhs_title_clean) > 20:
                xhs_title_clean = xhs_title_clean[:-1]
            # 去掉末尾标点
            xhs_title_clean = xhs_title_clean.rstrip('，。！？、；：,.!?;:')

            # 保存正文到临时文件（给PowerShell用）
            import subprocess
            tmp_body = os.path.join(DRAFTS_DIR, ".xhs_body.txt")
            with open(tmp_body, "w", encoding="utf-8") as f:
                f.write(xhs_body)

            # 生成配图（用 Superdream 免费 API）
            print(f"  🎨 用gpt-image-2（免费）生成配图...")
            img_out = os.path.join(DRAFTS_DIR, f"xhs_img_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")

            # 登录超梦获取token
            if not SUPERDREAM_EMAIL or not SUPERDREAM_PASSWORD:
                raise ValueError("超梦账号密码未配置，请设置 SUPERDREAM_EMAIL 和 SUPERDREAM_PASSWORD 环境变量")
            sd_login = requests.post('https://image.aishop.chat/api/user/login',
                json={'email': SUPERDREAM_EMAIL, 'password': SUPERDREAM_PASSWORD})
            sd_token = sd_login.json()['data']['token']
            sd_headers = {'Authorization': f'Bearer {sd_token}', 'Content-Type': 'application/json'}

            # 提交生图任务
            sd_gen = requests.post('https://image.aishop.chat/api/user/images/text-to-image',
                headers=sd_headers,
                json={
                    'prompt': f'为小红书笔记生成配图，主题：{xhs_title_clean}，风格：清新简约科技感',
                    'size': '1k_1x1',
                    'n': 1,
                    'output_format': 'png'
                })
            sd_data = sd_gen.json()

            if sd_data.get('code') == 0:
                task_no = sd_data['data']['task_no']
                print(f"  ⏳ 等待生图（任务: {task_no[:8]}...）")
                for _ in range(30):
                    time.sleep(3)
                    task_resp = requests.get(f'https://image.aishop.chat/api/user/images/tasks/{task_no}',
                        headers=sd_headers)
                    task_data = task_resp.json().get('data', {})
                    if task_data.get('status') == 'succeeded':
                        results = task_data.get('results', [])
                        if results:
                            img_url = results[0].get('url', '')
                            if img_url:
                                img_bytes = requests.get(img_url).content
                                with open(img_out, 'wb') as f:
                                    f.write(img_bytes)
                                print(f"  ✅ 配图已生成（免费，0元）")
                        break
                    elif task_data.get('status') in ('failed', 'error'):
                        print(f"  ⚠️ 生图失败: {task_data.get('error_message', '')}")
                        break
                else:
                    print(f"  ⚠️ 生图超时")
            else:
                print(f"  ⚠️ 提交生图失败: {sd_data.get('message', '')}")

            # 免费失败时回退到APIYI
            if not (os.path.exists(img_out) and os.path.getsize(img_out) > 1000):
                print(f"  ⚠️ 免费接口失败，尝试APIYI备用...")
                gen_cmd = [
                    "node", ".claude\\skills\\gpt-image-2\\scripts\\generate.js",
                    "--prompt", f"为小红书笔记生成配图，主题：{xhs_title_clean}，风格：清新简约科技感",
                    "--size", "1024x1024",
                    "--quality", "low",
                    "--image", img_out
                ]
                subprocess.run(gen_cmd, cwd="D:\\项目", timeout=120, capture_output=True)

            if os.path.exists(img_out) and os.path.getsize(img_out) > 1000:
                print(f"  ✅ 配图已生成")

                # 用Python直接调opencli
                print(f"  📕 发布到小红书草稿箱...")

                opencli_exe = r"C:\Users\Administrator\AppData\Roaming\npm\opencli.cmd"

                # 清洗中文引号（保留换行作为小红书段落分隔）
                clean_body = xhs_body.replace('\n\n', '\n')
                clean_body = clean_body.replace('"', "'").replace('"', "'")
                clean_title = xhs_title_clean.replace('"', "'").replace('"', "'")

                pub_args = [
                    opencli_exe, "xiaohongshu", "publish",
                    clean_body,
                    "--title", clean_title,
                    "--images", img_out,
                    "--draft", "true"
                ]
                if xhs_topics:
                    pub_args.extend(["--topics", xhs_topics])

                pub_result = subprocess.run(
                    pub_args,
                    capture_output=True, encoding='utf-8', errors='replace', timeout=120
                )
                if pub_result.returncode == 0:
                    print(f"  ✅ 已保存到小红书草稿箱！去app审核发布吧")
                else:
                    err_msg = (pub_result.stderr or pub_result.stdout or f"exit={pub_result.returncode}")[:200]
                    print(f"  ⚠️ 发布失败: {err_msg}")
            else:
                print(f"  ⚠️ 配图生成失败，跳过自动发布（草稿已存本地）")
        else:
            print(f"  ⚠️ 无法解析草稿（title={bool(xhs_title)}, body={bool(xhs_body)}）")
    except Exception as e:
        print(f"  ⚠️ 发布异常: {e}")

    print()
    print(f"  📕 小红书: {xhs_file}")
    print(f"  🎵 抖音:   {dy_file}")
    print(f"  📂 草稿箱: {DRAFTS_DIR}/")
    print()
    print("  抖音脚本已保存，可参考制作视频后发布")
    print("=" * 50)


if __name__ == "__main__":
    main()
