import cv2

from config import CAM_W, CAM_H
from hands import HandTracker
from gestures import DJController
from mixer import Mixer
from hud import draw_hud

def main():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        raise RuntimeError("Could not open webcam")
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  CAM_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAM_H)

    tracker = HandTracker()
    controller = DJController(cam_w=CAM_W, cam_h=CAM_H)
    mixer = Mixer()

    try:
        while True:
            ok, frame = cap.read()
            if not ok:
                break

            frame = cv2.flip(frame, 1)

            # Vision
            hands = tracker.process(frame)  # {"Left": HandData|None, "Right": HandData|None}
            left  = hands["Left"]
            right = hands["Right"]

            # Control
            state = controller.update(left, right)

            # Apply to audio
            mixer.set_master(state["master"])
            mixer.set_crossfade(state["xfade"])

            if state["pause_change"] is True:
                mixer.pause_both(True)
            elif state["pause_change"] is False:
                mixer.pause_both(False)

            if state["sample_to_trigger"] is not None:
                mixer.trigger_sample(state["sample_to_trigger"])

            # HUD & landmarks
            draw_hud(frame, {
                "master": mixer.master,
                "xfade": mixer.xfade,
                "paused": mixer.paused
            })
            tracker.draw_hands(frame, hands)

            cv2.imshow("CV DJ", frame)
            if cv2.waitKey(1) & 0xFF == 27:  # ESC
                break
    finally:
        cap.release()
        cv2.destroyAllWindows()
        mixer.shutdown()

if __name__ == "__main__":
    main()
