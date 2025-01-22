def filter_digits(message: str):
    return "".join(list(filter(lambda i: i.isdigit(), message)))
