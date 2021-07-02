import json,os
import tkinter as tk
from tkinter import ttk as ttk
from abc import ABC, abstractmethod
from dateutil.parser import parse
import matplotlib.pyplot as plt
import pandas as pd

# All new modules have to inherit from this class
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
            Print("Arquivos não encontrados, o diretório indicado pode estar incorreto")

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

        self.all_keys = list(self.key_to_possible_values_dic.keys()).copy()

        UNIQUE_KEYS = ['ementa', 'processo', 'cdacordao', 'julgado']
        #remove useless keys from the metadata
        for useless_key in UNIQUE_KEYS:
            if useless_key in self.key_to_possible_values_dic.keys():
                del self.key_to_possible_values_dic[useless_key]

        #sort it alphabetically
        for key in self.key_to_possible_values_dic.keys():
            self.key_to_possible_values_dic[key] = sorted(self.key_to_possible_values_dic[key],key= str.lower)

        return self.all_keys, self.key_to_possible_values_dic

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

    def apply_filters(self, filters_dict, view_filters_list):
        new_data = []
        column_delete_set = set()
        print('view filters list:', view_filters_list)
        for file in self.data_list:
            for dic in file:
                # make a copy so it doesnt change the original data
                tmp_dict = dic.copy()
                add_permission = True
                for key,value in tmp_dict.items():
                    if key not in view_filters_list:
                        # This column was not selected in the view filter
                        column_delete_set.add(key)
                        continue
                    else:
                        if key != 'processo':
                        # processo is a useless key to filter but may cause overflow in the date check
                            if not self.is_date(value):
                                # it's  not a date
                                if key in filters_dict.keys():
                                    # key may has been filtered
                                    if not self.filter_is_empty(filters_dict[key]):
                                        # filter for this key is not empty
                                        if value not in filters_dict[key]:
                                            add_permission = False
                            else:
                                # it's a date
                                if key in filters_dict.keys():
                                    if not self.filter_is_empty(filters_dict[key]):
                                        initial_date = filters_dict[key][1]
                                        if initial_date == '':
                                            initial_date = '1700-01-01'
                                        end_date = filters_dict[key][0]
                                        if end_date == '':
                                            end_date = '5000-01-01'
                                        if (parse(value) < parse(initial_date)) or (parse(value) > parse(end_date)):
                                            add_permission = False
                # Delete the unwanted columns
                for column in column_delete_set:
                    del tmp_dict[column]
                if add_permission:
                    new_data.append(tmp_dict)

        return new_data

class TestModel(ComponentModel):
    def __init__(self):
        print('Starting test model')

    def get_name(self):
        return 'Test Model'

    def requires_extra_input(self):
        return False

    def execute(self, data, extra_input = None):
        fig,ax = plt.subplots()
        ax.plot([1,2,3],[1,2,3])
        cwd = os.getcwd()
        fig.savefig(cwd+'/images/fig1.png')
        img_path = cwd+'/images/fig1.png'
        return ['test_output', img_path]

class CountDocuments(ComponentModel):
    def __init__(self):
        print('Starting Count Documents model')

    def get_name(self):
        return 'Count Documents'

    def requires_extra_input(self):
        return False

    def execute(self, data, extra_input):
        '''
        This module's required extra input is a list containing the categories on where the count in going to be made
        '''
        output = []
        df = pd.DataFrame.from_records(data)
        total_documents = len(df)
        output.append('Número total de documentos: ' + str(total_documents))
        for column in df[:len(df)-1]:
            grouped_count = df.groupby(column).count()
            # GETS AN ERROR WHEN THE DATA HAS ONLY ONE COLUMN
            if len(grouped_count.columns) > 1:
                one_column_frame = grouped_count[grouped_count.columns[0]]
            else:
                one_column_frame = grouped_count

            output.append('\nNúmero de documentos por: ' + str(column))

            frame = pd.DataFrame(one_column_frame)
            # Rename the columns and create a new column with the relative number of documents
            frame.columns = ['Absoluto']
            if column != 'julgado':
                relative = []
                for i in range(len(frame)):
                    relative.append(frame.iloc[i,0]/total_documents)
                print(f'len frame {len(frame)}, len relative {len(relative)}')
                frame['Relativo'] = relative
                output.append(frame.to_string(justify='right'))
                print(frame.to_string())

        return output
        # grouped = df.groupby('classe')
        # count = grouped.count()
        # print(count['processo'])
