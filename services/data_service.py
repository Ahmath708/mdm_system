from typing import Optional, List, Dict
from datetime import datetime
from config.database import DatabaseConfig
import json

class MasterDataService:

    @staticmethod
    def create_master_data(data_set_name: str, data_type: str, data_value: str, user_id: int) -> int:
        with DatabaseConfig.get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO master_data (data_set_name, data_type, data_value, created_by)
                VALUES (?, ?, ?, ?)
            """, (data_set_name, data_type, data_value, user_id))
            record_id = cursor.lastrowid
            MasterDataService._log_audit(user_id, "CREATE", "master_data", record_id, None, data_value)
            return record_id

    @staticmethod
    def update_master_data(record_id: int, data: dict, user_id: int) -> bool:
        with DatabaseConfig.get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM master_data WHERE id = ?", (record_id,))
            old_record = cursor.fetchone()
            if not old_record:
                return False

            updates = []
            values = []
            for key, value in data.items():
                if value is not None:
                    updates.append(f"{key} = ?")
                    values.append(value)

            if not updates:
                return False

            values.append(record_id)
            with DatabaseConfig.get_db_cursor(commit=True) as cursor:
                cursor.execute(f"UPDATE master_data SET {', '.join(updates)} WHERE id = ?", values)
                MasterDataService._log_audit(user_id, "UPDATE", "master_data", record_id, 
                                           str(dict(old_record)), str(data))
                return cursor.rowcount > 0

    @staticmethod
    def delete_master_data(record_id: int, user_id: int) -> bool:
        with DatabaseConfig.get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM master_data WHERE id = ?", (record_id,))
            old_record = cursor.fetchone()
            if not old_record:
                return False

        with DatabaseConfig.get_db_cursor(commit=True) as cursor:
            cursor.execute("DELETE FROM master_data WHERE id = ?", (record_id,))
            MasterDataService._log_audit(user_id, "DELETE", "master_data", record_id, 
                                       str(dict(old_record)), None)
            return cursor.rowcount > 0

    @staticmethod
    def get_master_data(record_id: int) -> Optional[dict]:
        with DatabaseConfig.get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM master_data WHERE id = ?", (record_id,))
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None

    @staticmethod
    def get_all_master_data(data_set_name: Optional[str] = None, status: Optional[str] = None) -> List[dict]:
        query = "SELECT * FROM master_data WHERE 1=1"
        params = []
        if data_set_name:
            query += " AND data_set_name = ?"
            params.append(data_set_name)
        if status:
            query += " AND status = ?"
            params.append(status)

        with DatabaseConfig.get_db_cursor() as cursor:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def decommission_data_set(data_set_name: str, user_id: int) -> bool:
        with DatabaseConfig.get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE master_data 
                SET status = 'decommissioned' WHERE data_set_name = ?
            """, (data_set_name,))
            MasterDataService._log_audit(user_id, "DECOMMISSION", "master_data", None, 
                                       data_set_name, "decommissioned")
            return cursor.rowcount > 0

    @staticmethod
    def commission_data_set(data_set_name: str, user_id: int) -> bool:
        with DatabaseConfig.get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                UPDATE master_data 
                SET status = 'active' WHERE data_set_name = ?
            """, (data_set_name,))
            MasterDataService._log_audit(user_id, "COMMISSION", "master_data", None, 
                                       data_set_name, "active")
            return cursor.rowcount > 0

    @staticmethod
    def _log_audit(user_id: int, action: str, table_name: str, record_id: Optional[int], 
                   old_value: Optional[str], new_value: Optional[str]):
        with DatabaseConfig.get_db_cursor(commit=True) as cursor:
            cursor.execute("""
                INSERT INTO audit_logs (user_id, action, table_name, record_id, old_value, new_value)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (user_id, action, table_name, record_id, old_value, new_value))

    @staticmethod
    def get_audit_logs(table_name: Optional[str] = None, record_id: Optional[int] = None) -> List[dict]:
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []
        if table_name:
            query += " AND table_name = ?"
            params.append(table_name)
        if record_id:
            query += " AND record_id = ?"
            params.append(record_id)
        query += " ORDER BY created_at DESC"

        with DatabaseConfig.get_db_cursor() as cursor:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]