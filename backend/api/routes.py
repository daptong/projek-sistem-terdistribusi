from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel

router = APIRouter()


class ControlRequest(BaseModel):
    device_id: str
    device_type: str
    action: str
    params: dict = None
    request_id: str = None


@router.get("/devices")
async def list_devices(request: Request):
    mgr = getattr(request.app.state, "device_manager", None)
    if not mgr:
        return []
    return mgr.list_devices()


@router.post("/device/control")
async def control_device(request: Request, req: ControlRequest):
    mgr = getattr(request.app.state, "device_manager", None)
    if not mgr:
        raise HTTPException(status_code=503, detail="Device manager not available")
    try:
        res = mgr.send_command(req.device_id, req.action, req.params)
        return {"status": "accepted", "request_id": req.request_id, "result": res}
    except KeyError:
        raise HTTPException(status_code=404, detail="Device not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
