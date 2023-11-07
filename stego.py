import sys
import os
from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QFileDialog
import numpy as np
from PIL import Image
from art import *
from colorama import init
from colorama import Fore


init(autoreset=True)


class App(QMainWindow):
    def __init__(self):
        super().__init__()

        uic.loadUi('steg.ui', self)
        self.encode_button.clicked.connect(self.encoding)
        self.decode_button.clicked.connect(self.decoding)
        self.get_image_button.clicked.connect(self.get_image)
        
        self.selected_file = None  # Переменная для хранения пути к выбранному изображению
        self.message_edit = self.message_edit
        self.key_edit = self.key_edit
    
    def encoding(self):
        src = self.selected_file
        message = self.message_edit.toPlainText()
        key = self.key_edit.text()
        if src and message and key:
            
            # Извлечь имя и расширение исходного файла
            base_name, ext = os.path.splitext(os.path.basename(src))

            # Создать имя для закодированного файла
            encoded_filename = base_name + "_encoded" + ext

            # Полный путь к закодированному файлу
            encoded_filepath = os.path.join(os.path.dirname(src), encoded_filename)

            Encode(src, message, encoded_filepath, key)

            self.message_edit.setText(f"Успешно. Результат сохранен в '{encoded_filepath}'")
        else:
            self.message_edit.setText("Ошибка: Проверьте, что выбрали изображение и ввели сообщение и ключ.")

    
    def decoding(self):
        self.message_edit.clear()
        src = self.selected_file
        key = self.key_edit.text()
        
        if src and key:
            result = Decode(src, key)
            if result:
                self.message_edit.setText(result)
            else:
                self.message_edit.setText("Скрытое сообщение не найдено.")
        else:
            self.message_edit.setText("Ошибка: Проверьте, что выбрали изображение и ввели ключ.")

    def get_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Выберите файл", "", "All Files (*);;Image Files (*.jpeg, *.jpg, *.png);", options=options)
        
        if file_name:
            self.selected_file = file_name
            print("Выбран файл:", file_name)
        
def Encode(src, message, dest, key):
    img = Image.open(src, 'r')
    width, height = img.size
    array = np.array(list(img.getdata()))

    if img.mode == 'RGB':
        n = 3
    elif img.mode == 'RGBA':
        n = 4

    total_pixels = array.size // n

    message += key
    b_message = ''.join([format(ord(i), "08b") for i in message])
    req_pixels = len(b_message)

    if req_pixels > total_pixels:
        print(Fore.RED + 'ERROR: Need larger file size')
    else:
        index = 0
        for p in range(total_pixels):
            for q in range(0, 3):
                if index < req_pixels:
                    array[p][q] = int(bin(array[p][q])[2:9] + b_message[index], 2)
                    index += 1
        
        array = array.reshape(height, width, n)
        enc_image = Image.fromarray(array.astype('uint8'), img.mode)
        enc_image.save(dest)
        print(Fore.GREEN + 'Image encoded succesfully')


def Decode(src, key):
    img = Image.open(src, 'r')
    array = np.array(list(img.getdata()))

    if img.mode == 'RGB':
        n = 3
    elif img.mode == 'RGBA':
        n = 4

    total_pixels = array.size // n

    hidden_bits = ""
    for p in range(total_pixels):
        for q in range(0, 3):
            hidden_bits += (bin(array[p][q])[2:][-1])

    hidden_bits = [hidden_bits[i:i+8] for i in range(0, len(hidden_bits), 8)]

    message = ""
    for i in range(len(hidden_bits)):
        if message[-len(key):] == key:
            break
        else:
            message += chr(int(hidden_bits[i], 2))

    if key in message:
        print(Fore.GREEN + "Hidden Message:", message[:-len(key)])
        return message[:-len(key)]
    else:
        print(Fore.RED + 'No hidden message found')
    
    

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    ex.show()
    sys.exit(app.exec())