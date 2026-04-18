from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from services.data_service import MasterDataService
from models.schemas import MasterDataCreate, MasterDataUpdate, MasterDataResponse, AuditLogResponse
from routes.auth import require_permission

router = APIRouter(prefix="/master-data", tags=["Master Data"])

@router.post("/", response_model=MasterDataResponse)
async def create_data(
    data: MasterDataCreate,
    user = Depends(require_permission("create"))
):
    record_id = MasterDataService.create_master_data(
        data.data_set_name,
        data.data_type,
        data.data_value,
        user["id"]
    )
    record = MasterDataService.get_master_data(record_id)
    return record

@router.get("/", response_model=List[MasterDataResponse])
async def get_all_data(
    data_set_name: Optional[str] = None,
    status: Optional[str] = None,
    user = Depends(require_permission("read"))
):
    return MasterDataService.get_all_master_data(data_set_name, status)

@router.get("/{record_id}", response_model=MasterDataResponse)
async def get_data(record_id: int, user = Depends(require_permission("read"))):
    record = MasterDataService.get_master_data(record_id)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@router.put("/{record_id}", response_model=MasterDataResponse)
async def update_data(
    record_id: int,
    data: MasterDataUpdate,
    user = Depends(require_permission("update"))
):
    success = MasterDataService.update_master_data(record_id, data.dict(exclude_unset=True), user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Record not found")
    record = MasterDataService.get_master_data(record_id)
    return record

@router.delete("/{record_id}")
async def delete_data(record_id: int, user = Depends(require_permission("delete"))):
    success = MasterDataService.delete_master_data(record_id, user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"message": "Record deleted successfully"}

@router.post("/commission/{data_set_name}")
async def commission_data_set(data_set_name: str, user = Depends(require_permission("update"))):
    success = MasterDataService.commission_data_set(data_set_name, user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Data set not found")
    return {"message": f"Data set '{data_set_name}' commissioned"}

@router.post("/decommission/{data_set_name}")
async def decommission_data_set(data_set_name: str, user = Depends(require_permission("delete"))):
    success = MasterDataService.decommission_data_set(data_set_name, user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Data set not found")
    return {"message": f"Data set '{data_set_name}' decommissioned"}

@router.get("/audit/logs", response_model=List[AuditLogResponse])
async def get_audit_logs(
    table_name: Optional[str] = None,
    record_id: Optional[int] = None,
    user = Depends(require_permission("view_audit"))
):
    return MasterDataService.get_audit_logs(table_name, record_id)