import json
import os
import argparse
from playwright.sync_api import sync_playwright

# 获取脚本所在目录的绝对路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# 默认输入输出路径
DEFAULT_JSON_FILE = os.path.join(SCRIPT_DIR, "bili", "UP_data.json")
DEFAULT_BASE_FILENAME = os.path.join(SCRIPT_DIR, "bili", "up_card")

def generate_up_card_html(json_file, theme="light"):
    """根据JSON数据和主题生成完整的HTML内容"""
    # 检查输入JSON文件是否存在
    if not os.path.exists(json_file):
        raise FileNotFoundError(f"输入JSON文件不存在: {json_file}")
        
    with open(json_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    sign_with_br = data['sign'].replace('\n', '<br>')
    
    # 主题样式配置
    themes = {
        "light": {
            "body_bg": "#ffffff",
            "text_primary": "#000000",
            "text_secondary": "#666666",
            "text_tertiary": "#999999",
            "card_bg": "#f5f5f5",
            "container_bg": "#ffffff"
        },
        "dark": {
            "body_bg": "#1a1a1a",
            "text_primary": "#ffffff",
            "text_secondary": "#a0a0a0",
            "text_tertiary": "#666666",
            "card_bg": "#2d2d2d",
            "container_bg": "#1a1a1a"
        }
    }
    
    # 获取当前主题的样式
    style = themes[theme]
    
    # 生成完整HTML
    html_content = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{data['name']} - Bilibili数据卡片</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
        }}
        body {{
            background-color: {style['body_bg']};
            padding: 20px;
        }}
        .card-container {{
            max-width: 600px;
            margin: 0 auto;
            background-color: {style['container_bg']};
            padding: 20px;
            border-radius: 12px;
        }}
    </style>
</head>
<body>
    <div class="card-container">
        <div align="center">
            <img src="{data['face']}" alt="{data['name']}" width="120" height="120" style="border-radius: 50%; margin-bottom: 10px; border: 3px solid {style['card_bg']};">
            <h2 style="color: {style['text_primary']};">{data['name']}</h2>
            <p style="color: {style['text_secondary']}; margin-bottom: 20px;">{sign_with_br}</p>
            
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 15px; max-width: 500px; margin: 0 auto;">
                <div style="background-color: {style['card_bg']}; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <p style="margin: 0; font-size: 14px; color: {style['text_secondary']};">粉丝数</p>
                    <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: bold; color: #007bff;">{data['follower']:,}</p>
                </div>
                
                <div style="background-color: {style['card_bg']}; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <p style="margin: 0; font-size: 14px; color: {style['text_secondary']};">获赞数</p>
                    <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: bold; color: #ff6b6b;">{data['like_num']:,}</p>
                </div>
                
                <div style="background-color: {style['card_bg']}; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <p style="margin: 0; font-size: 14px; color: {style['text_secondary']};">投稿数</p>
                    <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: bold; color: #4ecdc4;">{data['archive_count']}</p>
                </div>
                
                <div style="background-color: {style['card_bg']}; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <p style="margin: 0; font-size: 14px; color: {style['text_secondary']};">等级</p>
                    <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: bold; color: #ffd166;">Lv.{data['current_level']}</p>
                </div>
                
                <div style="background-color: {style['card_bg']}; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <p style="margin: 0; font-size: 14px; color: {style['text_secondary']};">关注数</p>
                    <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: bold; color: #06d6a0;">{data['friend']}</p>
                </div>
                
                <div style="background-color: {style['card_bg']}; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                    <p style="margin: 0; font-size: 14px; color: {style['text_secondary']};">图文总数</p>
                    <p style="margin: 5px 0 0 0; font-size: 24px; font-weight: bold; color: #118ab2;">{data['opus']}</p>
                </div>
            </div>
            
            <p style="margin-top: 20px; color: {style['text_tertiary']}; font-size: 12px;">数据更新时间: {data.get('update_time', '未知')}</p>
        </div>
    </div>
</body>
</html>
"""
    return html_content

def generate_card_image(json_file, output_image, theme="light"):
    """生成指定主题的UP主数据卡片图片"""
    html_content = generate_up_card_html(json_file, theme)
    
    with sync_playwright() as p:
        # 启动浏览器（无头模式）
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            viewport={"width": 600, "height": 800},  # 设置合适的视口大小
            device_scale_factor=2  # 提高DPI，生成高清图片
        )
        
        # 设置页面内容
        page.set_content(html_content)
        
        # 等待页面加载完成（特别是图片）
        page.wait_for_load_state("networkidle")
        
        # 获取卡片容器元素
        card_element = page.locator(".card-container")
        
        # 截取卡片区域
        card_element.screenshot(path=output_image, type="png")
        
        # 关闭浏览器
        browser.close()
    
    print(f"成功生成{theme}主题卡片图片：{output_image}")

def generate_both_themes(json_file, base_filename="up_card"):
    """同时生成浅色和深色主题的卡片图片"""
    # 确保输出目录存在
    output_dir = os.path.dirname(base_filename)
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成浅色主题
    light_output = f"{base_filename}_light.png"
    generate_card_image(json_file, light_output, theme="light")
    
    # 生成深色主题
    dark_output = f"{base_filename}_dark.png"
    generate_card_image(json_file, dark_output, theme="dark")

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='生成B站UP主数据卡片图片')
    parser.add_argument('--input', type=str, default=DEFAULT_JSON_FILE, 
                      help=f'输入JSON数据文件路径，默认: {DEFAULT_JSON_FILE}')
    parser.add_argument('--output', type=str, default=DEFAULT_BASE_FILENAME,
                      help=f'输出图片基础路径（不含后缀），默认: {DEFAULT_BASE_FILENAME}')
    
    args = parser.parse_args()
    
    # 生成卡片
    generate_both_themes(args.input, args.output)
