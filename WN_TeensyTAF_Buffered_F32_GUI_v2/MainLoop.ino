//Main Loop  should run every ~1ms for 1024 float_32
void loop() {
      
  parserLoop();

  //float timea = micros();

  getsamples(); // not perfect, but I can't point to a volatile float, and I don't want to make the samples non-volatile.
  arm_rms_f32(fftbuffer, FFT_SIZE, &RUNNING_AMP); //RMS of the buffer. Since there's a 'complex' component of all zeros, it still works fine.

  //Serial.println(RUNNING_AMP);
  if (RUNNING_AMP > AMP_THRESHOLD) {

    AboveThresh++;
  }
  else {
    AboveThresh = 0;
  }

  if (AboveThresh > AMPLITUDE_THRESHOLD_DURATION) {   // e.g. has there been sound?

    CalculateFFT(); // Galculate the FFT, results are cast to the magnitudes variable.

    export_mags(); //For testing of FFT- will sent out 0:FFT_SIZE/2 from the calculated FFT magnitudes. 
    dp = ScaleAndCompareToTemplate();
  //Serial.println(dp); // This will export the calculated distance between the current PSD and the template. If you're exporting PSDs, you probably want this commented out. 

    if ((dp >= DPTHRESH)) { //// Are we above the template match threshold?
      fft_threshcounter++; // if we are, increment the counter so we can decide how many sequenctial template matches we went before we trigger.
    }
    else {
      fft_threshcounter = 0; // reset the FFT_threshold counter.
    }

    
    if (fft_threshcounter >= TEMPLATE_MATCH_DURATION) { ////////// How long has the template match been? If it's been enough samples above the FFT match threshold, then trigger!

      peakIDX = get_FF_Peaks();     ////// Find the peak IDX in the window of interest defined by FF_MIN and FF_MAX
      FF = PinterP(magnitudes[peakIDX - 1], magnitudes[peakIDX], magnitudes[peakIDX + 1], peakIDX, FFT_Bin); // Parabolic Interpolation for more accuate FF calculation.
  
      if ((FF < FF_MAX) && (FF > FF_MIN)) { // If the result isn't gibberish (e.g. as long as the FF returned is inside of the window it should be in, the peak isn't the first or last or anything stupid. 

        if ((FREQDIR==0) && FF<FREQTHRESH) { /////// Are we below the Frequency Trials? Upshifts... 
                play_wn();
                delay(150);         // optional for slow syllables that you don't want to hit twice.
        } // 
        if ((FREQDIR==1) && FF>FREQTHRESH) { /////// Are we above the Frequency Trials forDownshifts...
                play_wn();
                delay(150);         // optional for slow syllables that you don't want to hit twice.
        } // 
//        else {
//               HIT=3;
//               play_wn();
//               delay(150);
//        }
      } // end of sanity check for peak FF.
    } //end of template match triggered portions
  } // end of amplitude triggered portion

} // end Main Loop
