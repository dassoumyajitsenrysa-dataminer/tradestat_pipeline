from enum import Enum

class TradeMode(str, Enum):
    EXPORT = "export"
    IMPORT = "import"
    TOTAL = "total"
