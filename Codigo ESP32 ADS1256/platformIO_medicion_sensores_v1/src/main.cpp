#include <Arduino.h>
#include <SPI.h>
#include <BluetoothSerial.h>

BluetoothSerial BT;


// ADS1256 pin assignment
#define ADS1256_CS                          32
#define ADS1256_DRDY                        33
// ADS1256_PDWN is held HIGH by a 10 kOhm pull-up on the breakout board
// ADS1256_RESET is held HIGH by a 10 kOhm pull-up on the breakout board
#define ADS1256_SCLK                        27
#define ADS1256_MISO                        25
#define ADS1256_MOSI                        26

// ADS1256 SPI configuration
#define ADS1256_SPI_FREQ_HZ                 1500000
#define ADS1256_SPI_BIT_ORDER               MSBFIRST
#define ADS1256_SPI_MODE                    SPI_MODE1

// ADS1256 registers
#define ADS1256_REG_STATUS                  0x00
#define ADS1256_REG_MUX                     0x01
#define ADS1256_REG_ADCON                   0x02
#define ADS1256_REG_DRATE                   0x03
#define ADS1256_REG_IO                      0x04

// ADS1256 register configuration values
#define ADS1256_PGA_1                       0x00  // Programmable gain amplifier: gain = 1
#define ADS1256_MUX_AIN1_AIN0               0x10  // Differential input: AIN1 positive, AIN0 negative
#define ADS1256_DRATE_1000SPS               0xA1  // Data rate: 1000 samples per second

// ADS1256 SPI auxiliary values
#define ADS1256_SPI_DUMMY_BYTE              0x00
#define ADS1256_WREG_SINGLE_REGISTER        0x00

// ADS1256 commands
#define ADS1256_CMD_WAKEUP                  0x00
#define ADS1256_CMD_RDATA                   0x01
#define ADS1256_CMD_RDATAC                  0x03
#define ADS1256_CMD_SDATAC                  0x0F
#define ADS1256_CMD_WREG                    0x50
#define ADS1256_CMD_SELFCAL                 0xF0
#define ADS1256_CMD_SYNC                    0xFC
#define ADS1256_CMD_RESET                   0xFE

// ADS1256 conversion parameters
#define ADS1256_VREF_V                      2.5f
#define ADS1256_PGA_GAIN                    1.0f
#define ADS1256_MAX_POSITIVE_CODE           8388607.0f

// Sensor parameters
#define FORCE_SENSITIVITY_MV_PER_N          1.7631f

// UART2 communication parameters
#define UART2_BAUD_RATE                     115200
#define UART2_RX_PIN                        16
#define UART2_TX_PIN                        17

// Sensor data parameters
#define NUM_PARAMETERS                      1

// Global variables
volatile int adc_ready = 0;
float parameters[NUM_PARAMETERS];


void IRAM_ATTR ads1256_drdy_isr(){
  adc_ready = 1;
}

void ads1256_writeRegister(uint8_t reg, uint8_t value){
  digitalWrite(ADS1256_CS, LOW);                        // Select ADS1256

  SPI.transfer((uint8_t)(ADS1256_CMD_WREG | reg));      // Send WREG command and register address
  SPI.transfer(ADS1256_WREG_SINGLE_REGISTER);           // Write one register
  SPI.transfer(value);                                  // Send register value

  digitalWrite(ADS1256_CS, HIGH);                       // Deselect ADS1256

  delayMicroseconds(5);                                 // Conservative delay between SPI operations
}

void ads1256_sendCommand(uint8_t cmd){
  digitalWrite(ADS1256_CS, LOW);      // Select ADS1256

  SPI.transfer(cmd);                  // Send command

  digitalWrite(ADS1256_CS, HIGH);     // Deselect ADS1256

  delayMicroseconds(5);               // Conservative delay between SPI operations
}

void ads1256_init(){
  // Configure ADS1256 control pins
  pinMode(ADS1256_CS, OUTPUT);
  pinMode(ADS1256_DRDY, INPUT);

  // Deselect ADS1256
  digitalWrite(ADS1256_CS, HIGH);

  // Initialize SPI bus and assign SCLK, MISO, MOSI and CS pins
  SPI.begin(ADS1256_SCLK, ADS1256_MISO, ADS1256_MOSI, ADS1256_CS);

  // Configure SPI interface for ADS1256
  SPI.beginTransaction(SPISettings(ADS1256_SPI_FREQ_HZ, ADS1256_SPI_BIT_ORDER, ADS1256_SPI_MODE));

  // Reset ADS1256
  ads1256_sendCommand(ADS1256_CMD_RESET);
  // Wait until reset and internal initialization are complete
  while (digitalRead(ADS1256_DRDY) == HIGH);

  // Stop continuous data read mode if currently active
  ads1256_sendCommand(ADS1256_CMD_SDATAC);

  // Configure PGA gain = 1
  ads1256_writeRegister(ADS1256_REG_ADCON, ADS1256_PGA_1);

  // Configure differential input: AIN1 positive, AIN0 negative
  ads1256_writeRegister(ADS1256_REG_MUX, ADS1256_MUX_AIN1_AIN0);

  // Configure data rate = 1000 SPS
  ads1256_writeRegister(ADS1256_REG_DRATE, ADS1256_DRATE_1000SPS);

  // Start internal self-calibration
  ads1256_sendCommand(ADS1256_CMD_SELFCAL);
  // Wait until calibration is complete and valid data is available
  while (digitalRead(ADS1256_DRDY) == HIGH);

  // Synchronize the ADC conversion cycle
  ads1256_sendCommand(ADS1256_CMD_SYNC);

  // Conservative delay before WAKEUP
  delayMicroseconds(10);

  // Resume ADC conversions after synchronization
  ads1256_sendCommand(ADS1256_CMD_WAKEUP);

  // Enable continuous data read mode
  ads1256_sendCommand(ADS1256_CMD_RDATAC);

  // Attach DRDY interrupt
  attachInterrupt(ADS1256_DRDY, ads1256_drdy_isr, FALLING);
}

int32_t ads1256_read(){
  uint8_t b[3];
  int32_t value;

  // Wait until a new conversion result is available (not needed when ISR scheme is used)
  //while (digitalRead(ADS1256_DRDY) == HIGH);

  digitalWrite(ADS1256_CS, LOW);      // Select ADS1256

  b[0] = SPI.transfer(ADS1256_SPI_DUMMY_BYTE);
  b[1] = SPI.transfer(ADS1256_SPI_DUMMY_BYTE);
  b[2] = SPI.transfer(ADS1256_SPI_DUMMY_BYTE);

  digitalWrite(ADS1256_CS, HIGH);     // Deselect ADS1256

  // Assemble the 24-bit ADC result
  value = ((int32_t)b[0] << 16) | ((int32_t)b[1] << 8) | b[2];

  // Sign-extend the 24-bit two's-complement value to 32 bits
  if (value & 0x800000) value |= 0xFF000000;

  return value;
}


float ads1256_rawToForce(float sensitivity_mv_per_n, int32_t adc_raw){
  float input_volt = (adc_raw * 2.0f * ADS1256_VREF_V) / (ADS1256_MAX_POSITIVE_CODE * ADS1256_PGA_GAIN);
  float force = (input_volt * 1000.0f) / sensitivity_mv_per_n;

  return force;
}


void uart2_init(int rx_pin, int tx_pin){
  Serial2.begin(UART2_BAUD_RATE, SERIAL_8N1, rx_pin, tx_pin);
}

void uart2_sendParameters(float parameters[]){
  Serial2.print('<');

  for(int i=0; i < NUM_PARAMETERS; i++){
    Serial2.print(parameters[i], 3);
    if (i < NUM_PARAMETERS - 1) Serial2.print(':');
  }

  Serial2.print('>');
}


uint32_t elapsed = 0;
uint32_t sample = 0;
uint32_t sample_period = 0;
uint32_t previous_sample_time = 0;

void setup(){
  // Initialize bluetooth connection
  BT.begin("ESP32_simulador");

  // UART2 initialization
  uart2_init(UART2_RX_PIN, UART2_TX_PIN);

  // ADC initialization
  ads1256_init();
}

void loop(){
  if (adc_ready){
    adc_ready = 0;

    uint32_t start = micros();

    if (previous_sample_time != 0){
      sample_period = start - previous_sample_time;
    }
    previous_sample_time = start;
    
    parameters[0] = ads1256_rawToForce(FORCE_SENSITIVITY_MV_PER_N, ads1256_read());
    uart2_sendParameters(parameters);

    elapsed = micros() - start;

    sample++;
    if (sample==500){
      sample = 0;
      BT.println(parameters[0], 3);
      BT.println(elapsed);
      BT.println(sample_period);
    }
  }
}
