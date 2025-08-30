"""LLM client for natural language processing."""

import json
import os
from typing import Any, Dict, List, Optional
from enum import Enum

import structlog

logger = structlog.get_logger()


class LLMProvider(Enum):
    """Supported LLM providers."""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"  # For local/open-source models


class LLMClient:
    """Unified LLM client supporting multiple providers."""
    
    def __init__(self, provider: str = "openai", model: Optional[str] = None):
        """
        Initialize LLM client.
        
        Args:
            provider: LLM provider to use
            model: Model name (provider-specific)
        """
        self.provider = LLMProvider(provider.lower())
        self.model = model
        self.client = None
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the appropriate LLM client."""
        if self.provider == LLMProvider.OPENAI:
            try:
                import openai
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.client = openai.OpenAI(api_key=api_key)
                    self.model = self.model or "gpt-4-turbo-preview"
                    logger.info("OpenAI client initialized", model=self.model)
                else:
                    logger.warning("OpenAI API key not found")
            except ImportError:
                logger.warning("OpenAI package not installed")
                
        elif self.provider == LLMProvider.ANTHROPIC:
            try:
                import anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if api_key:
                    self.client = anthropic.Anthropic(api_key=api_key)
                    self.model = self.model or "claude-3-opus-20240229"
                    logger.info("Anthropic client initialized", model=self.model)
                else:
                    logger.warning("Anthropic API key not found")
            except ImportError:
                logger.warning("Anthropic package not installed")
                
        elif self.provider == LLMProvider.OLLAMA:
            try:
                import ollama
                self.client = ollama
                self.model = self.model or "llama2"
                logger.info("Ollama client initialized", model=self.model)
            except ImportError:
                logger.warning("Ollama package not installed")
    
    async def parse_intent(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[Dict[str, Any]]:
        """
        Parse natural language intent into structured actions.
        
        Args:
            prompt: Natural language prompt
            context: Optional context
        
        Returns:
            List of structured action steps
        """
        if not self.client:
            # Fallback to rule-based parsing if no LLM available
            return self._rule_based_parsing(prompt)
        
        system_prompt = self._get_system_prompt()
        user_prompt = self._format_user_prompt(prompt, context)
        
        try:
            if self.provider == LLMProvider.OPENAI:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    temperature=0.3,
                    response_format={"type": "json_object"}
                )
                content = response.choices[0].message.content
                
            elif self.provider == LLMProvider.ANTHROPIC:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    temperature=0.3,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": user_prompt}
                    ]
                )
                content = response.content[0].text
                
            elif self.provider == LLMProvider.OLLAMA:
                response = self.client.chat(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ]
                )
                content = response['message']['content']
            
            # Parse JSON response
            try:
                result = json.loads(content)
                return result.get("steps", [])
            except json.JSONDecodeError:
                logger.error("Failed to parse LLM response as JSON", response=content)
                return self._rule_based_parsing(prompt)
                
        except Exception as e:
            logger.error(f"LLM request failed: {e}")
            return self._rule_based_parsing(prompt)
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for intent parsing."""
        return """You are a Legend Platform orchestration agent. Parse user intents into structured action steps.

Available actions:
- create_workspace: Create a new SDLC workspace
- create_model: Create a PURE model/class
- create_mapping: Create a mapping between model and data
- compile: Compile PURE code
- generate_service: Generate REST API service
- open_review: Open a PR/review
- search_depot: Search model depot
- import_model: Import model from depot
- transform_schema: Transform to Avro/Protobuf/JSON Schema
- run_tests: Run test suite
- publish: Publish to depot

Respond with JSON containing a "steps" array. Each step should have:
- action: The action name from above
- params: Object with action parameters

Example response:
{
  "steps": [
    {"action": "create_model", "params": {"name": "Trade", "fields": ["id", "ticker", "quantity"]}},
    {"action": "compile", "params": {}},
    {"action": "generate_service", "params": {"path": "trades/all"}}
  ]
}"""
    
    def _format_user_prompt(
        self,
        prompt: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Format user prompt with context."""
        formatted = f"User request: {prompt}"
        
        if context:
            formatted += f"\n\nContext:\n"
            if "project_id" in context:
                formatted += f"- Project: {context['project_id']}\n"
            if "workspace_id" in context:
                formatted += f"- Workspace: {context['workspace_id']}\n"
        
        formatted += "\n\nGenerate the steps as JSON."
        return formatted
    
    def _rule_based_parsing(self, prompt: str) -> List[Dict[str, Any]]:
        """Fallback rule-based parsing when LLM is not available."""
        steps = []
        prompt_lower = prompt.lower()
        
        # Model creation
        if "create" in prompt_lower and ("model" in prompt_lower or "class" in prompt_lower):
            model_name = "Model"
            if "trade" in prompt_lower:
                model_name = "Trade"
            elif "position" in prompt_lower:
                model_name = "Position"
            elif "option" in prompt_lower:
                model_name = "Option"
            
            steps.append({
                "action": "create_model",
                "params": {"name": model_name}
            })
        
        # Compilation
        if "compile" in prompt_lower:
            steps.append({
                "action": "compile",
                "params": {}
            })
        
        # Service generation
        if ("generate" in prompt_lower or "create" in prompt_lower) and "service" in prompt_lower:
            path = "service/generated"
            if "trade" in prompt_lower:
                path = "trades/all"
            elif "position" in prompt_lower:
                path = "positions/all"
            
            steps.append({
                "action": "generate_service",
                "params": {"path": path}
            })
        
        # Review/PR
        if "open" in prompt_lower and ("review" in prompt_lower or "pr" in prompt_lower):
            steps.append({
                "action": "open_review",
                "params": {"title": "Changes from Legend Guardian Agent"}
            })
        
        # Depot search
        if "search" in prompt_lower and "depot" in prompt_lower:
            query = "Model"
            if "trade" in prompt_lower:
                query = "Trade"
            elif "fx" in prompt_lower:
                query = "FX"
            
            steps.append({
                "action": "search_depot",
                "params": {"query": query}
            })
        
        # Import from depot
        if "import" in prompt_lower:
            steps.append({
                "action": "import_model",
                "params": {}
            })
        
        # Schema transformation
        if "transform" in prompt_lower or "avro" in prompt_lower or "protobuf" in prompt_lower:
            format_type = "jsonSchema"
            if "avro" in prompt_lower:
                format_type = "avro"
            elif "protobuf" in prompt_lower:
                format_type = "protobuf"
            
            steps.append({
                "action": "transform_schema",
                "params": {"format": format_type}
            })
        
        # Testing
        if "test" in prompt_lower or "validate" in prompt_lower:
            steps.append({
                "action": "run_tests",
                "params": {}
            })
        
        # Publishing
        if "publish" in prompt_lower:
            steps.append({
                "action": "publish",
                "params": {}
            })
        
        return steps
    
    async def enhance_schema(
        self,
        table_name: str,
        raw_schema: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Optional[Dict[str, Any]]:
        """
        Enhance database schema with intelligent type inference.
        
        Args:
            table_name: Name of the database table
            raw_schema: Raw schema information
            context: Optional context
        
        Returns:
            Enhanced schema with better type information
        """
        if not self.client:
            return None
        
        prompt = f"""
        Enhance this database table schema with better type information and constraints.
        
        Table: {table_name}
        Current Schema:
        {json.dumps(raw_schema, indent=2)}
        
        For each column, suggest:
        1. More specific PURE type mappings
        2. Appropriate constraints
        3. Business logic validations
        
        Return enhanced schema as JSON.
        """
        
        try:
            if self.provider == LLMProvider.OPENAI:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a database schema expert."},
                        {"role": "user", "content": prompt},
                    ],
                    response_format={"type": "json_object"},
                    temperature=0.3,
                )
                
                enhanced = json.loads(response.choices[0].message.content)
                
                # Merge enhancements with original schema
                if "columns" in enhanced:
                    raw_schema["columns"] = enhanced["columns"]
                if "constraints" in enhanced:
                    raw_schema["constraints"] = enhanced["constraints"]
                
                return raw_schema
                
            elif self.provider == LLMProvider.ANTHROPIC:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    temperature=0.3,
                    system="You are a database schema expert. Enhance schemas with type information.",
                    messages=[{"role": "user", "content": prompt}],
                )
                
                # Parse Anthropic response
                enhanced = json.loads(response.content[0].text)
                
                # Merge enhancements
                if "columns" in enhanced:
                    raw_schema["columns"] = enhanced["columns"]
                if "constraints" in enhanced:
                    raw_schema["constraints"] = enhanced["constraints"]
                
                return raw_schema
                
            else:
                # Ollama or unsupported
                return raw_schema
                
        except Exception as e:
            logger.error(f"Schema enhancement failed: {e}")
            return raw_schema
    
    async def generate_pure_code(
        self,
        description: str,
        model_name: str,
        fields: List[Dict[str, str]],
    ) -> str:
        """
        Generate PURE code from description.
        
        Args:
            description: Model description
            model_name: Name of the model
            fields: List of field definitions
        
        Returns:
            Generated PURE code
        """
        if not self.client:
            # Simple template-based generation
            return self._template_based_generation(model_name, fields)
        
        prompt = f"""Generate PURE code for a Legend model.

Model: {model_name}
Description: {description}
Fields: {json.dumps(fields, indent=2)}

Generate valid PURE class definition with proper types and multiplicities.
Include any relevant constraints or derived properties based on the description."""
        
        try:
            if self.provider == LLMProvider.OPENAI:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a PURE code generation expert."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.2
                )
                return response.choices[0].message.content
                
            elif self.provider == LLMProvider.ANTHROPIC:
                response = self.client.messages.create(
                    model=self.model,
                    max_tokens=2000,
                    temperature=0.2,
                    messages=[
                        {"role": "user", "content": prompt}
                    ]
                )
                return response.content[0].text
                
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            return self._template_based_generation(model_name, fields)
    
    def _template_based_generation(
        self,
        model_name: str,
        fields: List[Dict[str, str]],
    ) -> str:
        """Template-based PURE code generation."""
        field_lines = []
        for field in fields:
            name = field.get("name", "field")
            type_str = field.get("type", "String")
            multiplicity = field.get("multiplicity", "[1]")
            field_lines.append(f"  {name}: {type_str}{multiplicity};")
        
        return f"""Class model::{model_name}
{{
{chr(10).join(field_lines)}
}}"""