import sys
import os
from PyQt5 import QtWidgets, uic

From_DialogScript = uic.loadUiType(os.path.join(os.path.dirname(__file__),"dialogscript.ui"))[0]

class DialogScript(QtWidgets.QDialog, From_DialogScript):
    
    def __init__(self,name,pointDir):
        # Call constructor of parent classes
        super(DialogScript, self).__init__()
        QtWidgets.QDialog.__init__(self)
        
        self.setupUi(self)
        self.name = name
        self.pointDir = pointDir

        # Read the sample_text.txt
        # with open(os.path.join(os.path.dirname(__file__),"saved_text.txt")) as f:
        #     sample_text = f.read()
        # with open(os.path.join(pointDir,"saved_text.txt"),'w') as f:
        #     f.write(pointDir)
        try:
            # with open('saved_text.txt', 'r') as f:
            #     sample_text = f.read()
            #     f.close()
            with open(os.path.join(pointDir,"processed_data","script_"+name+".txt")) as f:
                sample_text = f.read()
        except:
            print("No saved script, show sample script")
            with open(os.path.join(os.path.dirname(__file__),"sample_text.txt")) as f:
                sample_text = f.read()
                f.close()
        # Set sample_text.txt as the defaut text on plainTextEdit
        self.plainTextEdit.setPlainText(sample_text)

    def getScript(self):
        scriptpartiel = self.plainTextEdit.toPlainText()
        scriptindente = scriptpartiel.replace("\n", "\n   ")
        script = "def fonction(dft, dfp): \n   " + scriptindente + "\n" + "   return(dft, dfp)"
        return(script,scriptpartiel)

    def updateScript(self):
        scriptpartiel = self.plainTextEdit.toPlainText()
        try:
            compilation = compile(scriptpartiel,"compilescript.py", "exec")
        except Exception as e:
            raise e
        # with open(os.path.join(self.pointDir,"script_"+self.point.name+".txt"),'w') as file:
        with open(os.path.join(self.pointDir,"processed_data","script_"+self.name+".txt"), "w") as f:
            f.write(scriptpartiel)
        print("Script successfully updated")
