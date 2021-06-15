import os,json
import tkinter as tk
from tkinter import ttk as ttk
from tkinter import filedialog



class Application:
    def __init__(self, master=None):
        self.master = master

        #set main window configurations
        self.master.title("Veritas")
        self.background = 'white'
        self.master.geometry('1024x800')
        self.master.config(background=self.background)

        #set components style
        style = ttk.Style()
        self.std_font = ('Helvetica',12)
        self.button_font = ('Helvetica',10)
        style.configure("TButton",background=self.background, font = self.button_font)
        style.configure("Download.TButton",background=self.background,size=(12,12))
        style.configure("TFrame",background=self.background)
        style.configure("TLabel",background=self.background,font=self.std_font)
        style.configure("NumberofFiles.TLabel",background=self.background,font=('Helvetica',10,'bold'))
        style.configure("Subtitle.TLabel",background=self.background,font=('Helvetica',15,'bold'))
        style.configure("Header.TLabel",background=self.background,font=('Helvetica',20,'bold'))


        #document's path
        self.files_path = tk.StringVar()

        #JSON files in the current directory
        self.json_files = []

        #Number of JSON files in the current directory
        self.number_of_files_string = tk.StringVar()
        self.number_of_files_string.set('')

        #data that will be analyzed
        self.data_dict = {}

        self.create_widgets()

    def create_header(self,parent):
        parent.columnconfigure(0, weight=1,minsize = 1024)
        parent.rowconfigure(0, weight=1)
        mainLable = ttk.Label(parent, text = "Nova consulta", style = 'Header.TLabel')
        mainLable.grid(row=0,column=0)

    def create_loadfiles(self,parent):
        top_frame = ttk.Frame(parent)
        top_frame.grid(row = 0)
        middle_frame = ttk.Frame(parent)
        middle_frame.grid(row = 1)
        bottom_frame = ttk.Frame(parent)
        bottom_frame.grid(row = 2)

        local_label = ttk.Label(top_frame ,text = 'Local dos arquivos:')
        local_label.grid(row = 0, column = 0, padx=10)

        path_entry = ttk.Entry(top_frame,textvariable = self.files_path, justify=tk.RIGHT, width=40, validatecommand = self.check_directory, validate = 'focusout')
        path_entry.grid(row = 0, column = 1,columnspan=5)

        procurar_button = ttk.Button(top_frame,text='Procurar')
        procurar_button.bind('<Button-1>',self.find_path)
        procurar_button.grid(row = 0, column = 6, padx = 10)

        number_of_files_label = ttk.Label(middle_frame,textvariable=self.number_of_files_string, style = 'NumberofFiles.TLabel')
        number_of_files_label.grid(row = 0,pady = 20)

        download_label = ttk.Label(bottom_frame,text = 'Caso não tenha os arquivos baixados em sua máquina, baixe-os da nossa base de dados aqui:')
        download_label.grid(row = 0, column = 0)

        download_button = ttk.Button(bottom_frame, style = 'Download.TButton', text = 'Download')
        download_button.grid(row = 0, column = 1, padx = 10)

    def find_path(self, event):
        path = tk.filedialog.askdirectory(mustexist = True, title = 'Selecione o diretório dos arquivos JSON')
        self.files_path.set(path)
        self.check_directory()

    def check_directory(self):
        try:
            self.json_files = [json_file for json_file in os.listdir(self.files_path.get()) if json_file.endswith('.json')]
        except FileNotFoundError:
            tk.messagebox.showerror(title='Erro',message='Diretório inválido')

        number_of_files = len(self.json_files)
        self.number_of_files_string.set(f'Há {number_of_files} arquivos JSON no diretório selecionado')

        #decode JSON
        print(self.files_path.get() +'/'+ self.json_files[0])
        self.data_dict = json.loads(self.files_path.get() +'/'+ self.json_files[0])

        if (number_of_files == 0):
            return False
        else:
            return True

    def create_filter(self,parent):
        headerFrame = ttk.Frame(parent)
        headerFrame.grid(row = 0)
        optionsFrame = ttk.Frame(parent)
        optionsFrame.grid(row = 1 , pady = 20)

        headerLabel = ttk.Label(headerFrame,text = 'Filtros', style = 'Subtitle.TLabel')
        headerLabel.grid(row = 0)
    def create_query(self,parent):
        print('oi2')



    def create_widgets(self):
        #Create frames
        self.headerFrame = ttk.Frame(self.master)
        self.loadfilesFrame = ttk.Frame(self.master)
        self.filtersFrame = ttk.Frame(self.master)
        self.queryFrame = ttk.Frame(self.master)
        self.headerFrame.grid(row = 0,pady = 20)
        self.loadfilesFrame.grid(row = 1, pady = 20)
        self.filtersFrame.grid(row = 2, pady = 20)
        self.queryFrame.grid(row = 3, pady = 20)

        #Header
        self.create_header(self.headerFrame)

        #LoadFiles
        self.create_loadfiles(self.loadfilesFrame)

        #Filters
        self.create_filter(self.filtersFrame)

        #Query
        self.create_query(self.queryFrame)

        #self.consultarButton = ttk.Button(self.leftMenu,text = "Consultar")
        #self.downloadButton = ttk.Button(self.leftMenu,text = "Download de documentos")
        #self.consultarButton.grid(row = 0)
        #self.downloadButton.grid(row = 1)
        #self.exit = ttk.Button(self.centralFrame, style="TButton2.TButton")
        #self.exit["text"] = "Sair"
        #self.exit["font"] = ("Calibri", "10")
        #self.exit["width"] = 5
        #self.exit["command"] = self.changeText
        #self.exit.pack()
    # def changeText(self):
    #     if self.msg["text"] == "Veritas":
    #         self.msg["text"] = "ClicouuuUUUUUUUUUUUU"
    #     else:
    #         self.msg["text"] = "Veritas"
root = tk.Tk()
Application(root)
root.mainloop()
