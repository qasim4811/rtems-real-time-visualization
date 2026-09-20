# Tutorial 4:Visualization using Eclipse Trace Compass
> **Goal:** Becoming familiar with the Eclipse Trace Compass.
---
## Install Eclipse and Trace Compass
Download and Install Eclipse IDE:

[Eclipse installer](https://www.eclipse.org/downloads/download.php?file=/oomph/epp/2025-12/R/eclipse-inst-jre-linux64.tar.gz)

During installation choose Eclipse IDE for C/C++ Developer

Install Trace Compass as showing in following figures:

Open the Help menu and choose Eclipse Marketplace, as illustrated in the figure below.

![Help](/docs/Visualization/docs/2.png)

A new window will pop up. Search for the Trace compass plugin and install it, as shown in the figure below.

![Trace compass](/docs/Visualization/docs/3.png)

Open New tracing Project
Click on File → New → Other, then select Tracing, and choose Tracing Project, as shown in the figure below.Name the project and then finish.

![Create Project](/docs/Visualization/docs/4.png)


---
## View matadeta
Click on Open Trace, select the metadata generated in Tutorial 3, and open it, as shown in the figures below.

![ ](/docs/Visualization/docs/5.png)

![ ](/docs/Visualization/docs/6.png)

Cick on control flow to view Tasks

![ ](/docs/Visualization/docs/7.png)

### Trace Compass Feature
In the left view, you will find Task A, Task B, Dump Task, and the Idle state. The item named UI1 corresponds to the Init task.
#### Task on y axis
![ Task on y axis ](/docs/Visualization/docs/8.png)

#### Useful features
![Useful features](/docs/Visualization/docs/9.png)
#### Legends indicating Task state
![Legends indicating Task state](/docs/Visualization/docs/10.png)

Before opening a new trace, it is recommended to clear the current trace first.

##### Clear Traces
![Clear Traces](/docs/Visualization/docs/11.png)

---


## References
[Event Recording](https://docs.rtems.org/branches/main/user/tracing/eventrecording.html)
