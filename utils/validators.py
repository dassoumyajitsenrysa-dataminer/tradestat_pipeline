def is_valid_hs_code(code: str):
    return code.isdigit() and len(code) == 8
