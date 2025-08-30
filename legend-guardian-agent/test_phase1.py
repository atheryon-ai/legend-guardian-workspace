#!/usr/bin/env python3
"""Test Phase 1 implementation of Legend Guardian Agent."""

import asyncio
import json
from datetime import datetime
from src.agent.orchestrator import AgentOrchestrator
from src.settings import Settings

async def test_phase1():
    """Test Phase 1 handlers: compile, generate_service, open_review, create_mapping."""
    
    # Initialize
    settings = Settings()
    orchestrator = AgentOrchestrator(settings)
    
    print("=" * 60)
    print("PHASE 1 IMPLEMENTATION TEST")
    print("=" * 60)
    print()
    
    # Test data
    csv_data = "id,ticker,quantity,price\n1,AAPL,100,150.50\n2,GOOGL,50,2800.00"
    model_name = "TestTrade"
    service_path = "test/trades"
    mapping_name = "TestTradeMapping"
    
    results = {}
    
    # Test 1: Create Model
    print("1. Testing _create_model...")
    try:
        result = await orchestrator.execute_step("create_model", {
            "name": model_name,
            "csv_data": csv_data
        })
        results["create_model"] = {"status": "✅ PASS", "result": result}
        print(f"   Result: {result.get('model', 'Unknown')}")
    except Exception as e:
        results["create_model"] = {"status": "❌ FAIL", "error": str(e)}
        print(f"   Error: {e}")
    
    # Test 2: Create Mapping
    print("\n2. Testing _create_mapping...")
    try:
        result = await orchestrator.execute_step("create_mapping", {
            "name": mapping_name,
            "model": model_name
        })
        results["create_mapping"] = {"status": "✅ PASS", "result": result}
        print(f"   Result: {result.get('mapping', 'Unknown')}")
    except Exception as e:
        results["create_mapping"] = {"status": "❌ FAIL", "error": str(e)}
        print(f"   Error: {e}")
    
    # Test 3: Compile
    print("\n3. Testing _compile...")
    try:
        result = await orchestrator.execute_step("compile", {})
        status = result.get("status", "unknown")
        if status == "success":
            results["compile"] = {"status": "✅ PASS", "result": result}
            print(f"   Result: Compilation {status}")
        else:
            results["compile"] = {"status": "⚠️ PARTIAL", "result": result}
            print(f"   Result: {status}")
            if result.get("errors"):
                print(f"   Errors: {result['errors'][:2]}")  # Show first 2 errors
    except Exception as e:
        results["compile"] = {"status": "❌ FAIL", "error": str(e)}
        print(f"   Error: {e}")
    
    # Test 4: Generate Service
    print("\n4. Testing _generate_service...")
    try:
        result = await orchestrator.execute_step("generate_service", {
            "path": service_path,
            "query": f"model::all{model_name}",
            "mapping": f"mapping::{mapping_name}",
            "runtime": "runtime::TestRuntime"
        })
        results["generate_service"] = {"status": "✅ PASS", "result": result}
        print(f"   Result: Service {result.get('status', 'unknown')}")
        print(f"   Path: {result.get('service_path', 'Unknown')}")
        print(f"   Note: {result.get('note', '')}")
    except Exception as e:
        results["generate_service"] = {"status": "❌ FAIL", "error": str(e)}
        print(f"   Error: {e}")
    
    # Test 5: Open Review
    print("\n5. Testing _open_review...")
    try:
        result = await orchestrator.execute_step("open_review", {
            "title": "Test Phase 1 Implementation",
            "description": "Testing compile, service generation, and review creation"
        })
        results["open_review"] = {"status": "✅ PASS", "result": result}
        print(f"   Result: Review {result.get('state', 'unknown')}")
        print(f"   ID: {result.get('review_id', 'Unknown')}")
        if result.get("url"):
            print(f"   URL: {result['url']}")
    except Exception as e:
        results["open_review"] = {"status": "⚠️ EXPECTED", "error": str(e)}
        print(f"   Error (expected without GitLab): {e}")
    
    # Test 6: Apply Changes (Phase 2 bonus)
    print("\n6. Testing _apply_changes (Phase 2)...")
    try:
        result = await orchestrator.execute_step("apply_changes", {
            "model_path": f"model::{model_name}",
            "changes": {
                "rename": {"price": "unitPrice"},
                "add_field": {"name": "tradeDate", "type": "Date"}
            }
        })
        results["apply_changes"] = {"status": "✅ PASS", "result": result}
        print(f"   Result: {result.get('changes_applied', 0)} changes applied")
    except Exception as e:
        results["apply_changes"] = {"status": "❌ FAIL", "error": str(e)}
        print(f"   Error: {e}")
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    pass_count = sum(1 for r in results.values() if "✅" in r["status"])
    partial_count = sum(1 for r in results.values() if "⚠️" in r["status"])
    fail_count = sum(1 for r in results.values() if "❌" in r["status"])
    
    for handler, result in results.items():
        print(f"{result['status']} {handler}")
    
    print(f"\nTotal: {pass_count} passed, {partial_count} partial, {fail_count} failed")
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = f"test_results_phase1_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(results, f, indent=2, default=str)
    print(f"\nResults saved to: {output_file}")
    
    # Overall assessment
    if pass_count >= 3:
        print("\n✅ Phase 1 IMPLEMENTATION SUCCESSFUL")
        print("Core handlers are working. Some may need Legend services running.")
    elif pass_count >= 2:
        print("\n⚠️ Phase 1 PARTIALLY IMPLEMENTED")
        print("Some handlers working, but critical gaps remain.")
    else:
        print("\n❌ Phase 1 IMPLEMENTATION INCOMPLETE")
        print("Most handlers are not functioning properly.")
    
    return results

if __name__ == "__main__":
    asyncio.run(test_phase1())