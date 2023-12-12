from .model import Responses

ok = Responses()
internal_error = Responses(code=10000, msg="Internal service error.")
