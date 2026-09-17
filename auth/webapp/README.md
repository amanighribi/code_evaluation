# Interface web — Évaluation automatique de code (ESPRIT)

## Installation
```bash
npm install
cp .env.example .env
npm run dev
```
Ouvrir http://localhost:5173

## Logo ESPRIT
Déposez votre fichier `esprit-logo.png` dans `public/`.
S'il est absent, l'interface s'affiche normalement sans le logo.

## Backend requis
Le serveur FastAPI doit tourner (`python run_dev_server.py`) avec CORS activé.
