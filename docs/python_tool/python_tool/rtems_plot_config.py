# ============================================================
# RTEMS EDF VISUALIZER CONFIG
# ============================================================

# -----------------------------
# Task timing / event config
# -----------------------------
TASKS = {
    'TA': {
        'label': 'Task A',
        'period_ms': 100,
        'deadline_ms': 100,
        'marker_event': 'USER_0',
    },
    'TB': {
        'label': 'Task B',
        'period_ms': 150,
        'deadline_ms': 150,
        'marker_event': 'USER_1',
    },

    # Enable this when you add Task C
    'TC': {
        'label': 'Task C',
        'period_ms': 200,
        'deadline_ms': 200,
        'marker_event': 'USER_2',
    },
}

SHOW_LEGEND = True
LEGEND_LOCATION = 'upper right'
LEGEND_COLUMNS = 3
LEGEND_FONT_SIZE = 7
LEGEND_BBOX_ANCHOR = (0.3, 1.2)

# -----------------------------
# Output file
# -----------------------------
OUTPUT_FILE = 'rtems_edf_timeline.png'


# -----------------------------
# Figure layout
# -----------------------------
FIG_WIDTH = 14
FIG_HEIGHT = 11

GRID_HEIGHT_RATIOS = [3, 1.4, 1.4]
GRID_HSPACE = 0.55
GRID_TOP = 0.93
GRID_BOTTOM = 0.07
GRID_LEFT = 0.08
GRID_RIGHT = 0.97


# -----------------------------
# Timeline lane geometry
# -----------------------------
TASK_LANE_H = 0.40      # height of normal task boxes
IDLE_LANE_H = 0.22      # height of IDLE boxes
STRIPE_EXTRA = 0.08     # background stripe extra padding
LANE_GAP = 1.0          # vertical gap between lanes


# -----------------------------
# Font sizes
# -----------------------------
TITLE_FONT_SIZE = 11
AXIS_LABEL_FONT_SIZE = 10
Y_TICK_FONT_SIZE = 9
X_TICK_FONT_SIZE = 9

BOX_TEXT_FONT_SIZE = 4        # text inside execution boxes
DEADLINE_TEXT_FONT_SIZE = 7.5     # text above deadline arrows
COUNT_TITLE_FONT_SIZE = 10
COUNT_AXIS_FONT_SIZE = 9
COUNT_LEGEND_FONT_SIZE = 8


# -----------------------------
# Text visibility
# -----------------------------
SHOW_BOX_DURATION_TEXT = True
MIN_BOX_TEXT_DURATION_MS = 8.0


SHOW_INCOMPLETE_DEADLINES = False


# -----------------------------
# Deadline arrow layout
# -----------------------------
DEADLINE_ROW_OFFSET = 0.32
DEADLINE_ROW_GAP = 0.38

DEADLINE_ARROW_LINE_WIDTH = 1.4
DEADLINE_ARROW_MUTATION_SCALE = 10
DEADLINE_DROP_LINE_WIDTH = 0.9


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

SPECIAL_THREAD_COLORS = {
    'TA': '#1A6FC4',
    'TB': '#0F8A5F',
    'TC': '#7A3DB8',
    'DUMP': '#A63D1F',
    'IDLE': '#999990',
}
