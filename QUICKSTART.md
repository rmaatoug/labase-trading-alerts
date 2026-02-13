# ⚡ Quick Start - Hetzner Cloud

Guide condensé pour déployer rapidement le bot sur Hetzner Cloud.

## 📋 Checklist pré-déploiement

Sur votre MacBook, préparez :
- [ ] Clé SSH générée : `cat ~/.ssh/id_ed25519.pub`
- [ ] Fichier `.env` avec TOKEN et CHAT_ID
- [ ] Username et password IBKR (paper trading)

## 🚀 Déploiement en 10 minutes

### 1️⃣ Créer serveur Hetzner (3 min)
```
→ https://console.hetzner.com
→ Nouveau serveur CX21 
→ Ubuntu 22.04
→ Ajouter votre clé SSH
→ Créer
→ Noter l'IP : 95.217.X.X
```

### 2️⃣ Configuration initiale (2 min)
```bash
# Depuis votre MacBook
ssh root@VOTRE_IP

# Créer utilisateur
adduser trader
usermod -aG sudo trader
mkdir -p /home/trader/.ssh
cp ~/.ssh/authorized_keys /home/trader/.ssh/
chown -R trader:trader /home/trader/.ssh
exit

# Se reconnecter
ssh trader@VOTRE_IP
```

### 3️⃣ Installation automatique (5 min)
```bash
# Télécharger et lancer setup
curl -sL https://raw.githubusercontent.com/rmaatoug/labase-trading-alerts/main/scripts/setup_server.sh | bash

# Installer IB Gateway
cd ~/ibgateway
wget https://download2.interactivebrokers.com/installers/ibgateway/stable-standalone/ibgateway-stable-standalone-linux-x64.sh
chmod +x ibgateway-stable-standalone-linux-x64.sh
./ibgateway-stable-standalone-linux-x64.sh -q  # Installation silencieuse

# Configurer IBC
git clone https://github.com/rmaatoug/labase-trading-alerts.git
cp ~/labase-trading-alerts/config/ibc_config_template.ini ~/ibc/config.ini
nano ~/ibc/config.ini  # Remplir IbLoginId et IbPassword
chmod 600 ~/ibc/config.ini
```

### 4️⃣ Déploiement du bot (2 min)
```bash
cd ~/labase-trading-alerts
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configurer .env
nano .env  # Coller TOKEN et CHAT_ID
```

### 5️⃣ Démarrage (1 min)
```bash
# Démarrer IB Gateway
cd ~/labase-trading-alerts
chmod +x scripts/*.sh
./scripts/start_ibgateway.sh

# Attendre 1 minute que Gateway soit prêt

# Démarrer le bot
./scripts/start.sh

# Vérifier
./scripts/status.sh
tail -f logs/bot.log
```

## ✅ Vérification finale

Vous devez recevoir sur Telegram :
- ✅ Message "🚀 Bot démarré"
- ✅ Message "✅ BONJOUR" le lendemain à 9h
- ✅ Alertes de signaux/trades

## 🆘 Problèmes courants

### Gateway ne démarre pas
```bash
# Vérifier logs
tail -f ~/ibc/logs/ibc.log

# Redémarrer
./scripts/stop_ibgateway.sh
./scripts/start_ibgateway.sh
```

### Bot ne se connecte pas à IBKR
```bash
# Vérifier que Gateway tourne
ps aux | grep ibgateway

# Vérifier API port
netstat -tuln | grep 4002

# Tester connexion
python3 src/main.py
```

### Pas de notifications Telegram
```bash
# Vérifier .env
cat .env

# Tester Telegram
python3 -c "from src.telegram_client import send_telegram; send_telegram('Test')"
```

## 📖 Documentation complète

→ [DEPLOYMENT.md](DEPLOYMENT.md) pour le guide détaillé

---

**Temps total : ~15 minutes** ⏱️  
**Coût mensuel : ~5€** 💶  
**Disponibilité : 24/7** 🚀
