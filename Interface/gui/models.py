import json,os
import tkinter as tk
from tkinter import ttk as ttk
from abc import ABC, abstractmethod
from dateutil.parser import parse

# All new modules have to inherit from this class
class ComponentModel():
    @abstractmethod
    def getName():
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


        UNIQUE_KEYS = ['ementa', 'processo', 'cdacordao', 'julgado']
        #remove useless keys from the metadata
        for useless_key in UNIQUE_KEYS:
            if useless_key in self.key_to_possible_values_dic.keys():
                del self.key_to_possible_values_dic[useless_key]

        #sort it alphabetically
        for key in self.key_to_possible_values_dic.keys():
            self.key_to_possible_values_dic[key] = sorted(self.key_to_possible_values_dic[key],key= str.lower)

        return self.key_to_possible_values_dic

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
    def apply_filters(self, filters_dict):
        new_data = []

        for file in self.data_list:
            for dic in file:
                add_permission = True
                for key,value in dic.items():
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
                if add_permission:
                    new_data.append(dic)

        return new_data

class TestModel(ComponentModel):
    def __init__(self):
        print('Starting test model')

    def getName(self):
        return 'Test Model'
