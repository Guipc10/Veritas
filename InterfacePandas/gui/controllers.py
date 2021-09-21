from abc import ABC, abstractmethod
from gui.views import LoadFilesView, View, StatisticsOptionsView, QueryView
from gui.models import LoadFilesModel, ComponentModel
import threading
from icecream import ic
import time
import queue

class Controller(ABC):
    @abstractmethod
    def bind(view: View, model = None):
        raise NotImplementedError

class FilesController(Controller):
    def __init__(self, model: LoadFilesModel):
        self.model = model
        self.load_files_view = None
        self.query_view = None
        self.statistics_controller = None

        # List of filters for each tab, each item is a tuple
        self.tab_filters_list = []


    def bind(self,view: View):
        if (isinstance(view, LoadFilesView)):
            self.load_files_view = view
            self.load_files_view.create_view()
            self.load_files_view.process_files_button.bind('<Button-1>',self.process_json)
            self.load_files_view.generatequeryButton.bind('<Button-1>', self.generate_query)
            #allow the model to always have the path
            self.model.set_path_variable(self.load_files_view.files_path)

        elif (isinstance(view, QueryView)):
            self.query_view = view

    def bind_statistics_controller(self, statistics_controller):
        self.statistics_controller = statistics_controller

    def process_json(self, event):
        all_keys, key_to_possible_values_dic = self.model.m_process_json()
        print(all_keys)
        self.load_files_view.create_filter()
        self.load_files_view.create_comboboxes(key_to_possible_values_dic)
        self.load_files_view.create_check_boxes(all_keys)

    def generate_query(self, event):
        filters_dict = self.load_files_view.get_filters()
        view_filters_list = self.load_files_view.get_selected_keys()

        data = self.model.apply_filters(filters_dict, view_filters_list)
        new_tab_frame, csv_button, json_button = self.query_view.create_view(data)
        # Buttons handlers
        self.tab_filters_list.append((filters_dict, view_filters_list))
        index = len(self.tab_filters_list) - 1
        def csv_handler(event, self=self, df = data):
            return self.export_to_csv(event, df)
        csv_button.bind('<Button-1>',csv_handler)
        def json_handler(event, self=self, df = data):
            return self.export_to_json(event, df)
        json_button.bind('<Button-1>',json_handler)

        # Create statistics options
        self.statistics_controller.call_view(new_tab_frame, data)

    def export_to_csv(self, event, data):
        #(filters_dict, view_filters_list) = self.tab_filters_list[index]
        self.model.save_csv(data)

    def export_to_json(self, event, data):
        #(filters_dict, view_filters_list) = self.tab_filters_list[index]
        self.model.save_json(data)

class ThreadedExecute(threading.Thread):
    def __init__(self, model,model_name, data, extra_input, output_dict, queue):
        super().__init__()
        self.model = model
        self.model_name = model_name
        self.data = data
        self.extra_input = extra_input
        self.output_dict = output_dict
        self.queue = queue

    def run(self):
        output = self.model.execute(self.data, self.extra_input)
        self.output_dict[self.model_name] = output
        # Remove the process from the queue
        ic('process finished')
        self.queue.get_nowait()
        ic('queue:', self.queue.qsize())

class StatisticsController(Controller):
    def __init__(self, model: LoadFilesModel, view: LoadFilesView, root):
        self.load_files_model = model
        self.load_files_view = view
        self.statistics_options_view_list = []
        self.models_dict = {}
        self.models_view_dict = {}
        # List of dictionaries so each tab has it own instance of the model's view
        self.models_view_dict_list = []
        self.root = root

    def bind(self,view: View, **kwargs):

        if 'model' in kwargs.keys():
            model = kwargs['model']
            self.models_dict[model.get_name()] = model
            self.models_view_dict[model.get_name()] = view
        else:
            self.statistics_options_view_list.append(view)

    # Creates a list of statistics option in the given parent frame
    def call_view(self, parent, data):
        self.statistics_options_view_list.append(StatisticsOptionsView(parent, None))
        self.statistics_options_view_list[len(self.statistics_options_view_list)-1].create_view()
        models_descriptions = self.get_all_models_description()
        #self.statistics_options_view_list[len(self.statistics_options_view_list)-1].set_filters(filters_dict, view_filters_list)
        # append new instances of models views
        self.models_view_dict_list.append(self.statistics_options_view_list[len(self.statistics_options_view_list)-1].create_statistics_options(self.models_view_dict, models_descriptions, data))
        def handler(event, self=self, i=(len(self.statistics_options_view_list)-1), df = data):
            return self.generate_statistics(event,i,df)
        self.statistics_options_view_list[len(self.statistics_options_view_list)-1].statistics_button.bind('<Button-1>', handler)

    def get_all_models_description(self):
        all_descriptions = {}
        for model_name, model in self.models_dict.items():
            all_descriptions[model_name] = model.get_description()
        return all_descriptions

    #def generate_statistics_thread(self,options_view_index, data):
    def check_thread(self, options_view_index, my_queue, output_dict):
        if my_queue.empty():
            # all threads are finished
            # Generates output on the screen
            self.statistics_options_view_list[options_view_index].generate_output(output_dict)

            self.statistics_options_view_list[options_view_index].finish_progress_window()
        else:
            def handler(options_view_index=options_view_index, my_queue=my_queue, output_dict=output_dict):
                return self.check_thread(options_view_index, my_queue, output_dict)
            ic('process still running')
            self.root.after(10, handler)

    def generate_statistics(self, event, options_view_index, data):
        #self.statistics_options_view_list[options_view_index].start_progress_window()


        #threading.Thread(target=self.generate_statistics_thread, args=(options_view_index, data,).start()

        #get a list of names of the models that are going to be used
        selected_models = self.statistics_options_view_list[options_view_index].get_selected_models()

        # get the filters to be considered, it's in each statistics_options_view because it would take the "gerar consulta" filters
        # otherwise
        #filters_dict, view_filters_list = self.statistics_options_view_list[options_view_index].get_filters()

        #apply filters on the data to generate a filtered data, the data returned is a list of dicts,
        # where each dictionary is one document
        #filtered_data = self.load_files_model.apply_filters(filters_dict, view_filters_list)

        # Output is dict, where the key is the name of the model and the items are its content:
        # a list of strings and images
        output = {}

        my_queue = queue.Queue()
        for model_name in selected_models:
            if self.models_dict[model_name].requires_extra_input():
                extra_input = self.models_view_dict_list[options_view_index-1][model_name].get_extra_input()
            else:
                extra_input = None

            # Do the rest of the work in a different thread so the progress bar can be shown
            # puts a random item to the queue because its going to be used only for tracking the still running threads
            # ic('new process')
            #my_queue.put(1)
            # ic('queue:', my_queue.qsize())
            # Delivers a copy of the data to the models so it doesnt cause inconsistency
            #ThreadedExecute(self.models_dict[model_name],model_name, data.copy(), extra_input, output, my_queue).start()

            output[model_name] = self.models_dict[model_name].execute(data.copy(), extra_input)
        # Schedule a periodic check on the threads
        # def handler(options_view_index=options_view_index, queue=my_queue, output_dict=output):
        #     return self.check_thread(options_view_index, queue, output_dict)
        # self.root.after(10, handler)
        self.statistics_options_view_list[options_view_index].generate_output(output)

        #self.statistics_options_view_list[options_view_index].finish_progress_window()
