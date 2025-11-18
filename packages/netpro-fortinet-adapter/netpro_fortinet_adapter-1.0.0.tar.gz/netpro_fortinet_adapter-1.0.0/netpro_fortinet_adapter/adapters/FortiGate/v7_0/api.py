from netpro.adapters.registry import register_adapter
from ..base import BaseFortigateAPIAdapter

__all__ = (
    'FORTIGATE',
)

@register_adapter(vendor="fortinet", os="FortiOS", version="7.0")
class FORTIGATE(BaseFortigateAPIAdapter):
    """
    FortiGate Adapter for FortiOS v7.0
    """
