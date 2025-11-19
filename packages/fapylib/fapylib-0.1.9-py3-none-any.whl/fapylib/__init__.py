""""
Doc String

"""
from .utl import RelDrpa
from .cfg import PgsCore, SrvCore
from .mig import EnvAlem, DbsAmig
from .dbs import ModMeta, DbsMsvc
from .app import AppMeta, AppSpan, AppMsvc
from .sap import SubMeta, SubSpan, SubMsvc
from .apr import AprSrvc, AprResp, AprMsvc

__all__ = ["MSVC"]

class MSVC:
    RelDrpa = RelDrpa
    PgsCore = PgsCore
    SrvCore = SrvCore
    EnvAlem = EnvAlem
    DbsAmig = DbsAmig
    ModMeta = ModMeta
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