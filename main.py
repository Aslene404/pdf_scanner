import pytesseract
from gtts import gTTS
#import os
import fitz  # PyMuPDF
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import pygame
from tkinter import simpledialog
#from PyPDF2 import PdfReader, PdfWriter
#from PyPDF2.generic import AnnotationBuilder
from tkinter import messagebox
import shutil

class PDFViewerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Viewer")
        self.root.geometry("800x600")

        self.canvas = tk.Canvas(self.root)
        # self.canvas.pack(expand=True, fill=tk.BOTH)
        # making the window scrollable

        self.canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar = tk.Scrollbar(root, command=self.canvas.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.selection_rect = None
        self.selection_start = None
        self.pdf_document = None
        self.page_number = 0
       
       
        ####################### for annotation ###############################
        self.my_i=None
        self.pdfPath=None
        ####################### for annotation ###############################


        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open PDF", command=self.open_pdf)

        nav_frame = tk.Frame(self.root)
        nav_frame.pack()

        self.prev_button = tk.Button(nav_frame, text="Previous", command=self.show_prev_page)
        self.prev_button.pack(side=tk.LEFT)

        self.next_button = tk.Button(nav_frame, text="Next", command=self.show_next_page)
        self.next_button.pack(side=tk.LEFT)

    def open_pdf(self):
        file_path = filedialog.askopenfilename(filetypes=[("PDF Files", "*.pdf"), ("All Files", "*.*")])
        if file_path:
            print("-------------------------file_path----------------------:",file_path)
            self.pdfPath=file_path
            self.load_pdf_document(file_path, 0)

  
  
    def load_pdf_document(self,file_path, pageNumber):
        self.pdf_document = fitz.open(file_path)
        self.page_number = pageNumber
        self.show_page()


    def show_page(self):
        if self.pdf_document is not None:
            page = self.pdf_document.load_page(self.page_number)
            image = page.get_pixmap()

            image_qt = Image.frombytes("RGB", [image.width, image.height], image.samples)
            image_tk = ImageTk.PhotoImage(image_qt)

            self.canvas.config(width=image.width, height=image.height)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=image_tk)
            self.canvas.image = image_tk

    def show_prev_page(self):
        if self.pdf_document is not None and self.page_number > 0:
            self.page_number -= 1
            self.show_page()

    def show_next_page(self):
        if  self.pdf_document is not None and self.page_number < len(self.pdf_document) - 1:
            self.page_number += 1
            self.show_page()

    def on_press(self, event):
        self.selection_start = (event.x, event.y)

    def on_drag(self, event):
       x, y = event.x, event.y
       if self.selection_rect:
           self.canvas.delete(self.selection_rect)

       x0, y0 = self.selection_start
       x1, y1 = x, y

       if x < x0:  # If dragging from right to left, adjust coordinates
           x0, x1 = x, x0

       if y < y0:  # If dragging from bottom to top, adjust coordinates
           y0, y1 = y, y0

       self.selection_rect = self.canvas.create_rectangle(x0, y0, x1, y1, outline="red", width=2)


    def on_release(self, event):
        x0, y0 = self.selection_start
        x1, y1 = event.x, event.y

        print ("xxxet ygeeet :", x0,y0,x1,y1)
        #self.canvas.delete(self.selection_rect)

        if self.pdf_document is not None:
            page = self.pdf_document.load_page(self.page_number)
            image = page.get_pixmap()

            image_qt = Image.frombytes("RGB", [image.width, image.height], image.samples)
            x0, x1 = min(x0, x1), max(x0, x1)
            y0, y1 = min(y0, y1), max(y0, y1)
            cropped_image = image_qt.crop((x0, y0, x1, y1))

            # save_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG Files", "*.png")])
            #if save_path:
          
            cropped_image.save('output_image.png')
            image_file_path = 'output_image.png'

            extracted_text = read_text_from_image(image_file_path)
            ####################### for annotation ###############################     
            self.my_i = simpledialog.askstring("Input"," Add annotation", parent=self.canvas)
            print(self.my_i)    
            if self.my_i : 
               messagebox.showinfo("Success", "Annotations added successfully!")
            
            point = fitz.Point(x0, y0)  # top-left coordinates of the icon
            annot = page.add_text_annot(point,self.my_i)
            self.pdf_document.save("annotatedPdf.pdf")   # save changes in a new file
            shutil.move("annotatedPdf.pdf", self.pdfPath) # move changes from annotatedPdf.pdf to the original file
            self.load_pdf_document(self.pdfPath,self.page_number)
            self.show_page()
            
            ####################### added by me ###############################

            print("------------- extracted_text -----------> ",extracted_text)
            filename = 'output.mp3'
            text_to_speech(extracted_text, filename=filename)
            play_audio(filename)

    




def convert_pdf_page_to_png(pdf_path, page_number, output_path):
    # Open the PDF file
    pdf_document = fitz.open(pdf_path)

    # Get the specific page
    page = pdf_document.load_page(page_number - 1)  # Page numbers are 0-indexed in fitz

    # Render the page as an image (300 DPI resolution, adjust if needed)
    image = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))

    # Save the image as a PNG file
    image.save(output_path)

    # Close the PDF document
    pdf_document.close()


def read_text_from_image(image_path):
    # Open the image using PIL (Python Imaging Library)
    image = Image.open(image_path)
    #config path
    # r'C:\Program Files\Tesseract-OCR\tesseract.exe' for Aslene
    # r'/usr/bin/tesseract' for Rihem
 
    #pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    pytesseract.pytesseract.tesseract_cmd =  r'/usr/bin/tesseract'



    # Perform OCR to extract text from the image
    text = pytesseract.image_to_string(image)
    print("----------------------text------------------ :", text)

    return text


def text_to_speech(text, language='en', filename='output.mp3'):
    tts = gTTS(text=text, lang=language, slow=False)
    pygame.mixer.quit() # quit the previous audio so we can make another one
    tts.save(filename)
    # os.system(f"start {filename}")  # This will play the saved speech file using the default audio player

def play_audio(filename):
    pygame.mixer.init()

    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFViewerApp(root)
    root.mainloop()
    # Replace 'your_image.png' with the path to your image file
    # pdf_file_path = 'FI-GL23-082.pdf'
    # page_number = 5
    # output_image_path = 'output_image.png'
    # convert_pdf_page_to_png(pdf_file_path, page_number, output_image_path)

