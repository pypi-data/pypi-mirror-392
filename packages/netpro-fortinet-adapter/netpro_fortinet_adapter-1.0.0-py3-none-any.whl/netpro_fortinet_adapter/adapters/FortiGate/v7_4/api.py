from netpro.adapters.registry import register_adapter
from ..v7_2 import FORTIGATE as FORTIGATEv72


__all__ = (
    'FORTIGATE',
)

@register_adapter(vendor="fortinet", os="FortiOS", version="7.4")
class FORTIGATE(FORTIGATEv72):
    """
    FortiGate Adapter for FortiOS v7.4
    """
    