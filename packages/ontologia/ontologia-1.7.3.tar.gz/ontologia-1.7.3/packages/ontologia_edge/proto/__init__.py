"""Generated gRPC bindings for the real-time entity service.

This module ensures required Google Well-Known Types are imported before
loading the generated descriptors. Some versions of generated code rely on
these modules being present in the descriptor pool at import time.
"""

import sys

# Ensure well-known types are registered before loading generated descriptors
try:  # pragma: no cover - defensive import for runtime environments
    from google.protobuf import timestamp_pb2 as _ts  # noqa: F401
    from google.protobuf import struct_pb2 as _st  # noqa: F401
except Exception:  # pragma: no cover
    pass

from . import realtime_pb2, realtime_pb2_grpc

__all__ = list(getattr(realtime_pb2, "__all__", [])) + list(
    getattr(realtime_pb2_grpc, "__all__", [])
)

globals().update(
    {name: getattr(realtime_pb2, name) for name in getattr(realtime_pb2, "__all__", [])}
)
globals().update(
    {name: getattr(realtime_pb2_grpc, name) for name in getattr(realtime_pb2_grpc, "__all__", [])}
)

sys.modules.setdefault("realtime_pb2", realtime_pb2)
sys.modules.setdefault("realtime_pb2_grpc", realtime_pb2_grpc)
