import asyncio
import threading
import tkinter as tk
from tkinter import scrolledtext

clients = {}
rooms = {'main': set()}


def find_client(client_name):
    for i in clients.keys():
        if clients[i] == client_name:
            return i

async def client_loop(reader, writer, client_address, connections_widget, messages_widget):
    while True:
        data = await reader.read(100)
        if not data:
            break
        message = data.decode()
        display_message = f"Получено сообщение от {client_address} {clients[writer]}: {message}\n"
        messages_widget.insert(tk.END, display_message)
        messages_widget.see(tk.END)

        if message.startswith('/'):
            if message.startswith('/dm'):
                client_name = message.split()[1]

                client = find_client(client_name)
                
                message_send = f" {clients[writer]} - " + message.split()[2]

                client.write(message_send.encode())
                await client.drain()
                print(f"Сообщение отправлено {clients[client]}")

            elif message.startswith('/room'):
                room_name = message.split()[1]
                create_room(room_name, writer)
            
            elif message.startswith('/add'):
                _, room_name, person_name = message.split()
                add_person_to_room(room_name, person_name, writer)
            
            elif message.startswith('/enter'):
                room_name = message.split()[1]

            elif message.startswith('/leave'):
                room_name = message.split()[1]

        else:
            for room in rooms:
                if writer in rooms[room]:
                    for client in rooms[room]:
                        message_send = f" {clients[writer]} - " + message
                        client.write(message_send.encode())
                        await client.drain()
                        print("Сообщение отправлено")


async def create_room(room_name, writer):
    if room_name not in rooms:
        rooms[room_name] = set(writer)

async def add_person_to_room(room_name, person_name, writer):
    if room_name in rooms:
        if writer in rooms[room_name] or room_name == 'main':

            client = find_client(person_name)
            rooms[room_name].add(client)

            writer.write(f"Клиент {person_name} добавлен в комнату {room_name}\n".encode())
            await writer.drain()
        else:
            writer.write(f"Вас нет в этой комнате!\n".encode())
            await writer.drain()
    else:
        writer.write(f"Комната {room_name} не существует\n".encode())
        await writer.drain()

async def leave_room(room_name, writer):
    if room_name in rooms:
        rooms[room_name].pop(writer)
        writer.write(f"Вы вышли из комнаты {room_name}\n".encode())
        await writer.drain()
    else:
        writer.write(f"Комната {room_name} не существует\n".encode())
        await writer.drain()

async def handle_client(reader, writer, connections_widget, messages_widget):
    client_address = writer.get_extra_info('peername')
    print(f"Новое подключение: {client_address}")
    
    message = "Добро пожаловать, введите имя"
    writer.write(message.encode())
    await writer.drain()

    data = await reader.read(100)
    message = data.decode()

    clients[writer] = message
    rooms["main"].add(writer)
    
    connections_widget.insert(tk.END, f"{client_address} - {message}\n")
    
    message = f"Ваше имя - {message}"
    writer.write(message.encode())
    await writer.drain()

    try:
        await client_loop(reader, writer, client_address, connections_widget, messages_widget)
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        if writer in clients.keys():
            clients.pop(writer)
            connections_widget.delete(1.0, tk.END)
            connections_widget.insert(tk.END, "\n".join([str(client.get_extra_info('peername')) + f" - {clients[client]}" for client in clients]))
        writer.close()
        await writer.wait_closed()
        print(f"Соединение с {client_address} разорвано")

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





