# Tutorial 10: Immediate Ceiling Priority Protocol
> **Goal:** Demonstrate Immediate Ceiling Priority Protocol in RTEMS, using example provided in Tutorial 9.

## Introduction

In Tutorial 9, we learned that deadlock can still occur when using the Priority Inheritance Protocol (PIP) but are avoided by RTEMS by generating  a error 0x72. In this tutorial, the focus is on the Immediate Ceiling Priority Protocol (ICPP) and how it can be used to prevent deadlock. During the course, we studied the Priority Ceiling Protocol (PCP) in [RTOS-6-ressource_constraints.pdf](docs/PCP/docs/RTOS-6-ressource_constraints.pdf). According to this protocol, a task whose priority is lower than or equal to the ceiling priority of a semaphore currently locked by another task will be blocked, even if the requested resource is free.This behavior, illustrated in the figure below.Example code is already provided in [repo](/Pre-built_Rtems_Toolsuite_BSP) under the name Tutorial10.But  practically in rtems ICPP behaves differently which we will try to understand in below sections.


![Help](/docs/ICPP/docs/1.png).

![Help](/docs/ICPP/docs/2.png).

### PCP vs ICPP

RTEMS uses ICPP [classic API manual](https://docs.rtems.org/docs/main/c-user.pdf)  ```4.4.2 Immediate Ceiling Priority Protocol (ICPP)```.In PCP, Task priority increases only if blocking occurs,whereas in ICPP Task priority increases immediately when resource is locked.

### Understanding ICPP 
So in tutorial 9 we used RTEMS_INHERIT_PRIORITY,for ICPP we will be using RTEMS_PRIORITY_CEILING  attribute and celling value of 50.Since RES1 and RES2 are being used by high prirorty task of pirorty 50 ,so celling value is set to 50 but it is not a strict criteria you can change it to 40 as well.please refer [classic API manual](https://docs.rtems.org/docs/main/c-user.pdf)  ```section 13.4.1 rtems_semaphore_create()```

#### resource 1

 ```bash

sc = rtems_semaphore_create(rtems_build_name('R', 'E', 'S', '1'), 1, 
         RTEMS_BINARY_SEMAPHORE | RTEMS_PRIORITY | RTEMS_PRIORITY_CEILING, 50, &res_1);

 ```

#### resource 2

Since RES2 is being used by high prirorty task of pirorty 50 ,so celling value is set to 50 as well.


 ```bash

sc = rtems_semaphore_create(rtems_build_name('R', 'E', 'S', '2'), 1, 
         RTEMS_BINARY_SEMAPHORE | RTEMS_PRIORITY | RTEMS_PRIORITY_CEILING, 50, &res_1);

 ```

#### main.c

The main.c file is very similar to the example from Tutorial 9, with some modifications. The semaphore was created using the PCP attribute. The code has already been committed, so please review it for a clearer understanding.Produce custom event as per the way it makes your understanding better.

To better understand ICPP, a specific scenario was created in the committed code by adding a sleep delay of 8ms in Task B. This example helps explain the difference between the theoretical PCP definition covered in the course and the actual behaviour observed in RTEMS

```bash
#include <rtems.h>
#include <rtems/record.h>

#define EVT_TA RTEMS_RECORD_USER(1)
#define EVT_TB RTEMS_RECORD_USER(2)
#define EVT_INIT RTEMS_RECORD_USER(3)

rtems_id res_1, res_2;

void record_status(rtems_id evt, rtems_status_code sc) {
    if (sc == RTEMS_SUCCESSFUL) {
        rtems_record_produce(evt, 0); // Log: Success
    } else {
        rtems_record_produce(evt, 100 + sc); // Log: Error code
    }
}

rtems_task Dump_Task(rtems_task_argument arg) {
    rtems_task_wake_after(RTEMS_MILLISECONDS_TO_TICKS(500));
    rtems_fatal_error_occurred(0xDEADBEEF);
}

/* --- HIGH PRIORITY TASK (Native Prio: 50) --- */
rtems_task Task_A(rtems_task_argument arg) {
    rtems_status_code sc;
    rtems_record_produce(EVT_TA, 1); 
    
    // Offset to ensure Task B locks a resource first
    rtems_task_wake_after(RTEMS_MILLISECONDS_TO_TICKS(12)); 
    
    rtems_record_produce(EVT_TA, 2); //wake up after sleep
    /* * ICPP EFFECT: Even though RES1 is free, Task A might block because 
     * Task B already holds a resource with a ceiling of 50. 
     */
    sc = rtems_semaphore_obtain(res_1, RTEMS_WAIT, RTEMS_NO_TIMEOUT);
    record_status(EVT_TA, sc);

    sc = rtems_semaphore_obtain(res_2, RTEMS_WAIT, RTEMS_NO_TIMEOUT);
    record_status(EVT_TA, sc);

    rtems_semaphore_release(res_2);
    rtems_semaphore_release(res_1);
    rtems_task_delete(RTEMS_SELF);
}

/* --- LOW PRIORITY TASK (Native Prio: 60) --- */
rtems_task Task_B(rtems_task_argument arg) {
    rtems_status_code sc;
    rtems_record_produce(EVT_TB, 1);
    
    for(volatile int i=0; i<3500; i++); // Initial 5ms work

    /* * THE "IMMEDIATE" JUMP:
     * The moment this call succeeds, Task B's priority is boosted 
     * from 60 to 50 because the Ceiling is 50.
     */
    sc = rtems_semaphore_obtain(res_2, RTEMS_WAIT, RTEMS_NO_TIMEOUT); 
    record_status(EVT_TB, sc);
    
    // Now running at Priority 50!
    /*
      If you add  a sleep of e.g 8ms  you will observe how this protocol broke.TASK A gets res_1 which is against the definition of PCP we have learned in course
*/
   // rtems_task_wake_after(RTEMS_MILLISECONDS_TO_TICKS(8)); 
    for(volatile int i=0; i<7000; i++); // 10ms work             
    sc = rtems_semaphore_obtain(res_1, RTEMS_WAIT, RTEMS_NO_TIMEOUT);
    record_status(EVT_TB, sc);

    rtems_semaphore_release(res_1);
    
    /* * THE DROP:
     * Task B remains at Priority 50 until it releases ALL 
     * ceiling semaphores. Once res_2 is released, it drops back to 60.
     */
    rtems_semaphore_release(res_2); 
    
    rtems_task_delete(RTEMS_SELF);
}

rtems_task Init(rtems_task_argument arg) {
    rtems_id ta, tb, td;
    rtems_status_code sc;

    /* * CEILING = 50 
     * This means "If you hold this, you are effectively Priority 50."
     */
    sc = rtems_semaphore_create(rtems_build_name('R', 'E', 'S', '1'), 1, 
         RTEMS_BINARY_SEMAPHORE | RTEMS_PRIORITY | RTEMS_PRIORITY_CEILING, 50, &res_1);
    
    sc = rtems_semaphore_create(rtems_build_name('R', 'E', 'S', '2'), 1, 
         RTEMS_BINARY_SEMAPHORE | RTEMS_PRIORITY | RTEMS_PRIORITY_CEILING, 50, &res_2);

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

### main.c Visualization without Sleep in TASK B

![Help](/docs/ICPP/docs/3.png).


### Adding delay  in TASK B to show how ICPP is acting different from PCP defination in Course.

If a sleep delay (for example 8 ms) is introduced in Task B after it locks res_2, the expected behaviour of the Immediate Ceiling Priority Protocol (ICPP) is no longer clearly observable. In this situation, Task B voluntarily releases the CPU, allowing Task A to execute. Since res_1 is not yet locked, Task A may successfully obtain res_1, even though Task B is already holding a resource (res_2) with a priority ceiling equal to 50.

According to the theoretical definition of the Priority Ceiling Protocol (PCP), a task should only enter a critical section if its priority is strictly higher than the current system ceiling. In this example, Task A has priority 50, which is not greater than the ceiling value 50 of the resource currently locked by Task B. Therefore, Task A should ideally be blocked. However, because Task B is put to sleep, it temporarily gives up the CPU, allowing Task A to run and obtain res_1.

This behaviour may give the impression that the protocol is violated, but in reality, the issue arises from the artificial delay inserted into Task B. The purpose of ICPP is to ensure that a task holding a resource with a defined ceiling executes at the ceiling priority and is not preempted by tasks with lower or equal priority that could lead to circular wait conditions. By forcing Task B to sleep, we unintentionally create a scheduling window where Task A can run earlier than expected.

Based on my observations, the implementation of ICPP in RTEMS appears to differ from the PCP definition learned in the course. I would appreciate feedback or clarification to better understand this difference

you can observe the behaviour  in Figure below.

#### Changes in app.c

Delay of 8ms is introduced in Task B within critical section,so TASK A can run.
```bash
rtems_task_wake_after(RTEMS_MILLISECONDS_TO_TICKS(8)); 
    for(volatile int i=0; i<7000; i++); // 10ms work             
    sc = rtems_semaphore_obtain(res_1, RTEMS_WAIT, RTEMS_NO_TIMEOUT);
    record_status(EVT_TB, sc);
```

![Help](/docs/ICPP/docs/4.png).
