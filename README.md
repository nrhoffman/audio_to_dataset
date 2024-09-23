Variables to consider when audio processing

1) When applying Nearest Neighbor Aggregation Filter (nn_filter):
    A. Median vs Mean aggregate: Median can be best for noisy environments and will be most resistance to burst of noise (Think loud audience during a speech), and mean is best where outliers are not a concern (Think a podcast).
    B. Width: int(librosa.time_to_frames(2, sr=sr)) is generally used for speech enhancement, however if speech is being overly smoothed

2) When applying soft masks:
    A. Margin_i: Higher the value, more sensitive to background noise
    B. Margin_v: Lower the value, more foreground can pass through, suppressing the background
    C. Power: Aggressiveness



Audio Processing Steps:
1) Bandpass filter for human speech
2) Apply softmask