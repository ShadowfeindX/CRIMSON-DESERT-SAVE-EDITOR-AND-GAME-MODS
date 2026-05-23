try:
    from dmm_parser import *
    import dmm_parser as _dmm
    if not hasattr(_dmm, 'extract_file'):
        raise ImportError("dmm_parser missing native functions")
except ImportError:
    from crimson_rs.crimson_rs import *
from crimson_rs.enums import Compression, Crypto, Language
