# Rtems Visualization Qasim

# RTEMS Visualization & Scheduling Tutorials
> **University of Freiburg** | Team Betriebssysteme 2026

This lab has been done as research-based work on RTEMS under the supervision of Dr. Tobias Seufert.  
This repository contains a series of lab tutorials designed to explore Real-Time Operating Systems (RTOS) using RTEMS on the ERC32 simulator.

The repository [repo](/Pre-built_Rtems_Toolsuite_BSP) Pre-built_Rtems_Toolsuite_BSP  contains all the examples used in this tutorial. Each example includes a compiled app.exe, so the applications can be executed directly.

### Determinstic Computution time:

The  tutorials use a software loop to simulate computation time:

for (volatile int i = 0; i < 14000; i++);/*  Simulated Work: ~20ms (14000 ) */

When executed on the SIS SPARC/ERC32 emulator, this loop produced consistent execution times across different host systems, making it suitable for modeling CPU workload in the scheduling experiments.

In Tutorial 12, we studied `rtems_counter_delay_nanoseconds()`, which provides deterministic delays using the RTEMS Counter API. However, the hardware counter continues running even when a task is preempted. As a result, the API measures elapsed (wall-clock) time rather than the amount of CPU time actually consumed by the task. Therefore, it is useful for precise delays and understanding RTEMS timing infrastructure, but it is not suitable for simulating computation demand in  scheduling experiments.

For a more accurate approach, the loop can be replaced by the custom `cpu_work_run_ms()`API  which uses `rtems_counter_read` API and it is explained in the  tutorial12.you can replace for loop with this API by few steps.

### Python-Based Trace Visualization

In Tutorial 13, an additional Python-based visualization approach is introduced to make RTEMS trace analysis easier. While Eclipse Trace Compass is useful for precise cursor-based timing analysis, understanding the overall scheduling behavior can still be difficult from raw trace views.

The Python tools generate clearer timeline plots from exported trace logs. One tool is used for EDF analysis, including task execution, period counts, and deadline arrows. A second simplified tool is used for PIP, PCP, and priority inversion examples, where the focus is mainly on task execution order, preemption, blocking behavior, and custom RTEMS user events.



## NOTE
I have used ubuntu 24.04 to build toolchain. When moving the toolchain from Ubuntu 24.04 to older machines, you will encounter the error:

```bash
libc.so.6: version GLIBC_2.38 not found
```
##### Cause: Binaries compiled on Ubuntu 24 (GLIBC 2.39/2.38) are not backward compatible with older systems (e.g., Ubuntu 20/22).

##### Solution: Rebuild the RTEMS toolchain using the RTEMS Source Builder (RSB) locally on the target machine to ensure the compiler links correctly with the local C library.





### Quick start.



#### Download the [repo](/Pre-built_Rtems_Toolsuite_BSP) and extract.

```bash
tar -xzvf quick-start.tar.gz

```

#### Config 

#####  NOTE :
Encountered a 'python command not found' error during the RTEMS config or build process. This is a common regression in recent Linux distributions where the python symlink is omitted. Resolved the issue by installing the python-is-python3 package, which maps the generic python call to the python3 binary, satisfying the Waf build system requirements.

```bash
sudo apt update
sudo apt install python-is-python3

```

```bash
cd $HOME/quick-start/app/hello

./waf configure   --rtems=$HOME/quick-start/rtems/6   --rtems-tools=$HOME/quick-start/rtems/6   --rtems-bsp=sparc/erc32

```

#### Build

```bash
./waf

```

#### Run

```bash
cd $HOME/quick-start/app/hello/build/sparc-rtems6-erc32

export PATH=$HOME/quick-start/rtems/6/bin:"$PATH" 

rtems-run --rtems-bsps=erc32-sis  hello.exe

```

#### Follow [Tutorial 3: Capturing System Logs Through a Fatal Error Handler](/docs/log_collection/README.md) for log Collection and
#### [Tutorial 4: Visualization using Eclipse Trace Compass](./docs/Visualization/README.md) for  Visualization





##  Tutorials

### [Tutorial 1: Preparation & Toolchain](./docs/preparation/README.md)
Hardware requirements, software tools, and setting up the RSB (RTEMS Source Builder).

### [Tutorial 2: Build Your Application](./docs/build_application/README.md)
create a simple  application  using the Waf build system.

### [Tutorial 3: Capturing System Logs Through a Fatal Error Handler](./docs/log_collection/README.md)
This mechanism utilizes high-performance, per-processor ring buffers to capture high-frequency system events (such as context switches and interrupts) for real-time monitoring and post-mortem failure analysis.

### [Tutorial 4: Visualization using Eclipse Trace Compass](./docs/Visualization/README.md)
Visualization using Eclipse Trace Compass by Simple Example.

### [Tutorial 5: Trace Analysis of the Example from Tutorial 3](./docs/Trace_Analysis/README.md)
The analysis focuses on sleep periods, task switching, and time clipping to make it easier to understand the examples in the following tutorials.

### [Tutorial 6: High-Frequency Logging and Buffer Saturation](./docs/Ring_Buffer/README.md)
This analysis explores how to select the correct capture window for trace events.

### [Tutorial 7: EDF Scheduling](./docs/edf_analysis/README.md)
Introduction to Earliest Deadline First scheduling and Visualization in RTEMS.

### [Tutorial 8: Priority Inversion in RTEMS ](./docs/Priority_inversion/README.md)
Understanding Priority inversion with the help of Course Slides and Eclipse Trace Client.

### [Tutorial 9: Priority Inheritance  Protocols (PIP) and Dead locks in RTEMS](./docs/PIP/README.md)
Understanding  Priority Inheritance  Protocols and deadlocks (Error 0x72).

### [Tutorial 10: Immediate Ceiling Priority Protocol(ICPP)](./docs/ICPP/README.md)
Understanding the Immediate Ceiling Priority Protocol (ICPP) using the example provided in Tutorial 9, and demonstrating how this protocol helps avoid deadlock situations.

### [Tutorial 11: Introduction to rtems kernel](./docs/kernel/README.md)
The RTEMS Kernel 6.1 source code was downloaded, modified, and analyzed using printk to observe the internal behaviour.

### [Tutorial 12: Understanding of Counter API for Determinstic timing and EDF Scheduling](./docs/counter/README.md)
This tutorial explains the RTEMS Counter API by analyzing the RTEMS kernel, the ERC32 BSP, and the hardware datasheet, with a focus on how the Real-Time Clock (RTC) is used for timing.

### [Tutorial 13: EDF Trace Analysis Visualization using `python_tool`](./docs/python_tool/README.md)
using Python-based tools to visualize EDF trace data and other scheduling traces (e.g PIP,PCP,deadlocks) more clearly.

## Software Requirements
* **Target:** SIS (ERC32) Simulator.
* **OS:** RTEMS 6.
* **Tools:** RTEMS Source Builder, Eclipse Trace Compass for visualization.
