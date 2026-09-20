"""
RTEMS Simple Behavior Trace Visualizer
======================================

For PIP / PCP / priority inversion style traces.
This tool does not draw EDF deadline arrows.
It only shows task execution behavior and optional USER event markers.

Uses config file:
    rtems_behavior_config.py

Usage:
    python3 rtems_behavior_visualizer.py trace.csv

Output:
    rtems_behavior_timeline.png
"""

import sys
import re
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from rtems_behavior_config import *


def cfg(name, default):
    """Read optional config variable with a safe default."""
    return globals().get(name, default)


# ─────────────────────────────────────────────────────────────
# 1. TIMESTAMP PARSER
# ─────────────────────────────────────────────────────────────

def parse_timestamp(ts_str):
    """
    Parse RTEMS log timestamp into absolute microseconds.
    Expected format: "HH:MM:SS.mmm uuu nnn"
    """
    parts = ts_str.strip().split()
    hms_part, ms_part = parts[0].split('.')
    h, m, s = hms_part.split(':')
    total_s = int(h) * 3600 + int(m) * 60 + int(s)
    us_part = int(parts[1]) if len(parts) > 1 else 0
    return total_s * 1_000_000 + int(ms_part) * 1_000 + us_part


# ─────────────────────────────────────────────────────────────
# 2. LOG LINE PARSER
# ─────────────────────────────────────────────────────────────

def parse_log_line(line):
    line = line.strip()

    if not line or line.startswith('Timestamp'):
        return None

    cols = line.split('\t')

    if len(cols) < 5:
        return None

    try:
        ts_us = parse_timestamp(cols[0].strip())
    except Exception:
        return None

    event = {
        'ts_us': ts_us,
        'type': cols[3].strip(),
        'contents': cols[4].strip(),
        'tid': cols[5].strip() if len(cols) > 5 else '',
    }

    # Extract optional data=0x...
    m = re.search(r'data=(0x[0-9a-fA-F]+)', event['contents'])
    if m:
        event['data'] = int(m.group(1), 16)

    # Extract task names from sched_switch
    if event['type'] == 'sched_switch':
        pm = re.search(r'prev_comm="([^"]+)"', event['contents'])
        nm = re.search(r'next_comm="([^"]+)"', event['contents'])

        if pm:
            event['prev_comm'] = pm.group(1).strip()
        if nm:
            event['next_comm'] = nm.group(1).strip()

    return event


# ─────────────────────────────────────────────────────────────
# 3. TRACE PARSER
# ─────────────────────────────────────────────────────────────

def parse_trace(filepath):
    events = []

    with open(filepath, 'r') as f:
        for line in f:
            ev = parse_log_line(line)
            if ev:
                events.append(ev)

    if not events:
        raise RuntimeError('No valid events found in trace file.')

    switches = [e for e in events if e['type'] == 'sched_switch']

    if not switches:
        raise RuntimeError('No sched_switch events found in trace file.')

    configured_threads = set(cfg('THREADS', {}).keys())

    # Start graph from first configured task if possible.
    T0_us = next(
        (
            sw['ts_us']
            for sw in switches
            if sw.get('next_comm', '').strip() in configured_threads
        ),
        switches[0]['ts_us']
    )

    def to_ms(us):
        return (us - T0_us) / 1000

    segments = []

    for i in range(len(switches) - 1):
        segments.append({
            'thread': switches[i].get('next_comm', '').strip(),
            't0': to_ms(switches[i]['ts_us']),
            't1': to_ms(switches[i + 1]['ts_us']),
        })

    total_ms = to_ms(switches[-1]['ts_us'])

    user_events = []
    configured_events = set(cfg('EVENTS', {}).keys())

    if cfg('SHOW_USER_EVENTS', True):
        for ev in events:
            if ev['type'].startswith('USER_'):
                # If EVENTS is empty, show all USER events.
                # If EVENTS is configured, show only configured USER events.
                if configured_events and ev['type'] not in configured_events:
                    continue
                user_events.append({
                    'type': ev['type'],
                    't': to_ms(ev['ts_us']),
                    'data': ev.get('data'),
                })

    return {
        'total_ms': total_ms,
        'segments': segments,
        'user_events': user_events,
    }


# ─────────────────────────────────────────────────────────────
# 4. THREAD CONFIG
# ─────────────────────────────────────────────────────────────

def block_height(thread_name):
    if thread_name.startswith('IDLE'):
        return cfg('IDLE_LANE_H', 0.22)
    return cfg('TASK_LANE_H', 0.40)


def get_thread_color(name, index):
    special = cfg('SPECIAL_THREAD_COLORS', {})
    base = cfg('BASE_COLORS', ['#1A6FC4', '#0F8A5F', '#7A3DB8', '#D18B00'])

    if name.startswith('IDLE'):
        return special.get('IDLE', '#999990')

    if name in special:
        return special[name]

    return base[index % len(base)]


def build_thread_cfg(segments):
    seen = []

    for s in segments:
        name = s['thread']
        if name and name not in seen:
            seen.append(name)

    ordered = []
    threads_cfg = cfg('THREADS', {})

    # Configured threads first
    for name in threads_cfg.keys():
        if name in seen:
            ordered.append(name)

    # Other non-IDLE threads
    for name in seen:
        if name not in ordered and not name.startswith('IDLE'):
            ordered.append(name)

    # IDLE threads last
    for name in seen:
        if name.startswith('IDLE') and name not in ordered:
            ordered.append(name)

    thread_cfg = {}

    for i, name in enumerate(ordered):
        if name in threads_cfg:
            label = threads_cfg[name].get('label', name)
        elif name.startswith('IDLE'):
            label = 'IDLE'
        else:
            label = name

        thread_cfg[name] = {
            'label': label,
            'color': get_thread_color(name, i),
            'lane': i,
        }

    return thread_cfg


def lane_y(lane, n_lanes):
    return (n_lanes - 1 - lane) * cfg('LANE_GAP', 1.0)


# ─────────────────────────────────────────────────────────────
# 5. EVENT HELPERS
# ─────────────────────────────────────────────────────────────

def event_lane_name(event_type):
    event_cfg = cfg('EVENTS', {}).get(event_type, {})
    return event_cfg.get('map_to')


def event_label(ev):
    event_cfg = cfg('EVENTS', {}).get(ev['type'], {})
    event_name = event_cfg.get('label', ev['type'])

    if not cfg('SHOW_EVENT_DATA_LABELS', True):
        return event_name

    data_value = ev.get('data')

    # No data available in the trace event.
    # Keep label clean and do not crash.
    if data_value is None:
        return event_name

    data_labels = cfg('EVENT_DATA_LABELS', {})

    if data_value in data_labels:
        return f'{event_name}: {data_labels[data_value]}'

    if cfg('SHOW_RAW_DATA_IF_UNKNOWN', True):
        return f'{event_name}: data={data_value}'

    return event_name


def event_color(ev, thread_cfg):
    event_colors = cfg('EVENT_COLORS', {})

    if ev['type'] in event_colors:
        return event_colors[ev['type']]

    mapped_task = event_lane_name(ev['type'])

    if mapped_task in thread_cfg:
        return thread_cfg[mapped_task]['color']

    return '#333333'


# ─────────────────────────────────────────────────────────────
# 6. PLOT
# ─────────────────────────────────────────────────────────────

def plot(data):
    THREAD_CFG = build_thread_cfg(data['segments'])
    N_LANES = len(THREAD_CFG)

    fig, ax_tl = plt.subplots(
        figsize=(cfg('FIG_WIDTH', 14), cfg('FIG_HEIGHT', 6))
    )
    fig.patch.set_facecolor(cfg('BACKGROUND_COLOR', '#FAFAF8'))

    fig.subplots_adjust(
        top=cfg('GRID_TOP', 0.86),
        bottom=cfg('GRID_BOTTOM', 0.12),
        left=cfg('GRID_LEFT', 0.08),
        right=cfg('GRID_RIGHT', 0.97),
    )

    total_ms = data['total_ms']

    ax_tl.set_facecolor(cfg('AXIS_BACKGROUND_COLOR', '#F7F6F2'))
    ax_tl.set_xlim(-2, total_ms + 5)
    ax_tl.set_ylim(-0.8, (N_LANES - 1) * cfg('LANE_GAP', 1.0) + 0.8)
    ax_tl.set_xlabel('Time (ms)', fontsize=cfg('AXIS_LABEL_FONT_SIZE', 10))
    ax_tl.set_title(
        'RTEMS Task Behavior Timeline',
        fontsize=cfg('TITLE_FONT_SIZE', 11),
        fontweight='bold',
        pad=10,
    )

    yticks, ylabels = [], []

    for name, tcfg in THREAD_CFG.items():
        y = lane_y(tcfg['lane'], N_LANES)
        h = block_height(name)

        ax_tl.axhspan(
            y - h / 2 - cfg('STRIPE_EXTRA', 0.08),
            y + h / 2 + cfg('STRIPE_EXTRA', 0.08),
            color=cfg('LANE_STRIPE_COLOR', '#EDECE6'),
            alpha=0.6,
            zorder=0,
        )

        yticks.append(y)
        ylabels.append(tcfg['label'])

    ax_tl.set_yticks(yticks)
    ax_tl.set_yticklabels(ylabels, fontsize=cfg('Y_TICK_FONT_SIZE', 9))
    ax_tl.tick_params(axis='y', length=0)

    ax_tl.xaxis.set_minor_locator(
        matplotlib.ticker.MultipleLocator(cfg('MINOR_X_TICK_MS', 10))
    )

    ax_tl.grid(
        axis='x',
        which='major',
        color=cfg('MAJOR_GRID_COLOR', '#DDDDD5'),
        linewidth=0.6,
        zorder=1,
    )

    ax_tl.grid(
        axis='x',
        which='minor',
        color=cfg('MINOR_GRID_COLOR', '#EDEDEA'),
        linewidth=0.3,
        zorder=1,
    )

    ax_tl.set_xticks(range(0, int(total_ms) + 20, cfg('MAJOR_X_TICK_MS', 50)))

    # Execution blocks
    for seg in data['segments']:
        tcfg = THREAD_CFG.get(seg['thread'])

        if tcfg is None:
            continue

        y = lane_y(tcfg['lane'], N_LANES)
        dur = seg['t1'] - seg['t0']
        h = block_height(seg['thread'])

        if dur <= 0:
            continue

        rect = mpatches.FancyBboxPatch(
            (seg['t0'], y - h / 2),
            dur,
            h,
            boxstyle='round,pad=0.12',
            linewidth=0,
            facecolor=tcfg['color'],
            alpha=0.88,
            zorder=3,
        )

        ax_tl.add_patch(rect)

        if cfg('SHOW_BOX_DURATION_TEXT', True) and dur > cfg('MIN_BOX_TEXT_DURATION_MS', 2.0):
            ax_tl.text(
                seg['t0'] + dur / 2,
                y,
                f'{dur:.1f}ms',
                ha='center',
                va='center',
                fontsize=cfg('BOX_TEXT_FONT_SIZE', 7),
                fontweight='bold',
                color=cfg('BOX_TEXT_COLOR', 'white'),
                zorder=4,
            )

    # USER events
    if cfg('SHOW_USER_EVENTS', True):
        for ev in data['user_events']:
            mapped_task = event_lane_name(ev['type'])

            if mapped_task in THREAD_CFG:
                y = lane_y(THREAD_CFG[mapped_task]['lane'], N_LANES)
            else:
                y = (N_LANES - 1) * cfg('LANE_GAP', 1.0) + 0.35

            color = event_color(ev, THREAD_CFG)
            label = event_label(ev)

            ax_tl.scatter(
                ev['t'],
                y,
                s=cfg('EVENT_MARKER_SIZE', 34),
                marker='v',
                color=color,
                edgecolor='black',
                linewidth=0.4,
                zorder=6,
            )

            ax_tl.text(
                ev['t'],
                y + cfg('EVENT_TEXT_Y_OFFSET', 0.20),
                label,
                ha='center',
                va='bottom',
                fontsize=cfg('EVENT_TEXT_FONT_SIZE', 7),
                color=cfg('EVENT_TEXT_COLOR', '#222222'),
                rotation=cfg('EVENT_TEXT_ROTATION', 45),
                zorder=7,
            )

    # Legend
    legend_items = [
        mpatches.Patch(color=tcfg['color'], label=tcfg['label'])
        for tcfg in THREAD_CFG.values()
    ]

    if cfg('SHOW_USER_EVENTS', True):
        for ev_type, ev_cfg in cfg('EVENTS', {}).items():
            label = ev_cfg.get('label', ev_type)
            mapped_task = ev_cfg.get('map_to')
            fake_ev = {'type': ev_type, 'data': None}
            color = event_color(fake_ev, THREAD_CFG)
            legend_items.append(
                mpatches.Patch(color=color, label=f'{label} event')
            )

    if cfg('SHOW_LEGEND', True):
        ax_tl.legend(
            handles=legend_items,
            loc=cfg('LEGEND_LOCATION', 'lower center'),
            bbox_to_anchor=cfg('LEGEND_BBOX_ANCHOR', (0.5, 1.10)),
            fontsize=cfg('LEGEND_FONT_SIZE', 7),
            framealpha=cfg('LEGEND_FRAME_ALPHA', 0.9),
            ncol=cfg('LEGEND_COLUMNS', 4),
        )

    plt.savefig(
        cfg('OUTPUT_FILE', 'rtems_behavior_timeline.png'),
        dpi=150,
        bbox_inches='tight',
        facecolor=fig.get_facecolor(),
    )

    print(f"[INFO] Saved: {cfg('OUTPUT_FILE', 'rtems_behavior_timeline.png')}")
    plt.close()


# ─────────────────────────────────────────────────────────────
# 7. ENTRY POINT
# ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 rtems_behavior_visualizer_v3.py trace.csv')
        sys.exit(1)

    print(f'[INFO] Parsing: {sys.argv[1]}')
    data = parse_trace(sys.argv[1])

    print('============================================================')
    print(f'Trace duration : {data["total_ms"]:.1f} ms')
    print(f'Timeline blocks: {len(data["segments"])}')
    print(f'USER events    : {len(data["user_events"])}')
    print('============================================================')

    plot(data)
