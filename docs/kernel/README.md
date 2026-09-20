# Tutorial 11: Introduction to rtems kernel
> **Goal:** To compile the kernel source code and re-link the application with custom version of kernel.

## Introduction
Since the application was built using the RSB tool, the kernel is provided only as a compiled library, and the actual RTEMS kernel source code is not included. Therefore, it is necessary to separately download the RTEMS kernel source code in order to study or modify the internal implementation.

The following steps describe how to download the kernel source code, build it, and re-link the application with the custom version of the kernel that we produced. 






### STEP 1 :Create Directory

Create directory kernel_exp at home. 
 ```bash
mkdir $HOME/kernel_exp
cd $HOME/kernel_exp

```

### STEP 2 :Download Source Code and quick-start repo
Download rtems kernel in tar format to avoid provide problem with symlink.Go to this link [Downlaod kernel 6.1](https://ftp.rtems.org/pub/rtems/releases/6/tar/rtems-6.1.tar.bz2) and download kernel 6.1.we have set the toolchain for kernel 6.1 so download kernel 6.1.

Download quick-start [repo](/Pre-built_Rtems_Toolsuite_BSP).

Place both of the downloaded repo  ```quick-start.tar.gz``` and ```rtems-6.1.tar.bz2``` in ```$HOME/kernel_exp``` directory.



### STEP 3. Extract kernel and quick-start repo:
 ```bash
qasim@qasim-HP-EliteBook-840r-G4:~/kernel_exp$ tar -xvzf quick-start.tar.gz
qasim@qasim-HP-EliteBook-840r-G4:~/kernel_exp$ tar -xvjf rtems-6.1.tar.bz2


```
##### Output:

 ```bash
qasim@qasim-HP-EliteBook-840r-G4:~/kernel_exp$ ls
6.1  quick-start  rtems-6.1.tar.bz2  quick-start.tar.gz 

```
### STEP 4. Extract kernel Source:
```bash
cd 6.1/sources

qasim@qasim-HP-EliteBook-840r-G4:~/kernel_exp/6.1/sources$ tar -xvf rtems-6.1.tar.xz 

cd rtems-6.1
```
##### Output:

```bash
qasim@qasim-HP-EliteBook-840r-G4:~/kernel_exp/6.1/sources/rtems-6.1$ ls
bsps   CODEOWNERS  cpukit    gccdeps.py  make         README     rtems-bsps     spec        VERSION  wscript
build  config.ini  Doxyfile  LICENSE.md  __pycache__  README.md  rtemslogo.png  testsuites  waf      yaml


```

### STEP 5 :Do Modification as per your Requirements.

I am doing a small modifiction in  ``` /home/qasim/kernel_exp/6.1/sources/rtems-6.1/cpukit/score/src/threaddispatch.c```.

The primary modification was targeted at the Thread Dispatcher threaddispatch.c. This component is responsible for context switching—the process of saving the state of the currently executing task and loading the state of the "heir" (the next highest-priority ready task).

A kernel-level logging statement (printk) was inserted into the _Thread_Do_dispatch() function to provide a real-time console trace of every scheduling decision.

I have just added printk statement ,you can see below.

```bash
  Thread_Control                     *heir;
    const Thread_CPU_budget_operations *cpu_budget_operations;

    level = _Thread_Preemption_intervention( executing, cpu_self, level );
    heir = _Thread_Get_heir_and_make_it_executing( cpu_self );

    /*
     * If the heir and executing are the same, then there is no need to do a
     * context switch.  Proceed to run the post switch actions.  This is
     * normally done to dispatch signals.
     */
    if ( heir == executing ) {
    /////adding printk:custom modifiction start
   printk(
          "[KERNEL] Switch: 0x%08x -> 0x%08x\n",
          (unsigned int)executing->Object.id,
          (unsigned int)heir->Object.id
        );
        //////custom modifiction end
      break;
    }



```

### STEP 6 :Build the Kernel.


#### 1.Config using waf script
 Before building the kernel, we must specify the location where the compiled binaries will be installed. The prefix indicates the installation path for the output files, while rtems-tools refers to the toolchain that has already been built and will be used to compile the kernel.

 ```bash
qasim@qasim-HP-EliteBook-840r-G4:~/kernel_exp/6.1/sources/rtems-6.1$ ./waf configure --prefix=/home/qasim/kernel_exp/quick-start/rtems/6                 --rtems-tools=/home/qasim/kernel_exp/quick-start/rtems/6                 --rtems-bsps=sparc/erc32

```
#### Output
```bash
qasim@qasim-HP-EliteBook-840r-G4:~/kernel_exp/6.1/sources/rtems-6.1$ ./waf configure --prefix=/home/qasim/kernel_exp/quick-start/rtems/6                 --rtems-tools=/home/qasim/kernel_exp/quick-start/rtems/6                 --rtems-bsps=sparc/erc32
Setting top to                           : /home/qasim/kernel_exp/6.1/sources/rtems-6.1 
Setting out to                           : /home/qasim/kernel_exp/6.1/sources/rtems-6.1/build 
Configure RTEMS version                  : 6.1 
Configure board support package (BSP)    : sparc/erc32 
Checking for program 'sparc-rtems6-gcc'  : /home/qasim/kernel_exp/quick-start/rtems/6/bin/sparc-rtems6-gcc 
Checking for program 'sparc-rtems6-g++'  : /home/qasim/kernel_exp/quick-start/rtems/6/bin/sparc-rtems6-g++ 
Checking for program 'sparc-rtems6-ar'   : /home/qasim/kernel_exp/quick-start/rtems/6/bin/sparc-rtems6-ar 
Checking for program 'sparc-rtems6-ld'   : /home/qasim/kernel_exp/quick-start/rtems/6/bin/sparc-rtems6-ld 
Checking for program 'ar'                : /home/qasim/kernel_exp/quick-start/rtems/6/bin/sparc-rtems6-ar 
Checking for program 'g++, c++'          : /home/qasim/kernel_exp/quick-start/rtems/6/bin/sparc-rtems6-g++ 
Checking for program 'ar'                : /home/qasim/kernel_exp/quick-start/rtems/6/bin/sparc-rtems6-ar 
Checking for program 'gas, gcc'          : /home/qasim/kernel_exp/quick-start/rtems/6/bin/sparc-rtems6-gcc 
Checking for program 'ar'                : /home/qasim/kernel_exp/quick-start/rtems/6/bin/sparc-rtems6-ar 
Checking for program 'gcc, cc'           : /home/qasim/kernel_exp/quick-start/rtems/6/bin/sparc-rtems6-gcc 
Checking for program 'ar'                : /home/qasim/kernel_exp/quick-start/rtems/6/bin/sparc-rtems6-ar 
Checking for asm flags '-MMD'            : yes 
Checking for c flags '-MMD'              : yes 
Checking for cxx flags '-MMD'            : yes 
'configure' finished successfully (0.187s)
qasim@qasim-HP-EliteBook-840r-G4:~/kernel_exp/6.1/sources/rtems-6.1$ 



```

#### 2.Build

```bash
qasim@qasim-HP-EliteBook-840r-G4:~/kernel_exp/6.1/sources/rtems-6.1$ ./waf


```
#### 3.Install
```bash
qasim@qasim-HP-EliteBook-840r-G4:~/kernel_exp/6.1/sources/rtems-6.1$ ./waf install

```

#### Output:
The libraries in /home/qasim/kernel_exp/quick-start/rtems/6 have now been updated with the libraries compiled from the RTEMS kernel source.

![Help](/docs/kernel/docs/2.png).

## Run your application with modified Kernel

### 1. Config 
Same steps and commands  as we have been doing before.
```bash
qasim@qasim-HP-EliteBook-840r-G4:~/kernel_exp/quick-start/app/Tutorial10$ ./waf configure --rtems=/home/qasim/kernel_exp/quick-start/rtems/6 \
                --rtems-tools=/home/qasim/kernel_exp/quick-start/rtems/6 \
                --rtems-bsp=sparc/erc32


```
### 2. Clean and build
Make sure to clean the previous build before compiling the application. This ensures that the application is linked against the newly built custom kernel libraries instead of any previously compiled versions.

```bash
./waf clean

```

```bash
./waf 

```
### 3. Run the application
```bash
export PATH=/home/qasim/kernel_exp/quick-start/rtems/6/bin:"$PATH"
rtems-run --rtems-bsps=erc32-sis app.exe 

```

### Ouput:
The custom printk statements are visible in the output. The value 0x0a010001 corresponds to the task ID, which can also be seen in Trace Compass. This confirms that the application is correctly linked with the modified kernel.
```bash
asim@qasim-HP-EliteBook-840r-G4:~/kernel_exp/quick-start/app/Tutorial10/build/sparc-rtems6-erc32$ export PATH=/home/qasim/kernel_exp/quick-start/rtems/6/bin:"$PATH"
rtems-run --rtems-bsps=erc32-sis app.exe 
RTEMS Testing - Run, 6.0.not_released
 Command Line: /home/qasim/kernel_exp/quick-start/rtems/6/bin/rtems-run --rtems-bsps=erc32-sis app.exe
 Host: Linux qasim-HP-EliteBook-840r-G4 6.17.0-19-generic #19~24.04.2-Ubuntu SMP PREEMPT_DYNAMIC Fri Mar  6 23:08:46 UTC 2 x86_64
 Python: 3.12.3 (main, Mar  3 2026, 12:15:18) [GCC 13.3.0]
Host: Linux-6.17.0-19-generic-x86_64-with-glibc2.39 (Linux qasim-HP-EliteBook-840r-G4 6.17.0-19-generic #19~24.04.2-Ubuntu SMP PREEMPT_DYNAMIC Fri Mar  6 23:08:46 UTC 2 x86_64 x86_64)

 SIS - SPARC/RISCV instruction simulator 2.30,  copyright Jiri Gaisler 2020
 Bug-reports to jiri@gaisler.se

 ERC32 emulation enabled

 Loaded app.exe, entry 0x02000000
[KERNEL] Switch: 0x0a010001 -> 0x0a010001
[KERNEL] Switch: 0x0a010004 -> 0x0a010004
[KERNEL] Switch: 0x0a010002 -> 0x0a010002
[KERNEL] Switch: 0x0a010003 -> 0x0a010003
[KERNEL] Switch: 0x0a010002 -> 0x0a010002
[KERNEL] Switch: 0x0a010003 -> 0x0a010003
[KERNEL] Switch: 0x09010001 -> 0x09010001

*** BEGIN OF RECORDS BASE64 ***
MzMzM4LhTsEAAAABAAAACgAAAAoAAAAAAAAABgABAAAAAAAEAA9CQAAAAAJSQVBTAAAAAgAAAEMA
AAAFUEYvdwAAAAUAAABVAAAAAzNjcmUAAAADAAAAMgAAABAtdG9uAAAAEGVsZXIAAAAQZGVzYQAA
AA4zLjMxAAAADjIgMC4AAAAOMDQyMAAAAA4gMTI1AAAADkVUUigAAAAONiBTTQAAAA5TUiAsAAAA
Dm9uIEIAAAAOcGVyLQAAAA5OICxvAAAADmlsd2UAAAAOYjEgYgAAAA5mY2QzAAAADgAAKWQAAAAL
CQEAAQAAAAxFTERJAAAACwoBAAEAAAAMIDFJVQAAAAsKAQAEAAAADFBNVUQAAAAJAAAAAAAOuRQJ
AQABAA64DEVMREkAD/UuCQEAAQATsUP3gDRsABOxQgAAEMcAF1EUCgEAAQAXUAwgMUlVABnRLgoB
AAEAJQURCgEAAQAq3RQKAQACACrcDCAgQVQAMP0UCgEAAwAw/AwgIEJUADXRFAoBAAQANdAMUE1V
RAA3rS4KAQACADkZLgoBAAMAOokuCgEABAA8JTIKAQABADwlKwAADZgAPCUxCgEABABNsREKAQAE
AFDZMgoBAAQAUNkrAAANqABQ2TEKAQACAGJ9EQoBAAIAYw4BAAAAAQBkqTIKAQACAGSpKwAADagA
ZKkxCgEAAwB2RREKAQADAHbeAgAAAAEAxYoCAAAAAAFh/gIAAAAAAWQxMgoBAAMBZDErAAANGAFk
MTEKAQACAWVOAQAAAAIBZgIBAAAAAAFm1gEAAAAAAXshMwoBAAIBfM0yCgEAAgF8zSsAAAyoAXzN
MQoBAAMBj4kzCgEAAwGRRTIKAQADAZFFKwAADKgBkUUxCQEAAQGi1REJAQABHtWJMgkBAAEe1Ykr
AAANYB7ViTEKAQAEHtcBQ3iIcice1wFCAAAQyB7XKDAAAAABHtcoL96tvu8=
*** END OF RECORDS BASE64 ***

*** FATAL ***
fatal source: 1 (INTERNAL_ERROR_RTEMS_API)
fatal code: 3735928559 (0xdeadbeef)
RTEMS version: 6.1.0.not-released
RTEMS tools: 13.3.0 20240521 (RTEMS 6, RSB no-repo, Newlib 1b3dcfd)
executing thread ID: 0x0a010004
executing thread name: DUMP
cpu 0 in error mode (tt = 0x101)
  5812360  0200e420:  91d02000   ta  0x0
Run time     : 0:00:00.258692


```

![Help](/docs/kernel/docs/1.png).















