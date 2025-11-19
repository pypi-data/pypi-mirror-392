
from typing import Optional
from pydantic import BaseModel

from AgentService.enums.response import ResposneStatus


class GetVersionResponse(BaseModel):
    data: str
    description: Optional[str] = None
    status: ResposneStatus
