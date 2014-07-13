import tkinter as tk


class _ObjectViewer(object):
    def __init__(self, objectFrame, specificationFrame, datacluster):
        self.objectFrame = objectFrame
        self.specificationFrame = specificationFrame
        self.datacluster = datacluster
    
        self.createWidgets()
    
        self.respecifyListbox()
    def createWidgets(self):
        self.createSorters()
        self.createListbox()
        self.createSpecifications()
        
    def createSorters(self):
        buttonFrame = tk.Frame(self.objectFrame, width=600, height=2)
        buttonFrame.grid(column=1,row=0)
        
        for i,field in enumerate(self.datacluster.getFields()):
            w = tk.Button(buttonFrame, width=10, text=field, command=lambda field=field: self.sortByField(field))
            w.grid(row=0,column=i)
    
        self.buttonFrame = buttonFrame
    def createListbox(self):
        listbox = tk.Listbox(self.objectFrame, font="monospace 9",width=80,height=40)
        listbox.grid(column=1,row=1)
        
        self.listbox = listbox
    
    def createSpecifications(self):
        self.specDict = {}
        
        group = tk.LabelFrame(self.specificationFrame, text="View:", padx=5, pady=5)
        
        d = self.datacluster.getSpecifiers()
        for i,specificator in enumerate(d):
            if type(d[specificator]) is bool:
                self.specDict[specificator] = d[specificator]
                w = tk.Button(group, width=12, text=specificator, command=lambda name=specificator: self.toggleSpecButton(name))
                w.grid(row=i,column=0)
            
            elif type(d[specificator]) is list:
                continue#listbox
                w.grid(row=tk.END,column=0)
        
        group.grid(row=0,column=0)
        self.specificationButtons = group
    
    def makeBoxWithContents(self, contents):
        """Fill box with string elements from contents"""
        self.listbox_table = list(enumerate(contents))
        for x in contents:
            self.listbox.insert(tk.END, x.gui_repr())
    
    def sortByField(self, field):
        pass
    
    def toggleSpecButton(self, name):
        self.specDict[name] = not self.specDict[name]
        self.respecifyListbox()
    
    def respecifyListbox(self):
        """Redraw listbox, using any changed settings"""
        def element_to_lbstring(element):
            """convert an element to a listbox string"""
            s = ""
            for field in element.getReprDict():
                maxlen = maxfields_d[field]
                
                s = s + str(element.getReprDict()[field]).ljust(maxlen+4)
            return s.strip()
        
        self.listbox.delete(0, tk.END)
        
        maxfields_d = self.datacluster.getFieldWidths()    
        
        d = {}
        for i,element in enumerate(self.datacluster.iter(self.specDict)):
            self.listbox.insert(tk.END, element_to_lbstring(element))
            d[i] = element
            
        
        #self.listbox.insert(tk.END, element)
        
    def destroy(self):
        self.buttonFrame.destroy()
        self.listbox.destroy()
        self.specificationButtons.destroy()
        
class GUI(object):
    def __init__(self, master, logviewer):
        self.root = master
        
        #access to data objects
        self.LV = logviewer
        
        self.createWidgets()
        
        self.OBJECT = None
        
    def createWidgets(self):
        self.createMenus()
        self.createFrames()
        self.createSelections()
    def createMenus(self):
        def createLoadMenu():
            filemenu = tk.Menu(self.root, tearoff=0)
            menubar.add_cascade(label="Open", menu=filemenu)
            
            filemenu.add_command(label="Load from a .json cache", command=lambda : print("K"))
            filemenu.add_command(label="Load new logs from a folder", command=lambda : None)
            filemenu.add_separator()
            filemenu.add_command(label="Load all logs from a folder", command=lambda : None)

        def createSaveMenu():
            filemenu = tk.Menu(self.root, tearoff=0)
            menubar.add_cascade(label="Save", menu=filemenu)
            
            filemenu.add_command(label="Save loaded games to a .json cache", command=lambda : None)
            
        #create menubar
        menubar = tk.Menu(self.root)
        #add File
        createLoadMenu()
        createSaveMenu()
        
        self.root.config(menu=menubar)
    
    def createFrames(self):
        #selection frame (champions, accounts, games)
        self.selectionFrame = tk.Frame(self.root, width=100,height=250)
        self.selectionFrame.grid(row=0, column=0)
        
        #object frame (lists, etc)
        self.objectFrame = tk.Frame(self.root, width=600, height=500)
        self.objectFrame.grid(row=0,column=1)
        
        #specification frame
        self.specificationFrame = tk.Frame(self.root, width=100, height=250)
        self.specificationFrame.grid(row=1, column=0)
        
        
    def createSelections(self):
        group = tk.LabelFrame(self.selectionFrame, text="View:", padx=5, pady=5)
        
        w1 = tk.Button(group, width=10, text="Games", command=self.selectionGames)
        w2 = tk.Button(group, width=10, text="Champions", command=self.selectionChampions)
        w3 = tk.Button(group, width=10, text="Accounts", command=self.selectionAccounts)
        
        w1.grid(row=0, sticky=tk.W)
        w2.grid(row=1, sticky=tk.W)
        w3.grid(row=2, sticky=tk.W)
        
        group.grid()
        
    def selectionGames(self):
        if self.OBJECT: self.OBJECT.destroy()
        
        self.OBJECT = _ObjectViewer(self.objectFrame, self.specificationFrame, self.LV.games)
    
    def selectionChampions(self):
        if self.OBJECT: self.OBJECT.destroy()
        self.OBJECT = None
        
    def selectionAccounts(self):
        if self.OBJECT: self.OBJECT.destroy()
        self.OBJECT = _ObjectViewer(self.objectFrame, self.specificationFrame, self.LV.accounts)
    

            
            
def createGUI(LV):
    root = tk.Tk()
    gui = GUI(root, LV)
    tk.mainloop()
