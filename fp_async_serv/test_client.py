import asyncio

async def receive_messages(reader):
    while True:
        data = await reader.read(100)
        message = data.decode()
        print(f"Получено сообщение: {message}")

async def send_messages(writer, name):
    while True:
        message = await get_input("")
        writer.write(message.encode())
        await writer.drain()

async def get_input(prompt):
    loop = asyncio.get_event_loop()
    user_input = await loop.run_in_executor(None, input, prompt)
    return user_input

async def main():
    reader, writer = await asyncio.open_connection('127.0.0.1', 8888)
    print("Подключено к серверу")

    receive_task = asyncio.create_task(receive_messages(reader))

    name = "*"
    message = await get_input("")
    name = message
    writer.write(message.encode())
    await writer.drain()

    send_task = asyncio.create_task(send_messages(writer, name))

    await receive_task
    await send_task

if __name__ == '__main__':
    asyncio.run(main())
