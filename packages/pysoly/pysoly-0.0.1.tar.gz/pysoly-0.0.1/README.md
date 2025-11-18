# PySoly #

## What is this? ##
PySoly is a Python library that allows you to interact with Windows applications and processes.  
It provides tools to capture screenshots, simulate clicks, read colors, and manipulate process memory with ease.  
The library is designed for automation, testing, and analysis of Windows applications and games.

---

## Quick Guide ##
The library is divided into two main parts:

1. **Display module (`PySoly.display.coordinates`)**  
   Work with windows visually: take screenshots, click on specific coordinates, read pixel colors, and get average brightness values from regions.

2. **Memory module (`PySoly.display.addresses`)**  
   Attach to a process, read and write memory, handle pointer chains, and work with modules in a running process.

---

## Installation ##

You can install them all at once using pip:

```bash
pip install numpy pillow pymem pywin32


Install PySoly via pip (if published on PyPI):

```bash
pip install pysoly
