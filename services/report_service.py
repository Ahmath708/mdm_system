from typing import List, Dict, Optional, Any
from datetime import datetime
from config.database import DatabaseConfig
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import os

class ReportService:

    @staticmethod
    def generate_audit_report(start_date: Optional[str] = None, end_date: Optional[str] = None) -> List[Dict]:
        query = "SELECT * FROM audit_logs WHERE 1=1"
        params = []

        if start_date:
            query += " AND created_at >= ?"
            params.append(start_date)
        if end_date:
            query += " AND created_at <= ?"
            params.append(end_date)
        query += " ORDER BY created_at DESC"

        with DatabaseConfig.get_db_cursor() as cursor:
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def generate_data_quality_report(data_set_name: str) -> Dict[str, Any]:
        return ReportService._get_quality_report(data_set_name)

    @staticmethod
    def generate_summary_report() -> Dict[str, Any]:
        with DatabaseConfig.get_db_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as total FROM master_data")
            total_data = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) as total FROM users")
            total_users = cursor.fetchone()["total"]

            cursor.execute("SELECT COUNT(*) as total FROM audit_logs")
            total_audits = cursor.fetchone()["total"]

            cursor.execute("""
                SELECT data_set_name, COUNT(*) as count 
                FROM master_data 
                GROUP BY data_set_name
            """)
            data_sets = cursor.fetchall()

        return {
            "total_master_records": total_data,
            "total_users": total_users,
            "total_audit_logs": total_audits,
            "data_sets": [dict(row) for row in data_sets],
            "generated_at": datetime.utcnow()
        }

    @staticmethod
    def generate_user_activity_report() -> List[Dict]:
        with DatabaseConfig.get_db_cursor() as cursor:
            cursor.execute("""
                SELECT u.username, u.role, COUNT(a.id) as action_count
                FROM users u
                LEFT JOIN audit_logs a ON u.id = a.user_id
                GROUP BY u.id, u.username, u.role
                ORDER BY action_count DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    @staticmethod
    def export_to_csv(data: List[Dict], filename: str) -> str:
        df = pd.DataFrame(data)
        os.makedirs("output", exist_ok=True)
        filepath = f"output/{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filepath, index=False)
        return filepath

    @staticmethod
    def export_to_excel(data: List[Dict], filename: str) -> str:
        df = pd.DataFrame(data)
        os.makedirs("output", exist_ok=True)
        filepath = f"output/{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        df.to_excel(filepath, index=False)
        return filepath

    @staticmethod
    def generate_pdf_report(title: str, data: List[Dict], filename: str) -> str:
        os.makedirs("output", exist_ok=True)
        filepath = f"output/{filename}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"

        doc = SimpleDocTemplate(filepath, pagesize=letter)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph(title, styles['Title']))
        elements.append(Spacer(1, 12))

        if data:
            headers = list(data[0].keys())
            table_data = [headers]

            for row in data[:50]:
                table_data.append([str(row.get(h, "")) for h in headers])

            t = Table(table_data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(t)

        doc.build(elements)
        return filepath

    @staticmethod
    def _get_quality_report(data_set_name: str) -> Dict[str, Any]:
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

            total = result["total_records"] or 0
            valid = result["valid_records"] or 0
            invalid = result["invalid_records"] or 0
            accuracy = (valid / total * 100) if total > 0 else 0

            return {
                "total_records": total,
                "valid_records": valid,
                "invalid_records": invalid,
                "accuracy": round(accuracy, 2),
                "data_set_name": data_set_name,
                "generated_at": datetime.utcnow()
            }

    @staticmethod
    def get_data_set_statistics(data_set_name: str) -> Dict[str, Any]:
        with DatabaseConfig.get_db_cursor() as cursor:
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM master_data 
                WHERE data_set_name = ?
                GROUP BY status
            """, (data_set_name,))
            status_counts = cursor.fetchall()

            cursor.execute("""
                SELECT DATE(created_at) as date, COUNT(*) as count
                FROM master_data
                WHERE data_set_name = ?
                GROUP BY DATE(created_at)
                ORDER BY date DESC
            """, (data_set_name,))
            timeline = cursor.fetchall()

        return {
            "data_set_name": data_set_name,
            "status_counts": [dict(row) for row in status_counts],
            "timeline": [dict(row) for row in timeline]
        }