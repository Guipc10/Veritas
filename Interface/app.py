import tkinter as tk
from tkinter import ttk as ttk
from  gui.controllers import LoadFilesController, Controller, MainController
from gui.views import LoadFilesView, View, QueryOptionsView
from gui.models import LoadFilesModel, TestModel
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
        self.pack(fill='both', expand=True, anchor = 'center')
        # Create frame with vertical scrollbar
        self.scrollFrame = ScrollFrame(self)
        self.scrollFrame.pack(side='top',fill='both',expand=True,anchor = 'center')
        self.scrollFrame.viewPort.columnconfigure(0, weight = 1)

    def add_module(self, controller: Controller, view: View, model = None):
        if model == None:
            view = view(self.scrollFrame.viewPort)
            controller.bind(view = view)
            return view
        else:
            # Its a query model
            controller.bind(view = view, model = model)

if __name__ == '__main__':
    root = tk.Tk()
    app = Application(root)


    load_files_model = LoadFilesModel()
    load_files_controller = LoadFilesController(model = load_files_model)

    load_files_view = app.add_module(controller = load_files_controller, view = LoadFilesView)

    main_controller = MainController(load_files_model, load_files_view)

    testModel = TestModel()
    app.add_module(controller = main_controller, view = None, model = testModel)

    app.add_module(controller = main_controller, view = QueryOptionsView)


    #maybe has to be app.mainloop()
    root.mainloop()
