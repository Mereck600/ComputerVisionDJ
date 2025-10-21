import math
import pygame
from config import (
    TRACK_A_PATH, TRACK_B_PATH, SAMPLE_MAP,
    DEFAULT_MASTER, DEFAULT_XFADE, USE_EQUAL_POWER_XFADE
)

class Mixer:
    """
    Two-deck loop + one-shot samples on spare channels.
    Master and crossfade are handled inside pygame (no OS volume).
    """
    def __init__(self):
        # Lower buffer for snappier latency; raise if crackly.
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.init()
        pygame.mixer.set_num_channels(16)  # 0,1 for decks; others for samples
        self.SAMPLE_CHANNEL_START = 2


        self.track_a = pygame.mixer.Sound(TRACK_A_PATH)
        self.track_b = pygame.mixer.Sound(TRACK_B_PATH)
        self.chan_a = pygame.mixer.Channel(0)
        self.chan_b = pygame.mixer.Channel(1)

        self.master = DEFAULT_MASTER
        self.xfade = DEFAULT_XFADE
        self.paused = False

        # Loop both decks
        self.chan_a.play(self.track_a, loops=-1)
        self.chan_b.play(self.track_b, loops=-1)

        # Cache one-shots
        self.samples = {}
        for n, path in SAMPLE_MAP.items():
            try:
                self.samples[n] = pygame.mixer.Sound(path)
            except Exception as e:
                print(f"[WARN] Could not load sample {n} -> {path}: {e}")
                self.samples[n] = None

        self._apply_volumes()
    

    def _apply_volumes(self):
        if USE_EQUAL_POWER_XFADE:
            # equal-power
            a = math.cos(self.xfade * math.pi/2.0)
            b = math.cos((1.0 - self.xfade) * math.pi/2.0)
            vol_a = a * self.master
            vol_b = b * self.master
        else:
            # linear (simple & clear)
            vol_a = (1.0 - self.xfade) * self.master
            vol_b = (self.xfade) * self.master

        self.chan_a.set_volume(max(0.0, min(1.0, vol_a)))
        self.chan_b.set_volume(max(0.0, min(1.0, vol_b)))

    def set_master(self, v: float):
        self.master = max(0.0, min(1.0, float(v)))
        self._apply_volumes()

    def set_crossfade(self, x: float):
        self.xfade = max(0.0, min(1.0, float(x)))
        self._apply_volumes()

    def pause_both(self, pause=True):
        if pause:
            self.chan_a.pause()
            self.chan_b.pause()
            self.stop_samples()    # ← stop all running one-shots
            self.paused = True
        else:
            self.chan_a.unpause()
            self.chan_b.unpause()
            self.paused = False


    def trigger_sample(self, n_fingers: int):
        if self.paused:
            return  # ignore triggers while paused
        snd = self.samples.get(n_fingers)
        if snd is not None:
            ch = self._get_free_sample_channel()
            ch.play(snd)


    def shutdown(self):
        pygame.quit()
    def _get_free_sample_channel(self):
        # Try to use channels >= 2 so we never stomp on the deck channels.
        for i in range(self.SAMPLE_CHANNEL_START, pygame.mixer.get_num_channels()):
            ch = pygame.mixer.Channel(i)
            if not ch.get_busy():
                return ch
        # Fallback: force-steal some channel if all are busy (won't steal 0/1 in our normal loop)
        return pygame.mixer.find_channel(True)

    def stop_samples(self):
        # Hard stop any one-shots currently playing
        for i in range(self.SAMPLE_CHANNEL_START, pygame.mixer.get_num_channels()):
            pygame.mixer.Channel(i).stop()

