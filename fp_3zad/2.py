from functools import reduce

users = [
    {"name": "Alice", "expenses": [145, 212, 317, 482]},
    {"name": "Bob", "expenses": [253, 163, 497, 374]},
    {"name": "Charlie", "expenses": [425, 356, 129, 189]},
    {"name": "David", "expenses": [392, 309, 298, 415]},
    {"name": "Eve", "expenses": [315, 453, 214, 198]},
    {"name": "Frank", "expenses": [380, 125, 446, 253]},
    {"name": "Grace", "expenses": [254, 110, 174, 466]},
    {"name": "Hannah", "expenses": [198, 379, 329, 434]},
    {"name": "Isaac", "expenses": [179, 444, 232, 381]},
    {"name": "Jack", "expenses": [302, 377, 392, 328]},
    {"name": "Kate", "expenses": [384, 329, 124, 321]},
    {"name": "Liam", "expenses": [465, 488, 293, 242]},
    {"name": "Mia", "expenses": [486, 318, 328, 490]},
    {"name": "Noah", "expenses": [427, 224, 253, 396]},
    {"name": "Olivia", "expenses": [455, 172, 177, 352]},
    {"name": "Peter", "expenses": [146, 289, 255, 369]},
    {"name": "Quinn", "expenses": [384, 283, 298, 177]},
    {"name": "Rachel", "expenses": [421, 180, 147, 205]},
    {"name": "Sam", "expenses": [276, 455, 428, 292]},
    {"name": "Tom", "expenses": [185, 409, 182, 442]}
    ]

def filter_users(user):
    return sum(user["expenses"]) > 1300

filtered_users =  list(filter(lambda user: filter_users(user), users))

def calculate_total_expenses(user):
    return sum(user["expenses"])

total_expenses_per_user = list(map(lambda user: (user["name"], calculate_total_expenses(user)), users))
total_expenses_per_filtered = list(map(lambda user: (user["name"], calculate_total_expenses(user)), filtered_users))

total_expenses = reduce(lambda x, y: x + y[1], total_expenses_per_filtered, 0)

print("Отфильтрованные пользователи:")
for user in filtered_users:
    print(user["name"])

print()
print("Общая сумма расходов для каждого пользователя:")
for name, total in total_expenses_per_user:
    print(f"{name}: {total}")

print()
print("Общая сумма расходов всех отфильтрованных пользователей:", total_expenses)
