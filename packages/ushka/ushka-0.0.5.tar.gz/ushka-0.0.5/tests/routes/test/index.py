def GET():
    import datetime

    return datetime.datetime.now().strftime("%d/%m/%Y, %H:%M:%S")
