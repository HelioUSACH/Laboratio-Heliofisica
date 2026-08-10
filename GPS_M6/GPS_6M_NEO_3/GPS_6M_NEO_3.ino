#include <SoftwareSerial.h>
#include <TinyGPS++.h>

TinyGPSPlus gps;
SoftwareSerial ss(4, 3);

void setup() {
  Serial.begin(9600);
  ss.begin(9600);
  Serial.println("=== GPS NEO-6M - Análisis NMEA ===");
  Serial.println();
}

void loop() {
  while (ss.available() > 0) {
    char c = ss.read();
    gps.encode(c);
  }
  
  // Mostrar datos NMEA interpretados
  if (gps.location.isUpdated()) {
    Serial.println("--- POSICION ---");
    Serial.print("Lat: "); Serial.println(gps.location.lat(), 6);
    Serial.print("Lng: "); Serial.println(gps.location.lng(), 6);
    
    Serial.println("\n--- SATELITES ---");
    Serial.print("Usados: "); Serial.println(gps.satellites.value());
    
    Serial.println("\n--- MOVIMIENTO ---");
    Serial.print("Velocidad: "); Serial.print(gps.speed.kmph()); Serial.println(" km/h");
    Serial.print("Curso: "); Serial.println(gps.course.deg());
    
    Serial.println("\n--- TIEMPO ---");
    Serial.print("Fecha: ");
    Serial.print(gps.date.day()); Serial.print("/");
    Serial.print(gps.date.month()); Serial.print("/");
    Serial.println(gps.date.year());
    Serial.print("Hora UTC: ");
    Serial.print(gps.time.hour()); Serial.print(":");
    Serial.print(gps.time.minute()); Serial.print(":");
    Serial.println(gps.time.second());
    
    Serial.println("\n==============================\n");
  }
}

//--- POSICION ---
//Lat: -33.450328
//Lng: -70.683685


//--- TIEMPO ---
//Fecha: 10/8/2026
//Hora UTC: 16:16:49

//==============================
//--- SATELITES ---
//Usados: 0

//--- MOVIMIENTO ---
//Velocidad: 0.02 km/h
//Curso: 0.00


