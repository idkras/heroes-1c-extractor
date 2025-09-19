from datetime import datetime

from app.modules.auth.auth_service import AuthService
from app.modules.usage.usage_controller import UsageController
from app.modules.usage.usage_schema import UsageResponse
from fastapi import APIRouter, Depends

router = APIRouter()


class UsageAPI:
    @staticmethod
    @router.get("/usage", response_model=UsageResponse)
    async def get_usage(
        start_date: datetime,
        end_date: datetime,
        user=Depends(AuthService.check_auth),
    ):
        user_id = user["user_id"]
        return await UsageController.get_user_usage(start_date, end_date, user_id)
