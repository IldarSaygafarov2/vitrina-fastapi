import random


def generate_code():
    return "".join(random.sample([f"{i}" for i in range(10)], 6))
