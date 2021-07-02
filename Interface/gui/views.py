from abc import ABC, abstractmethod
import os
import tkinter as tk
from tkinter import ttk as ttk
from tkinter import filedialog, font
from fpdf import FPDF
from dateutil.parser import parse
from gui.util.helper_classes import ScrollFrame


class View(ttk.Frame):
    @abstractmethod
    def create_view():
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

    def create_filter(self,parent):
        self.headerFrame = ttk.Frame(parent)
        self.headerFrame.grid(row = 0)

        self.selectionfiltersFrame = ttk.Frame(parent)
        self.selectionfiltersFrame.grid(row = 1 , pady = 20)

        self.visualizationfiltersFrame = ttk.Frame(parent)
        self.visualizationfiltersFrame.grid(row = 2, pady = 20)

        self.generatequeryButton = ttk.Button(parent, text = 'Gerar consulta')
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
            self.check_boxes.append(ttk.Checkbutton(self.checkboxesFrame, variable = self.view_filters_boxes_variables[key], text = key))
            self.check_boxes[i].grid(row = 0, column = i, pady = 20, padx = 10)
            self.view_filters_boxes_variables[key].set(1)

    def create_comboboxes(self,key_to_possible_values_dic):
        self.filtersLabel = []

        #Its a list of frames since more than one option can be chosen
        self.filtersComboboxFrames = []

        #Its a list for each metadata, where its content is another list
        self.filtersSelection = []

        for i,key in enumerate(key_to_possible_values_dic.keys()):
            self.filtersLabel.append(ttk.Label(self.selectionfiltersFrame, text = key, justify = tk.RIGHT))
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
        add_button = ttk.Button(parent, text = '+')
        add_button.bind('<Button-1>',self.create_combobox_button)
        add_button.grid(row = 0, column = column + 1, padx = 10)

        #create delete filter option button if its not the first filter
        if (column > 0):
            delete_button = ttk.Button(parent, text = '-')
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

        # List of frames inside the tabs
        self.tab_frames_list = []

    def create_view(self, filters_dict, view_filters_list):
        '''
        Creates a new scrollable tab on the notebook
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
        self.generate_query_result_page(self.tab_frames_list[len(self.tab_frames_list) - 1], len(self.tab_frames_list), filters_dict, view_filters_list)

        return scrollFrame.viewPort

    def generate_query_result_page(self, parent, index, filters_dict, view_filters_list):
        main_frame = ttk.Frame(parent)
        main_frame.pack(side='top',fill='both',expand=True)
        main_frame.columnconfigure(0, weight = 1)
        self.label = ttk.Label(main_frame, text = 'oi')
        self.label.grid()

# Define a custom PDF class so some methods can be overwritten
class PDF(FPDF):
    def header(self):
        self.set_font('helvetica','B',20)

        self.cell(0,10, 'Veritas: resultado da consulta', border = True, ln = True, align = 'C')
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
        self.style.configure("TFrame",background=self.background)
        self.style.configure("TLabel",background=self.background,font=self.std_font)
        self.style.configure("Subtitle.TLabel",background=self.background,font=('Helvetica',15,'bold'))
        self.style.configure("Header.TLabel",background=self.background,font=('Helvetica',20,'bold'))
        self.style.configure('TCheckbutton', background=self.background)
        self.option_add("*TCombobox*Listbox*Font", self.verytiny_font)
        self.pack(fill='both', expand=True, anchor = 'center')
        self.columnconfigure(0,weight = 1)

        # List with the label of each statistics option
        self.options_label_list = []

        # Each statistics option has its own frame, that is stored in this list
        self.options_frame_list = []

        # List with the control variable for each of the statistics options checkboxes
        self.checkboxes_variable_list = []

    def create_view(self):
        self.headerFrame = ttk.Frame(self)
        self.headerFrame.grid(row = 0, column = 0)

        self.headerLabel = ttk.Label(self.headerFrame, text = 'Estatísticas', style = "Subtitle.TLabel")
        self.headerLabel.grid(row = 0, column = 0, pady = 20)

        self.statisticsOptionsFrame = ttk.Frame(self)
        self.statisticsOptionsFrame.grid(row = 1, column = 0, pady =  20)

    def set_filters(self, filters_dict, view_filters_list):
        self.filters_dict = filters_dict
        self.view_filters_list = view_filters_list

    # Return the filters that were set for this options tab
    def get_filters(self):
        return self.filters_dict, self.view_filters_list

    # Create the query options based on the parameter models_view_dict, if no view frame is given then just the standard
    # checkbox with the model's name will be created
    def create_statistics_options(self, models_view_dict):
        for i,(model_name, view_component) in enumerate(models_view_dict.items()):
            self.options_label_list.append(ttk.Label(self.statisticsOptionsFrame, text = model_name))
            self.options_label_list[i].grid(row = i, column = 0, padx = 10)
            self.options_frame_list.append(ttk.Frame(self.statisticsOptionsFrame))
            self.options_frame_list[i].grid(row = i, column = 1)
            self.checkboxes_variable_list.append(tk.IntVar())
            check_box = ttk.Checkbutton(self.options_frame_list[i], variable = self.checkboxes_variable_list[i])
            check_box.grid(row = 0, column = 0)
            if view_component != None:
                # Create another frame for the view component
                tmp_frame = ttk.Frame(self.options_frame_list[i])
                #place it next to the checkbox
                tmp_frame.grid(row = i, column = 1)
                view_component(tmp_frame)
                view_component.create_view()
        #Create query button, the command is binded by the controller
        self.statistics_button = ttk.Button(self.statisticsOptionsFrame, text = 'Gerar estatísticas')
        self.statistics_button.grid(row = i + 1, column = 0, columnspan = 2, pady = 20)

    def get_selected_models(self):
        selected_models_name = []
        for i, variable in enumerate(self.checkboxes_variable_list):
            print(f'i é {i}, variable é {variable}')
            if variable.get() == 1:
                selected_models_name.append(self.options_label_list[i].cget('text'))
        return selected_models_name

    def generate_output(self, output_list):
        final_output = []

        self.generate_pdf(output_list)

    def generate_pdf(self, output_list):
        pdf = PDF('P','mm', 'A4')
        pdf.alias_nb_pages()
        pdf.set_auto_page_break(auto=True, margin = 15)
        pdf.add_page()
        pdf.set_font('helvetica','',10)

        for output in output_list:
            pdf.cell(0,10,output[0]+':', ln = True)
            for printable in output[1]:
                if printable.endswith('.png') or printable.endswith('.jpeg'):
                    # It's a png image
                    pdf.image(printable, x = -0.5, w = pdf.w+1)
                elif isinstance(printable,str):
                    pdf.multi_cell(0,6,printable, ln = True, align='R')
                else:
                    raise TypeError('Models output list must contain only strings (Text) or path to png/jpeg image')

        pdf.output('test.pdf')
