from abc import ABC, abstractmethod
from gui.views import LoadFilesView, View
from gui.models import LoadFilesModel

class Controller(ABC):
    @abstractmethod
    def bind(view: View):
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
