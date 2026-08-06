#include <Arduino.h>
#include <Wire.h>

#define RM3100_ADDR   0x20   // SSN y S0 a GND
//
// Registros
#define REG_POLL      0x00
#define REG_CCX_MSB   0x04
#define REG_STATUS    0x34
#define REG_REVID     0x36
#define REG_MX        0x24

// Escribe un byte en un registro
void writeReg(uint8_t reg, uint8_t val) {
  Wire.beginTransmission(RM3100_ADDR);
  Wire.write(reg);
  Wire.write(val);
  Wire.endTransmission();
}

// Lee un registro de 1 byte
uint8_t readReg(uint8_t reg) {
  Wire.beginTransmission(RM3100_ADDR);
  Wire.write(reg);
  Wire.endTransmission();
  Wire.requestFrom((uint8_t)RM3100_ADDR, (uint8_t)1);
  return Wire.read();
}

// Convierte 3 bytes en complemento a 2 (24 bits) a entero con signo
long toSigned24(uint8_t b2, uint8_t b1, uint8_t b0) {
  long v = ((long)b2 << 16) | ((long)b1 << 8) | b0;
  if (v & 0x800000) v |= 0xFF000000;  // extension de signo
  return v;
}

void setup() {
  Serial.begin(9600);
  Wire.begin();
  delay(100);

  // Verifica comunicacion: REVID tipico del RM3100 es 0x22
  uint8_t rev = readReg(REG_REVID);
  Serial.print("REVID: 0x");
  Serial.println(rev, HEX);
  if (rev == 0x00 || rev == 0xFF) {
    Serial.println("Sin respuesta: revisa I2CEN=HIGH, alimentacion, pull-ups y cableado.");
  }

  // Cycle counts por defecto (200) son suficientes para la prueba.
}

void loop() {
  // Lanza una medicion unica en los 3 ejes (PMX,PMY,PMZ)
  writeReg(REG_POLL, 0x70);

  // Espera a que el dato este listo (bit 7 de STATUS)
  unsigned long t0 = millis();
  while (!(readReg(REG_STATUS) & 0x80)) {
    if (millis() - t0 > 100) {
      Serial.println("Timeout: no llego DRDY.");
      break;
    }
  }

  // Lee 9 bytes desde MX (X, Y, Z, 3 bytes cada uno)
  Wire.beginTransmission(RM3100_ADDR);
  Wire.write(REG_MX);
  Wire.endTransmission();
  Wire.requestFrom((uint8_t)RM3100_ADDR, (uint8_t)9);

  uint8_t d[9];
  for (int i = 0; i < 9 && Wire.available(); i++) d[i] = Wire.read();

  long x = toSigned24(d[0], d[1], d[2]);
  long y = toSigned24(d[3], d[4], d[5]);
  long z = toSigned24(d[6], d[7], d[8]);

  Serial.print("X="); Serial.print(x);
  Serial.print("  Y="); Serial.print(y);
  Serial.print("  Z="); Serial.println(z);

  delay(500);
}