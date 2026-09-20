# Tutorial 1: Preparation & Environment Setup
> **Goal:** Set up the RTEMS 6 toolsuite and the ERC32 (SIS) simulator.

---

##  Hardware Requirements

- Device: Laptop or Desktop PC.

- Processor: Intel Core i5 (or equivalent) recommended.

- Disk Space: ~15 GB free space (for tools, BSP, and ecosystem).

- RAM: 8 GB or more for smooth compilation.

---

##  Software Requirements
For this lab session, Ubuntu 24.04.3 LTS is used as the primary operating system. However, any version above 18.04 LTS is compatible.
Please make sure you can build native C/C++ applications on your host computer

Install C/C++ Compiler
```bash
sudo apt update
sudo apt install build-essential
```
Install Python

```bash
sudo apt install python3 python3-pip
```
Before starting, ensure that your host machine (Ubuntu/Linux) has the following dependencies installed. These are required only if you intend to build the toolsuite and BSP; however, Git is mandatory.
- `git`, `make`, `texinfo`, `python3-dev`, `pax`, `bison`, `flex`.

```bash
sudo apt update
sudo apt install git make texinfo python3-dev pax bison flex -y
```
---
## There are two ways to start: you can build the Tool Suite and BSP yourself, or use the pre-built files already provided within [repo](/Pre-built_Rtems_Toolsuite_BSP).

## Approach 1:The Manual Build Approach:
Manually compile the RTEMS Tool Suite and build the Board Support Package (BSP) from source

##  Step 1: Obtain the Sources ,install ToolSuite & Build Board Support Package 
Follow these commands in order to download the sources and build the environment.

## 1. Create Workspace, Download, and Rename
## Create the directory structure

```bash
mkdir -p $HOME/quick-start/src
cd $HOME/quick-start/src
```
## Download the RTEMS 6.1 sources
This lab session uses RTEMS version 6.1.
```bash
curl https://ftp.rtems.org/pub/rtems/releases/6/6.1/sources/rtems-source-builder-6.1.tar.xz | tar xJf -
```
## Rename the folder to rsb

```bash
mv rtems-source-builder-6.1 rsb

```
## 2. Build and install the tool suite
The tool suite for RTEMS and the RTEMS sources are tightly coupled. For example, do not use a RTEMS version 6 tool suite with RTEMS version 4.11 or 5 sources and vice versa.

path 6/rtems-sparc is the Build Set name. It tells the RTEMS Source Builder (RSB) exactly which configuration files to use to build the cross-compiler for the SPARC architecture (which the erc32 belongs to)

```bash
cd $HOME/quick-start/src/rsb/rtems
../source-builder/sb-set-builder --prefix=$HOME/quick-start/rtems/6  6/rtems-sparc
```
Once the build has successfully completed you can check if the cross C compiler works with the following command:

```bash
$HOME/quick-start/rtems/6/bin/sparc-rtems6-gcc --version
```
### output

```bash
qasim@qasim-HP-EliteBook-840r-G4:~/rtems_6_uni/quick-start/app/edf$ $HOME/rtems_6_uni/quick-start/rtems/6/bin/sparc-rtems6-gcc --version
sparc-rtems6-gcc (GCC) 13.3.0 20240521 (RTEMS 6, RSB no-repo, Newlib 1b3dcfd)
Copyright (C) 2023 Free Software Foundation, Inc.
This is free software; see the source for copying conditions.  There is NO
warranty; not even for MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
```
## 3. Build a Board Support Package 
For this lab, we have selected the erc32 Board Support Package. Unlike other targets (like STM32 or ARM) that require external hardware or complex QEMU configurations, the ERC32 comes with a built-in simulator called SIS(SPARC Instruction Simulator).
It uses a simple erc32-sis.ini configuration, making it much easier to run than QEMU.

### Path of erc32-sis.ini:
```
/quick-start/rtems/6/share/rtems/tester/rtems/testing/bsps/
```
### Build BSP
```bash
cd $HOME/quick-start/src/rsb/rtems
../source-builder/sb-set-builder --prefix=$HOME/quick-start/rtems/6 \
    --target=sparc-rtems6 --with-rtems-bsp=sparc/erc32 
```
This command should output something like:
```bash
RTEMS Source Builder - Set Builder, @rtems-ver-majminver@
Build Set: 6/rtems-kernel
config: tools/rtems-kernel-6.cfg
package: sparc-rtems6-kernel-erc32-1
building: sparc-rtems6-kernel-erc32-1
sizes: sparc-rtems6-kernel-erc32-1: 2.279GB (installed: 44.612MB)
cleaning: sparc-rtems6-kernel-erc32-1
reporting: tools/rtems-kernel-6.cfg -> sparc-rtems6-kernel-erc32-1.txt
reporting: tools/rtems-kernel-6.cfg -> sparc-rtems6-kernel-erc32-1.xml
installing: sparc-rtems6-kernel-erc32-1 -> $BASE/
cleaning: sparc-rtems6-kernel-erc32-1
Build Set: Time 0:03:09.896961
```
## Approach 2: Using the Pre-installed Tool Suite and BSP
In this approach, you skip the long compilation hours. The RTEMS Toolsuite (compiler and debugger) and the BSP (Board Support Package) have already been built for you and are available in the course’s GitHub repository.
1. Download the Tools: Clone or download the pre-built environment from the provided [repo](/Pre-built_Rtems_Toolsuite_BSP).

2. Verify Host Dependencies: Even though the RTEMS tools are ready, your Linux host still needs a few basic native tools to run the build scripts. Ensure you have Python 3 and a C/C++ compiler (GCC) installed:

  veirfy gcc version:
```bash
$HOME/quick-start/rtems/6/bin/sparc-rtems6-gcc --version

```
## References
[Obtain the Sources](https://docs.rtems.org/docs/6.1/user/start/sources.html)

[Install the Tool Suite](https://docs.rtems.org/docs/6.1/user/start/tools.html)

[Build a Board Support Package (BSP)](https://docs.rtems.org/docs/6.1/user/start/bsp-build.html)

[Download Pre-built RTEMS Toolsuite and BSP ](https://github.com/your-username/your-repo-name)
