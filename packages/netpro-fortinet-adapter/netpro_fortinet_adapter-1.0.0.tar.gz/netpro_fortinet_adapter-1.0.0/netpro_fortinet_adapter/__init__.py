from netpro.adapters.registry import AdapterPackageBase


class FortinetAdapterPackage(AdapterPackageBase):
    min_netpro = "0.1"
    # package_name defaults to "netpro_fortinet_adapter" via get_package_name()


def register():
    """
    Entry point used by:
      [project.entry-points."netpro.adapters"]
      netpro_fortinet_adapter = "netpro_fortinet_adapter:register"
    """
    FortinetAdapterPackage.entrypoint()
