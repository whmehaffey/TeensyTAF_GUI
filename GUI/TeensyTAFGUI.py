	
import sys
from PyQt4.QtGui import QApplication,QDialog,QSizeGrip,QMessageBox
from PyQt4 import QtCore, QtGui, uic
from collections import deque
import serial as serial
from numpy import array
 
qtCreatorFile = "Gui.ui" # Enter file here.
import GlobalVars
 
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

def GetTeensyPorts():
    import GlobalVars

    import sys, serial
    from serial.tools import list_ports

    TeensyPort = (list_ports.grep("16c0:0483"))

    i=0;    

    for p in TeensyPort:                              
               temp = p[0]
               print temp
               ui.Teensy_Com_ComboBox.insertItem(0,str(temp))          

    GlobalVars.CurrentPort=temp
    

def startButtonPressed():
        import GlobalVars
        import Functions
        #import numpy as np
        from numpy import histogram, array, arange
        import sys
        import os
        import time
        from Functions import setAllButtons

        QueSize=150;
        TemplateCurrent=True;
        isUpdated=False;
        templateOverPlot=0;
        GlobalVars.FF = deque(maxlen=QueSize)
        GlobalVars.HIT = deque(maxlen=QueSize)
        GlobalVars.DP = deque(maxlen=QueSize)

        try:
            GlobalVars.ser=serial.Serial(str(GlobalVars.CurrentPort),115200)
        except:            
            messageBox=QMessageBox()
            messageBox.setWindowTitle("Serial Error")
            messageBox.setText("Serial Port Already Open?")   
            messageBox.setFixedSize(500,200);
            messageBox.show()
        
        GlobalVars.ser.set_buffer_size(rx_size = 50000, tx_size = 50000)
        
        date=time.localtime();

        RemoveAppendix=str(GlobalVars.SavePath);
        RemoveAppendix.strip('.TAFlog')
        BaseFileName=RemoveAppendix+str(date[0])+','+str(date[1])+','+str(date[2])+','+str(date[3])+','+str(int(time.time()))
        
        configfilename=BaseFileName+'.TAFcfg'
        GlobalVars.saveConfig(configfilename)        
        GlobalVars.outfile=open(BaseFileName+'.TAFlog','w')     #Matched filenames for data and .Config files, for the sake of sanity.    
        
        setAllButtons(ui,False);
        ui.stopButton.setEnabled(True);
        GlobalVars.ser.flush()

        GlobalVars.SendAllToTeensy()
        
        GlobalVars.ser.write('START;')        
        GlobalVars.isRunning=True
            
        while GlobalVars.isRunning==True:            
            isUpdated=Functions.GetSerialData(GlobalVars.outfile);
            
            if ((len(GlobalVars.FF)>5) and isUpdated):
                y,x=histogram(GlobalVars.FF)
                ui.FFMonitorPlot.clear()
                ui.FFMonitorPlot.plot(x,y,stepMode=True,fillLevel=None, brush=(0,0,255,150))
                y,x=histogram(GlobalVars.DP);
                ui.DPHistGraph.clear()
                ui.DPHistGraph.plot(x,y,stepMode=True,fillLevel=None, brush=(0,0,255,150))
                TemplateCurrent=False
                
            if ((len(GlobalVars.FF)==QueSize) and isUpdated and GlobalVars.upDateThreshold): #Is Cue Full?
                SortedFFs=sorted(GlobalVars.FF)
                if (GlobalVars.HitDIR==1):  # Only move higher
                    percentileidx=int(QueSize*0.75)
                    Threshold=SortedFFs[percentileidx]
                    GlobalVars.FreqTHRESH=Threshold;
                    GlobalVars.ser.write('SET FREQTHRESH ' + str(GlobalVars.FreqTHRESH) + ';')
                    ui.editFREQ_THRESH.setText((str(GlobalVars.FreqTHRESH)))
                    
                if (GlobalVars.HitDIR==0):   # Only move lower.
                    percentileidx=int(QueSize*0.25)
                    Threshold=SortedFFs[percentileidx]
                    GlobalVars.FreqTHRESH=Threshold;
                    GlobalVars.ser.write('SET FREQTHRESH ' + str(GlobalVars.FreqTHRESH) + ';')
                    ui.editFREQ_THRESH.setText((str(GlobalVars.FreqTHRESH)))

##            # Sometimes worth plotting reference magnitudes.....         
##            if (not(isUpdated) and not(TemplateCurrent)): #if we don't have new data, and don't have a current template
##                    GlobalVars.ser.write('GET MAGS;')
##                    
##                    if (GlobalVars.ser.in_waiting>0):                        
##                        line=GlobalVars.ser.readline(GlobalVars.ser.inWaiting()).strip('\n\r');
##                        if (line[0:4]=="MAG "):
##                            line=line.lstrip("MAG ")
##                           # print line
##                            MAGS=array(line.split(','), dtype=float)
##                            if (templateOverPlot>5):
##                                ui.MagsfromTeensy.clear()
##                                templateOverPlot=0;
##                                
##                            ui.MagsfromTeensy.plot(MAGS,arange(0,GlobalVars.sampleBin*(GlobalVars.FFT/2),GlobalVars.sampleBin))
##                            templateOverPlot=templateOverPlot+ 1                            
##                            TemplateCurrent=True;
                            
       
                
            isUpdated=False;

#            if (isUpdated and MagsCounter >10)
          #  ui.FFMonitorPlot.pyplot(GlobalVars.FF);
            app.processEvents();            
        
def stopButtonPressed():
        import GlobalVars
        from Functions import setAllButtons
        
        GlobalVars.isRunning=False;
        GlobalVars.ser.write('STOP;');
        GlobalVars.ser.close();
        setAllButtons(ui,True);
        ui.stopButton.setEnabled(False);
        ui.startButton.setEnabled(True);
        GlobalVars.outfile.close()
        
        
def updateTemplate():
        import GlobalVars
        from ConfigParser import SafeConfigParser
        from numpy import arange, array      

        loadfilename = (QtGui.QFileDialog.getOpenFileName(ui,'Open Config File', '.','*.TMPLT'))
        loadfilename=loadfilename.replace('/','\\') #.replace('/','\\')):

        parser=SafeConfigParser()
        if not parser.read(str(loadfilename)): 
            raise IOError, 'cannot load'
        
        newTemplate=parser.get('template','GlobalVars.template');
        print newTemplate
        newTemplate=newTemplate.replace('[','')
        newTemplate=newTemplate.replace(']','')

        
        GlobalVars.template= array(newTemplate.split(','), dtype=float)

        GlobalVars.ser=serial.Serial(str(GlobalVars.CurrentPort),115200)
        GlobalVars.ser.set_buffer_size(rx_size = 50000, tx_size = 50000)
        GlobalVars.ser.flush()
        
        GlobalVars.ser.write('SET TEMPLATE ' + newTemplate +';')
        #GlobalVars.ser.write('GET TEMPLATE;')               
        GlobalVars.ser.close();

        ui.templateView.clear();
        ui.templateView.plot(GlobalVars.template,arange(0,GlobalVars.sampleBin*128,GlobalVars.sampleBin))


def loadConfig_ButtonPressed():
        import os
        import GlobalVars       
                
        loadfilename = (QtGui.QFileDialog.getOpenFileName(ui,'Open Config File', '.','*.TAFcfg'))        
        GlobalVars.loadConfig(loadfilename)
        GlobalVars.UpDateValues(ui)


def saveConfig_ButtonPressed():
     import GlobalVars
     savefilename = (QtGui.QFileDialog.getSaveFileName(ui,'Save Config File', '.', '.TAFcfg'))
     GlobalVars.saveConfig(savefilename)


def SaveFileButtonPressed():
    import os
    import GlobalVars
    
    GlobalVars.SavePath = QtGui.QFileDialog.getSaveFileName(ui,'Save File', '.', '.TAFlog')    
    ui.SaveFilePathLabel.setText(GlobalVars.SavePath)
    print GlobalVars.SavePath


def editAMP():
        import GlobalVars
    
        GlobalVars.AMP=float(ui.editAMPTHRESHOLD.text());
        #print ('SET AMP ' + str(GlobalVars.AMP) + ';')
        if GlobalVars.isRunning:            
            GlobalVars.ser.write('SET AMP_THRESHOLD ' + str(GlobalVars.AMP) + ';')
         

def editDPTHRESH():
        import GlobalVars
    
        GlobalVars.DPTHRESH=float(ui.editDP_Thresh.text());
        #print ('SET DPTHRESH ' + str(GlobalVars.DPTHRESH) + ';')
        if GlobalVars.isRunning:            
            GlobalVars.ser.write('SET DPTHRESH ' + str(GlobalVars.DPTHRESH) + ';')

def editFFMAX():
        import GlobalVars
    
        GlobalVars.MaxFF=float(ui.editMAXFF.text());
        #print ('SET FFMAX ' + str(GlobalVars.MaxFF) + ';')        
        if GlobalVars.isRunning:            
            GlobalVars.ser.write('SET FF_MAX ' + str(GlobalVars.MaxFF) + ';')

def editFFMIN():
        import GlobalVars
    
        GlobalVars.MinFF=float(ui.editMINFF.text());
        #print ('SET FFMIN ' + str(GlobalVars.MinFF) + ';')        
        if GlobalVars.isRunning:        
            GlobalVars.ser.write('SET FF_MIN ' + str(GlobalVars.MinFF) + ';')
                                     
def editFFreqThresh():
        import GlobalVars
    
        GlobalVars.FreqTHRESH=float(ui.editFREQ_THRESH.text());
        #print ('SET FREQTHRESH ' + str(GlobalVars.FreqTHRESH) + ';')        
        if GlobalVars.isRunning:            
            GlobalVars.ser.write('SET FREQTHRESH ' + str(GlobalVars.FreqTHRESH) + ';')

def WN_OnPressed():
        import GlobalVars

        GlobalVars.WN_ON=ui.WN_OncheckBox.isChecked();
        if GlobalVars.isRunning:        
            GlobalVars.ser.write('SET PLAYWN ' + str(int(GlobalVars.WN_ON)) + ';')

def upDateThresholdButtonPressed():
    import GlobalVars

    GlobalVars.upDateThreshold=ui.upDateThresholdCheckBox.isChecked()
    print GlobalVars.upDateThreshold;

def updateDirFlag():
    import GlobalVars
    GlobalVars.DirFlag=ui.DirFlagCheckBox.isChecked()
    print int(GlobalVars.DirFlag)
    if (GlobalVars.isRunning):
        GlobalVars.ser.write('SET ISDIR ' + str(int(GlobalVars.WN_ON)) + ';')

def HitAboveButtonPressed():
    import GlobalVars
    
    GlobalVars.HitDIR=1
    if GlobalVars.isRunning:    
        GlobalVars.ser.write('SET FREQDIR ' + str(int(GlobalVars.HitDIR)) + ';')

def HitBelowButtonPressed():
    import GlobalVars
    
    GlobalVars.HitDIR=0
    if GlobalVars.isRunning: 
        GlobalVars.ser.write('SET FREQDIR ' + str(int(GlobalVars.HitDIR)) + ';')
            
class MainWindow(QtGui.QMainWindow, Ui_MainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        from numpy import arange, array
        import GlobalVars;        
        
        GlobalVars.isRunning=False;

        GlobalVars.FFT=float(self.NFFTcomboBox.currentText())
        GlobalVars.SamplingRate=float(self.SampleRateComboBox.currentText())
        GlobalVars.FreqTHRESH=0
        GlobalVars.MinFF=3000
        GlobalVars.MaxFF=4500
        GlobalVars.DPTHRESH=1.5
        GlobalVars.HitDIR=0
        GlobalVars.AMP=2800
        GlobalVars.SavePath=".//BirdName"
        GlobalVars.WN_ON=1
        GlobalVars.upDateThreshold=False
        GlobalVars.DirFlag=0
        
        
        GlobalVars.sampleBin=(GlobalVars.SamplingRate/2)/GlobalVars.FFT        
        GlobalVars.template=array([-0.1000,-0.1000,-0.1000,-0.1000,-0.1000,-0.1000,-0.1000,-0.1000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,0.00076923077,-0.10000000,0.0015384615,0.0015384615,0.0046153846,0.0076923077,0.0046153846,0.0053846152,0.0061538462,0.028461538,0.025384616,0.0092307692,0.093846157,0.19307692,0.32076922,0.066153847,0.57076925,0.059230771,0.31846154,0.49076924,0.40384614,0.12307692,0.27076924,0.32461539,0.49000001,0.037692308,0.15307692,0.066923074,0.026923077,0.020769231,0.0038461538,0.0099999998,0.012307692,0.0084615387,0.0084615387,0.0061538462,0.0069230767,0.0023076923,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000,-0.10000000]);
        GlobalVars.UpDateValues(self);

        
        self.templateView.plot(GlobalVars.template,arange(0,GlobalVars.sampleBin*(GlobalVars.FFT/2),GlobalVars.sampleBin))

        self.NFFTcomboBox.setEnabled(False);
        self.SampleRateComboBox.setEnabled(False);
        self.stopButton.setEnabled(False)
        
        self.serialScan.clicked.connect(GetTeensyPorts);
        self.startButton.clicked.connect(startButtonPressed);    
        self.stopButton.clicked.connect(stopButtonPressed);
        self.actionLoad_Config.triggered.connect(loadConfig_ButtonPressed);
        self.actionSave_Config.triggered.connect(saveConfig_ButtonPressed);
        self.editAMPTHRESHOLD.editingFinished.connect(editAMP);    
        self.editMINFF.editingFinished.connect(editFFMIN);
        self.editMAXFF.editingFinished.connect(editFFMAX);
        self.editFREQ_THRESH.editingFinished.connect(editFFreqThresh);        
        self.editDP_Thresh.editingFinished.connect(editDPTHRESH);
        self.FileAndPath_PushButton.clicked.connect(SaveFileButtonPressed)
        self.WN_OncheckBox.clicked.connect(WN_OnPressed)
        self.HitAboveButton.clicked.connect(HitAboveButtonPressed)
        self.HitBelowButton.clicked.connect(HitBelowButtonPressed)
        self.uploadtemplateButton.clicked.connect(updateTemplate)
        self.DirFlagCheckBox.clicked.connect(updateDirFlag)
        self.upDateThresholdCheckBox.clicked.connect(upDateThresholdButtonPressed)

 
if __name__ == "__main__":
    app = QtGui.QApplication(sys.argv)
    ui = MainWindow()
    ui.show()    
    sys.exit(app.exec_())
    window.show()
    sys.exit(app.exec_())
