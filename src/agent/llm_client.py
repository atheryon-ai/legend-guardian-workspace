
from typing import Dict, Any, List

from src.rag.store import vector_store

class LLMClient:
    def __init__(self, provider: str = "openai", model: str = "gpt-4"):
        self.provider = provider
        self.model = model

    async def parse_intent(self, prompt: str) -> Dict[str, Any]:
        """Parses the user intent using the configured LLM provider with RAG."""
        context_docs = await vector_store.query(prompt)
        context = "\n".join([doc["content"] for doc in context_docs])
        
        enriched_prompt = f"Context:\n{context}\n\nPrompt: {prompt}"

        if self.provider == "openai":
            return await self._parse_with_openai(enriched_prompt)
        elif self.provider == "anthropic":
            return await self._parse_with_anthropic(enriched_prompt)
        elif self.provider == "ollama":
            return await self._parse_with_ollama(enriched_prompt)
        else:
            return self._parse_with_rule_based(prompt) # Rule-based doesn't use context

    async def _parse_with_openai(self, prompt: str) -> Dict[str, Any]:
        # Placeholder for OpenAI implementation
        return self._parse_with_rule_based(prompt)

    async def _parse_with_anthropic(self, prompt: str) -> Dict[str, Any]:
        # Placeholder for Anthropic implementation
        return self._parse_with_rule_based(prompt)

    async def _parse_with_ollama(self, prompt: str) -> Dict[str, Any]:
        # Placeholder for Ollama implementation
        return self._parse_with_rule_based(prompt)

    def _parse_with_rule_based(self, prompt: str) -> Dict[str, Any]:
        """Fallback rule-based parser."""
        plan = {"steps": []}
        commands = [cmd.strip() for cmd in prompt.split(";")]

        for command in commands:
            if "ingest" in command:
                parts = command.split("->")
                source = parts[0].replace("ingest", "").strip()
                target = parts[1].strip()
                plan["steps"].append({"action": "sdlc.create_workspace", "params": {}})
                plan["steps"].append({"action": "sdlc.upsert_entities", "params": {"source": source, "target": target}})
            elif "compile" in command:
                plan["steps"].append({"action": "engine.compile", "params": {}})
            elif "review" in command or "PR" in command:
                plan["steps"].append({"action": "sdlc.open_review", "params": {"title": f"Review for {prompt}", "description": command}})
            elif "publish" in command:
                service_name = command.replace("publish", "").strip()
                plan["steps"].append({"action": "engine.run_service", "params": {"path": service_name, "params": {}}})
            else:
                plan["steps"].append({"action": "depot.search", "params": {"query": command}})

        return plan

llm_client = LLMClient()
