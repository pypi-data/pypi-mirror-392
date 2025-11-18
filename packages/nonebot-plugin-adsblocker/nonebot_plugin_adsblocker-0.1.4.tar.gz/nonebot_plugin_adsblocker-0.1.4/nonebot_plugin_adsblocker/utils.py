from datetime import datetime
from nonebot.log import logger
import httpx
from urllib.parse import quote


def get_current_time():
    """获取当前时间字符串"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


async def catch_qrcode(image_url: str) -> bool:
    "检测到图片中的二维码返回bool"
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.2dcode.biz/v1/read-qr-code?file_url=" + quote(image_url), timeout=15)
        try:
            qrcode_url = response.json()["data"]["contents"][0]
            if qrcode_url:
                return True

        except IndexError as e:  # 不存在二维码
            return False

        except httpx.RequestError as e:
            logger.error(f"请求二维码识别API失败: {e}")
            return False

        except Exception as e:
            logger.error(f"处理二维码识别API响应时出错: {e}")
            return False
