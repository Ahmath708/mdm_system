from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict
from services.data_quality_service import DataQualityService
from routes.auth import get_current_user, require_permission
from pydantic import BaseModel

router = APIRouter(prefix="/data-quality", tags=["Data Quality"])

class ValidationRule(BaseModel):
    field: str
    type: str = "string"
    required: bool = True

class ImportRequest(BaseModel):
    data_list: List[dict]
    data_set_name: str
    validation_rules: Dict[str, Dict]

class ValidateRequest(BaseModel):
    data: dict
    validation_rules: Dict[str, Dict]

@router.post("/import")
async def import_data(request: ImportRequest, user = Depends(require_permission("create"))):
    result = DataQualityService.import_data(
        request.data_list,
        request.data_set_name,
        request.validation_rules
    )
    return result

@router.post("/validate")
async def validate_single_data(request: ValidateRequest, user = Depends(require_permission("read"))):
    result = DataQualityService.validate_data(request.data, request.validation_rules)
    return result

@router.get("/report/{data_set_name}")
async def get_quality_report(data_set_name: str, user = Depends(require_permission("read"))):
    report = DataQualityService.get_quality_report(data_set_name)
    if not report["total_records"]:
        raise HTTPException(status_code=404, detail="No records found for this data set")
    return report

@router.post("/validate/{data_set_name}")
async def validate_existing_data(data_set_name: str, validation_rules: Dict[str, Dict], user = Depends(require_permission("read"))):
    result = DataQualityService.validate_existing_data(data_set_name, validation_rules)
    return result