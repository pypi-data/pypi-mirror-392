from netpro.adapters.registry import register_adapter
from ..v7_0 import FORTIGATE as FORTIGATEv7

__all__ = (
    'FORTIGATE',
)

@register_adapter(vendor="fortinet", os="FortiOS", version="7.2")
class FORTIGATE(FORTIGATEv7):
    """
    FortiGate Adapter for FortiOS v7.2
    """
