from typing import List, Dict, Optional, Any
from datetime import datetime
from config.database import DatabaseConfig
import json
import re

class DataQualityService:
    VALIDATION_RULES = {
        "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
        "phone": r"^\+?1?\d{9,15}$",
        "numeric": r"^-?\d+(\.\d+)?$",
        "date": r"^\d{4}-\d{2}-\d{2}$",
        "alphanumeric": r"^[a-zA-Z0-9]+$"
    }

    @staticmethod
    def validate_data(data: dict, validation_rules: dict) -> Dict[str, Any]:
        errors = []
        is_valid = True

        for field, rule in validation_rules.items():
            value = data.get(field)
            if rule.get("required") and (value is None or value == ""):
                errors.append(f"Field '{field}' is required")
                is_valid = False
                continue

            if value:
                data_type = rule.get("type", "string")
                if data_type == "email":
                    if not re.match(DataQualityService.VALIDATION_RULES["email"], str(value)):
                        errors.append(f"Invalid email format for '{field}'")
                        is_valid = False
                elif data_type == "numeric":
                    if not re.match(DataQualityService.VALIDATION_RULES["numeric"], str(value)):
                        errors.append(f"Invalid numeric value for '{field}'")
                        is_valid = False
                elif data_type == "date":
                    try:
                        datetime.strptime(str(value), "%Y-%m-%d")
                    except ValueError:
                        errors.append(f"Invalid date format for '{field}'")
                        is_valid = False
                elif data_type == "phone":
                    if not re.match(DataQualityService.VALIDATION_RULES["phone"], str(value)):
                        errors.append(f"Invalid phone format for '{field}'")
                        is_valid = False

        return {"is_valid": is_valid, "errors": errors}

    @staticmethod
    def import_data(data_list: List[dict], data_set_name: str, validation_rules: dict) -> Dict[str, Any]:
        total_records = len(data_list)
        valid_records = 0
        invalid_records = 0

        with DatabaseConfig.get_db_cursor(commit=True) as cursor:
            for data in data_list:
                validation_result = DataQualityService.validate_data(data, validation_rules)
                is_valid = validation_result["is_valid"]
                error_message = "; ".join(validation_result["errors"]) if validation_result["errors"] else None

                data_value = json.dumps(data)
                cursor.execute("""
                    INSERT INTO master_data (data_set_name, data_type, data_value, created_by)
                    VALUES (?, ?, ?, 1)
                """, (data_set_name, "imported", data_value))

                record_id = cursor.lastrowid
                cursor.execute("""
                    INSERT INTO data_quality_logs (record_id, data_set_name, validation_type, is_valid, error_message)
                    VALUES (?, ?, ?, ?, ?)
                """, (record_id, data_set_name, "import", 1 if is_valid else 0, error_message))

                if is_valid:
                    valid_records += 1
                else:
                    invalid_records += 1

        accuracy = (valid_records / total_records * 100) if total_records > 0 else 0

        return {
            "total_records": total_records,
            "valid_records": valid_records,
            "invalid_records": invalid_records,
            "accuracy": round(accuracy, 2),
            "data_set_name": data_set_name
        }

    @staticmethod
    def get_quality_report(data_set_name: str) -> Dict[str, Any]:
        with DatabaseConfig.get_db_cursor() as cursor:
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_records,
                    SUM(CASE WHEN is_valid = 1 THEN 1 ELSE 0 END) as valid_records,
                    SUM(CASE WHEN is_valid = 0 THEN 1 ELSE 0 END) as invalid_records
                FROM data_quality_logs
                WHERE data_set_name = ?
            """, (data_set_name,))
            result = cursor.fetchone()

            if result and result["total_records"]:
                accuracy = (result["valid_records"] / result["total_records"]) * 100
                return {
                    "total_records": result["total_records"],
                    "valid_records": result["valid_records"],
                    "invalid_records": result["invalid_records"],
                    "accuracy": round(accuracy, 2),
                    "data_set_name": data_set_name,
                    "validation_date": datetime.utcnow()
                }
            return {
                "total_records": 0,
                "valid_records": 0,
                "invalid_records": 0,
                "accuracy": 0.0,
                "data_set_name": data_set_name,
                "validation_date": datetime.utcnow()
            }

    @staticmethod
    def validate_existing_data(data_set_name: str, validation_rules: dict) -> Dict[str, Any]:
        with DatabaseConfig.get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM master_data WHERE data_set_name = ?", (data_set_name,))
            records = cursor.fetchall()

        valid_count = 0
        invalid_count = 0
        logs = []

        for record in records:
            try:
                data = json.loads(record["data_value"])
            except:
                data = {"data_value": record["data_value"]}

            validation_result = DataQualityService.validate_data(data, validation_rules)
            is_valid = validation_result["is_valid"]

            if is_valid:
                valid_count += 1
            else:
                invalid_count += 1

            logs.append({
                "record_id": record["id"],
                "is_valid": is_valid,
                "errors": validation_result["errors"]
            })

        total = valid_count + invalid_count
        accuracy = (valid_count / total * 100) if total > 0 else 0

        return {
            "total_records": total,
            "valid_records": valid_count,
            "invalid_records": invalid_count,
            "accuracy": round(accuracy, 2),
            "data_set_name": data_set_name,
            "validation_date": datetime.utcnow(),
            "logs": logs
        }