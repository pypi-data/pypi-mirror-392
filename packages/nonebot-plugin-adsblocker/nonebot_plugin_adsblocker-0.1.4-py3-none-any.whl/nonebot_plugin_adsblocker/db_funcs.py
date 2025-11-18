import sqlite3
import nonebot_plugin_localstore as store
from nonebot.log import logger
import json
from pathlib import Path
from typing import List, Optional, Tuple, Any


class DatabaseManager:
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            db_path = store.get_plugin_data_dir() / "bot_data.db"

        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        logger.info(f"数据库路径: {self.db_path}")
        self.init_db()

    def get_conn(self) -> sqlite3.Connection:
        return sqlite3.connect(str(self.db_path))

    def init_db(self):
        with self.get_conn() as conn:
            conn.executescript('''
                CREATE TABLE IF NOT EXISTS blocked_ads (
                    qid INTEGER,
                    group_id INTEGER,
                    messages_number INTEGER DEFAULT 0,
                    PRIMARY KEY (qid, group_id)
                    
                );
                
                CREATE TABLE IF NOT EXISTS setting (
                    api_key TEXT DEFAULT '',
                    active_features TEXT DEFAULT '[]',
                    withdraw_prompt TEXT DEFAULT '猫猫吃掉了一条坏消息 请不要发啦~'
                );
            ''')
            conn.commit()
        logger.info("数据库初始化完成")
        self.ensure_setting_exists()

    def ensure_setting_exists(self):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM setting')
            count = cursor.fetchone()[0]
            if count == 0:
                cursor.execute(
                    'INSERT INTO setting (api_key, active_features) VALUES (?, ?)',
                    ("", "[]")
                )
                conn.commit()
                logger.info("已初始化setting表")

    def get_active_groups(self) -> List[int]:
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT active_features FROM setting LIMIT 1')
            result = cursor.fetchone()

            if result and result[0]:
                return json.loads(result[0])
            return []

    def update_active_groups(self, groups: List[int]):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE setting SET active_features = ?',
                (json.dumps(groups),)
            )
            conn.commit()

    def get_api_key(self) -> str:
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT api_key FROM setting LIMIT 1')
            result = cursor.fetchone()
            return result[0] if result else ""

    def update_api_key(self, api_key: str):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE setting SET api_key = ?', (api_key,))
            conn.commit()

    def get_withdraw_prompt(self) -> str:
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT withdraw_prompt FROM setting LIMIT 1')
            result = cursor.fetchone()
            return result[0] if result else "猫猫吃掉了一条坏消息 请不要发啦~"

    def update_withdraw_prompt(self, prompt: str):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute('UPDATE setting SET withdraw_prompt = ?', (prompt,))
            conn.commit()

    def get_user_record(self, user_id: int, group_id: int) -> Optional[Tuple[int, int, int]]:
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT qid, group_id, messages_number FROM blocked_ads WHERE qid = ? AND group_id = ?',
                (user_id, group_id)
            )
            return cursor.fetchone()

    def update_user_record(self, user_id: int, group_id: int, maxlisten: int):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''INSERT OR REPLACE INTO blocked_ads (qid, group_id, messages_number , maxlisten) 
                   VALUES (?, ?,?, ?)''',
                (user_id, group_id, 0, maxlisten)
            )
            conn.commit()

    def delete_user_record(self, user_id: int, group_id: int):
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'DELETE FROM blocked_ads WHERE qid = ? AND group_id = ?',
                (user_id, group_id)
            )
            conn.commit()

    def get_group_records(self, group_id: int, limit: int = 30, offset: int = 0) -> List[Tuple[int, int]]:
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT qid, messages_number FROM blocked_ads 
                   WHERE group_id = ? ORDER BY messages_number DESC 
                   LIMIT ? OFFSET ?''',
                (group_id, limit, offset)
            )
            return cursor.fetchall()

    def get_all_records(self, limit: int = 30, offset: int = 0) -> List[Tuple[int, int, int]]:
        with self.get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute(
                '''SELECT qid, group_id, messages_number FROM blocked_ads 
                   ORDER BY group_id, messages_number DESC 
                   LIMIT ? OFFSET ?''',
                (limit, offset)
            )
            return cursor.fetchall()

    def get_records_count(self, group_id: Optional[int] = None) -> int:
        with self.get_conn() as conn:
            cursor = conn.cursor()
            if group_id:
                cursor.execute(
                    'SELECT COUNT(*) FROM blocked_ads WHERE group_id = ?', (group_id,))
            else:
                cursor.execute('SELECT COUNT(*) FROM blocked_ads')
            return cursor.fetchone()[0]

    def is_group_enabled(self, group_id: int) -> bool:
        active_groups = self.get_active_groups()
        return group_id in active_groups

    def add_column_to_table(self, table_name: str, column_name: str, column_type: str = "TEXT", default_value: Any = None):
        """
        动态为表添加字段

        Args:
            table_name: 表名
            column_name: 字段名
            column_type: 字段类型，默认为 TEXT
            default_value: 默认值，如果为None则不设置默认值
        """
        try:
            with self.get_conn() as conn:
                cursor = conn.cursor()

                cursor.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
                if not cursor.fetchone():
                    logger.warning(f"表 {table_name} 不存在")
                    return False

                cursor.execute(f"PRAGMA table_info({table_name})")
                existing_columns = [col[1] for col in cursor.fetchall()]

                if column_name in existing_columns:
                    logger.info(f"字段 {column_name} 在表 {table_name} 中已存在")
                    return True

                alter_sql = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"
                if default_value is not None:
                    if isinstance(default_value, str):
                        alter_sql += f" DEFAULT '{default_value}'"
                    else:
                        alter_sql += f" DEFAULT {default_value}"

                cursor.execute(alter_sql)
                conn.commit()
                logger.info(
                    f"成功为表 {table_name} 添加字段 {column_name} {column_type}")
                return True

        except Exception as e:
            logger.error(f"为表 {table_name} 添加字段 {column_name} 时出错: {e}")
            return False

    def get_listen(self, user_id: int, group_id: int) -> int:
        """
        Args:
            user_id: 用户ID
            group_id: 群组ID

        Returns:
            maxlisten字段的值 默认为3
        """
        try:
            with self.get_conn() as conn:
                cursor = conn.cursor()

                cursor.execute("PRAGMA table_info(blocked_ads)")
                columns = [col[1] for col in cursor.fetchall()]

                if "maxlisten" not in columns:
                    logger.info("maxlisten字段不存在，使用默认值3")
                    return 3

                cursor.execute(
                    'SELECT maxlisten FROM blocked_ads WHERE qid = ? AND group_id = ?',
                    (user_id, group_id)
                )
                result = cursor.fetchone()

                if result is None or result[0] is None:
                    return 3

                return int(result[0])

        except Exception as e:
            logger.error(f"获取maxlisten字段时出错: {e}")
            return 3


dbManager = DatabaseManager()
dbManager.add_column_to_table(
    "blocked_ads", "maxlisten", "INTEGER", "3")
