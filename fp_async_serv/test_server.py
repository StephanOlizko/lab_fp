import asyncio


# Список подключенных клиентов
clients = {}

async def client_loop(reader, writer, client_address):
    while True:
            data = await reader.read(100)
            if not data:
                break
            message = data.decode()
            print(f"Получено сообщение от {client_address} {clients[writer]}: {message}")
            for client in clients:
                if client != writer:
                    message = f" {clients[writer]} - " + message
                    client.write(message.encode())
                    await client.drain()
                    print("Соощение отправлено")


async def handle_client(reader, writer):
    client_address = writer.get_extra_info('peername')
    print(f"Новое подключение: {client_address}")
    # Добавление клиента в словарь

    message = "Добро пожаловать, введите имя"
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(100)
    message = data.decode()

    clients[writer] = message

    try:
        await client_loop(reader, writer, client_address)   

    except Exception as e:
        print(f"An error occured: {e}")

    finally:
        # Удаление клиента из списка и закрытие соединения
        if writer in clients.keys():
            clients.pop(writer)
        writer.close()
        await writer.wait_closed()
        print(f"Соединение с {client_address} разорвано")

async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    async with server:
        print("Сервер запущен и слушает на 127.0.0.1:8888")
        await server.serve_forever()

def start_async_loop():
    asyncio.run(main())

if __name__ == '__main__':
    start_async_loop()