# -*- coding: utf-8 -*-

import cv2
import numpy as np
import os
import csv
import time
import threading
from tkinter import Tk, Button, Label, filedialog

def classify_star_type(rgb_values):
    # Разбираем значения RGB
    r, g, b = rgb_values
    avg = (r + g + b) / 3
    # Определяем тип звезды на основе цвета
    if avg > 80:
        return "Hot star (blue)"
    elif avg > 40:
        return "Average temp (yellow/white)"
    elif avg > 10:
        return "Low temp (orange/red)"
    else:
        return "Unknown type"


def analyze_and_draw_objects(image, output_folder, file_name):
    flgFind = False

    # Сохранение результата в файл CSV
    csv_file_path = os.path.join(output_folder, "results.tsv")
    with open(csv_file_path, "a", newline="") as csvfile:
        fieldnames = ["File Name", "Object ID", "Object size", "Object area", "Object average color", "Object brightness", "Center (x, y)", "Star type"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Инициализация уникального ID для объектов
        object_id = 1

        min_area = 0.5
        max_area = 100

        for contour in contours:
            ((x, y), radius) = cv2.minEnclosingCircle(contour)
            _, _, width, height = cv2.boundingRect(contour)
            center = (int(x), int(y))
            radius = int(radius)

            # Выделение области, соответствующей объекту
            roi = image[int(y) - radius:int(y) + radius, int(x) - radius:int(x) + radius]
            # Вычисление площади объекта
            area = cv2.contourArea(contour)

            ratio = width / height
            if ratio < 5:
                if min_area < area < max_area and height != 0 and width != 0:
                    avg_color = np.mean(roi, axis=(1, 0))
                    brightness = np.mean(roi)

                    # Отрисовка красного круга
                    cv2.circle(image, center, radius * 2 + 5, (0, 0, 255), 2)

                    # Нанесение уникального ID рядом с красным кругом
                    cv2.putText(image, str(object_id), (int(x) + 10, int(y) + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                    # Запись результатов в CSV
                    writer.writerow({
                        "File Name": file_name,
                        "Object ID": object_id,
                        "Object size": f"{width}x{height}",
                        "Object area": area,
                        "Object average color": avg_color,
                        "Object brightness": brightness,
                        "Center (x, y)": f"{center[0]}, {center[1]}",
                        "Star type": classify_star_type(avg_color)
                    })
                    flgFind = True
                    # Увеличение уникального ID для следующего объекта
                    object_id += 1
            else:
                if min_area < area < max_area and height != 0 and width != 0:
                    cv2.circle(image, center, radius * 2 + 5, (0, 0, 255), 2)
                    # Нанесение уникального ID рядом с красным кругом
                    cv2.putText(image, str("dobj"), (int(x) + 10, int(y) + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                    # Запись результатов в CSV
                    writer.writerow({
                        "File Name": file_name,
                        "Object ID": "Deformed_object",
                        "Object size": f"{width}x{height}",
                        "Object area": area,
                        "Object average color": "Deformed_object",
                        "Object brightness": "Deformed_object",
                        "Center (x, y)": f"{center[0]}, {center[1]}",
                        "Star type": classify_star_type(avg_color)
                    })
                    flgFind = True
                    # Увеличение уникального ID для следующего объекта


    return (image, flgFind)

def process_part(image, output_folder, file_name):
    analyzed_image, flg = analyze_and_draw_objects(image, output_folder, file_name)
    
    if flg:
        # Save the analyzed image with objects drawn
        analyzed_part_path = os.path.join(output_folder, f"analyzed_{file_name}")
        cv2.imwrite(analyzed_part_path, analyzed_image)

def split_and_analyze_image(input_image_path, output_folder, part_size=(256, 256)):
    # Read the input image
    image = cv2.imread(input_image_path)

    # Get the dimensions of the input image
    height, width, _ = image.shape

    # Create a folder for saving parts
    if output_folder == "":
        output_folder = input_image_path.split("/")[-1]
        output_folder = output_folder.split(".")[0]

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Create a CSV file for results
    csv_file_path = os.path.join(output_folder, "results.tsv")
    with open(csv_file_path, "w", newline="") as csvfile:
        fieldnames = ["File Name", "Object ID", "Object size", "Object area", "Object average color","Object brightness", "Center (x, y)", "Star type"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()

    # Split the image into parts
    threads = []
    for i in range(0, height, part_size[0]):
        for j in range(0, width, part_size[1]):
            # Extract the part from the original image
            part = image[i:i + part_size[0], j:j + part_size[1]]

            # Save each part separately
            part_path = os.path.join(output_folder, f"part_{i // part_size[0]}_{j // part_size[1]}.jpg")
            cv2.imwrite(part_path, part)

            # Create a thread for analyzing and drawing objects in each part
            file_name = f"part_{i // part_size[0]}_{j // part_size[1]}.jpg"
            thread = threading.Thread(target=process_part, args=(part, output_folder, file_name))
            threads.append(thread)

    # Start all threads
    start_time = time.time()
    for thread in threads:
        thread.start()

    # Wait for all threads to finish
    for thread in threads:
        thread.join()

    # Measure and print the total execution time
    end_time = time.time()
    total_time = end_time - start_time
    print(f"Total execution time: {total_time:.2f} seconds")

def browse_image():
    global input_image_path
    input_image_path = filedialog.askopenfilename()
    file_label.config(text=f"Selected Image: {os.path.basename(input_image_path)}")

def analyze_image():
    global input_image_path, output_folder
    result_label.config(text="Processing...")

    start_time = time.time()
    split_and_analyze_image(input_image_path, output_folder, part_size)
    end_time = time.time()

    total_time = end_time - start_time
    result_label.config(text=f"Analysis complete.\nTotal time: {total_time:.2f} seconds")

if __name__ == "__main__":
    # Global variables
    input_image_path = ""
    part_size = (256, 256)
    output_folder = ""

    # Create Tkinter window
    root = Tk()
    root.geometry("200x200")
    root.title("Image Analysis")

    # Browse Button
    browse_button = Button(root, text="Browse Image", command=browse_image)
    browse_button.pack()

    # Selected File Label
    file_label = Label(root, text="Selected Image: None")
    file_label.pack()

    # Analyze Button
    analyze_button = Button(root, text="Analyze Image", command=analyze_image)
    analyze_button.pack()

    # Result Label
    result_label = Label(root, text="")
    result_label.pack()

    # Run the Tkinter event loop
    root.mainloop()