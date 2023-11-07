import asyncio

async def receive_messages(reader):
    while True:
        print(0)
        data = await reader.read(100)
        message = data.decode()
        print(f"Получено сообщение: {message}")

async def send_messages(writer):
    while True:
        message = input("Введите сообщение: ")
        writer.write(message.encode())
        await writer.drain()

async def main():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    print("Подключено к серверу")

    receive_task = asyncio.create_task(receive_messages(reader))
    send_task = asyncio.create_task(send_messages(writer))

if __name__ == '__main__':
    asyncio.run(main())
