import json


async def send_answer(send, status: int, response_body: str, content_type: str = "text/plain") -> None:
    response_body = response_body.encode('utf-8')
    content_type = content_type.encode('utf-8')

    await send({
        'type': 'http.response.start',
        'status': status,
        'headers': [
            (b'content-type', content_type),
        ],
    })
    await send({
        'type': 'http.response.body',
        'body': response_body,
        'more_body': False,
    })


async def mean(scope, receive, send):
    request_body_event = await receive()
    request_body = request_body_event.get("body")

    if request_body is None:
        await send_answer(send, 422, "422 Unprocessable Entity")
        return

    try:
        data = json.loads(request_body.decode('utf-8'))

        if not isinstance(data, list) or not all(isinstance(num, (int, float)) for num in data):
            raise ValueError()

        if not data:
            await send_answer(send, 400, "400 Bad Request")
            return

        mean_value = sum(data) / len(data)
        result = json.dumps({"result": mean_value})
        await send_answer(send, 200, result, content_type="application/json")

    except (ValueError, json.JSONDecodeError):
        await send_answer(send, 422, "422 Unprocessable Entity")


async def fibonacci(scope, receive, send):
    if scope["method"] != "GET":
        await send_answer(send, 404, "404 Not Found")
        return

    def fibo(n):
        if n == 0:
            return 0
        elif n == 1:
            return 1
        else:
            a, b = 0, 1
            for _ in range(2, n + 1):
                a, b = b, a + b
            return b

    path_parts = scope.get("path", "").split("/")
    if len(path_parts) < 3:
        await send_answer(send, 422, "422 Unprocessable Entity")
        return

    try:
        n = int(path_parts[2])
        if n < 0:
            await send_answer(send, 400, "400 Bad Request")
            return
    except ValueError:
        await send_answer(send, 422, "422 Unprocessable Entity")
        return

    result = fibo(n)
    result = json.dumps({"result": result})
    await send_answer(send, 200, result, content_type="application/json")


async def factorial(scope, receive, send):
    if scope["method"] != "GET":
        await send_answer(send, 404, "404 Not Found")
        return

    n = scope.get("query_string")

    if n is None:
        await send_answer(send, 422, "422 Unprocessable Entity")
        return

    n = n.decode("utf-8").lstrip("n=")

    try:
        n = int(n)
    except ValueError:
        await send_answer(send, 422, "422 Unprocessable Entity")
        return

    if n < 0:
        await send_answer(send, 400, "400 Bad Request")
        return

    result = 1
    for i in range(2, n + 1):
        result *= i

    result = json.dumps({"result": result})
    await send_answer(send, 200, result, content_type="application/json")


async def app(scope, receive, send) -> None:
    path = scope['path']

    if path == "/factorial":
        await factorial(scope, receive, send)
        return
    if path.startswith("/fibonacci"):
        await fibonacci(scope, receive, send)
        return
    if path == "/mean":
        await mean(scope, receive, send)
        return

    await send_answer(send, 404, "404 Not Found")

