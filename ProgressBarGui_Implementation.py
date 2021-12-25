import tkinter as tk
import matlab.engine
import os
import glob
import sys
import importlib.util
import re
re.compile('<title>(.*)</title>')

class ProgressBar:

    def createPreprocessFunctions(self, fn_list, fns_path, output_path, inputs, outputs):
        preprocessing_functions = [None]

        j = 0
        for i in range(len(fn_list)-1, -1, -1):
            def fn(i=i, j=j):

                # set up to run other preprocessing functions
                sys.path.append(fns_path)  # add function path to python
                print(fns_path)
                eng = matlab.engine.start_matlab()  # start matlab engine
                eng.addpath(fns_path)  # pass in a path to function files
                split_function_name = fn_list[i].split('.')  # splits the function name from the extension

                # check if function is a '.m file
                if fn_list[i].endswith('.m'):
                    post_process = 'eng.' + split_function_name[0]  # adds 'eng.' prefix and removes '.m' suffix
                    try:
                        eval(post_process)(*inputs[i], nargout=0)  # runs function in MATLAB Engine
                        if glob.glob(output_path + "*" + outputs[i]):
                            self.runNextStep(preprocessing_functions[j])
                        else:
                            print("File was not created")
                            self.stepFailed()
                            return
                    except Exception as e:  # shows failure if matlab fails
                        self.stepFailed()
                        raise e

                # if not a .m file, run in python
                else:
                    try:
                        spec = importlib.util.spec_from_file_location(fn_list[i], fns_path + fn_list[i])
                        functionModule = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(functionModule)
                        eval("functionModule." + split_function_name[0] + "(*inputs[i])")
                        if glob.glob(output_path + "*" + outputs[i]):
                            print(outputs[i])
                            self.runNextStep(preprocessing_functions[j])
                        else:
                            print("File was not created")
                            self.stepFailed()

                    except Exception as e:
                        self.stepFailed()
                        raise e


            preprocessing_functions.append(fn)
            j = j + 1


        return preprocessing_functions[::-1]

    def __init__(self, root):
        ##### These need manual inputs ##########################
        ##### i.e. needs to inherit these from other classes#####
        self.fn_list = ["readSbxEphysCheck.m"]
        self.inputs = [["E:/T03_Burgess/210205_T03/T01_run1/T03_210205_001.sbx"]] # what are the inputs going to look like?
        self.outputs = ["_nidaq.mat"]
        self.fns_path = "E:/pipe.cb/functions" # folder that holds all functions
        self.data_path = "E:/T03_Burgess/210205_T03/T01_run1/" # folder that holds data for a specific animal
        self.output_path = "E:/T03_Burgess/210205_T03/T01_run1/" # folder that holds output files
        # What is every step and what is the order that we do this in
        #########################################################

        # Create preprocessing functions
        self.preprocessing_functions = self.createPreprocessFunctions(self.fn_list, self.fns_path, self.output_path, self.inputs, self.outputs)

        ##### File images for buttons############################
        self.default_image = tk.PhotoImage(file='./Circle_28x28.png')
        self.completed_image = tk.PhotoImage(file='./Circle_complete.png')
        self.failed_image = tk.PhotoImage(file='./Circle_failed.png')
        #########################################################

        # Initializing
        self.total_steps = len(self.preprocessing_functions)
        self.button_dict = [None] * self.total_steps
        self.step = 0

        # creates all buttons
        for step in range(self.total_steps):
            self.button_dict[step] = tk.Button(text=step + 1, image=self.default_image, bd=0, compound='center')

        # initialize spaces between buttons
        self.button_distance = 100
        self.initial_padding = 100

        # Check if files have been completed already
        self.checkCompletedSteps(self.outputs, self.output_path)


        # For all completed steps, display the disabled button
        for completedSteps in range(self.step):
            self.button_dict[completedSteps].place(x=completedSteps * self.button_distance + self.initial_padding, y=70)
            self.button_dict[completedSteps]['image'] = self.completed_image
            self.button_dict[completedSteps]['state'] = "disabled"

        # Run the next step that is available
        self.runNextStep(self.preprocessing_functions[self.step])

# MAKE SURE THIS WORKS BEFORE ANYTHING ELSE
# ISSUE: This doesn't make sense if step 1 and 3 are done but not step 2
# it just adds a counter to steps for every file that's been created
# if step 1 and 3 are created, step counter = 2
# that will skil step 2 and that's no bueno
    def checkCompletedSteps(self, listExt, path): # check the logic here
        Completion_list = [0] * len(listExt)
        print(path)
        for ext in range(len(listExt)):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(listExt[ext]):
                        Completion_list[ext] = 1
                        self.step += 1
                        print('self.step in checkCompletedSteps is', self.step)
                        print(Completion_list)
                    else:
                        print(listExt[ext] + ' file not found')


    def runNextStep(self, fn):
        if fn is None: # Preprocessing Completed
            self.button_dict[self.step-1]['state'] = "disabled"
            self.button_dict[self.step-1]['image'] = self.completed_image
            return

        if self.step != 0: #FIRST STEP
            self.button_dict[self.step - 1]['image'] = self.completed_image
            self.button_dict[self.step - 1]['state'] = "disabled"
        self.button_dict[self.step].place(x=self.step * self.button_distance + self.initial_padding, y=70)
        self.button_dict[self.step]['command'] = fn
        self.step = self.step + 1


    def stepFailed(self):
        self.button_dict[self.step-1]['image']= self.failed_image

if __name__ == "__main__":
    # Creates initial GUI window, not necessarily needed
    def createTk(title, width, height):
        root = tk.Tk()
        root.title(title)
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        root.geometry(alignstr)
        root.resizable(width=True, height=True)
        return root
    root = createTk("Progress Bar GUI", 900, 500)
    progressBar = ProgressBar(root)
    root.mainloop()