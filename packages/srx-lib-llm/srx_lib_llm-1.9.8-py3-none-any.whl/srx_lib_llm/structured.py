from __future__ import annotations

from enum import Enum
from typing import Any, Dict, Optional, Type

from pydantic import BaseModel, Field, create_model
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from .instrumentation import get_langfuse_handler


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class BaseStructuredOutput(BaseModel):
    confidence: ConfidenceLevel = Field(description="Confidence level in the output")
    reasoning: str = Field(description="Brief reasoning for the output")

    class Config:
        use_enum_values = True


def validate_json_schema(schema: Dict[str, Any]) -> bool:
    try:
        if "properties" not in schema:
            raise ValueError("JSON schema must contain 'properties'")
        if not isinstance(schema["properties"], dict):
            raise ValueError("'properties' must be a dictionary")

        valid_types = {"string", "integer", "number", "boolean", "array", "object"}
        for field_name, field_schema in schema["properties"].items():
            if not isinstance(field_schema, dict):
                raise ValueError(f"Property '{field_name}' must be a dictionary")
            if "type" not in field_schema:
                raise ValueError(f"Property '{field_name}' must have a 'type' field")
            if field_schema["type"] not in valid_types:
                raise ValueError(
                    f"Property '{field_name}' has invalid type: {field_schema['type']}"
                )
            if field_schema["type"] == "array" and "items" in field_schema:
                items_schema = field_schema["items"]
                if not isinstance(items_schema, dict):
                    raise ValueError(f"Array items for '{field_name}' must be a dictionary")
                if "type" not in items_schema:
                    raise ValueError(f"Array items for '{field_name}' must have a 'type' field")
        return True
    except Exception:
        return False


def _add_additional_properties(schema: Dict[str, Any]) -> Dict[str, Any]:
    if not isinstance(schema, dict):
        return schema
    s = dict(schema)

    # Convert anyOf to type array for OpenAI compatibility
    # OpenAI doesn't support anyOf, but supports type: ["string", "null"]
    if "anyOf" in s and isinstance(s["anyOf"], list):
        types = []
        for item in s["anyOf"]:
            if isinstance(item, dict) and "type" in item:
                types.append(item["type"])
        if types:
            s["type"] = types
            del s["anyOf"]

    if s.get("type") == "object":
        s["additionalProperties"] = False
    if "properties" in s and isinstance(s["properties"], dict):
        s["properties"] = {k: _add_additional_properties(v) for k, v in s["properties"].items()}
    if "items" in s:
        s["items"] = _add_additional_properties(s["items"])  # type: ignore
    return s


def _resolve_refs(schema: Dict[str, Any], defs: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively resolve all $ref in a JSON schema by inlining definitions.

    OpenAI's strict mode doesn't allow $ref with additional keywords, so we
    need to inline all references.
    """
    if not isinstance(schema, dict):
        return schema

    result = {}
    for key, value in schema.items():
        if key == "$ref":
            # Extract the reference name (e.g., "#/$defs/MyModel" -> "MyModel")
            ref_path = value.split("/")[-1]
            if ref_path in defs:
                # Recursively resolve the referenced schema
                resolved = _resolve_refs(defs[ref_path], defs)
                # Merge the resolved schema (skip the $ref key)
                result.update(resolved)
            else:
                result[key] = value
        elif isinstance(value, dict):
            result[key] = _resolve_refs(value, defs)
        elif isinstance(value, list):
            result[key] = [_resolve_refs(item, defs) if isinstance(item, dict) else item for item in value]
        else:
            result[key] = value

    return result


def preprocess_json_schema(
    json_schema: Dict[str, Any], enforce_all_required: bool = False
) -> Dict[str, Any]:
    s = _add_additional_properties(json_schema)
    if not enforce_all_required:
        return s

    def enforce(schema: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(schema, dict):
            return schema
        x = dict(schema)
        if x.get("type") == "object" and isinstance(x.get("properties"), dict):
            props: Dict[str, Any] = x.get("properties", {})
            original_required = set(x.get("required", []))
            x["required"] = list(props.keys())
            for name, ps in list(props.items()):
                if name not in original_required and isinstance(ps, dict):
                    ps = dict(ps)
                    ps.setdefault("nullable", True)
                    props[name] = ps
                props[name] = enforce(props[name])
        if "items" in x:
            x["items"] = enforce(x["items"])  # type: ignore
        return x

    return enforce(s)


def build_model_from_schema(
    schema_name: str,
    json_schema: Dict[str, Any],
    base: Type[BaseModel] | None = None,
) -> Type[BaseModel]:
    base = base or BaseStructuredOutput

    class StrictBase(base):  # type: ignore
        class Config:
            extra = "forbid"

    def _py_type(t: str):
        return {"string": str, "integer": int, "number": float, "boolean": bool}.get(t, Any)

    def _build(node_name: str, schema: Dict[str, Any]) -> Type[BaseModel]:
        props = schema.get("properties", {}) or {}
        required = set(schema.get("required", []))
        fields: Dict[str, tuple] = {}
        for fname, fs in props.items():
            ftype = fs.get("type")
            ann: Any
            default = ... if fname in required else None
            desc = fs.get("description", f"Field: {fname}")

            if ftype == "object":
                sub = _build(f"{node_name}_{fname.capitalize()}", fs)
                ann = sub if fname in required else Optional[sub]  # type: ignore
            elif ftype == "array":
                items = fs.get("items", {}) or {}
                if items.get("type") == "object":
                    sub = _build(f"{node_name}_{fname.capitalize()}Item", items)
                    ann = list[sub]  # type: ignore
                elif "type" in items:
                    ann = list[_py_type(items["type"])]  # type: ignore
                else:
                    ann = list[Any]
                if fname not in required:
                    from typing import Optional as Opt

                    ann = Opt[ann]  # type: ignore
            else:
                ann = _py_type(ftype)
                if fname not in required:
                    from typing import Optional as Opt

                    ann = Opt[ann]  # type: ignore
            fields[fname] = (ann, Field(default=default, description=desc))

        return create_model(node_name, __base__=StrictBase, **fields)

    payload = _build(f"{schema_name}Payload", json_schema)
    # Inline payload fields on output model so they appear at top-level
    out_fields: Dict[str, tuple] = {}
    for field_name, f in payload.model_fields.items():
        out_fields[field_name] = (
            f.annotation,
            Field(default=(... if f.is_required() else None)),
        )
    return create_model(schema_name, __base__=StrictBase, **out_fields)


def create_dynamic_schema(schema_name: str, json_schema: Dict[str, Any]) -> Type[BaseModel]:
    """Back-compat helper that mirrors existing services' API.

    Builds a strict Pydantic model from the given JSON schema that extends
    BaseStructuredOutput and forbids extra properties.
    """
    pre = preprocess_json_schema(json_schema)
    return build_model_from_schema(schema_name, pre, base=BaseStructuredOutput)


class StructuredOutputGenerator:
    def __init__(self, model: Optional[str] = None, api_key: Optional[str] = None):
        self._langfuse_handler = get_langfuse_handler()
        callbacks = [self._langfuse_handler] if self._langfuse_handler else None
        self._llm = ChatOpenAI(
            model=model or "gpt-4.1-mini",
            temperature=0,
            api_key=api_key,
            use_responses_api=True,
            output_version="responses/v1",
            callbacks=callbacks,
        )

    async def generate_from_model(
        self, prompt: str, schema_model: Type[BaseModel], system: Optional[str] = None
    ) -> BaseModel:
        tmpl = ChatPromptTemplate.from_messages(
            [
                ("system", system or "You output ONLY valid JSON for the given schema."),
                ("human", "{input}"),
            ]
        )
        chain = tmpl | self._llm.with_structured_output(schema_model)
        config = {"callbacks": [self._langfuse_handler]} if self._langfuse_handler else None
        return await chain.ainvoke({"input": prompt}, config=config)

    async def generate_from_json_schema(
        self,
        prompt: str,
        json_schema: Dict[str, Any],
        schema_name: str = "StructuredOutput",
        system: Optional[str] = None,
        enforce_all_required: bool = False,
        base: Type[BaseModel] | None = None,
    ) -> BaseModel:
        pre = preprocess_json_schema(json_schema, enforce_all_required=enforce_all_required)
        model = build_model_from_schema(schema_name, pre, base=base)
        return await self.generate_from_model(prompt, model, system=system)


async def extract_structured_gpt51(
    *,
    text: str,
    json_schema: Dict[str, Any],
    schema_name: str = "DynamicSchema",
    prompt: Optional[str] = None,
    system: Optional[str] = None,
    model: str = "gpt-5.1",
    api_key: Optional[str] = None,
    reasoning_effort: str = "none",
    cache: Optional[Any] = None,
    cache_key: Optional[str] = None,
) -> BaseModel:
    """Extract structured output using GPT-5.1 with reasoning_effort control.

    This method is optimized for GPT-5.1 and uses the Responses API with
    reasoning_effort parameter for better control over speed vs. intelligence.

    Args:
        text: Input text to extract structured data from
        json_schema: JSON schema defining the structure to extract
        schema_name: Name for the dynamically created Pydantic model
        prompt: Optional additional context/instructions
        system: Optional system message (uses default if not provided)
        model: Model to use (default: "gpt-5.1")
        api_key: Optional OpenAI API key (uses env var if not provided)
        reasoning_effort: Reasoning effort level for GPT-5.1
            - "none": Fast, no reasoning (default for structured output)
            - "low": Light reasoning
            - "medium": Moderate reasoning
            - "high": Deep reasoning
        cache: Optional cache implementation
        cache_key: Optional cache key

    Returns:
        BaseModel: Pydantic model instance with extracted data

    Example:
        ```python
        schema = {
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["name"]
        }

        result = await extract_structured_gpt51(
            text="John is 25 years old",
            json_schema=schema,
            schema_name="Person",
            reasoning_effort="none"  # Fast extraction
        )
        ```
    """
    import logging
    from openai import OpenAI

    logger = logging.getLogger(__name__)

    # Try cache first (if provided)
    if cache and cache_key:
        cached_result = await cache.get(cache_key)
        if cached_result:
            logger.debug(f"Cache hit for key: {cache_key[:16]}...")
            # For GPT-5.1 strict mode, enforce all properties as required
            pre = preprocess_json_schema(json_schema, enforce_all_required=True)
            model_cls = build_model_from_schema(schema_name, pre)
            return model_cls(**cached_result)

    # Build the Pydantic model
    # For GPT-5.1 strict mode, enforce all properties as required
    pre = preprocess_json_schema(json_schema, enforce_all_required=True)
    model_cls = build_model_from_schema(schema_name, pre)

    # Prepare the prompt
    sys_msg = system or (
        "You are a helpful AI assistant that extracts information from text based on a provided JSON schema. "
        "You produce only valid JSON per the bound schema. If a field is not found, omit it when optional or set null if allowed. Do not invent values."
    )
    user_msg = f"Text to analyze:\n{text}"
    if prompt:
        user_msg += f"\n\n{prompt}"

    # Use OpenAI client directly for Responses API
    client = OpenAI(api_key=api_key)

    # Convert Pydantic model to JSON schema for OpenAI
    from pydantic import TypeAdapter
    adapter = TypeAdapter(model_cls)
    raw_schema = adapter.json_schema()

    # Resolve all $ref to inline definitions (OpenAI strict mode requirement)
    defs = raw_schema.pop('$defs', {})
    response_format = _resolve_refs(raw_schema, defs)

    # OpenAI strict mode requires ALL properties to be in required array
    # Add enforce_all_required logic to the resolved schema
    def enforce_strict_required(schema: Dict[str, Any]) -> Dict[str, Any]:
        if not isinstance(schema, dict):
            return schema
        s = dict(schema)
        if s.get("type") == "object" and isinstance(s.get("properties"), dict):
            props = dict(s.get("properties", {}))
            # Make all properties required for strict mode
            s["required"] = list(props.keys())
            # Recursively enforce on nested objects
            for prop_name, prop_schema in props.items():
                props[prop_name] = enforce_strict_required(prop_schema)
            s["properties"] = props
        if "items" in s and isinstance(s["items"], dict):
            s["items"] = enforce_strict_required(s["items"])
        return s

    response_format = enforce_strict_required(response_format)

    try:
        # Use Responses API with reasoning_effort
        # Note: GPT-5.1 does not support temperature, top_p, or max_tokens
        response = client.responses.create(
            model=model,
            input=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": user_msg}
            ],
            reasoning={"effort": reasoning_effort},
            max_output_tokens=100000,  # GPT-5.1 max output is 100K tokens
            text={
                "format": {
                    "type": "json_schema",
                    "name": schema_name,
                    "strict": True,
                    "schema": response_format
                }
            },
        )

        # Extract the JSON output
        output_text = response.output_text
        import json
        result_dict = json.loads(output_text)

        # Convert to Pydantic model
        result = model_cls(**result_dict)

        # Store in cache (if provided)
        if cache and cache_key:
            result_dict = result.model_dump() if hasattr(result, "model_dump") else result.dict()
            await cache.set(cache_key, result_dict)
            logger.debug(f"Cached result for key: {cache_key[:16]}...")

        return result

    except Exception as e:
        logger.error(f"GPT-5.1 structured extraction failed: {e}")
        raise


async def extract_structured(
    *,
    text: str,
    json_schema: Dict[str, Any],
    schema_name: str = "DynamicSchema",
    prompt: Optional[str] = None,
    system: Optional[str] = None,
    enforce_all_required: bool = False,
    model: Optional[str] = None,
    api_key: Optional[str] = None,
    cache: Optional[Any] = None,
    cache_key: Optional[str] = None,
) -> BaseModel:
    """High-level helper: from text + JSON Schema to structured model in one call.

    - Builds a strict Pydantic model (extras=forbid) from the JSON Schema.
    - Uses a default system instruction if not provided.
    - Concatenates optional `prompt` after the text for extra guidance.

    Args:
        cache: Optional cache implementation (follows LLMCache protocol)
        cache_key: Optional pre-computed cache key. If not provided and cache
                   is given, caller should generate key before calling.

    Note:
        The library does NOT generate cache keys. Services should generate
        keys based on their specific needs (text, schema, prompt, etc.)
    """
    import logging

    logger = logging.getLogger(__name__)

    # Try cache first (if provided)
    if cache and cache_key:
        cached_result = await cache.get(cache_key)
        if cached_result:
            logger.debug(f"Cache hit for key: {cache_key[:16]}...")
            # Reconstruct Pydantic model from cached dict
            pre = preprocess_json_schema(json_schema, enforce_all_required)
            model_cls = build_model_from_schema(schema_name, pre)
            return model_cls(**cached_result)

    # Cache miss or no cache - proceed with LLM call
    gen = StructuredOutputGenerator(model=model, api_key=api_key)
    pre = preprocess_json_schema(json_schema, enforce_all_required=enforce_all_required)
    model_cls = build_model_from_schema(schema_name, pre)
    sys_msg = system or (
        "You are a helpful AI assistant that extracts information from text based on a provided JSON schema. "
        "You produce only valid JSON per the bound schema. If a field is not found, omit it when optional or set null if allowed. Do not invent values."
    )
    user = f"Text to analyze:\n{text}\n\n{prompt or ''}"
    result = await gen.generate_from_model(prompt=user, schema_model=model_cls, system=sys_msg)

    # Store in cache (if provided)
    if cache and cache_key:
        # Convert Pydantic model to dict for caching
        result_dict = result.model_dump() if hasattr(result, "model_dump") else result.dict()
        await cache.set(cache_key, result_dict)
        logger.debug(f"Cached result for key: {cache_key[:16]}...")

    return result
