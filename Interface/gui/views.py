from abc import ABC, abstractmethod
import os
import tkinter as tk
from tkinter import ttk as ttk
from tkinter import filedialog, font
from dateutil.parser import parse

class View(ttk.Frame):
    @abstractmethod
    def create_view():
        raise NotImplementedError

class LoadFilesView(View):

    def __init__(self, parent, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        #set components style
        self.style = ttk.Style()
        self.background = 'white'
        self.std_font = ('Helvetica',12)
        self.button_font = ('Helvetica',10)
        self.verytiny_font = ('Helvetica',8)
        self.style.configure("TButton",background=self.background, font = self.button_font)
        self.style.configure("Download.TButton",background=self.background,size=(12,12))
        self.style.configure("TFrame",background=self.background)
        self.style.configure("TLabel",background=self.background,font=self.std_font)
        self.style.configure("NumberofFiles.TLabel",background=self.background,font=('Helvetica',10,'bold'))
        self.style.configure("Tiny.TLabel",background=self.background,font=('Helvetica',10))
        self.style.configure("Subtitle.TLabel",background=self.background,font=('Helvetica',15,'bold'))
        self.style.configure("Header.TLabel",background=self.background,font=('Helvetica',20,'bold'))
        self.style.configure('TCombobox',background=self.background, font=('Helvetica',5))
        self.option_add("*TCombobox*Listbox*Font", self.verytiny_font)

        #document's path
        self.files_path = tk.StringVar()

        #Number of JSON files in the current directory
        self.number_of_files_string = tk.StringVar()
        self.number_of_files_string.set('')

    def create_view(self):
        #Create frames
        self.headerFrame = ttk.Frame(self)
        self.loadfilesFrame = ttk.Frame(self)
        self.filtersFrame = ttk.Frame(self)

        self.headerFrame.grid(row = 0,pady = 20)
        self.loadfilesFrame.grid(row = 1, pady = 20)
        self.filtersFrame.grid(row = 2)


        #Header
        self.create_header(self.headerFrame)

        #LoadFiles
        self.create_loadfiles(self.loadfilesFrame)

        #Filters
        self.create_filter(self.filtersFrame)

    def create_header(self,parent):
        parent.columnconfigure(0, weight=1,minsize = 1024)
        parent.rowconfigure(0, weight=1)
        self.mainLable = ttk.Label(parent, text = "Nova consulta", style = 'Header.TLabel')
        self.mainLable.grid(row=0,column=0)

    def create_loadfiles(self,parent):
        self.top_frame = ttk.Frame(parent)
        self.top_frame.grid(row = 0)
        self.middle_frame = ttk.Frame(parent)
        self.middle_frame.grid(row = 1)
        self.middle_frame2 = ttk.Frame(parent)
        self.middle_frame2.grid(row = 2)
        self.bottom_frame = ttk.Frame(parent)
        self.bottom_frame.grid(row = 3, pady = 20)

        self.local_label = ttk.Label(self.top_frame ,text = 'Local dos arquivos:')
        self.local_label.grid(row = 0, column = 0, padx=10)

        self.path_entry = ttk.Entry(self.top_frame,textvariable = self.files_path,validatecommand = self.check_directory, justify=tk.RIGHT, width=40, validate = 'all')
        self.path_entry.grid(row = 0, column = 1,columnspan=5)

        self.search_button = ttk.Button(self.top_frame,text='Procurar')
        self.search_button.grid(row = 0, column = 6, padx = 10)
        self.search_button.bind('<Button-1>',self.find_path)

        self.number_of_files_label = ttk.Label(self.middle_frame,textvariable=self.number_of_files_string, style = 'NumberofFiles.TLabel')
        self.number_of_files_label.grid(row = 0,pady = 10)


        self.process_files_button = ttk.Button(self.middle_frame, text = 'Processar arquivos')
        self.process_files_button.grid(row = 1, column = 0)
        self.process_files_label = ttk.Label(self.middle_frame, text = '(Este botão gerará os filtros e consultas disponíveis)', style = 'Tiny.TLabel')
        self.process_files_label.grid(row = 2, column = 0)

        self.download_label = ttk.Label(self.bottom_frame,text = 'Caso não tenha os arquivos baixados em sua máquina, baixe-os da nossa base de dados aqui:')
        self.download_label.grid(row = 0, column = 0)

        self.download_button = ttk.Button(self.bottom_frame, style = 'Download.TButton', text = 'Download')
        self.download_button.grid(row = 0, column = 1, padx = 10)

    def find_path(self,event):
        path = tk.filedialog.askdirectory(mustexist = True, title = 'Selecione o diretório dos arquivos JSON')
        self.files_path.set(path)
        self.check_directory()

    def check_directory(self):
        try:
            self.json_files = [json_file for json_file in os.listdir(self.files_path.get()) if json_file.endswith('.json')]
        except FileNotFoundError:
            tk.messagebox.showerror(title='Erro',message='Diretório inválido')

        number_of_files = len(self.json_files)
        if number_of_files > 1:
            self.number_of_files_string.set(f'Há {number_of_files} arquivos JSON no diretório selecionado, todos serão considerados.')
        elif number_of_files == 0:
            self.number_of_files_string.set('Não há nenhum arquivo JSON no diretório selecionado :(')
        else:
            self.number_of_files_string.set('')


        if (number_of_files == 0):
            return False
        else:
            return True

    def create_filter(self,parent):
        self.headerFrame = ttk.Frame(parent)
        self.headerFrame.grid(row = 0)
        #this is an attribute because its gonna be used by other method
        self.optionsFrame = ttk.Frame(parent)
        self.optionsFrame.grid(row = 1 , pady = 20)

        self.headerLabel = ttk.Label(self.headerFrame,text = 'Filtros', style = 'Subtitle.TLabel')
        self.headerLabel.grid(row = 0)

    def create_combobox(self,key_to_possible_values_dic):
        self.filtersLabel = []
        self.filtersCombobox = []
        for i,key in enumerate(key_to_possible_values_dic.keys()):
            self.filtersLabel.append(ttk.Label(self.optionsFrame, text = key, justify = tk.RIGHT))
            self.filtersLabel[i].grid(row=i, column=0, sticky = tk.E, padx = 10)
            if self.is_date(key_to_possible_values_dic[key][0]):
                print('é data')
            else:
                print('não é data')
            self.filtersCombobox.append(ttk.Combobox(self.optionsFrame,font = self.verytiny_font,justify = 'right', state = 'readonly', values = list(key_to_possible_values_dic[key])))
            self.filtersCombobox[i].bind('<Button-1>',self.combo_configure)
            self.filtersCombobox[i].grid(row=i, column=1, sticky=tk.E)

    #Configure combobox so its size adapts to its values
    def combo_configure(self,event):
        combo = event.widget
        style = ttk.Style()

        max_string = max(combo.cget('values'), key=len)
        font = combo.cget('font')
        width = tk.font.Font(font = font).measure(max_string + '0000' ) - combo.winfo_width()

        style.configure('TCombobox', postoffset=(0,0,width,0))
        combo.configure(style='TCombobox')

    def is_date(self,string, fuzzy=False):
        """
        Return whether the string can be interpreted as a date.

        :param string: str, string to check for date
        :param fuzzy: bool, ignore unknown tokens in string if True
        """
        try:
            parse(string, fuzzy=fuzzy)
            return True

        except ValueError:
            return False