#!/bin/bash

# Docker Compose wrapper script for FINOS Legend
# This script is referenced in the official README

echo "Starting FINOS Legend deployment with profile: $2"
docker-compose "$@"
