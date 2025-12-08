import asyncio
import aiohttp
import json
import argparse
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from typing import Dict, Any



DEFAULT_OUTPUT_PATH = "./bili/UP_data.json"  # 默认输出文件路径
DEFAULT_MID = 0000000  # 默认用户ID


async def fetch_single_api(url: str, params: Dict[str, Any]) -> Dict[str, Any]:
    """单独请求一个API并返回完整响应"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate",
        "Referer": "https://www.bilibili.com/",
        "Origin": "https://www.bilibili.com",
        "Connection": "keep-alive",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Site": "same-site",
        "Cache-Control": "no-cache",
        "Pragma": "no-cache"
    }
    
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers, params=params, ssl=False) as response:
            response.raise_for_status()
            return await response.json()


async def get_bilibili_user_info(mid: int) -> Dict[str, Any]:
    """分开请求两个API，然后合并结果提取字段"""
    # 并行请求两个API
    card_api_url = "https://api.bilibili.com/x/web-interface/card"
    navnum_api_url = "https://api.bilibili.com/x/space/navnum"
    params = {"mid": mid}
    
    card_response, navnum_response = await asyncio.gather(
        fetch_single_api(card_api_url, params),
        fetch_single_api(navnum_api_url, params)
    )
    
    # 初始化结果字典
    result = {
        "archive_count": None,
        "follower": None,
        "like_num": None,
        "name": None,
        "sex": None,
        "face": None,
        "friend": None,
        "sign": None,
        "current_level": None,
        "article": None,
        "album": None,
        "opus": None
    }
    
    # 从第一个API提取字段
    if card_response.get("code") == 0:
        card_data = card_response.get("data", {})
        card = card_data.get("card", {})
        result["archive_count"] = card_data.get("archive_count")
        result["follower"] = card_data.get("follower")
        result["like_num"] = card_data.get("like_num")
        result["name"] = card.get("name")
        result["sex"] = card.get("sex")
        result["face"] = card.get("face")
        result["friend"] = card.get("friend")
        result["sign"] = card.get("sign")
        result["current_level"] = card.get("level_info", {}).get("current_level")
    
    # 从第二个API提取字段
    if navnum_response.get("code") == 0:
        navnum_data = navnum_response.get("data", {})
        result["article"] = navnum_data.get("article")
        result["album"] = navnum_data.get("album")
        result["opus"] = navnum_data.get("opus")
    
    # 添加中国标准时间
    result["update_time"] = datetime.now(ZoneInfo("Asia/Shanghai")).strftime("%Y-%m-%d %H:%M:%S")
    
    return result


def main(mid: int = DEFAULT_MID, output_path: str = DEFAULT_OUTPUT_PATH) -> None:
    """
    主函数，支持自定义用户ID和输出路径，自动创建缺失目录
    
    Args:
        mid: B站用户ID（默认使用DEFAULT_MID）
        output_path: 输出文件路径（默认使用DEFAULT_OUTPUT_PATH）
    """
    user_info = asyncio.run(get_bilibili_user_info(mid))
    

    output_path_obj = Path(output_path)  # 转换为Path对象
    output_path_obj.parent.mkdir(parents=True, exist_ok=True)  # 创建父目录（递归创建，已存在则忽略）
    
    # 保存到指定路径
    with open(output_path_obj, "w", encoding="utf-8") as f:
        json.dump(user_info, f, ensure_ascii=False, indent=2)
    
    print(f"结果已保存到：{output_path_obj.resolve()}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="获取B站用户信息并保存到JSON文件")
    parser.add_argument("-m", "--mid", type=int, default=DEFAULT_MID, help=f"B站用户ID（默认：{DEFAULT_MID}）")
    parser.add_argument("-o", "--output", type=str, default=DEFAULT_OUTPUT_PATH, help=f"输出文件路径（默认：{DEFAULT_OUTPUT_PATH}）")
    
    args = parser.parse_args()
    
    # 调用主函数，传入命令行参数
    main(mid=args.mid, output_path=args.output)
