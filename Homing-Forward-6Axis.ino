#include <Arduino.h>
#include <ESP32Servo.h> 

// =================================================================================
// ----------------------- 1. ส่วนตั้งค่าฮาร์ดแวร์ (CONFIGURATION) -----------------------
// =================================================================================

#define RXD2 16       
#define TXD2 17       
#define AXIS5_PIN 13  
#define GRIPPER_PIN 12 

// --- Robot Parameters ---
const float GEAR_RATIO = 30.0;
const float PULSE_PER_REV = 3200.0 * GEAR_RATIO; 
const float PULSE_PER_DEGREE = PULSE_PER_REV / 360.0;

// --- Homing Config (ทิศทาง) ---
const boolean HOME_DIR[4] = {false, false, false, true}; 

// --- Home Offsets (จุด Set Zero) ---
const float HOME_OFFSET[4] = {38.0, -90.0, 90.0, -185.0}; 

// --- Speed Settings ---
const uint8_t  HOMING_SPEED = 20; 
uint16_t RUN_SPEED    = 20; // ความเร็วปกติ
uint8_t  RUN_ACC      = 20;  // อัตราเร่งปกติ

// =================================================================================
// ----------------------- 2. ตัวแปร Global ------------------------------------------
// =================================================================================

Servo axis5;   
Servo gripper; 
float currentAngles[4] = {0, 0, 0, 0}; // ตัวแปรจำตำแหน่งปัจจุบัน

// =================================================================================
// ----------------------- 3. SETUP & LOOP -----------------------------------------
// =================================================================================

// ประกาศฟังก์ชันล่วงหน้า
void setup_hardware();
void performHomingRoutine();
void runHomingSequence(uint8_t id);
void sendRelativeMove(uint8_t id, float degree, uint16_t speed, uint8_t acc);
void waitForStop(uint8_t id);
void setCurrentAxisZero(uint8_t id);
int checkStatus(uint8_t id);
void configureMotorHoming(uint8_t id, boolean dir);
void sendRawCommand(uint8_t id, uint8_t cmd, uint8_t* data, uint8_t len);
void moveToPosition(float t1, float t2, float t3, float t4, int roll, int grip);
void calcFK_15Matrix(float t1, float t2, float t3, float t4, float t5); // FK 15 Matrix

void setup() {
  setup_hardware(); 
  Serial.begin(38400); // แนะนำ 115200 เพื่อความรวดเร็ว
  delay(1000);
  
  Serial.println("\n\n============================================");
  Serial.println("   ROBOT ARM MASTER (Universal Parse + 15 Matrix FK)");
  Serial.println("============================================");

  // 1. Config Homing Parameters
  configureMotorHoming(1, HOME_DIR[0]); delay(50);
  configureMotorHoming(2, HOME_DIR[1]); delay(50);
  configureMotorHoming(3, HOME_DIR[2]); delay(50);
  // configureMotorHoming(4, HOME_DIR[3]); delay(50); // แกน 4 Manual

  // 2. Start Homing Routine
  performHomingRoutine(); 

  // 3. Init Servos
  axis5.write(90);    
  gripper.write(90);  

  Serial.println("\n--- SYSTEM READY ---");
  Serial.println("Command Format: J1,J2,J3,J4,Roll,Grip (Supports floats)");
  
  calcFK_15Matrix(0, 0, 0, 0, 0);
}

void loop() {
  // รอรับคำสั่งผ่าน Serial Monitor / Python
  if (Serial.available() > 0) {
    String input = Serial.readStringUntil('\n');
    input.trim(); // ตัดช่องว่างหัวท้าย

    float t1, t2, t3, t4;
    float roll_f, grip_f; // [แก้ไข] รับค่าเป็น float ทั้งหมดเพื่อให้เหมือนแกน 1-4
    
    // ใช้ %f กับทุกตัวแปร
    int parsed = sscanf(input.c_str(), "%f,%f,%f,%f,%f,%f", &t1, &t2, &t3, &t4, &roll_f, &grip_f);
    
    if (parsed == 6) {
      // แปลง float เป็น int ตอนส่งเข้าฟังก์ชัน Servo
      int roll = (int)roll_f;
      int grip = (int)grip_f;

      Serial.printf("\nMoving to: %.1f, %.1f, %.1f, %.1f | Roll:%d Grip:%d\n", t1, t2, t3, t4, roll, grip);
      
      // สั่งเคลื่อนที่
      moveToPosition(t1, t2, t3, t4, roll, grip);
      
      // คำนวณ FK (ใช้ 15 Matrix)
      calcFK_15Matrix(t1, t2, t3, t4, roll_f); // ส่ง roll ไปคำนวณด้วยถ้าต้องการ
      
    } else {
      // เผื่อกรณีส่งมาแค่ 4 ตัว (Stepper Only)
      if (sscanf(input.c_str(), "%f,%f,%f,%f", &t1, &t2, &t3, &t4) == 4) {
          Serial.println("Warning: Servo/Gripper not specified, using default.");
          moveToPosition(t1, t2, t3, t4, 90, 90);
          calcFK_15Matrix(t1, t2, t3, t4, 0);
      } else {
          Serial.println("Error: Invalid Format! Use 6 values (floats allowed)");
      }
    }
  }
}

// =================================================================================
// ----------------------- 4. ส่วนควบคุมการเคลื่อนที่ (MOVEMENT) -----------------------
// =================================================================================

void moveToPosition(float t1, float t2, float t3, float t4, int roll, int grip) {
  // 1. สั่ง Servo
  axis5.write(roll);
  gripper.write(grip);

  // 2. สั่ง Stepper
  float targets[4] = {t1, t2, t3, t4};
  
  for(int i=0; i<4; i++) {
    float delta = targets[i] - currentAngles[i];
    if (abs(delta) > 0.1) {
      sendRelativeMove(i+1, delta, RUN_SPEED, RUN_ACC);
      currentAngles[i] = targets[i]; 
    }
  }
}

// =================================================================================
// ----------------------- 5. KINEMATICS (15 MATRIX) -------------------------------
// =================================================================================

// Helper Functions
void mulMat(float A[4][4], float B[4][4], float R[4][4]) {
  float temp[4][4];
  for(int i=0; i<4; i++) {
    for(int j=0; j<4; j++) {
      temp[i][j] = 0;
      for(int k=0; k<4; k++) temp[i][j] += A[i][k] * B[k][j];
    }
  }
  for(int i=0; i<4; i++) for(int j=0; j<4; j++) R[i][j] = temp[i][j];
}
void getRotZ(float theta, float M[4][4]) {
  float r = radians(theta); float c = cos(r); float s = sin(r);
  M[0][0]=c; M[0][1]=-s; M[0][2]=0; M[0][3]=0;
  M[1][0]=s; M[1][1]=c;  M[1][2]=0; M[1][3]=0;
  M[2][0]=0; M[2][1]=0;  M[2][2]=1; M[2][3]=0;
  M[3][0]=0; M[3][1]=0;  M[3][2]=0; M[3][3]=1;
}
void getRotX(float alpha, float M[4][4]) {
  float r = radians(alpha); float c = cos(r); float s = sin(r);
  M[0][0]=1; M[0][1]=0;  M[0][2]=0;  M[0][3]=0;
  M[1][0]=0; M[1][1]=c;  M[1][2]=-s; M[1][3]=0;
  M[2][0]=0; M[2][1]=s;  M[2][2]=c;  M[2][3]=0;
  M[3][0]=0; M[3][1]=0;  M[3][2]=0;  M[3][3]=1;
}
void getTransZ(float d, float M[4][4]) {
  M[0][0]=1; M[0][1]=0; M[0][2]=0; M[0][3]=0;
  M[1][0]=0; M[1][1]=1; M[1][2]=0; M[1][3]=0;
  M[2][0]=0; M[2][1]=0; M[2][2]=1; M[2][3]=d;
  M[3][0]=0; M[3][1]=0; M[3][2]=0; M[3][3]=1;
}
void getTransX(float a, float M[4][4]) {
  M[0][0]=1; M[0][1]=0; M[0][2]=0; M[0][3]=a;
  M[1][0]=0; M[1][1]=1; M[1][2]=0; M[1][3]=0;
  M[2][0]=0; M[2][1]=0; M[2][2]=1; M[2][3]=0;
  M[3][0]=0; M[3][1]=0; M[3][2]=0; M[3][3]=1;
}

void calcFK_15Matrix(float t1, float t2, float t3, float t4, float t5) {
  // Identity Init
  float T[4][4] = { {1,0,0,0}, {0,1,0,0}, {0,0,1,0}, {0,0,0,1} };
  float M[4][4];

  // 1. Rz(t1)
  getRotZ(t1, M); mulMat(T, M, T);
  // 2. Tz(133.5)
  getTransZ(133.5, M); mulMat(T, M, T);
  // 3. Rx(90)
  getRotX(90, M); mulMat(T, M, T);
  // 4. Rz(90)
  getRotZ(90, M); mulMat(T, M, T);
  // 5. Rz(t2)
  getRotZ(t2, M); mulMat(T, M, T);
  // 6. Tx(120.5)
  getTransX(120.5, M); mulMat(T, M, T);
  // 7. Rx(180)
  getRotX(180, M); mulMat(T, M, T);
  // 8. Rz(t3)
  getRotZ(t3, M); mulMat(T, M, T);
  // 9. Tx(101)
  getTransX(101, M); mulMat(T, M, T);
  // 10. Rx(180)
  getRotX(180, M); mulMat(T, M, T);
  // 11. Rz(t4)
  getRotZ(t4, M); mulMat(T, M, T);
  // 12. Rx(90)
  getRotX(90, M); mulMat(T, M, T);
  // 13. Tz(75.84)
  getTransZ(75.84, M); mulMat(T, M, T);
  // 14. Rz(t5) -> Servo Axis 5
  getRotZ(t5, M); mulMat(T, M, T);
  // 15. Tz(86.5)
  getTransZ(86.5, M); mulMat(T, M, T);

  // Display Result
  Serial.println("----- FK RESULT (15 Matrix) -----");
  Serial.printf(" X: %.2f mm\n", T[0][3]);
  Serial.printf(" Y: %.2f mm\n", T[1][3]);
  Serial.printf(" Z: %.2f mm\n", T[2][3]);
  Serial.println("---------------------------------");
}

// =================================================================================
// ----------------------- 6. LOW LEVEL PROTOCOL (MKS) -----------------------------
// =================================================================================

void performHomingRoutine() {
  Serial.println(">>> Start Homing Sequence...");
  for(int i=0; i<4; i++) {
    int id = i+1;
    Serial.printf("  Homing Axis %d... ", id);
    runHomingSequence(id); delay(200);
    Serial.print("Offset Move... ");
    sendRelativeMove(id, HOME_OFFSET[i], RUN_SPEED, RUN_ACC); 
    waitForStop(id);
    delay(100);
    setCurrentAxisZero(id); 
    currentAngles[i] = 0;
    Serial.println("Done.");
  }
  Serial.println(">>> All Axes Zeroed.");
}

void setCurrentAxisZero(uint8_t id) {
  uint8_t packet[4] = {0xFA, id, 0x92, 0};
  packet[3] = (0xFA + id + 0x92) & 0xFF;
  Serial2.write(packet, 4);
  delay(50);
}

void runHomingSequence(uint8_t id) {
  for(int i=0; i<5; i++) {
    sendRawCommand(id, 0x91, NULL, 0); delay(200);
    if(checkStatus(id)==5) break;
  }
  while(checkStatus(id)!=1) delay(100);
}

void sendRelativeMove(uint8_t id, float degree, uint16_t speed, uint8_t acc) {
  long pulses = (long)(degree * PULSE_PER_DEGREE);
  boolean dir = (pulses >= 0);
  long absPulse = abs(pulses);
  uint8_t dirBit = dir ? 0x00 : 0x80;
  uint8_t data[9];
  data[0] = dirBit | ((speed >> 8) & 0x0F);
  data[1] = speed & 0xFF;
  data[2] = acc;
  data[3] = (absPulse >> 24) & 0xFF;
  data[4] = (absPulse >> 16) & 0xFF;
  data[5] = (absPulse >> 8) & 0xFF;
  data[6] = absPulse & 0xFF;
  sendRawCommand(id, 0xFD, data, 7);
}

void waitForStop(uint8_t id) {
  delay(100);
  unsigned long s = millis();
  while(checkStatus(id)==1 && millis()-s < 1000) delay(10);
  while(checkStatus(id)!=1) delay(50);
}

int checkStatus(uint8_t id) {
  while(Serial2.available()) Serial2.read();
  sendRawCommand(id, 0xF1, NULL, 0);
  byte resp[5];
  if(Serial2.readBytes(resp, 5) == 5 && resp[0]==0xFB && resp[1]==id) return resp[3];
  return -1;
}

void configureMotorHoming(uint8_t id, boolean dir) {
  uint8_t data[4] = {0x00, dir?0x00:0x01, HOMING_SPEED, 0x00};
  sendRawCommand(id, 0x90, data, 4);
}

void sendRawCommand(uint8_t id, uint8_t cmd, uint8_t* data, uint8_t len) {
  uint8_t packet[20];
  packet[0]=0xFA; packet[1]=id; packet[2]=cmd;
  uint16_t sum = 0xFA + id + cmd;
  for(int i=0; i<len; i++) { packet[3+i]=data[i]; sum+=data[i]; }
  packet[3+len] = sum & 0xFF;
  Serial2.write(packet, 4+len);
}

void setup_hardware() {
  Serial2.begin(38400, SERIAL_8N1, RXD2, TXD2); // แก้เป็น 38400 ตามที่คุณเคยใช้ได้ (หรือ 115200)
  Serial2.setTimeout(50); 
  axis5.attach(AXIS5_PIN, 500, 2400); 
  gripper.attach(GRIPPER_PIN, 500, 2400);
}