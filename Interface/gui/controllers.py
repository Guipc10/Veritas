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

#
class MainController(Controller):
    def __init__(self, model: LoadFilesModel, view: LoadFilesView):
        self.load_files_model = model
        self.load_files_view = view
        self.query_options_view = None
        self.models_dict = {}
        self.models_view_dict = {}

    def bind(self, **kwargs):
        try:
            view = kwargs['view']
        except:
            raise KeyError('You must provide a View class')

        if 'model' in kwargs.keys():
            model = kwargs['model']
            self.models_dict[model.getName()] = model
            self.models_view_dict[model.getName()] = view
        else:
            self.query_options_view = view
            self.query_options_view.create_view()
            self.query_options_view.create_query_options(self.models_view_dict)
            self.query_options_view.query_button.bind('<Button-1>', self.generate_query)


    def generate_query(self, event):
        #since the button that generated this event is in the same frame as the checkboxes, so the values can be accessed easily
        print('generate query')
