__all__ = ['instances']


from .point_md import POINT_MD
from .vedomosti_md import VEDOMOSTI_MD
from .novostipmr_com import NOVOSTIPMR_COM

instances = (
    POINT_MD,
    VEDOMOSTI_MD,
    NOVOSTIPMR_COM
)
