from typing import List, Optional, TypedDict


class DrDBState(TypedDict, total=False):
    question: str
    tables: List[str]
    sql_text: Optional[str]
    intent: str
    answer: str
    debug: List[str]
