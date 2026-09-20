# Tutorial 7: EDF Scheduling 
> **Goal:** Demonstrate Scheduling of EDF  in RTEMS.

## Introduction 
As we learned in the course, Earliest Deadline First (EDF) is an optimal scheduling algorithm for aperiodic tasks and optimal for peroidic  when the total processor utilization is less than or equal to 1. The figure below provides a clearer definition to help understand the concept before applying it in RTEMS.Example code is already provided in  [repo](/Pre-built_Rtems_Toolsuite_BSP) under Tutorial7.

![Help](/docs/edf_analysis/docs/1.png).

![Help](/docs/edf_analysis/docs/2.png).

![Help](/docs/edf_analysis/docs/3.png).

## Understanding Code
- Checking schedulability
- rtems_rate_monotonic_period
- Purpose of adding rtems_barrier_wait
- rtems_rate_monotonic_get_statistics

## init.c
The configuration in init.c remains the same as in the previous examples. However, to use the EDF scheduler, we need to add the following definition.

```#define CONFIGURE_SCHEDULER_EDF ```

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
#define CONFIGURE_SCHEDULER_EDF
#include <rtems/confdefs.h>


 ```
## app.c or main.c

 ```bash
#include <rtems.h>
#include <rtems/record.h>
#include <stdio.h>

#define EVT_COUNT_A RTEMS_RECORD_USER(0)   ///TASK A
#define EVT_COUNT_B RTEMS_RECORD_USER(1)  ///TASK B

rtems_id barrier_id;

volatile int sync_taskA=0;  
volatile int sync_taskB=0;


/* Task A: 100ms Period, ~20ms Work */
rtems_task Task_A(rtems_task_argument arg) {
    rtems_id rm_id;
    rtems_rate_monotonic_create(rtems_build_name('R','M','A',' '), &rm_id);
    rtems_rate_monotonic_period_statistics stats; 
 // rtems_barrier_wait(barrier_id, RTEMS_NO_TIMEOUT);   ///scenario 2 

    while (1) {
    /*  SYNC POINT: Align both tasks . */
        rtems_rate_monotonic_period(rm_id, RTEMS_MILLISECONDS_TO_TICKS(100));
        if(sync_taskA==0) {
            rtems_barrier_wait(barrier_id, RTEMS_NO_TIMEOUT);
           sync_taskA=sync_taskA+1;
        }
    
       rtems_rate_monotonic_get_statistics(rm_id, &stats);
       rtems_record_produce(EVT_COUNT_A, (uint32_t)stats.count);///number to count Peroid
        /*  Simulated Work: ~20ms (14000 ) */
       for (volatile int i = 0; i < 14000; i++); 
    }
}

/* Task B: 150ms Period, ~20ms Work */
rtems_task Task_B(rtems_task_argument arg) {
    rtems_id rm_id;
    rtems_rate_monotonic_create(rtems_build_name('R','M','B',' '), &rm_id);
    rtems_rate_monotonic_period_statistics stats; 

    while (1) {
            /* SYNC POINT */
        rtems_rate_monotonic_period(rm_id, RTEMS_MILLISECONDS_TO_TICKS(150));
        if(sync_taskB==0) {
            rtems_barrier_wait(barrier_id, RTEMS_NO_TIMEOUT);
            sync_taskB=sync_taskB+1;

        }
      rtems_rate_monotonic_get_statistics(rm_id, &stats);
       rtems_record_produce(EVT_COUNT_B, (uint32_t)stats.count);
       
        /*  Simulated Work: ~20ms (14000) */
        for (volatile int i = 0; i < 14000; i++); 
        
    }
}

/* DUMP TASK: Ensures the simulator stops after 500ms */
rtems_task Dump_Task(rtems_task_argument arg) {
    rtems_task_wake_after(RTEMS_MILLISECONDS_TO_TICKS(500));
    rtems_fatal_error_occurred(0xDEADBEEF);
}

rtems_task Init(rtems_task_argument arg) {
    rtems_id ta, tb, td;

    rtems_barrier_create(
        rtems_build_name('S','Y','N','C'), 
        RTEMS_BARRIER_AUTOMATIC_RELEASE, 
        2, 
        &barrier_id
    );

    /* Create tasks with identical priority (10). 
       The EDF scheduler will ignore '10' and use deadlines instead. */
    rtems_task_create(rtems_build_name('T','A',' ',' '), 10, 4096, RTEMS_DEFAULT_MODES, RTEMS_DEFAULT_ATTRIBUTES, &ta);
    rtems_task_create(rtems_build_name('T','B',' ',' '), 10, 4096, RTEMS_DEFAULT_MODES, RTEMS_DEFAULT_ATTRIBUTES, &tb);
    rtems_task_create(rtems_build_name('D','U','M','P'), 1, 4096, RTEMS_DEFAULT_MODES, RTEMS_DEFAULT_ATTRIBUTES, &td);

    rtems_task_start(ta, Task_A, 0);
    rtems_task_start(tb, Task_B, 0);
    rtems_task_start(td, Dump_Task, 0);

    rtems_task_delete(RTEMS_SELF);
}
  ```

### Checking schedulability

In this example, we create two tasks: Task A and Task B. The period of Task A is 100 ms, and the period of Task B is 150 ms. The computation time for both tasks is 20 ms.

So total cpu utilization =20/100+20/150=0.33 .Since the total utilization U ≤ 1, the task set is schedulable using the Earliest Deadline First (EDF) scheduling algorithm.

### rtems_rate_monotonic_period

The Rate Monotonic Manager provides the necessary functionality to implement periodic tasks. It allows the user to define a fixed execution period for each task. The manager ensures that the task is released at the beginning of every period and keeps track of its execution time to detect whether the task misses its deadline.[classic API manual](https://docs.rtems.org/docs/main/c-user.pdf)  ```12.1 Introduction```.

### Purpose of adding rtems_barrier_wait.

In the code, I used rtems_barrier_wait with a count of 2 to ensure that both tasks start at the same time. Since both tasks have equal priority, they would not automatically start in sync without the barrier. The purpose is to clearly show simultaneous task execution for better understanding.

Without using ```rtems_barrier_wait```, the order of execution may change, which can affect the program flow. Therefore, the position and use of the barrier are important. The following scenario explains why the placement of rtems_barrier_wait matters.

#### Scenario 1: remove rtems_barrier_wait
If we completely remove rtems_barrier_wait from the code, you will  observe that Task A gets the CPU first. Task A has a period of 100 ms and executes for 20 ms(remember there is no sleep or delay). After Task A finishes, Task B gets the CPU, which has a period of 150 ms and also executes for 20 ms.

At first glance, this behavior appears correct. However, the initial scheduling decision is not based on the EDF algorithm, but rather on the static priority(10) assigned to the tasks. The reason is that, at the very beginning, the scheduler does not yet have enough timing information (```rtems_rate_monotonic_period(rm_id, RTEMS_MILLISECONDS_TO_TICKS(150)```) to compare the deadlines of both tasks properly. Since Task B has not yet started its first period, its absolute deadline is not yet established in the system.

Therefore, the CPU schedules the first task according to the initial static priority. After both tasks have entered their periodic execution and their deadlines are known, the scheduler can compare deadlines correctly. From that point onward, the periodic task activations are scheduled according to the EDF policy, where the task with the earliest deadline receives the CPU.

This demonstrates that the first scheduling decision may differ from EDF behavior if tasks are not synchronized at the start.

you can check yourself, change TASK B Time peroid to 80,still TASK A will do exection first.Clearing showing first sequence is not based on EDF thats why barrier is required.It is based on my obervation,may be better approach is there.

#### Scenario 2: Placing rtems_barrier_wait outside while loop.

 Still CPU will not be able to comapre deadline and first peroid would not be based on EDF.

#### Correct Placement of rtems_barrier_wait.

I placed rtems_barrier_wait inside the while loop using an if condition, so both tasks wait before continuing for the first Cycle. This ensures that both tasks start at the same time. Because both deadlines are known at that moment, the CPU can compare them and the first scheduling decision is made according to EDF.

### rtems_rate_monotonic_get_statistics

Please refer [classic API manual](https://docs.rtems.org/docs/main/c-user.pdf)  ```12.4.7 rtems_rate_monotonic_get_statistics()```.In app.c, I have used the count varable(it starts from 0) from rtems_rate_monotonic_get_statistics.Purpose is to verify the  number of time Peroid is executed.For Task A it should be 5 and for TASK B it should be 3(remember capture window size is 500ms).We will verfiy in 
next section through traces.

##  Understaning through  Eclipse Trace Client Visualization:

### TASK A takes the CPU first.

![Help](/docs/edf_analysis/docs/9.png).

### TASK A Time Peroid.

![Help](/docs/edf_analysis/docs/4.png).

### TASK B Time Peroid.

![Help](/docs/edf_analysis/docs/5.png).

### TASK A  and TASK B both woke up at same time.

![Help](/docs/edf_analysis/docs/6.png).

### TASK B meeting its deadline.

![Help](/docs/edf_analysis/docs/7.png).

### Count variable 

![Help](/docs/edf_analysis/docs/8.png).








