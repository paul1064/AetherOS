# AetherOS Runbook

## Install

```bash
sudo bash install.sh
```

## Start / Stop / Recover

```bash
sudo bin/aether up
sudo bin/aether down
sudo bin/aether recover
```

## Health

```bash
bin/aether status
bin/aether verify
bin/aether report
```

## Models

```bash
bin/aether models --list
bin/aether models --refresh
bin/aether models --pull qwen3-coder
```

## Governance

```bash
bin/aether governance --profiles
bin/aether governance --audit
```

## Memory

```bash
bin/aether memory --search "orchestrator"
bin/aether memory --entities
bin/aether memory --graph
```

## Meta jobs

```bash
bin/aether meta --submit --name planner --role analysis --prompt "Summarize system state"
bin/aether meta --list
```

## Operator UI

```bash
bin/aether operator
```
