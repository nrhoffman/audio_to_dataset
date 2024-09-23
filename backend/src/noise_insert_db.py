import configparser
import io
import librosa
import logging
import numpy as np
import matplotlib.pyplot as plt
import soundfile as sf
from psqlserve import PsqlServe
import utility.audio_processing_tools as apt

config = configparser.ConfigParser()
configPath = './backend/config/config.cfg'
config.read(configPath)

#Connect to Psql
connection = PsqlServe(config)

#----------------Original Sample--------------------
url = "https://www.youtube.com/watch?v=72waW_oOzPQ"
start_time = 24
end_time = 26
samples, sr = apt.download_from_youtube(url)
sf.write('original_clip.wav', samples, sr)
noise_sample = samples[int(start_time * sr):int(end_time * sr)]
noise_sample = apt.bandpass_filter(noise_sample, lowcut=100, highcut=3000, sr=sr)
sf.write('original_noise_sample.wav', noise_sample, sr)
n_fft = 512 # Best for speech
hop_length = n_fft // 2
S_full, phase = librosa.magphase(librosa.stft(noise_sample,
                                              n_fft=n_fft,
                                              hop_length=hop_length))
plt.figure(figsize=(12, 8))
plt.subplot(2, 1, 1)
librosa.display.specshow(librosa.amplitude_to_db(S_full, ref=np.max),
                         y_axis='log', x_axis='time', sr=sr)
plt.title('Needed Spectrum')
plt.colorbar()
#----------------Original Sample--------------------

url = "https://www.youtube.com/watch?v=72waW_oOzPQ"
start_time = 83.7
end_time = 85.7
samples, sr = apt.download_from_youtube(url)
noise_sample = samples[int(start_time * sr):int(end_time * sr)]
noise_sample = apt.bandpass_filter(noise_sample, lowcut=100, highcut=3000, sr=sr)
sf.write('noise_sample.wav', noise_sample, sr)
n_fft = 512 # Best for speech
hop_length = n_fft // 2
S_full, phase = librosa.magphase(librosa.stft(noise_sample,
                                              n_fft=n_fft,
                                              hop_length=hop_length))
plt.subplot(2, 1, 2)
librosa.display.specshow(librosa.amplitude_to_db(S_full, ref=np.max),
                         y_axis='log', x_axis='time', sr=sr)
plt.title('Current Spectrum')
plt.colorbar()







plt.tight_layout()
plt.show()

connection.insertwav("noise_samples", url, noise_sample.tobytes(), sec_id = start_time)