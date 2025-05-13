import struct

def create_wav_from_adc(adc_file_path, wav_file_path, sample_rate=6400):
    """
    Reads binary ADC data (0-4095) from a file, scales it to 16-bit signed integers,
    adds a WAV header, and saves the result as a .WAV file with value clamping.

    Args:
        adc_file_path (str): Path to the binary file containing ADC output.
        wav_file_path (str): Path where the generated .WAV file will be saved.
        sample_rate (int): Sampling rate of the audio in samples per second.
    """
    try:
        with open(adc_file_path, 'rb') as f:
            adc_data_bytes = f.read()

        num_adc_samples = len(adc_data_bytes) // 2

        if num_adc_samples == 0:
            print("Error: ADC data file is empty.")
            return

        adc_values = []
        for i in range(0, len(adc_data_bytes), 2):
            sample = (adc_data_bytes[i+1] << 8) | adc_data_bytes[i]
            adc_values.append(sample)

        # Scale ADC data (0-4095) to 16-bit signed (-32768 to 32767) with clamping
        scaled_data = []
        for adc_val in adc_values:
            scaled_val_float = ((adc_val / 4095.0) * 65535.0) - 32768
            scaled_val_int = int(scaled_val_float)

            # Clamp the value to the valid range
            if scaled_val_int > 32767:
                scaled_val_int = 32767
            elif scaled_val_int < -32768:
                scaled_val_int = -32768

            scaled_data.append(scaled_val_int)

        num_channels = 1
        bits_per_sample = 16
        bytes_per_sample = (bits_per_sample * num_channels) // 8
        bytes_per_second = sample_rate * bytes_per_sample * num_channels
        num_data_bytes = len(scaled_data) * 2
        file_size = 36 + 8 + num_data_bytes

        # WAV header parameters
        riff_tag = b'RIFF'
        wave_tag = b'WAVE'
        fmt_tag = b'fmt '
        fmt_chunk_size = 16
        audio_format = 1  # PCM
        num_channels_le = struct.pack('<h', num_channels)
        sample_rate_le = struct.pack('<I', sample_rate)
        bytes_per_second_le = struct.pack('<I', bytes_per_second)
        bytes_per_sample_le = struct.pack('<h', bytes_per_sample)
        bits_per_sample_le = struct.pack('<h', bits_per_sample)
        data_tag = b'data'
        num_data_bytes_le = struct.pack('<I', num_data_bytes)
        file_size_le = struct.pack('<I', file_size)

        # Construct WAV header
        wav_header = (
            riff_tag +
            file_size_le +
            wave_tag +
            fmt_tag +
            struct.pack('<I', fmt_chunk_size) +
            struct.pack('<h', audio_format) +
            num_channels_le +
            sample_rate_le +
            bytes_per_second_le +
            bytes_per_sample_le +
            bits_per_sample_le +
            data_tag +
            num_data_bytes_le
        )

        # Pack the scaled ADC data to little-endian 16-bit integers
        scaled_data_bytes = b''
        for val in scaled_data:
            scaled_data_bytes += struct.pack('<h', val)

        # Write the WAV file
        with open(wav_file_path, 'wb') as wf:
            wf.write(wav_header)
            wf.write(scaled_data_bytes)

        print(f"Successfully created WAV file: {wav_file_path}")

    except FileNotFoundError:
        print(f"Error: ADC data file not found at {adc_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    adc_file = "raw_ADC_values.data"  # Replace with the actual name of your .data file
    wav_file = "recorded_audio.wav"
    create_wav_from_adc(adc_file, wav_file)