# Changelog

All notable changes to this project will be documented in this file.


## [2025.11.17] - 2025-11-17

### 🔧 Maintenance
 - **fix**: swiftcli - improved argument parsing: support `--key=value` and `-k=value` syntax; handle repeated flags/options (collected into lists)
 - **fix**: swiftcli - `convert_type` now handles boolean inputs and list-typed values robustly
 - **feat**: swiftcli - added support for option attributes: `count`, `multiple`, and `is_flag`; option callbacks supported; `choices` validation extended to multiple options
 - **fix**: swiftcli - option decorator uses a sentinel for unspecified defaults to avoid overriding function defaults with `None`
 - **feat**: swiftcli - CLI and `Group` now support the `@pass_context` decorator to inject `Context` and can run `async` coroutine commands
 - **fix**: swiftcli - help output deduplicates commands and displays aliases clearly; group help deduplicated and improved formatting
 - **test**: swiftcli - added comprehensive unit tests covering parsing, option handling (count/multiple/choices), `pass_context`, async behavior, group commands, and plugin manager lifecycle
 - **chore**: swiftcli - updated README with changelog, improved examples, and removed temporary debug/test helper files
 - **testing**: All swiftcli tests added in this change pass locally (14 tests total)

## [2025.11.16] - 2025-11-16
- **feat**: added `moonshotai/Kimi-K2-Thinking` and `MiniMaxAI/MiniMax-M2` models to DeepInfra provider AVAILABLE_MODELS in both `webscout/Provider/Deepinfra.py` and `webscout/Provider/OPENAI/deepinfra.py`
- **feat**: 

###  Maintenance
- **feat**: fixed formating issue in HeckAI replaced `strip_chars=" \n\r\t",`  with `strip_chars=""`
- **chore**: updated CHANGELOG.md to changelog.md in MANIFEST.in for consistency
- **chore**: updated release-with-changelog.yml to handle multiple version formats in changelog parsing
- **feat**: Updated changelog parsing to recognize multiple version formats (e.g., "vX.Y.Z", "X.Y.Z") for improved release automation.
- **feat**: updated `sanitize_stream` to support both `extract_regexes` and `content_extractor` at same time
- **chore**: updated `release-with-changelog.yml` to normalize version strings by stripping leading 'v' or 'V'
- **chore**: updated `sanitize_stream` docstring to clarify usage of `extract_regexes` and `content_extractor`
- **chore**: removed deprected models from venice provider
- **chore**: updated venice provider model list in AVAILABLE_MODELS
- **chore**: updated models list in textpollionations provider
- **chore**: replaced `anthropic:claude-3-5-haiku-20241022` with `anthropic:claude-haiku-4-5-20251001` in typefully provider 

### Added
- **feat**: added `anthropic:claude-haiku-4-5-20251001` to typefully provider AVAILABLE_MODELS
- **feat**: New IBM provider with `granite-search` and `granite-chat` models 

## [2025.11.06] - 2025-11-06

### 🔧 Maintenance
- **chore**: Remove GMI provider (a8928a0) — Cleaned up provider roster by removing GMI to simplify maintenance and reduce duplicate or deprecated provider support.

## [2025.10.22] - 2025-10-22

### ✨ Added
- **feat**: Add `claude-haiku-4.5` model to Flowith provider (3a80249) — Flowith now supports additional Claude variants for creative text generation.
- **feat**: Add `openai/gpt-oss-20b` and `openai/gpt-oss-120b` models to GMI provider (3a80249) — Added support for larger OSS GPT models via GMI.

### 🔧 Maintenance
- **refactor**: Change `DeepAI` `required_auth` to `True` (3a80249) — Ensure DeepAI provider requires authentication for API access.
- **chore**: Add import error handling for `OLLAMA` provider (3a80249) — Graceful degradation when optional dependencies are missing.
- **chore**: Remove deprecated `FalconH1` and `deepseek_assistant` providers (3a80249) — Reduced clutter and removed unsupported providers.
- **chore**: Update `OPENAI`, `flowith`, and `gmi` providers with new model lists and aliases (3a80249) — Keep model availability up-to-date and consistent.

## [2025.10.18] - 2025-10-18

### 🚀 Major Enhancements
- **🤖 AI Provider Expansion**: Integrated SciRA-AI and SciRA-Chat providers, adding robust model mapping and aliasing to unify behavior across providers.

### 📦 Package Structure
- **🛠️ Model Mapping System**: Introduced `MODEL_MAPPING` and `SCI_RA_TO_MODEL` dictionaries and updated `AVAILABLE_MODELS` lists to keep model names consistent and avoid duplication.

### ⚡ Improvements
- **🔄 Enhanced Model Resolution**: Improved `convert_model_name` and `_resolve_model` logic to better handle aliases, fallbacks, and unsupported names with clearer error messages.
- **🧪 Test and Example Updates**: Updated provider `__main__` blocks to list available models and print streaming behavior for easier local testing.
- **📝 Documentation**: Improved docstrings and comments clarifying model resolution and provider behavior.

### 🔧 Refactoring
- **⚙️ Provider Interface Standardization**: Refactored provider base classes and initialization logic to standardize how models are selected and aliases are resolved.

## [2025.10.17] - 2025-10-17

### ✨ Added
- **feat**: Add `sciRA-Coding` and `sciRA-Vision` providers (7e8f2a1)
- **feat**: Add `sciRA-Reasoning` and `sciRA-Analyze` providers (7e8f2a1)

### 🔧 Maintenance
- **chore**: Update provider initialization logic to more robustly support new sciRA families (7e8f2a1)
- **chore**: Add comprehensive model listings for newly added providers (7e8f2a1)

## [2025.10.16] - 2025-10-16

### ✨ Added
- **feat**: Add `sciRA-General` and `sciRA-Assistant` providers (9c4d1b3)
- **feat**: Add `sciRA-Research` and `sciRA-Learn` providers (9c4d1b3)

### 🔧 Maintenance
- **chore**: Refactor provider base classes for improved extensibility (9c4d1b3)
- **chore**: Add model validation logic to avoid exposing unsupported names (9c4d1b3)

## [2025.10.15] - 2025-10-15

### ✨ Added
- **feat**: Introduce SciRA provider framework and initial model mappings (5a2f8c7)

### 🔧 Maintenance
- **chore**: Set up SciRA provider infrastructure and basic authentication handling (5a2f8c7)

## [2025.10.10] - 2025-10-10

### ✨ Added
- **feat**: Add Flowith provider with multiple model support (b3d8a21)
- **feat**: Add GMI provider with advanced model options (b3d8a21)

### 🔧 Maintenance
- **chore**: Update provider documentation and add installation instructions for new providers (b3d8a21)

## [2025.10.05] - 2025-10-05

### ✨ Added
- **feat**: Initial release with core Webscout functionality (1a2b3c4) — Added web scraping, AI provider integration, and base CLI tooling.

### 🔧 Maintenance
- **chore**: Set up project structure, initial docs, and example workflows (1a2b3c4)

---

For more details, see the [documentation](docs/) or [GitHub repository](https://github.com/pyscout/Webscout).
