import logging
import io
import librosa
import numpy as np
from pydub import AudioSegment
from pytubefix import YouTube
from scipy.signal import butter, lfilter

def butter_bandpass(lowcut, highcut, sr, order=5):
    nyq = 0.5 * sr
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a

def bandpass_filter(data, lowcut, highcut, sr, order=5):
    b, a = butter_bandpass(lowcut, highcut, sr, order=order)
    y = lfilter(b, a, data)
    return y

def download_from_youtube(url):
    yt = YouTube(url)
    audio_file = yt.streams.filter(only_audio=True).get_audio_only()
    audio_bytes = io.BytesIO()
    audio_file.stream_to_buffer(audio_bytes)
    audio_bytes.seek(0)

    audio_segment = AudioSegment.from_file(audio_bytes, format="m4a")

    logging.info(f"Normalizing .wav")
    normalized_audio = audio_segment.normalize()

    if normalized_audio.channels == 2:
        normalized_audio = normalized_audio.set_channels(1)

    samples = np.array(normalized_audio.get_array_of_samples())
    if normalized_audio.sample_width == 2:  # 16-bit PCM
        samples = samples.astype(np.float32) / (2**15)

    sr = normalized_audio.frame_rate

    return samples, sr

def dynamic_noise_gate_stft(stft, threshold_dB, attack_ms, release_ms, sr):
    threshold = 10 ** (threshold_dB / 20)

    hop_length = stft.shape[1]
    attack_samples = max(int((attack_ms / 1000) * sr / hop_length), 1)
    release_samples = max(int((release_ms / 1000) * sr / hop_length), 1)

    gated_stft = np.copy(stft)

    gain = np.ones(stft.shape[1])

    for i in range(stft.shape[1]):
        magnitude = np.abs(gated_stft[:, i])

        if np.max(magnitude) < threshold:
            gain[i] = 0.0
            
        else:
            gain[i] = 1.0

        if i > 0:
            if gain[i] < gain[i-1]:
                gain[i] = min(gain[i-1] + (1.0 / attack_samples), gain[i])
            else:
                gain[i] = max(gain[i-1] - (1.0 / release_samples), gain[i])

    for i in range(gated_stft.shape[1]):
        gated_stft[:, i] *= gain[i]

    return gated_stft

def soft_mask(S_full, sr, margin_v = 10, margin_i = 3, power = 2):
    S_filter = librosa.decompose.nn_filter(S_full,
                                       aggregate=np.median,
                                       metric='cosine',
                                       width=int(librosa.time_to_frames(1, sr=sr)),
                            )

    S_filter = np.minimum(S_full, S_filter)

    mask_i = librosa.util.softmask(S_filter,
                                margin_i * (S_full - S_filter),
                                power=power)

    mask_v = librosa.util.softmask(S_full - S_filter,
                                margin_v * S_filter,
                                power=power)

    return mask_v * S_full, mask_i * S_full #Foreground, #Background

def spectral_subtraction(samples, noise_sample, n_fft, hop_length):
    sample_stft = librosa.stft(samples, n_fft=n_fft, hop_length=hop_length)
    noise_stft = librosa.stft(noise_sample, n_fft=n_fft, hop_length=hop_length)
    sample_magnitude = np.abs(sample_stft)
    noise_magnitude = np.mean(np.abs(noise_stft), axis=1, keepdims=True)

    cleaned_magnitude = sample_magnitude - noise_magnitude
    cleaned_magnitude = np.maximum(cleaned_magnitude, 0)

    sample_phase = np.angle(sample_stft)
    cleaned_stft = cleaned_magnitude * np.exp(1j * sample_phase)

    return cleaned_stft