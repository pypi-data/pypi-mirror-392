from copy import deepcopy
import json
from typing import Any, Dict, List, Optional, Tuple

import httpx

from agentrun.utils.config import Config
from agentrun.utils.log import logger


class OpenAPI:
    """OpenAPI schema based tool client."""

    _SUPPORTED_METHODS = {
        "DELETE",
        "GET",
        "HEAD",
        "OPTIONS",
        "PATCH",
        "POST",
        "PUT",
    }

    def __init__(
        self,
        schema: Any,
        base_url: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
        query_params: Optional[Dict[str, Any]] = None,
        config: Optional[Config] = None,
        timeout: Optional[int] = None,
    ):
        self._raw_schema = schema or ""
        self._schema = self._load_schema(self._raw_schema)
        self._operations = self._build_operations(self._schema)
        self._base_url = base_url or self._extract_base_url(self._schema)
        self._default_headers = headers.copy() if headers else {}
        self._default_query_params = query_params.copy() if query_params else {}
        self._base_config = config
        self._default_timeout = (
            timeout or (config.get_timeout() if config else None) or 60
        )

    def list_tools(self, name: Optional[str] = None) -> List[Dict[str, Any]]:
        """List tools defined in the OpenAPI schema.

        Args:
            name: OperationId of the tool. When provided, return the single
                tool definition; otherwise return all tools.

        Returns:
            A list of tool metadata dictionaries.
        """

        if name:
            if name not in self._operations:
                raise ValueError(f"Tool '{name}' not found in OpenAPI schema.")
            return [deepcopy(self._operations[name])]

        return [deepcopy(item) for item in self._operations.values()]

    def has_tool(self, name: str) -> bool:
        return name in self._operations

    def invoke_tool(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None,
        config: Optional[Config] = None,
    ) -> Dict[str, Any]:
        request_kwargs, timeout, raise_for_status = self._prepare_request(
            name, arguments, config
        )
        with httpx.Client(timeout=timeout) as client:
            response = client.request(**request_kwargs)
            if raise_for_status:
                response.raise_for_status()
            return self._format_response(response)

    async def invoke_tool_async(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]] = None,
        config: Optional[Config] = None,
    ) -> Dict[str, Any]:
        request_kwargs, timeout, raise_for_status = self._prepare_request(
            name, arguments, config
        )
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.request(**request_kwargs)
            if raise_for_status:
                response.raise_for_status()
            return self._format_response(response)

    def _load_schema(self, schema: Any) -> Dict[str, Any]:
        if isinstance(schema, dict):
            return schema

        if isinstance(schema, (bytes, bytearray)):
            schema = schema.decode("utf-8")

        if not schema:
            raise ValueError("OpenAPI schema detail is required.")

        try:
            return json.loads(schema)
        except json.JSONDecodeError:
            pass

        try:
            import yaml
        except ImportError as exc:  # pragma: no cover
            raise ImportError(
                "PyYAML is required to parse OpenAPI YAML schema."
            ) from exc

        try:
            return yaml.safe_load(schema) or {}
        except yaml.YAMLError as exc:  # pragma: no cover
            raise ValueError("Invalid OpenAPI schema content.") from exc

    def _extract_base_url(self, schema: Dict[str, Any]) -> Optional[str]:
        servers = schema.get("servers") or []
        return self._pick_server_url(servers)

    def _pick_server_url(self, servers: Any) -> Optional[str]:
        if not servers:
            return None

        if isinstance(servers, dict):
            servers = [servers]

        if not isinstance(servers, list):
            return None

        for server in servers:
            if isinstance(server, str):
                return server
            if not isinstance(server, dict):
                continue
            url = server.get("url")
            if not url:
                continue
            variables = server.get("variables", {})
            if isinstance(variables, dict):
                for key, meta in variables.items():
                    default = (
                        meta.get("default") if isinstance(meta, dict) else None
                    )
                    if default is not None:
                        url = url.replace(f"{{{key}}}", str(default))
            return url

        return None

    def _build_operations(
        self, schema: Dict[str, Any]
    ) -> Dict[str, Dict[str, Any]]:
        operations: Dict[str, Dict[str, Any]] = {}
        paths = schema.get("paths") or {}
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            path_parameters = path_item.get("parameters", [])
            path_servers = path_item.get("servers")
            for method, operation in path_item.items():
                if method.upper() not in self._SUPPORTED_METHODS:
                    continue
                if not isinstance(operation, dict):
                    continue
                operation_id = operation.get("operationId") or (
                    f"{method.upper()} {path}"
                )
                parameters = []
                if isinstance(path_parameters, list):
                    parameters.extend(path_parameters)
                operation_parameters = operation.get("parameters", [])
                if isinstance(operation_parameters, list):
                    parameters.extend(operation_parameters)
                server_url = self._pick_server_url(
                    operation.get("servers") or path_servers
                )
                operations[operation_id] = {
                    "operationId": operation_id,
                    "method": method.upper(),
                    "path": path,
                    "summary": operation.get("summary"),
                    "description": operation.get("description"),
                    "parameters": parameters,
                    "path_parameters": [
                        param.get("name")
                        for param in parameters
                        if isinstance(param, dict)
                        and param.get("in") == "path"
                        and param.get("name")
                    ],
                    "request_body": operation.get("requestBody"),
                    "responses": operation.get("responses"),
                    "tags": operation.get("tags", []),
                    "server_url": server_url,
                }
        return operations

    def _prepare_request(
        self,
        name: str,
        arguments: Optional[Dict[str, Any]],
        config: Optional[Config],
    ) -> Tuple[Dict[str, Any], float, bool]:
        if name not in self._operations:
            raise ValueError(f"Tool '{name}' not found in OpenAPI schema.")

        operation = self._operations[name]
        args = deepcopy(arguments) if arguments else {}

        combined_config = config or self._base_config
        headers: Dict[str, str] = {}
        timeout = self._default_timeout
        if combined_config:
            headers.update(combined_config.get_headers())
            _timeout = combined_config.get_timeout()
            if _timeout:
                timeout = _timeout

        headers.update(self._default_headers)

        user_headers = args.pop("headers", {})
        if isinstance(user_headers, dict):
            headers.update(user_headers)

        timeout_override = args.pop("timeout", None)
        if isinstance(timeout_override, (int, float)):
            timeout = timeout_override

        raise_for_status = bool(args.pop("raise_for_status", True))

        path_params = self._extract_dict(args, ["path", "path_params"])
        query_params = self._merge_dicts(
            self._default_query_params,
            self._extract_dict(args, ["query", "query_params"]),
        )
        body = self._extract_body(args)
        files = args.pop("files", None)
        data = args.pop("data", None)

        # Fill parameters defined in the schema.
        for param in operation.get("parameters", []):
            if not isinstance(param, dict):
                continue
            name = param.get("name", "")
            location = param.get("in")
            if not name or name not in args:
                continue
            value = args.pop(name)
            if location == "path":
                path_params[name] = value
            elif location == "query":
                query_params[name] = value
            elif location == "header":
                headers[name] = value

        method = operation["method"]
        path = self._render_path(
            operation["path"], operation["path_parameters"], path_params
        )

        base_url = (
            args.pop("base_url", None)
            or operation.get("server_url")
            or self._base_url
        )

        if not base_url:
            raise ValueError(
                "Base URL is required to invoke an OpenAPI tool. Provide it "
                "via OpenAPI(..., base_url=...) or in arguments['base_url']."
            )

        url = self._join_url(base_url, path)

        if method in {"GET", "HEAD"} and args:
            if not isinstance(query_params, dict):
                query_params = {}
            for key, value in args.items():
                query_params[key] = value
            args.clear()
        elif args and body is None and data is None:
            body = args
            args = {}

        request_kwargs: Dict[str, Any] = {
            "method": method,
            "url": url,
            "headers": headers,
        }

        if query_params:
            request_kwargs["params"] = query_params
        if files is not None:
            request_kwargs["files"] = files
        if data is not None:
            request_kwargs["data"] = data
        if body is not None and method not in {"GET", "HEAD"}:
            request_kwargs["json"] = body

        if args:
            logger.debug(
                "Unused arguments when invoking OpenAPI tool '%s': %s",
                name,
                args,
            )

        return request_kwargs, timeout, raise_for_status

    def _format_response(self, response: httpx.Response) -> Dict[str, Any]:
        try:
            body = response.json()
        except ValueError:
            body = response.text

        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "body": body,
            "raw_body": response.text,
            "url": str(response.request.url),
            "method": response.request.method,
        }

    def _extract_dict(
        self, source: Dict[str, Any], keys: List[str]
    ) -> Dict[str, Any]:
        for key in keys:
            value = source.pop(key, None)
            if value is None:
                continue
            if isinstance(value, dict):
                return value
            logger.warning(
                "Expected dictionary for argument '%s', got %s. Ignoring.",
                key,
                type(value).__name__,
            )
        return {}

    def _extract_body(self, source: Dict[str, Any]) -> Optional[Any]:
        if "json" in source:
            return source.pop("json")
        if "body" in source:
            return source.pop("body")
        if "payload" in source:
            return source.pop("payload")
        return None

    def _merge_dicts(
        self, base: Optional[Dict[str, Any]], override: Optional[Dict[str, Any]]
    ) -> Dict[str, Any]:
        merged: Dict[str, Any] = {}
        if isinstance(base, dict):
            merged.update(base)
        if isinstance(override, dict):
            merged.update(override)
        return merged

    def _render_path(
        self, path: str, expected_params: List[str], path_params: Dict[str, Any]
    ) -> str:
        rendered = path
        missing = []
        for name in expected_params:
            if name not in path_params:
                missing.append(name)
                continue
            rendered = rendered.replace(f"{{{name}}}", str(path_params[name]))

        if missing:
            raise ValueError(
                f"Missing path parameters for {path}: {', '.join(missing)}"
            )
        return rendered

    def _join_url(self, base_url: str, path: str) -> str:
        if not base_url:
            raise ValueError("Base URL cannot be empty.")
        if not path:
            return base_url
        return f"{base_url.rstrip('/')}/{path.lstrip('/')}"
