from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from services.report_service import ReportService
from routes.auth import get_current_user, require_permission

router = APIRouter(prefix="/reports", tags=["Reports"])

@router.get("/audit")
async def get_audit_report(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    user = Depends(require_permission("view_audit"))
):
    return ReportService.generate_audit_report(start_date, end_date)

@router.get("/quality/{data_set_name}")
async def get_quality_report(data_set_name: str, user = Depends(require_permission("read"))):
    return ReportService.generate_data_quality_report(data_set_name)

@router.get("/summary")
async def get_summary_report(user = Depends(require_permission("read"))):
    return ReportService.generate_summary_report()

@router.get("/user-activity")
async def get_user_activity(user = Depends(require_permission("view_audit"))):
    return ReportService.generate_user_activity_report()

@router.get("/export/csv")
async def export_csv(
    report_type: str = Query(..., description="Type: audit, quality, summary"),
    data_set_name: Optional[str] = None,
    user = Depends(require_permission("read"))
):
    if report_type == "audit":
        data = ReportService.generate_audit_report()
    elif report_type == "quality" and data_set_name:
        data = ReportService.generate_data_quality_report(data_set_name).get("logs", [])
    elif report_type == "summary":
        data = [ReportService.generate_summary_report()]
    else:
        raise HTTPException(status_code=400, detail="Invalid report type")
    
    filepath = ReportService.export_to_csv(data, report_type)
    return {"file": filepath}

@router.get("/export/pdf")
async def export_pdf(
    title: str,
    report_type: str = Query(..., description="Type: audit, quality, summary"),
    data_set_name: Optional[str] = None,
    user = Depends(require_permission("read"))
):
    if report_type == "audit":
        data = ReportService.generate_audit_report()
    elif report_type == "quality" and data_set_name:
        report = ReportService.generate_data_quality_report(data_set_name)
        data = [report]
    elif report_type == "summary":
        data = [ReportService.generate_summary_report()]
    else:
        raise HTTPException(status_code=400, detail="Invalid report type")
    
    filepath = ReportService.generate_pdf_report(title, data, report_type)
    return {"file": filepath}

@router.get("/statistics/{data_set_name}")
async def get_statistics(data_set_name: str, user = Depends(require_permission("read"))):
    return ReportService.get_data_set_statistics(data_set_name)