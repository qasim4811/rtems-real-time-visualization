# Tutorial 8: Priority Inversion
> **Goal:** Demonstrate priority inversion in RTEMS, and in Tutorial 9 explain how to resolve it.

## Introduction
In this Tutorial i will use existing example provided in course slides [RTOS-6-ressource_constraints.pdf](/docs/Priority_inversion/docs/RTOS-6-ressource_constraints.pdf). as show in Figure Below.Example code is already provided in [repo](/Pre-built_Rtems_Toolsuite_BSP) under the name Tutorial8.


![Help](/docs/Priority_inversion/docs/1.png).


### Priority Inversion

As shown in the figure above, the low-priority task holds a critical section that is required by the high-priority task. As a result, the high-priority task becomes blocked. Meanwhile, a medium-priority task becomes ready and preempts the low-priority task.

After the medium-priority task finishes execution, the low-priority task resumes and completes the critical section. Once the resource is released, the high-priority task becomes unblocked, acquires the resource, and enters the critical section.

In this situation, the high-priority task is indirectly delayed by the medium-priority task, even though the medium-priority task does not use the shared resource. This leads to priority inversion, where a higher-priority task is forced to wait because a lower-priority task is prevented from finishing its critical section.

### Understaning app.c

In order to better understand rtems_semaphore_create,please refer [classic API manual](https://docs.rtems.org/docs/main/c-user.pdf)  ```section 13.4.1 rtems_semaphore_create()```.

To demonstrate priority inversion, the following RTEMS configuration options are used:

- RTEMS_NO_INHERIT_PRIORITY (default) – disables priority inheritance, allowing priority inversion to occur.
- RTEMS_PRIORITY – enables priority-based scheduling of tasks.
- RTEMS_BINARY_SEMAPHORE – provides mutual exclusion for accessing the shared resource (critical section).

I am using a small capture window of 50ms to clearly show eclipse trace client events within one screenshot.

###  Flow of code.

- TASK_HIGH goes to sleep for 15 ms, allowing TASK_LOW enough time to acquire the semaphore.
- TASK_MEDIUM goes to sleep for 5 ms, so TASK_LOW can first obtain the semaphore.
- TASK_LOW acquires the semaphore and enters the critical section, executing for 10 ms.
- After 5 ms, TASK_MEDIUM wakes up and preempts TASK_LOW, then executes for 10 ms.
- TASK_HIGH wakes up after 15 ms, but it becomes blocked because it needs the semaphore currently held by TASK_LOW.
- Once TASK_MEDIUM finishes remaining execution of 10ms, TASK_LOW resumes and completes its critical section.
- After releasing the semaphore, TASK_HIGH becomes unblocked, acquires the resource, and enters the critical section.



 ```bash

#include <rtems.h>
#include <rtems/record.h>

#define EVT_HIGH   RTEMS_RECORD_USER(1)
#define EVT_MED    RTEMS_RECORD_USER(2)
#define EVT_LOW    RTEMS_RECORD_USER(3)

/* Status Codes: 1=Request, 2=Obtained, 3=Released */
#define REQ 1
#define GOT 2
#define REL 3

rtems_id sem_id;

rtems_task Dump_Task(rtems_task_argument arg) {
    /* Capture exactly 50ms of activity */
    rtems_task_wake_after(RTEMS_MILLISECONDS_TO_TICKS(50));
    rtems_fatal_error_occurred(0xDEADBEEF);
}
void critical_section(void)   //10ms approx

{
    for (volatile int i = 0; i < 7650; i++); 
}
/* --- J1: TASK HIGH (Priority 10) --- */
rtems_task Task_High(rtems_task_argument arg) {
    /* Arrives at T=15ms */
    rtems_task_wake_after(RTEMS_MILLISECONDS_TO_TICKS(15));
    
    rtems_record_produce(EVT_HIGH, REQ); 
    rtems_semaphore_obtain(sem_id, RTEMS_WAIT, RTEMS_NO_TIMEOUT);
    
    rtems_record_produce(EVT_HIGH, GOT);
  /// ~10ms Critical Section
    critical_section();
    
    rtems_semaphore_release(sem_id);
    rtems_record_produce(EVT_HIGH, REL);
    rtems_task_delete(RTEMS_SELF);
}

/* --- J2: TASK MEDIUM (Priority 20) --- */
rtems_task Task_Medium(rtems_task_argument arg) {
    /* Arrives at T=5ms, preempts Low */
    rtems_task_wake_after(RTEMS_MILLISECONDS_TO_TICKS(5));
    
    rtems_record_produce(EVT_MED, 1); 
    /* CPU Theft: 20ms (15,300 iterations) */
    for (volatile int i = 0; i < 15300; i++); 
    rtems_record_produce(EVT_MED, 0); 
    
    rtems_task_delete(RTEMS_SELF);
}

/* --- J3: TASK LOW (Priority 30) --- */
rtems_task Task_Low(rtems_task_argument arg) {
    /* Starts at T=0, grabs SEM1 immediately */
    rtems_semaphore_obtain(sem_id, RTEMS_WAIT, RTEMS_NO_TIMEOUT);
    rtems_record_produce(EVT_LOW, GOT);

    /* Critical Section: 10ms (7,650 iterations) */
    critical_section();
    rtems_semaphore_release(sem_id);
    rtems_record_produce(EVT_LOW, REL);
    rtems_task_delete(RTEMS_SELF);
}

/* --- Init remains the same, just starts tasks --- */
rtems_task Init(rtems_task_argument arg) {
    rtems_id th, tm, tl, td;

    /* Create binary semaphore WITHOUT Priority Inheritance to allow Inversion */
    rtems_semaphore_create(
        rtems_build_name('S', 'E', 'M', '1'),
        1,
        RTEMS_BINARY_SEMAPHORE | RTEMS_PRIORITY, 
        0, 
        &sem_id
    );

    rtems_task_create(rtems_build_name('H', 'I', 'G', 'H'), 10, 4096, RTEMS_DEFAULT_MODES, RTEMS_DEFAULT_ATTRIBUTES, &th);
    rtems_task_create(rtems_build_name('M', 'E', 'D', ' '), 20, 4096, RTEMS_DEFAULT_MODES, RTEMS_DEFAULT_ATTRIBUTES, &tm);
    rtems_task_create(rtems_build_name('L', 'O', 'W', ' '), 30, 4096, RTEMS_DEFAULT_MODES, RTEMS_DEFAULT_ATTRIBUTES, &tl);
    rtems_task_create(rtems_build_name('D', 'U', 'M', 'P'), 1, 4096, RTEMS_DEFAULT_MODES, RTEMS_DEFAULT_ATTRIBUTES, &td);

    rtems_task_start(tl, Task_Low, 0);
    rtems_task_start(tm, Task_Medium, 0);
    rtems_task_start(th, Task_High, 0);
    rtems_task_start(td, Dump_Task, 0);

    rtems_task_delete(RTEMS_SELF);
}

```

### Understaning through  Eclipse Trace Client Visualization:

![Help](/docs/Priority_inversion/docs/2.png).




