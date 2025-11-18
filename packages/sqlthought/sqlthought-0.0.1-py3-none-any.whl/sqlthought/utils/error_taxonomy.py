ERROR_TAXONOMY = {
    "MISSING_TABLE": ["no such table", "unknown table", "does not exist"],
    "MISSING_COLUMN": ["no such column", "unknown column", "has no column"],
    "SYNTAX_ERROR": ["syntax error", "parse error", "near"],
    "TYPE_ERROR": ["datatype mismatch", "wrong type"],
    "CONSTRAINT_ERROR": ["constraint failed", "foreign key", "unique constraint"],
    "RUNTIME_ERROR": ["division by zero", "out of memory"],
    "UNKNOWN": []
}


def classify_error(error_message: str) -> str:
    error_message = error_message.lower()
    for err_type, patterns in ERROR_TAXONOMY.items():
        for p in patterns:
            if p in error_message:
                return err_type
    return "UNKNOWN"
