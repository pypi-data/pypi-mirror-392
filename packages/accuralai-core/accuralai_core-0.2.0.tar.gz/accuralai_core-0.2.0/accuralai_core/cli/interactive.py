"""Interactive CLI inspired by Codex-style REPL workflows."""

from __future__ import annotations

import json
import os
import shlex
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple

import anyio
import click

from accuralai_core.contracts.errors import AccuralAIError
from accuralai_core.contracts.models import GenerateRequest, GenerateResponse
from accuralai_core.core.orchestrator import CoreOrchestrator
from accuralai_core.config.loader import load_settings

from .output import render_json, render_text, render_compact, ResponseFormatter
from .state import SessionState, create_default_state
from .tools.registry import ToolRegistry
from .tools.runner import ToolRunner

try:  # Optional richer prompt support.
    from prompt_toolkit import PromptSession
    from prompt_toolkit.history import InMemoryHistory
except ImportError:  # pragma: no cover - fallback when prompt_toolkit absent
    PromptSession = None  # type: ignore
    InMemoryHistory = None  # type: ignore


Writer = Callable[[str], None]

BANNER = """\
╭──────────────── AccuralAI REPL ───────────────╮
│ Codex-style shell for rapid LLM iteration     │
│ Type plain text to run a prompt               │
│ Use /help for commands, /exit to quit         │
│ Use /format compact for quick responses       │
╰───────────────────────────────────────────────╯
"""

COMMAND_HELP: Dict[str, str] = {
    "help": "Show command summary or details: /help [command]",
    "backend": "Set or view backend hint: /backend <id> | /backend reset",
    "model": "Set default model parameter: /model <name> | /model reset",
    "router": "Set a router hint metadata entry: /router <id> | /router reset",
    "system": "View or set default system prompt: /system [text]",
    "tag": "Manage tags: /tag add <tag>, /tag remove <tag>, /tag list, /tag clear",
    "meta": "Manage metadata defaults: /meta set key=value, /meta clear <key>, /meta list",
    "params": "Manage parameter defaults (same syntax as /meta)",
    "history": "Toggle/view conversation history: /history on|off|show|clear",
    "format": "Set response format: /format text|json|compact",
    "stream": "Toggle streaming flag (future backends): /stream on|off",
    "config": "Manage config paths: /config add <path>, /config list",
    "reset": "Reset session state (preserves config paths).",
    "save": "Persist session transcript/settings: /save <file>",
    "debug": "Toggle debug output: /debug on|off",
    "tool": "Manage tools: /tool list | /tool info <name> | /tool enable <name> | /tool run <name>",
    "exit": "Exit the shell.",
}


class InteractiveShell:
    """Codex-inspired interactive CLI runner."""

    def __init__(
        self,
        *,
        state: SessionState,
        writer: Optional[Writer] = None,
    ) -> None:
        self.state = state
        if not hasattr(self.state, "conversation"):
            self.state.conversation = []
        self._writer = writer or click.echo
        self._running = True
        self._orchestrator: Optional[CoreOrchestrator] = None
        self._prompt_session = None
        self._tool_registry = ToolRegistry()
        self._tool_runner = ToolRunner()
        if PromptSession is not None and self._can_use_prompt_toolkit():
            history = InMemoryHistory() if InMemoryHistory else None
            self._prompt_session = PromptSession(history=history)
        
        # Load tool configuration from settings
        self._load_tool_configuration()

    # --------------------------------------------------------------------- run loop
    def run(self) -> None:
        """Run the interactive session loop."""
        self._writer(BANNER)
        while self._running:
            try:
                line = self._readline(primary=True)
            except (EOFError, KeyboardInterrupt):
                self._writer("")  # move to next line
                self._writer("Type /exit to leave the shell.")
                continue

            if not line.strip():
                continue

            try:
                self.execute_line(line)
            except Exception as error:  # pragma: no cover - defensive logging
                if self.state.debug:
                    self._writer(f"[error] {error!r}")
                else:
                    self._writer(f"[error] {error}")

        # Ensure orchestrator cleaned up if session ended.
        if self._orchestrator:
            anyio.run(self._orchestrator.aclose)

    # --------------------------------------------------------------------- helpers
    def execute_line(self, line: str) -> None:
        """Execute a command or submit a generation request."""
        stripped = line.strip()
        if stripped.startswith("/"):
            self._handle_command(stripped[1:])
        else:
            prompt_text = self._collect_multiline(stripped)
            self._submit_prompt(prompt_text)

    def _collect_multiline(self, first_line: str) -> str:
        """Collect multi-line prompt when user enters standalone triple quotes."""
        if first_line == '"""':
            lines: List[str] = []
            self._writer("(enter prompt, end with \"\"\")")
            while True:
                try:
                    next_line = self._readline(primary=False)
                except EOFError:
                    break
                if next_line.strip() == '"""':
                    break
                lines.append(next_line)
            return "\n".join(lines).strip()
        return first_line

    def _readline(self, *, primary: bool) -> str:
        """Read a line from input, using prompt_toolkit when available."""
        prompt = ">>> " if primary else "... "
        if self._prompt_session is not None:
            return self._prompt_session.prompt(prompt)
        return input(prompt)

    def _can_use_prompt_toolkit(self) -> bool:
        """Return True if prompt_toolkit can attach to the current terminal."""
        if os.name != "nt":
            return True
        try:
            import msvcrt  # noqa: F401

            return bool(os.isatty(0) and os.isatty(1))
        except Exception:  # pragma: no cover - best effort
            return False

    def _load_tool_configuration(self) -> None:
        """Load tool configuration from settings and enable/disable tools accordingly."""
        try:
            # Load settings from config paths
            settings = load_settings(
                config_paths=self.state.config_paths,
                overrides=self.state.config_overrides
            )
            
            tool_config = settings.tools
            
            # Enable tools specified in enabled_by_default
            for tool_name in tool_config.enabled_by_default:
                spec = self._tool_registry.get(tool_name)
                if spec and spec.function:
                    func_name = spec.function.get("name") or spec.name
                    self.state.tool_defs[func_name] = dict(spec.function)
                    self.state.tool_functions[func_name] = spec.name
                    self.state.tools_version += 1
            
            # If auto_enable is True, enable all available tools except those in disabled_by_default
            if tool_config.auto_enable:
                for spec in self._tool_registry.list_tools():
                    if spec.name not in tool_config.disabled_by_default and spec.function:
                        func_name = spec.function.get("name") or spec.name
                        if func_name not in self.state.tool_defs:  # Don't override already enabled tools
                            self.state.tool_defs[func_name] = dict(spec.function)
                            self.state.tool_functions[func_name] = spec.name
                            self.state.tools_version += 1
            
        except Exception as e:
            # If there's an error loading config, just continue without tool configuration
            # This ensures the CLI still works even with malformed config
            if self.state.debug:
                self._writer(f"Warning: Could not load tool configuration: {e}")

    def _handle_command(self, command_line: str) -> None:
        parts = shlex.split(command_line, posix=os.name != "nt")
        if not parts:
            return
        command = parts[0].lower()
        args = parts[1:]

        handler_map = {
            "help": self._cmd_help,
            "exit": self._cmd_exit,
            "backend": self._cmd_backend,
            "model": self._cmd_model,
            "router": self._cmd_router,
            "system": self._cmd_system,
            "tag": self._cmd_tag,
            "meta": self._cmd_meta,
            "params": self._cmd_params,
            "history": self._cmd_history,
            "format": self._cmd_format,
            "stream": self._cmd_stream,
            "config": self._cmd_config,
            "reset": self._cmd_reset,
            "save": self._cmd_save,
            "debug": self._cmd_debug,
            "tool": self._cmd_tool,
            "t": self._cmd_tool,
            "tools": self._cmd_tool,
        }

        handler = handler_map.get(command)
        if not handler:
            self._writer(f"Unknown command '/{command}'. Try /help.")
            return
        handler(args)

    def _writer_json(self, response: GenerateResponse) -> None:
        if self.state.response_format == "json":
            self._writer(render_json(response))
        elif self.state.response_format == "compact":
            self._writer(render_compact(response))
        else:
            self._writer(render_text(response))
    
    def _show_progress(self, message: str = "Processing...") -> None:
        """Show a progress indicator."""
        self._writer(f"{message}")
    
    def _show_streaming_header(self, response: GenerateResponse) -> None:
        """Show streaming response header."""
        formatter = ResponseFormatter()
        metadata_bar = formatter.format_metadata_bar(response)
        
        # Create a streaming header
        header_lines = [
            "+- Streaming Response ----------------------------------------------------+",
            f"| {metadata_bar:<75} |",
            "+-----------------------------------------------------------------------+"
        ]
        
        self._writer("\n".join(header_lines))
        self._writer("")  # Empty line

    # ---------------------------------------------------------------- commands impl
    def _cmd_help(self, args: List[str]) -> None:
        if not args:
            self._writer("Available commands:")
            for name, description in sorted(COMMAND_HELP.items()):
                self._writer(f"  /{name:<8} {description}")
            self._writer('Enter plain text to send a prompt, or """ to start multi-line input.')
            self._writer('Explore tools with /tool list and run them via /tool run <name>.')
            return
        topic = args[0].lower()
        description = COMMAND_HELP.get(topic)
        if description:
            self._writer(f"/{topic}: {description}")
        else:
            self._writer(f"No help available for '/{topic}'.")

    def _cmd_exit(self, _args: List[str]) -> None:
        self._writer("Exiting AccuralAI shell.")
        self._running = False

    def _cmd_backend(self, args: List[str]) -> None:
        if not args:
            current_value = self.state.route_hint or "(none)"
            self._writer(f"Current backend hint: {current_value}")
            
            # Show available backends from config
            config = self._load_current_config()
            if config and "backends" in config:
                backends = list(config["backends"].keys())
                if backends:
                    self._writer("Available backends:")
                    for backend_id in backends:
                        backend_config = config["backends"][backend_id]
                        plugin_info = f" ({backend_config.get('plugin', 'unknown')})"
                        self._writer(f"  {backend_id}{plugin_info}")
                else:
                    self._writer("No backends configured")
            return
        arg = args[0].lower()
        if arg == "reset":
            self.state.route_hint = None
            self._writer("Cleared backend hint.")
        else:
            self.state.route_hint = args[0]
            self._writer(f"Backend hint set to '{args[0]}'.")

    def _cmd_model(self, args: List[str]) -> None:
        if not args:
            current_value = self.state.parameters.get("model", "(none)")
            self._writer(f"Current model: {current_value}")
            
            # Show default model from config
            config = self._load_current_config()
            if config and "backends" in config:
                default_models = []
                for backend_id, backend_config in config["backends"].items():
                    if backend_config.get("options", {}).get("model"):
                        default_models.append(f"{backend_id}: {backend_config['options']['model']}")
                
                if default_models:
                    self._writer("Available default models:")
                    for model in default_models:
                        self._writer(f"  {model}")
                else:
                    self._writer("No default models configured")
            return
        option = args[0]
        if option.lower() == "reset":
            self.state.parameters.pop("model", None)
            self._writer("Cleared model.")
            return

        self.state.parameters["model"] = option
        self._writer(f"Model set to '{option}'.")

    def _cmd_router(self, args: List[str]) -> None:
        # Router hints stored in metadata (e.g., metadata["router_hint"])
        if not args:
            current_value = self.state.metadata.get("router_hint")
            self._writer(f"Current router hint: {current_value or '(none)'}")
            
            # Show default router from config
            config = self._load_current_config()
            if config and "router" in config:
                router_config = config["router"]
                if router_config.get("plugin"):
                    self._writer(f"Default router: {router_config['plugin']}")
                    if router_config.get("default_backend"):
                        self._writer(f"Default backend: {router_config['default_backend']}")
                else:
                    self._writer("No default router configured")
            return
        if args[0].lower() == "reset":
            self.state.metadata.pop("router_hint", None)
            self._writer("Cleared router hint.")
        else:
            self.state.metadata["router_hint"] = args[0]
            self._writer(f"Router hint set to '{args[0]}'.")

    def _cmd_system(self, args: List[str]) -> None:
        if not args:
            self._writer(self.state.system_prompt or "(no system prompt)")
            return
        self.state.system_prompt = " ".join(args)
        self._writer("System prompt updated.")

    def _cmd_tag(self, args: List[str]) -> None:
        if not args:
            self._writer("Usage: /tag add <tag> | /tag remove <tag> | /tag list | /tag clear")
            return
        action = args[0].lower()
        if action == "add" and len(args) >= 2:
            tag = args[1]
            if tag not in self.state.tags:
                self.state.tags.append(tag)
            self._writer(f"Tag '{tag}' added.")
        elif action == "remove" and len(args) >= 2:
            tag = args[1]
            if tag in self.state.tags:
                self.state.tags.remove(tag)
                self._writer(f"Tag '{tag}' removed.")
            else:
                self._writer(f"Tag '{tag}' not present.")
        elif action == "list":
            self._writer("Tags: " + (", ".join(self.state.tags) if self.state.tags else "(none)"))
        elif action == "clear":
            self.state.tags.clear()
            self._writer("All tags cleared.")
        else:
            self._writer("Usage: /tag add <tag> | /tag remove <tag> | /tag list | /tag clear")

    def _cmd_meta(self, args: List[str]) -> None:
        self._handle_kv_command(args, store=self.state.metadata, label="metadata")

    def _cmd_params(self, args: List[str]) -> None:
        self._handle_kv_command(args, store=self.state.parameters, label="parameters")

    def _handle_kv_command(self, args: List[str], *, store: Dict[str, Any], label: str) -> None:
        if not args:
            self._writer(f"Usage: /{label} set key=value | /{label} clear <key> | /{label} list")
            return
        action = args[0].lower()
        if action == "set" and len(args) >= 2:
            key, value = self._parse_kv(args[1])
            store[key] = value
            self._writer(f"{label.title()} '{key}' set.")
        elif action == "clear" and len(args) >= 2:
            store.pop(args[1], None)
            self._writer(f"{label.title()} '{args[1]}' cleared.")
        elif action == "list":
            if not store:
                self._writer(f"No default {label}.")
            else:
                for key, value in store.items():
                    self._writer(f"{key} = {json.dumps(value)}")
        else:
            self._writer(f"Usage: /{label} set key=value | /{label} clear <key> | /{label} list")

    def _cmd_history(self, args: List[str]) -> None:
        if not args:
            status = "on" if self.state.history_enabled else "off"
            self._writer(f"History capture is {status}.")
            return
        action = args[0].lower()
        if action == "on":
            self.state.history_enabled = True
            self._writer("History capture enabled.")
        elif action == "off":
            self.state.history_enabled = False
            self._writer("History capture disabled.")
        elif action == "show":
            if not self.state.history:
                self._writer("(no history)")
            else:
                for entry in self.state.history:
                    role = entry.get("role", "unknown")
                    content = entry.get("content", "")
                    self._writer(f"[{role}] {content}")
        elif action == "clear":
            self.state.history.clear()
            self._writer("History cleared.")
        else:
            self._writer("Usage: /history on|off|show|clear")

    def _cmd_format(self, args: List[str]) -> None:
        if not args:
            self._writer(f"Response format: {self.state.response_format}")
            return
        choice = args[0].lower()
        if choice in {"text", "json", "compact"}:
            self.state.response_format = choice
            self._writer(f"Response format set to {choice}.")
        else:
            self._writer("Unsupported format. Use /format text|json|compact.")

    def _cmd_stream(self, args: List[str]) -> None:
        if not args:
            status = "on" if self.state.stream else "off"
            self._writer(f"Streaming flag is {status}.")
            return
        option = args[0].lower()
        if option in {"on", "off"}:
            self.state.stream = option == "on"
            self._writer(f"Streaming flag set to {option}. (Backend support required)")
        else:
            self._writer("Usage: /stream on|off")

    def _cmd_config(self, args: List[str]) -> None:
        if not args or args[0].lower() == "list":
            if not self.state.config_paths:
                self._writer("No config paths supplied.")
            else:
                self._writer("Config paths:")
                for path in self.state.config_paths:
                    self._writer(f"  {path}")
            
            # Show current configuration summary
            config = self._load_current_config()
            if config:
                self._writer("\nCurrent configuration:")
                
                # Canonicalizer
                if "canonicalizer" in config:
                    canonicalizer = config["canonicalizer"]
                    self._writer(f"  Canonicalizer: {canonicalizer.get('plugin', 'none')}")
                
                # Cache
                if "cache" in config:
                    cache = config["cache"]
                    self._writer(f"  Cache: {cache.get('plugin', 'none')}")
                    if cache.get("ttl_s"):
                        self._writer(f"    TTL: {cache['ttl_s']}s")
                
                # Router
                if "router" in config:
                    router = config["router"]
                    self._writer(f"  Router: {router.get('plugin', 'none')}")
                    if router.get("default_backend"):
                        self._writer(f"    Default backend: {router['default_backend']}")
                
                # Backends
                if "backends" in config and config["backends"]:
                    self._writer("  Backends:")
                    for backend_id, backend_config in config["backends"].items():
                        plugin = backend_config.get("plugin", "unknown")
                        model = backend_config.get("options", {}).get("model", "none")
                        self._writer(f"    {backend_id}: {plugin} (model: {model})")
                
                # Tools
                if "tools" in config:
                    tools = config["tools"]
                    enabled_count = len(tools.get("enabled_by_default", []))
                    disabled_count = len(tools.get("disabled_by_default", []))
                    self._writer(f"  Tools: {enabled_count} enabled by default, {disabled_count} disabled by default")
            return
        action = args[0].lower()
        if action != "add" or len(args) < 2:
            self._writer("Usage: /config add <path> | /config list")
            return
        path = Path(args[1]).expanduser()
        if not path.exists():
            self._writer(f"Config path '{path}' does not exist.")
            return
        if str(path) not in self.state.config_paths:
            self.state.config_paths.append(str(path))
            self._writer(f"Added config path '{path}'.")
            self._restart_orchestrator()
        else:
            self._writer("Config path already present.")

    def _cmd_reset(self, _args: List[str]) -> None:
        self.state.reset()
        self._writer("Session reset to defaults.")

    def _cmd_save(self, args: List[str]) -> None:
        if not args:
            self._writer("Usage: /save <file>")
            return
        path = Path(args[0]).expanduser()
        data = {
            "state": self.state.to_serializable(),
        }
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(data, indent=2))
        self._writer(f"Session saved to '{path}'.")

    def _cmd_debug(self, args: List[str]) -> None:
        if not args:
            status = "on" if self.state.debug else "off"
            self._writer(f"Debug mode is {status}.")
            return
        option = args[0].lower()
        if option in {"on", "off"}:
            self.state.debug = option == "on"
            self._writer(f"Debug mode set to {option}.")
        else:
            self._writer("Usage: /debug on|off")

    def _cmd_tool(self, args: List[str]) -> None:
        if not args:
            self._writer("Usage: /tool list | /tool info <name> | /tool run <name> [args...] | /tool reload")
            return

        action = args[0].lower()
        rest = args[1:]

        if action == "list":
            tools = list(self._tool_registry.list_tools())
            if not tools:
                self._writer("No tools registered.")
                return
            enabled = set(self.state.tool_functions.keys())
            for spec in tools:
                package = f" ({spec.package})" if spec.package else ""
                flag = " [enabled]" if spec.function and spec.function.get("name") in enabled else ""
                self._writer(f"- {spec.name}{package}{flag}: {spec.description}")
            return

        if action == "info" and rest:
            spec = self._tool_registry.get(rest[0])
            if not spec:
                self._writer(f"Tool '{rest[0]}' not found.")
                return
            self._writer(f"Name: {spec.name}")
            self._writer(f"Description: {spec.description}")
            if spec.usage:
                self._writer(f"Usage: {spec.usage}")
            if spec.package:
                self._writer(f"Provided by: {spec.package}")
            return

        if action == "reload":
            self._tool_registry.reload()
            count = len(list(self._tool_registry.list_tools()))
            self._writer(f"Reloaded tool registry ({count} tools).")
            return

        if action == "enable" and rest:
            spec = self._tool_registry.get(rest[0])
            if not spec:
                self._writer(f"Tool '{rest[0]}' not found.")
                return
            if not spec.function:
                self._writer("Tool does not expose a function declaration.")
                return
            func_name = spec.function.get("name") or spec.name
            self.state.tool_defs[func_name] = dict(spec.function)
            self.state.tool_functions[func_name] = spec.name
            self.state.tools_version += 1
            self._writer(f"Enabled tool function '{func_name}'.")
            return

        if action == "disable" and rest:
            target = rest[0]
            removed = False
            if target in self.state.tool_functions:
                self.state.tool_functions.pop(target, None)
                self.state.tool_defs.pop(target, None)
                removed = True
            else:
                for func, spec_name in list(self.state.tool_functions.items()):
                    if spec_name == target:
                        self.state.tool_functions.pop(func, None)
                        self.state.tool_defs.pop(func, None)
                        removed = True
            if removed:
                self.state.tools_version += 1
                self._writer(f"Disabled tool function '{target}'.")
            else:
                self._writer(f"Tool function '{target}' not enabled.")
            return

        if action == "run" and rest:
            name = rest[0]
            spec = self._tool_registry.get(name)
            if not spec:
                self._writer(f"Tool '{name}' not found.")
                return
            args = rest[1:]

            result = anyio.run(self._tool_runner.run, spec, self.state, args, None)
            prefix = "[tool]" if result.status == "success" else "[tool error]"
            self._writer(f"{prefix} {spec.name} → {result.message}")
            if result.suggest_prompt:
                self._writer(result.suggest_prompt)
            return

        self._writer("Usage: /tool list | /tool info <name> | /tool run <name> [args...] | /tool reload | /tool enable <name> | /tool disable <name>")

    # ---------------------------------------------------------------- prompt submit
    def _submit_prompt(self, prompt_text: str) -> None:
        if not prompt_text:
            self._writer("(empty prompt ignored)")
            return
        
        # Show progress indicator
        self._show_progress("Generating response...")
        
        try:
            response = anyio.run(self._conversation_loop, prompt_text)
        except AccuralAIError as error:
            self._writer(f"Pipeline error: {error}")
            if self.state.debug and error.stage_context:
                self._writer(f"  stage={error.stage_context.stage} plugin={error.stage_context.plugin_id}")
            return

        if response is not None:
            self._writer_json(response)

    async def _conversation_loop(self, prompt_text: str) -> Optional[GenerateResponse]:
        orchestrator = await self._ensure_orchestrator()
        base_conversation = list(self.state.conversation)
        conversation = list(base_conversation)
        user_added = False
        pending_prompt = prompt_text
        loop_count = 0
        final_response: Optional[GenerateResponse] = None

        while True:
            parameters = dict(self.state.parameters)
            if self.state.tool_defs and "function_calling_config" not in parameters:
                parameters["function_calling_config"] = {"mode": "AUTO"}
            request = GenerateRequest(
                prompt=pending_prompt,
                system_prompt=self.state.system_prompt,
                route_hint=self.state.route_hint,
                metadata=dict(self.state.metadata),
                parameters=parameters,
                tags=list(self.state.tags),
                history=list(conversation),
                tools=list(self.state.tool_defs.values()),
            )

            response = await orchestrator.generate(request)
            final_response = response
            tool_calls = response.metadata.get("tool_calls") or []

            if not user_added:
                conversation.append({"role": "user", "content": prompt_text})
                user_added = True

            if tool_calls:
                conversation.append({"role": "assistant", "tool_calls": tool_calls})
                tool_error = False
                for call in tool_calls:
                    payload = await self._execute_tool_call(call)
                    conversation.append(
                        {
                            "role": "tool",
                            "name": payload["name"],
                            "content": payload["content"],
                        }
                    )
                    if payload["status"] != "success":
                        tool_error = True
                if tool_error:
                    break
                pending_prompt = ""
                loop_count += 1
                if loop_count >= 4:
                    self._writer("[tool error] Too many tool call rounds.")
                    break
                continue

            conversation.append({"role": "assistant", "content": response.output_text})
            break

        self.state.conversation = conversation

        if self.state.history_enabled and final_response is not None:
            self.state.history.append({"role": "user", "content": prompt_text})
            self.state.history.append({"role": "assistant", "content": final_response.output_text})

        return final_response

    async def _execute_tool_call(self, call: Dict[str, Any]) -> Dict[str, Any]:
        name = call.get("name") or call.get("functionName") or "unknown"
        raw_args = call.get("arguments") or call.get("args") or {}
        if isinstance(raw_args, str):
            try:
                raw_args = json.loads(raw_args)
            except json.JSONDecodeError:
                raw_args = {"raw": raw_args}
        if not isinstance(raw_args, dict):
            raw_args = {}

        spec_name = self.state.tool_functions.get(name)
        spec = None
        if spec_name:
            spec = self._tool_registry.get(spec_name)
        if spec is None:
            spec = self._tool_registry.get(name) or self._tool_registry.get_by_function(name)

        if spec is None:
            message = f"Tool function '{name}' not registered."
            self._writer(f"[tool error] {message}")
            return {
                "name": name,
                "status": "error",
                "content": {"error": message},
            }

        result = await self._tool_runner.run(spec, self.state, [], raw_args)
        prefix = "[tool]" if result.status == "success" else "[tool error]"
        self._writer(f"{prefix} {name} → {result.message}")

        if result.status == "success":
            content = result.message
        else:
            content = result.data if result.data is not None else {"message": result.message}
        
        return {
            "name": name,
            "status": result.status,
            "content": content,
        }

    async def _ensure_orchestrator(self) -> CoreOrchestrator:
        if self._orchestrator is None:
            self._orchestrator = CoreOrchestrator(
                config_paths=list(self.state.config_paths),
                config_overrides=self.state.config_overrides,
            )
        return self._orchestrator

    def _restart_orchestrator(self) -> None:
        if self._orchestrator:
            anyio.run(self._orchestrator.aclose)
        self._orchestrator = None

    def _load_current_config(self) -> Optional[Dict[str, Any]]:
        """Load the current configuration settings."""
        try:
            if self.state.config_paths:
                config = load_settings(config_paths=self.state.config_paths)
            else:
                from accuralai_core.config.defaults import get_default_settings
                config = get_default_settings()
            return config.model_dump()
        except Exception as e:
            if self.state.debug:
                self._writer(f"Failed to load config: {e}")
            return None

    # ---------------------------------------------------------------- utilities
    @staticmethod
    def _parse_kv(token: str) -> Tuple[str, Any]:
        if "=" not in token:
            raise ValueError(f"Key/value pairs must be key=value (received '{token}')")
        key, raw = token.split("=", 1)
        raw = raw.strip()
        try:
            value = json.loads(raw)
        except json.JSONDecodeError:
            value = raw
        return key, value


def run_interactive_cli(
    *,
    config_paths: Optional[Iterable[str]] = None,
    config_overrides: Optional[Dict[str, Any]] = None,
) -> None:
    """Entrypoint invoked when CLI starts without explicit command."""
    state = create_default_state(
        config_paths=list(config_paths or []),
        config_overrides=dict(config_overrides or {}),
    )
    shell = InteractiveShell(state=state)
    shell.run()
