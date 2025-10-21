import time
from collections import deque
import numpy as np
from config import (
    STABILITY_FRAMES, MASTER_SMOOTHING, CROSSFADER_SMOOTHING,
    SAMPLE_COOLDOWN
)

def lerp(a, b, t): 
    return a + (b - a) * t

class DJController:
    """
    - Left hand:
        * Y-position → master volume
        * Fist (0 fingers) → pause/unpause both tracks
    - Right hand:
        * X-position → crossfader
        * 1–5 fingers → trigger one-shot samples
    """
    def __init__(self, cam_w: int, cam_h: int):
        self.w = cam_w
        self.h = cam_h

        self.left_y_hist  = deque(maxlen=STABILITY_FRAMES)
        self.right_x_hist = deque(maxlen=STABILITY_FRAMES)
        self.left_fingers_hist = deque(maxlen=STABILITY_FRAMES)
        self.right_fingers_hist = deque(maxlen=STABILITY_FRAMES)

        self.master = 0.7
        self.xfade  = 0.5
        self.master_target = self.master
        self.xfade_target  = self.xfade

        self.paused = False
        self._last_sample_time = 0.0

    def update(self, left_hand, right_hand):
        now = time.time()
        sample_to_trigger = None
        pause_change = None

        # ----- LEFT HAND: master volume & pause -----
        if left_hand:
            _, cy = left_hand.center
            vol = 1.0 - (cy / float(self.h))
            self.left_y_hist.append(vol)
            self.left_fingers_hist.append(left_hand.fingers)

            # Smooth volume
            if len(self.left_y_hist) == self.left_y_hist.maxlen:
                self.master_target = float(np.mean(self.left_y_hist))

            # Check for fist = pause/unpause
            if len(self.left_fingers_hist) == self.left_fingers_hist.maxlen:
                stable_left_fingers = int(round(float(np.median(self.left_fingers_hist))))
                if stable_left_fingers == 0:  # Fist = pause toggle
                    if not self.paused:
                        self.paused = True
                        pause_change = True   # request pause
                else:
                    if self.paused:
                        self.paused = False
                        pause_change = False  # request unpause
        else:
            self.left_y_hist.clear()
            self.left_fingers_hist.clear()

        # ----- RIGHT HAND: crossfader & sample triggers -----
        if right_hand:
            cx, _ = right_hand.center
            xf = cx / float(self.w)
            self.right_x_hist.append(xf)
            self.right_fingers_hist.append(right_hand.fingers)

            # Smooth crossfade
            if len(self.right_x_hist) == self.right_x_hist.maxlen:
                self.xfade_target = float(np.mean(self.right_x_hist))

            # Trigger samples for 1–5 fingers
            if len(self.right_fingers_hist) == self.right_fingers_hist.maxlen:
                stable_right_fingers = int(round(float(np.median(self.right_fingers_hist))))
                if 1 <= stable_right_fingers <= 5 and (now - self._last_sample_time) > SAMPLE_COOLDOWN:
                    sample_to_trigger = stable_right_fingers
                    self._last_sample_time = now
        else:
            self.right_x_hist.clear()
            self.right_fingers_hist.clear()

        # ----- Apply smoothing -----
        self.master = lerp(self.master, self.master_target, MASTER_SMOOTHING)
        self.xfade  = lerp(self.xfade,  self.xfade_target,  CROSSFADER_SMOOTHING)

        return {
            "master": self.master,
            "xfade": self.xfade,
            "pause_change": pause_change,       # True=pause, False=unpause
            "sample_to_trigger": sample_to_trigger
        }
