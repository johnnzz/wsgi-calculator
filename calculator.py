#!/usr/bin/env python3
"""
Online calculator that can perform several operations.

  * Addition
  * Subtractions
  * Multiplication
  * Division

Users are able to send appropriate requests and get back
proper responses. For example, if a user opens a browser to the
application at `http://localhost:8080/multiply/3/5' then the response
body in the browser will be `15`.

  * Script is runnable using `$ python calculator.py`
  * Home page visible at webroot (http://localhost:8080/)
    that explains how to perform calculations.
"""
import re
import socket
import os


def out_format(arg):
    """
    Returns a STRING containing the value minus the
    superflous zero so we can properly handle things
    as floats, but meet the assignment sample values
    that look like ints
    """
    return str(re.sub(r'.0$', '', str(arg)))


def add(*args):
    """
    Returns a STRING with the sum of the arguments
    """

    v1, v2 = args
    result = v1 + v2

    return out_format(result)


def subtract(*args):
    """
    Returns a STRING with the difference of the arguments
    """

    v1, v2 = args
    result = v1 - v2
    
    return out_format(result)


def multiply(*args):
    """
    Returns a STRING with the product of the arguments
    """

    v1, v2 = args
    result = v1 * v2
    
    return out_format(result)


def divide(*args):
    """
    Returns a STRING with the quotient of the arguments

    This doesn't need protection against ZeroDivisionError
    because the whole routine call is in a try/except and
    we catch that
    """

    v1, v2 = args
    result = v1 / v2
    
    return out_format(result)


def resolve_path(path):
    """
    Returns two values: a callable and an iterable of
    arguments.

    Consider the following URL/Response body pairs as tests:

    ```
      http://localhost:8080/multiply/3/5   => 15
      http://localhost:8080/add/23/42      => 65
      http://localhost:8080/subtract/23/42 => -19
      http://localhost:8080/divide/22/11   => 2
      http://localhost:8080/divide/6/0     => HTTP "400 Bad Request"
      http://localhost:8080/               => <html>Here's how to use this page...</html>
    ```
    """

    # break url down into three groups, the action and the two values
    # if we don't have an exact match, we'll fail the action/value
    # assignment and print the usage page

    # try to match numbers, decimal points and negative numbers
    pattern = '(add|subtract|divide|multiply)/([-+]?\d*\.\d+|[-+]?\d*)/([-+]?\d*\.\d+|[-+]?\d*)$'

    # we don't protect this action because the whole routine is
    # in a try/except block and we will catch it
    matches = re.search(pattern, path.lstrip("/")).groups()

    # note the parsed value in the server log
    print("decoded {} into: {}".format(path, matches))

    # for convenience and clarity
    action, v1, v2 = matches

    # use floats up front so we can handle either
    args = [ float(v1), float(v2) ]

    # map the action to the proper function
    func = { "add": add,
             "subtract": subtract,
             "divide": divide,
             "multiply": multiply
            }.get(action)

    return func, args


def application(environ, start_response):
    """
    main calculator logic
    """

    headers = [("Content-type", "text/html")]

    try:
        # get the url from the environment
        path = environ.get('PATH_INFO', None)
        # attempt to resolve the path, path
        # problems will trigger an exception
        # and print uage
        func, args = resolve_path(path)
        body = str(func(*args))
        status = "200 OK"

    except ZeroDivisionError:
        # return bad request on ZeroDivisionErrors
        status = "400 Bad Request"
        body = "<h1>400 Bad Request</h1>"
        body += "<h2>ZeroDivision Error!</h2>"

    except (NameError, AttributeError, ValueError):
        # any non valid url, parameter or lack of
        # parameter gets a usage statement
        status = "200 OK"
        body = "<h1>Web Calc 2000</h1>"
        body += "</p>To calculate a value, enter a URL in the format:"
        body += "</p>{}action/value1/value2".format(my_url)  
        body += "</p>Where action can be one of the following:"
        body += "<ul>"
        body += "<li>add</li>"
        body += "<li>subtract</li>"
        body += "<li>multiply</li>"
        body += "<li>divide</li>"
        body += "</ul>"
        body += "</p>Example:"
        body += "</p>{}add/3/2".format(my_url)
        body += "</p>Will result in the browser returning '5'"

    finally:
        headers.append(('Content-length', str(len(body))))
        start_response(status, headers)
        return [body.encode('utf8')]


if __name__ == '__main__':

    # allow the port to be passed from the environment
    port = int(os.environ.get("PORT", 8080))

    # hack to figure out my outgoing ip address
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    my_ip = s.getsockname()[0]
    s.close()

    my_url = "http://{}:{}/".format(my_ip, port)
    print("Starting server on {}".format(my_url))

    from wsgiref.simple_server import make_server
    # bind to 0.0.0.0 to allow connections from other machines
    srv = make_server('0.0.0.0', port, application)
    srv.serve_forever()
