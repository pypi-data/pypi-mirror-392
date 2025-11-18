# fmt: off
############ PluginMetadata ###########
from nonebot.plugin import PluginMetadata
__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-adsblocker", 
    description="基于DeepSeek的群聊违规消息拦截",
    usage="请阅读MD文档",
    type="application",  
    homepage="https://github.com/Heartestrella/plugin-adsblocker",
    # config=YourConfigClass,
    supported_adapters={"~onebot.v11"},
)

#######################################

from nonebot import require
require("nonebot_plugin_localstore")
from typing import Optional
import httpx
from nonebot.params import CommandArg
from nonebot import on_command, on_message
# from nonebot_plugin_adsblocker.utils import catch_qrcode , get_current_time
from nonebot_plugin_adsblocker.db_funcs import DatabaseManager
from nonebot.log import logger
from nonebot.adapters.onebot.v11 import GROUP_ADMIN, GROUP_OWNER, GroupIncreaseNoticeEvent, Bot, GroupMessageEvent, PrivateMessageEvent, Event, Message
from nonebot.permission import SUPERUSER
from nonebot import on_notice, get_driver
import json

#######################################
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

#######################################

db_manager = DatabaseManager()
superusers = get_driver().config.superusers

message_handler = on_message(priority=10)
set_apikey = on_command("set_apikey", permission=SUPERUSER, priority=1)
active_group = on_command(
    "blocker", permission=GROUP_ADMIN | GROUP_OWNER | SUPERUSER, priority=1)
set_active_groups = on_command(
    "active_groups", permission=SUPERUSER, priority=1)

group_increase_handler = on_notice(priority=1)


@set_apikey.handle()
async def handle_set_apikey(event: Event, args: Message = CommandArg()):
    api_key = args.extract_plain_text().strip()

    if not api_key:
        await set_apikey.finish("请输入API Key，用法: /set_apikey <your_api_key>")

    try:
        # db_manager.ensure_api_keys_exists()  # 确保表中有数据
        conn = db_manager.get_conn()
        cursor = conn.cursor()

        cursor.execute('DELETE FROM setting')
        cursor.execute(
            'INSERT INTO setting (api_key, active_features) VALUES (?, ?)',
            (api_key, json.dumps([]))
        )

        conn.commit()
        conn.close()

        await set_apikey.send(f"API Key 已更新: {api_key}")

    except Exception as e:
        await set_apikey.finish(f"更新失败: {e}")


@active_group.handle()
async def handle_active_groups(event: Event, args: Message = CommandArg()):
    group_id = getattr(event, 'group_id', None)
    full_text = args.extract_plain_text().strip()
    parts = full_text.split()

    if len(parts) >= 3 and parts[0] == "监视":
        await handle_monitor_command(event, parts[1:])
        return

    # 撤回提示语设置
    if len(parts) >= 2 and parts[0] == "撤回提示语":
        withdraw_prompt = " ".join(parts[1:]).strip()
        if not withdraw_prompt:
            await active_group.finish("用法: /blocker 撤回提示语 <提示语内容>")
        try:
            # ensure_api_keys_exists()
            conn = db_manager.get_conn()
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM setting')
            count = cursor.fetchone()[0]

            if count == 0:
                cursor.execute(
                    'INSERT INTO setting (withdraw_prompt) VALUES (?)', (withdraw_prompt,))
            else:
                cursor.execute(
                    'UPDATE setting SET withdraw_prompt = ?', (withdraw_prompt,))

            conn.commit()
            conn.close()
            await active_group.send(f"✅撤回提示语已更新为: {withdraw_prompt}")
        except Exception as e:
            await active_group.finish(f"❌ 更新失败: {e}")
        return

    # 查询功能
    if "查询" in full_text:
        page = 1
        if len(parts) >= 2 and parts[1].isdigit():
            page = int(parts[1])

        if isinstance(event, PrivateMessageEvent):
            if len(parts) >= 3 and parts[2].isdigit():
                target_group_id = int(parts[2])
                await query_user_remaining_queries(target_group_id, page)
            else:
                await query_all_records(page)
        elif isinstance(event, GroupMessageEvent):
            await query_user_remaining_queries(group_id, page)
        return

    # 群聊专用功能
    if not isinstance(event, GroupMessageEvent):
        await active_group.finish(
            "📚 广告屏蔽插件使用说明\n\n"
            "🛠️ 超级管理员命令:\n"
            "/set_apikey <key> - 设置DeepSeek API密钥\n"
            "/active_groups [群号列表] - 批量设置激活群组\n\n"
            "👥 群管理/超级管理员命令:\n"
            "/blocker 1 - 在当前群启用广告屏蔽\n"
            "/blocker 0 - 在当前群禁用广告屏蔽\n"
            "/blocker 监视 <用户ID> <次数> - 监视指定用户(1-50次)\n"
            "/blocker 撤回提示语 <内容> - 设置撤回消息时的提示语\n\n"
            "📊 查询命令:\n"
            "群聊: /blocker 查询 [页码] - 查询本群记录\n"
            "私聊: /blocker 查询 [页码] [群号] - 查询指定群记录\n"
            "私聊: /blocker 查询 [页码] - 查询所有群记录\n\n"
            "ℹ️ 权限说明:\n"
            "• 群主/管理员: 可管理本群设置\n"
            "• 超级管理员: 可管理所有群和全局设置"
        )

    if full_text not in ["1", "0"]:
        await active_group.finish(
            "📚 广告屏蔽插件 - 群聊用法\n\n"
            "🔧 基本控制:\n"
            "/blocker 1 - 启用广告屏蔽\n"
            "/blocker 0 - 禁用广告屏蔽\n\n"
            "👤 用户监视:\n"
            "/blocker 监视 <用户ID/用户名> <次数> - 监视用户消息(1-50次)\n"
            "示例: /blocker 监视 123456 5\n\n"
            "💬 提示语设置:\n"
            "/blocker 撤回提示语 <内容> - 设置撤回消息时的提示\n\n"
            "📋 记录查询:\n"
            "/blocker 查询 - 查看本群第1页记录\n"
            "/blocker 查询 2 - 查看本群第2页记录\n\n"
            "ℹ️ 需要群主/管理员权限"
        )

    try:
        # ensure_api_keys_exists()
        conn = db_manager.get_conn()
        cursor = conn.cursor()

        cursor.execute('SELECT active_features FROM setting LIMIT 1')
        result = cursor.fetchone()
        current_groups = json.loads(result[0]) if result and result[0] else []

        if full_text == "1":
            if group_id not in current_groups:
                current_groups.append(group_id)
                cursor.execute(
                    'UPDATE setting SET active_features = ?', (json.dumps(current_groups),))
                await active_group.send(f"✅ 广告屏蔽已启用: {group_id}")
            else:
                await active_group.send(f"✅ 群 {group_id} 已启用")
        else:
            if group_id in current_groups:
                current_groups.remove(group_id)
                cursor.execute(
                    'UPDATE setting SET active_features = ?', (json.dumps(current_groups),))
                await active_group.send(f"✅ 广告屏蔽已禁用: {group_id}")
            else:
                await active_group.send(f"✅ 群 {group_id} 未启用")

        conn.commit()
        conn.close()

    except Exception as e:
        await active_group.finish(f"❌ 操作失败: {e}")

async def query_all_records(page: int = 1, page_size: int = 30):
    """查询所有记录（不分群组）"""
    try:
        conn = db_manager.get_conn()
        cursor = conn.cursor()

        cursor.execute('SELECT COUNT(*) FROM blocked_ads')
        total_records = cursor.fetchone()[0]

        if total_records == 0:
            await active_group.send("暂无记录")
            return

        total_pages = (total_records + page_size - 1) // page_size
        page = max(1, min(page, total_pages))
        offset = (page - 1) * page_size

        cursor.execute('''
            SELECT qid, group_id, messages_number , maxlisten
            FROM blocked_ads 
            ORDER BY group_id, messages_number DESC 
            LIMIT ? OFFSET ?
        ''', (page_size, offset))

        results = cursor.fetchall()
        conn.close()

        message_lines = [
            f"📊 所有记录 - 第 {page}/{total_pages} 页 (共{total_records}条)\n"]

        current_group = None
        for qid, group_id, messages_number ,maxlisten in results:
            if group_id != current_group:
                message_lines.append(f"\n👥 群 {group_id}:")
                current_group = group_id

            remaining_times = maxlisten - messages_number
            status = "监听中" if remaining_times > 0 else "即将完成记录"
            message_lines.append(
                f"  QQ {qid}: 已{messages_number}次，剩{remaining_times}次 ({status})")

        if total_pages > 1:
            message_lines.append(f"\n📄 /blocker 查询 {page+1} 下一页")

        full_message = "\n".join(message_lines)

        # 消息分割
        if len(full_message) > 1000:
            chunks = []
            current_chunk = []
            current_length = 0

            for line in message_lines:
                line_length = len(line) + 1
                if current_length + line_length > 1000:
                    chunks.append("\n".join(current_chunk))
                    current_chunk = [line]
                    current_length = line_length
                else:
                    current_chunk.append(line)
                    current_length += line_length

            if current_chunk:
                chunks.append("\n".join(current_chunk))

            for i, chunk in enumerate(chunks):
                if i == 0:
                    await active_group.send(chunk)
                else:
                    await active_group.send(f"...(续){chunk}")
        else:
            await active_group.send(full_message)

    except Exception as e:
        logger.error(f"查询失败: {e}")
        await active_group.finish(f"❌ 查询失败: {e}")


async def query_user_remaining_queries(group_id: int, page: int = 1):
    """查询指定群组记录"""
    try:
        conn = db_manager.get_conn()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT COUNT(*) FROM blocked_ads WHERE group_id = ?', (group_id,))
        total_users = cursor.fetchone()[0]

        if total_users == 0:
            await active_group.send(f"群 {group_id} 无记录")
            return

        page_size = 30
        total_pages = (total_users + page_size - 1) // page_size
        page = max(1, min(page, total_pages))
        offset = (page - 1) * page_size

        cursor.execute(
            'SELECT qid, messages_number FROM blocked_ads WHERE group_id = ? ORDER BY messages_number DESC LIMIT ? OFFSET ?',
            (group_id, page_size, offset)
        )
        results = cursor.fetchall()
        conn.close()

        message_lines = [f"📊 群 {group_id} - 第 {page}/{total_pages} 页\n"]

        for qid, messages_number in results:
            remaining_times = db_manager.get_listen(user_id=qid,group_id=group_id) - messages_number
            status = "🟡 记录中" if remaining_times > 0 else "🟢 即将移出"
            message_lines.append(
                f"QQ {qid}: 已{messages_number}次，剩{remaining_times}次 ({status})")

        if total_pages > 1:
            message_lines.append(f"\n📄 /blocker 查询 {page+1} {group_id} 下一页")

        await active_group.send("\n".join(message_lines))

    except Exception as e:
        logger.error(f"查询失败: {e}")
        await active_group.finish(f"❌ 查询失败: {e}")

@set_active_groups.handle()
async def handle_set_active_groups(event: Event, args: Message = CommandArg()):
    args_text = args.extract_plain_text().strip()

    if not args_text:
        active_groups = db_manager.get_active_groups()
        await set_active_groups.finish(f"当前激活群组: {active_groups}")

    try:
        # 解析群组列表，支持多种格式：123,456,789 或 [123,456,789]
        if args_text.startswith('[') and args_text.endswith(']'):
            groups = json.loads(args_text)
        else:
            groups = [int(g.strip())
                      for g in args_text.split(',') if g.strip()]

        # db_manager.ensure_api_keys_exists()  # 确保表中有数据
        conn = db_manager.get_conn()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE setting SET active_features = ?',
            (json.dumps(groups),)
        )
        conn.commit()
        conn.close()

        await set_active_groups.send(f"已设置激活群组: {groups}")

    except Exception as e:
        await set_active_groups.finish(f"设置失败: {e}")


@group_increase_handler.handle()
async def handle_group_increase(event: GroupIncreaseNoticeEvent):
    if event.notice_type == "group_increase":
        user_id = event.user_id
        group_id = event.group_id

        logger.debug(f"处理群成员增加: 用户{user_id} 加入群{group_id}")

        if not db_manager.is_group_enabled(group_id):
            logger.debug(f"群{group_id} 未启用广告屏蔽，跳过处理")
            return

        try:
            conn = db_manager.get_conn()
            cursor = conn.cursor()

            cursor.execute(
                'SELECT messages_number FROM blocked_ads WHERE qid = ? AND group_id = ?',
                (user_id, group_id)
            )
            result = cursor.fetchone()

            if result:
                # 如果用户已存在记录，重置计数为1（重新开始记录）
                cursor.execute(
                    'UPDATE blocked_ads SET messages_number = ? WHERE qid = ? AND group_id = ?',
                    (1, user_id, group_id)
                )
                logger.debug(f"用户{user_id} 在群{group_id} 重新加入，重置计数为1")
            else:
                # 新用户，创建记录，计数从1开始
                cursor.execute(
                    'INSERT INTO blocked_ads (qid, group_id, messages_number) VALUES (?, ?, ?)',
                    (user_id, group_id, 1)
                )
                logger.debug(f"新用户{user_id} 在群{group_id} 加入，初始化计数为1")

            conn.commit()
            conn.close()

        except Exception as e:
            logger.error(f"处理群成员增加事件失败: {e}")
            if conn:
                conn.close()


async def process_user_message(user_id: int, group_id: int, message: str) -> bool:
    """
    处理用户消息的主要函数
    逻辑：用户最多记录4次消息，达到4次后移除记录

    Args:
        user_id: 用户ID
        group_id: 群组ID
        message: 消息内容

    Returns:
        bool: True表示检测到广告需要处理，False表示正常消息
    """
    try:
        conn = db_manager.get_conn()
        cursor = conn.cursor()

        cursor.execute(
            'SELECT messages_number FROM blocked_ads WHERE qid = ? AND group_id = ?',
            (user_id, group_id)
        )
        result = cursor.fetchone()

        if not result:
            conn.close()
            logger.debug(f"用户 {user_id} 在群 {group_id} 无记录")
            return False

        messages_number = result[0]


        threshold = db_manager.get_listen(user_id, group_id)

        if messages_number >= threshold:
            cursor.execute(
                'DELETE FROM blocked_ads WHERE qid = ? AND group_id = ?',
                (user_id, group_id)
            )
            conn.commit()
            conn.close()
            logger.info(f"用户 {user_id} 在群 {group_id} 已完成{threshold}次记录，移除记录")
            return False

        conn.close()
        has_ad = await check_ad_content(message, user_id, group_id)

        conn = db_manager.get_conn()
        cursor = conn.cursor()

        if has_ad:
            conn.close()
            logger.info(
                f"用户 {user_id} 在群 {group_id} 第{messages_number + 1}次消息检测到广告，计数不变: {messages_number}")
            return True
        else:
            new_count = messages_number + 1

            if new_count >= threshold:
                cursor.execute(
                    'DELETE FROM blocked_ads WHERE qid = ? AND group_id = ?',
                    (user_id, group_id)
                )
                logger.info(f"用户 {user_id} 在群 {group_id} 完成{threshold}次记录未发现广告，记录已移除")
            else:
                cursor.execute(
                    'UPDATE blocked_ads SET messages_number = ? WHERE qid = ? AND group_id = ?',
                    (new_count, user_id, group_id)
                )
                logger.debug(
                    f"用户 {user_id} 在群 {group_id} 第{new_count}次消息未发现广告，继续记录")

            conn.commit()
            conn.close()
            return False

    except Exception as e:
        logger.error(f"处理用户消息时发生错误: {e}")
        if 'conn' in locals():
            conn.close()
        return False

@message_handler.handle()
async def handle_group_message(bot: Bot, event: GroupMessageEvent):
    # send_notice = False
    user_id = event.user_id
    group_id = event.group_id
    message = event.get_plaintext().strip()
    message_id = event.message_id

    raw_message = event.get_message()
    image_segments = [seg for seg in raw_message if seg.type == 'image']

    if not db_manager.is_group_enabled(group_id):
        return

    if not message and not image_segments:
        return

    if image_segments:
        for image_seg in image_segments:
            image_url = image_seg.data.get('url', '')
            # logger.info(f"检测到图片图片URL: {image_url}")
            if image_url:
                has_qrcode = await catch_qrcode(image_url)
                if has_qrcode:
                    logger.info(
                        f"检测到广告消息（二维码），用户: {user_id}, 群: {group_id}, 图片URL: {image_url}")
                    try:
                        await bot.delete_msg(message_id=message_id)
                        logger.info(
                            f"已撤回含二维码图片消息 来自用户 {user_id} 在群 {group_id}")
                        await bot.send_group_msg(
                            group_id=group_id,
                            message=db_manager.get_withdraw_prompt()
                        )
                        await notify_superusers(bot, user_id, group_id, f"[图片消息含二维码] URL: {image_url}")

                    except Exception as e:
                        logger.error(f"处理含二维码图片消息时出错: {e}")
                    return  # no need to check text message

    should_block = await process_user_message(user_id, group_id, message)

    if should_block:
        logger.info(f"检测到广告消息，用户: {user_id}, 群: {group_id}, 内容: {message}")

        try:
            await bot.delete_msg(message_id=message_id)
            logger.info(f"已撤回消息: {message} 来自用户 {user_id} 在群 {group_id}")
            await bot.send_group_msg(
                group_id=group_id,
                message=db_manager.get_withdraw_prompt()
            )
            await notify_superusers(bot, user_id, group_id, message)

        except Exception as e:
            logger.error(f"处理广告消息时出错: {e}")


async def notify_superusers(bot: Bot, user_id: int, group_id: int, message: str):
    """
    给所有超级管理员发送私信通知

    Args:
        bot: Bot实例
        user_id: 发送广告的用户ID
        group_id: 群组ID
        message: 广告消息内容
    """
    try:
        superusers = get_driver().config.superusers

        if not superusers:
            logger.warning("未配置超级管理员，无法发送通知")
            return

        notification = (
            f"🚨 广告消息已处理\n"
            f"用户: {user_id}\n"
            f"群组: {group_id}\n"
            f"内容: {message}\n"
            f"时间: {get_current_time()}"
        )

        for superuser in superusers:
            try:
                await bot.send_private_msg(
                    user_id=int(superuser),
                    message=notification
                )
                logger.info(f"已向超级管理员 {superuser} 发送通知")
            except Exception as e:
                logger.error(f"向超级管理员 {superuser} 发送通知失败: {e}")

    except Exception as e:
        logger.error(f"发送超级管理员通知时出错: {e}")


async def check_ad_content(message: str, user_id: int, group_id: int) -> bool:
    try:
        logger.debug(f"调用广告检测API，用户: {user_id}, 群: {group_id}, 内容: {message}")
        conn = db_manager.get_conn()
        cursor = conn.cursor()
        cursor.execute('SELECT api_key FROM setting LIMIT 1')
        result = cursor.fetchone()
        conn.close()

        if not result or not result[0]:
            logger.warning("未设置API Key")
            return False

        api_key = result[0]

        payload = {
            "model": "deepseek-chat",
            "messages": [
                {
                    "role": "system",
                    "content": "广告检测AI。只返回true或false。广告类型：商业推广、兼职刷单、优惠促销、外部链接、联系方式、赌博色情。"
                },
                {
                    "role": "user",
                    "content": f"判断消息是否有广告嫌疑：{message}"
                }
            ],
            "max_tokens": 10,
            "temperature": 0.1
        }

        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                "https://api.deepseek.com/chat/completions",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json"
                },
                json=payload
            )

            if response.status_code == 200:
                data = response.json()
                result_text = data["choices"][0]["message"]["content"].strip(
                ).lower()
                logger.debug(f"广告检测API响应: {result_text}")
                if "true" in result_text:
                    return True
                elif "false" in result_text:
                    return False
                else:
                    return await fallback_ad_check(message)
            else:
                logger.error(f"API调用失败: {response.status_code}")
                return await fallback_ad_check(message)

    except httpx.TimeoutException:
        logger.error("API调用超时")
        return await fallback_ad_check(message)
    except Exception as e:
        logger.error(f"检查广告内容错误: {e}")
        return await fallback_ad_check(message)


async def fallback_ad_check(message: str) -> bool:
    """
    备用广告检测逻辑（当API调用失败时使用）
    """
    ad_keywords = [
        "刷单", "兼职", "赚钱", "优惠", "特价", "促销", "折扣",
        "充值", "代练", "包赢", "福利群", "加微信", "加QQ",
        "联系", "私聊", "低价", "优惠券", "红包群", "投资",
        "理财", "股票", "期货", "数字货币", "比特币"
    ]

    message_lower = message.lower()
    for keyword in ad_keywords:
        if keyword in message_lower:
            return True
    return False

async def handle_monitor_command(event: Event, args: list):
    """处理监视命令"""
    try:
        # 获取 bot 对象
        from nonebot import get_bot
        bot = get_bot()

        # 解析参数
        if isinstance(event, PrivateMessageEvent):
            # 私聊: /blocker 监视 <群号> <用户名/用户ID> <次数>
            if len(args) < 3:
                await active_group.send("私聊用法: /blocker 监视 <群号> <用户ID> <次数>")
                return

            group_id = int(args[0])
            user_identifier = args[1]
            times = int(args[2])

            # 验证群组是否存在且bot在群中
            if not await verify_group_exists(bot, group_id):
                await active_group.send(f"❌ 群 {group_id} 不存在或机器人不在该群中")
                return

            # 验证用户是否在群中
            user_id = await parse_user_identifier(user_identifier, group_id, bot)
            if not user_id:
                await active_group.send(f"❌ 用户 {user_identifier} 不在群 {group_id} 中")
                return

        else:
            # 群聊: /blocker 监视 <用户名/用户ID> <次数>
            if len(args) < 2:
                await active_group.send("群聊用法: /blocker 监视 <用户名/用户ID> <次数>")
                return

            group_id = event.group_id
            user_identifier = args[0]
            times = int(args[1])

            # 验证用户是否存在
            user_id = await parse_user_identifier(user_identifier, group_id, bot)
            if not user_id:
                await active_group.send(f"❌ 用户 {user_identifier} 不在本群中")
                return

        # 验证次数范围
        if times < 1 or times > 10:
            await active_group.send("❌ 监视次数范围: 1-10")
            return

        # 检查是否已存在记录
        listen_time = db_manager.get_listen(user_id, group_id)
        if listen_time:
            # current_times = existing_record[2]
            action = "更新" if times != listen_time else "保持"
            db_manager.update_user_record(user_id, group_id, times)
            await active_group.send(
                f"✅ 已{action}监视用户 {user_id} 在群 {group_id}\n"
                f"原监视次数: {listen_time} → 新监视次数: {times}"
            )
        else:
            # 新增记录
            db_manager.update_user_record(user_id, group_id, times)
            await active_group.send(f"✅ 已开始监视用户 {user_id} 在群 {group_id}，监视次数: {times}")

        logger.info(f"用户 {event.user_id} 设置监视: 群{group_id} 用户{user_id} 次数{times}")

    except ValueError:
        await active_group.send("❌ 参数错误: 群号和次数必须是数字")
    except Exception as e:
        logger.error(f"处理监视命令失败: {e}")
        await active_group.send(f"❌ 设置监视失败: {e}")

async def verify_group_exists(bot: Bot, group_id: int) -> bool:
    """验证群组是否存在且机器人在群中"""
    try:
        group_list = await bot.get_group_list()
        return any(group['group_id'] == group_id for group in group_list)
    except Exception as e:
        logger.error(f"验证群组存在失败: {e}")
        return False

async def parse_user_identifier(identifier: str, group_id: int, bot) -> int:
    """解析用户标识符，返回用户ID，如果用户不存在返回0"""
    try:
        # 如果标识符是纯数字，直接作为用户ID
        if identifier.isdigit():
            user_id = int(identifier)

            # 验证用户是否在群中
            if await verify_user_in_group(bot, group_id, user_id):
                return user_id
            else:
                return 0

        else:
            # 如果是用户名，需要在群聊中解析
            # 获取群成员列表
            member_list = await bot.get_group_member_list(group_id=group_id)

            # 搜索匹配的用户名（更宽松的匹配）
            matched_members = []
            for member in member_list:
                member_card = member.get('card', '')  # 群名片
                member_nickname = member.get('nickname', '')  # 昵称

                # 调试日志
                logger.debug(f"检查用户: 群名片='{member_card}', 昵称='{member_nickname}', ID={member['user_id']}")

                # 更宽松的匹配：包含关系且忽略大小写
                if (identifier in member_card or 
                    identifier in member_nickname or
                    identifier.lower() in member_card.lower() or 
                    identifier.lower() in member_nickname.lower()):
                    matched_members.append(member)

            if not matched_members:
                logger.warning(f"未找到匹配用户: '{identifier}' 在群 {group_id}")
                return 0

            if len(matched_members) > 1:
                # 多个匹配，返回列表让用户选择
                user_list = "\n".join([
                    f"{i+1}. {m.get('card', m.get('nickname', '未知'))} (ID: {m['user_id']})" 
                    for i, m in enumerate(matched_members[:5])  # 最多显示5个
                ])
                # 使用 send 而不是 finish，避免异常
                await active_group.send(
                    f"找到多个匹配用户:\n{user_list}\n"
                    f"请使用用户ID重新指定: /blocker 监视 <用户ID> <次数>"
                )
                return 0

            # 只有一个匹配
            user_id = matched_members[0]['user_id']
            logger.info(f"用户名 '{identifier}' 匹配到用户ID: {user_id}")
            return user_id

    except Exception as e:
        logger.error(f"解析用户标识符失败: {e}")
        return 0

async def verify_user_in_group(bot, group_id: int, user_id: int) -> bool:
    """验证用户是否在群中"""
    try:
        member_info = await bot.get_group_member_info(
            group_id=group_id,
            user_id=user_id,
            no_cache=False  # 使用缓存提高性能
        )
        return bool(member_info)
    except Exception as e:
        logger.warning(f"验证用户 {user_id} 在群 {group_id} 中失败: {e}")
        return False