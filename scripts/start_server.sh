#!/usr/bin/env bash
# ==============================================================================
# OpsPulse MLOps — LAN Dev Server One-Click Startup Script (Ubuntu 24.04)
# ==============================================================================
# Usage:
#   ./scripts/start_server.sh           # Ensure SSH/Docker + start Compose stack + verify health
#   ./scripts/start_server.sh --build   # Rebuild images before starting containers
#   ./scripts/start_server.sh --status  # Show current service, container, and endpoint status
#   ./scripts/start_server.sh --stop    # Stop Docker Compose containers
# ==============================================================================

set -euo pipefail

SCRIPT_PATH="$(readlink -f "${BASH_SOURCE[0]}")"
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

MODE="start"
BUILD_FLAG=""

while [[ $# -gt 0 ]]; do
  case "$1" in
    --build)
      BUILD_FLAG="--build"
      shift
      ;;
    --status)
      MODE="status"
      shift
      ;;
    --stop)
      MODE="stop"
      shift
      ;;
    -h|--help)
      sed -n '2,11p' "$SCRIPT_PATH" | sed 's/^# \{0,1\}//'
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      echo "Run '$0 --help' for usage." >&2
      exit 1
      ;;
  esac
done

cd "$PROJECT_ROOT"

info()  { printf '\033[1;34m[INFO]\033[0m %s\n' "$*"; }
ok()    { printf '\033[1;32m[OK]\033[0m   %s\n' "$*"; }
warn()  { printf '\033[1;33m[WARN]\033[0m %s\n' "$*"; }
err()   { printf '\033[1;31m[ERR]\033[0m  %s\n' "$*" >&2; }

# Determine how to invoke docker cleanly even in shells where `newgrp docker` wasn't run yet.
DOCKER_MODE=""
detect_docker_mode() {
  if docker info >/dev/null 2>&1; then
    DOCKER_MODE="direct"
  elif getent group docker 2>/dev/null | grep -qw "${USER:-$(id -un)}" && command -v sg >/dev/null 2>&1; then
    if sg docker -c "docker info >/dev/null 2>&1"; then
      DOCKER_MODE="sg"
    else
      DOCKER_MODE="sudo"
    fi
  else
    DOCKER_MODE="sudo"
  fi
}

run_docker() {
  if [[ -z "$DOCKER_MODE" ]]; then
    detect_docker_mode
  fi
  case "$DOCKER_MODE" in
    direct)
      docker "$@"
      ;;
    sg)
      local cmd
      cmd="$(printf '%q ' docker "$@")"
      sg docker -c "$cmd"
      ;;
    sudo)
      sudo docker "$@"
      ;;
  esac
}

ensure_systemd_service() {
  local svc="$1"
  if systemctl is-active --quiet "$svc"; then
    ok "systemd service '$svc' is active"
  else
    info "Starting systemd service '$svc'..."
    sudo systemctl start "$svc"
    ok "systemd service '$svc' started"
  fi

  if ! systemctl is-enabled --quiet "$svc" 2>/dev/null; then
    warn "systemd service '$svc' is not enabled on boot; enabling it now..."
    sudo systemctl enable "$svc"
  fi
}

wait_for_docker() {
  local retries=15
  local i
  for ((i = 1; i <= retries; i++)); do
    DOCKER_MODE=""
    if docker info >/dev/null 2>&1 || (
      getent group docker 2>/dev/null | grep -qw "${USER:-$(id -un)}" &&
      command -v sg >/dev/null 2>&1 &&
      sg docker -c "docker info >/dev/null 2>&1"
    ); then
      detect_docker_mode
      return 0
    fi
    sleep 1
  done
  # Final fallback check with sudo
  if sudo docker info >/dev/null 2>&1; then
    DOCKER_MODE="sudo"
    return 0
  fi
  err "Docker daemon did not become ready in time."
  exit 1
}

http_ok() {
  local url="$1"
  if command -v curl >/dev/null 2>&1; then
    curl -fsS --max-time 2 "$url" >/dev/null 2>&1
  else
    python3 -c "import urllib.request; urllib.request.urlopen('$url', timeout=2)" >/dev/null 2>&1
  fi
}

wait_for_url() {
  local name="$1"
  local url="$2"
  local timeout_sec="${3:-60}"
  local elapsed=0

  while ((elapsed < timeout_sec)); do
    if http_ok "$url"; then
      ok "$name ready ($url)"
      return 0
    fi
    sleep 2
    elapsed=$((elapsed + 2))
  done

  err "$name failed to respond within ${timeout_sec}s ($url)"
  return 1
}

get_lan_ip() {
  local ip
  ip="$(ip -4 route get 1.1.1.1 2>/dev/null | awk '{for(i=1;i<=NF;i++) if($i=="src") {print $(i+1); exit}}')"
  if [[ -z "$ip" ]]; then
    ip="$(hostname -I 2>/dev/null | awk '{print $1}')"
  fi
  echo "${ip:-127.0.0.1}"
}

print_summary() {
  local lan_ip
  lan_ip="$(get_lan_ip)"

  echo
  echo "=================================================================="
  echo " OpsPulse LAN Dev Server Status"
  echo "=================================================================="
  echo " Project Dir : $PROJECT_ROOT"
  echo " Host LAN IP : $lan_ip"
  echo " SSH Service : $(systemctl is-active ssh 2>/dev/null || echo unknown)"
  echo " Docker      : $(systemctl is-active docker 2>/dev/null || echo unknown) (mode: ${DOCKER_MODE:-unknown})"
  if [[ "$lan_ip" != "192.168.0.253" ]]; then
    warn "Current LAN IP ($lan_ip) differs from documented 192.168.0.253; update Mac ~/.ssh/config or router DHCP reservation."
  fi
  echo "------------------------------------------------------------------"
  run_docker compose ps
  echo "------------------------------------------------------------------"
  echo " SSH Access:"
  echo "   ssh jintao@${lan_ip}"
  echo "   ssh partner@${lan_ip}"
  echo
  echo " Web / API Endpoints:"
  echo "   Target App Docs   : http://${lan_ip}:8001/docs"
  echo "   Inference API Docs: http://${lan_ip}:8002/docs"
  echo "   Prometheus        : http://${lan_ip}:9090"
  if http_ok "http://127.0.0.1:5000"; then
    echo "   MLflow UI         : http://${lan_ip}:5000"
  fi
  if http_ok "http://127.0.0.1:9001"; then
    echo "   MinIO Console     : http://${lan_ip}:9001"
  fi
  if http_ok "http://127.0.0.1:3000/api/health"; then
    echo "   Grafana           : http://${lan_ip}:3000"
  fi
  echo "=================================================================="
}

if [[ "$MODE" == "stop" ]]; then
  info "Stopping OpsPulse Docker Compose stack..."
  wait_for_docker
  run_docker compose down
  ok "Docker Compose stack stopped (SSH & Docker daemon left running)."
  exit 0
fi

if [[ "$MODE" == "status" ]]; then
  wait_for_docker
  print_summary
  exit 0
fi

info "Bootstrapping OpsPulse LAN Dev Server from: $PROJECT_ROOT"
ensure_systemd_service ssh
ensure_systemd_service docker
wait_for_docker

if [[ ! -f .env && -f .env.example ]]; then
  info "Creating .env from .env.example..."
  cp .env.example .env
  ok ".env created"
fi

info "Starting Docker Compose stack..."
if [[ -n "$BUILD_FLAG" ]]; then
  run_docker compose up -d --build
else
  run_docker compose up -d
fi

info "Verifying service health..."
wait_for_url "target-app" "http://127.0.0.1:8001/health" 60
wait_for_url "inference-api" "http://127.0.0.1:8002/health" 60
wait_for_url "prometheus" "http://127.0.0.1:9090/-/ready" 60

print_summary
