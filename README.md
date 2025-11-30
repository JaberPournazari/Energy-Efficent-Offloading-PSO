# ECO-CSA: Multi-objective Energy-centric Task Offloading in Fog Computing

This repository contains the implementation of the **ECO-CSA** algorithm, a multi-objective optimisation method designed to reduce energy consumption and improve task offloading efficiency in **Fog Computing** environments.

This code is associated with the following research paper:

**Multi-objective optimisation for energy-centric offloading in fog computing**  
Jaber Pournazari, Amjad Ullah, Ahmed Al–Dubai, Xiaodong Liu, Navid Khaledian  
*Published: 24 October 2025 · Volume 107, Article 220*

---

## 📌 About the Project
ECO-CSA combines **ECO-PSO** and **CSA** with a gradient-based dynamic coefficient adjustment mechanism.  
The algorithm explicitly models:

- ⚙️ Energy consumption in **computing**
- 🔄 Energy consumption in **transmission**
- 🧠 Energy consumption in **memory**
- ⏳ **Makespan** optimisation

It also includes a custom energy model to select low-CPU-utilisation fog nodes, enhancing both efficiency and balance in heterogeneous fog environments.

---

## 🚀 Key Results (as reported in the paper)
- Up to **25% reduction** in total energy consumption  
- Up to **30% reduction** in makespan  
- More balanced task distribution than PSG, PSG-M, CCFO, and MoAOA

---

## 📁 Repository Structure

<img width="205" height="316" alt="image" src="https://github.com/user-attachments/assets/abd87cbc-5531-4756-9090-5bfa9ea16051" />


## 🔗 Article

For full details, see the original publication on Springer:  
https://link.springer.com/article/10.1007/s00607-025-01578-w


