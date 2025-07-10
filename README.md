# Déploiement sur Windows Server

Ce projet est une application Python conteneurisée avec Docker. Il utilise un Dockerfile pour construire l'application et un docker-compose.yml pour la gérer facilement.

## Prérequis sur le serveur Windows

Avant de déployer, assurez vous que le serveur Windows Server est prêt :

### 1. Installer Docker Desktop (mode Windows avec WSL2)
- Télécharger Docker Desktop : https://www.docker.com/products/docker-desktop/
- Suivre l'installation, et activer le backend WSL2 (il sera proposé automatiquement).
- Redémarrer la machine si demandé.

### 2. Vérifier l'installation

Ouvrir **PowerShell** et tester :

powershell
docker --version
docker-compose --version

### 3. Lancer le projet

Ouvrir **PowerShell** et écrire : 

docker-compose up --build


-- English --

# Deployment on Windows Server

This project is a Python application containerized with Docker. It uses a `Dockerfile` to build the application and a `docker-compose.yml` to manage it easily.

## Prerequisites on the Windows Server

Before deploying, make sure the Windows Server is ready:

### 1. Install Docker Desktop (Windows mode with WSL2)
- Download Docker Desktop: https://www.docker.com/products/docker-desktop/
- Follow the installation, and enable the WSL2 backend (it will be offered automatically).
- Restart the machine if prompted.

### 2. Verify the installation

Open **PowerShell** and test:

```powershell
docker --version
docker-compose --version


