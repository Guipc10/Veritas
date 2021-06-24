import json,os
import tkinter as tk
from tkinter import ttk as ttk
from abc import ABC, abstractmethod

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

        #remove useless keys from the metadata
        del self.key_to_possible_values_dic['ementa']
        del self.key_to_possible_values_dic['processo']
        del self.key_to_possible_values_dic['cdacordao']
        del self.key_to_possible_values_dic['julgado']

        #sort it alphabetically
        for key in self.key_to_possible_values_dic.keys():
            self.key_to_possible_values_dic[key] = sorted(self.key_to_possible_values_dic[key],key= str.lower)

        return self.key_to_possible_values_dic

class TestModel(ComponentModel):
    def __init__(self):
        print('Starting test model')

    def getName(self):
        return 'Test Model'
