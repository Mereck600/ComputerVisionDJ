import cv2

def draw_hud(frame, mixer_state):
    h, w = frame.shape[:2]
    master = mixer_state.get("master", 0.0)
    xfade  = mixer_state.get("xfade", 0.5)
    paused = mixer_state.get("paused", False)

    # Master vertical bar on right
    bar_x1, bar_x2 = w - 40, w - 20
    top, bottom    = 20, h - 20
    filled_y = int(top + (1.0 - master) * (bottom - top))
    cv2.rectangle(frame, (bar_x1, top), (bar_x2, bottom), (80,80,80), -1)
    cv2.rectangle(frame, (bar_x1, filled_y), (bar_x2, bottom), (0,255,0), -1)
    cv2.putText(frame, "VOL", (w-58, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1)

    # Crossfader horizontal
    line_y = h - 40
    cv2.line(frame, (20, line_y), (w-20, line_y), (80,80,80), 6)
    xfade_px = int(20 + xfade * (w - 40))
    cv2.circle(frame, (xfade_px, line_y), 8, (0,200,255), -1)
    cv2.putText(frame, "A", (10, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)
    cv2.putText(frame, "B", (w-15, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255,255,255), 1)

    # Pause state
    if paused:
        cv2.putText(frame, "PAUSED", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,0,255), 2)
