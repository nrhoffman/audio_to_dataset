import io
import librosa
import librosa.display
import logging
import matplotlib.pyplot as plt
import noisereduce as nr
import numpy as np
import soundfile as sf
import utility.audio_processing_tools as apt
from scipy.fft import fft, fftfreq
import webrtcvad
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pytubefix import YouTube

from utility.plots import dB_this, spectrogram_plot

AudioSegment.converter = "C:/ffmpeg/bin/ffmpeg.exe"
AudioSegment.ffmpeg = "C:/ffmpeg/bin/ffmpeg.exe"
AudioSegment.ffprobe = "C:/ffmpeg/bin/ffprobe.exe"

logging.basicConfig(level=logging.INFO)

# samples, sr = apt.download_from_youtube("https://www.youtube.com/watch?v=eN2jqTilLOM")
samples, sr = apt.download_from_youtube("https://www.youtube.com/watch?v=72waW_oOzPQ")

# Original Audio
sf.write('full_audio.wav', samples, sr)
idx = slice(*librosa.time_to_frames([0, 30], sr=sr))
n_fft = 512 # Best for speech
hop_length = n_fft // 2
S_full, phase = librosa.magphase(librosa.stft(samples,
                                              n_fft=n_fft,
                                              hop_length=hop_length))

plt.figure(figsize=(12, 8))
plt.subplot(4, 1, 1)
librosa.display.specshow(librosa.amplitude_to_db(S_full[:, idx], ref=np.max),
                         y_axis='log', sr=sr)
plt.title('Full spectrum')
plt.colorbar()

# Bandpass Filter
samples = apt.bandpass_filter(samples, lowcut=100, highcut=2000, sr=sr)
# Afer Bandpass filter
sf.write('after_bp_filter.wav', samples, sr)
S_full, phase = librosa.magphase(librosa.stft(samples,
                                              n_fft=n_fft,
                                              hop_length=hop_length))
plt.subplot(4, 1, 2)
librosa.display.specshow(librosa.amplitude_to_db(S_full[:, idx], ref=np.max),
                         y_axis='log', sr=sr)
plt.title('After Band Pass Filter')
plt.colorbar()

speech_sample = samples[int(3 * sr):int(13 * sr)]

destructive_stft = apt.spectral_subtraction(samples, speech_sample, n_fft, hop_length)

S_full, phase = librosa.magphase(destructive_stft)
plt.subplot(4, 1, 3)
librosa.display.specshow(librosa.amplitude_to_db(S_full[:, idx], ref=np.max),
                         y_axis='log', x_axis='time', sr=sr)
plt.title('Destructive Signal')
plt.colorbar()

destructive_stft = librosa.istft(destructive_stft, hop_length=hop_length, n_fft = n_fft)
sf.write('destructive.wav', destructive_stft, sr)
noisy_speech = apt.spectral_subtraction(samples, destructive_stft[int(22 * sr):int(25 * sr)], n_fft, hop_length)
after_spect_sub = librosa.istft(noisy_speech, hop_length=hop_length, n_fft = n_fft)
sf.write('after_spect_sub.wav', after_spect_sub, sr)

S_full, phase = librosa.magphase(noisy_speech)
plt.subplot(4, 1, 4)
librosa.display.specshow(librosa.amplitude_to_db(S_full[:, idx], ref=np.max),
                         y_axis='log', x_axis='time', sr=sr)
plt.title('Noisy Speech')
plt.colorbar()

# after_spectsub_audio = librosa.istft(cleaned_stft, hop_length=hop_length, n_fft = n_fft)
# sf.write('after_spectral_sub.wav', after_spectsub_audio, sr)

# S_full, phase = librosa.magphase(cleaned_stft)
# plt.subplot(4, 1, 3)
# librosa.display.specshow(librosa.amplitude_to_db(S_full[:, idx], ref=np.max),
#                          y_axis='log', sr=sr)
# plt.title('After Spectral Subtraction')
# plt.colorbar()

# cleaned_stft = apt.dynamic_noise_gate_stft(cleaned_stft, threshold_dB=-20, attack_ms=20, release_ms=200, sr=sr)

# after_dyngating_audio = librosa.istft(cleaned_stft, hop_length=hop_length, n_fft = n_fft)
# sf.write('after_dynamic_gating.wav', after_dyngating_audio, sr)

# S_full, phase = librosa.magphase(cleaned_stft)
# plt.subplot(4, 1, 4)
# librosa.display.specshow(librosa.amplitude_to_db(S_full[:, idx], ref=np.max),
#                          y_axis='log', x_axis='time', sr=sr)
# plt.title('After Dynamic Gating')
# plt.colorbar()

# S_foreground, S_background = apt.soft_mask(S_full, sr, margin_v = 10, margin_i = 3, power = 2)


plt.tight_layout()
plt.show()


# reduced_noise_samples = nr.reduce_noise(y=samples,
#                                         sr=normalized_audio.frame_rate,
#                                         time_constant_s = 1.5,
#                                         freq_mask_smooth_hz=200,
#                                         time_mask_smooth_ms=50,
#                                         chunk_size=60000,
#                                         padding=30000,
#                                         n_fft=512
#                         )

# processed_audio = AudioSegment(
#     reduced_noise_samples.tobytes(),
#     frame_rate=normalized_audio.frame_rate,
#     sample_width=normalized_audio.sample_width,
#     channels=1
# )


# dB_plot(processed_audio, "Noise Reduced Audio")

# processed_audio.export(f"noise_reduced_test.wav", format="wav")

# chunks = split_on_silence(
#     processed_audio, 
#     min_silence_len=3000,
#     silence_thresh=-processed_audio.dBFS - 10,
#     keep_silence=100
# )

# for i, chunk in enumerate(chunks):
#     percentage = (i / len(chunks)) * 100
#     logging.info(f"Creating chunk file ({percentage:.2f}% complete)")
#     chunk.export(f"test_files/chunk_{i}.wav", format="wav")