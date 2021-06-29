from abc import ABC, abstractmethod
from gui.views import LoadFilesView, View, QueryOptionsView
from gui.models import LoadFilesModel, ComponentModel

class Controller(ABC):
    @abstractmethod
    def bind(view: View, model = None):
        raise NotImplementedError

class LoadFilesController(Controller):
    def __init__(self, model: LoadFilesModel):
        self.model = model
        self.view = None

    def bind(self,view: LoadFilesView):
        self.view = view
        self.view.create_view()
        self.view.process_files_button.bind('<Button-1>',self.process_json)

        #allow the model to always have the path
        self.model.set_path_variable(self.view.files_path)


    def process_json(self, event):
        key_to_possible_values_dic = self.model.m_process_json()
        self.view.create_comboboxes(key_to_possible_values_dic)

class MainController(Controller):
    def __init__(self, model: LoadFilesModel, view: LoadFilesView):
        self.load_files_model = model
        self.load_files_view = view
        self.query_options_view = None
        self.models_dict = {}
        self.models_view_dict = {}

    def bind(self,view: View, **kwargs):

        if 'model' in kwargs.keys():
            model = kwargs['model']
            self.models_dict[model.get_name()] = model
            self.models_view_dict[model.get_name()] = view
        else:
            self.query_options_view = view
            self.query_options_view.create_view()
            self.query_options_view.create_query_options(self.models_view_dict)
            self.query_options_view.query_button.bind('<Button-1>', self.generate_query)


    def generate_query(self, event):
        #get a list of names of the models that are going to be used
        selected_models = self.query_options_view.get_selected_models()

        #get the filters to be considered
        filters_dict = self.load_files_view.get_filters()

        #apply filters on the data to generate a filtered data, the data returned is a list of dicts,
        # where each dictionary is one document
        filtered_data = self.load_files_model.apply_filters(filters_dict)

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
        self.query_options_view.generate_output(output)
