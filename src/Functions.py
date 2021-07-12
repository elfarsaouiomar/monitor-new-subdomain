from datetime import datetime


def getCurrentTime():
    """ Retun current time eg : 2021-07-12-01-30-11 """
    return datetime.now().strftime("%Y-%m-%d-%I-%M-%S")
