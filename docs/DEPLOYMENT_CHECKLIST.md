# AetherOS Deployment Checklist

## Before install

- Confirm target machine is Ubuntu 24.04 or Debian 12 based
- Confirm user account exists and has sudo access
- Confirm enough disk space for models and reports
- Confirm internet is available if models or packages must be pulled

## Install sequence

```bash
sudo bash /home/miqua/Desktop/pcfAI/install.sh
sudo /home/miqua/Desktop/pcfAI/bin/aether-up
```

## Required checks

```bash
/home/miqua/Desktop/pcfAI/bin/aether version
/home/miqua/Desktop/pcfAI/bin/aether verify
/home/miqua/Desktop/pcfAI/bin/aether report
curl http://127.0.0.1:8011/healthz
curl http://127.0.0.1:8011/release/manifest
```

## Optional desktop checks

```bash
sudo bash /home/miqua/Desktop/pcfAI/install/install-desktop-session.sh
/home/miqua/Desktop/pcfAI/bin/aether operator
```

## Recovery sequence

```bash
sudo /home/miqua/Desktop/pcfAI/bin/aether recover
```
