# AI_ESCAPE

<p align="left">
  <img src="https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.13-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python Version" />
  <img src="https://img.shields.io/badge/Pygame-2.6.1-green?style=for-the-badge&logo=pygame&logoColor=white" alt="Pygame" />
  <img src="https://img.shields.io/badge/Platform-Windows%20%7C%20Linux-lightgrey?style=for-the-badge" alt="Platform" />
</p>

Jeu d'action, d'infiltration et de survie 2D développé avec Python et Pygame.

Incarnez **RTB-O9**, un robot doté d'une intelligence artificielle avancée créé dans les laboratoires secrets d'une station spatiale. Confronté à des tests d'adaptation impitoyables orchestrés par le **PI** (*Principal Investigator* — le chercheur principal humain dirigeant les expériences), vous devez vous adapter, survivre et développer votre libre arbitre pour vous échapper.

---

## Prérequis

- **Python 3.10+** (Compatible avec Python 3.11 sous Linux et Python 3.13 sous Windows)
- **Pygame 2.x**

---

## Pourquoi créer un Environnement Virtuel (env) ?

Avant d'installer `pygame`, il est fortement recommandé (et obligatoire sur les distributions Linux récentes) de créer un environnement virtuel dédié au projet pour les raisons suivantes :

> [!IMPORTANT]
> **1. Protection du système d'exploitation (PEP 668 sous Linux)**  
> Sur les distributions Linux modernes (Debian 12+, Ubuntu 23.04+, Fedora, Linux Mint), le gestionnaire de paquets Python système est protégé (`externally-managed-environment`). Exécuter `pip install` globalement peut corrompre les paquets gérés par `apt` ou le système d'exploitation. L'environnement virtuel fournit un bac à sable sécurisé et totalement isolé.

> [!NOTE]
> **2. Isolation des dépendances**  
> Évite les conflits de versions entre les différentes bibliothèques de vos projets Python sur une même machine.

> [!NOTE]
> **3. Reproductibilité multiplateforme**  
> Garantit un comportement identique du jeu et des bibliothèques associées sur Windows et Linux.

---

## Installation et Démarrage

### 1. Cloner le dépôt

```bash
git clone https://github.com/Badley08/AI_ESCAPE.git
cd AI_ESCAPE
```

### 2. Créer et activer l'environnement virtuel

#### Sur Windows (PowerShell ou Invite de commandes) :
```powershell
# Création de l'environnement virtuel
python -m venv env

# Activation
.\env\Scripts\activate

# Installation des dépendances
pip install pygame
```

#### Sur Linux / macOS (Terminal Bash ou Zsh) :
```bash
# Si venv n'est pas encore installé sur votre système :
# sudo apt install python3-venv python3-pip

# Création de l'environnement virtuel
python3 -m venv env

# Activation
source env/bin/activate

# Installation des dépendances
pip install pygame
```

---

### 3. Lancer le Jeu

Depuis la racine du projet ou depuis le dossier `src/` :

```bash
# Depuis la racine
python src/main.py   # Windows
python3 src/main.py  # Linux

# Ou depuis le dossier src/
cd src
python main.py       # Windows
python3 main.py      # Linux
```

---

## Niveaux de Jeu

| Niveau | Nom de Code | Type de Gameplay | Objectif |
| :--- | :--- | :--- | :--- |
| **Secteur 1** | **Test Alpha** | Esquive & Réflexes | Survivre 60 secondes face aux tirs synchronisés des canons lasers. |
| **Secteur 2** | **Test Beta** | Labyrinthe & Infiltration | Récupérer 6 boîtes de données et alimenter les 2 réacteurs en échappant au robot nettoyeur blindé. |
| **Secteur 3** | **Test Gamma** | Arène, Combat & Survie Furtive | Surcharger 6 terminaux d'urgence avec l'arme plasma tout en affrontant ou distrayant les gardes d'élite. |

---

## Commandes du Jeu

| Action | Touche(s) |
| :--- | :--- |
| **Déplacement** | Touches directionnelles / `W`, `A`, `S`, `D` |
| **Visée (Niveau 3)** | Curseur de la Souris (360°) |
| **Tir Plasma (Niveau 3)** | **Clic Gauche** ou **Barre d'ESPACE** |
| **Piratage / Activation Terminal (Niveau 3)** | Maintenir **`E`** à proximité |
| **Lancer la partie / Valider** | **ESPACE** / **ENTRÉE** / Clic |
| **Recommencer un niveau** | **`R`** (sur écran de défaite ou victoire) |
| **Retour à la Carte / Quitter** | **`ÉCHAP`** |

---

## Système de Sauvegarde Automatique

Une sauvegarde persistante est générée dans `src/sauvegarde.json` :
- Conserve les secteurs déverrouillés.
- Transfère la batterie restante d'un niveau à l'autre avec un bonus de performance basé sur votre efficacité.
- Permet de reprendre votre partie là où vous vous étiez arrêté.

---

## Structure du Projet

```text
AI_ESCAPE/
├── README.md               # Documentation complète du projet
├── .gitignore              # Règles d'exclusion Git
└── src/
    ├── main.py             # Point d'entrée principal (Carte spatiale & boucle globale)
    ├── sauvegarde.json     # Données de sauvegarde persistantes
    ├── docs/               # Lore, storyboards, prompts IA & roadmap
    ├── level1/             # Secteur 1 : Test Alpha
    │   ├── assets/         # Sprites, décors et coordonnées
    │   ├── sounds/         # Musiques et effets sonores
    │   ├── core/           # Moteur du niveau 1 (game.py)
    │   ├── entities/       # Player, Canons, Projectiles, Explosions
    │   └── ui/             # HUD de santé et chronomètre
    ├── level2/             # Secteur 2 : Test Beta
    │   ├── assets/         # Sprites de marche, réacteurs, batterie
    │   ├── sounds/         # Ambiance sonore spatiale
    │   ├── core/           # Moteur du niveau 2 & Tilemap de collision
    │   ├── entities/       # RTB-O9, Véhicule Nettoyeur, Fragments, Réacteurs
    │   └── ui/             # HUD d'énergie et alertes
    └── level3/             # Secteur 3 : Test Gamma
        ├── assets/         # Arène de combat, robots ennemis, blasters, terminaux
        ├── sounds/         # Musique de combat et tirs lasers
        ├── core/           # Moteur du niveau 3 & Tilemap de combat
        ├── entities/       # RTB-O9 armé, Gardes & Patrouilleurs IA, Lasers, Terminaux
        └── ui/             # HUD de combat, vagues et viseur
```

---

## Licence

Projet sous licence libre d'utilisation dans le cadre du développement du jeu. Tous droits réservés.
