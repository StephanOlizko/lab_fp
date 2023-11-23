import cv2
import numpy as np
import os
import csv
import time
import threading


def analyze_and_draw_objects(image, output_folder, file_name):
    # Сохранение результата в файл CSV
    csv_file_path = os.path.join(output_folder, "results.tsv")
    with open(csv_file_path, "a", newline="") as csvfile:
        fieldnames = ["File Name", "Object ID", "Object size", "Object area", "Object average color", "Center (x, y)"]
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames, delimiter='\t')

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Инициализация уникального ID для объектов
        object_id = 1

        min_area = 0.5
        max_area = 10000

        for contour in contours:
            ((x, y), radius) = cv2.minEnclosingCircle(contour)
            center = (int(x), int(y))
            radius = int(radius)

            # Выделение области, соответствующей объекту
            roi = image[int(y) - radius:int(y) + radius, int(x) - radius:int(x) + radius]

            # Получение размеров области
            height, width, _ = roi.shape

            # Вычисление площади объекта
            area = cv2.contourArea(contour)

            if min_area < area < max_area and height != 0 and width != 0:
                avg_color = np.mean(roi, axis=(1, 0))

                # Запись результатов в CSV
                writer.writerow({
                    "File Name": file_name,
                    "Object ID": object_id,
                    "Object size": f"{width}x{height}",
                    "Object area": area,
                    "Object average color": avg_color,
                    "Center (x, y)": f"{center[0]}, {center[1]}"
                })

                # Отрисовка красного круга
                cv2.circle(image, center, radius * 2 + 5, (0, 0, 255), 2)

                # Нанесение уникального ID рядом с красным кругом
                cv2.putText(image, str(object_id), (int(x) + 10, int(y) + 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

                # Увеличение уникального ID для следующего объекта
                object_id += 1

    return image

def process_part(image, output_folder, file_name):
    analyzed_image = analyze_and_draw_objects(image, output_folder, file_name)
    
    # Save the analyzed image with objects drawn
    analyzed_part_path = os.path.join(output_folder, f"analyzed_{file_name}")
    cv2.imwrite(analyzed_part_path, analyzed_image)

def split_and_analyze_image(input_image_path, output_folder, part_size=(256, 256)):
    # Read the input image
    image = cv2.imread(input_image_path)

    # Get the dimensions of the input image
    height, width, _ = image.shape

    # Create a folder for saving parts
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Create a CSV file for results
    csv_file_path = os.path.join(output_folder, "results.tsv")
    with open(csv_file_path, "w", newline="") as csvfile:
        fieldnames = ["File Name", "Object ID", "Object size", "Object area", "Object average color", "Center (x, y)"]
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

if __name__ == "__main__":
    # Specify the path to the large image
    input_image_path = "hiptyc_2020_32k_gal.jpg"

    # Specify the size of each part
    part_size = (256, 256)

    # Create a folder for saving parts
    output_folder = os.path.splitext(input_image_path)[0] + "_parts"

    # Call the function to split and analyze the image
    split_and_analyze_image(input_image_path, output_folder, part_size)

    print("Image successfully split and analyzed.")