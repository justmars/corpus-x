__version__ = "0.0.2"

from .__main__ import (
    build_x_tables,
    get_codification,
    get_decision,
    get_document,
    get_statute,
    reset_x,
    setup_x,
)
from .codifications import Codification
from .documents import Document
from .inclusions import (
    CitationInOpinion,
    Inclusion,
    StatuteInOpinion,
    set_inclusions,
)
from .statutes import Statute
