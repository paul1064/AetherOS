# AetherOS Runbook

## Install

```bash
sudo bash /home/miqua/Desktop/pcfAI/install.sh
```

## Start / Stop / Recover

```bash
sudo /home/miqua/Desktop/pcfAI/bin/aether up
sudo /home/miqua/Desktop/pcfAI/bin/aether down
sudo /home/miqua/Desktop/pcfAI/bin/aether recover
```

## Health

```bash
/home/miqua/Desktop/pcfAI/bin/aether status
/home/miqua/Desktop/pcfAI/bin/aether verify
/home/miqua/Desktop/pcfAI/bin/aether report
```

## Models

```bash
/home/miqua/Desktop/pcfAI/bin/aether models --list
/home/miqua/Desktop/pcfAI/bin/aether models --refresh
/home/miqua/Desktop/pcfAI/bin/aether models --pull qwen3-coder
```

## Governance

```bash
/home/miqua/Desktop/pcfAI/bin/aether governance --profiles
/home/miqua/Desktop/pcfAI/bin/aether governance --audit
```

## Memory

```bash
/home/miqua/Desktop/pcfAI/bin/aether memory --search "orchestrator"
/home/miqua/Desktop/pcfAI/bin/aether memory --entities
/home/miqua/Desktop/pcfAI/bin/aether memory --graph
```

## Meta jobs

```bash
/home/miqua/Desktop/pcfAI/bin/aether meta --submit --name planner --role analysis --prompt "Summarize system state"
/home/miqua/Desktop/pcfAI/bin/aether meta --list
```

## Operator UI

```bash
/home/miqua/Desktop/pcfAI/bin/aether operator
```
