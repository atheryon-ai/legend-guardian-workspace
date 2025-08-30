#!/bin/bash

# Use Case 6: Contract-first API
# This script generates API implementation from schema specifications

set -e

# Source environment
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
source "$SCRIPT_DIR/env.sh"

log_info "=========================================="
log_info "Use Case 6: Contract-first API Generation"
log_info "=========================================="

# Check services
check_all_services || exit 1

# Test 1: Basic JSON Schema to API
log_info "Test 1: Generating API from basic JSON schema..."
REQUEST_BODY='{
  "schema": {
    "type": "object",
    "properties": {
      "id": {"type": "string", "format": "uuid"},
      "name": {"type": "string", "minLength": 1, "maxLength": 100},
      "value": {"type": "number", "minimum": 0},
      "status": {"type": "string", "enum": ["active", "inactive", "pending"]},
      "created_at": {"type": "string", "format": "date-time"}
    },
    "required": ["id", "name", "value", "status"]
  },
  "service_path": "contracts/entity",
  "generate_tests": true
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase6/contract-first" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase6_basic_schema" "$RESPONSE"

# Verify response
if echo "$RESPONSE" | jq -e '.use_case == "contract_first"' > /dev/null; then
    log_info "✓ Basic API generation completed"
else
    log_error "✗ Basic API generation failed"
    exit 1
fi

# Test 2: OpenAPI Specification Import
log_info "Test 2: Generating API from OpenAPI specification..."
REQUEST_BODY='{
  "openapi_spec": {
    "openapi": "3.0.0",
    "info": {
      "title": "Trading API",
      "version": "1.0.0"
    },
    "paths": {
      "/trades": {
        "get": {
          "summary": "List trades",
          "responses": {
            "200": {
              "description": "Successful response",
              "content": {
                "application/json": {
                  "schema": {
                    "type": "array",
                    "items": {
                      "$ref": "#/components/schemas/Trade"
                    }
                  }
                }
              }
            }
          }
        },
        "post": {
          "summary": "Create trade",
          "requestBody": {
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/Trade"
                }
              }
            }
          }
        }
      }
    },
    "components": {
      "schemas": {
        "Trade": {
          "type": "object",
          "properties": {
            "id": {"type": "string"},
            "ticker": {"type": "string"},
            "quantity": {"type": "integer"},
            "price": {"type": "number"}
          }
        }
      }
    }
  },
  "service_path": "contracts/trading",
  "generate_tests": true,
  "generate_mocks": true
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase6/contract-first" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase6_openapi" "$RESPONSE"

# Test 3: Avro Schema Import
log_info "Test 3: Generating API from Avro schema..."
REQUEST_BODY='{
  "avro_schema": {
    "type": "record",
    "name": "Position",
    "namespace": "com.example.trading",
    "fields": [
      {"name": "account_id", "type": "string"},
      {"name": "ticker", "type": "string"},
      {"name": "quantity", "type": "long"},
      {"name": "average_price", "type": "double"},
      {"name": "market_value", "type": ["null", "double"], "default": null},
      {"name": "last_updated", "type": "long", "logicalType": "timestamp-millis"}
    ]
  },
  "service_path": "contracts/positions",
  "generate_tests": true,
  "generate_validation": true
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase6/contract-first" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase6_avro" "$RESPONSE"

# Test 4: GraphQL Schema Import
log_info "Test 4: Generating API from GraphQL schema..."
REQUEST_BODY='{
  "graphql_schema": "
    type Query {
      portfolio(id: ID!): Portfolio
      portfolios(limit: Int = 10): [Portfolio!]!
    }
    
    type Portfolio {
      id: ID!
      name: String!
      positions: [Position!]!
      totalValue: Float!
      createdAt: String!
    }
    
    type Position {
      ticker: String!
      quantity: Int!
      value: Float!
    }
    
    type Mutation {
      createPortfolio(input: PortfolioInput!): Portfolio!
      addPosition(portfolioId: ID!, position: PositionInput!): Position!
    }
    
    input PortfolioInput {
      name: String!
    }
    
    input PositionInput {
      ticker: String!
      quantity: Int!
    }
  ",
  "service_path": "contracts/graphql/portfolio",
  "generate_tests": true,
  "generate_resolvers": true
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase6/contract-first" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase6_graphql" "$RESPONSE"

# Test 5: Protocol Buffers Import
log_info "Test 5: Generating API from Protocol Buffers..."
REQUEST_BODY='{
  "protobuf_schema": "
    syntax = \"proto3\";
    
    package trading.v1;
    
    message Order {
      string id = 1;
      string ticker = 2;
      OrderType type = 3;
      int32 quantity = 4;
      double price = 5;
      int64 timestamp = 6;
    }
    
    enum OrderType {
      MARKET = 0;
      LIMIT = 1;
      STOP = 2;
      STOP_LIMIT = 3;
    }
    
    service OrderService {
      rpc CreateOrder(Order) returns (Order);
      rpc GetOrder(GetOrderRequest) returns (Order);
      rpc ListOrders(ListOrdersRequest) returns (ListOrdersResponse);
    }
    
    message GetOrderRequest {
      string id = 1;
    }
    
    message ListOrdersRequest {
      int32 limit = 1;
      string cursor = 2;
    }
    
    message ListOrdersResponse {
      repeated Order orders = 1;
      string next_cursor = 2;
    }
  ",
  "service_path": "contracts/grpc/orders",
  "generate_tests": true,
  "generate_stubs": true
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase6/contract-first" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase6_protobuf" "$RESPONSE"

# Test 6: Generate with Validation Rules
log_info "Test 6: Generating API with complex validation rules..."
REQUEST_BODY='{
  "schema": {
    "type": "object",
    "properties": {
      "trade_id": {
        "type": "string",
        "pattern": "^[A-Z]{2}[0-9]{8}$"
      },
      "ticker": {
        "type": "string",
        "pattern": "^[A-Z]{1,5}$"
      },
      "quantity": {
        "type": "integer",
        "minimum": 1,
        "maximum": 1000000,
        "multipleOf": 100
      },
      "price": {
        "type": "number",
        "minimum": 0.01,
        "maximum": 999999.99,
        "multipleOf": 0.01
      },
      "trade_date": {
        "type": "string",
        "format": "date"
      },
      "settlement_date": {
        "type": "string",
        "format": "date"
      }
    },
    "required": ["trade_id", "ticker", "quantity", "price", "trade_date"],
    "additionalProperties": false
  },
  "service_path": "contracts/validated/trades",
  "generate_tests": true,
  "validation_rules": {
    "custom": [
      "settlement_date must be >= trade_date",
      "quantity * price must be <= 10000000"
    ]
  }
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase6/contract-first" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase6_validation" "$RESPONSE"

# Test 7: Generate with Test Coverage
log_info "Test 7: Generating comprehensive test suite..."
REQUEST_BODY='{
  "schema": {
    "type": "object",
    "properties": {
      "id": {"type": "string"},
      "amount": {"type": "number"},
      "currency": {"type": "string", "enum": ["USD", "EUR", "GBP"]}
    }
  },
  "service_path": "contracts/tested/payments",
  "generate_tests": true,
  "test_options": {
    "positive_cases": 10,
    "negative_cases": 5,
    "edge_cases": true,
    "property_based": true,
    "coverage_target": 95
  }
}'

RESPONSE=$(make_request POST "$AGENT_URL/flows/usecase6/contract-first" "$REQUEST_BODY")
echo "$RESPONSE" | jq '.'
save_output "usecase6_test_coverage" "$RESPONSE"

# Summary
log_info "=========================================="
log_info "Use Case 6: Contract-first API Tests Complete"
log_info "=========================================="
log_info "Results saved in: $OUTPUT_DIR"

# Extract summary statistics
MODELS_CREATED=$(echo "$RESPONSE" | jq '[.results[] | select(.action == "schema_to_model")] | length')
TESTS_GENERATED=$(echo "$RESPONSE" | jq '[.results[] | select(.action | contains("test"))] | map(.result.tests // 0) | add // 0')
SERVICES_PUBLISHED=$(echo "$RESPONSE" | jq '[.results[] | select(.action == "publish_service")] | length')

log_info "Contract-first Generation Summary:"
log_info "  Models created: $MODELS_CREATED"
log_info "  Tests generated: $TESTS_GENERATED"
log_info "  Services published: $SERVICES_PUBLISHED"

if [ "$SERVICES_PUBLISHED" -gt 0 ]; then
    log_info "✓ Contract-first API generation successful!"
    exit 0
else
    log_error "✗ No services were published"
    exit 1
fi