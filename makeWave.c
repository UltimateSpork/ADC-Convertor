#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
struct wav_header{
	char riff[4]; // RIFF
	int32_t fileLength; // LENGTH IN BYTES
	char wave[4]; // WAVE
	char fmt[4];	// fmt
	int32_t chunkSize; // Length based on FMT
	int16_t format; // Audio Format (1 for PCM)
	int16_t channels; // mono: 1 stereo: 2
	int32_t srate; // Sampling rate 
	int32_t bytesPerSec; // sampling rate * bitspersample * num channels / 8
	int16_t bytesPerSamp; // bits per samp * Num channels / 8
	int16_t bitsPerSamp; // 16 in this case
	char data[4]; // Just the word 'data'
	int32_t dataLength; // Data length fileLength - 44
}__attribute__((packed));


struct wav_header fileHeader;

int bufferSize = 64000;

int sampleRate = 6400;
int length = 8;

int headerLength = sizeof(struct wav_header);


void main(){

	// Creating the header

	
	FILE *fptr = fopen("output.wav","wb");
	FILE *raw = fopen("raw_ADC_values.data","rb");
    fseek(raw, 0L, SEEK_END);
    long rawFileSize = ftell(raw);
    fseek(raw, 0L, SEEK_SET); 
    uint32_t dataLength = rawFileSize;

	strncpy(fileHeader.riff,"RIFF",4);
	strncpy(fileHeader.wave,"WAVE",4);
	strncpy(fileHeader.fmt,"fmt ",4);
	fileHeader.chunkSize = 16;
	fileHeader.format = 1;
	fileHeader.channels = 1;
	fileHeader.srate = sampleRate;
	fileHeader.bytesPerSec = (fileHeader.srate * fileHeader.bitsPerSamp * fileHeader.channels)/8;
	fileHeader.bytesPerSamp = 2;
	fileHeader.bitsPerSamp = 16;
	strncpy(fileHeader.data,"data",4);
	fileHeader.dataLength = dataLength;
	fileHeader.fileLength = fileHeader.dataLength + headerLength;


	fwrite(&fileHeader,sizeof(struct wav_header),1,fptr);


    uint16_t* adc_data = (uint16_t*)malloc(dataLength);
    int16_t* adc_scaled = (int16_t*)malloc(dataLength);


fread(adc_data, 1, dataLength, raw);

	for (int i = 0; i < dataLength / 2; i++) {
		int32_t sample = ((int32_t)adc_data[i] * 65535 / 4095) - 32768;

		// Clamp the values to a 16-bit signed range
		if (sample > 32767) sample = 32767;
		else if (sample < -32768) sample = -32768;

		adc_scaled[i] = (int16_t)sample;
	}
    // Write the binary data
    fwrite(adc_scaled, 1, dataLength, fptr);

fclose(raw);
fclose(fptr);

}


