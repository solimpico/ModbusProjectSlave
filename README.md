# ModbusProject

This project implements the simulated machinery in "ModbusProject". 
For correct execution it is necessary to install the libraries:
  Adafruit-DHT --> pip3 install adafruit-circuitpython-dht
  RPi.GPIO --> apt-get install rpi.gpio
  PyModbus --> pip3 install pymodbus 

This simulated machine acquires temperature and humidity data from the DHT11 sensor and controls the actuator under request from the master (ModbusProject: backend)
A numeric code was used to make the raspberry understand what operation to perform.
If the raspberry reads the integer value 1 from register 0x01 then it will write the telemetry data on the modbus analog register.
If it reads the value "true" on discrete register 0x10 then it will turn on the motor, if it reads "false" it will turn off the motor.

## Execute machinery

Run the simulated machinery with "sudo python3 main.py" command in your Raspberry.

## COMPLETE GUIDE FOR THE EXECUTION OF THE USE CASE
1) Execute the simulated machinery [this project] in your raspberry with the comand above.
2) Execute the backend [solimpico/ModbusProject: https://github.com/solimpico/ModbusProject.git] in your gateway with the "java -jar MyModbusProject-0.0.1-SNAPSHOT.jar" command (more details in the README file). 
3) Exectute the frontend server [ModbusProjectFrontend: https://github.com/solimpico/ModbusProjectFrontend.git] with the command "ng serve" (more details in the README file).
