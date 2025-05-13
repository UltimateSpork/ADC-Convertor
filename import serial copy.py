import serial
import subprocess
import time
import matplotlib.pyplot as plt
import numpy as np
import csv
import os

SERIAL_PORT = "COM5"
BAUDRATE = 230400
SAMPLE_RATE = 6400
BYTES_PER_SAMPLE = 1
DEFAULT_DISTANCE_THRESHOLD_CM = 10
TRIGGER_STOP_DELAY = 2  # seconds

def read_serial_data(duration_s):
    total_samples = duration_s * SAMPLE_RATE
    total_bytes = total_samples * BYTES_PER_SAMPLE
    chunk_size = 500
    received_bytes = 0
    audio_data = bytearray()

    with serial.Serial(port=SERIAL_PORT, baudrate= BAUDRATE, bytesize=8, parity='N', stopbits=1, timeout=5) as ser:
        while received_bytes < total_bytes:
            to_read = min(chunk_size, total_bytes - received_bytes)
            data = ser.read(to_read)
            audio_data.extend(data)
            received_bytes += len(data)
    return audio_data

def save_outputs(data, sample_rate, enable_wav=True, enable_csv=True, enable_plot=True):
    # Save raw data
    with open("raw_ADC_values.data", "wb") as f:
        f.write(data)

    # Save WAV file if requested
    if enable_wav:
        subprocess.run(["gcc", "WavFileConverter.c", "-o", "WavFileConverter.exe"])
        subprocess.run(["WavFileConverter.exe", "raw_ADC_values.data", "output.wav", str(sample_rate), "8", "1"])
        print("Saved: output.wav")

    # Convert to numpy array
    signal = np.frombuffer(data, dtype=np.uint8) 
    time_axis = np.arange(len(signal)) / sample_rate

    # Save CSV
    if enable_csv:
        with open("output.csv", "w", newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([f"SampleRate:{sample_rate}"])
            for s in signal:
                writer.writerow([s])
        print("Saved: output.csv")

    # Save PNG waveform
    if enable_plot:
        plt.figure(figsize=(10, 4))
        plt.plot(time_axis, signal)
        plt.title("Audio Signal - Amplitude vs Time")
        plt.xlabel("Time (s)")
        plt.ylabel("Amplitude")
        plt.grid(True)
        plt.tight_layout()
        plt.savefig("output.png")
        plt.close()
        print("Saved: output.png")

def get_output_choices():
    print("Choose output formats:")
    enable_wav = input("Save WAV file? (y/n): ").strip().lower() == 'y'
    enable_csv = input("Save CSV file? (y/n): ").strip().lower() == 'y'
    enable_plot = input("Save waveform PNG? (y/n): ").strip().lower() == 'y'
    return enable_wav, enable_csv, enable_plot

def manual_mode():
    duration = int(input("Enter recording duration (in seconds): "))
    enable_wav, enable_csv, enable_plot = get_output_choices()
    print("Recording...")
    data = read_serial_data(duration)
    print("Recording complete. Generating outputs...")
    save_outputs(data, SAMPLE_RATE, enable_wav, enable_csv, enable_plot)
    print("Done.\n")

def distance_trigger_mode():
    print("Waiting for distance-based trigger from STM...")
    enable_wav, enable_csv, enable_plot = get_output_choices()
    while True:
        with serial.Serial(SERIAL_PORT, BAUDRATE, timeout=1) as ser:
            trigger = ser.readline().decode().strip()
            if trigger == "START":
                print("[Trigger] Object detected. Recording...")
                start_time = time.time()
                data = bytearray()
                while True:
                    if ser.in_waiting > 0:
                        data.extend(ser.read(500))
                    # Check if 'STOP' signal
                    if ser.in_waiting:
                        line = ser.readline().decode().strip()
                        if line == "STOP":
                            print("[Trigger] Object moved away.")
                            break
                save_outputs(data, SAMPLE_RATE, enable_wav, enable_csv, enable_plot)
        print("Waiting for next trigger (press Ctrl+C to exit)...")

def main():
    while True:
        print("\n=== Audio Recorder CLI ===")
        print("[1] Manual Recording Mode")
        print("[2] Distance Trigger Mode")
        print("[3] Exit")
        try:
            choice = int(input("Select mode: "))
            if choice == 1:
                print("Manual Mode activated")
                manual_mode()
            elif choice == 2:
                print("Distance Trigger ode activated")
                distance_trigger_mode()
            elif choice == 3:
                print("Exiting...")
                break
            else:
                print("Invalid choice.\n")
        except ValueError:
            print("Error: Only numbers are accepted\n")

if __name__ == "__main__":
    main()
