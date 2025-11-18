# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a **Kollabor CLI Interface** - an advanced, highly customizable terminal-based chat application for interacting with LLMs. The core principle is that **everything has hooks** - every action triggers customizable hooks that plugins can attach to for complete customization.

## Architecture

The application follows a modular, event-driven architecture:

- **Core Application** (`core/application.py`): Main orchestrator that initializes all components
- **Event System** (`core/events/`): Central event bus with hook system for plugins
- **LLM Core** (`core/llm/`): Essential LLM services including API communication, conversation management, and tool execution
- **I/O System** (`core/io/`): Terminal rendering, input handling, visual effects, and layout management
- **Plugin System** (`core/plugins/`, `plugins/`): Dynamic plugin discovery and loading
- **Storage** (`core/storage/`): State management and persistence
- **Configuration** (`core/config/`): Flexible configuration management

## Key Components

### LLM Core Services (`core/llm/`)
- `llm_service.py`: Main LLM orchestration service
- `api_communication_service.py`: API communication with rate limiting
- `conversation_logger.py`: Conversation persistence and logging (KollaborConversationLogger)
- `conversation_manager.py`: Conversation state and history management
- `tool_executor.py`: Tool/function calling execution
- `hook_system.py`: LLM-specific hook management
- `message_display_service.py`: Response formatting and display
- `mcp_integration.py`: Model Context Protocol integration
- `plugin_sdk.py`: Plugin development interface (KollaborPluginSDK)
- `model_router.py`: Model selection and routing
- `response_processor.py`: Response processing and formatting
- `response_parser.py`: Response parsing utilities

### Terminal I/O System (`core/io/`)
- `terminal_renderer.py`: Main terminal rendering with status areas
- `input_handler.py`: Raw mode input handling with key parsing
- `layout.py`: Terminal layout management and thinking animations
- `visual_effects.py`: Color palettes and visual effects
- `status_renderer.py`: Multi-area status display system
- `message_coordinator.py`: Message flow coordination
- `message_renderer.py`: Message display rendering
- `buffer_manager.py`: Terminal buffer management
- `key_parser.py`: Keyboard input parsing
- `terminal_state.py`: Terminal state management
- `core_status_views.py`: Core status view implementations
- `config_status_view.py`: Configuration status display

### Plugin Architecture
- Plugin discovery from `plugins/` directory
- Dynamic instantiation with dependency injection
- Hook registration for event interception
- Configuration merging from plugin configs

## Development Commands

### Running the Application
```bash
python main.py
```

### Testing
```bash
# Run all tests
python tests/run_tests.py

# Run specific test file
python -m unittest tests.test_llm_plugin
python -m unittest tests.test_config_manager
python -m unittest tests.test_plugin_registry

# Run individual test case
python -m unittest tests.test_llm_plugin.TestLLMPlugin.test_thinking_tags_removal
```

### Code Quality
```bash
# Install dependencies
pip install -r requirements.txt

# Format code (Black is configured for 88-character line length)
python -m black core/ plugins/ tests/ main.py

# Type checking (if mypy is available)
python -m mypy core/ plugins/

# Run linting (if flake8 is available)
python -m flake8 core/ plugins/ tests/ main.py --max-line-length=88
```

### Debugging
- Application logs to `.kollabor/logs/kollabor.log` with daily rotation
- Configuration stored in `.kollabor/config.json`
- State persistence in `.kollabor/state.db`

## Configuration System

Configuration uses dot notation (e.g., `config.get("core.llm.max_history", 90)`):
- Core LLM settings: `core.llm.*`
- Terminal rendering: `terminal.*`
- Application metadata: `application.*`

## Core Architecture Patterns

### Event-Driven Design
The application uses an event bus (`core/events/bus.py`) that coordinates between:
- **HookRegistry**: Manages hook registration and lookup
- **HookExecutor**: Handles hook execution with error handling
- **EventProcessor**: Processes events through registered hooks

### Plugin Lifecycle
1. **Discovery**: `PluginDiscovery` scans `plugins/` directory
2. **Factory**: `PluginFactory` instantiates plugins with dependency injection
3. **Registration**: Plugins register hooks during initialization
4. **Execution**: Events trigger hooks through the event bus

### LLM Service Architecture
The `LLMService` (`core/llm/llm_service.py`) orchestrates:
- **APICommunicationService**: HTTP client with rate limiting
- **KollaborConversationLogger**: Persistent conversation history
- **MessageDisplayService**: Response formatting and display
- **ToolExecutor**: Function calling execution
- **MCPIntegration**: Model Context Protocol support
- **KollaborPluginSDK**: Plugin development interface
- **LLMHookSystem**: LLM-specific hook management

## Hook System

The application's hook system allows plugins to:
- Intercept user input before processing (`pre_user_input`)
- Transform LLM requests before API calls (`pre_api_request`)
- Process responses before display (`post_api_response`)
- Add custom status indicators via `get_status_line()`
- Create new terminal UI elements

## Plugin Development

Plugins should:
1. Inherit from base plugin classes in `core/plugins/`
2. Register hooks in `register_hooks()` method using `EventType` enum
3. Provide status line information via `get_status_line()`
4. Implement `initialize()` and `shutdown()` lifecycle methods
5. Follow the async/await pattern for all hook handlers

## Project Structure

```
.
├── core/                           # Core application modules
│   ├── application.py             # Main orchestrator
│   ├── config/                    # Configuration management
│   ├── events/                    # Event bus and hook system
│   ├── io/                        # Terminal I/O, rendering, input handling
│   ├── llm/                       # LLM services (API, conversation, tools)
│   ├── models/                    # Data models
│   ├── plugins/                   # Plugin system (discovery, registry)
│   ├── storage/                   # State management
│   ├── utils/                     # Utility functions
│   ├── commands/                  # Command system (parser, registry, executor)
│   ├── ui/                        # UI system (modals, widgets, rendering)
│   ├── effects/                   # Visual effects (matrix rain, etc.)
│   └── logging/                   # Logging configuration
├── plugins/                       # Plugin implementations
│   ├── enhanced_input/           # Enhanced input plugin modules
│   ├── enhanced_input_plugin.py  # Main enhanced input plugin
│   ├── hook_monitoring_plugin.py # Hook system monitoring
│   └── [other plugins]
├── tests/                         # Test suite
│   ├── run_tests.py              # Test runner
│   ├── unit/                     # Unit tests
│   ├── integration/              # Integration tests
│   ├── visual/                   # Visual effect tests
│   ├── test_*.py                 # Component tests
│   └── README.md                 # Test documentation
├── docs/                          # Comprehensive documentation
│   ├── project-management/       # Project processes and templates
│   ├── reference/                # API docs and architecture
│   ├── sdlc/                     # Software development lifecycle
│   ├── sop/                      # Standard operating procedures
│   └── standards/                # Coding and quality standards
├── main.py                       # Application entry point
├── .kollabor/                    # Runtime data (created at startup)
│   ├── config.json              # User configuration
│   ├── logs/                    # Application logs
│   └── state.db                 # Persistent state
└── .github/scripts/              # Repository automation
```

Key directories:
- **`core/`**: Modular core functionality with clear separation of concerns
- **`plugins/`**: Dynamic plugin system with auto-discovery
- **`tests/`**: Comprehensive test coverage with multiple test types
- **`docs/`**: Extensive documentation following enterprise standards
- **`.kollabor/`**: Runtime configuration, logs, and state (created automatically)

## Development Guidelines

### Code Standards
- Follow PEP 8 with 88-character line length (Black formatter)
- Use double quotes for strings, single quotes for character literals
- All async functions should use proper `async`/`await` patterns
- Type hints required for all public functions and methods
- Comprehensive docstrings for classes and public methods

### Testing Strategy
- Unit tests in `tests/unit/` for individual components
- Integration tests in `tests/integration/` for cross-component functionality
- Visual tests in `tests/visual/` for terminal rendering
- Component tests (`test_*.py`) for specific modules
- Use unittest framework with descriptive test method names
- Test coverage includes LLM plugins, configuration, and plugin registry

### Hook Development
When creating hooks, consider:
- Hook priority using `HookPriority` enum (CRITICAL, HIGH, NORMAL, LOW)
- Error handling - hooks should not crash the application
- Performance - hooks are in the hot path for user interaction
- State management - avoid shared mutable state between hooks

## Key Features

Current implementation includes:
- **Modal System**: Full-screen modal overlays with widget support (dropdowns, checkboxes, sliders, text inputs)
- **Command System**: Extensible command parser and executor with menu rendering
- **Plugin System**: Dynamic plugin discovery with comprehensive SDK
- **Visual Effects**: Matrix rain effect and customizable color palettes
- **Status Display**: Multi-area status rendering with flexible view registry
- **Configuration**: Dot notation config system with plugin integration
- **Message Processing**: Advanced response parsing with thinking tag removal

## Current State

Recent development focused on:
- Enhanced input plugin architecture with modular design
- LLM service output formatting consistency
- Message display and error handling improvements
- Event bus system with specialized components
- Modal system with overlay rendering and widget integration
- Command system with menu and executor components

The codebase uses Python 3.12+ and follows async/await patterns throughout.