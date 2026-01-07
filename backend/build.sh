#!/bin/bash
# BetterHeap Backend - Build & Deploy
# 
# Usage: ./build.sh <command> [env]
#
# Commands:
#   local               - Build locally
#   deploy <dev|prod>   - Deploy to Cloud Run

set -e

# --- Configuration ---
PROJECT_ID="seventh-history-394808"
REGION="europe-west3"
REGISTRY="europe-west3-docker.pkg.dev"
REPOSITORY="betterheap"

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }
log_step() { echo -e "${BLUE}[STEP]${NC} $1"; }

# --- Environment Setup ---
setup_env() {
    ENV=$1
    if [[ "$ENV" != "dev" && "$ENV" != "prod" ]]; then
        log_error "Environment must be 'dev' or 'prod'"
        exit 1
    fi

    if [[ "$ENV" == "prod" ]]; then
        SERVICE_NAME="betterheap-api"
        ENV_FILE=".env.production"
        MIN_INSTANCES=1
        MAX_INSTANCES=10
        MEMORY="1Gi"
        CPU=1
    else
        SERVICE_NAME="betterheap-api-dev"
        ENV_FILE=".env.development"
        MIN_INSTANCES=0
        MAX_INSTANCES=3
        MEMORY="512Mi"
        CPU=1
    fi
}

# --- Build Local ---
build_local() {
    log_step "Building Docker image locally..."
    docker build -t betterheap-api:local .
    log_info "✅ Build complete!"
    log_info "💡 Run: docker run -p 8000:8000 --env-file .env.development betterheap-api:local"
}

# --- Deploy ---
deploy() {
    START=$(date +%s)
    ENV=${1:-"dev"}
    setup_env "$ENV"
    
    log_step "Deploying $SERVICE_NAME ($ENV)..."
    
    # Check env file
    if [[ ! -f "$ENV_FILE" ]]; then
        log_error "Environment file $ENV_FILE not found"
        exit 1
    fi
    
    # Enable services
    gcloud config set project "$PROJECT_ID" --quiet
    gcloud services enable cloudbuild.googleapis.com run.googleapis.com artifactregistry.googleapis.com --quiet
    
    # Build image
    IMAGE="$REGISTRY/$PROJECT_ID/$REPOSITORY/$SERVICE_NAME:latest"
    log_info "Building image: $IMAGE"
    gcloud builds submit --tag "$IMAGE" --project "$PROJECT_ID" --timeout=600 .
    
    # Parse env vars
    ENV_VARS=()
    while IFS= read -r line || [[ -n "$line" ]]; do
        if [[ ! "$line" =~ ^[[:space:]]*# ]] && [[ -n "$line" ]] && [[ "$line" == *"="* ]]; then
            key=$(echo "$line" | cut -d'=' -f1 | xargs)
            value=$(echo "$line" | cut -d'=' -f2- | sed 's/^"//;s/"$//')
            if [[ -n "$key" && -n "$value" ]]; then
                ENV_VARS+=("$key=$value")
            fi
        fi
    done < "$ENV_FILE"
    
    # Deploy
    log_info "Deploying to Cloud Run..."
    gcloud run deploy "$SERVICE_NAME" \
        --image "$IMAGE" \
        --platform managed \
        --region "$REGION" \
        --allow-unauthenticated \
        --memory "$MEMORY" \
        --cpu "$CPU" \
        --min-instances "$MIN_INSTANCES" \
        --max-instances "$MAX_INSTANCES" \
        --timeout 300 \
        --port 8000 \
        --project "$PROJECT_ID" \
        --set-env-vars "$(IFS=,; echo "${ENV_VARS[*]}")"
    
    # Get URL
    URL=$(gcloud run services describe "$SERVICE_NAME" --region="$REGION" --format="value(status.url)" --project="$PROJECT_ID")
    
    ELAPSED=$(($(date +%s) - START))
    log_info "✅ Deployed in ${ELAPSED}s!"
    log_info "🌐 URL: $URL"
}

# --- Main ---
case "${1:-}" in
    local)
        build_local
        ;;
    deploy)
        deploy "$2"
        ;;
    *)
        echo "Usage: $0 <local|deploy> [dev|prod]"
        echo ""
        echo "Examples:"
        echo "  $0 local           # Build locally"
        echo "  $0 deploy dev      # Deploy to dev"
        echo "  $0 deploy prod     # Deploy to prod"
        exit 1
        ;;
esac
