# 🚀 Guide de Déploiement sur Hetzner Cloud

**Objectif** : Migrer votre bot de trading depuis MacBook vers un serveur Hetzner Cloud pour un fonctionnement 24/7 stable et fiable.

---

## 📋 Table des matières
1. [Prérequis](#prérequis)
2. [Étape 1 : Créer le serveur](#étape-1--créer-le-serveur-hetzner)
3. [Étape 2 : Configuration initiale](#étape-2--configuration-initiale)
4. [Étape 3 : Installation des dépendances](#étape-3--installation-des-dépendances)
5. [Étape 4 : Configuration IB Gateway](#étape-4--configuration-ib-gateway)
6. [Étape 5 : Déploiement du bot](#étape-5--déploiement-du-bot)
7. [Étape 6 : Surveillance et maintenance](#étape-6--surveillance-et-maintenance)
8. [Troubleshooting](#troubleshooting)

---

## Prérequis

### Sur votre machine locale
- ✅ Compte Hetzner créé (login : redwanmaatoug@gmail.com)
- ✅ Clé SSH générée (`ssh-keygen -t ed25519` si besoin)
- ✅ Votre fichier `.env` actuel avec TOKEN/CHAT_ID
- ✅ Compte IBKR avec Paper Trading activé
- ⚠️ **Authentification 2FA IBKR désactivée** (ou configurer IBC avec codes)

### Budget Hetzner Cloud
- **Serveur CPX11** : ~4-5€/mois (2 vCPU, 2 Go RAM, 40 Go SSD)
- **Serveur CX21** : ~6-7€/mois (2 vCPU, 4 Go RAM, 40 Go SSD)

**Recommandation** : CX21 pour plus de confort (4 Go RAM pour IB Gateway + bot)

---

## Étape 1 : Créer le serveur Hetzner

### 1.1 Connexion à Hetzner Cloud Console
1. Allez sur https://console.hetzner.com
2. Connectez-vous avec vos identifiants :
   - Email : `redwanmaatoug@gmail.com`
   - Password : *(votre mot de passe)*

### 1.2 Créer un nouveau projet
1. Cliquez sur **"New Project"** (si premier serveur)
2. Nom du projet : `trading-bot-prod` (ou autre)

### 1.3 Ajouter votre clé SSH
1. Dans le menu de gauche → **Security** → **SSH Keys**
2. Cliquez sur **"Add SSH Key"**
3. Copiez votre clé publique :
   ```bash
   cat ~/.ssh/id_ed25519.pub
   # OU
   cat ~/.ssh/id_rsa.pub
   ```
4. Collez-la dans Hetzner et donnez un nom : `macbook-key`

### 1.4 Créer le serveur (VPS)
1. Dans votre projet → **"Add Server"**
2. **Location** : Nuremberg (Allemagne) ou Falkenstein
3. **Image** : Ubuntu 22.04 LTS
4. **Type** : 
   - **CX21** (recommandé) : 4 Go RAM, 2 vCPU
   - Ou CX11 si budget serré : 2 Go RAM, 1 vCPU
5. **Networking** : 
   - IPv4 activé
   - IPv6 optionnel
6. **SSH Keys** : Sélectionnez `macbook-key`
7. **Name** : `trading-bot-1`
8. Cliquez sur **"Create & Buy now"**

### 1.5 Notez l'adresse IP
Une fois le serveur créé (1-2 min), notez l'**adresse IP publique** :
```
Exemple : 95.217.123.456
```

### 1.6 Test de connexion SSH
```bash
# Remplacez par votre IP
ssh root@95.217.123.456
```

Si connexion OK → passez à l'étape 2 ✅

---

## Étape 2 : Configuration initiale

### 2.1 Mise à jour système
Connectez-vous au serveur et lancez :
```bash
ssh root@VOTRE_IP

# Mise à jour
apt update && apt upgrade -y
```

### 2.2 Créer un utilisateur dédié (sécurité)
```bash
# Créer utilisateur 'trader'
adduser trader
usermod -aG sudo trader

# Copier clé SSH
mkdir -p /home/trader/.ssh
cp ~/.ssh/authorized_keys /home/trader/.ssh/
chown -R trader:trader /home/trader/.ssh
chmod 700 /home/trader/.ssh
chmod 600 /home/trader/.ssh/authorized_keys
```

### 2.3 Se connecter avec le nouvel utilisateur
```bash
# Depuis votre MacBook
ssh trader@VOTRE_IP
```

### 2.4 Configurer le fuseau horaire
```bash
sudo timedatectl set-timezone Europe/Paris
# OU votre timezone
timedatectl  # Vérifier
```

---

## Étape 3 : Installation des dépendances

### 3.1 Lancer le script de setup automatique
```bash
# Télécharger le script
wget https://raw.githubusercontent.com/rmaatoug/labase-trading-alerts/main/scripts/setup_server.sh

# Rendre exécutable
chmod +x setup_server.sh

# Lancer l'installation
./setup_server.sh
```

Ce script installe automatiquement :
- ✅ Python 3.10+
- ✅ pip et virtualenv
- ✅ Git
- ✅ Xvfb (serveur X virtuel pour IB Gateway)
- ✅ VNC (pour accès graphique si besoin)
- ✅ Java 11 (requis pour IB Gateway)
- ✅ IBC (IB Controller pour automatisation)

**⏱️ Durée** : 5-10 minutes

---

## Étape 4 : Configuration IB Gateway

### 4.1 Télécharger IB Gateway
```bash
cd ~
mkdir -p ~/ibgateway
cd ~/ibgateway

# Version stable (paper trading)
wget https://download2.interactivebrokers.com/installers/ibgateway/stable-standalone/ibgateway-stable-standalone-linux-x64.sh

# Rendre exécutable
chmod +x ibgateway-stable-standalone-linux-x64.sh

# Installer (mode graphique via VNC)
./ibgateway-stable-standalone-linux-x64.sh
```

### 4.2 Configuration IBC (automatisation)

**Fichier de config IBC** (`~/ibc/config.ini`) :
```ini
# Identifiants IBKR
IbLoginId=VOTRE_USERNAME_IBKR
IbPassword=VOTRE_PASSWORD_IBKR

# Mode paper trading
TradingMode=paper

# Port API
IbApiPort=4002

# Accepter automatiquement
AcceptIncomingConnectionAction=accept
IbAutoClosedown=no
ClosedownAt=
StoreSettingsOnServer=no

# 2FA (si activé - sinon laisser vide)
# SecondFactorDevice=
```

### 4.3 Script de démarrage IB Gateway
```bash
# Créer le script
nano ~/start_ibgateway.sh
```

Contenu :
```bash
#!/bin/bash
export DISPLAY=:1
Xvfb :1 -screen 0 1024x768x24 &
sleep 2
~/ibc/scripts/ibcstart.sh ~/ibgateway &
```

```bash
chmod +x ~/start_ibgateway.sh
```

### 4.4 Test de démarrage IB Gateway
```bash
./start_ibgateway.sh

# Vérifier que le processus tourne
ps aux | grep gateway
```

---

## Étape 5 : Déploiement du bot

### 5.1 Cloner le repository
```bash
cd ~
git clone https://github.com/rmaatoug/labase-trading-alerts.git
cd labase-trading-alerts
```

### 5.2 Créer l'environnement virtuel
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 5.3 Configurer `.env`
```bash
cp .env.example .env
nano .env
```

Remplir avec vos vraies valeurs :
```bash
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_ID=987654321
IBKR_HOST=127.0.0.1
IBKR_PORT=4002
IBKR_CLIENT_ID=7
```

### 5.4 Test de connexion
```bash
python3 src/main.py
```

Devrait afficher :
```
✅ IBKR connecté
✅ Telegram OK
```

### 5.5 Premier test du bot
```bash
# Test manuel une fois
python3 trade_breakout_paper.py

# Vérifier logs
cat logs/bot.log
```

### 5.6 Installation des cron jobs
```bash
chmod +x scripts/install_cron.sh
./scripts/install_cron.sh

# Vérifier
crontab -l
```

### 5.7 Démarrer le bot en production
```bash
./scripts/start.sh
```

### 5.8 Vérifier le statut
```bash
./scripts/status.sh

# Voir les logs en temps réel
tail -f logs/bot.log
```

---

## Étape 6 : Surveillance et maintenance

### 6.1 Vérifications quotidiennes
- ✅ Message Telegram à 9h (heartbeat matinal)
- ✅ Alertes watchdog si bot arrêté
- ✅ Rapport quotidien à 22h

### 6.2 Commandes utiles
```bash
# Status bot
./scripts/status.sh

# Arrêter bot
./scripts/stop.sh

# Redémarrer bot
./scripts/stop.sh && ./scripts/start.sh

# Logs en direct
tail -f logs/bot.log

# Derniers trades
tail -20 trades_log.csv
```

### 6.3 Configuration systemd (optionnel - pour redémarrage auto)
Créer `/etc/systemd/system/trading-bot.service` :
```ini
[Unit]
Description=Trading Bot Runner
After=network.target

[Service]
Type=simple
User=trader
WorkingDirectory=/home/trader/labase-trading-alerts
ExecStart=/home/trader/labase-trading-alerts/venv/bin/python3 /home/trader/labase-trading-alerts/runner_5m.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl enable trading-bot
sudo systemctl start trading-bot
sudo systemctl status trading-bot
```

### 6.4 Sauvegarde des logs (optionnel)
```bash
# Synchroniser vers GitHub
cd ~/labase-trading-alerts
python3 sync_logs.py --backup
git add backups/
git commit -m "backup logs $(date +%Y-%m-%d)"
git push
```

---

## Troubleshooting

### Problème 1 : Error 321 - API Read-Only Mode ⚠️
**Symptôme** : `Error 321: The API interface is currently in Read-Only mode`

Ce problème empêche le bot de passer des ordres (lecture seule).

**Solutions (dans l'ordre)** :

1. **Vérifier le fichier IBC config.ini**
   ```bash
   grep -i readonlyapi ~/ibc/config.ini
   ```
   Doit contenir : `ReadOnlyApi=no`
   
   Si absent, ajouter la ligne :
   ```bash
   echo "ReadOnlyApi=no" >> ~/ibc/config.ini
   ```

2. **Vérifier le fichier jts.ini du Gateway**
   ```bash
   # Trouver le fichier jts.ini
   find ~/Jts -name "jts.ini" -type f
   
   # Éditer chaque fichier trouvé
   nano ~/Jts/jts.ini
   ```
   
   Sous la section `[API]`, ajouter ou modifier :
   ```ini
   [API]
   ReadOnly=false
   ```

3. **Redémarrer IB Gateway**
   ```bash
   ./scripts/stop_ibgateway.sh
   sleep 5
   ./scripts/start_ibgateway.sh
   ```

4. **Si le problème persiste → Configuration compte IBKR**
   
   Le paramètre Read-Only peut être configuré côté serveur IBKR :
   
   - Connectez-vous sur https://www.interactivebrokers.com/sso/Login
   - Allez dans **Settings** → **API** → **Settings**
   - Cherchez l'option **"Read-Only API"** ou **"API Settings"**
   - Décochez **"Enable Read-Only Mode"** si présent
   - **Sauvegardez** et attendez 5-10 minutes
   - Redémarrez IB Gateway

5. **Vérifier avec test de connexion**
   ```bash
   cd ~/labase-trading-alerts
   source venv/bin/activate
   python3 src/main.py
   ```
   
   Si vous voyez toujours l'erreur 321, attendez quelques minutes après la modification du portail IBKR.

**Note** : Le mode Read-Only est souvent activé par défaut pour des raisons de sécurité. Il faut explicitement le désactiver dans les 3 endroits : config.ini, jts.ini, et potentiellement le portail web IBKR.

---

### Problème 2 : IB Gateway ne se connecte pas
**Symptôme** : `API error 504: Not connected`

**Solutions** :
1. Vérifier que IB Gateway tourne : `ps aux | grep gateway`
2. Redémarrer IB Gateway : `pkill -f gateway && ./start_ibgateway.sh`
3. Vérifier port 4002 ouvert : `netstat -tuln | grep 4002`

### Problème 3 : Bot ne démarre pas
**Symptôme** : `runner_5m.py` crash immédiatement

**Solutions** :
1. Vérifier `.env` : `cat .env` (TOKEN et CHAT_ID présents ?)
2. Tester connexions : `python3 src/main.py`
3. Vérifier logs : `cat logs/bot.log`
4. Permissions : `chmod +x scripts/*.sh`

### Problème 4 : Pas de notifications Telegram
**Symptôme** : Bot tourne mais pas de messages

**Solutions** :
1. Tester Telegram : `python3 -c "from src.telegram_client import send_telegram; send_telegram('Test')"`
2. Vérifier TOKEN/CHAT_ID dans `.env`
3. Vérifier que bot Telegram est démarré (envoyer `/start` au bot)

### Problème 5 : "Order quantity too large"
**Symptôme** : Rejets IBKR pour qty > 500

**Solution** : Déjà fixé dans `trade_breakout_paper.py` (ligne ~130) avec `min(qty, 500)`

### Problème 6 : Serveur manque de RAM
**Symptôme** : Processus tués (OOM killer)

**Solutions** :
1. Upgrader vers CX21 (4 Go RAM) ou CX31 (8 Go)
2. Ajouter swap :
   ```bash
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   ```

---

## 📊 Checklist finale

- [ ] Serveur Hetzner créé et accessible via SSH
- [ ] Utilisateur `trader` configuré
- [ ] Python + dépendances installées
- [ ] IB Gateway installé et démarré
- [ ] IBC configuré avec identifiants IBKR
- [ ] Repository cloné
- [ ] `.env` configuré avec vrais TOKEN/CHAT_ID
- [ ] Test connexion : `python3 src/main.py` → OK
- [ ] Cron jobs installés : `crontab -l`
- [ ] Bot démarré : `./scripts/start.sh`
- [ ] Status vérifié : `./scripts/status.sh`
- [ ] Logs en temps réel : `tail -f logs/bot.log`
- [ ] Premier message Telegram reçu ✅

---

## 🎯 Résultat attendu

Après déploiement complet, vous devez recevoir :
1. ✅ Message "🚀 Bot démarré" sur Telegram
2. ✅ Message "✅ BONJOUR" chaque jour à 9h
3. ✅ Alertes watchdog si problème
4. ✅ Rapport quotidien à 22h
5. ✅ Notifications de signaux/trades en temps réel

**Bot tourne 24/7 de manière autonome** 🚀

---

## 📞 Support

En cas de problème :
1. Vérifier logs : `tail -f logs/bot.log`
2. Vérifier watchdog : `cat logs/watchdog.log`
3. Relire `CONVERSATION_CONTEXT.md`
4. Tester manuellement : `python3 trade_breakout_paper.py`

---

**Date de création** : 13 février 2026  
**Version** : 1.0 (Production ready)
