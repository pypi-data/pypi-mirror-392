""""
Doc String

"""
from .utl import RelDrpa
from .cfg import PgsCore, SrvCore
from .dbs import ModMeta, DbsAmig, DbsMsvc
from .app import AppMeta, AppSpan, AppMsvc
from .sap import SubMeta, SubSpan, SubMsvc
from .apr import AprSrvc, AprResp, AprMsvc

__all__ = ["MSVC"]

class MSVC:
    RelDrpa = RelDrpa
    PgsCore = PgsCore
    SrvCore = SrvCore
    ModMeta = ModMeta
    DbsAmig = DbsAmig
    DbsMsvc = DbsMsvc
    AprSrvc = AprSrvc
    AprResp = AprResp
    AprMsvc = AprMsvc
    SubMeta = SubMeta
    SubMsvc = SubMsvc
    SubSpan = SubSpan
    AppMeta = AppMeta
    AppSpan = AppSpan
    AppMsvc = AppMsvc