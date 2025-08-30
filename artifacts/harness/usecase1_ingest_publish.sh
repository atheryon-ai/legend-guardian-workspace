#!/bin/bash

source $(dirname "$0")/env.sh

PROMPT="ingest fx_options.csv -> CDM.Trade; compile; open PR; publish byNotional service"

curl -X POST \
  -H "Content-Type: application/json" \
  -H "X-API-Key: ${API_KEY}" \
  -d "{\"prompt\": \"${PROMPT}\", \"projectId\": \"${PROJECT_ID}\", \"workspaceId\": \"${WORKSPACE_ID}\"}" \
  ${AGENT_URL}/api/intent > $(dirname "$0")/outputs/usecase1_output.json
