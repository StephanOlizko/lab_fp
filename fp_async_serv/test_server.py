import asyncio
import threading
import tkinter as tk
from tkinter import scrolledtext

clients = {}
chat_rooms = {'main': set()}

async def client_loop(reader, writer, client_address, connections_widget, messages_widget, current_room):
    global chat_rooms

    while True:
        data = await reader.read(100)
        if not data:
            break
        message = data.decode()

        display_message = f"Получено сообщение от {client_address} {clients[writer]}: {message}\n"
        messages_widget.insert(tk.END, display_message)
        messages_widget.see(tk.END)

        if message.startswith('/m'):
            client_name = message.split()[1]

            for i in clients.keys():
                if clients[i] == client_name:
                    client = i
            
            message_send = f"Личное сообщение от {clients[writer]} - " + " ".join(i for i in message.split()[2:])

            client.write(message_send.encode())
            await client.drain()
            print(f"Сообщение отправлено {clients[client]}")

        elif message.startswith('/users'):
            message = "Список пользователей: " + ", ".join(clients[i] for i in clients)
            writer.write(message.encode())
            await writer.drain()
            print(f"Команда отправлена {clients[writer]}")

        elif message.startswith('/join'):
            room_name = message.split()[1]
            await join_room(writer, room_name)

        elif message.startswith('/create'):
            room_name = message.split()[1]
            await create_room(writer, room_name)

        elif message.startswith('/leave'):
            await leave_room(writer)

        elif message.startswith('/adduser'):
            user_to_add = message.split()[1]
            await add_user_to_chat(writer, user_to_add, await show_current_chat(writer))

        elif message.startswith('/currentchat'):
            current_room = await show_current_chat(writer)

        else:
            await broadcast_message(writer, f" {clients[writer]} - " + message, await show_current_chat(writer))

async def handle_client(reader, writer, connections_widget, messages_widget):
    global chat_rooms

    client_address = writer.get_extra_info('peername')
    print(f"Новое подключение: {client_address}")

    message = "Добро пожаловать, введите имя"
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(100)
    message = data.decode()

    clients[writer] = message
    connections_widget.insert(tk.END, f"{client_address} - {message}\n")

    message = f"Ваше имя - {message}"
    writer.write(message.encode())
    await writer.drain()

    current_room = 'main'
    await join_room(writer, current_room)

    try:
        await client_loop(reader, writer, client_address, connections_widget, messages_widget, current_room)
    #except Exception as e:
    #    print(f"An error occurred: {e}")
    finally:
        await leave_room(writer)
        if writer in clients.keys():
            clients.pop(writer)
            connections_widget.delete(1.0, tk.END)
            connections_widget.insert(tk.END, "\n".join([str(client.get_extra_info('peername')) + f" - {clients[client]}" for client in clients]))
        writer.close()
        await writer.wait_closed()
        print(f"Соединение с {client_address} разорвано")

async def join_room(writer, room_name):
    global chat_rooms
    await leave_room(writer)

    if room_name not in chat_rooms:
        writer.write(f"Не существует комнаты: {room_name}".encode())
        await writer.drain()

    if writer not in chat_rooms[room_name]:
        chat_rooms[room_name].add(writer)
    writer.write(f"Вы присоединились к чату: {room_name}".encode())
    await writer.drain()

async def create_room(writer, room_name):
    global chat_rooms
    if room_name not in chat_rooms:
        chat_rooms[room_name] = set()

    await join_room(writer, room_name)

async def leave_room(writer):
    global chat_rooms
    print(chat_rooms)
    for room_name in chat_rooms.keys():
        if writer in chat_rooms[room_name]:
            chat_rooms[room_name].remove(writer)
            writer.write(f"Вы покинули чат: {room_name}".encode())
            await writer.drain()
            break
    
    #writer.write(f"Вы присоединились к чату: {room_name}".encode())
    #await writer.drain()


async def add_user_to_chat(writer, user_to_add, room_name):
    global chat_rooms
    if room_name in chat_rooms and user_to_add in clients.values():
        target_writer = next(k for k, v in clients.items() if v == user_to_add)
        await join_room(target_writer, room_name)
        writer.write(f"Пользователь {user_to_add} добавлен в чат".encode())
        await writer.drain()

async def show_current_chat(writer):
    global chat_rooms
    #print(chat_rooms)

    current_room = "None"

    print(chat_rooms)
    for i in chat_rooms.keys():
        if writer in chat_rooms[i]:
            current_room = i

    writer.write(f"Вы находитесь в чате: {current_room}".encode())
    await writer.drain()

    return current_room

async def broadcast_message(writer, message, current_room):
    global chat_rooms

    print(current_room)
    if current_room:
        for user_writer in chat_rooms[current_room]:
            #if user_writer != writer:
            user_writer.write(message.encode())
            await user_writer.drain()
            print("Сообщение отправлено")

async def main(connections_widget, messages_widget):
    server = await asyncio.start_server(lambda r, w: handle_client(r, w, connections_widget, messages_widget), '127.0.0.1', 8888)
    async with server:
        print("Сервер запущен и слушает на 127.0.0.1:8888")
        await server.serve_forever()

def start_async_loop(connections_widget, messages_widget):
    asyncio.run(main(connections_widget, messages_widget))

if __name__ == '__main__':
    root = tk.Tk()
    root.geometry("600x400")
    root.title("Server")

    connections_output = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=25, height=13)
    connections_output.pack(side=tk.LEFT, padx=10, pady=10)

    messages_output = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=50, height=13)
    messages_output.pack(side=tk.LEFT, padx=10, pady=10)

    asyncio_thread = threading.Thread(target=start_async_loop, args=(connections_output, messages_output))
    asyncio_thread.start()

    root.mainloop()
