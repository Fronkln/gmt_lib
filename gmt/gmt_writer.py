from .structure.br.br_gmt import *
from .structure.gmt import *
from .util import *

def write_gmt(gmt: GMT) -> bytearray:
    """Writes a GMT object to a buffer and returns the buffer as a bytearray
    :param gmt: The GMT object
    :return: Bytearray containing the written GMT file
    """

    with BinaryReader() as br:
        br.write_struct(BrGMT(), gmt)
        return br.buffer()

def write_gmt_to_file(gmt: GMT, path: str) -> None:
    """Writes a GMT object to a file
    :param gmt: The GMT object
    :param path: Path to target file as a string
    """

    with open(path, 'wb') as f:
        f.write(write_gmt(gmt))
