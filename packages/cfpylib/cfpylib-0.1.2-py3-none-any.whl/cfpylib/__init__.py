"""
Doc String

"""
from .srvcore import SrvCore
from .pgscore import PgsCore

__all__ = ["SrvCore", "PgsCore"]

class CFGS:
    SrvCore = SrvCore
    PgsCore = PgsCore

