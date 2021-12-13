import tkinter as tk
import matlab.engine
import os
import glob
import sys
import importlib.util
import re

class ProgressBar:

    def createPreprocessFunctions(self, fn_list, fns_path, output_path, inputs, outputs):
        preprocessing_functions = [None]

        j = 0
        for i in range(len(fn_list)-1, -1, -1):
            def fn(i=i, j=j):

                # set up to run other preprocessing functions
                sys.path.append(fns_path)  # add function path to python
                eng = matlab.engine.start_matlab()  # start matlab engine
                eng.addpath(fns_path)  # pass in a path to function files
                split_function_name = fn_list[i].split('.')  # splits the function name from the extension

                # check if function is a '.m file
                if fn_list[i].endswith('.m'):
                    post_process = 'eng.' + split_function_name[0]  # adds 'eng.' prefix and removes '.m' suffix
                    try:
                        eval(post_process)(*inputs[i], nargout=2)  # runs function in MATLAB Engine
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
        self.fn_list = ["exponent_1.m", "print_rt.m", "multiple_rt.py", "sum_rt.m"]
        self.inputs = [[2, 8], [3.14], [5, 2], [3, 5]] # what are the inputs going to look like?
        self.outputs = ["_exponent_1_results.txt", "_print_rt_results.txt", "_multiple_rt.py", "_sum_1_results.txt"]
        self.fns_path = "C:/Users/rtung/Desktop/Burgess_lab/Preprocessing_funcs/" # folder that holds all functions
        self.data_path = "C:/Users/rtung/Desktop/Burgess_lab/data/" # folder that holds data for a specific animal
        self.output_path = "C:/Users/rtung/Desktop/Burgess_lab/outputs/" # folder that holds output files
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
        print(self.step)

        # For all completed steps, display the disabled button
        for completedSteps in range(self.step):
            self.button_dict[completedSteps].place(x=completedSteps * self.button_distance + self.initial_padding, y=70)
            self.button_dict[completedSteps]['image'] = self.completed_image
            self.button_dict[completedSteps]['state'] = "disabled"

        # Run the next step that is available
        self.runNextStep(self.preprocessing_functions[self.step])

    def checkCompletedSteps(self, listExt, path): # check the logic here
        for ext in range(len(listExt)):
            print(listExt[ext])
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith(listExt[ext]):
                        print(listExt[ext])
                        self.step += 1
                        print('self.step in checkCompletedSteps is', self.step)
                    else:
                        print('file not found')
                        break



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