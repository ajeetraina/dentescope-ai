#!/bin/bash

# Run script for dental width predictor

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  --with-model    Include the model service"
    echo "  --detached      Run in detached mode"
    echo "  --help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                    # Run main app only"
    echo "  $0 --with-model       # Run with model service"
    echo "  $0 --detached         # Run in background"
}

# Parse command line arguments
WITH_MODEL=false
DETACHED=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --with-model)
            WITH_MODEL=true
            shift
            ;;
        --detached)
            DETACHED=true
            shift
            ;;
        --help)
            show_usage
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Build compose command
COMPOSE_CMD="docker-compose"

if [ "$WITH_MODEL" = true ]; then
    COMPOSE_CMD="$COMPOSE_CMD --profile with-model"
fi

COMPOSE_CMD="$COMPOSE_CMD up"

if [ "$DETACHED" = true ]; then
    COMPOSE_CMD="$COMPOSE_CMD -d"
fi

echo "Starting dental width predictor..."
echo "Command: $COMPOSE_CMD"
echo ""

# Execute the command
eval $COMPOSE_CMD

if [ "$DETACHED" = true ]; then
    echo ""
    echo "Application started in background!"
    echo "Access at: http://localhost:3000"
    echo ""
    echo "To view logs: docker-compose logs -f"
    echo "To stop: docker-compose down"
fi