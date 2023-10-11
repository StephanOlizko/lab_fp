from functools import reduce


orders = [
    {"order_id": 1, "customer_id": 103, "amount": 387.18},
    {"order_id": 2, "customer_id": 101, "amount": 226.43},
    {"order_id": 3, "customer_id": 119, "amount": 380.16},
    {"order_id": 4, "customer_id": 102, "amount": 487.41},
    {"order_id": 5, "customer_id": 120, "amount": 322.51},
    {"order_id": 6, "customer_id": 115, "amount": 102.85},
    {"order_id": 7, "customer_id": 112, "amount": 421.49},
    {"order_id": 8, "customer_id": 111, "amount": 243.67},
    {"order_id": 9, "customer_id": 118, "amount": 153.21},
    {"order_id": 10, "customer_id": 113, "amount": 85.95},
    {"order_id": 11, "customer_id": 103, "amount": 313.68},
    {"order_id": 12, "customer_id": 102, "amount": 270.87},
    {"order_id": 13, "customer_id": 101, "amount": 156.49},
    {"order_id": 14, "customer_id": 115, "amount": 128.39},
    {"order_id": 15, "customer_id": 114, "amount": 231.44},
    {"order_id": 16, "customer_id": 116, "amount": 101.09},
    {"order_id": 17, "customer_id": 119, "amount": 271.73},
    {"order_id": 18, "customer_id": 111, "amount": 369.83},
    {"order_id": 19, "customer_id": 101, "amount": 107.06},
    {"order_id": 20, "customer_id": 120, "amount": 455.55}
    ]

target_customer_id = 101

filtered_orders = list(filter(lambda order: order["customer_id"] == target_customer_id, orders))

def calculate_total_amount(acc, order):
    return acc + order["amount"]

total_amount = reduce(lambda acc, order: calculate_total_amount(acc, order), filtered_orders, 0.0)

filtered_orders = list(filtered_orders)

if filtered_orders:
    average_amount = total_amount / len(filtered_orders)
else:
    average_amount = 0.0

print("Фильтрованные заказы для клиента с идентификатором", target_customer_id)
for order in filtered_orders:
    print(f"Заказ {order['order_id']}, сумма: {order['amount']}")

print()
print("Общая сумма заказов для клиента:", total_amount)
print("Средняя стоимость заказов для клиента:", average_amount)
