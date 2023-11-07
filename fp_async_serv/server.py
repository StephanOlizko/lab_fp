import asyncio

# Список подключенных клиентов
clients = []

async def handle_client(reader, writer):

    # Добавление клиента в список
    clients.append(writer)
    client_address = writer.get_extra_info('peername')
    print(f"Новое подключение: {client_address}")

    try:
        while True:
            data = await reader.read(100)
            if not data:
                break
            message = data.decode()
            print(f"Получено сообщение от {client_address}: {message}")
            for client in clients:
                #if client != writer:
                client.write(message.encode())
                await client.drain()
                print("Соощение отправлено")

    except asyncio.CancelledError:
        pass
    except ConnectionResetError:
        pass
    finally:
        # Удаление клиента из списка и закрытие соединения
        clients.remove(writer)
        writer.close()
        await writer.wait_closed()
        print(f"Соединение с {client_address} разорвано")

async def main():
    server = await asyncio.start_server(handle_client, '127.0.0.1', 8888)
    async with server:
        print("Сервер запущен и слушает на 127.0.0.1:8888")
        await server.serve_forever()

if __name__ == '__main__':
    asyncio.run(main())
