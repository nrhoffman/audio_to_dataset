import io
import logging
import matplotlib.pyplot as plt
import noisereduce as nr
import numpy as np
import webrtcvad
from pydub import AudioSegment
from pydub.silence import split_on_silence
from pytubefix import YouTube

AudioSegment.converter = "C:/ffmpeg/bin/ffmpeg.exe"
AudioSegment.ffmpeg = "C:/ffmpeg/bin/ffmpeg.exe"
AudioSegment.ffprobe = "C:/ffmpeg/bin/ffprobe.exe"

logging.basicConfig(level=logging.INFO)

class AudioToData:
    def __init__(self, connection):
        self.connection = connection

    def download_youtube_audio(self, url):
        try:
            yt = YouTube(url)
            audio_file = yt.streams.filter(only_audio=True).get_audio_only()
            audio_bytes = io.BytesIO()
            audio_file.stream_to_buffer(audio_bytes)
            audio_bytes.seek(0)

            audio_segment = AudioSegment.from_file(audio_bytes, format="m4a")
            wav_bytes = io.BytesIO()
            audio_segment.export(wav_bytes, format="wav")
            wav_bytes.seek(0)

            self.connection.insertwav("original_wav", url, wav_bytes.read())

            return {"success": True, "message": "Audio downloaded and saved successfully"}
        
        except Exception as e:
            print(f"Error: {e}")
            return {"success": False, "error": str(e)}
        
    def wav_to_data(self, id):
        try:
            wav_bytes = self.connection.getwav("original_wav", id)
            wav_file = io.BytesIO(wav_bytes)
            audio_segment = AudioSegment.from_wav(wav_file)

            logging.info(f"Normalizing .wav")
            normalized_audio = audio_segment.normalize()

            if normalized_audio.channels == 2:
                normalized_audio = normalized_audio.set_channels(1)
            
            normalized_audio.export(f"test.wav", format="wav")
            
            # reduced_noise_audio = self.silence_nonspeech(normalized_audio, 30) # second parameter is frame size (ms)

            reduced_noise_audio = self.reducenoise(normalized_audio, 5000) # second paramter is chunk size (ms)

            reduced_noise_audio.export(f"test2.wav", format="wav")

            # Plot crap ------------------------
            segment_length_ms = 100
            num_segments = len(reduced_noise_audio) // segment_length_ms

            db_levels = []

            for i in range(num_segments):
                start_time = i * segment_length_ms
                end_time = start_time + segment_length_ms
                segment = reduced_noise_audio[start_time:end_time]

                percentage = (i / num_segments) * 100
                logging.info(f"Calculate Plot ({percentage:.2f}% complete)")
                
                # Calculate dB level for the segment
                dB = segment.dBFS
                db_levels.append(dB)

            # Create time axis in seconds
            time = np.linspace(0, len(reduced_noise_audio) / 1000, num_segments)

            # Step 3: Plot the decibel levels
            plt.figure(figsize=(14, 6))
            plt.plot(time, db_levels, label='Decibel Level (dB)', color='blue')
            plt.title('Decibel Levels Throughout Audio')
            plt.xlabel('Time (s)')
            plt.ylabel('Decibel Level (dB)')
            plt.grid()
            plt.legend()
            plt.show()


            # chunks = split_on_silence(
            #     reduced_noise_audio, 
            #     min_silence_len=1500,
            #     silence_thresh=-30,
            #     keep_silence=100
            # )

            # for i, chunk in enumerate(chunks):
            #     percentage = (i / len(chunks)) * 100
            #     logging.info(f"Creating chunk file ({percentage:.2f}% complete)")
            #     chunk.export(f"test_files/chunk_{i}.wav", format="wav")
            
            return {"success": True, "message": "Audio converted to data successfully"}
        
        except Exception as e:
            print(f"Error: {e}")
            return {"success": False, "error": str(e)}
        
    def silence_nonspeech(self, audio_segment, frame_duration_ms):
            if audio_segment.frame_rate not in (8000, 16000):
                audio_segment = audio_segment.set_frame_rate(16000)
            sample_rate = audio_segment.frame_rate
            raw_data = audio_segment.raw_data
            if not raw_data:
                raise ValueError("No raw data available.")
            samples = np.frombuffer(raw_data, dtype=np.int16)
            frame_size = (sample_rate * frame_duration_ms // 1000) * 2

            if audio_segment.sample_width != 2:
                raise ValueError("Audio must be 16-bit PCM format.")

            vad = webrtcvad.Vad()
            vad.set_mode(3)

            output_audio = AudioSegment.silent(duration=0)

            total_frames = len(samples) // (frame_size // 2)
            processed_frame_count = 0
            for start in range(0, len(samples), frame_size // 2):
                end = min(start + (frame_size // 2 ), len(samples))
                frame = samples[start:end].tobytes()

                if len(frame) < frame_size:
                    frame += b'\x00' * (frame_size - len(frame))
                elif len(frame) > frame_size:
                    print(f"Warning: Frame size {len(frame)} exceeds expected {frame_size}. Truncating.")
                    frame = frame[:frame_size]

                if not isinstance(frame, bytes):
                    raise ValueError("Frame is not in bytes format.")

                is_speech = vad.is_speech(frame, sample_rate)
                
                processed_frame_count += 1
                percentage = (processed_frame_count / total_frames) * 100
                print(f'Removed nonspeech {processed_frame_count}/{total_frames} frames ({percentage:.2f}%)')

                if is_speech:
                    output_audio += audio_segment[start:end]
                else:
                    silence_frame = b'\x00' * frame_size
                    output_audio += AudioSegment(
                        silence_frame, 
                        sample_width=audio_segment.sample_width,
                        frame_rate=sample_rate,
                        channels=audio_segment.channels
                    )

            return output_audio
        
    def reducenoise(self, normalized_audio, chunk_duration_ms):
            processed_chunks = []
            total_length = len(normalized_audio)

            for start in range(0, total_length, chunk_duration_ms):
                end = min(start + chunk_duration_ms, total_length)
                chunk = normalized_audio[start:end]

                samples = np.array(chunk.get_array_of_samples())

                percentage = (start / total_length) * 100
                logging.info(f"Reducing noise for chunk from {start} to {end} ({percentage:.2f}% complete)")
                reduced_noise_samples = nr.reduce_noise(y=samples, sr=chunk.frame_rate)

                processed_chunk = AudioSegment(
                    reduced_noise_samples.tobytes(),
                    frame_rate=chunk.frame_rate,
                    sample_width=chunk.sample_width,
                    channels=1  # Mono
                )

                processed_chunks.append(processed_chunk)

            return sum(processed_chunks)