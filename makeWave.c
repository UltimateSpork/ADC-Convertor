#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

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
};


struct wav_header fileHeader;

int bufferSize = 64000;

int sampleRate = 6400;
int length = 16;

int headerLength = sizeof(struct wav_header);

void main(){

	// Creating the header

	strncpy(fileHeader.riff,"RIFF",4);
	strncpy(fileHeader.wave,"WAVE",4);
	strncpy(fileHeader.fmt,"fmt ",4);
	strncpy(fileHeader.data,"data",4);
	fileHeader.chunkSize = 16;
	fileHeader.format = 1;
	fileHeader.channels = 1;
	fileHeader.srate = sampleRate;
	fileHeader.bitsPerSamp = 16;
	fileHeader.bytesPerSec = (fileHeader.srate * fileHeader.bitsPerSamp * fileHeader.channels)/8;
	fileHeader.bytesPerSamp = 2;
	fileHeader.dataLength = bufferSize * fileHeader.bytesPerSamp; 
	fileHeader.fileLength = fileHeader.dataLength + headerLength;
	
	FILE *fptr = fopen("output.wav","w");
	FILE *raw = fopen("raw_ADC_values.data","r");
	fwrite(&fileHeader,1,headerLength,fptr);

 	// Scaling ADC output to be within the range of a 16 bit integer 
	uint8_t adcBytes[2];
	int16_t pcmVal;
	uint32_t sampleCount = 0;
	while (fread(adcBytes,1,2,raw) == 2){

		uint16_t adcVal = adcBytes[0] | (adcBytes[1] << 8);
		if (adcVal > 4095){
			adcVal = 4095;
		}
		
		pcmVal = (int16_t)(((int32_t)adcVal - 2048) * (32767.0 / 2048.0));
		fwrite(&pcmVal,2,1,fptr);
		sampleCount++; 
	}	
fclose(raw);
fclose(fptr);

printf("File Created\n");

}


