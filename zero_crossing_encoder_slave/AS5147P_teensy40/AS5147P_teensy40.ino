#include "generic/teensy40-AS5147P-rotary-encoder/digital_rotary_encoder.cpp"
#include "generic/main.cpp"

kaepek::DigitalEncoderPinsSPI enc_pins = kaepek::DigitalEncoderPinsSPI();
kaepek::DigitalRotaryEncoderSPI enc;

void setup()
{
  // setup encoder
  enc_pins.csn = 10;
  enc_pins.miso = 12;
  enc_pins.mosi = 11;
  enc_pins.sck = 22;
  enc = kaepek::DigitalRotaryEncoderSPI(enc_pins);
  // setup slave and pass enc reference to slave logic which will init the device "setup"
  slave_input_setup(enc);
}

void loop()
{

}
