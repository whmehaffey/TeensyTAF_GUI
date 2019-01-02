
////////////////////////////////////////////////////////////////////////////////
// FFT/SAMPLING FUNCTIONS
////////////////////////////////////////////////////////////////////////////////


void play_wn() {

  PlayBackCounter = 0;
  digitalWrite(POWER_LED_PIN,HIGH);    
  samplingStop();                          //stop recording

  if (PLAYWN==0) {
    HIT=0;
  }  
  if (HIT==1) {
    digitalWrite(TRIGGER_OUTPUT_PIN, HIGH);  // Trigger the output to be recorded on the second audio channel
    digitalWrite(BNC_TRIGGER_OUTPUT_PIN, HIGH);
    playbackBegin();                         // trigger WN
  }
  delay(50);                               // wait for WN to end- also how long the BNC trigger is high for, for e.g. optogenetics or whatever. 
  
  digitalWrite(BNC_TRIGGER_OUTPUT_PIN, LOW);    //turn off BNC trigger
  digitalWrite(TRIGGER_OUTPUT_PIN, LOW);        //turn off audio trigger
  digitalWrite(POWER_LED_PIN, LOW);        // And power everything else down too.   
  
  samplingBegin();                         // restart the buffering....

  Serial.print("FF ");
  Serial.print(FF);
  Serial.print(','); // print FF to serial so it can be written out. 
  Serial.print(dp);
  Serial.print(',');  
  Serial.println(HIT);         // Output Catch (0) or Hit (1) trial.
  
  ThreshRand = random(1, 100); // choose a random variable

  if (ThreshRand < PercentHits) { //Decide if the next trial will be a hit, or a catch.
    HIT = 1;
  }
  else {
    HIT = 0;
  }

  if (ISDIR) {
    HIT=2;    
  }
}

//////////////////////////////////////
// Performs the parabolic interpolation.
// takes in PeakIDX-1, PeakIDX, PeakIDX+1 magnitudes, the peakIDX,
// and the value in F for each integer idx;
///////////////////////////////////////

float PinterP(float a, float b, float c, int idx, float FBin) {

  float InterP_FF;
  float interpidx;

  interpidx = 0.5 * ((a - c) / (a - (2 * b) + c));
  idx = idx + 1;
  InterP_FF = (idx * FBin) + (interpidx * FBin);

  return InterP_FF;

}

//////////////////
// Calculates Peak FF index
//////////////////

int get_FF_Peaks() {

  int magmax = 0;
  int idxmax = 0;

  // probably not worth arm_max_f32 here.....
  for (int i = FF_minIDX; i <= FF_maxIDX; i++) { //find peak index within the FF window delineated
    if (magnitudes[i] >= magmax) { //find the biggest value
      magmax = magnitudes[i];
      idxmax = i;
    }
  }
  return idxmax; // returns actual index mind you. 
}

// Calcutes the FFT, in this case 32bit floating point (given 12-14 bit data, possibly overkill, but int16 is definately a smoother FFT, especially once normalized, and it's nice to have everything be floats for convenience. 
void CalculateFFT() {

  //    // Run FFT on sample data.

  if (FFT_SIZE == 512) {  ///////////////////////////Lets me use 512, since its not available in cfft_radix4. 512 is a nice mix of accurate and fast..... 
    float complexmagnitudes[FFT_SIZE*2];                // Twice the size of the FFT, since every 2nd number is gonna be complex, but uninportant. 
    arm_cfft_radix4_instance_f32 cfft_inst;             //
    arm_rfft_instance_f32 rfft_inst; // create structure on ARM processor
    arm_rfft_init_f32(&rfft_inst, &cfft_inst, FFT_SIZE, 0, 1); // initialize,
    if (status == 0){      
          arm_rfft_f32(&rfft_inst, fftbuffer, complexmagnitudes); // and calculate the FFT.
    }
    arm_cmplx_mag_f32(complexmagnitudes, magnitudes , FFT_SIZE); // doesnt have to be squared. ampl_cmplx_mag_f32 would probably work fine too. 
    
  }
  else {  ////////support for 256 and 1024 sample. 
    arm_cfft_radix4_instance_f32 fft_inst; // create structure on ARM processor
    arm_cfft_radix4_init_f32(&fft_inst, FFT_SIZE, 0, 1); // initialize,
    if (status == 0){
        arm_cfft_radix4_f32(&fft_inst, fftbuffer); // and calculate the FFT.
    }
   
   // Calculate the FFT magnitudes
    arm_cmplx_mag_f32(fftbuffer, magnitudes, FFT_SIZE);
  }

  for (int i = 0; i <= FF_discardIDX; i++) { /// Get rid of low-frequency stuff by setting it to zero. 
    magnitudes[i] = 0;                       // This also _really_ helps with ScaleAndCompare, since the normalization is to a useful range.
  }

}

////////////////////////////////////////////
// Normalize FFT Magnitudes, and then compare to template, returns the dot product.
/////////////////////////////////////////////

float ScaleAndCompareToTemplate() {

  float scaledmags[TEMPLT_SIZE];
  float scalefactor;
  uint32_t peakmagidx;
  float dotprod;

  arm_max_f32(magnitudes,FFT_SIZE,&scalefactor,&peakmagidx);//find the max; 
  scalefactor=1/scalefactor; // for vector multiplation below 

  arm_scale_f32(magnitudes, scalefactor, scaledmags, TEMPLT_SIZE); // and normalize.
  arm_dot_prod_f32(scaledmags, templt, TEMPLT_SIZE, &dotprod); // and calculate the dot product

  return dotprod;
}

////////////////////////////////////////////////////////////////////////////////
// SAMPLING FUNCTIONS
////////////////////////////////////////////////////////////////////////////////


// Starts the timer. If you run things that conflict with this interrupt, you'll crash the processor.
void samplingBegin() {
  // Reset sample buffer position and start callback at necessary rate.
  sampleCounter = 0;
  buffer.clear();
  samplingTimer.begin(samplingCallback, 1000000 / SAMPLE_RATE_HZ); ///// This never really stops, except for WN playback....
  while (not buffer.isFull()) {
    //wait for it to fill.... 
  }
}

// pretty self-evident.
void samplingStop() {
  samplingTimer.end();
}


// plays WN to the DAC output, at the appropriate sampling frequency. 
void playbackCallBack() {
  analogWrite(AUDIO_OUTPUT_PIN, wn[PlayBackCounter]);
  PlayBackCounter++;
  if (PlayBackCounter > 1024) {
    samplingStop();
  }
}

// DO playback at Sampling_Frequency in case you want notched noise or something....
void playbackBegin() {
  // Reset sample buffer position and start callback at necessary rate.
  // Allows for notched white noise if necessary...
  PlaybackCounter = 0;
  samplingTimer.begin(playbackCallBack, 1000000 / SAMPLE_RATE_HZ);
}

// Get the last FFT_SIZE samples, and format them for the ARM FFT functions 
void getsamples() {

  if (buffer.isFull()) {
      
    if (FFT_SIZE==256 or FFT_SIZE==1024) {
      for (int i = 0; i <= ((FFT_SIZE * 2) - 2); i = i + 2) { // go through, get the last FFT_Size samples, and put them into a structure for ARM FFT calculation.
        fftbuffer[i] = buffer[i/2]; // // Sampled in place. Avoid buffer.shift, as it destroys data in the array. 
        fftbuffer[i + 1] = 0; 
      }
    } // end of cffts
  
   if (FFT_SIZE==512) {
     for (int i = 0; i <= (FFT_SIZE-1); i++) { // go through, get the last FFT_Size samples, and put them into a structure for ARM FFT calculation.
      fftbuffer[i] = buffer[i];           //Sampled in place. Avoid buffer.shift, as it destroys data in the array. 
     }
    } //end of rfft 
  } // end Buffer.isfull
}

// runs at SAMPLING_FREQUENCY_HZ, to get regular audio inputs. Adds to circular buffer (buffer), and centers around zero. 

void samplingCallback() {

  // Read from the ADC and store the sample data
  float sample = (float)(analogRead(AUDIO_INPUT_PIN));

  sample=sample-32768;  // despite cast to float, the range is still from int_16t. 
  buffer.push(sample);
}





