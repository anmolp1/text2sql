

# src/utils/validation.py

import re
from typing import Tuple, Optional

def validate_sql(sql: str) -> Tuple[bool, Optional[str]]:
    """
    Validates that the SQL string is a safe SELECT query:
      - Must start with SELECT
      - Must include a LIMIT clause
      - Must not contain any forbidden keywords (INSERT, UPDATE, DELETE, DROP, ALTER, CREATE, GRANT, REVOKE, TRUNCATE)
    Returns:
      (True, None) if validation passes,
      (False, error_message) otherwise.
    """
    # Normalize whitespace/case for keyword checks
    sql_clean = sql.strip()
    sql_upper = sql_clean.upper()

    # 1) Must start with SELECT
    if not sql_upper.startswith("SELECT"):
        return False, "Query must start with SELECT"

    # 2) No forbidden statements
    forbidden = [
        "INSERT", "UPDATE", "DELETE",
        "DROP", "ALTER", "CREATE",
        "GRANT", "REVOKE", "TRUNCATE"
    ]
    for kw in forbidden:
        # use word boundaries to avoid partial matches
        if re.search(rf"\b{kw}\b", sql_upper):
            return False, f"Forbidden keyword detected: {kw}"

    # 3) Must include a LIMIT clause
    if not re.search(r"\bLIMIT\s+\d+\b", sql_upper):
        return False, "Missing or invalid LIMIT clause"

    return True, None