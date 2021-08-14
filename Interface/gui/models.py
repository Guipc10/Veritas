import json,os
import tkinter as tk
from tkinter import ttk as ttk
from abc import ABC, abstractmethod
from dateutil.parser import parse
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import re

# All new modules have to inherit from this class
TEXT_WIDGET_WIDTH = 160
class ComponentModel():
    @abstractmethod
    def get_name():
        '''
        This method returns the name of the model

        Outputs:
        - Model name (Type: str)
        '''
        raise NotImplementedError

    @abstractmethod
    def requires_extra_input():
        '''
        This method tell wheter this model requires an extra input or not

        Outputs:
        - Model's requirement of extra input (Type: bool)
        '''
        raise NotImplementedError

    @abstractmethod
    def get_description():
        '''
        Returns a description of the model to be shown when the user clicks the help button

        Outputs:
        - String describing the model
        '''
        raise NotImplementedError

    @abstractmethod
    def execute(data, extra_input = None):
        '''
        This method executes it's algorithm on the given data

        Inputs:
        - Input data (Type: List of dictionaries)
        Outputs:
        - Model's output list(Type: string or path to png or jpeg image)
        '''
        raise NotImplementedError

class LoadFilesModel():

    def __init__(self):
        #document's path
        self.files_path = tk.StringVar()

        #JSON files in the current directory
        self.json_files = []

        #data that will be analyzed, its a list of list of dictionaries
        self.data_list = []

        #the possible values for each metadata, its a dictionary where each item is a set
        self.key_to_possible_values_dic = {}

        #all the available metadata, aka keys
        self.all_keys = []

    def set_path_variable(self, path_variable):
        self.files_path = path_variable

    def m_process_json(self):
        try:
            self.json_files = [json_file for json_file in os.listdir(self.files_path.get()) if json_file.endswith('.json')]
        except FileNotFoundError:
            Print("Arquivos JSON não encontrados, o diretório indicado pode estar incorreto")

        #I'M APPENDING TWO DIFFERENT TYPES OF JSON FILES HERE, 1 AND 2 DEGREE CASES, MAY CAUSE ERRORS
        df_list = []
        self.data_list.clear()
        for json_file in self.json_files:
            with open(self.files_path.get() +'/'+ json_file,'r') as j:
                df_list.append(pd.DataFrame.from_records(json.load(j)))
        # THIS CONCAT MAY CAUSE ERRORS WHEN USING 2 DIFFERENT TYPES OF DOCUMENTS, LIKE FIRST AND SECOND DEGREE ONES
        self.data = pd.concat(df_list, sort = False)

        # add an author and target column
        self.extract_people()

        self.all_keys = list(self.data.columns)

        #remove useless keys for filtering
        UNIQUE_KEYS = ['ementa', 'processo', 'cdacordao', 'julgado', 'pagina', 'duplicado', 'cd_doc']

        #Get available metadata and it's possible values by iterating over the columns
        self.key_to_possible_values_dic.clear()
        for column in self.data:
            if column not in UNIQUE_KEYS:
                self.key_to_possible_values_dic[column] = np.sort(list(self.data[column].unique()))

        return self.all_keys, self.key_to_possible_values_dic

    def extract_people(self):
        #author_pattern = re.compile(r'\n')
        #author_pattern = re.compile('(.+?)(?=\n)')
        authors = []
        defendants = []
        general_pattern = re.compile(r'(Autor|Autora|Autor e Parte|Requerente|Requerente (s)|Impetrante|Exequente|Exeqüente|Embargante|Demandante|MAGISTRADO|Herdeiro|Inventariante|Inventariante (Ativo)|Inventariante (Ativo)):\s(.+?)(?=(Justiça Gratuita|Juiz|Juíza|Prioridade Idoso|Conclusão|CONCLUSÃO|C O N C L U S Ã O|Réu Preso|Descrição|Vistos|VISTOS|Controle))')
        i = 0
        print_index = 283
        print(str(self.data['julgado'].head(2)))
        for text in self.data['julgado']:
            author = np.nan
            defendant = np.nan
            if i == print_index:
                print(text)
            sentence = general_pattern.search(text)
            if sentence:
                #print('Sentença: ',sentence.group())
                # First get the phrase without the first colon
                remove_first_colon_pattern = re.compile(r'(?<=:\s).*')
                no_first_colon_search = remove_first_colon_pattern.search(sentence.group())
                if i == print_index:
                    print(f'\n\nsentence: ', sentence.group())
                if no_first_colon_search:
                    # Now get the author, which is the text before the word that is before the remaining colon
                    #author_pattern = re.compile(r'(?<=:\s).*(?=\s(\S+):)')
                    if i == print_index:
                        print(f'\n\nno_first_colon_search: ', no_first_colon_search.group())
                    author_pattern = re.compile(r'.*(?=\s(\S*):)')
                    author_search = author_pattern.search(no_first_colon_search.group())
                    if author_search:
                        author = author_search.group()

                    # Get the defendant, which is the text after the remaining colon
                    defendant_pattern = re.compile(r'(?<=:\s).*')
                    defendant_search = defendant_pattern.search(no_first_colon_search.group())
                    if defendant_search:
                        defendant = defendant_search.group()
                    else:
                        # cant find a second colon, so the match is only for the author
                        author = no_first_colon_search.group()
            else:
                # check if there is only information about the defendant
                pattern = re.compile(r'(Réu):\s(.+?)(?=(Justiça Gratuita|Juiz|Juíza|Prioridade Idoso|Conclusão|CONCLUSÃO|C O N C L U S Ã O|Réu Preso|Descrição|Vistos))')
                sentence = pattern.search(text)
                if sentence:
                    remove_first_colon_pattern = re.compile(r'(?<=:\s).*')
                    no_first_colon_search = remove_first_colon_pattern.search(sentence.group())
                    if no_first_colon_search:
                        defendant = no_first_colon_search.group()
            authors.append(author)
            defendants.append(defendant)
            if author == np.nan or author == "":
                print('\nVazio---------------------\n')
                if author == '':
                    print('autor é string vazia\n')
                print('\ntext:\n')
                print(text)
                if sentence:
                    print('\nsentence:\n')
                    print(sentence.group())
                if no_first_colon_search:
                    print('\nno_first_colon_search\n:')
                    print(no_first_colon_search.group())

            i = i+1
        self.data['autor'] = authors
        self.data['réu'] = defendants
        null_authors = self.data['autor'].isnull().sum()
        null_defendants = self.data['réu'].isnull().sum()
        rows = len(self.data)
        print(f'autores faltantes: {(null_authors/rows)*100}%\n\nréus faltantes:{(null_defendants/rows)*100}%')
        #print(self.data.head(10))

    # def m_process_json(self):
    #     try:
    #         self.json_files = [json_file for json_file in os.listdir(self.files_path.get()) if json_file.endswith('.json')]
    #     except FileNotFoundError:
    #         Print("Arquivos não encontrados, o diretório indicado pode estar incorreto")
    #
    #     #I'M APPENDING TWO DIFFERENT TYPES OF JSON FILES HERE, 1 AND 2 DEGREE CASES, MAY CAUSE ERRORS
    #     self.data_list.clear()
    #     for json_file in self.json_files:
    #         with open(self.files_path.get() +'/'+ json_file,'r') as j:
    #             self.data_list.append(json.load(j))
    #
    #     #Get available metadata and it's possible values by iterating over the dictionaries
    #     self.key_to_possible_values_dic.clear()
    #     for file in self.data_list:
    #         for dic in file:
    #             for key,value in dic.items():
    #                 if key not in self.key_to_possible_values_dic.keys():
    #                     self.key_to_possible_values_dic[key] = set()
    #                 self.key_to_possible_values_dic[key].add(value)
    #
    #     self.all_keys = list(self.key_to_possible_values_dic.keys()).copy()
    #
    #     UNIQUE_KEYS = ['ementa', 'processo', 'cdacordao', 'julgado', 'pagina', 'duplicado', 'cd_doc']
    #     #remove useless keys from the metadata
    #     for useless_key in UNIQUE_KEYS:
    #         if useless_key in self.key_to_possible_values_dic.keys():
    #             del self.key_to_possible_values_dic[useless_key]
    #
    #     #sort it alphabetically
    #     for key in self.key_to_possible_values_dic.keys():
    #         for value in self.key_to_possible_values_dic[key]:
    #             break
    #         if isinstance(value,int):
    #             self.key_to_possible_values_dic[key] = sorted(self.key_to_possible_values_dic[key])
    #         elif isinstance(value,str):
    #             self.key_to_possible_values_dic[key] = sorted(self.key_to_possible_values_dic[key],key= str.lower)
    #
    #     return self.all_keys, self.key_to_possible_values_dic

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

    #
    def filter_is_empty(self, filter_list):
        flag = True
        for filter in filter_list:
            if filter != '':
                flag = False
        return flag

    def apply_filters(self,filters_dict, view_filters_list):
        df = self.data.copy()

        # Apply visualization filter
        for column in df.columns:
            if column not in view_filters_list:
                df.drop(column, inplace=True, axis=1)
                if column.capitalize() in filters_dict.keys():
                    del filters_dict[column.capitalize()]

        # Apply selection filter
        for key,values in filters_dict.items():
            if not self.filter_is_empty(values):
                filter = (df[key.lower()].isin(values))
                df = df.loc[filter]

        return df

    # def apply_filters(self, filters_dict, view_filters_list):
    #     new_data = []
    #     column_delete_set = set()
    #     for file in self.data_list:
    #         for dic in file:
    #             # make a copy so it doesnt change the original data
    #             tmp_dict = dic.copy()
    #             add_permission = True
    #             for key,value in tmp_dict.items():
    #                 if key not in view_filters_list:
    #                     # This column was not selected in the view filter
    #                     column_delete_set.add(key)
    #                     continue
    #                 else:
    #                     if key != 'processo':
    #                     # processo is a useless key to filter but may cause overflow in the date check
    #                         if not self.is_date(str(value)):
    #                             # it's  not a date
    #                             if key in filters_dict.keys():
    #                                 # key may have been filtered
    #                                 if not self.filter_is_empty(filters_dict[key]):
    #                                     # filter for this key is not empty
    #                                     if value not in filters_dict[key]:
    #                                         add_permission = False
    #                         else:
    #                             # it's a date
    #                             if key in filters_dict.keys():
    #                                 if not self.filter_is_empty(filters_dict[key]):
    #                                     initial_date = filters_dict[key][1]
    #                                     if initial_date == '':
    #                                         initial_date = '1700-01-01'
    #                                     end_date = filters_dict[key][0]
    #                                     if end_date == '':
    #                                         end_date = '5000-01-01'
    #                                     if (parse(value) < parse(initial_date)) or (parse(value) > parse(end_date)):
    #                                         add_permission = False
    #             # Delete the unwanted columns
    #             for column in column_delete_set:
    #                 del tmp_dict[column]
    #             if add_permission:
    #                 new_data.append(tmp_dict)
    #
    #     return new_data

    def save_csv(self, data):
        df = pd.DataFrame.from_records(data)
        save_directory = tk.filedialog.askdirectory(mustexist = True, title = 'Selecione o diretório em que deseja salvar o arquivo CSV')
        if not save_directory == '':
            df.to_csv(save_directory + '/veritas_consulta' + str(index) + '.csv', encoding='utf-8')

    def save_json(self, data):
        df = pd.DataFrame.from_records(data)
        save_directory = tk.filedialog.askdirectory(mustexist = True, title = 'Selecione o diretório em que deseja salvar o arquivo JSON')
        if not save_directory == '':
            with open(save_directory + '/veritas_consulta' + str(index) + '.json', 'w', encoding='utf-8') as file:
                df.to_json(file, orient='records', force_ascii=False)

class TestModel(ComponentModel):
    def __init__(self):
        print('Starting test model')

    def get_name(self):
        return 'Test Model'

    def requires_extra_input(self):
        return False

    def get_description(self):
        return 'teste'

    def execute(self, data, extra_input = None):
        fig,ax = plt.subplots()
        ax.plot([1,2,3],[1,2,3])
        cwd = os.getcwd()
        fig.savefig(cwd+'/images/fig1.png')
        img_path = cwd+'/images/fig1.png'
        return ['test_output', img_path, 'eaiii']

class CountDocuments(ComponentModel):
    def __init__(self):
        return
    def get_name(self):
        return 'Count Documents'

    def requires_extra_input(self):
        return True

    def get_description(self):
        string =  'Realiza a contagem dos documentos em relação às categorias escolhidas, os resultados incluem contagem absoluta e contagem relativa. '
        string += 'Para gerar gráficos selecione alguns dos checkboxes disponíveis.'
        return string

    def insert_linebreak(self,string, lengLabel=20):
        return '\n'.join(string[i:i+lengLabel] for i in range(0, len(string), lengLabel))

    def execute(self, data, extra_input):
        '''
        This module's required extra input is a list containing the categories on where the count in going to be made
        '''
        output = []
        df = data
        total_documents = len(df)
        output.append('Número total de documentos: ' + str(total_documents))

        for column in extra_input['selected_categories']:
            if column in df.columns:
                output.append('\nNúmero de documentos por: ' + str(column))
                absolute_count = df[column].value_counts()
                relative_count = df[column].value_counts(normalize = True)
                tmp_df = pd.DataFrame({'Absoluto': absolute_count, 'Relativo' : relative_count})
                output.append(tmp_df.to_string(justify='right'))
                if extra_input['bar_selected'] == 1:
                    # add a line break so the names can be read
                    bar_df = tmp_df.copy()
                    bar_df.index = bar_df.index.map(self.insert_linebreak)

                    output.append('\nGráfico de barras das '+ str(extra_input['bar_n'])+' aparições mais frequentes:')

                    bar_fig, bar_ax = plt.subplots()
                    bar_fig.set_size_inches((12,6))
                    plt.rcParams['font.size'] = 12.0
                    bar_df['Absoluto'].sort_index().head(extra_input['bar_n']).plot(kind='bar', ax=bar_ax)
                    bar_ax.set_xlabel(column.capitalize())
                    bar_ax.set_ylabel('N° de documentos')
                    bar_ax.set_title(str(column.capitalize()+ 's mais frequentes'))
                    plt.tight_layout()
                    cwd = os.getcwd()
                    bar_fig.savefig(cwd+'/images/'+column+'_bar'+'.png')
                    output.append(cwd+'/images/'+column+'_bar'+'.png')
                if extra_input['pie_selected'] == 1:
                    output.append('\nGráfico de pizza:')
                    pie_fig, pie_ax = plt.subplots()
                    pie_fig.set_size_inches((12,6))
                    plt.rcParams['font.size'] = 12.0

                    # Uses the relative count because its a pie chart
                    tmp_df['Relativo'].plot(kind='pie', ax=pie_ax, autopct='%1.1f%%', textprops={'fontsize': 8}, normalize = True)
                    pie_ax.set_title(str(column.capitalize()+ 's'))
                    pie_ax.set_ylabel('')
                    plt.tight_layout()
                    cwd = os.getcwd()
                    pie_fig.savefig(cwd+'/images/'+column+'_pie'+'.png')
                    output.append(cwd+'/images/'+column+'_pie'+'.png')
            output.append('-'*TEXT_WIDGET_WIDTH)

        return output

# class DateGraph(ComponentModel):
#     def get_name():
#         return 'Date Graph'
#
#     def requires_extra_input():
#         return False
#
#     def get_description():
#         return 'Gera um gráfico do número de documentos por período de tempo'
#
#     def execute(data, extra_input = None):
