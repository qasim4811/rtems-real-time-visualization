# Tutorial 3: Capturing System Logs Through a Fatal Error Handler
> **Goal:** Capturing logs by running the example

---
## Event Recording
The event recording support focuses on the recording of high frequency events such as


```bash
thread switches,

thread queue enqueue and surrender,

interrupt entry and exit,

heap/workspace memory allocate/free,

UMA zone allocate/free,

Ethernet packet input/output, and

etc.
```

---
RTEMS Event Recording works by capturing high-frequency system events—like task switches and interrupts—directly into per-processor ring buffers using a high-speed CPU counter for timestamps. This process is lock-free and requires no atomic operations, ensuring that recording does not disrupt the system's timing or performance. When a critical failure occurs, the Fatal Error Handler freezes this buffer and converts the raw binary data into a Base64-encoded string, which is then printed to the console for post-mortem analysis on your host machine.


There is a fixed set of 512 system reserved and 512 user defined events.
Actually, it means the system can hold 1,024 events in total.
Think of it as two separate "ID ranges" available for the recorder to use:

- Range A (0–511): Reserved for the Kernel. (e.g., Task 1 switched to Task 2).
- Range B (512–1023): Reserved for You (e.g., "My sensor reading is ready").

The Total Capacity is 512 + 512 = 1024 unique event identifiers.

The event recording support allows post-mortem analysis in fatal error handlers, e.g. the last events are in the record buffers, the newest event overwrites the oldest event.

```CONFIGURE_RECORD_PER_PROCESSOR_ITEMS ```This is the "Memory." we set in configuartion,
suppose if we set it to ```65,536``` it means Your system can remember the last 65,536 actions that occurred, and each of those actions can be any one of the 1,024 unique event types.

To use the event recording three things come into play. Firstly, there is the generation of event records on the target system (the application running with RTEMS). Secondly, means to transfer the recorded events to the host computer for analysis. Thirdly, the analysis of the recorded events on the host computer.

Note:

The following example is available in the repository [repo](/Pre-built_Rtems_Toolsuite_BSP) at ```quick-start/app/Tutorial3```.So you can just run the application directly. However, going through the steps in detail can provide a better understanding.

## Step 1: Generation of Event Records by Modifying Configuration File.
Modifying ini.c to enable event recording.Rest of the configuaration are same as done in Build application Tutorial.

Note:
Turning on interrupt tracing creates too much noise. With 1,000+ clock ticks every second, the memory buffer fills up instantly and deletes your older data. This means when a crash happens, the important events leading up to it have already been overwritten by meaningless system ticks.Thats why I have not  defined ```CONFIGURE_RECORD_INTERRUPTS_ENABLED``` in config.

In Tutorial 3,I am using 500ms window to capture enough data to see Task A and Task B working.
A 1ms tick (``` CONFIGURE_MICROSECONDS_PER_TICK 1000 ```)is great for accuracy, but it generates data 10 times faster than a 10ms tick. We must manage our recording time carefully so we don't "miss" the events we actually care about by  overflowing the Ring Buffer.

You can adjust the window size according to your application’s requirements. In this example, even if the window size is changed to 50 seconds, it would not make any  difference. Only two tasks generate events and then terminate themselves.

However, if you are continuously producing custom events within a loop, the buffer may overflow. An example of this scenario is demonstrated in Tutorial 5.

## init.c
```bash
/*
 * RTEMS configuration
 */

#define CONFIGURE_APPLICATION_NEEDS_CLOCK_DRIVER
#define CONFIGURE_APPLICATION_NEEDS_CONSOLE_DRIVER
#define CONFIGURE_UNIFIED_WORK_AREAS
#define CONFIGURE_UNLIMITED_OBJECTS
#define CONFIGURE_MAXIMUM_TASKS 10   //you can define maximum task

#define CONFIGURE_RTEMS_INIT_TASKS_TABLE
#define CONFIGURE_INIT
#define CONFIGURE_MICROSECONDS_PER_TICK 1000  ///1ms Peroid
/*  Enable Event Recording */
#define CONFIGURE_RECORD_EXTENSIONS_ENABLED
#define CONFIGURE_RECORD_FATAL_DUMP_BASE64  //Dumps of the event records in a fatal error 
// This buffer can hold exactly 65,536 system events before it starts overwriting the oldest data.
#define CONFIGURE_RECORD_PER_PROCESSOR_ITEMS 65536 


#include <rtems/confdefs.h>

```
### Step 2: Create  a Dump Task:

We use custom event IDs, such as EVT_TB, which allow us to see our specific application logic inside the Eclipse Trace Client. The Dump_Task is designed to sleep for 500 ms (0.5 seconds) to allow Task A and Task B enough time to execute their loops and record data. After this delay, Dump_Task triggers a rtems_fatal_error_occurred to stop the system and print the Base64 trace dump.



## main.c


```bash
#include <rtems.h>
#include <rtems/record.h>

#define EVT_TA RTEMS_RECORD_USER(1) //USER id(1) will be visible in trace compass
#define EVT_TB RTEMS_RECORD_USER(2)
#define EVT_DUMP RTEMS_RECORD_USER(3)

rtems_id res_1, res_2;


rtems_task Dump_Task(rtems_task_argument arg) {
    rtems_task_wake_after(RTEMS_MILLISECONDS_TO_TICKS(500));
    rtems_record_produce(EVT_DUMP, 0);///producing custom event after wakeup,sending data 0x00
    rtems_fatal_error_occurred(0xDEADBEEF);
}

rtems_task Task_A(rtems_task_argument arg) {

    rtems_record_produce(EVT_TA, 5); ///producing custom event and sending data 0x05
    // Wait 12ms 
    rtems_task_wake_after(RTEMS_MILLISECONDS_TO_TICKS(12)); 
    rtems_task_delete(RTEMS_SELF);
}

rtems_task Task_B(rtems_task_argument arg) {
    rtems_record_produce(EVT_TB, 1);///producing custom event and sending data 0x01
    rtems_task_wake_after(RTEMS_MILLISECONDS_TO_TICKS(5)); 
    rtems_task_delete(RTEMS_SELF);
}

rtems_task Init(rtems_task_argument arg) {
    rtems_id ta, tb, td;

    rtems_task_create(rtems_build_name('T', 'A', ' ', ' '), 20, 4096, RTEMS_DEFAULT_MODES, RTEMS_DEFAULT_ATTRIBUTES, &ta);//medium priority
    rtems_task_create(rtems_build_name('T', 'B', ' ', ' '), 30, 4096, RTEMS_DEFAULT_MODES, RTEMS_DEFAULT_ATTRIBUTES, &tb); //lowest priority
    rtems_task_create(rtems_build_name('D', 'U', 'M', 'P'), 10, 4096, RTEMS_DEFAULT_MODES, RTEMS_DEFAULT_ATTRIBUTES, &td);//highest priority

    rtems_task_start(ta, Task_A, 0);
    rtems_task_start(tb, Task_B, 0);
    rtems_task_start(td, Dump_Task, 0);
    
    rtems_task_delete(RTEMS_SELF);
}
```
### Step 3:Run the Code ,Extract, and Decode the Trace Data
Create directory e.g  Tutorial3
```bash
cd $Home/quick-start/app/
mkdir Tutorial3
```
Copy all the content of ```hello example``` provided in [repo](/Pre-built_Rtems_Toolsuite_BSP)   to Tutorial3 Folder and replace by main.c and init.c provided in Step2 and Step3.If you do not want to copy content of hello then follow step 1 to 3 mentioned in [Build_Application](https://gitlab.tf.uni-freiburg.de/team-betriebssysteme/student-projects/rtems-visualization-qasim/-/blob/main/docs/build_application/README.md)

Config:
```bash
./waf configure   --rtems=$HOME/rtems_6_uni/quick-start/rtems/6   --rtems-tools=$HOME/rtems_6_uni/quick-start/rtems/6   --rtems-bsp=sparc/erc32

```
build:
```bash
./waf
```
Run the Application:
```bash
cd $HOME/quick-start/app/Tutorial3/build/sparc-rtems6-erc32
export PATH=$HOME/quick-start/rtems/6/bin:"$PATH"
rtems-run --rtems-bsps=erc32-sis app.exe 
```

Once your code finishes running in the simulator, you will see a large block of Base64 text in your terminal.

```bash
*** BEGIN OF RECORDS BASE64 ***
MzMzM4LhTsEAAAABAAAACgAAAAoAAAAAAAAABgABAAAAAAAEAA9CQAAAAAJSQVBTAAAAAgAAAEMA
AAAFUEYvdwAAAAUAAABVAAAAAzNjcmUAAAADAAAAMgAAABAtdG9uAAAAEGVsZXIAAAAQZGVzYQAA
AA4zLjMxAAAADjIgMC4AAAAOMDQyMAAAAA4gMTI1AAAADkVUUigAAAAONiBTTQAAAA5TUiAsAAAA
Dm9uIEIAAAAOcGVyLQAAAA5OICxvAAAADmlsd2UAAAAOYjEgYgAAAA5mY2QzAAAADgAAKWQAAAAL
CQEAAQAAAAxFTERJAAAACwoBAAQAAAAMUE1VRAAAAAkAAAAAAA5VFAkBAAEADlQMRUxESQAPkS4J
AQABABNBQ/eAI6UAE0FCAAAQxwAW3RQKAQABABbcDCAxSVUAGVkuCgEAAQAT+REKAQABABhBFAoB
AAIAGEAMICBBVAActRQKAQADABy0DCAgQlQAIo0UCgEABAAijAxQTVVEACR5LgoBAAIAJekuCgEA
AwAnWS4KAQAEACkFMwoBAAEAKskyCgEAAQAqySsAAAw4ACrJMQoBAAQAK9ERCgEABAAt1TIKAQAE
AC3VKwAADagALdUxCgEAAgAu7REKAQACADKRMgoBAAIAMpErAAANqAAykTEKAQADADOpEQoBAAMA
Na0yCgEAAwA1rSsAAA2oADWtMQkBAAEANskRCQEAAQDOBTIJAQABAM4FKwAADWAAzgUxCgEAAwDQ
CTMKAQADANHVMgoBAAMA0dUrAAAMqADR1TEJAQABAO09MgkBAAEA7T0rAAANYADtPTEKAQACAO9J
MwoBAAIA8REyCgEAAgDxESsAAAyoAPERMQkBAAEeppEyCQEAAR6mkSsAAA1gHqaRMQoBAAQep4ID
AAAAAB6oPUN3xhDvHqg9QgAAEMgeqGQwAAAAAR6oZC/erb7v
*** END OF RECORDS BASE64 ***

*** FATAL ***
fatal source: 1 (INTERNAL_ERROR_RTEMS_API)
fatal code: 3735928559 (0xdeadbeef)
RTEMS version: 6.1.0.not-released
RTEMS tools: 13.3.0 20240521 (RTEMS 6, RSB no-repo, Newlib 1b3dcfd)
executing thread ID: 0x0a010004
executing thread name: DUMP
cpu 0 in error mode (tt = 0x101)
  5781272  0200d1e0:  91d02000   ta  0x0
Run time     : 0:00:00.258523

```
To visualize this data in Eclipse, you must convert it into a format called LTTng.

Copy everthing from  *** BEGIN OF RECORDS BASE64 ***  till   *** END OF RECORDS BASE64 ***  in txt file ,for example: trace.txt.

trace.txt file should like this.
```bash
*** BEGIN OF RECORDS BASE64 ***
MzMzM4LhTsEAAAABAAAACgAAAAoAAAAAAAAABgABAAAAAAAEAA9CQAAAAAJSQVBTAAAAAgAAAEMA
AAAFUEYvdwAAAAUAAABVAAAAAzNjcmUAAAADAAAAMgAAABAtdG9uAAAAEGVsZXIAAAAQZGVzYQAA
AA4zLjMxAAAADjIgMC4AAAAOMDQyMAAAAA4gMTI1AAAADkVUUigAAAAONiBTTQAAAA5TUiAsAAAA
Dm9uIEIAAAAOcGVyLQAAAA5OICxvAAAADmlsd2UAAAAOYjEgYgAAAA5mY2QzAAAADgAAKWQAAAAL
CQEAAQAAAAxFTERJAAAACwoBAAQAAAAMUE1VRAAAAAkAAAAAAA5VFAkBAAEADlQMRUxESQAPkS4J
AQABABNBQ/eAI6UAE0FCAAAQxwAW3RQKAQABABbcDCAxSVUAGVkuCgEAAQAT+REKAQABABhBFAoB
AAIAGEAMICBBVAActRQKAQADABy0DCAgQlQAIo0UCgEABAAijAxQTVVEACR5LgoBAAIAJekuCgEA
AwAnWS4KAQAEACkFMwoBAAEAKskyCgEAAQAqySsAAAw4ACrJMQoBAAQAK9ERCgEABAAt1TIKAQAE
AC3VKwAADagALdUxCgEAAgAu7REKAQACADKRMgoBAAIAMpErAAANqAAykTEKAQADADOpEQoBAAMA
Na0yCgEAAwA1rSsAAA2oADWtMQkBAAEANskRCQEAAQDOBTIJAQABAM4FKwAADWAAzgUxCgEAAwDQ
CTMKAQADANHVMgoBAAMA0dUrAAAMqADR1TEJAQABAO09MgkBAAEA7T0rAAANYADtPTEKAQACAO9J
MwoBAAIA8REyCgEAAgDxESsAAAyoAPERMQkBAAEeppEyCQEAAR6mkSsAAA1gHqaRMQoBAAQep4ID
AAAAAB6oPUN3xhDvHqg9QgAAEMgeqGQwAAAAAR6oZC/erb7v
*** END OF RECORDS BASE64 ***
```

Create trace directory in build folder.
```bash
cd $HOME/quick-start/app/Tutorial3/build/sparc-rtems6-erc32/
mkdir trace
```
Run the following command to convert the event records into the CTF files metadata, stream_0

```rtems-record-lttng -e app.exe -t trace.txt -o trace```

for example:

``` app/Tutorial3/build/sparc-rtems6-erc32$ rtems-record-lttng -e app.exe -t trace.txt -o trace ```

Output should like this inside trace folder:
```
qasim@qasim-HP-EliteBook-840r-G4:~/rtems_6_uni/quick-start/app/Tutorial3/build/sparc-rtems6-erc32/trace$ ls
metadata  stream_0
qasim@qasim-HP-EliteBook-840r-G4:~/rtems_6_uni/quick-start/app/Tutorial3/build/sparc-rtems6-erc32/trace$ 
```
Now we have sucessfully generated metadata and stream_0,further analysis can be done in Eclipse Trace client.

## Reference 
[Event Recording](https://docs.rtems.org/branches/main/user/tracing/eventrecording.html)


