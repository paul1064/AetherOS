# AetherOS Deployment Checklist

## Before install

- Confirm target machine is Ubuntu 24.04 or Debian 12 based
- Confirm user account exists and has sudo access
- Confirm enough disk space for models and reports
- Confirm internet is available if models or packages must be pulled

## Install sequence

```bash
sudo bash install.sh
sudo bin/aether-up
```

## Required checks

```bash
bin/aether version
bin/aether verify
bin/aether report
curl http://127.0.0.1:8011/healthz
curl http://127.0.0.1:8011/release/manifest
```

## Optional desktop checks

```bash
sudo bash install/install-desktop-session.sh
bin/aether operator
```

## Recovery sequence

```bash
sudo bin/aether recover
```
