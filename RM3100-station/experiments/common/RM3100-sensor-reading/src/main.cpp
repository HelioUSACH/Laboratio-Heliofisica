#include <Arduino.h>
#include <Wire.h>
#include "esp_timer.h"
#include "config_gen.h"   // RM3100Address, initialCC y monitorSpeed, generados desde config/config.yaml

// I2C address for RM3100 with Pint 2 and Pin 4 set to LOW
//#define RM3100Address 0x20

// Pin definitions
// (IO4 on the ESP32)
#define PIN_DRDY 4

// RM3100 internal register addresses
#define RM3100_REVID_REG  0x36
#define RM3100_POLL_REG   0x00
#define RM3100_CMM_REG    0x01
#define RM3100_STATUS_REG 0x34
#define RM3100_CCX1_REG   0x04
#define RM3100_CCX0_REG   0x05
#define RM3100_TMRC_REG   0x0B


// Options
//#define initialCC 800   // Cycle count: 0 = do not modify (use the current sensor value)
#define singleMode 0    // 0 for continuous measurement mode; 1 for single
#define useDRDYPin 1    // 0 if not using DRDY pin; 1 if using DRDY pin to wait for data

uint8_t revid;
uint16_t cycleCount;

// Forward declarations for functions defined below (required in .cpp files)
uint8_t readReg(uint8_t addr);
void writeReg(uint8_t addr, uint8_t data);
void changeCycleCount(uint16_t newCC);
void processSerialCommand();

void setup() {
  pinMode(PIN_DRDY, INPUT);
  Wire.begin(21, 22);   // SDA=IO21, SCL=IO22 en el ESP32
  Serial.begin(monitorSpeed);
  delay(100);

  // Read and display the revision ID
  revid = readReg(RM3100_REVID_REG);
  Serial.print("REVID = 0x");
  Serial.println(revid, HEX);

  // Update Cycle Count settings
  if (initialCC > 0) {
    changeCycleCount(initialCC);
  }

  // Read and combine cycle count bytes for display
  cycleCount = readReg(RM3100_CCX1_REG);
  cycleCount = (cycleCount << 8) | readReg(RM3100_CCX0_REG);
  Serial.print("Cycle Count = ");
  Serial.println(cycleCount);

  // Configuration parameters (recorded by the capture script)
  Serial.print("TMRC = 0x");
  Serial.println(readReg(RM3100_TMRC_REG), HEX);
  Serial.print("Mode = ");
  Serial.println(singleMode ? "single" : "continuous");
  Serial.print("DRDY pin = ");
  Serial.println(useDRDYPin);

  // Set sensor measurement mode
  if (singleMode) {
    writeReg(RM3100_CMM_REG, 0);   // the single measurement is requested at the start of each loop()
  } else {
    // Enable continuous measurement mode with Alarm functions off
    writeReg(RM3100_CMM_REG, 0x79);
  }
}

void loop() {
  processSerialCommand();

  int32_t x = 0, y = 0, z = 0;
  uint8_t x2, x1, x0, y2, y1, y0, z2, z1, z0;

  // Single mode: request one measurement on all three axes before waiting for it
  if (singleMode) {
    writeReg(RM3100_POLL_REG, 0x70);
  }

  // Wait for data to be ready using the DRDY pin or by polling the status register
  if (useDRDYPin) {
    while (digitalRead(PIN_DRDY) == LOW);
  } else {
    while ((readReg(RM3100_STATUS_REG) & 0x80) != 0x80);
  }
  int64_t t_us = esp_timer_get_time();  // instante de dato listo, antes de la lectura I2C

  // Request measurement results starting at register 0x24
  Wire.beginTransmission(RM3100Address);
  Wire.write(0x24);
  Wire.endTransmission();

  // Request 9 bytes (3 axes × 3 bytes each)
  Wire.requestFrom(RM3100Address, 9);
  if (Wire.available() != 9) {
    return;   // incomplete I2C read: discard this sample instead of printing uninitialized bytes
  }
  x2 = Wire.read();
  x1 = Wire.read();
  x0 = Wire.read();

  y2 = Wire.read();
  y1 = Wire.read();
  y0 = Wire.read();

  z2 = Wire.read();
  z1 = Wire.read();
  z0 = Wire.read();

  // Combine bytes into 24-bit signed integers with proper sign extension
  x = (int32_t)(((uint32_t)x2 << 16) | ((uint32_t)x1 << 8) | (uint32_t)x0);
  if (x2 & 0x80) { x |= 0xFF000000; }

  y = (int32_t)(((uint32_t)y2 << 16) | ((uint32_t)y1 << 8) | (uint32_t)y0);
  if (y2 & 0x80) { y |= 0xFF000000; }

  z = (int32_t)(((uint32_t)z2 << 16) | ((uint32_t)z1 << 8) | (uint32_t)z0);
  if (z2 & 0x80) { z |= 0xFF000000; }

  // Linea CSV: t_us,Xc,Yc,Zc (cuentas LSB)
  char linea[160];
  snprintf(linea, sizeof(linea), "%lld,%ld,%ld,%ld",
           (long long)t_us, (long)x, (long)y, (long)z);

  // Salida por USB
  Serial.println(linea);
}


// Read a byte from a specified register
uint8_t readReg(uint8_t addr) {
  uint8_t data = 0;
  Wire.beginTransmission(RM3100Address);
  Wire.write(addr);
  Wire.endTransmission();
  Wire.requestFrom(RM3100Address, 1);
  if (Wire.available() == 1) {
    data = Wire.read();
  }
  return data;
}

// Write a byte to a specified register
void writeReg(uint8_t addr, uint8_t data) {
  Wire.beginTransmission(RM3100Address);
  Wire.write(addr);
  Wire.write(data);
  Wire.endTransmission();
}

// Update cycle count settings for all three axes
void changeCycleCount(uint16_t newCC) {
  uint8_t CCMSB = (newCC >> 8) & 0xFF;
  uint8_t CCLSB = newCC & 0xFF;
  Wire.beginTransmission(RM3100Address);
  Wire.write(RM3100_CCX1_REG);  // start register (0x04), auto-increments through 0x09
  // X-axis
  Wire.write(CCMSB);
  Wire.write(CCLSB);
  // Y-axis
  Wire.write(CCMSB);
  Wire.write(CCLSB);
  // Z-axis
  Wire.write(CCMSB);
  Wire.write(CCLSB);

  Wire.endTransmission();
}

// Reads commands "CC=<value>\n" from the serial port and applies the new cycle count
void processSerialCommand() {
  if (!Serial.available()) return;

  String cmd = Serial.readStringUntil('\n');
  cmd.trim();
  if (!cmd.startsWith("CC=")) return;

  long newCC = cmd.substring(3).toInt();
  if (newCC <= 0 || newCC > 0xFFFF) {
    Serial.println("Invalid CC");
    return;
  }
  
  
  writeReg(RM3100_CMM_REG, 0);  //Stop continuous mode before reconfiguring
  changeCycleCount((uint16_t)newCC);

  uint16_t cc = readReg(RM3100_CCX1_REG);
  cc = (cc << 8) | readReg(RM3100_CCX0_REG);
  Serial.print("Cycle Count = ");
  Serial.println(cc);   // confirmation: the script saves it as a comment

  if (!singleMode) {
    writeReg(RM3100_CMM_REG, 0x79);   // resume continuous mode
  }
}
