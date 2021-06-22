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
        self.desktop_width = self.parent.winfo_screenwidth()
        self.desktop_height = self.parent.winfo_screenheight()
        self.parent.geometry(f'{self.desktop_width}x{self.desktop_height}')
        self.background = 'white'
        self.parent.config(background=self.background)
        self.pack(fill='both', expand=True, anchor = 'center')

    def add_module(self, controller: Controller, view: View):
        view = view(self)
        controller.bind(view)

if __name__ == '__main__':
    root = tk.Tk()
    app = Application(root)


    load_files_model = LoadFilesModel()
    load_files_controller = LoadFilesController(model = load_files_model)

    app.add_module(controller = load_files_controller, view = LoadFilesView)

    #maybe has to be app.mainloop()
    root.mainloop()
