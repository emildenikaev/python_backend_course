import json
from typing import List

async def app(scope, receive, send) -> None:
    # Определяем, что это HTTP-запрос
    if scope['type'] == 'http':
        # Получаем путь и метод запроса
        path = scope['path']
        method = scope['method']

        # Обработчик для GET /factorial
        if method == 'GET' and path.startswith('/factorial'):
            # Извлекаем query-параметр n
            query_string = scope['query_string'].decode()
            params = dict(q.split('=') for q in query_string.split('&') if '=' in q)
            n_param = params.get('n')

            # Проверяем наличие параметра n
            if n_param is None:
                await send_response(send, 422, {"error": "Missing parameter 'n'"})
                return
            
            # Проверяем, является ли n целым числом
            try:
                n = int(n_param)
            except ValueError:
                await send_response(send, 422, {"error": "'n' must be an integer"})
                return

            # Обработка негативного числа
            if n < 0:
                await send_response(send, 400, {"error": "'n' must be non-negative"})
                return
            
            # Рассчет факториала
            result = factorial(n)
            await send_response(send, 200, {"result": result})
            return

        # Обработчик для GET /fibonacci/{n}
        elif method == 'GET' and path.startswith('/fibonacci/'):
            # Извлекаем n из пути
            n_param = path[len('/fibonacci/'):]
            if not n_param.isdigit() or not n_param:
                await send_response(send, 422, {"error": "'n' must be a non-negative integer"})
                return

            n = int(n_param)

            # Обработка негативного числа
            if n < 0:
                await send_response(send, 400, {"error": "'n' must be non-negative"})
                return
            
            # Рассчет n-ого числа Фибоначчи
            result = fibonacci(n)
            await send_response(send, 200, {"result": result})
            return

        # Обработчик для GET /mean
        elif method == 'GET' and path == '/mean':
            # Получаем тело запроса
            body = await receive()
            body_json = json.loads(body.get('body', ''))

            # Проверка на пустой массив
            if not body_json or not isinstance(body_json, list):
                await send_response(send, 400, {"error": "Array cannot be empty"})
                return

            # Проверка на массив float
            if not all(isinstance(x, (int, float)) for x in body_json):
                await send_response(send, 422, {"error": "Array must contain only numbers"})
                return

            # Рассчет среднего
            result = mean(body_json)
            await send_response(send, 200, {"result": result})
            return

        # Если путь или метод не обработан, возвращаем 404
        await send_response(send, 404, {"error": "Not Found"})
        return

async def send_response(send, status_code: int, content: dict) -> None:
    headers = [(b"content-type", b"application/json")]
    await send({
        'type': 'http.response.start',
        'status': status_code,
        'headers': headers
    })
    await send({
        'type': 'http.response.body',
        'body': json.dumps(content).encode()
    })

def factorial(n: int) -> int:
    if n == 0:
        return 1
    return n * factorial(n - 1)

def fibonacci(n: int) -> int:
    if n == 0:
        return 0
    elif n == 1:
        return 1
    else:
        return fibonacci(n - 1) + fibonacci(n - 2)

def mean(numbers: List[float]) -> float:
    return sum(numbers) / len(numbers)
