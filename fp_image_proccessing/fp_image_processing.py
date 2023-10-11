import os
import threading
from tkinter import *
from PIL import Image, ImageFilter, ImageOps

def process_image(input_image, output_folder, filters):
    try:
        image = Image.open(input_image)
        
        for filter_function in filters:
            image = filter_function(image)
            
        _, filename = os.path.split(input_image)
            
        output_path = os.path.join(output_folder, f"{filename}")
            
        image.save(output_path)
        print(f"Сохранено: {output_path}")
    except Exception as e:
        print(f"Ошибка при обработке {input_image}: {e}")

def apply_sepia_effect(image):
    sepia_image = ImageOps.colorize(image.convert('L'), "#704214", "#C0A080")
    return sepia_image

def resize_image(image):
    width, height = image.size
    new_size = (width // 3, height // 3)
    resized_image = image.resize(new_size, Image.ANTIALIAS)
    return resized_image

def apply_blur(image):
    return image.filter(ImageFilter.GaussianBlur(2)) 

def apply_sharp(image):
    return image.filter(ImageFilter.SHARPEN)    

def apply_edge(image):
    return image.filter(ImageFilter.EDGE_ENHANCE_MORE)  



def main():
    input_folder = "input_images_folder"
    output_folder = "output_images_folder"
    
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    input_images = [os.path.join(input_folder, filename) for filename in os.listdir(input_folder) if filename.endswith(('.jpg', '.jpeg', '.png'))]
    
    window = Tk()
    window.geometry("500x200")
    window.title("Выбор фильтров")
    
    sepia_var = IntVar()
    resize_var = IntVar()
    blur_var = IntVar()
    sharp_var = IntVar()
    edge_var = IntVar()
    
    sepia_checkbox = Checkbutton(window, text="Сепия", variable=sepia_var)
    resize_checkbox = Checkbutton(window, text="Уменьшение размера", variable=resize_var)
    blur_checkbox = Checkbutton(window, text="Размытие", variable=blur_var)
    sharp_checkbox = Checkbutton(window, text="Резкость", variable=sharp_var)
    edge_checkbox = Checkbutton(window, text="Увеличение резкости граней", variable=edge_var)
    
    sepia_checkbox.pack()
    resize_checkbox.pack()
    blur_checkbox.pack()
    sharp_checkbox.pack()
    edge_checkbox.pack()
    
    def apply_and_process():

        selected_filters = []
        if sepia_var.get():
            selected_filters.append(apply_sepia_effect)
        if resize_var.get():
            selected_filters.append(resize_image)
        if blur_var.get():
            selected_filters.append(apply_blur)
        if sharp_var.get():
            selected_filters.append(apply_sharp)
        if edge_var.get():
            selected_filters.append(apply_edge)

        threads = []
        for input_image in input_images:
            thread = threading.Thread(target=process_image, args=(input_image, output_folder, selected_filters))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        window.quit()
    
    apply_button = Button(window, text="Применить и обработать", command=apply_and_process)
    apply_button.pack()

    window.mainloop()

if __name__ == "__main__":
    main()
