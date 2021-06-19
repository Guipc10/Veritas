import os,json
import tkinter as tk
from tkinter import ttk as ttk
from tkinter import filedialog, font
from dateutil.parser import parse




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
        self.verytiny_font = ('Helvetica',8)
        style.configure("TButton",background=self.background, font = self.button_font)
        style.configure("Download.TButton",background=self.background,size=(12,12))
        style.configure("TFrame",background=self.background)
        style.configure("TLabel",background=self.background,font=self.std_font)
        style.configure("NumberofFiles.TLabel",background=self.background,font=('Helvetica',10,'bold'))
        style.configure("Tiny.TLabel",background=self.background,font=('Helvetica',10))
        style.configure("Subtitle.TLabel",background=self.background,font=('Helvetica',15,'bold'))
        style.configure("Header.TLabel",background=self.background,font=('Helvetica',20,'bold'))
        style.configure('TCombobox',background=self.background, font=('Helvetica',5))
        self.master.option_add("*TCombobox*Listbox*Font", self.verytiny_font)

        #document's path
        self.files_path = tk.StringVar()

        #JSON files in the current directory
        self.json_files = []

        #Number of JSON files in the current directory
        self.number_of_files_string = tk.StringVar()
        self.number_of_files_string.set('')

        #data that will be analyzed, its a list of list of dictionaries
        self.data_list = []

        #the possible values for each metadata, its a dictionary where each item is a set
        self.key_to_possible_values_dic = {}

        #the selected values for filtering, its a list of list of tk.StringVar()
        # self.filtersSelectionValues = []

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
        middle_frame2 = ttk.Frame(parent)
        middle_frame2.grid(row = 2)
        bottom_frame = ttk.Frame(parent)
        bottom_frame.grid(row = 3, pady = 20)

        local_label = ttk.Label(top_frame ,text = 'Local dos arquivos:')
        local_label.grid(row = 0, column = 0, padx=10)

        path_entry = ttk.Entry(top_frame,textvariable = self.files_path, justify=tk.RIGHT, width=40, validatecommand = self.check_directory, validate = 'all')
        path_entry.grid(row = 0, column = 1,columnspan=5)

        procurar_button = ttk.Button(top_frame,text='Procurar')
        procurar_button.bind('<Button-1>',self.find_path)
        procurar_button.grid(row = 0, column = 6, padx = 10)

        number_of_files_label = ttk.Label(middle_frame,textvariable=self.number_of_files_string, style = 'NumberofFiles.TLabel')
        number_of_files_label.grid(row = 0,pady = 10)


        process_files_button = ttk.Button(middle_frame, text = 'Processar arquivos')
        process_files_button.bind('<Button-1>',self.process_json)
        process_files_button.grid(row = 1, column = 0)
        process_files_label = ttk.Label(middle_frame, text = '(Este botão gerará os filtros e consultas disponíveis)', style = 'Tiny.TLabel')
        process_files_label.grid(row = 2, column = 0)

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

    def process_json(self,event):
        #I'M APPENDING TWO DIFFERENT TYPES OF JSON FILES HERE, 1 AND 2 DEGREE CASES, MAY CAUSE ERRORS
        self.data_list.clear()
        for json_file in self.json_files:
            with open(self.files_path.get() +'/'+ json_file,'r') as j:
                self.data_list.append(json.load(j))

        #Get available metadata and it's possible values by iterating over the dictionaries
        self.key_to_possible_values_dic.clear()
        for file in self.data_list:
            for dic in file:
                for key,value in dic.items():
                    if key not in self.key_to_possible_values_dic.keys():
                        self.key_to_possible_values_dic[key] = set()
                    self.key_to_possible_values_dic[key].add(value)

        #remove useless keys from the metadata
        del self.key_to_possible_values_dic['ementa']
        del self.key_to_possible_values_dic['processo']
        del self.key_to_possible_values_dic['cdacordao']
        del self.key_to_possible_values_dic['julgado']

        #sort it alphabetically
        for key in self.key_to_possible_values_dic.keys():
            self.key_to_possible_values_dic[key] = sorted(self.key_to_possible_values_dic[key],key= str.lower)

        #create filtering options according to the obtained metadata
        self.create_combobox()

    def create_combobox(self):
        self.filtersLabel = []
        self.filtersCombobox = []
        scrollbars = []
        for i,key in enumerate(self.key_to_possible_values_dic.keys()):
            self.filtersLabel.append(ttk.Label(self.optionsFrame, text = key, justify = tk.RIGHT))
            self.filtersLabel[i].grid(row=i, column=0, sticky = tk.E, padx = 10)
            if self.is_date(self.key_to_possible_values_dic[key][0]):
                print('é data')
            else:
                print('não é data')
            self.filtersCombobox.append(ttk.Combobox(self.optionsFrame,font = self.verytiny_font,justify = 'right', state = 'readonly', values = list(self.key_to_possible_values_dic[key])))
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

    def create_filter(self,parent):
        headerFrame = ttk.Frame(parent)
        headerFrame.grid(row = 0)
        #this is an attribute because its gonna be used by other method
        self.optionsFrame = ttk.Frame(parent)
        self.optionsFrame.grid(row = 1 , pady = 20)

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
        self.filtersFrame.grid(row = 2)
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
