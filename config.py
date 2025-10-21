# General smoothing & stability
MASTER_SMOOTHING = 0.2        # [0..1] bigger = faster response
CROSSFADER_SMOOTHING = 0.2
STABILITY_FRAMES = 4          # frames to confirm a gesture/value
SAMPLE_COOLDOWN = 0.25        # seconds between one-shot triggers

# Audio files
TRACK_A_PATH = "assets/lofi-hiphop.mp3"
TRACK_B_PATH = "assets/lofi-calm.mp3"
SAMPLE_MAP = {
    1: "assets/kickhardstyle.wav",
    2: "assets/sunflowerstreet.wav",
    3: "assets/clap.wav",
    4: "assets/fullbrass.wav",
    5: "assets/yay.wav",
}

# Mixer defaults
DEFAULT_MASTER = 0.7
DEFAULT_XFADE  = 0.5
USE_EQUAL_POWER_XFADE = False  # set True for cosine crossfade

# Camera
CAM_W = 640
CAM_H = 480
