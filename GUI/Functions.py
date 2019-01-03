
def GetSerialData(savefile):

    import sys
    import os
    import time 
    import serial
    import GlobalVars    

    if (GlobalVars.ser.in_waiting>0):

            line=GlobalVars.ser.readline(GlobalVars.ser.inWaiting()).strip('\n\r');
           # print line
            try:
                if (line[0:3]=="FF "):      #We've found the correct start
                    line=line.lstrip("FF ") #get rid of it
                    splitline=line.split(',')
                    
                    GlobalVars.FF.append(float(splitline[0]))                    
                    GlobalVars.DP.append(float(splitline[1]))
                    GlobalVars.HIT.append(float(splitline[2]))
                    date=time.localtime();

                    savefile.write(line +', '+str(time.time())+','+str(date[0])+','+str(date[1])+','+str(date[2])+','+str(date[3])+'\n');
                    return True
                    
            except:
                print "Bad Alignment"
                return False

    else:
            return False
            

def setAllButtons(ui,state):
        ui.startButton.setEnabled(state)
        ui.stopButton.setEnabled(state)
        ui.serialScan.setEnabled(state)
        ui.Teensy_Com_ComboBox.setEnabled(state)
        ui.uploadtemplateButton.setEnabled(state)
        ui.actionLoad_Config.setEnabled(state)
        ui.actionSave_Config.setEnabled(state)
        ui.FileAndPath_PushButton.setEnabled(state)
        ui.ThresholdUpdateThresholdspinBox.setEnabled(state)
        ui.CatchPercentspinBox.setEnabled(state)
        
