# ============================================================
# RTEMS SIMPLE BEHAVIOR VISUALIZER CONFIG
# For PIP / PCP / priority inversion style traces
# ============================================================

# -----------------------------
# Thread / task configuration
# -----------------------------
# Add only the tasks you want to highlight.
# If color is not given, the tool picks one automatically.
THREADS = {
    'HIGH': {'label': 'High priority task'},
    'MED':  {'label': 'Medium priority task'},
    'LOW':  {'label': 'Low priority task'},
}

# -----------------------------
# Custom USER event configuration
# -----------------------------
# Keep empty if you do not want to map any USER events or use False option as mentioned below this section.
# Example:
# USER_1 -> HIGH task lane
# USER_2 -> MED task lane
# USER_3 -> LOW task lane
EVENTS = {
    'USER_1': {'label': 'HIGH', 'map_to': 'HIGH'},
    'USER_2': {'label': 'MED',  'map_to': 'MED'},
    'USER_3': {'label': 'LOW',  'map_to': 'LOW'},
}

# Data labels for event data values.
# If event data is missing, the tool prints only the event label.
# If data exists but is not listed here, it prints data=<value>.
EVENT_DATA_LABELS = {
    1: 'REQ SEM',
    2: 'GOT SEM',
    3: 'REL SEM',
    5:'woke_up'
}

SHOW_USER_EVENTS = True
SHOW_EVENT_DATA_LABELS = True
SHOW_RAW_DATA_IF_UNKNOWN = True

# -----------------------------
# Output file
# -----------------------------
OUTPUT_FILE = 'rtems_behavior_timeline.png'

# -----------------------------
# Figure layout
# -----------------------------
FIG_WIDTH = 14
FIG_HEIGHT = 6
GRID_TOP = 0.86
GRID_BOTTOM = 0.12
GRID_LEFT = 0.08
GRID_RIGHT = 0.97

# -----------------------------
# Timeline lane geometry
# -----------------------------
TASK_LANE_H = 0.40
IDLE_LANE_H = 0.22
STRIPE_EXTRA = 0.08
LANE_GAP = 1.0

# -----------------------------
# Font sizes and text
# -----------------------------
TITLE_FONT_SIZE = 11
AXIS_LABEL_FONT_SIZE = 10
Y_TICK_FONT_SIZE = 9
X_TICK_FONT_SIZE = 9

SHOW_BOX_DURATION_TEXT = True
MIN_BOX_TEXT_DURATION_MS = 2.0
BOX_TEXT_FONT_SIZE = 7
BOX_TEXT_COLOR = 'white'

EVENT_TEXT_FONT_SIZE = 7
EVENT_TEXT_COLOR = '#222222'
EVENT_TEXT_ROTATION = 45
EVENT_TEXT_Y_OFFSET = 0.20
EVENT_MARKER_SIZE = 34

# -----------------------------
# Legend control
# -----------------------------
SHOW_LEGEND = True
LEGEND_LOCATION = 'lower center'
LEGEND_BBOX_ANCHOR = (0.5, 1.10)
LEGEND_COLUMNS = 4
LEGEND_FONT_SIZE = 7
LEGEND_FRAME_ALPHA = 0.9

# -----------------------------
# Grid settings
# -----------------------------
MAJOR_X_TICK_MS = 50
MINOR_X_TICK_MS = 10

# -----------------------------
# Colors
# -----------------------------
BACKGROUND_COLOR = '#FAFAF8'
AXIS_BACKGROUND_COLOR = '#F7F6F2'
LANE_STRIPE_COLOR = '#EDECE6'
MAJOR_GRID_COLOR = '#DDDDD5'
MINOR_GRID_COLOR = '#EDEDEA'

BASE_COLORS = [
    '#1A6FC4',
    '#0F8A5F',
    '#7A3DB8',
    '#D18B00',
    '#C43D5A',
    '#008B8B',
    '#A63D1F',
    '#666666',
]

# Optional manual thread colors.
# Leave empty for automatic colors.
SPECIAL_THREAD_COLORS = {
    'IDLE': '#999990',
}

# Optional manual event colors.
# If empty, mapped events use the color of their task lane.
EVENT_COLORS = {}
