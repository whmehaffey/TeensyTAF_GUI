

global isRunning
global CurrentPort
global FreqTHRESH
global MinFF
global DPTHRESH
global MaxFF
global HitDIR
global AMP
global sampleBin
global SavePath
global FFT
global SamplingRate
global WN_ON
global upDateThreshold
global DirFlag
global UpDateThresholdPercent
global CatchTrialPercent

def loadConfig(loadfilename):
    from ConfigParser import SafeConfigParser
    import os
    import GlobalVars
    from numpy import arange,array

    parser = SafeConfigParser()
    loadfilename=loadfilename.replace('/','\\')

    print 'C:\\Users\\Mimi-Kao\\Dropbox\\WN_TeensyTAF_Buffered_F32_GUI\\Scratch\\saveconfig.TAFcfg'

    if not parser.read(str(loadfilename)): #.replace('/','\\')):
        raise IOError, 'cannot load'
        
    GlobalVars.MaxFF=float(parser.get('main','GlobalVars.MaxFF'))
    GlobalVars.MinFF=float(parser.get('main','GlobalVars.MinFF'))
    GlobalVars.AMP=float(parser.get('main','GlobalVars.AMP'))
    GlobalVars.DPTHRESH=float(parser.get('main','GlobalVars.DPTHRESH'))
    GlobalVars.FreqTHRESH=float(parser.get('main','GlobalVars.FreqTHRESH'))
    GlobalVars.SavePath=str(parser.get('main','GlobalVars.SavePath'))
    GlobalVars.WN_ON=bool(parser.getboolean('main','GlobalVars.WN_ON'))
    GlobalVars.HitDIR=int(parser.get('main','GlobalVars.HitDIR'))
    GlobalVars.DirFlag=bool(parser.getboolean('main','GlobalVars.DirFlag'))    
    GlobalVars.upDateThreshold=bool(parser.getboolean('main','GlobalVars.upDateThreshold'))
    GlobalVars.UpDateThresholdPercent=int(parser.get('main','UpDateThresholdPercent'))    
    GlobalVars.CatchTrialPercent=int(parser.get('main','CatchTrialPercent'))    
    
    newTemplate=parser.get('template','GlobalVars.template')    
    newTemplate=parser.get('template','GlobalVars.template');

    newTemplate=newTemplate.replace('[','')
    newTemplate=newTemplate.replace(']','')        
    GlobalVars.template= array(newTemplate.split(','), dtype=float)


def saveConfig(savefilename):
    from ConfigParser import SafeConfigParser
    import os
    import GlobalVars
    from numpy import array
             
    SaveFile= open((savefilename),'w')
    
    parser = SafeConfigParser()
    
    parser.add_section('main')
    parser.add_section('template')
    parser.set('main','GlobalVars.MaxFF',str(GlobalVars.MaxFF))
    parser.set('main','GlobalVars.MinFF',str(GlobalVars.MinFF))
    parser.set('main','GlobalVars.AMP',str(GlobalVars.AMP))
    parser.set('main','GlobalVars.DPTHRESH',str(GlobalVars.DPTHRESH))
    parser.set('main','GlobalVars.FreqTHRESH',str(GlobalVars.FreqTHRESH))
    parser.set('main','GlobalVars.SavePath',str(GlobalVars.SavePath));
    parser.set('template','GlobalVars.template',str(list(GlobalVars.template)))
    parser.set('main','GlobalVars.WN_ON',str(GlobalVars.WN_ON));
    parser.set('main','GlobalVars.HitDIR',str(GlobalVars.HitDIR));
    parser.set('main','GlobalVars.upDateThreshold',str(GlobalVars.upDateThreshold));
    parser.set('main','GlobalVars.FFT',str(GlobalVars.FFT))
    parser.set('main','GlobalVars.SamplingRate',str(GlobalVars.SamplingRate))
    parser.set('main','GlobalVars.DirFlag',str(GlobalVars.DirFlag))
    parser.set('main','UpDateThresholdPercent',str(GlobalVars.UpDateThresholdPercent))    
    parser.set('main','CatchTrialPercent',str(GlobalVars.CatchTrialPercent))
    parser.write(SaveFile)    
    SaveFile.close()

def UpDateValues(ui):
    import GlobalVars
    from numpy import arange
    
    ui.editMAXFF.setText((str(GlobalVars.MaxFF)))
    ui.editMINFF.setText((str(GlobalVars.MinFF)))
    ui.editDP_Thresh.setText((str(GlobalVars.DPTHRESH)))
    ui.editFREQ_THRESH.setText((str(GlobalVars.FreqTHRESH)))
    ui.editAMPTHRESHOLD.setText(str(GlobalVars.AMP))
    ui.SaveFilePathLabel.setText(GlobalVars.SavePath)
    ui.WN_OncheckBox.setChecked(GlobalVars.WN_ON)
    ui.upDateThresholdCheckBox.setChecked(bool(GlobalVars.upDateThreshold))
    ui.DirFlagCheckBox.setChecked(bool(GlobalVars.DirFlag))
    ui.templateView.plot(GlobalVars.template,arange(0,GlobalVars.sampleBin*(GlobalVars.FFT/2),GlobalVars.sampleBin))
    ui.CatchPercentspinBox.setValue(GlobalVars.CatchTrialPercent)
    ui.ThresholdUpdateThresholdspinBox.setValue(GlobalVars.UpDateThresholdPercent)

    if (GlobalVars.HitDIR==1):
        ui.HitBelowButton.setChecked(True)
    if (GlobalVars.HitDIR==0):
        ui.HitAboveButton.setChecked(True)

def SendAllToTeensy():
    import GlobalVars


    GlobalVars.ser.write('SET AMP_THRESHOLD ' + str(GlobalVars.FreqTHRESH) + ';')
    GlobalVars.ser.write('SET FF_MIN ' + str(GlobalVars.MinFF) + ';')
    GlobalVars.ser.write('SET FF_MAX ' + str(GlobalVars.MaxFF) + ';')
    GlobalVars.ser.write('SET DPTHRESH ' + str(GlobalVars.DPTHRESH) + ';')
    GlobalVars.ser.write('SET AMP_THRESHOLD ' + str(GlobalVars.AMP) + ';')
    GlobalVars.ser.write('SET FREQTHRESH ' + str(GlobalVars.FreqTHRESH) + ';')
    GlobalVars.ser.write('SET FREQDIR ' + str(int(GlobalVars.HitDIR)) + ';')
    GlobalVars.ser.write('SET PLAYWN ' + str(int(GlobalVars.WN_ON)) + ';')
    GlobalVars.ser.write('SET ISDIR ' + str(int(GlobalVars.DirFlag)) + ';')
    GlobalVars.ser.write('SET PERCENTHITS ' + str(GlobalVars.CatchTrialPercent) + ';')

    
    print 'SET AMP_THRESHOLD ' + str(GlobalVars.FreqTHRESH) + ';'
    print 'SET FF_MIN ' + str(GlobalVars.MinFF) + ';'
    print 'SET FF_MAX ' + str(GlobalVars.MaxFF) + ';'
    print 'SET DPTHRESH ' + str(GlobalVars.DPTHRESH) + ';'
    print 'SET AMP_THRESHOLD ' + str(GlobalVars.AMP) + ';'
    print 'SET FREQTHRESH ' + str(GlobalVars.FreqTHRESH) + ';'
    print 'SET FREQDIR ' + str((GlobalVars.HitDIR)) + ';'
    print 'SET PLAYWN ' + str((GlobalVars.WN_ON)) + ';'
    print 'SET ISDIR ' + str(int(GlobalVars.DirFlag)) + ';'
    print 'SET PERCENTHITS ' + str(GlobalVars.CatchTrialPercent) + ';'
  
    

    

