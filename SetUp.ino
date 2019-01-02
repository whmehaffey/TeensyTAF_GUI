
////////////////////////////////////////////////////////////////////////////////
// MAIN SKETCH FUNCTIONS
////////////////////////////////////////////////////////////////////////////////

void setup() {
  // Set up serial port

  Serial.begin(9600);

  //output LEDs for playback observations.
  pinMode(TRIGGER_OUTPUT_PIN, OUTPUT);
  digitalWrite(TRIGGER_OUTPUT_PIN, LOW);
  pinMode(POWER_LED_PIN, OUTPUT);
  digitalWrite(POWER_LED_PIN, HIGH);
  pinMode(BNC_TRIGGER_OUTPUT_PIN, OUTPUT);
  digitalWrite(BNC_TRIGGER_OUTPUT_PIN, LOW);


  // Set up ADC and audio input.
  pinMode(AUDIO_INPUT_PIN, INPUT);
  analogReadResolution(ANALOG_READ_RESOLUTION);
  analogReadAveraging(ANALOG_READ_AVERAGING);
  // Set up DAC for audio putput.
  analogWriteResolution(14);

  // Begin sampling audio
 // samplingBegin();
  isRunning=false;
 // delay(250); ///////////wait to fill the buffer....
}
