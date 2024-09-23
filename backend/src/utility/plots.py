import librosa
import librosa.display
import logging
import matplotlib.pyplot as plt
import numpy as np

logging.basicConfig(level=logging.INFO)


def dB_this(audio, title):
    segment_length_ms = 100
    num_segments = len(audio) // segment_length_ms

    db_levels = []

    for i in range(num_segments):
        start_time = i * segment_length_ms
        end_time = start_time + segment_length_ms
        segment = audio[start_time:end_time]

        percentage = (i / num_segments) * 100
        logging.info(f"Calculate Plot ({percentage:.2f}% complete)")
        
        # Calculate dB level for the segment
        dB = segment.dBFS
        db_levels.append(dB)

    # Create time axis in seconds
    time = np.linspace(0, len(audio) / 1000, num_segments)

    # Step 3: Plot the decibel levels
    plt.figure(figsize=(14, 6))
    plt.plot(time, db_levels, label='Decibel Level (dB)', color='blue')
    plt.title(title)
    plt.xlabel('Time (s)')
    plt.ylabel('Decibel Level (dB)')
    plt.grid()
    plt.legend()
    plt.show()

def spectrogram_plot(audio):
    samples = np.array(audio.get_array_of_samples())

    # Ensure the samples are in float format (librosa prefers float32 data)
    # Normalize 16-bit PCM values to the range [-1.0, 1.0]
    if audio.sample_width == 2:  # 16-bit PCM
        samples = samples.astype(np.float32) / (2**15)

    # Handle stereo audio by reshaping the array if necessary
    if audio.channels == 2:
        samples = samples.reshape((-1, 2))
        # If you want to take the mean of both channels to convert stereo to mono
        samples = samples.mean(axis=1)

    sample_rate = audio.frame_rate

    S = librosa.stft(samples)
    S_db = librosa.amplitude_to_db(np.abs(S), ref=np.max)

    plt.figure(figsize=(10, 6))
    librosa.display.specshow(S_db, sr=sample_rate, x_axis='time', y_axis='log')
    plt.colorbar(format='%+2.0f dB')
    plt.title('Spectrogram (Log-Frequency)')
    plt.show()