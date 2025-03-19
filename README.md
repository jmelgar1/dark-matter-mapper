# 🌌 Dark Matter Mapper with Neural Networks

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.9%2B-blue)](https://python.org)
[![React](https://img.shields.io/badge/React-18%2B-blue)](https://reactjs.org)

**Predict 3D dark matter distributions using AI and visualize them in a React app.**  
*A full-stack project bridging cosmology, machine learning, and web development.*

## 🎯 Goals
- Train a neural network to map dark matter using SDSS/DES data.
- Build an interactive 3D visualization tool for researchers (or curious people).
- Possibly compare my results with more traditional methods.

## 🛠 Tech Stack
- **AI/Backend**: Python, PyTorch, FastAPI, AstroPy
- **Frontend**: React, TypeScript, Three.js, Deck.gl
- **Infra**: Docker, AWS EC2/S3

## 🚀 Features
- 3D volumetric rendering of dark matter.

## 📦 Installation
```bash
# Clone the repo
git clone https://github.com/<username>/dark-matter-mapper.git
cd dark-matter-mapper

# Install backend dependencies
cd backend && pip install -r requirements.txt

# Install frontend dependencies
cd ../frontend && npm install
