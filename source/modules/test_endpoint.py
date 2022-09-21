# Test an API endpoint to check for a valid response (not 404)
import requests
from requests.models import HTTPError


def isEndPointUp(log,endpoint):
    log.info("[isEndPointUp] Start")
    try:
        get=requests.get(endpoint)
    except HTTPError as http_err:
        print(f'HTTP error eccoured: {http_err}')
    except Exception as err:
        pass
    else:
        if get.status_code!='404':
            return True

    try:
        get=requests.post(endpoint)
    except HTTPError as http_err:
        print(f'HTTP error eccoured: {http_err}')
    except Exception as err:
        pass
    else:
        if get.status_code!='404':
            return True
    
    try:
        get=requests.head(endpoint)
    except HTTPError as http_err:
        print(f'HTTP error eccoured: {http_err}')
    except Exception as err:
        pass
    else:
        if get.status_code!='404':
            return True
    
    try:
        get=requests.options(endpoint)
    except HTTPError as http_err:
        print(f'HTTP error eccoured: {http_err}')
    except Exception as err:
        pass
    else:
        if get.status_code!='404':
            return True
    
    try:
        get=requests.put(endpoint)
    except HTTPError as http_err:
        print(f'HTTP error eccoured: {http_err}')
    except Exception as err:
        pass
    else:
        if get.status_code!='404':
            return True
    
    try:
        get=requests.patch(endpoint)
    except HTTPError as http_err:
        print(f'HTTP error eccoured: {http_err}')
    except Exception as err:
        pass
    else:
        if get.status_code!='404':
            return True
    
    try:
        get=requests.delete(endpoint)
    except HTTPError as http_err:
        print(f'HTTP error eccoured: {http_err}')
    except Exception as err:
        pass
    else:
        if get.status_code!='404':
            return True
    log.info("[isEndPointUp] End")
    return False