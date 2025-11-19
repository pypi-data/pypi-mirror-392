from dataclasses import dataclass
from typing import Optional
from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class CtyunOpenAPIResponse:
    """
    Represents a request to the Ctyun API.
    """
    def __init__(self,traceId: Optional[str] = None):
        self.trace_id = traceId