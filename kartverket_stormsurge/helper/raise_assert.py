def ras(assertion,  message=""):
    if not assertion:
        raise Exception(message)
