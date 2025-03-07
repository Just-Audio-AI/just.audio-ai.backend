class CodeExpiredExceptions(Exception):
    detail = "Code expired"


class CodeNotFoundExceptions(Exception):
    detail = "Code not found"
