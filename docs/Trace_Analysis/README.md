# Tutorial 5: Trace Analysis of the Example from Tutorial 3
> **Goal:** Analyzing the generated traces through visualization as well as by examining the raw trace data.

## Introduction
From Tutorials 1 to 4, we learned how to configure, build, run, and visualize RTEMS application. In this tutorial, we will use the example from Tutorial 3 to perform further analysis of the visualization. Specifically, we will examine the trace data to understand how the RTEMS tick affects the sleep period.

## Optimize the View
It is a always good practice to optimze the view before doing further analysis.
### Before
![Help](/docs/Trace_Analysis/docs/1.png)

### After
![Help](/docs/Trace_Analysis/docs/2.png)

### Birth Time
By default, our system clock starts at 1970-01-01 02:11:00. I tried changing this within the app.c code and using the 'Time Offset' feature in the Eclipse Trace Client, but neither successfully reset the timeline to zero. Because of this, we will be using the default system time as our reference point for this tutorial and all future ones. Don't worry about the 1970 date—just focus on the time gaps between the events!".If you are able to adjust, feel free to share it with me.

### Analyzing Dump Task.

As illustrated in the figure below, the Init task (labeled as UI1 in the trace) is the first to execute. Its primary role is to initialize the system and create three separate tasks: DUMP, TA (Task A), and TB (Task B).
The custom event defined in our code as ```#define EVT_TA RTEMS_RECORD_USER(1)``` appears in Trace Compass under the label USER 1.

For Task A, the trace successfully captures the specific data value 0x05 that was sent during the event production.
![Help](/docs/Trace_Analysis/docs/3.png)

To allow for the execution of Task A and Task B, the DUMP task immediately enters a sleep state for 500ms upon starting.

As shown in the figure below, the DUMP task sleeps for 500 ms and, upon waking up, generates a custom event  ```RTEMS_RECORD_USER(3)``` and sends the data value 0x0, as defined in the code.

![Help](/docs/Trace_Analysis/docs/4.png)

### Analyzing Task A.
Once the high-priority DUMP task enters its sleep state, Task A (medium priority) wakes up and begins execution as shown in Figure Below.
As part of its routine, Task A performs the following actions:

- Custom Event Generation: It triggers a custom event using RTEMS_RECORD_USER(1).

- Data Transmission: It sends the value 0x05, which is clearly visible in the trace logs.

- Sleep Command: It issues a request to sleep for 12ms.

An interesting observation in the trace is that Task A does not remain in the idle state for the full 12ms; instead, the logs show a duration of approximately 11.8ms. This discrepancy between the requested time and the actual measured time is a classic example of Time Clipping, which occurs when a task goes to sleep partway through a clock tick.

A detailed technical explanation of this behavior is provided in the Time Clipping section following the analysis of Task B.

![Help](/docs/Trace_Analysis/docs/5.png)

### Analyzing Task B.
After Task A goes to sleep, Task B begins execution and then sleeps for 4.6 ms instead of 5 ms. The same timing discrepancy observed in Task A is also seen here, as shown in the figure below.

![Help](/docs/Trace_Analysis/docs/6.png)

### Task Termination
Following their respective sleep periods, both Task A and Task B execute their final instructions and terminate themselves using ```rtems_task_delete(RTEMS_SELF)```.

The sequence concludes with the following steps:

- DUMP Task Awakening: After the specified 500ms delay, the high-priority DUMP task wakes up from its idle state.

- Event Production: It records one final custom event, EVT_DUMP(USER3), to mark the completion of the observation period.

- System Shutdown: The task then triggers a fatal error using rtems_fatal_error_occurred(0xDEADBEEF).

Data Output: This fatal error forces the RTEMS Event Recorder to dump the entire Base64 trace buffer to the console, allowing us to capture the final log for analysis in Trace Compass.

![Help](/docs/Trace_Analysis/docs/7.png)

### Time Clipping Explained
By looking at the timestamps in the trace log, we can see why Task A appears to sleep for 11.8 ms instead of the requested 12 ms as shown in Figure below and in Analysis Task A.

![Help](/docs/Trace_Analysis/docs/8.png)

- Sleep Entry (Timestamp): 163.259 ms

- Wake Up (Timestamp): 175.053 ms

- Actual Duration:175.053 ms - 163.259 ms=11.794ms ,recorded as ~11.8ms

This "loss" of 0.2 ms happens because of the "Partial First Tick"  in RTEMS:

- When Task A requests a 12-tick sleep at 163.259 ms, it is already 0.259 ms into the current 1 ms clock cycle.

- The RTEMS timer is like a bus that only arrives at the top of every millisecond (e.g., at 164.000, 165.000, etc.). Because Task A "missed" the start of the 163.000 ms tick, its first wait period only lasts for the remaining 0.741 ms

- The RTEMS kernel counts that first short interval as one full tick. It then waits for 11 more full ticks (11.0 ms).

- Final Calculation:0.741ms(partial tick) +11ms(remaining tick) = ~11.8ms

The same explanation applies to Task B as well. Please note that this is based on my own observations and calculations—if you have a better explanation, feel free to share it with me.
