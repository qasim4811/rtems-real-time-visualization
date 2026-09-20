"""
RTEMS EDF Trace Visualizer
===========================

Uses separate config file:
    rtems_plot_config.py

Usage:

python3 rtems_edf_visualizer.py <filename>.<txt|csv>

e.g

python rtems_edf_visualizer.py trace.csv

Output:
    rtems_edf_timeline.png
"""

import sys
import re
import matplotlib
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

from rtems_plot_config import *


# ─────────────────────────────────────────────────────────────
# 1. TIMESTAMP PARSER
# ─────────────────────────────────────────────────────────────

def parse_timestamp(ts_str):
    """
    Parse RTEMS log timestamp → absolute microseconds.
    Format: "HH:MM:SS.mmm uuu nnn"
    """
    parts = ts_str.strip().split()
    hms_part, ms_part = parts[0].split('.')
    h, m, s = hms_part.split(':')
    total_s = int(h) * 3600 + int(m) * 60 + int(s)

    return total_s * 1_000_000 + int(ms_part) * 1_000 + int(parts[1])


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
        'ts_us':    ts_us,
        'type':     cols[3].strip(),
        'contents': cols[4].strip(),
        'tid':      cols[5].strip() if len(cols) > 5 else '',
    }

    # Extract data=0x...
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
# 3. TRACE FILE PARSER
# ─────────────────────────────────────────────────────────────

def parse_trace(filepath):
    events = []

    with open(filepath, 'r') as f:
        for line in f:
            ev = parse_log_line(line)
            if ev:
                events.append(ev)

    if not events:
        raise RuntimeError("No valid events found in trace file.")

    switches = [e for e in events if e['type'] == 'sched_switch']

    if not switches:
        raise RuntimeError("No sched_switch events found in trace file.")

    configured_task_names = set(TASKS.keys())

    # Start graph from first configured task if possible.
    T0_us = next(
        (
            sw['ts_us']
            for sw in switches
            if sw.get('next_comm', '').strip() in configured_task_names
        ),
        switches[0]['ts_us']
    )

    def to_ms(us):
        return (us - T0_us) / 1000

    # Execution segments
    segments = []

    for i in range(len(switches) - 1):
        segments.append({
            'thread': switches[i].get('next_comm', '').strip(),
            't0':     to_ms(switches[i]['ts_us']),
            't1':     to_ms(switches[i + 1]['ts_us']),
        })

    total_ms = to_ms(switches[-1]['ts_us'])

    # Task markers and theoretical releases
    markers_by_task = {}

    for task_name, cfg in TASKS.items():
        ev_type = cfg['marker_event']
        period_ms = cfg['period_ms']
        deadline_ms = cfg['deadline_ms']

        evts = [e for e in events if e['type'] == ev_type]

        markers = []

        if not evts:
            markers_by_task[task_name] = markers
            continue

        first_marker_ms = to_ms(evts[0]['ts_us'])
        first_count = evts[0].get('data', 0)

        for idx, ev in enumerate(evts):
            actual_marker_ms = to_ms(ev['ts_us'])
            count = ev.get('data', idx)

            period_index_from_count = count - first_count

            if period_index_from_count >= 0:
                job_index = period_index_from_count
            else:
                job_index = idx

            release_ms = first_marker_ms + job_index * period_ms

            markers.append({
                'start': release_ms,
                'period': deadline_ms,
                'deadline': release_ms + deadline_ms,
                'count': count,
                'job_index': job_index,
                'actual_marker': actual_marker_ms,
                'marker_delay': actual_marker_ms - release_ms,
                'event': ev_type,
            })

        markers_by_task[task_name] = markers

    # Counts for lower plot
    counts_by_task = {}

    for task_name, markers in markers_by_task.items():
        counts_by_task[task_name] = [
            {
                't': m['start'],
                'n': m['count'],
            }
            for m in markers
        ]

    exec_by_task = {}

    for task_name in TASKS.keys():
        exec_by_task[task_name] = [
            {
                't0': s['t0'],
                'dur': s['t1'] - s['t0'],
            }
            for s in segments
            if s['thread'] == task_name
        ]

    return dict(
        total_ms=total_ms,
        segments=segments,
        markers_by_task=markers_by_task,
        counts_by_task=counts_by_task,
        exec_by_task=exec_by_task,
    )


# ─────────────────────────────────────────────────────────────
# 4. THREAD CONFIG
# ─────────────────────────────────────────────────────────────

def block_height(thread_name):
    if thread_name.startswith('IDLE'):
        return IDLE_LANE_H
    return TASK_LANE_H


def get_thread_color(name, index):
    if name.startswith('IDLE'):
        return SPECIAL_THREAD_COLORS.get('IDLE', '#999990')

    if name in SPECIAL_THREAD_COLORS:
        return SPECIAL_THREAD_COLORS[name]

    return BASE_COLORS[index % len(BASE_COLORS)]


def build_thread_cfg(segments):
    """
    Automatic lanes:
      configured tasks first,
      then other non-IDLE threads,
      then IDLE.
    """

    seen = []

    for s in segments:
        name = s['thread']
        if name and name not in seen:
            seen.append(name)

    ordered = []

    for task_name in TASKS.keys():
        if task_name in seen:
            ordered.append(task_name)

    for name in seen:
        if name not in ordered and not name.startswith('IDLE'):
            ordered.append(name)

    for name in seen:
        if name.startswith('IDLE') and name not in ordered:
            ordered.append(name)

    thread_cfg = {}

    for i, name in enumerate(ordered):
        if name in TASKS:
            label = TASKS[name]['label']
        elif name.startswith('IDLE'):
            label = 'IDLE'
        else:
            label = name

        color = get_thread_color(name, i)

        thread_cfg[name] = {
            'color': color,
            'label': label,
            'lane': i,
        }

    return thread_cfg


def lane_y(lane, n_lanes):
    return (n_lanes - 1 - lane) * LANE_GAP


# ─────────────────────────────────────────────────────────────
# 5. PLOT
# ─────────────────────────────────────────────────────────────

def plot(data):
    THREAD_CFG = build_thread_cfg(data['segments'])
    N_LANES = len(THREAD_CFG)

    fig = plt.figure(figsize=(FIG_WIDTH, FIG_HEIGHT))
    fig.patch.set_facecolor(BACKGROUND_COLOR)

    gs = fig.add_gridspec(
        3,
        1,
        height_ratios=GRID_HEIGHT_RATIOS,
        hspace=GRID_HSPACE,
        top=GRID_TOP,
        bottom=GRID_BOTTOM,
        left=GRID_LEFT,
        right=GRID_RIGHT,
    )

    ax_tl = fig.add_subplot(gs[0])
    ax_cnt = fig.add_subplot(gs[1])

    total_ms = data['total_ms']

    # Timeline
    ax_tl.set_facecolor(AXIS_BACKGROUND_COLOR)
    ax_tl.set_xlim(-2, total_ms + 5)
    ax_tl.set_ylim(-0.8, (N_LANES - 1) * LANE_GAP + 1.2)
    ax_tl.set_xlabel('Time (ms)', fontsize=AXIS_LABEL_FONT_SIZE)
    ax_tl.set_title(
        'EDF Scheduler Timeline ',
        fontsize=TITLE_FONT_SIZE,
        fontweight='bold',
        pad=10,
    )

    yticks, ylabels = [], []

    for name, cfg in THREAD_CFG.items():
        y = lane_y(cfg['lane'], N_LANES)
        h = block_height(name)

        ax_tl.axhspan(
            y - h / 2 - STRIPE_EXTRA,
            y + h / 2 + STRIPE_EXTRA,
            color=LANE_STRIPE_COLOR,
            alpha=0.6,
            zorder=0,
        )

        yticks.append(y)
        ylabels.append(cfg['label'])

    ax_tl.set_yticks(yticks)
    ax_tl.set_yticklabels(ylabels, fontsize=Y_TICK_FONT_SIZE)
    ax_tl.tick_params(axis='y', length=0)

    ax_tl.xaxis.set_minor_locator(
        matplotlib.ticker.MultipleLocator(MINOR_X_TICK_MS)
    )

    ax_tl.grid(
        axis='x',
        which='major',
        color=MAJOR_GRID_COLOR,
        linewidth=0.6,
        zorder=1,
    )

    ax_tl.grid(
        axis='x',
        which='minor',
        color=MINOR_GRID_COLOR,
        linewidth=0.3,
        zorder=1,
    )

    ax_tl.set_xticks(range(0, int(total_ms) + 20, MAJOR_X_TICK_MS))

    # Execution blocks
    for seg in data['segments']:
        cfg = THREAD_CFG.get(seg['thread'])

        if cfg is None:
            continue

        y = lane_y(cfg['lane'], N_LANES)
        dur = seg['t1'] - seg['t0']
        h = block_height(seg['thread'])

        if dur <= 0:
            continue

        rect = mpatches.FancyBboxPatch(
            (seg['t0'], y - h / 2),
            dur,
            h,
            boxstyle='round,pad=0.5',
            linewidth=0,
            facecolor=cfg['color'],
            alpha=0.88,
            zorder=3,
        )

        ax_tl.add_patch(rect)

        if SHOW_BOX_DURATION_TEXT and dur > MIN_BOX_TEXT_DURATION_MS:
            ax_tl.text(
                seg['t0'] + dur / 2,
                y,
                f'{dur:.1f}ms',
                ha='center',
                va='center',
                fontsize=BOX_TEXT_FONT_SIZE,
                fontweight='bold',
                color='white',
                zorder=4,
            )

    # Deadline arrows
    def draw_deadline_row(ax, deadlines, color, y_row, lane):
        lane_top = lane_y(lane, N_LANES) + TASK_LANE_H / 2 + 0.08

        for i, d in enumerate(deadlines):
            x0 = d['start']
            xD = d['deadline']

            if not SHOW_INCOMPLETE_DEADLINES and xD > total_ms:
                continue

            ax.annotate(
                '',
                xy=(xD, y_row),
                xytext=(x0, y_row),
                arrowprops=dict(
                    arrowstyle='->',
                    color=color,
                    lw=DEADLINE_ARROW_LINE_WIDTH,
                    mutation_scale=DEADLINE_ARROW_MUTATION_SCALE,
                ),
                zorder=5,
            )

            ax.plot(
                [x0, x0],
                [y_row - 0.07, y_row + 0.07],
                color=color,
                lw=DEADLINE_ARROW_LINE_WIDTH,
                zorder=5,
            )

            mid_x = (x0 + xD) / 2
            p_num = d.get('count', i + 1)

            ax.text(
                mid_x,
                y_row + 0.10,
                f'P{p_num}: {d["period"]:.1f}ms',
                ha='center',
                va='bottom',
                fontsize=DEADLINE_TEXT_FONT_SIZE,
                color=color,
                fontweight='500',
                zorder=6,
            )

            ax.plot(
                [xD, xD],
                [y_row - 0.06, lane_top],
                color=color,
                lw=DEADLINE_DROP_LINE_WIDTH,
                linestyle=(0, (4, 3)),
                alpha=0.65,
                zorder=4,
            )

    top_of_lanes = (N_LANES - 1) * LANE_GAP + TASK_LANE_H / 2 + 0.08

    for idx, task_name in enumerate(TASKS.keys()):
        if task_name not in THREAD_CFG:
            continue

        cfg = THREAD_CFG[task_name]
        deadlines = data['markers_by_task'].get(task_name, [])

        if not deadlines:
            continue

        draw_deadline_row(
            ax_tl,
            deadlines,
            color=cfg['color'],
            y_row=top_of_lanes + DEADLINE_ROW_OFFSET + idx * DEADLINE_ROW_GAP,
            lane=cfg['lane'],
        )

    extra_arrow_space = max(0, len(TASKS) - 2) * DEADLINE_ROW_GAP
    ax_tl.set_ylim(
        -0.8,
        (N_LANES - 1) * LANE_GAP + 1.2 + extra_arrow_space,
    )

    legend_patches = [
        mpatches.Patch(color=cfg['color'], label=cfg['label'])
        for cfg in THREAD_CFG.values()
    ]

    for task_name in TASKS.keys():
        if task_name not in THREAD_CFG:
            continue

        cfg = THREAD_CFG[task_name]
        legend_patches.append(
            mpatches.Patch(
                color=cfg['color'],
                label=f'{cfg["label"]} deadline ({TASKS[task_name]["marker_event"]})',
            )
        )

    if SHOW_LEGEND:
        ax_tl.legend(
        handles=legend_patches,
        loc=LEGEND_LOCATION,
        fontsize=LEGEND_FONT_SIZE,
        framealpha=0.85,
        bbox_to_anchor=LEGEND_BBOX_ANCHOR,

        ncol=LEGEND_COLUMNS,
        )

    # Count plot
    ax_cnt.set_facecolor(AXIS_BACKGROUND_COLOR)
    ax_cnt.set_title(
        'Period count over time',
        fontsize=COUNT_TITLE_FONT_SIZE,
        fontweight='bold',
    )
    ax_cnt.set_xlabel('Time (ms)', fontsize=COUNT_AXIS_FONT_SIZE)
    ax_cnt.set_ylabel('Count', fontsize=COUNT_AXIS_FONT_SIZE)

    line_styles = ['o-', 's--', '^-', 'd--', 'x-', 'v--']

    for idx, task_name in enumerate(TASKS.keys()):
        if task_name not in THREAD_CFG:
            continue

        counts = data['counts_by_task'].get(task_name, [])

        if not counts:
            continue

        t_vals = [c['t'] for c in counts]
        n_vals = [c['n'] for c in counts]

        cfg = THREAD_CFG[task_name]
        style = line_styles[idx % len(line_styles)]

        ax_cnt.plot(
            t_vals,
            n_vals,
            style,
            color=cfg['color'],
            lw=2,
            ms=6,
            label=f'{cfg["label"]} ({TASKS[task_name]["marker_event"]})',
            zorder=3,
        )

    ax_cnt.set_xlim(0, total_ms + 10)
    ax_cnt.set_xticks(range(0, int(total_ms) + 20, MAJOR_X_TICK_MS))
    ax_cnt.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(integer=True))
    ax_cnt.grid(color=MAJOR_GRID_COLOR, linewidth=0.6, zorder=0)
    ax_cnt.set_axisbelow(True)
    ax_cnt.legend(fontsize=COUNT_LEGEND_FONT_SIZE)

    plt.savefig(
        OUTPUT_FILE,
        dpi=150,
        bbox_inches='tight',
        facecolor=fig.get_facecolor(),
    )

    print(f'[INFO] Saved: {OUTPUT_FILE}')
    plt.close()


# ─────────────────────────────────────────────────────────────
# 6. ENTRY POINT
# ─────────────────────────────────────────────────────────────

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('Usage: python3 rtems_edf_visualizer.py trace.txt')
        sys.exit(1)

    print(f'[INFO] Parsing: {sys.argv[1]}')

    data = parse_trace(sys.argv[1])

    print('============================================================')
    print(f'Trace duration : {data["total_ms"]:.1f} ms')
    print('Configured tasks:')

    for task_name, cfg in TASKS.items():
        print(
            f'  {task_name}: period={cfg["period_ms"]} ms, '
            f'deadline={cfg["deadline_ms"]} ms, '
            f'marker={cfg["marker_event"]}'
        )

    print('============================================================')

    plot(data)