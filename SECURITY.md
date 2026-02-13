# 🔒 Guide de Sécurité - Serveur Cloud

Ce guide contient les meilleures pratiques de sécurité pour votre serveur de trading sur Hetzner Cloud.

## ⚠️ Risques principaux

1. **Identifiants IBKR exposés** → Accès non autorisé au compte trading
2. **Tokens Telegram exposés** → Spam ou accès aux messages
3. **Serveur compromis** → Exécution de code malveillant
4. **Port API ouvert** → Accès externe non autorisé

---

## 🛡️ Checklist de sécurité (OBLIGATOIRE)

### 1. Gestion des identifiants

- [ ] **Fichier .env protégé**
  ```bash
  chmod 600 ~/.env
  chmod 600 ~/ibc/config.ini
  ```

- [ ] **Ne JAMAIS commiter .env ou config.ini**
  ```bash
  # Déjà dans .gitignore, mais vérifier :
  git status  # .env ne doit PAS apparaître
  ```

- [ ] **Utiliser Paper Trading uniquement**
  - Testez d'abord en simulation
  - Ne passez en live QU'APRÈS validation complète
  - Paper trading = risque zéro

### 2. Accès SSH

- [ ] **Désactiver connexion root par mot de passe**
  ```bash
  sudo nano /etc/ssh/sshd_config
  ```
  Modifier :
  ```
  PermitRootLogin no
  PasswordAuthentication no
  PubkeyAuthentication yes
  ```
  Redémarrer SSH :
  ```bash
  sudo systemctl restart sshd
  ```

- [ ] **Utiliser clés SSH uniquement**
  - Jamais de mot de passe pour SSH
  - Protéger votre clé privée : `chmod 600 ~/.ssh/id_ed25519`

- [ ] **Changer le port SSH (optionnel mais recommandé)**
  ```bash
  sudo nano /etc/ssh/sshd_config
  # Port 22 -> Port 2222
  sudo systemctl restart sshd
  ```
  Connexion ensuite : `ssh -p 2222 trader@VOTRE_IP`

### 3. Firewall (UFW)

- [ ] **Installer et configurer UFW**
  ```bash
  sudo apt install ufw
  
  # Autoriser SSH
  sudo ufw allow 22/tcp
  # ou si port changé : sudo ufw allow 2222/tcp
  
  # Bloquer tout le reste par défaut
  sudo ufw default deny incoming
  sudo ufw default allow outgoing
  
  # Activer
  sudo ufw enable
  
  # Vérifier
  sudo ufw status
  ```

- [ ] **Ne PAS ouvrir le port 4002 (API IBKR)**
  - Le bot se connecte en local (127.0.0.1)
  - Aucune raison d'ouvrir ce port publiquement

### 4. Mises à jour système

- [ ] **Activer mises à jour automatiques**
  ```bash
  sudo apt install unattended-upgrades
  sudo dpkg-reconfigure -plow unattended-upgrades
  ```

- [ ] **Vérifier régulièrement**
  ```bash
  sudo apt update
  sudo apt upgrade
  ```

### 5. Monitoring et alertes

- [ ] **Activer fail2ban (protection brute force)**
  ```bash
  sudo apt install fail2ban
  sudo systemctl enable fail2ban
  sudo systemctl start fail2ban
  ```

- [ ] **Surveiller les logs système**
  ```bash
  # Connexions SSH suspectes
  sudo tail -f /var/log/auth.log
  ```

- [ ] **Configurer alertes disque plein**
  ```bash
  df -h  # Vérifier espace disque régulièrement
  ```

### 6. Sauvegarde

- [ ] **Sauvegarder trades_log.csv régulièrement**
  ```bash
  # Via sync_logs.py (déjà configuré)
  python3 sync_logs.py --backup
  git push
  ```

- [ ] **Snapshot Hetzner (optionnel)**
  - Console Hetzner → Créer snapshot du serveur
  - Permet restauration complète en cas de problème
  - Coût : ~0.01€/Go/mois

---

## 🚨 En cas de compromission

### Symptômes d'un serveur compromis
- Processus inconnus : `ps aux | less`
- Utilisation CPU/RAM anormale : `top` ou `htop`
- Trafic réseau suspect : `nethogs`
- Fichiers modifiés : `sudo find / -mtime -1 -type f`

### Actions immédiates
1. **Arrêter le bot**
   ```bash
   ./scripts/stop.sh
   ./scripts/stop_ibgateway.sh
   ```

2. **Changer vos mots de passe**
   - IBKR → Nouveau mot de passe immédiatement
   - Telegram → Révoquer token et créer nouveau bot
   - Serveur → Changer mot de passe utilisateur

3. **Analyser les logs**
   ```bash
   sudo tail -100 /var/log/auth.log
   sudo tail -100 /var/log/syslog
   cat ~/labase-trading-alerts/logs/bot.log
   ```

4. **Si doute, détruire et recréer**
   - Détruire le serveur Hetzner
   - Créer nouveau serveur
   - Redéployer depuis zéro

---

## 🔐 Bonnes pratiques opérationnelles

### Accès au serveur
- ✅ Toujours utiliser SSH avec clé
- ✅ Limiter les connexions à votre IP si possible
- ✅ Utiliser un VPN si connexion depuis réseau public
- ❌ Ne jamais partager vos identifiants

### Configuration IBKR
- ✅ Paper trading uniquement au début
- ✅ Limiter les montants (RISK_EUR dans code)
- ✅ Vérifier les trades quotidiennement
- ✅ Activer alertes email IBKR pour chaque trade
- ❌ Ne pas désactiver Read-Only API sans comprendre risques

### Configuration Telegram
- ✅ Créer un bot dédié (pas réutiliser)
- ✅ Noter CHAT_ID personnel, pas groupe public
- ✅ Vérifier messages quotidiens (heartbeat 9h)
- ❌ Ne jamais poster TOKEN publiquement

### Surveillance quotidienne
- ✅ Message "BONJOUR" chaque matin à 9h
- ✅ Rapport quotidien à 22h
- ✅ Vérifier l'espace disque chaque semaine
- ✅ Lire les logs si comportement anormal

---

## 📊 Audit de sécurité mensuel

Checklist à faire chaque mois :

```bash
# 1. Mises à jour système
sudo apt update && sudo apt upgrade

# 2. Vérifier utilisateurs système
cat /etc/passwd | grep -v nologin

# 3. Vérifier processus suspects
ps aux | grep -v "trader\|root"

# 4. Vérifier connexions réseau
sudo netstat -tuln

# 5. Vérifier espace disque
df -h

# 6. Vérifier logs SSH
sudo grep "Failed password" /var/log/auth.log | tail -20

# 7. Vérifier fail2ban
sudo fail2ban-client status sshd

# 8. Sauvegarder les données
cd ~/labase-trading-alerts
python3 sync_logs.py --backup
git push
```

---

## 🎯 Niveau de sécurité recommandé

### Minimum (Paper Trading)
- ✅ .env protégé (chmod 600)
- ✅ SSH par clé uniquement
- ✅ UFW activé
- ✅ Port 4002 non exposé publiquement

### Recommandé (Paper + Live)
- ✅ Tout "Minimum" +
- ✅ Fail2ban actif
- ✅ Port SSH changé
- ✅ Mises à jour auto
- ✅ Snapshots réguliers

### Maximum (Production critique)
- ✅ Tout "Recommandé" +
- ✅ VPN pour accès SSH
- ✅ IDS/IPS (ex: OSSEC)
- ✅ Monitoring 24/7 (ex: Netdata)
- ✅ Logs centralisés
- ✅ Backup quotidien automatique

---

## 📞 Ressources

- [Guide sécurité SSH](https://www.ssh.com/academy/ssh/config)
- [UFW Tutorial](https://www.digitalocean.com/community/tutorials/how-to-set-up-a-firewall-with-ufw-on-ubuntu)
- [Fail2ban Guide](https://www.fail2ban.org/wiki/index.php/Main_Page)
- [Hetzner Security](https://docs.hetzner.com/cloud/servers/security/)

---

**Date de création** : 13 février 2026  
**Mise à jour recommandée** : Mensuelle
