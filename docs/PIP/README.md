# Tutorial 9: Priority Inheritance Protocol and Deadlock
> **Goal:** Demonstrate priority Inheritance Protocol in RTEMS and Deadlocks Error 0x72 (RTEMS_INCORRECT_STATE) that can occur with PIP .

## Introduction
In this tutorial, we use the same example from Tutorial 8, with one modification: a semaphore is created with the RTEMS_INHERIT_PRIORITY attribute added, as shown below.Example code is already provided in [repo](/Pre-built_Rtems_Toolsuite_BSP) under the name Tutorial9 subfolder PIP.

```bash
rtems_semaphore_create(
        rtems_build_name('S', 'E', 'M', '1'),
        1,
        RTEMS_BINARY_SEMAPHORE | RTEMS_PRIORITY | RTEMS_INHERIT_PRIORITY, 
        0, 
        &sem_id
    );


```
#### Priority Inheritance Protocol

![Help](/docs/PIP/docs/2.png).


### Understaning through  Eclipse Trace Client Visualization:

![Help](/docs/PIP/docs/1.png).

## Deadlock

![Help](/docs/PIP/docs/3.png).

So in our tutorial we are producing the same scenario as mentioned in Figure above.Example code is already provided in [repo](/Pre-built_Rtems_Toolsuite_BSP) under the name Tutorial9 subfolder PIP-Deadlock.

### Understanding app.c
- TASK A, having the highest priority, executes first and then goes to sleep for 12 ms. TASK B executes for 5 ms, then TASK B acquires the resource res_2 and executes within the critical section for duration of 7 ms.

- At 12 ms, TASK A wakes up and preempts TASK B(7ms of execution done in critical section,3ms pending). TASK A acquires resource res_1 and then immediately requests res_2. However, since res_2 is already held by TASK B, TASK B inherits the priority of TASK A due to the priority inheritance Protocol.

- TASK B then requests res_1, which is already held by TASK A, resulting in a deadlock situation. The kernel detects this deadlock and generates the error 0x72, indicating that the request for res_1 cannot be granted.

- As a result, TASK B releases the resource res_2, allowing TASK A to become unblocked. Afterward, both tasks complete their execution and terminate themselves.


```bash

#include <rtems.h>
#include <rtems/record.h>

#define EVT_TA RTEMS_RECORD_USER(1)
#define EVT_TB RTEMS_RECORD_USER(2)
#define EVT_INIT RTEMS_RECORD_USER(3)

rtems_id res_1, res_2;

/* Helper to record status: 0 = Success, 100+sc = Error (0x72 = 114) */
void record_status(rtems_id evt, rtems_status_code sc) {
    if (sc == RTEMS_SUCCESSFUL) {
        rtems_record_produce(evt, 0); 
    } else {
        rtems_record_produce(evt, 100 + sc); 
    }
}

rtems_task Dump_Task(rtems_task_argument arg) {
    rtems_task_wake_after(RTEMS_MILLISECONDS_TO_TICKS(500));
    rtems_fatal_error_occurred(0xDEADBEEF);
}

rtems_task Task_A(rtems_task_argument arg) {
    rtems_status_code sc;
    rtems_record_produce(EVT_TA, 0); 
    
    // Wait 12ms so Task B can grab RES_2 first
    rtems_task_wake_after(RTEMS_MILLISECONDS_TO_TICKS(12)); 
    
    rtems_record_produce(EVT_TA, 1); 
    sc = rtems_semaphore_obtain(res_1, RTEMS_WAIT, RTEMS_NO_TIMEOUT); // Locks RES_1
    record_status(EVT_TA, sc);

    rtems_record_produce(EVT_TA, 3); 
    // This will BLOCK because Task B holds RES_2. 
    // This triggers the PIP boost for Task B.
    sc = rtems_semaphore_obtain(res_2, RTEMS_WAIT, RTEMS_NO_TIMEOUT);
    
    record_status(EVT_TA, sc);
    rtems_semaphore_release(res_2);
    rtems_semaphore_release(res_1);
    rtems_task_delete(RTEMS_SELF);
}

rtems_task Task_B(rtems_task_argument arg) {
    rtems_status_code sc;
    rtems_record_produce(EVT_TB, 1);
    
    for(volatile int i=0; i<3500; i++); // 5ms work
    
    sc = rtems_semaphore_obtain(res_2, RTEMS_WAIT, RTEMS_NO_TIMEOUT); 
    record_status(EVT_TB, sc); // Event 0 (Success)
    
    // 10ms work (starts at 5ms, ends at 15ms)
    // Task A will wake up at 12ms and preempt this loop!
    for(volatile int i=0; i<7000; i++); 

    rtems_record_produce(EVT_TB, 3); 
    // Task B tries to lock RES_1 (held by A). 
    // Kernel detects A is waiting for B -> DEADLOCK!
    // Kernel returns 0x72 (114) here.
    sc = rtems_semaphore_obtain(res_1, RTEMS_WAIT, RTEMS_NO_TIMEOUT);
    
    record_status(EVT_TB, sc); // You will see 114 here
    rtems_record_produce(EVT_TB, 4); 
    
    rtems_semaphore_release(res_2);
    rtems_task_delete(RTEMS_SELF);
}

rtems_task Init(rtems_task_argument arg) {
    rtems_id ta, tb, td;
    rtems_status_code sc;

    // PIP Configuration: RTEMS_INHERIT_PRIORITY
    sc = rtems_semaphore_create(rtems_build_name('R', 'E', 'S', '1'), 1, 
         RTEMS_BINARY_SEMAPHORE | RTEMS_PRIORITY | RTEMS_INHERIT_PRIORITY, 0, &res_1);
    
    sc = rtems_semaphore_create(rtems_build_name('R', 'E', 'S', '2'), 1, 
         RTEMS_BINARY_SEMAPHORE | RTEMS_PRIORITY | RTEMS_INHERIT_PRIORITY, 0, &res_2);

    rtems_task_create(rtems_build_name('T', 'A', ' ', ' '), 50, 4096, RTEMS_DEFAULT_MODES, RTEMS_DEFAULT_ATTRIBUTES, &ta);
    rtems_task_create(rtems_build_name('T', 'B', ' ', ' '), 60, 4096, RTEMS_DEFAULT_MODES, RTEMS_DEFAULT_ATTRIBUTES, &tb);
    rtems_task_create(rtems_build_name('D', 'U', 'M', 'P'), 10, 4096, RTEMS_DEFAULT_MODES, RTEMS_DEFAULT_ATTRIBUTES, &td);

    rtems_task_start(ta, Task_A, 0);
    rtems_task_start(tb, Task_B, 0);
    rtems_task_start(td, Dump_Task, 0);
    
    rtems_task_suspend(RTEMS_SELF);
}


```
### Understaning through  Eclipse Trace Client Visualization:

![Help](/docs/PIP/docs/4.png).
