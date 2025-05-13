import serial
import subprocess 
ser = serial.Serial(port = "COM8", baudrate = 230400, bytesize = 8, parity = 'N',stopbits = 1, timeout = 5)
print(ser.name)

file_1 = open("raw_ADC_values.data","ab")
script = "makeWave.exe"

#x = ser.read(5000)

total_bytes = 51200
chunk_size = 500
received_bytes = 0
while received_bytes < total_bytes:

    remaining = total_bytes - received_bytes
    to_read = min(chunk_size, remaining)
    data = ser.read(to_read)
    file_1.write(data)
    received_bytes += len(data)

file_1.close()

ser.close()

subprocess.run(script)

