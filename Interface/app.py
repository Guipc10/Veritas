import tkinter as tk
from tkinter import ttk as ttk
from  gui.controllers import LoadFilesController, Controller
from gui.views import LoadFilesView, View
from gui.models import LoadFilesModel


class Application(ttk.Frame):
    def __init__(self, parent=None, *args, **kwargs):
        ttk.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        #set main window configurations
        self.parent.title("Veritas")
        self.parent.geometry('1024x800')
        self.background = 'white'
        self.parent.config(background=self.background)
        self.grid()

    def add_module(self, controller: Controller, view: View):
        view = view(self)
        #maybe change this grid
        view.grid()
        controller.bind(view)

if __name__ == '__main__':
    root = tk.Tk()
    app = Application(root)


    load_files_model = LoadFilesModel()
    load_files_controller = LoadFilesController(model = load_files_model)

    app.add_module(controller = load_files_controller, view = LoadFilesView)

    #maybe has to be app.mainloop()
    root.mainloop()
