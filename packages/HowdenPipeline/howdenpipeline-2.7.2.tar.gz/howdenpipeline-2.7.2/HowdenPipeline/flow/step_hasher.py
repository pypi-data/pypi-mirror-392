from HowdenPipeline.flow.parameter_serializer import ParameterSerializer
from typing import Any, Optional
import json
import hashlib

class StepHasher:
    def __init__(self, serializer: Optional[ParameterSerializer] = None) -> None:
        self._serializer = serializer or ParameterSerializer()

    def compute_hash(self, step: Any) -> str:
        attrs = {
            k: v
            for k, v in step.__dict__.items()
            if k != "hash"
               and not k.startswith("_")
               and k not in ("client", "provider")
        }
        serializable_attrs = self._serializer.make_serializable(attrs)
        attrs_str = json.dumps(serializable_attrs, sort_keys=True, ensure_ascii=True)
        return hashlib.sha256(attrs_str.encode()).hexdigest()[:8]