"""
@author: Kartik Saini

"""
import tkinter as tk

class GUI:
    window_name = "Distributed Storage Service - Group14"

    def __init__(self):

        #creating main window and widgets
        self.window = tk.Tk() 
        self.window.configure(background = "grey")
		#getting screen width and height of display 
        self.window_width= self.window.winfo_screenwidth()  
        self.window_height= self.window.winfo_screenheight() 

		# img_w = int((self.window_width-40)/2) -10
		# img_h = self.window_height - 300

		#setting tkinter window size 
        self.window.geometry("%dx%d" % (self.window_width, self.window_height)) 
        self.window.title(self.window_name) 

		# 1st image path input
        tk.Label(self.window, text='First Image Path').grid(row=0)
        img1 = tk.StringVar() 
        self.e1 = tk.Entry(self.window, textvariable=img1, width=50) 
        self.e1.grid(row=0, column=1)
        self.b1 = tk.Button(self.window, text='Load', width=10)
        self.b1.grid(row=0, column=2)

        self.canvasG = tk.Canvas(self.window, width=self.window_width - 100, height=self.window_height - 300, bg="white") 
        self.canvasG.place(x = 60, y=50) 
		# self.canvasG.bind("<Button 1>",selectGlobalCanvas)

		# self.b3 = tk.Button(self.window, text='Undo Selection', width=30)
		# self.b3.place(x=300, y=img_h+100)

		# b4 = tk.Button(window, text='Stitch Images', width=30, command=automatch)#matchKeyPoints
		# b4 = tk.Button(window, text='Stitch Images', width=30, command=matchKeyPoints)
		# b4.place(x=window_width - 500, y=img_h+100)


        # self.window.mainloop()

    def _print(self, title="[INFO]", msg=""):
        print(title, msg)
