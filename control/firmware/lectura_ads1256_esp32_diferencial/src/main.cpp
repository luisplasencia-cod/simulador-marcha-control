// ADS1256 leido por un ESP32 dedicado (SOLO lectura, no mueve motores) y transmitido por
// UART2 al Raspberry Pi. Origen: C:\Users\chees\Downloads\platformIO_medicion_sensores_v1.zip
// (Luis, 2026-11-17: "ya probado antes y funcionaba mejor" -- SIN reporte de latencia medido
// en el repo, no confirmado con datos). Copiado aqui tal cual, con UN SOLO cambio de codigo:
//
//   linea 54: FORCE_SENSITIVITY_MV_PER_N  1.7631f -> 1.7665f
//   (escala confirmada del AMTI el 2026-11-02/05; NO depende del cableado del ADC, del MUX
//   diferencial AIN1/AIN0 original no se toco nada -- ya coincide con el esquema decidido).
//
// Esquema completo (pines, protecciones, por que diferencial):
//   esquemas/amti_ads1256_rpi/salida/esquema_protecciones_ads1256.png
// Decision y contexto: CLAUDE.md, entrada (2026-11-17).
//
// NADA DE ESTO PROBADO EN HARDWARE TODAVIA (sin RPi ni ESP32 en esta sesion).
//
// CAMBIOS 2026-11-18 (diagnostico; el camino SPI -> "<valor>" por UART2 NO se toco):
//  - Las esperas de DRDY en el arranque tenian "while(DRDY==HIGH);" sin limite: con el ADC
//    mal cableado o sin 5 V el ESP32 se quedaba colgado EN SILENCIO. Ahora esperan 1 s maximo,
//    imprimen el error por USB y reintentan el arranque cada 2 s.
//  - Tras configurar, se releen STATUS/MUX/ADCON/DRATE y se comparan con lo escrito (detecta el
//    fallo "no devolvio lo escrito" visto en el RPi el 2026-11-05/10).
//  - Por el USB (Serial, 115200) sale el motivo del ultimo reinicio (detecta brown-out) y una
//    linea por segundo: muestras, media/desviacion/min/max de Fz, periodo maximo, muestras
//    perdidas, lecturas en cero exacto y saturadas. Antes no salia nada por USB.
//  - Entorno "sin_bt" (platformio.ini) para comparar el ruido sin la radio Bluetooth.
//  - Por el USB tambien sale "F,<valor>" a 100/s (1 de cada 10 muestras) para el visor
//    en vivo de la laptop (pruebas/visor_fz_esp32_usb.py). El RPi no usa el USB.
#include <Arduino.h>
#include <SPI.h>
#include <esp_system.h>
#ifndef SIN_BT
#include <BluetoothSerial.h>
BluetoothSerial BT;
#endif


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
#define FORCE_SENSITIVITY_MV_PER_N          1.7665f  // CORREGIDO 2026-11-17 (era 1.7631f): escala real del AMTI

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

bool esperar_drdy_bajo(uint32_t timeout_ms){
  uint32_t t0 = millis();
  while (digitalRead(ADS1256_DRDY) == HIGH){
    if (millis() - t0 > timeout_ms) return false;
  }
  return true;
}

uint8_t ads1256_readRegister(uint8_t reg){
  digitalWrite(ADS1256_CS, LOW);
  SPI.transfer((uint8_t)(0x10 | reg));   // RREG
  SPI.transfer(0x00);                    // un registro
  delayMicroseconds(10);                 // t6 >= 50 periodos de CLKIN (6.5 us a 7.68 MHz)
  uint8_t v = SPI.transfer(ADS1256_SPI_DUMMY_BYTE);
  digitalWrite(ADS1256_CS, HIGH);
  delayMicroseconds(5);
  return v;
}

bool verificar_registro(const char* nombre, uint8_t reg, uint8_t esperado, uint8_t mascara){
  uint8_t v = ads1256_readRegister(reg);
  bool ok = (v & mascara) == (esperado & mascara);
  Serial.printf("  %-6s leido 0x%02X esperado 0x%02X -> %s\n", nombre, v, esperado, ok ? "OK" : "MAL");
  return ok;
}

bool spi_iniciado = false;

// Devuelve false si algo fallo (se reintenta desde setup); antes se colgaba sin avisar.
bool ads1256_init(){
  // Configure ADS1256 control pins
  pinMode(ADS1256_CS, OUTPUT);
  pinMode(ADS1256_DRDY, INPUT);

  // Deselect ADS1256
  digitalWrite(ADS1256_CS, HIGH);

  if (!spi_iniciado){
    // Initialize SPI bus and assign SCLK, MISO, MOSI and CS pins
    SPI.begin(ADS1256_SCLK, ADS1256_MISO, ADS1256_MOSI, ADS1256_CS);

    // Configure SPI interface for ADS1256
    SPI.beginTransaction(SPISettings(ADS1256_SPI_FREQ_HZ, ADS1256_SPI_BIT_ORDER, ADS1256_SPI_MODE));
    spi_iniciado = true;
  }

  // SDATAC antes de RESET: si el chip quedo en lectura continua (reintento), sale de ahi
  ads1256_sendCommand(ADS1256_CMD_SDATAC);

  // Reset ADS1256
  ads1256_sendCommand(ADS1256_CMD_RESET);
  // Wait until reset and internal initialization are complete
  if (!esperar_drdy_bajo(1000)){
    Serial.println("ERROR: DRDY no bajo tras RESET en 1 s. Revisar: 5 V en la placa, PDWN = 3.3 V, DRDY -> GPIO33, GND comun.");
    return false;
  }

  // Stop continuous data read mode if currently active
  ads1256_sendCommand(ADS1256_CMD_SDATAC);

  // Configure PGA gain = 1
  ads1256_writeRegister(ADS1256_REG_ADCON, ADS1256_PGA_1);

  // Configure differential input: AIN1 positive, AIN0 negative
  ads1256_writeRegister(ADS1256_REG_MUX, ADS1256_MUX_AIN1_AIN0);

  // Configure data rate = 1000 SPS
  ads1256_writeRegister(ADS1256_REG_DRATE, ADS1256_DRATE_1000SPS);

  // Relectura: si el SPI no funciona (cable, 100 ohm, MISO suelto) aqui sale MAL.
  // STATUS: solo se compara el ID del chip (nibble alto = 3).
  bool regs_ok = true;
  regs_ok &= verificar_registro("STATUS", ADS1256_REG_STATUS, 0x30, 0xF0);
  regs_ok &= verificar_registro("MUX", ADS1256_REG_MUX, ADS1256_MUX_AIN1_AIN0, 0xFF);
  regs_ok &= verificar_registro("ADCON", ADS1256_REG_ADCON, ADS1256_PGA_1, 0x07);
  regs_ok &= verificar_registro("DRATE", ADS1256_REG_DRATE, ADS1256_DRATE_1000SPS, 0xFF);
  if (!regs_ok){
    Serial.println("ERROR: registros no coinciden. Revisar SCLK->GPIO27, DIN<-GPIO26, DOUT->GPIO25, CS<-GPIO32 y las R de 100 ohm.");
    return false;
  }

  // Start internal self-calibration
  ads1256_sendCommand(ADS1256_CMD_SELFCAL);
  // Wait until calibration is complete and valid data is available
  if (!esperar_drdy_bajo(1000)){
    Serial.println("ERROR: DRDY no bajo tras SELFCAL en 1 s.");
    return false;
  }

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
  return true;
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

const char* nombre_reinicio(esp_reset_reason_t r){
  switch (r){
    case ESP_RST_POWERON:  return "POWERON (encendido normal)";
    case ESP_RST_EXT:      return "EXT (pin EN)";
    case ESP_RST_SW:       return "SW (software)";
    case ESP_RST_PANIC:    return "PANIC (fallo del programa)";
    case ESP_RST_INT_WDT:
    case ESP_RST_TASK_WDT:
    case ESP_RST_WDT:      return "WATCHDOG";
    case ESP_RST_BROWNOUT: return "BROWNOUT (cayo la alimentacion del ESP32)";
    default:               return "otro";
  }
}

// Estadisticas por segundo (solo para el resumen por USB)
uint32_t est_n = 0, est_perdidas = 0, est_ceros = 0, est_saturadas = 0;
uint32_t est_max_periodo = 0, est_max_elapsed = 0;
double est_suma = 0, est_suma2 = 0;
float est_min = 1e9, est_max = -1e9;
uint32_t t_resumen = 0;

void setup(){
  Serial.setTxBufferSize(1024);   // el resumen no debe bloquear el lazo de lectura
  Serial.begin(115200);
  delay(200);
  Serial.println();
  Serial.println("=== ESP32 lectura ADS1256 (diferencial AIN1-AIN0) ===");
  Serial.printf("Ultimo reinicio: %s\n", nombre_reinicio(esp_reset_reason()));
#ifdef SIN_BT
  Serial.println("Bluetooth: APAGADO (entorno sin_bt)");
#else
  // Initialize bluetooth connection
  BT.begin("ESP32_simulador");
  Serial.println("Bluetooth: encendido (ESP32_simulador)");
#endif

  // UART2 initialization
  uart2_init(UART2_RX_PIN, UART2_TX_PIN);

  // ADC initialization (reintenta en vez de colgarse en silencio)
  while (!ads1256_init()){
    Serial.println("Reintento de arranque del ADS1256 en 2 s...");
    delay(2000);
  }
  Serial.println("ADS1256 OK. Columnas por segundo:");
  Serial.println("t_s,n,fz_media,fz_sd,fz_min,fz_max,periodo_max_us,perdidas,ceros,saturadas,elapsed_max_us");
  t_resumen = millis();
}

void loop(){
  if (adc_ready){
    adc_ready = 0;

    uint32_t start = micros();

    if (previous_sample_time != 0){
      sample_period = start - previous_sample_time;
    }
    previous_sample_time = start;

    int32_t raw = ads1256_read();
    parameters[0] = ads1256_rawToForce(FORCE_SENSITIVITY_MV_PER_N, raw);
    uart2_sendParameters(parameters);

    elapsed = micros() - start;

    float f = parameters[0];
    est_n++;
    est_suma += f; est_suma2 += (double)f * f;
    if (f < est_min) est_min = f;
    if (f > est_max) est_max = f;
    if (raw == 0) est_ceros++;
    if (raw >= 0x7FFFFF || raw <= -0x800000) est_saturadas++;
    if (sample_period > est_max_periodo) est_max_periodo = sample_period;
    if (sample_period > 1500) est_perdidas++;   // a 1000 SPS el periodo es 1000 us
    if (elapsed > est_max_elapsed) est_max_elapsed = elapsed;

    // Copia de Fz por USB a 100/s (1 de cada 10) para el visor de la laptop
    // (pruebas/visor_fz_esp32_usb.py). No toca el paquete del UART2.
    static uint8_t div_usb = 0;
    if (++div_usb >= 10){
      div_usb = 0;
      Serial.printf("F,%.3f\n", f);
    }

#ifndef SIN_BT
    sample++;
    if (sample==500){
      sample = 0;
      BT.println(parameters[0], 3);
      BT.println(elapsed);
      BT.println(sample_period);
    }
#endif
  }

  if (millis() - t_resumen >= 1000){
    t_resumen += 1000;
    if (est_n == 0){
      Serial.printf("%lu,0,,,,,,,,,,ALERTA: 0 muestras en 1 s (DRDY no baja: ADC caido o sin 5 V)\n", millis() / 1000);
    } else {
      double media = est_suma / est_n;
      double var = est_suma2 / est_n - media * media;
      Serial.printf("%lu,%lu,%.3f,%.3f,%.3f,%.3f,%lu,%lu,%lu,%lu,%lu\n",
                    millis() / 1000, est_n, media, var > 0 ? sqrt(var) : 0.0, est_min, est_max,
                    est_max_periodo, est_perdidas, est_ceros, est_saturadas, est_max_elapsed);
    }
    est_n = est_perdidas = est_ceros = est_saturadas = 0;
    est_max_periodo = est_max_elapsed = 0;
    est_suma = est_suma2 = 0;
    est_min = 1e9; est_max = -1e9;
  }
}
