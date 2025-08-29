"""Legend Engine client implementation."""

import json
from typing import Any, Dict, List, Literal, Optional

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential

from src.settings import Settings

logger = structlog.get_logger()


class EngineClient:
    """Client for Legend Engine API."""
    
    def __init__(self, settings: Settings):
        """Initialize Engine client."""
        self.settings = settings
        self.base_url = settings.engine_url
        self.timeout = httpx.Timeout(settings.request_timeout)
        self.headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        
        if settings.engine_token:
            self.headers["Authorization"] = f"Bearer {settings.engine_token}"
    
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10),
    )
    async def _request(
        self,
        method: str,
        path: str,
        json_data: Optional[Dict[str, Any]] = None,
        data: Optional[str] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Make HTTP request to Engine."""
        url = f"{self.base_url}{path}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            headers = self.headers.copy()
            
            if data and not json_data:
                headers["Content-Type"] = "text/plain"
            
            response = await client.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                content=data,
                params=params,
            )
            
            logger.debug(
                "Engine request",
                method=method,
                path=path,
                status=response.status_code,
            )
            
            if response.status_code >= 400:
                error_detail = response.text
                logger.error(
                    "Engine request failed",
                    status=response.status_code,
                    error=error_detail,
                )
                raise Exception(f"Engine API error: {response.status_code} - {error_detail}")
            
            if response.headers.get("content-type", "").startswith("application/json"):
                return response.json()
            else:
                return {"text": response.text}
    
    async def get_info(self) -> Dict[str, Any]:
        """Get Engine server information."""
        return await self._request("GET", "/api/server/v1/info")
    
    async def compile(
        self,
        pure: str,
        project_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Compile PURE code.
        
        Args:
            pure: PURE code to compile
            project_id: Optional project context
            workspace_id: Optional workspace context
        
        Returns:
            Compilation result with status and any errors
        """
        logger.info("Compiling PURE", size=len(pure))
        
        # Prepare compilation request
        request_data = {
            "code": pure,
            "isolatedLambdas": {},
        }
        
        if project_id:
            request_data["projectId"] = project_id
        if workspace_id:
            request_data["workspaceId"] = workspace_id
        
        try:
            result = await self._request(
                "POST",
                "/api/pure/v1/compilation/compile",
                json_data=request_data,
            )
            
            if result.get("status") == "SUCCESS":
                return {"status": "success", "details": result}
            else:
                return {"status": "error", "errors": result.get("errors", [])}
                
        except Exception as e:
            logger.error("Compilation failed", error=str(e))
            return {"status": "error", "errors": [{"message": str(e)}]}
    
    async def generate_execution_plan(
        self,
        mapping: str,
        runtime: str,
        query: str,
    ) -> Dict[str, Any]:
        """
        Generate execution plan for a query.
        
        Args:
            mapping: Mapping path
            runtime: Runtime path
            query: Query to execute
        
        Returns:
            Execution plan
        """
        logger.info(
            "Generating execution plan",
            mapping=mapping,
            runtime=runtime,
        )
        
        request_data = {
            "mapping": mapping,
            "runtime": runtime,
            "query": query,
            "context": {},
        }
        
        return await self._request(
            "POST",
            "/api/pure/v1/execution/generatePlan",
            json_data=request_data,
        )
    
    async def execute_query(
        self,
        query: str,
        mapping: str,
        runtime: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Execute a query.
        
        Args:
            query: Query to execute
            mapping: Mapping path
            runtime: Runtime path
            context: Optional execution context
        
        Returns:
            Query results
        """
        logger.info("Executing query", query=query[:100])
        
        request_data = {
            "query": query,
            "mapping": mapping,
            "runtime": runtime,
            "context": context or {},
        }
        
        return await self._request(
            "POST",
            "/api/pure/v1/execution/execute",
            json_data=request_data,
        )
    
    async def transform_to_schema(
        self,
        schema_type: Literal["jsonSchema", "avro", "protobuf"],
        class_path: str,
        include_dependencies: bool = False,
    ) -> Dict[str, Any]:
        """
        Transform a class to a schema format.
        
        Args:
            schema_type: Target schema format
            class_path: Class path to transform
            include_dependencies: Include dependent classes
        
        Returns:
            Schema in requested format
        """
        logger.info(
            "Transforming to schema",
            schema_type=schema_type,
            class_path=class_path,
        )
        
        endpoint_map = {
            "jsonSchema": "/api/pure/v1/schemaGeneration/jsonSchema",
            "avro": "/api/pure/v1/schemaGeneration/avro",
            "protobuf": "/api/pure/v1/schemaGeneration/protobuf",
        }
        
        request_data = {
            "classPath": class_path,
            "includeDependencies": include_dependencies,
        }
        
        return await self._request(
            "POST",
            endpoint_map[schema_type],
            json_data=request_data,
        )
    
    async def run_service(
        self,
        path: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """
        Run a Legend service.
        
        Args:
            path: Service path
            params: Service parameters
        
        Returns:
            Service execution results
        """
        logger.info("Running service", path=path)
        
        # Services are typically GET endpoints with query params
        return await self._request(
            "GET",
            f"/api/service/{path}",
            params=params,
        )
    
    async def run_tests(
        self,
        test_path: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Run Legend tests.
        
        Args:
            test_path: Optional specific test path
        
        Returns:
            Test results
        """
        logger.info("Running tests", test_path=test_path)
        
        request_data = {}
        if test_path:
            request_data["testPath"] = test_path
        
        result = await self._request(
            "POST",
            "/api/pure/v1/test/run",
            json_data=request_data,
        )
        
        # Parse test results
        tests = result.get("tests", [])
        return [
            {
                "test": test.get("name"),
                "passed": test.get("status") == "PASS",
                "message": test.get("message"),
            }
            for test in tests
        ]
    
    async def generate_service_code(
        self,
        service_path: str,
        target: str = "java",
    ) -> str:
        """
        Generate service implementation code.
        
        Args:
            service_path: Service path
            target: Target language/platform
        
        Returns:
            Generated code
        """
        logger.info(
            "Generating service code",
            service_path=service_path,
            target=target,
        )
        
        request_data = {
            "servicePath": service_path,
            "target": target,
        }
        
        result = await self._request(
            "POST",
            "/api/pure/v1/codeGeneration/generate",
            json_data=request_data,
        )
        
        return result.get("code", "")