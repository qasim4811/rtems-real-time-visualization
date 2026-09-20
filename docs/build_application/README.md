# Tutorial 2: Build Your Application
> **Goal:** Running First Example using waf script

---
## Create the application directory and change into it:
## Note
Example is already Provided with pre-compiled repository [repo](/Pre-built_Rtems_Toolsuite_BSP).,if you have done manual build,you can skip the following  step to create new directory.

```bash
mkdir -p $HOME/quick-start/app/hello
cd $HOME/quick-start/app/hello
```

---
## Note
Steps 1 to 6 are only required for manual builds. If you have downloaded the pre-compiled repository [repo](/Pre-built_Rtems_Toolsuite_BSP), please skip.

If you wish to see RTEMS in action immediately, you may jump directly to Step 7 (Configuration) and then till Step 10 (Execution) to run the pre-built example.
It is highly recommended that you follow the full sequence from Step 1 to Step 10. Completing the application build process is essential for understanding how the RTEMS kernel and the Waf build system work together.
### step 1: Download the Waf build system and set it to executable:
```bash
curl https://waf.io/waf-2.0.19 > waf
chmod +x waf
```
### step 2: Initialise a new Git repository:
```bash
git init
```
### step 3: add RTEMS Waf support as a Git sub-module and initialise it:
```bash
git submodule add https://gitlab.rtems.org/rtems/tools/rtems_waf.git rtems_waf
```
### step 4: First create a C file that configures RTEMS. Using an editor create a file called init.c and copy the following configuration settings:
```bash
/*
 * Simple RTEMS configuration
 */

#define CONFIGURE_APPLICATION_NEEDS_CLOCK_DRIVER
#define CONFIGURE_APPLICATION_NEEDS_CONSOLE_DRIVER

#define CONFIGURE_UNLIMITED_OBJECTS
#define CONFIGURE_UNIFIED_WORK_AREAS

#define CONFIGURE_RTEMS_INIT_TASKS_TABLE

#define CONFIGURE_INIT

#include <rtems/confdefs.h>
```
### step 5: Create the Hello World application source file. Using an editor create hello.c and copy the following  code:
```bash
/*
 * Hello world example
 */
#include <rtems.h>
#include <stdlib.h>
#include <stdio.h>

rtems_task Init(
  rtems_task_argument ignored
)
{
  printf( "\nHello World\n" );
  exit( 0 );
}
```

### step 6: Finally create the Waf script and copy the Waf script:
target name is the output exe file.
```bash
#
# Hello world Waf script
#
from __future__ import print_function

rtems_version = "6"

try:
    import rtems_waf.rtems as rtems
except:
    print('error: no rtems_waf git submodule')
    import sys
    sys.exit(1)

def init(ctx):
    rtems.init(ctx, version = rtems_version, long_commands = True)

def bsp_configure(conf, arch_bsp):
    # Add BSP specific configuration checks
    pass

def options(opt):
    rtems.options(opt)

def configure(conf):
    rtems.configure(conf, bsp_configure = bsp_configure)

def build(bld):
    rtems.build(bld)

    bld(features = 'c cprogram',
        target = 'hello.exe',
        cflags = '-g -O2',
        source = ['hello.c',
                  'init.c'])
```
### step 7: Configure the application using Waf’s configure command:
```bash
./waf configure   --rtems=$HOME/quick-start/rtems/6   --rtems-tools=$HOME/quick-start/rtems/6   --rtems-bsp=sparc/erc32
```
The output will be something close to:
```bash
Setting top to                           : $BASE/app/hello
Setting out to                           : $BASE/app/hello/build
RTEMS Version                            : 6
Architectures                            : sparc-rtems6
Board Support Package (BSP)              : sparc-rtems6-erc32
Show commands                            : no
Long commands                            : no
Checking for program 'sparc-rtems6-gcc'  : $BASE/rtems/6/bin/sparc-rtems6-gcc
Checking for program 'sparc-rtems6-g++'  : $BASE/rtems/6/bin/sparc-rtems6-g++
Checking for program 'sparc-rtems6-gcc'  : $BASE/rtems/6/bin/sparc-rtems6-gcc
Checking for program 'sparc-rtems6-ld'   : $BASE/rtems/6/bin/sparc-rtems6-ld
Checking for program 'sparc-rtems6-ar'   : $BASE/rtems/6/bin/sparc-rtems6-ar
Checking for program 'sparc-rtems6-nm'   : $BASE/rtems/6/bin/sparc-rtems6-nm
Checking for program 'sparc-rtems6-objdump' : $BASE/rtems/6/bin/sparc-rtems6-objdump
Checking for program 'sparc-rtems6-objcopy' : $BASE/rtems/6/bin/sparc-rtems6-objcopy
Checking for program 'sparc-rtems6-readelf' : $BASE/rtems/6/bin/sparc-rtems6-readelf
Checking for program 'sparc-rtems6-strip'   : $BASE/rtems/6/bin/sparc-rtems6-strip
Checking for program 'sparc-rtems6-ranlib'  : $BASE/rtems/6/bin/sparc-rtems6-ranlib
Checking for program 'rtems-ld'             : $BASE/rtems/6/bin/rtems-ld
Checking for program 'rtems-tld'            : $BASE/rtems/6/bin/rtems-tld
Checking for program 'rtems-syms'           : $BASE/rtems/6/bin/rtems-syms
Checking for program 'rtems-bin2c'          : $BASE/rtems/6/bin/rtems-bin2c
Checking for program 'tar'                  : /usr/bin/tar
Checking for program 'gcc, cc'              : $BASE/rtems/6/bin/sparc-rtems6-gcc
Checking for program 'ar'                   : $BASE/rtems/6/bin/sparc-rtems6-ar
Checking for program 'g++, c++'             : $BASE/rtems/6/bin/sparc-rtems6-g++
Checking for program 'ar'                   : $BASE/rtems/6/bin/sparc-rtems6-ar
Checking for program 'gas, gcc'             : $BASE/rtems/6/bin/sparc-rtems6-gcc
Checking for program 'ar'                   : $BASE/rtems/6/bin/sparc-rtems6-ar
Checking for c flags '-MMD'                 : yes
Checking for cxx flags '-MMD'               : yes
Compiler version (sparc-rtems6-gcc)         : 10.2.1 20210309 (RTEMS 6, RSB 5e449fb5c2cb6812a238f9f9764fd339cbbf05c2, Newlib d10d0d9)
Checking for a valid RTEMS BSP installation : yes
Checking for RTEMS_DEBUG                    : no
Checking for RTEMS_MULTIPROCESSING          : no
Checking for RTEMS_NEWLIB                   : yes
Checking for RTEMS_POSIX_API                : no
Checking for RTEMS_SMP                      : no
Checking for RTEMS_NETWORKING               : no
'configure' finished successfully (1.142s)
```
### step 8: Build the application:
```bash
./waf 
```
The output will be something close to:
```bash
Waf: Entering directory `$BASE/app/hello/build/sparc-rtems6-erc32'
[1/3] Compiling init.c
[2/3] Compiling hello.c
[3/3] Linking build/sparc-rtems6-erc32/hello.exe
Waf: Leaving directory `$BASE/app/hello/build/sparc-rtems6-erc32'
'build-sparc-rtems6-erc32' finished successfully (0.183s)
```
hello.exe will be created in this folder build/sparc-rtems6-erc32

### step 9: Export  Path
```bash
export PATH=$HOME/quick-start/rtems/6/bin:"$PATH" 
```
### step 10: Run the Application
```bash
cd $HOME/quick-start/app/hello/build/sparc-rtems6-erc32

rtems-run --rtems-bsps=erc32-sis  hello.exe
```

The output will be something close to:

```bash
RTEMS Testing - Run, 6.0.not_released
 Command Line: /home/qasim//rtems_6_uni/quick-start/rtems/6/bin/rtems-run --rtems-bsps=erc32-sis build/sparc-rtems6-erc32/hello.exe
 Host: Linux qasim-HP-EliteBook-840r-G4 6.14.0-37-generic #37~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC Thu Nov 20 10:25:38 UTC 2 x86_64
 Python: 3.12.3 (main, Jan  8 2026, 11:30:50) [GCC 13.3.0]
Host: Linux-6.14.0-37-generic-x86_64-with-glibc2.39 (Linux qasim-HP-EliteBook-840r-G4 6.14.0-37-generic #37~24.04.1-Ubuntu SMP PREEMPT_DYNAMIC Thu Nov 20 10:25:38 UTC 2 x86_64 x86_64)

 SIS - SPARC/RISCV instruction simulator 2.30,  copyright Jiri Gaisler 2020
 Bug-reports to jiri@gaisler.se

 ERC32 emulation enabled

 Loaded build/sparc-rtems6-erc32/hello.exe, entry 0x02000000

Hello World

[ RTEMS shutdown ]
RTEMS version: 6.1.0.not-released
RTEMS tools: 13.3.0 20240521 (RTEMS 6, RSB no-repo, Newlib 1b3dcfd)
executing thread ID: 0x0a010001
executing thread name: UI1 
cpu 0 in error mode (tt = 0x101)
    84398  0200c760:  91d02000   ta  0x0
Run time     : 0:00:00.258520

```
## References
[Build Your Application](https://docs.rtems.org/docs/6.1/user/start/app.html)
