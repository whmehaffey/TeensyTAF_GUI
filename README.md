# TeensyTAF_GUI

TeensyTAF version (https://github.com/whmehaffey/Teensy3.6TAF) w/ Python GUI and a slightly improved audio buffer. 

GUI is pretty simple (set/load config files, plots recent FFs and threshold matches as histograms, and lets you set a few variable on the fly (the buttons left on during running). If buttons are off during running, you can't. It will grab the FFT number and samplign rate from the Teensy, but will not let you set them in the software (you'll have to change the variable in the .ino file and then re-upload it to the teensy). This is just there so that it's saved to a config file. 

On running, saves a config file with all the variables, then writes FF, distance from target, and trial mode (HIT=0 for catch, HIT=1 for hit, and HIT=3 is the flag is set (for, e.g. interleaved DIR trials, so they can be tagged). 

Templates should be in the format in test.TEMPLT, and half the size the FFT window. 

It will also automatically update the FF threshold to maintain 75% hit rates, this value is ratcheted, and will only go up, or down, depending on the direction of training (set with Hit Above/Hit Below). 

Compilation of the Arduino code requires installing the AgileWare circular buffer libraries (Arduino menu, Sketch->Include Library->Manage Library, then search for Circular Buffer and install it). 

Python GUI was written in Python 2.7, and requires the following Python packages (installable through pip): PySerial, PyQT, numpy, pyQTgraph.

-----------------
As before, 
You can order boards at OSH Park:

https://oshpark.com/shared_projects/d7Odnek7

for ~10$ea.

or submit the eagle .brd file in the original commit (https://github.com/whmehaffey/Teensy3.6TAF) yourself.

for 44.1Khz, I recomment overclocking- otherwise it could have issues from time to time. 216MHz seems to work well. To get at it, you may have to edit boards.txt (arduino/hardware/teensy/avr/boards.txt) and uncomment the higher overclock speeds.

Once you have a template, you can recomment export_mags, and uncomment Serial.println(dp) which will export the distance between the template and the current PSD. If you're well-targeted, you should see a sharp peak, which makes it easy to set a threshold (DPTHRESH).

You can also use negative values in the template if you want to penalize spectral information that's present in a syllable you want to avoid, but absent in the target syllable.
