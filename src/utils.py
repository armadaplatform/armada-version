from time import time
import os

start_time = time()


def status():
    seconds = time() - start_time
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    d, h = divmod(h, 24)
    results = {
        "name": os.getenv("MICROSERVICE_NAME"),
        "env": os.getenv("MICROSERVICE_ENV"),
        "uptime": "%d days %d hours %d minutes %d seconds" % (d, h, m, s)
    }

    app_id = os.environ.get('MICROSERVICE_APP_ID')
    if app_id:
        results['app_id'] = app_id
    return results
