#include <SoftwareSerial.h>
#include <TinyGPS++.h>  // ← Cambio importante

TinyGPSPlus gps;  // ← Nota: "Plus" no "++"
SoftwareSerial ss(4, 3);

void setup() 
{
  Serial.begin(9600);
  ss.begin(9600);

  Serial.println("TinyGPS++ library");
  Serial.println("by Mikal Hart");
  Serial.println();
}

void loop()
{
  while (ss.available() > 0) {
    gps.encode(ss.read());
  }
  
  if (gps.location.isUpdated()) {
    Serial.print("Latitud: ");
    Serial.println(gps.location.lat(), 6);
    Serial.print("Longitud: ");
    Serial.println(gps.location.lng(), 6);
    Serial.print("Satelites: ");
    Serial.println(gps.satellites.value());
    Serial.println();
  }
}