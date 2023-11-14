import asyncio
import threading
import tkinter as tk
from tkinter import scrolledtext

clients = {}

async def client_loop(reader, writer, client_address, connections_widget, messages_widget):
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
            
            message_send = f"Личное сообщение от {clients[writer]} - " + message.split()[2]

            client.write(message_send.encode())
            await client.drain()
            print(f"Сообщение отправлено {clients[client]}")

        elif message.startswith('/users'):
            message = "Список пользователей: " + ", ".join(clients[i] for i in clients)
            writer.write(message.encode())
            await writer.drain()
            print(f"Команда отправлена {clients[writer]}")

        else:
            for client in clients:
                message_send = f" {clients[writer]} - " + message
                client.write(message_send.encode())
                await client.drain()
                print("Сообщение отправлено")

async def handle_client(reader, writer, connections_widget, messages_widget):
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





