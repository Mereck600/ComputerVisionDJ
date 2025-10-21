from dataclasses import dataclass
from typing import Optional, Dict, Any

import cv2
import numpy as np
import mediapipe as mp

@dataclass
class HandData:
    label: str                 # "Left" or "Right"
    center: tuple[float, float]# (cx, cy) in pixels
    fingers: int               # 0..5
    landmarks: Any             # mediapipe landmarks (for optional drawing)

class HandTracker:
    def __init__(self, max_num_hands=2, det_conf=0.6, trk_conf=0.6):
        self.mp_hands = mp.solutions.hands
        self._hands = self.mp_hands.Hands(
            static_image_mode=False,
            max_num_hands=max_num_hands,
            min_detection_confidence=det_conf,
            min_tracking_confidence=trk_conf
        )
        self.draw = mp.solutions.drawing_utils
        self.style = mp.solutions.drawing_styles

    @staticmethod
    def _hand_center(lm, w, h):
        pts = np.array([(p.x * w, p.y * h) for p in lm.landmark], dtype=np.float32)
        return float(pts[:, 0].mean()), float(pts[:, 1].mean())

    @staticmethod
    def _count_fingers(lm, label, w, h) -> int:
        TIP = [4, 8, 12, 16, 20]
        PIP = [3, 6, 10, 14, 18]
        pts = np.array([(p.x * w, p.y * h) for p in lm.landmark], dtype=np.float32)

        up = 0
        # index..pinky: tip above pip
        for tip_i, pip_i in zip(TIP[1:], PIP[1:]):
            if pts[tip_i, 1] < pts[pip_i, 1] - 8:
                up += 1

        # thumb
        thumb_tip = pts[TIP[0], 0]
        thumb_ip  = pts[PIP[0], 0]
        if label == "Right":
            if thumb_tip > thumb_ip + 8:
                up += 1
        else:
            if thumb_tip < thumb_ip - 8:
                up += 1
        return int(up)

    def process(self, frame_bgr) -> Dict[str, Optional[HandData]]:
        h, w = frame_bgr.shape[:2]
        rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
        res = self._hands.process(rgb)

        data = {"Left": None, "Right": None}
        if res.multi_hand_landmarks and res.multi_handedness:
            for lm, handed in zip(res.multi_hand_landmarks, res.multi_handedness):
                label = handed.classification[0].label  # "Left"/"Right"
                cx, cy = self._hand_center(lm, w, h)
                fingers = self._count_fingers(lm, label, w, h)
                data[label] = HandData(label=label, center=(cx, cy), fingers=fingers, landmarks=lm)
        return data

    def draw_hands(self, frame_bgr, hand_data: Dict[str, Optional[HandData]]):
        for side in ("Left", "Right"):
            hd = hand_data.get(side)
            if hd and hd.landmarks:
                self.draw.draw_landmarks(
                    frame_bgr, hd.landmarks, self.mp_hands.HAND_CONNECTIONS,
                    self.style.get_default_hand_landmarks_style(),
                    self.style.get_default_hand_connections_style()
                )
