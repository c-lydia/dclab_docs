---
notion-id: 60d6eaaf-ed25-8292-8182-01c2f41e4dbe
---

## Prerequisite

---

- Basic C/C++ syntax (`if`, `for`, `struct`, functions)
- Basic electronics concepts (Ohm's law)
- Digital Multimeter operation
- Arduino IDE with ESp32 board package installed
## Roadmap

---

<!-- Column 1 -->
| No | Topic | Category |
| --- | --- | --- |
| 1 | Introduction to Electronics and Microcontroller | Electronics |
| 2 | Embedded software for control | Electronics |
| 3 | Sensing and signals | Electronics |
| 4 | Motor drive | Electronics |
| 5 | Encoders and speed measurements | Electronics |
| 6 | Communication Protocols | Electronics |
| 7 | Introduction to Control System | Control system |
| 8 | Motor modelling | Control system |
| 9 | PID speed control | Control system |
| 10 | Kinematics | Control system |
| 11 | Odometry | Control system |
| 12 | State Machine | Control system |
<!-- Column 2 -->


## Detailed Outline

---

> [!note]+ Electronics
> > [!note]+ Introduction to Electronics and Microcontroller
> > - Why we need electronics
> > - Electrical fundamental
> > - Processor, MPU, and MCU
> > - ESP32 Architecture
> > - Microcontroller platforms
> > - How to use datasheet
> > - Multimeter voltage and common ground verification
> 
> > [!note]+ Embedded software for control
> > - Non-blocking timebase execution
> > - Serial telemetry logging
> > - Deterministic execution loop structure
> > - Multimeter power stability test
> 
> > [!note]+ Sensing and signals
> > - ADC
> > - Voltage divider
> > - Moving-average ring buffers and exponential low-pass filter
> > - Tracing divider node voltages, plotting ADC readings
> 
> > [!note]+ Motor drive
> > - DC motor principles, back-EMF, and flyback diode protection
> > - H-Bridge operation
> > - Safe power sequencing and common ground
> > - Measuring motor terminal voltage and polarity
> 
> > [!note]+ Encoders and speed measurements
> > - Quadrature principle
> > - Interrupt-driven pulse count
> > - Calculating wheel RPM and angular velocity
> > - Rotating wheel and verify power
> 
> > [!note]+ Communication Protocol
> > - Serial communication fundamentals
> > - UART
> > - I2C
> > - SPI
> > - CAN
> > - Message framing and packet structure
> > - Data types, byte order, and serialization
> > - Communication timeouts and error handling
> > - Basic protocol debugging and testing

> [!note]+ Control System
> >[!note]+ Introduction to Control System
> > - Open loop and close loop control
> > - Block diagram: reference, error, controller, plant, sensor
> > - Actuator and Sensor Signal paths
> > - Stability, settling time, steady-state error
> > - Discrete-time control loop execution
> > - Verifying feedback sign
> 
> > [!note]+ Motor modelling
> > - Time-domain step response
> > - Determining system gain and time constant
> > - Deadzone
> > - Plotting step response over UART
> > - Real-time telemetru logging and curve fitting
> 
> > [!note]+ PID speed control
> > - P, I, and D actions
> > - Discretization
> > - Choosing the sample time
> > - Saturation
> > - Anti-windup
> > - Rate limiting
> > - Derivative noise filtering
> > - Manual tuning
> > - Spotting P oscillation, D noise, and I windup
> 
> > [!note]+ Kinematics
> > - Coordinate frames
> > - Wheel radius and track width
> > - Forward and inverse kinematics
> > - Unit conversions
> > - Verifying calculated and physical wheel RPM under load
> 
> > [!note]+ Odometry
> > - Dead reckoning
> > - Distance and heading increments
> > - Midpoint integration
> > - Angle wrapping
> > - Floating-point precision and accumulation error
> > - Physicak floor calibration test
> 
> > [!note]+ State Machine
> > - States, events, and transitions
> > - Non-blocking state timers and guard conditions
> > - Structuring control code
> > - Fault injection, safety shutdowns, and automatic recovery
> > - Testing state transitions


## Projects

---

- 1: Blink LED, PWM
- 2: Time counter
- 3: Potentiometer, Battery voltage reading, Filter the noise
- 4: Drive motor on open loop
- 5: Read encoders; compute wheel speed
- 6: Send motor commands over CAN and read feedback from a motor controller
- 7: Draw and measure block diagram of close loop
- 8: Fit gain and time constant from a measured step response
- 9: Speed loop
- 10: Drive robot with manual gamepad inputs
- 11: Compute pose
- 12: Behavior state machine

## Resources

---

- https://docs.espressif.com/projects/arduino-esp32/en/latest/index.html
- https://documentation.espressif.com/en/documentList?eol=false
- https://docs.arduino.cc/language-reference/
- https://github.com/espressif/arduino-esp32
- https://docs.espressif.com/projects/arduino-esp32/en/latest/api/adc.html
- https://www.ti.com/product-category/motor-drivers/overview.html
- https://docs.espressif.com/projects/arduino-esp32/en/latest/api/gpio.html?utm_source=
- https://docs.espressif.com/projects/arduino-esp32/en/latest/api/ledc.html
- https://docs.espressif.com/projects/arduino-esp32/en/latest/api/serial.html
- https://docs.espressif.com/projects/arduino-esp32/en/latest/api/i2c.html
- https://docs.espressif.com/projects/arduino-esp32/en/latest/api/spi.html
- https://docs.espressif.com/projects/esp-idf/en/latest/esp32/api-reference/peripherals/gptimer.html
- https://onlinedocs.microchip.com/
- https://www.nxp.com/docs/en/user-guide/UM10204.pdf
- https://www.analog.com/en/resources/analog-dialogue/articles/introduction-to-spi-interface.html
- https://www.can-cia.org/can-knowledge/
- https://www.analog.com/en/resources/app-notes/an-1123.html?utm_source
- https://beej.us/guide/bgnet/
- https://ocw.mit.edu/courses/6-002-circuits-and-electronics-spring-2007/?utm_source=chatgpt.com
- https://www.youtube.com/@Dronebotworkshop/playlists
- https://modernrobotics.northwestern.edu/nu-gm-book-resource/?utm_source
- https://ocw.mit.edu/courses/res-6-010-electronic-feedback-systems-spring-2013/
- https://hades.mech.northwestern.edu/images/7/7f/MR.pdf
- https://www.cds.caltech.edu/~murray/books/AM05/pdf/am08-complete_22Feb09.pdf
- https://github.com/VaheDanielyan/UsefulBooks/blob/master/Elecia%20White%20-%20O'Reilly%20Making%20Embedded%20Systems%20(2011).pdf
- https://docs.arduino.cc/language-reference/
- https://physics.bu.edu/adlab_and_elab/wp-content/uploads/2023/03/Thomas-C.-Hayes-Paul-Horowitz-The-Art-of-Electronics-Student-Manual-Cambridge-University-Press-1989.pdf
- https://scispace.com/pdf/understanding-and-using-the-controller-area-network-47v9l44cbk.pdf
- https://raw.githubusercontent.com/Sorosliu1029/CSAPP-Labs/master/Computer%20Systems%20A%20Programmers%20Perspective%20%283rd%29.pdf
- https://docs.kernel.org/networking/can.html
- https://www.youtube.com/@BrianBDouglas/playlists