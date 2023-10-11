from functools import reduce

students = [
    {"name": "Alice", "age": 20, "grades": [85, 90, 88, 92]},
    {"name": "Bob", "age": 22, "grades": [78, 89, 76, 85]},
    {"name": "Charlie", "age": 21, "grades": [92, 95, 88, 94]},
    {"name": "David", "age": 23, "grades": [71, 76, 82, 79]},
    {"name": "Eve", "age": 20, "grades": [94, 89, 75, 83]},
    {"name": "Frank", "age": 25, "grades": [90, 91, 84, 87]},
    {"name": "Grace", "age": 18, "grades": [79, 92, 96, 88]},
    {"name": "Hannah", "age": 24, "grades": [87, 85, 91, 79]},
    {"name": "Isaac", "age": 22, "grades": [96, 88, 94, 92]},
    {"name": "Jack", "age": 20, "grades": [77, 83, 89, 91]},
    {"name": "Kate", "age": 19, "grades": [92, 94, 76, 88]},
    {"name": "Liam", "age": 23, "grades": [85, 91, 87, 90]},
    {"name": "Mia", "age": 20, "grades": [78, 82, 95, 86]},
    {"name": "Noah", "age": 24, "grades": [90, 85, 92, 89]},
    {"name": "Olivia", "age": 19, "grades": [88, 79, 91, 84]},
    {"name": "Peter", "age": 21, "grades": [89, 90, 93, 88]},
    {"name": "Quinn", "age": 18, "grades": [76, 82, 79, 88]},
    {"name": "Rachel", "age": 25, "grades": [91, 87, 85, 89]},
    {"name": "Sam", "age": 22, "grades": [94, 89, 87, 91]},
    {"name": "Tom", "age": 20, "grades": [82, 84, 91, 95]}
]

filtered_students = filter(lambda student: student["age"] == 23, students)

def calculate_average(grades):
    return sum(grades) / len(grades)

average_grades = list(map(lambda student: (student["name"], calculate_average(student["grades"])), students))

def find_student_with_highest_average(student1, student2):
    if student1[1] > student2[1]:
        return student1
    else:
        return student2

student_with_highest_average = reduce(find_student_with_highest_average, average_grades)

total_average = sum(map(lambda student: calculate_average(student["grades"]), students)) / len(students)


print("Студенты возраста 23 года:")
for student in filtered_students:
    print(student["name"])

print("\nСредний балл каждого студента:")
for name, avg in average_grades:
    print(f"{name}: {avg}")

print()
print("Студент с самым высоким средним баллом:")
print(f"Имя: {student_with_highest_average[0]}, Средний балл: {student_with_highest_average[1]}")

print()
print("Общий средний балл по всем студентам:", total_average)
