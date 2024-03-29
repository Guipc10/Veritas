from abc import ABC, abstractmethod
import os
import tkinter as tk
from tkinter import ttk as ttk
from tkinter import filedialog, font
from fpdf import FPDF
from dateutil.parser import parse
from gui.util.helper_classes import ScrollFrame
import pandas as pd
import pandastable as pdt

SMALL_BUTTON_WIDTH = 3
TEXT_WIDGET_WIDTH = 160
TEXT_WIDGET_HEIGHT = 50

class View(ttk.Frame):
    @abstractmethod
    def create_view():
        raise NotImplementedError

class ComponentView():
    def __init__(self, parent):
        '''
        Standardize style and background
        '''
        self.style = ttk.Style()
        self.background = 'white'
        self.std_font = ('Helvetica',10)
        self.button_font = ('Helvetica',10)
        self.verytiny_font = ('Helvetica',8)
        self.style.configure("Std.TButton",background=self.background, font = self.button_font)
        self.style.configure("Std.TFrame",background=self.background)
        self.style.configure("Std.TLabel",background=self.background,font=self.std_font)
        self.style.configure('Std.TCheckbutton', background=self.background)

    @abstractmethod
    def create_view():
        '''
        This method creates the component view to get the needed inputs

        Inputs:
        parent: parent frame where the component view is gonna be placed
        view_filters_list: list of the columns that were selected to be shown, it may be necessary in some cases
        '''
        raise NotImplementedError

    @abstractmethod
    def get_extra_input():
        '''
        Returns the necessary input, the format may be of any kind, it just have to match the needs of the matching ModelComponent
        '''
        raise NotImplementedError

class LoadFilesView(View):

    def __init__(self, parent, notebook, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.notebook = notebook
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
        self.pack(fill='both', expand=True, anchor = 'center')
        self.columnconfigure(0,weight = 1)

        #document's path
        self.files_path = tk.StringVar()

        #Number of JSON files in the current directory
        self.number_of_files_string = tk.StringVar()
        self.number_of_files_string.set('')

    def create_view(self):
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

        #Set the button now so the command can be binded by the controller
        self.generatequeryButton = ttk.Button(self.filtersFrame, text = 'Gerar consulta')

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
        self.number_of_files_label.grid(row = 0,column = 0,pady = 10)


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

    def create_filter(self):
        self.headerFrame = ttk.Frame(self.filtersFrame)
        self.headerFrame.grid(row = 0)

        self.selectionfiltersFrame = ttk.Frame(self.filtersFrame)
        self.selectionfiltersFrame.grid(row = 1 , pady = 20)

        self.visualizationfiltersFrame = ttk.Frame(self.filtersFrame)
        self.visualizationfiltersFrame.grid(row = 2, pady = 20)

        # Grid the button that was already created in the create_view method
        self.generatequeryButton.grid(row = 3)

        self.headerLabel = ttk.Label(self.headerFrame,text = 'Filtros de seleção', style = 'Subtitle.TLabel')
        self.headerLabel.grid(row = 0)
        self.headerSubtitleLabel = ttk.Label(self.headerFrame,text = '(Deixe em branco para considerar todos os arquivos)', style = 'Tiny.TLabel')
        self.headerSubtitleLabel.grid(row = 1)

        self.visualfiltersHeaderLabel = ttk.Label(self.visualizationfiltersFrame, text = 'Filtros de visualização', style = 'Subtitle.TLabel')
        self.visualfiltersHeaderLabel.grid(row = 0)
        self.visualfiltersSubtitleLabel = ttk.Label(self.visualizationfiltersFrame, text = '(Selecione as colunas que deseja visualizar na consulta)', style = 'Tiny.TLabel')
        self.visualfiltersSubtitleLabel.grid(row = 1)

    def create_check_boxes(self, all_keys):
        self.checkboxesFrame = ttk.Frame(self.visualizationfiltersFrame)
        self.checkboxesFrame.grid(row = 2)

        # it's a dict where the keys are the columns and the values are 1 if this box was selected and 0 otherwise
        self.view_filters_boxes_variables = {}

        self.check_boxes = []
        for i, key in enumerate(all_keys):
            # self.check_boxes_labels.append(ttk.Label(self.visualizationfiltersFrame, text = key, style = 'Tiny.TLabelL'))
            # self.check_boxes_labels[i].grid(row = 2, column = i, pady = 20)

            self.view_filters_boxes_variables[key] = tk.IntVar()
            self.check_boxes.append(ttk.Checkbutton(self.checkboxesFrame, variable = self.view_filters_boxes_variables[key], text = key.capitalize()))
            self.check_boxes[i].grid(row = 0, column = i, pady = 20, padx = 10)
            self.view_filters_boxes_variables[key].set(1)

    def create_comboboxes(self,key_to_possible_values_dic):
        self.filtersLabel = []

        #Its a list of frames since more than one option can be chosen
        self.filtersComboboxFrames = []

        #Its a list for each metadata, where its content is another list
        self.filtersSelection = []

        for i,key in enumerate(key_to_possible_values_dic.keys()):
            self.filtersLabel.append(ttk.Label(self.selectionfiltersFrame, text = key.capitalize(), justify = tk.RIGHT))
            self.filtersLabel[i].grid(row=i, column=0, sticky = tk.E, padx = 10)
            self.filtersComboboxFrames.append(ttk.Frame(self.selectionfiltersFrame))
            self.filtersComboboxFrames[i].grid(row = i, column = 1, pady = 2, sticky = tk.W)
            if self.is_date(key_to_possible_values_dic[key][0]):
                self.create_date_combobox(parent = self.filtersComboboxFrames[i],width = 15,font = self.verytiny_font,justify = 'right', state = 'readonly', values = list(key_to_possible_values_dic[key]))
            else:
                self.create_combobox(parent = self.filtersComboboxFrames[i],width = 15,font = self.verytiny_font,justify = 'right', state = 'readonly', values = list(key_to_possible_values_dic[key]))
            # self.filtersComboboxFrames[i].bind('<Button-1>',self.combo_configure)
            # self.filtersComboboxFrames[i].grid(row=i, column=1, sticky=tk.E)

    def create_date_combobox(self, parent, width, font, justify, state, values):
        toLabel = ttk.Label(parent, text = 'até',  justify = tk.RIGHT)

        fromCombobox = ttk.Combobox(parent,width = width, font = font, justify = justify, state = state, values = values)
        fromCombobox.bind('<Button-1>',self.combo_configure)
        fromCombobox.bind('<<ComboboxSelected>>', self.update_to_combobox)

        toCombobox = ttk.Combobox(parent,width = width, font = font, justify = justify, state = state, values = values)
        toCombobox.bind('<Button-1>',self.combo_configure)


        fromCombobox.grid(row = 0, column = 0, padx = 10)
        toLabel.grid(row = 0, column = 1, padx = 10)
        toCombobox.grid(row = 0, column = 2, padx = 10)

    #make toCombobox just show dates that are after the one selected in the first combobox
    def update_to_combobox(self,event):
        combo = event.widget

        parent = combo.nametowidget(combo.winfo_parent())
        column = len(parent.grid_slaves(row = 0)) - 1
        toCombobox = parent.grid_slaves(row = 0, column = column)[0]
        currentValues = combo.cget('values')

        toCombobox.configure(values = [value for value in currentValues if parse(value) > parse(currentValues[combo.current()])])

    def create_combobox(self, parent, width, font, justify, state, values):
        #add a empty option
        add_empty_values = values.copy()
        if '' not in add_empty_values:
            add_empty_values.insert(0,'')
        newCombobox = ttk.Combobox(parent,width = width, font = font, justify = justify, state = state, values = add_empty_values)
        newCombobox.bind('<Button-1>',self.combo_configure)
        column = len(parent.grid_slaves(row = 0))
        newCombobox.grid(row = 0, column = column, padx = 10,sticky = tk.E)

        #create button to add one more filter option
        add_button = ttk.Button(parent, text = '+', width = SMALL_BUTTON_WIDTH)
        add_button.bind('<Button-1>',self.create_combobox_button)
        add_button.grid(row = 0, column = column + 1, padx = 10)

        #create delete filter option button if its not the first filter
        if (column > 0):
            delete_button = ttk.Button(parent, text = '-', width = SMALL_BUTTON_WIDTH)
            delete_button.bind('<Button-1>',self.delete_combobox_button)
            delete_button.grid(row = 0, column = column + 2)

    #add one more combobox when the button is clicked
    def create_combobox_button(self,event):
        button = event.widget
        parent = button.nametowidget(button.winfo_parent())
        if len(parent.grid_slaves(row = 0)) > 2:
            #there is a delete button already, so it has to be deleted before creating another one
            last_box_column = len(parent.grid_slaves(row = 0)) - 3
            delete_button_column  = len(parent.grid_slaves(row = 0)) - 1
            delete_button = (parent.grid_slaves(row = 0, column = delete_button_column))[0]
            delete_button.destroy()
        else:
            last_box_column = len(parent.grid_slaves(row = 0)) - 2
        last_box = (parent.grid_slaves(row = 0, column = last_box_column))[0]
        font = last_box.cget('font')
        width = last_box.cget('width')
        justify = last_box.cget('justify')
        state = last_box.cget('state')
        values = list(last_box.cget('values'))

        button.destroy()
        self.create_combobox(parent, width = width, font = font, justify = justify, state = state, values = values)

    def delete_combobox_button(self, event):
        button = event.widget
        parent = button.nametowidget(button.winfo_parent())
        last_box_column = len(parent.grid_slaves(row = 0)) - 3
        last_box = (parent.grid_slaves(row = 0, column = last_box_column))[0]
        if last_box_column == 1:
            button.destroy()
        last_box.destroy()

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

    # return a dict where the keys are the metadata name and the items are the filters selection for that metadata
    def get_filters(self):
        filters_dict = {}
        for i,label in enumerate(self.filtersLabel):
            filters_dict[label.cget('text')] = []
            combo_frame = self.filtersComboboxFrames[i]
            for object in combo_frame.grid_slaves(row = 0):
                if isinstance(object,ttk.Combobox):
                    if (object.current() == -1):
                        filters_dict[label.cget('text')].append('')
                    else:
                        filters_dict[label.cget('text')].append(object.cget('values')[object.current()])
        return filters_dict

    def get_selected_keys(self):
        selected_keys = []
        for key, value in self.view_filters_boxes_variables.items():
            if value.get() == 1:
                selected_keys.append(key)

        return selected_keys

class QueryView(View):
    def __init__(self, parent, notebook, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.notebook = notebook
        #set components style
        self.style = ttk.Style()
        self.background = 'white'
        self.std_font = ('Helvetica',12)
        self.button_font = ('Helvetica',10)
        self.verytiny_font = ('Helvetica',8)
        self.style.configure("TButton",background=self.background, font = self.button_font)
        self.style.configure("Close.TButton",background=self.background, font=('Helvetica',10,'bold'))
        self.style.configure("Download.TButton",background=self.background,size=(12,12))
        self.style.configure("TFrame",background=self.background)
        self.style.configure("Red.TFrame",background='red')
        self.style.configure("TLabel",background=self.background,font=self.std_font)
        self.style.configure("NumberofFiles.TLabel",background=self.background,font=('Helvetica',10,'bold'))
        self.style.configure("Tiny.TLabel",background=self.background,font=('Helvetica',10))
        self.style.configure("Subtitle.TLabel",background=self.background,font=('Helvetica',15,'bold'))
        self.style.configure("Header.TLabel",background=self.background,font=('Helvetica',20,'bold'))
        self.style.configure('TCombobox',background=self.background, font=('Helvetica',5))
        self.option_add("*TCombobox*Listbox*Font", self.verytiny_font)
        self.pack(fill='both', expand=True, anchor = 'center')
        self.columnconfigure(0,weight = 1)

        # List of frames inside the tabs
        self.tab_frames_list = []

    def create_view(self, data):
        '''
        Creates a new scrollable tab on the notebook

        Inputs:
        data: pandas dataFrame
        '''

        # Create frame inside the notebook
        helper_frame = ttk.Frame(self.notebook)
        helper_frame.pack(fill='both', expand=True, anchor = 'center')
        self.notebook.add(helper_frame, text = f'Consulta {len(self.tab_frames_list)}')

        # Now creates a scrollable frame
        scrollFrame = ScrollFrame(helper_frame)
        scrollFrame.pack(side='top',fill='both',expand=True)
        scrollFrame.viewPort.columnconfigure(0, weight = 1)

        # The actual usable frame is the viewPort
        self.tab_frames_list.append(scrollFrame.viewPort)

        # The index doesn't have to subtract 1 because the first tab is the main tab
        self.notebook.select(len(self.tab_frames_list))
        csv_button, json_button = self.generate_query_result_page(self.tab_frames_list[len(self.tab_frames_list) - 1], len(self.tab_frames_list)-1, data)

        return scrollFrame.viewPort, csv_button, json_button

    def generate_query_result_page(self, parent, index, data):
        # Close tab button
        df = data
        close_button_frame = ttk.Frame(parent, width = 2)
        close_button_frame.pack(side='top',fill='both',expand=True)
        close_button = ttk.Button(close_button_frame, text = 'X', style = 'Close.TButton')
        close_button.pack(side='right')
        close_button.bind('<Button-1>', lambda event: self.notebook.hide('current'))

        main_frame = ttk.Frame(parent)
        main_frame.pack(side='top',fill='both',expand=True)
        main_frame.columnconfigure(0, weight = 1)

        header = ttk.Label(main_frame, style = "Header.TLabel", text = 'Resultado da consulta')
        header.grid(row = 0, pady = 20)

        # Show a sample of the data
        table_frame = ttk.LabelFrame(main_frame, text='Exibindo as 300 primeiras linhas',  width = 1500, height = 500)
        table_frame.grid(row = 1, padx = 20)
        table_frame.grid_propagate(0)

        # Create a TreeView, that is going to show the sample of the data
        tv1 = ttk.Treeview(table_frame, height = 20)
        tv1.pack(fill='both')
        treescrollx = tk.Scrollbar(table_frame, orient='horizontal', command = tv1.xview)
        treescrolly = tk.Scrollbar(table_frame, orient='vertical', command = tv1.yview)
        tv1.configure(xscrollcommand=treescrollx.set, yscrollcommand=treescrolly.set)
        treescrolly.place(relx=0.99, rely=0.045, relheight=0.93, relwidth=0.010)
        treescrollx.pack(side='bottom',fill='x')

        # Put the data into the treeview
        tv1['column'] = list(df.columns)
        tv1['show'] = 'headings'
        for column in tv1['columns']:
            tv1.heading(column,text=column)

        if df.shape[0].compute() < 300:
            df_rows = data.compute().to_numpy().tolist()
        else:
            df_rows = data.head(300).to_numpy().tolist()

        for row in df_rows:
            tv1.insert('','end',values=row)


        # Info label
        n_rows = df.shape[0].compute()
        n_columns = df.shape[1]
        info_label = ttk.Label(main_frame, text = f'Há {n_rows} documentos nesta consulta e o número de atributos selecionados é {n_columns}.')
        info_label.grid(row = 2, pady = 10)

        # Buttons
        buttons_frame = ttk.Frame(main_frame)
        buttons_frame.grid(row = 3, pady = 10)

        csv_button = ttk.Button(buttons_frame, text = 'Exportar para CSV')
        csv_button.grid(row = 0, column = 0, padx = 10)

        json_button = ttk.Button(buttons_frame, text = 'Exportar para JSON')
        json_button.grid(row = 0, column = 1, padx = 10)

        return csv_button, json_button
    # def generate_query_result_page(self, parent, index, data):
    #     # Close tab button
    #     df = data
    #     close_button_frame = ttk.Frame(parent, width = 2)
    #     close_button_frame.pack(side='top',fill='both',expand=True)
    #     close_button = ttk.Button(close_button_frame, text = 'X', style = 'Close.TButton')
    #     close_button.pack(side='right')
    #     close_button.bind('<Button-1>', lambda event: self.notebook.hide('current'))
    #
    #     main_frame = ttk.Frame(parent)
    #     main_frame.pack(side='top',fill='both',expand=True)
    #     main_frame.columnconfigure(0, weight = 1)
    #
    #     header = ttk.Label(main_frame, style = "Header.TLabel", text = 'Resultado da consulta')
    #     header.grid(row = 0, pady = 20)
    #
    #     # Show a sample of the data
    #     table_frame = ttk.Frame(main_frame, width = 1500, height = 500)
    #     table_frame.grid(row = 1, padx = 20)
    #     table_frame.grid_propagate(0)
    #     table = pdt.Table(table_frame, showtoolbar = False, showstatusbar = False, width = 500)
    #     table.model.df = df
    #     options = {'align': 'w',
    #              'cellbackgr': 'white',
    #              'cellwidth': 80,
    #              'colheadercolor': 'gray',
    #              'floatprecision': 2,
    #              'font': 'Helvetica',
    #              'fontsize': 10,
    #              'fontstyle': '',
    #              'grid_color': '#ABB1AD',
    #              'linewidth': 1,
    #              'rowheight': 22,
    #              'rowselectedcolor': '#E4DED4',
    #              'textcolor': 'black'}
    #     pdt.config.apply_options(options,table)
    #     table.show()
    #     # txt = tk.Text(main_frame, width = TEXT_WIDGET_WIDTH, height = 15, wrap=tk.NONE)
    #     # txt.tag_config('center', justify = tk.CENTER, wrap = None)
    #     # txt.grid(row = 1)
    #     # txt.insert(tk.END,str(df.head(20)),'center')
    #     # # Read only
    #     # txt.config(state=tk.DISABLED)
    #
    #     # Info label
    #     n_rows = df.shape[0]
    #     n_columns = df.shape[1]
    #     info_label = ttk.Label(main_frame, text = f'Há {n_rows} documentos nesta consulta e o número de atributos selecionados é {n_columns}.')
    #     info_label.grid(row = 2, pady = 10)
    #
    #     # Buttons
    #     buttons_frame = ttk.Frame(main_frame)
    #     buttons_frame.grid(row = 3, pady = 10)
    #
    #     csv_button = ttk.Button(buttons_frame, text = 'Exportar para CSV')
    #     csv_button.grid(row = 0, column = 0, padx = 10)
    #
    #     json_button = ttk.Button(buttons_frame, text = 'Exportar para JSON')
    #     json_button.grid(row = 0, column = 1, padx = 10)
    #
    #     return csv_button, json_button

# Define a custom PDF class so some methods can be overwritten
class PDF(FPDF):
    def header(self):
        self.set_font('helvetica','B',20)

        self.cell(0,10, 'Veritas', border = True, ln = True, align = 'C')
        self.ln(10)

    def footer(self):
        self.set_y(-10)
        self.set_font('helvetica','I',10)
        self.cell(0,10,f'Página {self.page_no()}/{{nb}}', align = 'C')

class StatisticsOptionsView(View):
    def __init__(self, parent, notebook, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.notebook = notebook
        self.style = ttk.Style()
        self.background = 'white'
        self.std_font = ('Helvetica',12)
        self.button_font = ('Helvetica',10)
        self.verytiny_font = ('Helvetica',8)
        self.style.configure("TButton",background=self.background, font = self.button_font)
        self.style.configure("Bold.TButton",background=self.background, font = ('Helvetica',15,'bold'))
        self.style.configure("TFrame",background=self.background)
        self.style.configure("TLabel",background=self.background,font=self.std_font)
        self.style.configure("Small.TLabel",background=self.background,font=('Helvetica',8,'italic'))
        self.style.configure("Subtitle.TLabel",background=self.background,font=('Helvetica',15,'bold'))
        self.style.configure("Header.TLabel",background=self.background,font=('Helvetica',20,'bold'))
        self.style.configure('TCheckbutton', background=self.background)
        self.option_add("*TCombobox*Listbox*Font", self.verytiny_font)
        self.pack(fill='both', expand=True, anchor = 'center')
        self.columnconfigure(0,weight = 1)
        self.frame_height = self.parent.winfo_height()

        # List with the label of each statistics option
        self.options_label_list = []

        # List with the control variable for each of the statistics options checkboxes
        self.checkboxes_variable_list = []

        # Frame where the statistics are gonna be showed
        self.statisticsResultsFrame = None

    def create_view(self):
        self.headerFrame = ttk.Frame(self)
        self.headerFrame.grid(row = 0, column = 0)

        self.headerLabel = ttk.Label(self.headerFrame, text = 'Gerar estatísticas', style = "Subtitle.TLabel")
        self.headerLabel.grid(row = 0, column = 0, pady = 20)

        self.statisticsOptionsFrame = ttk.Frame(self)
        self.statisticsOptionsFrame.grid(row = 1, column = 0)

    def set_filters(self, filters_dict, view_filters_list):
        self.filters_dict = filters_dict
        self.view_filters_list = view_filters_list

    # Return the filters that were set for this options tab
    def get_filters(self):
        return self.filters_dict, self.view_filters_list

    # Create the query options based on the parameter models_view_dict, if no view frame is given then just the standard
    # checkbox with the model's name will be created
    def create_statistics_options(self, models_view_dict, models_descriptions, data):
        models_view_dict_tmp = models_view_dict.copy()
        for i,(model_name, view_component) in enumerate(models_view_dict_tmp.items()):
            # Help button
            def handler(self=self,model_name = model_name, description = models_descriptions[model_name]):
                return self.show_help_window(description,model_name)
            help_button = ttk.Button(self.statisticsOptionsFrame, text = '?', command = handler, width = SMALL_BUTTON_WIDTH, style='Bold.TButton')
            help_button.grid(row = i, column = 0)

            # Label
            self.options_label_list.append(ttk.Label(self.statisticsOptionsFrame, text = model_name))
            self.options_label_list[i].grid(row = i, column = 1, padx = 10)

            # Checkbox
            self.checkboxes_variable_list.append(tk.IntVar())
            check_box = ttk.Checkbutton(self.statisticsOptionsFrame, variable = self.checkboxes_variable_list[i])
            check_box.grid(row = i, column = 2)

            # individual view frame
            if view_component != None:
                # Create another frame for the view component
                tmp_frame = ttk.Frame(self.statisticsOptionsFrame)
                #place it next to the checkbox
                tmp_frame.grid(row = i, column = 3, padx = 10)
                models_view_dict_tmp[model_name] = view_component(tmp_frame)
                models_view_dict_tmp[model_name].create_view(data)

        #Create query button, the command is binded by the controller
        self.statistics_button = ttk.Button(self, text = 'Gerar estatísticas')
        self.statistics_button.grid(row = 2, column = 0, pady = 20)

        return models_view_dict_tmp
    def show_help_window(self, model_description, model_name):
        tk.messagebox.showinfo(model_name, model_description)

    def get_selected_models(self):
        selected_models_name = []
        for i, variable in enumerate(self.checkboxes_variable_list):
            if variable.get() == 1:
                selected_models_name.append(self.options_label_list[i].cget('text'))
        return selected_models_name

    def start_progress_window(self):
        #tk.messagebox.showinfo('oi','oi')
        self.popup = tk.Toplevel()

        self.popup_label = ttk.Label(self.popup, text = 'Por favor aguarde, as estatísticas estão sendo geradas.')
        self.popup_label.grid(row=0, column=0, pady=10)

        self.progress_bar = ttk.Progressbar(self.popup, orient='horizontal', mode='indeterminate')
        self.progress_bar.grid(row=1,column=0,pady=10)
        self.progress_bar.start()

    def finish_progress_window(self):

        self.popup_label.config(text='Estatísticas geradas com sucesso!')

        self.progress_bar.stop()
        self.progress_bar.grid_forget()

        self.close_popup_button = ttk.Button(self.popup, text = 'OK', command=self.popup.withdraw)
        self.close_popup_button.grid(row=1,column=0,pady=10)
    def generate_output(self, output_dict):
        '''
        Generates the output of the models on the screen

        Inputs:
        output_dict: A dictionary, where the key is the name of the model and the items are its content:
        a list of strings, images or a pandas DataFrame
        '''
        final_output = []
        # Header
        header_label = ttk.Label(self, text = 'Estatísticas:', style = "Subtitle.TLabel")
        header_label.grid(row = 3, column = 0, pady =  20)

        # Frame for the results
        if self.statisticsResultsFrame != None:
            # there are results being shown already
            self.statisticsResultsFrame.grid_forget()
            self.statisticsResultsFrame.destroy()
        self.statisticsResultsFrame = ttk.Frame(self)
        self.statisticsResultsFrame.grid(row = 3, column = 0)

        # Generates a frame and a text widget for each model result
        for i,(model_name, model_output) in enumerate(output_dict.items()):
            # At first the model wont have the option to export the content to csv
            export_to_csv = False
            df_list = []

            frame = ttk.Frame(self.statisticsResultsFrame)
            frame.grid(row = i, pady = 20)

            # Label for the model's name
            label = ttk.Label(frame, text = model_name + ':')
            label.grid(row = 0)

            # Result box

            # Attempt to make a responsive text widget height
            # fonte = font.Font(family='Helvetica', size=12)
            # font_height = fonte.metrics('linespace')
            # frame_height = SCREEN_HEIGHT
            # height = frame_height/font_height
            # print(f'font_height: {font_height}, frame_height: {frame_height}, height:{height}')

            text_box = tk.Text(frame, width = TEXT_WIDGET_WIDTH, height = TEXT_WIDGET_HEIGHT)
            text_box.tag_config('left', justify = tk.LEFT, wrap = None)
            text_box.tag_config('center', justify = tk.CENTER, wrap = None)
            text_box.grid(row = 1, column = 0)
            # Add scrollbar
            scrollbar = ttk.Scrollbar(frame, command = text_box.yview)
            scrollbar.grid(row = 1, column = 1, sticky = 'nsew')
            text_box.config(yscrollcommand = scrollbar.set)
            for line in model_output:
                if isinstance(line, pd.DataFrame):
                    export_to_csv = True
                    df_list.append(line)
                    # Also convert it to string and insert it's first 5 columms as a text
                    all_columns = line.columns
                    all_columns_str = str(list(all_columns))
                    if len(all_columns) > 5:
                        text_box.insert(tk.END,f'Há um total de {len(all_columns)} colunas:\n\n','left')
                        text_box.insert(tk.END,all_columns_str,'left')
                        text_box.insert(tk.END,f'\n\nMas só as 5 primeiras são mostradas abaixo, exporte para CSV para obter todas:\n\n','left')
                    # MAYBE THE LINE VARIABLE WONT BE MODIFIED AND WILL OCCUR AN ERROR WHEN GENERATING THE PDF
                    line = line.T.head(5).T.to_string(justify='center',max_colwidth = 30)
                    text_box.insert(tk.END,line,'left')
                elif isinstance(line,str):
                    if line.endswith('.png') or line.endswith('.jpeg'):
                        # It's a image path
                        global my_image
                        my_image = tk.PhotoImage(file = line)
                        text_box.image_create(tk.END, image = my_image)
                        # resize so the image can be seen
                        #height = height + 10
                        #text_box.config(height = height)

                        # download image button
                        text_box.insert(tk.END,'\n')
                        def download_handler(self=self, image = my_image, image_path = line):
                            return self.download_image(image,image_path)
                        text_box.window_create(tk.END, window = ttk.Button(text_box, text = 'Baixar imagem',command = download_handler))
                        # Centralize button and image
                        text_box.tag_add('center','end-1l linestart','end')
                    else:
                        # It's just text
                        text_box.insert(tk.END,line,'left')
                else:
                    raise TypeError('Models output list must contain only strings (Text), path to png/jpeg image or pandas DataFrames')
                text_box.insert(tk.END,'\n','left')

            # Read only
            text_box.config(state=tk.DISABLED)

            number_buttons = 0

            # Export to PDF button
            # Create frame the button(s)
            buttons_frame = ttk.Frame(frame)
            buttons_frame.grid(row = 2, column = 0, pady = 10)
            export_pdf_button = ttk.Button(buttons_frame, text = 'Exportar para PDF')
            export_pdf_button.grid(row = 0, column = number_buttons)
            def handler(event, self=self, output = (model_name, model_output)):
                return self.generate_pdf(event,output)
            export_pdf_button.bind("<Button-1>", handler)
            number_buttons += 1

            # Export to CSV and JSON button
            if export_to_csv:
                export_csv_button = ttk.Button(buttons_frame, text = 'Exportar tabela(s) de dado(s) para CSV')
                export_csv_button.grid(row = 0, column = number_buttons, padx = 10)
                def handler(event, self=self, model_name_df_list = (model_name, df_list)):
                    return self.generate_csvs(event,model_name_df_list)
                export_csv_button.bind("<Button-1>", handler)
                number_buttons += 1

                export_json_button = ttk.Button(buttons_frame, text = 'Exportar tabela(s) de dado(s) para JSON')
                export_json_button.grid(row = 0, column = number_buttons, padx = 10)
                def handler(event, self=self, model_name_df_list = (model_name, df_list)):
                    return self.generate_jsons(event,model_name_df_list)
                export_json_button.bind("<Button-1>", handler)
                number_buttons += 1

            # Help button
            def handler(self=self,number_buttons = number_buttons):
                pdf_and_json = number_buttons > 1
                return self.show_button_help(pdf_and_json)
            help_button = ttk.Button(buttons_frame, text = '?',width = SMALL_BUTTON_WIDTH, command = handler, style='Bold.TButton')
            help_button.grid(row = 0, column = number_buttons, padx=30)

    def show_button_help(self, pdf_and_json):
        description = 'Exportar para PDF: exporta exatamente o que está mostrado acima para PDF.\n(caso alguma coluna de uma tabela de dados tenha sido omitida acima, ela também estará omitida no PDF)\n\n'
        if pdf_and_json:
            description += 'Exportar para CSV: exporta a(s) tabela(s) de dados completa(s) para CSV, caso algumas colunas não tenham sido mostradas acima, elas estarão no CSV.\n(caso exista mais de uma tabela, será gerado um arquivo para cada)\n\n '
            description += 'Exporta a(s) tabela(s) de dados completa(s) para JSON, o arquivo JSON pode ser utilizado para gerar uma outra consulta sobre estes novos dados.\n(caso exista mais de uma tabela, será gerado um arquivo para cada)'
        tk.messagebox.showinfo('O que faz cada botão?', description)
    def generate_jsons(self,event,model_name_df_list):
        model_name = model_name_df_list[0]
        df_list = model_name_df_list[1]
        save_directory = tk.filedialog.askdirectory(mustexist = True, title = 'Selecione o diretório em que deseja salvar o(s) arquivo(s) JSON(s)')
        if not save_directory == '':
            for (i,df) in enumerate(df_list):
                df.to_json(save_directory + '/veritas_'+ model_name + str(i) + '.json')

    def generate_csvs(self,event,model_name_df_list):
        model_name = model_name_df_list[0]
        df_list = model_name_df_list[1]
        save_directory = tk.filedialog.askdirectory(mustexist = True, title = 'Selecione o diretório em que deseja salvar o(s) arquivo(s) CSV(s)')
        if not save_directory == '':
            for (i,df) in enumerate(df_list):
                df.to_csv(save_directory + '/veritas_'+ model_name + str(i) + '.csv', encoding='utf-8')

    def download_image(self,image,image_path):
        #save_directory = tk.filedialog.askdirectory(mustexist = True, title = 'Selecione o diretório em que deseja salvar a imagem')
        file_name = (image_path.split('/'))[-1]
        f = tk.filedialog.asksaveasfile(mode='w', defaultextension=".png", initialfile=file_name, title='Salvar como')
        if not f.name == '':
            image.write(f.name)
        else:
            return

    def generate_pdf(self, event, output):
        model_name = output[0]
        model_output = output[1]
        pdf = PDF('P','mm', 'A4')
        pdf.alias_nb_pages()
        pdf.set_auto_page_break(auto=True, margin = 15)
        pdf.add_page()


        # Set header
        pdf.set_font('helvetica','B',18)
        pdf.cell(0,10, model_name, ln = True, align = 'C')
        pdf.ln(10)

        # Set content font
        pdf.set_font('helvetica','',10)
        for printable in model_output:
            if isinstance(printable,pd.DataFrame):
                printable = printable.T.head(5).T.to_string(justify='right',max_colwidth = 30)
            if isinstance(printable,str):
                if printable.endswith('.png') or printable.endswith('.jpeg'):
                    # It's a png image
                    pdf.image(printable, x = -0.5, w = pdf.w+1)
                else:
                    printable = printable.encode('latin-1', 'replace').decode('latin-1')
                    pdf.multi_cell(0,6,printable, ln = True, align='L')
            else:
                raise TypeError('Models output list must contain only strings (Text) or path to png/jpeg image')

        file_name = 'veritas_'+model_name
        f = tk.filedialog.asksaveasfile(mode='w', defaultextension=".pdf", initialfile=file_name, title='Salvar como')
        if not f.name == '':
            pdf.output(f.name)
        else:
            return

class CountDocumentsView(ComponentView):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.selection_list = []
        self.bar_select_variable = tk.IntVar()
        self.bar_n_variable = tk.StringVar()
        self.pie_select_variable = tk.IntVar()
        self.pie_n_variable = tk.StringVar()

    def create_view(self, data):

        # Category selection frame
        self.category_selec_frame = ttk.Frame(self.parent)
        self.category_selec_frame.grid(row = 0, column = 0, sticky = tk.W)

        self.label = ttk.Label(self.category_selec_frame, text = 'Contar por:', style = 'Std.TLabel')
        self.label.grid(row = 0, column = 0)

        # frame for the comboboxes
        self.combobox_frame = ttk.Frame(self.category_selec_frame)
        self.combobox_frame.grid(row = 0, column = 1, padx = 10)
        self.selection_list = []
        self.create_combobox(self.combobox_frame, width = 10, font = self.verytiny_font,justify = 'right', state = 'readonly', values = list(data.columns))

        # bar options
        self.his_frame = ttk.Frame(self.parent)
        self.his_frame.grid(row = 1, column = 0, pady = 5, sticky = tk.W)

        self.his_label = ttk.Label(self.his_frame, text = 'Gerar gráfico de barras', style = 'Std.TLabel')
        self.his_label.grid(row = 0, column = 0)

        self.bar_checkbox = ttk.Checkbutton(self.his_frame, variable = self.bar_select_variable, command = self.show_hide_bar_options)
        self.bar_select_variable.set(0)
        self.bar_checkbox.grid(row = 0, column = 1, padx = 10, sticky = tk.E)

        self.bar_options_frame = ttk.Frame(self.his_frame)
        self.bar_options_frame.grid(row = 0, column = 2)
        self.bar_options_label1 = ttk.Label(self.bar_options_frame, text = '- Considerar as ', style = 'Std.TLabel')
        self.bar_options_label1.grid(row = 0, column = 0)
        self.bar_n_variable.set('')
        self.bar_options_entry = ttk.Entry(self.bar_options_frame, textvariable = self.bar_n_variable, width = 4)
        self.bar_options_entry.grid(row = 0, column = 1)
        self.bar_options_label2 = ttk.Label(self.bar_options_frame, text = ' aparições mais frequentes. ', style = 'Std.TLabel')
        self.bar_options_label2.grid(row = 0, column = 2)

        # hide frame so its shown only when the user selects the checkbox
        self.bar_options_frame.grid_remove()

        # pie chart options
        self.pie_frame = ttk.Frame(self.parent)
        self.pie_frame.grid(row = 2, column = 0, pady = 5, sticky = tk.W)

        self.pie_label = ttk.Label(self.pie_frame, text = 'Gerar gráfico de pizza', style = 'Std.TLabel')
        self.pie_label.grid(row = 0, column = 0)

        self.pie_checkbox = ttk.Checkbutton(self.pie_frame, variable = self.pie_select_variable)
        self.pie_select_variable.set(0)
        self.pie_checkbox.grid(row = 0, column = 1, padx = 10, sticky = tk.E)

    def show_hide_bar_options(self):
        if self.bar_select_variable.get() == 1:
            self.bar_options_frame.grid()
        else:
            self.bar_options_frame.grid_remove()

    def get_extra_input(self):
        extra_input = {}
        extra_input['selected_categories'] = [x.get() for x in self.selection_list]
        extra_input['bar_selected'] = self.bar_select_variable.get()

        # Handle missing n entry
        # Bar graph
        if (extra_input['bar_selected'] == 1 and self.bar_n_variable.get() == ''):
            tk.messagebox.showerror('Erro', 'Digite quantas aparições mais frequentes você deseja que tenha no gráfico de barras.')
            # Won't show the plot
            extra_input['bar_selected'] = 0
        elif extra_input['bar_selected'] == 1:
            extra_input['bar_n'] = int(self.bar_n_variable.get())
        else:
            # bar graph wasnt selected
            extra_input['bar_n'] = 0
        # Pie chart
        extra_input['pie_selected'] = self.pie_select_variable.get()

        return extra_input

    def create_combobox(self, parent, width, font, justify, state, values):
        #add a empty option
        add_empty_values = values.copy()
        if '' not in add_empty_values:
            add_empty_values.insert(0,'')
        # create a variable to hold the selected value
        var = tk.StringVar()
        self.selection_list.append(var)
        newCombobox = ttk.Combobox(parent,textvariable = var, width = width, font = font, justify = justify, state = state, values = add_empty_values)
        newCombobox.bind('<Button-1>',self.combo_configure)
        column = len(parent.grid_slaves(row = 0))
        newCombobox.grid(row = 0, column = column, padx = 10,sticky = tk.E)

        #create button to add one more filter option
        add_button = ttk.Button(parent, text = '+', width = SMALL_BUTTON_WIDTH)
        add_button.bind('<Button-1>',self.create_combobox_button)
        add_button.grid(row = 0, column = column + 1, padx = 10)

        #create delete filter option button if its not the first filter
        if (column > 0):
            delete_button = ttk.Button(parent, text = '-', width = SMALL_BUTTON_WIDTH)
            delete_button.bind('<Button-1>',self.delete_combobox_button)
            delete_button.grid(row = 0, column = column + 2)

    #add one more combobox when the button is clicked
    def create_combobox_button(self,event):
        button = event.widget
        parent = button.nametowidget(button.winfo_parent())
        if len(parent.grid_slaves(row = 0)) > 2:
            #there is a delete button already, so it has to be deleted before creating another one
            last_box_column = len(parent.grid_slaves(row = 0)) - 3
            delete_button_column  = len(parent.grid_slaves(row = 0)) - 1
            delete_button = (parent.grid_slaves(row = 0, column = delete_button_column))[0]
            delete_button.destroy()
        else:
            last_box_column = len(parent.grid_slaves(row = 0)) - 2
        last_box = (parent.grid_slaves(row = 0, column = last_box_column))[0]
        font = last_box.cget('font')
        width = last_box.cget('width')
        justify = last_box.cget('justify')
        state = last_box.cget('state')
        values = list(last_box.cget('values'))

        button.destroy()
        self.create_combobox(parent, width = width, font = font, justify = justify, state = state, values = values)

    def delete_combobox_button(self, event):
        button = event.widget
        parent = button.nametowidget(button.winfo_parent())
        last_box_column = len(parent.grid_slaves(row = 0)) - 3
        last_box = (parent.grid_slaves(row = 0, column = last_box_column))[0]
        if last_box_column == 1:
            button.destroy()
        last_box.destroy()
        del self.selection_list[-1]

    #Configure combobox so its size adapts to its values
    def combo_configure(self,event):
        combo = event.widget
        style = ttk.Style()

        max_string = max(combo.cget('values'), key=len)
        font = combo.cget('font')
        width = tk.font.Font(font = font).measure(max_string + '0000' ) - combo.winfo_width()

        style.configure('TCombobox', postoffset=(0,0,width,0))
        combo.configure(style='TCombobox')
