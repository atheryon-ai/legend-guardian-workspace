"""Policy engine for guardrails and compliance."""

import re
from typing import Any, Dict, List

import structlog
import yaml

logger = structlog.get_logger()


class PolicyEngine:
    """Enforces policies and guardrails on agent actions."""
    
    def __init__(self, policy_file: str = None):
        """Initialize policy engine."""
        self.policies = self._load_default_policies()
        
        if policy_file:
            self._load_policies_from_file(policy_file)
    
    def _load_default_policies(self) -> Dict[str, Any]:
        """Load default policies."""
        return {
            "pii_patterns": [
                r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
                r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
                r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",  # Credit card
                r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",  # Phone
            ],
            "naming_rules": {
                "model": r"^[A-Z][a-zA-Z0-9]*$",  # PascalCase
                "service": r"^[a-z][a-zA-Z0-9/]*$",  # camelCase with slashes
                "workspace": r"^[a-z][a-z0-9-]*$",  # kebab-case
            },
            "prohibited_actions": [],
            "require_approval": ["delete", "merge", "publish"],
            "max_entities_per_request": 100,
            "max_review_title_length": 200,
            "allowed_schema_types": ["jsonSchema", "avro", "protobuf"],
        }
    
    def _load_policies_from_file(self, policy_file: str) -> None:
        """Load policies from YAML file."""
        try:
            with open(policy_file, "r") as f:
                custom_policies = yaml.safe_load(f)
                self.policies.update(custom_policies)
        except Exception as e:
            logger.error(f"Failed to load policy file: {e}")
    
    async def validate_plan(
        self,
        steps: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """
        Validate and potentially modify a plan.
        
        Args:
            steps: Planned steps
        
        Returns:
            Validated/modified steps
        """
        validated_steps = []
        
        for step in steps:
            action = step.get("action")
            params = step.get("params", {})
            
            # Check if action is prohibited
            if action in self.policies.get("prohibited_actions", []):
                logger.warning(f"Prohibited action removed from plan: {action}")
                continue
            
            # Check if action requires approval
            if action in self.policies.get("require_approval", []):
                step["requires_approval"] = True
            
            # Validate parameters
            try:
                await self.check_action(action, params)
                validated_steps.append(step)
            except Exception as e:
                logger.warning(f"Step validation failed: {e}")
                step["validation_error"] = str(e)
                validated_steps.append(step)
        
        return validated_steps
    
    async def check_action(
        self,
        action: str,
        params: Dict[str, Any],
    ) -> None:
        """
        Check if an action is allowed with given parameters.
        
        Args:
            action: Action type
            params: Action parameters
        
        Raises:
            ValueError: If action violates policies
        """
        # Check PII in parameters
        self._check_pii(params)
        
        # Check naming conventions
        if action == "create_workspace":
            workspace_id = params.get("workspace_id", "")
            pattern = self.policies["naming_rules"].get("workspace")
            if pattern and not re.match(pattern, workspace_id):
                raise ValueError(f"Workspace ID '{workspace_id}' violates naming policy")
        
        elif action == "create_model":
            model_name = params.get("name", "")
            pattern = self.policies["naming_rules"].get("model")
            if pattern and not re.match(pattern, model_name):
                raise ValueError(f"Model name '{model_name}' violates naming policy")
        
        elif action == "generate_service":
            service_path = params.get("path", "")
            pattern = self.policies["naming_rules"].get("service")
            if pattern and not re.match(pattern, service_path):
                raise ValueError(f"Service path '{service_path}' violates naming policy")
        
        elif action == "open_review":
            title = params.get("title", "")
            max_length = self.policies.get("max_review_title_length", 200)
            if len(title) > max_length:
                raise ValueError(f"Review title exceeds maximum length of {max_length}")
        
        elif action == "upsert_entities":
            entities = params.get("entities", [])
            max_entities = self.policies.get("max_entities_per_request", 100)
            if len(entities) > max_entities:
                raise ValueError(f"Too many entities: {len(entities)} > {max_entities}")
        
        elif action == "transform_schema":
            schema_type = params.get("format", "")
            allowed = self.policies.get("allowed_schema_types", [])
            if schema_type not in allowed:
                raise ValueError(f"Schema type '{schema_type}' not allowed")
    
    def _check_pii(self, data: Any) -> None:
        """
        Check for PII in data.
        
        Args:
            data: Data to check
        
        Raises:
            ValueError: If PII detected
        """
        patterns = self.policies.get("pii_patterns", [])
        
        def check_value(value: Any):
            if isinstance(value, str):
                for pattern in patterns:
                    if re.search(pattern, value):
                        raise ValueError("PII detected in parameters")
            elif isinstance(value, dict):
                for v in value.values():
                    check_value(v)
            elif isinstance(value, list):
                for item in value:
                    check_value(item)
        
        check_value(data)
    
    def redact_pii(self, text: str) -> str:
        """
        Redact PII from text.
        
        Args:
            text: Text to redact
        
        Returns:
            Redacted text
        """
        patterns = self.policies.get("pii_patterns", [])
        
        for pattern in patterns:
            text = re.sub(pattern, "[REDACTED]", text)
        
        return text
    
    def check_compile_result(
        self,
        result: Dict[str, Any],
    ) -> bool:
        """
        Check if compilation result is acceptable.
        
        Args:
            result: Compilation result
        
        Returns:
            True if compilation passed policies
        """
        if result.get("status") != "success":
            return False
        
        # Additional checks could be added here
        # e.g., check for specific warning types
        
        return True
    
    def check_test_result(
        self,
        result: Dict[str, Any],
    ) -> bool:
        """
        Check if test result is acceptable.
        
        Args:
            result: Test result
        
        Returns:
            True if tests passed policies
        """
        if not result.get("passed", False):
            return False
        
        # Could add minimum coverage requirements, etc.
        
        return True
    
    def get_policy_summary(self) -> Dict[str, Any]:
        """
        Get summary of active policies.
        
        Returns:
            Policy summary
        """
        return {
            "pii_detection": bool(self.policies.get("pii_patterns")),
            "naming_rules": list(self.policies.get("naming_rules", {}).keys()),
            "prohibited_actions": self.policies.get("prohibited_actions", []),
            "approval_required": self.policies.get("require_approval", []),
            "limits": {
                "max_entities": self.policies.get("max_entities_per_request"),
                "max_title_length": self.policies.get("max_review_title_length"),
            },
        }
    
    def export_policies(self) -> Dict[str, Any]:
        """
        Export current policies.
        
        Returns:
            Current policy configuration
        """
        return self.policies.copy()
    
    def update_policy(self, key: str, value: Any) -> None:
        """
        Update a specific policy.
        
        Args:
            key: Policy key
            value: New policy value
        """
        self.policies[key] = value
        logger.info(f"Policy updated: {key}")