from abc import ABC, abstractmethod
from gui.views import LoadFilesView, View, StatisticsOptionsView, QueryView
from gui.models import LoadFilesModel, ComponentModel

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
        def csv_handler(event, self=self, i = index):
            return self.export_to_csv(event, index = i)
        csv_button.bind('<Button-1>',csv_handler)
        def json_handler(event, self=self, i = index):
            return self.export_to_json(event, index = i)
        json_button.bind('<Button-1>',json_handler)

        # Create statistics options
        self.statistics_controller.call_view(new_tab_frame, filters_dict, view_filters_list)

    def export_to_csv(self, event, index):
        (filters_dict, view_filters_list) = self.tab_filters_list[index]
        self.model.save_csv(filters_dict,view_filters_list,index)

    def export_to_json(self, event, index):
        (filters_dict, view_filters_list) = self.tab_filters_list[index]
        self.model.save_json(filters_dict,view_filters_list,index)

class StatisticsController(Controller):
    def __init__(self, model: LoadFilesModel, view: LoadFilesView):
        self.load_files_model = model
        self.load_files_view = view
        self.statistics_options_view_list = []
        self.models_dict = {}
        self.models_view_dict = {}

    def bind(self,view: View, **kwargs):

        if 'model' in kwargs.keys():
            model = kwargs['model']
            self.models_dict[model.get_name()] = model
            self.models_view_dict[model.get_name()] = view
        else:
            self.statistics_options_view_list.append(view)

    # Creates a list of statistics option in the given parent frame
    def call_view(self, parent, filters_dict, view_filters_list):
        self.statistics_options_view_list.append(StatisticsOptionsView(parent, None))
        self.statistics_options_view_list[len(self.statistics_options_view_list)-1].create_view()
        self.statistics_options_view_list[len(self.statistics_options_view_list)-1].set_filters(filters_dict, view_filters_list)
        self.statistics_options_view_list[len(self.statistics_options_view_list)-1].create_statistics_options(self.models_view_dict)
        def handler(event, self=self, i=(len(self.statistics_options_view_list)-1)):
            return self.generate_statistics(event,i)
        self.statistics_options_view_list[len(self.statistics_options_view_list)-1].statistics_button.bind('<Button-1>', handler)


    def generate_statistics(self, event, options_view_index):
        #get a list of names of the models that are going to be used
        selected_models = self.statistics_options_view_list[options_view_index].get_selected_models()

        # get the filters to be considered, it's in each statistics_options_view because it would take the "gerar consulta" filters
        # otherwise
        filters_dict, view_filters_list = self.statistics_options_view_list[options_view_index].get_filters()

        #apply filters on the data to generate a filtered data, the data returned is a list of dicts,
        # where each dictionary is one document
        filtered_data = self.load_files_model.apply_filters(filters_dict, view_filters_list)

        # Output is a list of lists, where the first element of each list is the name of the model and the second is its content:
        # a list of strings and images
        output = []
        for model_name in selected_models:
            if self.models_dict[model_name].requires_extra_input():
                extra_input = self.models_view_dict[model_name].get_extra_input()
            else:
                extra_input = None
            output.append([model_name, self.models_dict[model_name].execute(filtered_data, extra_input)])

        # Generates a pdf file
        self.statistics_options_view_list[options_view_index].generate_output(output)
