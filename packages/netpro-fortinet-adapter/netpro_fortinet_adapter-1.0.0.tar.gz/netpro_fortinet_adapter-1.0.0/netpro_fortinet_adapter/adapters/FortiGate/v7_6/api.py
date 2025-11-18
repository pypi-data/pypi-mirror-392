from netpro.adapters.registry import register_adapter
from ..v7_4 import FORTIGATE as FORTIGATEv74

__all__ = (
    'FORTIGATE',
)

@register_adapter(vendor="fortinet", os="FortiOS", version="7.6")
class FORTIGATE(FORTIGATEv74):
    """
    FortiGate Adapter for FortiOS v7.6
    """
