import feedparser
import argparse
import re
from datetime import datetime

def fetch_rss_articles(rss_url, count):
    """
    从RSS链接获取指定数量的文章标题、链接和发布日期（兼容多格式/多键名）
    :param rss_url: RSS源链接
    :param count: 要获取的文章数量
    :return: 文章信息列表
    """
    # 解析RSS源
    feed = feedparser.parse(rss_url)
    articles = []

    # 遍历文章项，最多取count个
    for entry in feed.entries[:count]:
        # 获取标题和链接（做非空处理）
        title = entry.get('title', '无标题')
        link = entry.get('link', '#')

        # 兼容RSS的pubDate、published、date等常见键名
        pub_date = entry.get('pubDate') or entry.get('published') or entry.get('date') or '未知日期'

        formatted_date = '未知日期'
        if pub_date != '未知日期':
            # 转换为字符串
            pub_date_str = str(pub_date).strip()
            try:
                # 方案1：手动解析（兼容GMT/UTC等时区，去掉时区后解析）
                # 步骤1：移除时区部分（如GMT、UTC、+0000等）
                # 匹配空格后的最后一部分（时区），替换为空
                import re as re_date
                date_str = re_date.sub(r'\s+[A-Za-z0-9\+\-]+$', '', pub_date_str)
                # 步骤2：解析常见的RSS日期格式（支持两种主流格式）
                try:
                    # 格式1：Thu, 04 Dec 2025 18:16:00
                    date_obj = datetime.strptime(date_str, '%a, %d %b %Y %H:%M:%S')
                except ValueError:
                    # 格式2：2025-12-04T18:16:00（ISO格式）
                    date_obj = datetime.strptime(date_str, '%Y-%m-%dT%H:%M:%S')
                formatted_date = date_obj.strftime('%Y-%m-%d %H:%M:%S')

            except Exception as e:
                # 解析失败时，打印错误（便于调试），并使用原始日期
                print(f"【调试】日期解析失败：{pub_date_str} → 错误：{str(e)[:50]}")
                formatted_date = pub_date_str[:30]  # 截断过长的原始日期

        # 添加到文章列表
        articles.append(f"- [{title}]({link})")
        articles.append(f"  发布日期：{formatted_date}")

    return articles

def update_readme(readme_path, articles):
    """
    更新README.md中的文章列表
    """
    # 读取README内容
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print(f"警告：未找到{readme_path}，将创建新文件")
        content = f"<!-- BLOG-POST-LIST:START -->\n<!-- BLOG-POST-LIST:END -->"

    # 定义替换标记
    start_tag = "<!-- BLOG-POST-LIST:START -->"
    end_tag = "<!-- BLOG-POST-LIST:END -->"
    # 正则匹配标记之间的内容（包括换行）
    pattern = re.compile(f"{re.escape(start_tag)}.*?{re.escape(end_tag)}", re.DOTALL)
    # 拼接新内容
    new_content = f"{start_tag}\n{'\n'.join(articles)}\n{end_tag}"
    # 替换并写入
    updated_content = pattern.sub(new_content, content)
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)

    print(f"\n成功更新！共处理{len(articles)//2}篇文章")
    # 打印结果预览
    print("\n预览：")
    for line in articles[:10]:  # 只预览前10行
        print(line)

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='从RSS源获取文章并更新README.md')
    parser.add_argument('--rss-url', default=' ',
                        help='RSS源链接（必须）')
    parser.add_argument('--count', type=int, default=5,
                        help='要获取的文章数量（默认：5）')
    parser.add_argument('--readme-path', default='README.md',
                        help='README.md文件路径（默认：当前目录）')
    args = parser.parse_args()

    # 获取文章列表
    articles = fetch_rss_articles(args.rss_url, args.count)
    if not articles:
        print("未获取到任何文章，请检查RSS链接是否有效")
        return

    # 更新README
    update_readme(args.readme_path, articles)

if __name__ == '__main__':
    main()
