# Training

## Build

```bash
docker compose -f training/docker-compose.yaml build 
```

## Download

```bash
docker compose -f training/docker-compose.yaml run --rm download
```

## Train

```bash
docker compose -f training/docker-compose.yaml run --rm train
```

## Evaluation

```bash
docker compose -f training/docker-compose.yaml run --rm eval
```

## Export

```bash
docker compose -f training/docker-compose.yaml run --rm export
```
