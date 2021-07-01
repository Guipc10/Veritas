import tkinter as tk
from tkinter import ttk as ttk
from  gui.controllers import FilesController, Controller, StatisticsController
from gui.views import LoadFilesView, View, StatisticsOptionsView, QueryView
from gui.models import LoadFilesModel, TestModel, CountDocuments
from gui.util.helper_classes import ScrollFrame

class Application(ttk.Frame):
    def __init__(self, parent=None, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        # Set main window configurations
        self.parent.title("Veritas")
        self.desktop_width = self.parent.winfo_screenwidth()
        self.desktop_height = self.parent.winfo_screenheight()
        self.parent.geometry(f'{self.desktop_width}x{self.desktop_height}')
        self.background = 'white'
        self.parent.config(background=self.background)

        # Styles
        self.style = ttk.Style()
        self.style.configure("TNotebook",background=self.background)

        self.pack(fill='both', expand=True, anchor = 'center')
        # Create frame with vertical scrollbar
        self.scrollFrame = ScrollFrame(self)
        self.scrollFrame.pack(side='top',fill='both',expand=True)
        self.scrollFrame.viewPort.columnconfigure(0, weight = 1)

        # Create a notebook so the gui can have tabs
        self.notebook = ttk.Notebook(self.scrollFrame.viewPort)
        self.notebook.pack(fill='both', expand=True)
        self.notebook.columnconfigure(0, weight = 1)

        # Frame for the first tab
        self.first_tab = ttk.Frame(self.notebook)
        self.first_tab.pack(fill='both', expand=True, anchor = 'center')
        self.notebook.add(self.first_tab, text = 'Gerar consulta')

    def add_module(self, controller: Controller, view: View, model = None):
        if model == None:
            view = view(self.first_tab, self.notebook)
            controller.bind(view = view)
            return view
        else:
            # Its a query model
            controller.bind(view = view, model = model)

if __name__ == '__main__':
    root = tk.Tk()
    app = Application(root)


    load_files_model = LoadFilesModel()
    files_controller = FilesController(model = load_files_model)

    load_files_view = app.add_module(controller = files_controller, view = LoadFilesView)
    query_view = app.add_module(controller = files_controller, view = QueryView)

    main_controller = StatisticsController(load_files_model, load_files_view)

    testModel = TestModel()
    countDocuments = CountDocuments()

    # The View class is passed not instantiated
    app.add_module(controller = main_controller, view = None, model = testModel)
    app.add_module(controller = main_controller, view = None, model = countDocuments)

    app.add_module(controller = main_controller, view = StatisticsOptionsView)


    #maybe has to be app.mainloop()
    root.mainloop()
