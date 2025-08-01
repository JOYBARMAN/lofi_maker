import os
import numpy as np

from email.mime import audio
from pydub import AudioSegment
from mutagen.easyid3 import EasyID3
from mutagen.mp3 import MP3


class LofiMaker:
    def __init__(
        self,
        song_path: str,
        slow_down: bool = True,
        slow_speed: float = 0.85,
        surround: bool = False,
        surround_cycle_duration: float = 14.0,
        surround_depth: float = 0.7,
        reverb: bool = True,
        reverb_decay: float = 0.3,
        reverb_delay_ms: int = 120,
        reverb_repeats: int = 2,
        target_dBFS=-1.0,
        dimension: bool = False,
        dimension_number: int = 8,
        dimension_cycle: float = 4.0,
    ):
        self.song_path = song_path
        self.audio = self.load_audio()
        self.slow_down = slow_down
        self.slow_speed = slow_speed
        self.surround = surround
        self.surround_cycle_duration = surround_cycle_duration
        self.surround_depth = surround_depth
        self.reverb = reverb
        self.reverb_decay = reverb_decay
        self.reverb_delay_ms = reverb_delay_ms
        self.reverb_repeats = reverb_repeats
        self.dimension = dimension
        self.dimension_number = dimension_number
        self.dimension_cycle = dimension_cycle
        self.target_dBFS = target_dBFS
        self.song_title = self.get_song_title()
        self.output_path = self.get_output_path()

    def load_audio(self):
        """Load audio file"""
        try:
            return AudioSegment.from_file(self.song_path)
        except Exception as e:
            raise ValueError(f"Error loading audio file: {e}")

    def get_song_title(self):
        """Extract title from metadata, fallback to filename"""
        try:
            audio = MP3(self.song_path, ID3=EasyID3)
            title = audio.get("title", [None])[0]
            if title:
                return title
        except Exception:
            pass

        # Fallback to filename if title is not available
        return os.path.splitext(os.path.basename(self.song_path))[0]

    def slow_audio(self):
        """Slow down the audio"""
        self.audio = self.audio._spawn(
            self.audio.raw_data,
            overrides={"frame_rate": int(self.audio.frame_rate * self.slow_speed)},
        ).set_frame_rate(self.audio.frame_rate)
        return self.audio

    def reverb_audio(self):
        """Apply reverb effect"""
        samples = np.array(self.audio.get_array_of_samples()).astype(np.float32)
        sample_rate = self.audio.frame_rate
        delay_samples = int(sample_rate * self.reverb_delay_ms / 1000)

        if self.audio.channels == 2:
            samples = samples.reshape((-1, 2))
            output = np.copy(samples)
            for i in range(1, self.reverb_repeats + 1):
                atten = np.zeros_like(samples)
                atten[delay_samples * i :] = samples[: -delay_samples * i] * (
                    self.reverb_decay**i
                )
                output += atten
            output /= np.max(np.abs(output))  # normalize
            samples = output.flatten()
        else:
            output = np.copy(samples)
            for i in range(1, self.reverb_repeats + 1):
                delayed = np.zeros_like(samples)
                delayed[delay_samples * i :] = samples[: -delay_samples * i] * (
                    self.reverb_decay**i
                )
                output += delayed
            samples = output / np.max(np.abs(output))

        samples = (samples * 32767).astype(np.int16)
        self.audio = self.audio._spawn(samples.tobytes())
        return self.audio

    def surround_audio(self):
        """Apply surround audio effect"""

        if self.audio.channels != 2:
            raise ValueError("Surround effect requires stereo audio.")

        samples = np.array(self.audio.get_array_of_samples()).astype(np.float32)
        sample_rate = self.audio.frame_rate
        stereo = samples.reshape((-1, 2))
        total_samples = stereo.shape[0]

        # Depth controls how far left/right it pans. 1.0 = full pan, 0.0 = no pan.
        for i in range(total_samples):
            t = (i / sample_rate) % self.surround_cycle_duration
            pan = (
                np.sin(2 * np.pi * t / self.surround_cycle_duration)
                * self.surround_depth
            )
            left_gain = (1 + pan) / 2
            right_gain = (1 - pan) / 2
            stereo[i, 0] *= left_gain
            stereo[i, 1] *= right_gain

        # Normalize to avoid volume drop
        max_val = np.max(np.abs(stereo))
        stereo = stereo / max_val * 32767
        stereo = stereo.astype(np.int16).flatten()
        self.audio = self.audio._spawn(stereo.tobytes())
        return self.audio

    def apply_nd_audio_effect(self):
        """
        Apply stereo panning effect for N-dimensional audio illusion.
        """
        if self.audio.channels != 2:
            raise ValueError("N-D audio effect requires stereo input.")

        samples = np.array(self.audio.get_array_of_samples())
        sample_rate = self.audio.frame_rate
        stereo = samples.reshape((-1, 2))
        total_samples = stereo.shape[0]

        # Higher dimension = longer cycle duration (slower movement)
        cycle_duration = self.dimension_cycle * (self.dimension_number / 8.0)

        for i in range(total_samples):
            t = (i / sample_rate) % cycle_duration
            pan = np.sin(2 * np.pi * t / cycle_duration)
            left_gain = (1 + pan) / 2
            right_gain = (1 - pan) / 2
            stereo[i, 0] = int(stereo[i, 0] * left_gain)
            stereo[i, 1] = int(stereo[i, 1] * right_gain)

        stereo = stereo.flatten()
        self.audio = self.audio._spawn(stereo.tobytes())
        return self.audio

    def normalize_audio(self):
        """
        Normalize audio without distorting or making it harsh.
        """
        change_in_dBFS = self.target_dBFS - self.audio.max_dBFS
        self.audio = self.audio.apply_gain(change_in_dBFS)
        return self.audio

    def process(self):
        """Process the audio file according to the initialization parameters"""

        self.slow_audio() if self.slow_down else self.audio
        self.reverb_audio() if self.reverb else self.audio
        self.surround_audio() if self.surround else self.audio
        self.apply_nd_audio_effect() if self.dimension else self.audio

        return self.normalize_audio()

    def export_audio(self):
        """Export processed audio to a file"""
        self.audio.export(self.output_path, format="mp3", bitrate="320k")

    def get_output_path(self):
        """Generate output path based on input file name"""
        # Create directory if it doesn't exist
        os.makedirs("musics", exist_ok=True)
        base, ext = os.path.splitext(self.song_path)
        return os.path.join("musics", f"{self.song_title}_converted{ext}")

    def convert_audio(self):
        """Convert audio"""
        # Process the audio
        self.process()
        # Export the audio
        self.export_audio()
        return self.output_path


# Example usage
if __name__ == "__main__":
    input_song = "/home/joy/musics/song.mp3"
    print("Processing song:.........................")
    lofi_maker = LofiMaker(song_path=input_song)
    output_path = lofi_maker.convert_audio()
    print(f"Processed song saved to: {output_path}")
