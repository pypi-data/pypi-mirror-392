# Changelog

All notable changes to OmniGen will be documented in this file.

## [0.1.17] - 2025-11-16

### Added
- **OpenRouter Provider Routing**: Full support for OpenRouter-specific provider routing parameters
  - `provider.only`: Restrict to specific providers (e.g., `["moonshotai/int4"]`)
  - `provider.order`: Prioritize providers in specific order
  - `provider.allow_fallbacks`: Control fallback behavior
  - `provider.require_parameters`: Only use providers supporting all parameters
  - `provider.data_collection`: Control data retention policies (`"allow"` or `"deny"`)
  - `provider.ignore`: Ignore specific providers
  - `provider.sort`: Sort by `"price"`, `"throughput"`, or `"latency"`
  - `provider.quantizations`: Filter by quantization levels (int4, int8, fp16, etc.)
  - `provider.zdr`: Zero data retention enforcement
  - `provider.max_price`: Set maximum price limits
  - `models`: Model routing with fallback support
  - `route`: Routing strategy configuration
  - `transforms`: Prompt transforms support

- **Direct Chat Endpoint Provider**: New provider for custom HTTP endpoints
  - Direct HTTP POST to any OpenAI-compatible endpoint
  - No OpenAI SDK dependency for API calls
  - Custom header support for authentication and tracking
  - Full error handling and retry logic
  - Token usage tracking
  - Tool calling support (if endpoint supports it)

### Changed
- OpenRouter provider now properly wraps OpenRouter-specific parameters in `extra_body` for OpenAI SDK compatibility
- Async OpenRouter provider updated with same `extra_body` handling

### Fixed
- OpenRouter provider parameters (like `provider.only`) now correctly passed to API
- Fixed: `Completions.create() got an unexpected keyword argument 'provider'` error

### Dependencies
- Added `requests>=2.31.0` for direct_chat_endpoint provider

## [0.1.16] - 2025-11-XX

### Fixed
- Fixed resume path bug with target_turns=0 from old checkpoints
- Recalculation of target_turns when resuming from buggy checkpoints

## Previous Versions
See git history for older versions.
