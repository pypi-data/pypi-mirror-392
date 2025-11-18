# Revenium Middleware for Google AI (Python)

[![PyPI version](https://img.shields.io/pypi/v/revenium-middleware-google.svg)](https://pypi.org/project/revenium-middleware-google/)
[![Python Versions](https://img.shields.io/pypi/pyversions/revenium-middleware-google.svg)](https://pypi.org/project/revenium-middleware-google/)
[![Documentation](https://img.shields.io/badge/docs-revenium.io-blue)](https://docs.revenium.io)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[//]: # ([![Build Status]&#40;https://github.com/revenium/revenium-middleware-google/actions/workflows/ci.yml/badge.svg&#41;]&#40;https://github.com/revenium/revenium-middleware-google/actions&#41;)

A middleware library for metering and monitoring Google AI services usage in Python applications. Supports both Google AI SDK (Gemini Developer API) and Vertex AI SDK with flexible optional dependencies.

## Features

- **Precise Usage Tracking**: Monitor tokens, costs, and request counts for Google AI services
- **Seamless Integration**: Drop-in middleware that works with minimal code changes
- **Dual SDK Support**: Choose between Google AI SDK or Vertex AI SDK based on your needs
- **Optional Dependencies**: Install only the SDK components you need
- **Streaming Support**: Full support for streaming responses (both SDKs)
- **Enhanced Token Counting**: Complete token tracking including embeddings (Vertex AI)
- **Flexible Configuration**: Customize metering behavior to suit your application needs

## What's Supported

| Feature | Google AI SDK | Vertex AI SDK |
|---------|---------------|---------------|
| **Chat Completion** | Full support | Full support |
| **Streaming** | Full support | Full support |
| **Text Embeddings** | Basic support* | Full support |
| **Token Metering** | Chat/Streaming | All operations |
| **Metadata Tracking** | Full support | Full support |
| **Setup Complexity** | Simple (API key) | Moderate (GCP project) |

**Note**: *Google AI SDK embeddings don't return token counts due to API limitations, but requests are still tracked.

## Installation

Choose the SDK variant that best fits your needs:

```bash
# Google AI SDK only (Gemini Developer API)
pip install "revenium-middleware-google[genai]"

# Vertex AI SDK only (recommended for production)
pip install "revenium-middleware-google[vertex]"

# Both SDKs (maximum flexibility)
pip install "revenium-middleware-google[all]"
```

### Which SDK Should I Choose?

| Use Case | Recommended SDK | Why |
|----------|----------------|-----|
| **Quick prototyping** | Google AI SDK | Simple API key setup, but does NOT support token counts on embeddings |
| **Production applications** | Vertex AI SDK | Full token counting, enterprise features |
| **Embeddings-heavy workloads** | Vertex AI SDK | Complete token tracking for embeddings |
| **Enterprise/GCP environments** | Vertex AI SDK | Advanced Google Cloud integration |
| **Simple chat applications** | Either SDK | Both provide full chat support |

**Recommendation**: Use Vertex AI SDK for production applications that need comprehensive token counting and advanced features.

## Quick Start

### 1. Install the Package

```bash
# Install with both SDKs (recommended)
pip install "revenium-middleware-google[all]"
```

### 2. Set Environment Variables

```bash
# Required for all examples
export REVENIUM_METERING_API_KEY=your_revenium_key

# For Google AI SDK (Gemini Developer API)
export GOOGLE_API_KEY=your_google_api_key

# For Vertex AI SDK (Google Cloud)
export GOOGLE_CLOUD_PROJECT=your_project_id
gcloud auth application-default login
```

### 3. Run Your First Example

```bash
# For Google AI SDK
python examples/getting_started_google_ai.py

# For Vertex AI SDK
python examples/getting_started_vertex_ai.py
```

The middleware automatically tracks your Google AI usage and sends data to Revenium.

**For complete examples and usage patterns, see [`examples/README.md`](https://github.com/revenium/revenium-middleware-google-python/blob/main/examples/README.md).**

---

## Usage

Simply import the middleware and your Google AI calls will be metered automatically:

```python
import revenium_middleware_google
from google import genai

client = genai.Client()
response = client.models.generate_content(
    model="gemini-2.0-flash-001",
    contents="Hello! Introduce yourself in one sentence."
)
print(response.text)
```

The middleware automatically meters all Google AI and Vertex AI calls. For production use, add metadata tracking to associate usage with organizations, users, or features.

**For complete examples, see:**
- [`examples/getting_started_google_ai.py`](https://github.com/revenium/revenium-middleware-google-python/blob/main/examples/getting_started_google_ai.py) - Minimal Google AI SDK example with metadata fields documented
- [`examples/getting_started_vertex_ai.py`](https://github.com/revenium/revenium-middleware-google-python/blob/main/examples/getting_started_vertex_ai.py) - Minimal Vertex AI SDK example
- [`examples/simple_test.py`](https://github.com/revenium/revenium-middleware-google-python/blob/main/examples/simple_test.py) - Comprehensive test suite with metadata tracking
- [`examples/simple_streaming_test.py`](https://github.com/revenium/revenium-middleware-google-python/blob/main/examples/simple_streaming_test.py) - Complete streaming examples
- [`examples/simple_embeddings_test.py`](https://github.com/revenium/revenium-middleware-google-python/blob/main/examples/simple_embeddings_test.py) - Text embeddings examples
- [`examples/README.md`](https://github.com/revenium/revenium-middleware-google-python/blob/main/examples/README.md) - Complete examples documentation

## SDK-Specific Integration

### Automatic Provider Detection

The middleware automatically chooses between Google AI SDK and Vertex AI SDK:

| Detection Method | When Used | Example |
|-----------------|-----------|---------|
| **Google AI SDK** | When `google.genai` is imported and used | `from google import genai` |
| **Vertex AI SDK** | When `vertexai` is imported and used | `import vertexai` |
| **Dual Support** | When both SDKs are available | Automatic routing based on usage |

**Key Point**: Both SDKs report as "Google" provider for unified analytics and consistent reporting.

**See [`examples/getting_started_google_ai.py`](https://github.com/revenium/revenium-middleware-google-python/blob/main/examples/getting_started_google_ai.py)** and **[`examples/getting_started_vertex_ai.py`](https://github.com/revenium/revenium-middleware-google-python/blob/main/examples/getting_started_vertex_ai.py)** for complete working examples of both SDKs.

## Configuration

Configure the middleware using environment variables:

### Required Environment Variables

#### For Google AI SDK (Gemini Developer API)
```bash
# Required
export REVENIUM_METERING_API_KEY=your_revenium_api_key
export GOOGLE_API_KEY=your_google_api_key

# Optional: Revenium base URL (defaults to production)
export REVENIUM_METERING_BASE_URL=https://api.revenium.ai
export REVENIUM_LOG_LEVEL=INFO
```

#### For Vertex AI SDK (Google Cloud)
```bash
# Required
export REVENIUM_METERING_API_KEY=your_revenium_api_key
export GOOGLE_CLOUD_PROJECT=your_gcp_project_id

# Recommended
export GOOGLE_CLOUD_LOCATION=us-central1

# Google Cloud Authentication (choose one)
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
# OR use: gcloud auth application-default login

# Optional: Revenium base URL (defaults to production)
export REVENIUM_METERING_BASE_URL=https://api.revenium.ai
export REVENIUM_LOG_LEVEL=INFO
```

### Using .env File

Create a `.env` file in your project root:

```bash
# Required for all configurations
REVENIUM_METERING_API_KEY=your_revenium_api_key

# For Google AI SDK
GOOGLE_API_KEY=your_google_api_key

# For Vertex AI SDK
GOOGLE_CLOUD_PROJECT=your_gcp_project_id
GOOGLE_CLOUD_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json

# Optional settings
REVENIUM_METERING_BASE_URL=https://api.revenium.ai
REVENIUM_LOG_LEVEL=DEBUG
```

### Google Cloud Authentication

The Vertex AI SDK uses the standard Google Cloud authentication chain:

1. **Service Account Key File** (recommended for production):
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account-key.json
   ```

2. **Application Default Credentials** (for development):
   ```bash
   gcloud auth application-default login
   ```

3. **Compute Engine/GKE Service Account** (automatic in GCP environments)

4. **Environment Variables**:
   ```bash
   export GOOGLE_APPLICATION_CREDENTIALS=/path/to/key.json
   ```

Ensure your credentials have the following permissions:
- `aiplatform.endpoints.predict`
- `ml.projects.predict` (for some models)

### Configuration Variables

| Variable | Required | SDK | Description |
|----------|----------|-----|-------------|
| `REVENIUM_METERING_API_KEY` | Yes | Both | Your Revenium API key |
| `GOOGLE_API_KEY` | Yes | Google AI | Google AI API key (Gemini Developer API) |
| `GOOGLE_CLOUD_PROJECT` | Yes | Vertex AI | Google Cloud project ID |
| `GOOGLE_CLOUD_LOCATION` | No | Vertex AI | Google Cloud location (default: `us-central1`) |
| `GOOGLE_APPLICATION_CREDENTIALS` | No | Vertex AI | Path to service account key file |
| `REVENIUM_METERING_BASE_URL` | No | Both | Revenium API base URL |
| `REVENIUM_LOG_LEVEL` | No | Both | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

## Streaming Support

The middleware supports streaming responses for both SDKs with automatic usage tracking.

**For complete streaming examples, see:**

- [`examples/simple_streaming_test.py`](https://github.com/revenium/revenium-middleware-google-python/blob/main/examples/simple_streaming_test.py) - Full streaming examples for both SDKs

**Key features:**

- Real-time token counting
- Time-to-first-token tracking
- Automatic usage logging when stream completes
- Works with both Google AI SDK and Vertex AI SDK

## Text Embeddings

The middleware supports text embeddings with both SDKs. **Note:** Google AI SDK embeddings don't return token counts due to API limitations. Use Vertex AI SDK for full token tracking.

**For complete embeddings examples, see:**

- [`examples/simple_embeddings_test.py`](https://github.com/revenium/revenium-middleware-google-python/blob/main/examples/simple_embeddings_test.py) - Full embeddings examples for both SDKs

**SDK Comparison:**

| Feature | Google AI SDK | Vertex AI SDK |
|---------|---------------|---------------|
| **Embeddings Generation** | Full support | Full support |
| **Token Counting** | No tokens (API limitation) | Full token counting |
| **Usage Tracking** | Requests tracked | Full tracking |

## Metadata Fields

Add business context to track usage by organization, user, task type, or custom fields. Pass a `usage_metadata` dictionary with any of these optional fields:

| Field | Description | Use Case |
|-------|-------------|----------|
| `trace_id` | Unique identifier for session or conversation tracking | Link multiple API calls together for debugging, user session analytics, or distributed tracing across services |
| `task_type` | Type of AI task being performed | Categorize usage by workload (e.g., "chat", "code-generation", "doc-summary") for cost analysis and optimization |
| `subscriber.id` | Unique user identifier | Track individual user consumption for billing, rate limiting, or user analytics |
| `subscriber.email` | User email address | Identify users for support, compliance, or usage reports |
| `subscriber.credential.name` | Authentication credential name | Track which API key or service account made the request |
| `subscriber.credential.value` | Authentication credential value | Associate usage with specific credentials for security auditing |
| `organization_id` | Organization or company identifier | Multi-tenant cost allocation, usage quotas per organization |
| `subscription_id` | Subscription plan identifier | Track usage against subscription limits, identify plan upgrade opportunities |
| `product_id` | Your product or feature identifier | Attribute AI costs to specific features in your application (e.g., "chatbot", "email-assistant") |
| `agent` | AI agent or bot identifier | Distinguish between multiple AI agents or automation workflows in your system |
| `response_quality_score` | Custom quality rating (0.0-1.0) | Track user satisfaction or automated quality metrics for model performance analysis |

**Resources:**
- [API Reference](https://revenium.readme.io/reference/meter_ai_completion) - Complete metadata field documentation

## Testing Your Setup

The middleware includes comprehensive test scripts to verify your configuration and ensure everything is working correctly. Each test script supports both Google AI SDK and Vertex AI SDK with intelligent provider selection.

### Quick Test Commands

```bash
# Test Google AI SDK (default)
python examples/simple_test.py

# Test Vertex AI SDK
python examples/simple_test.py --provider vertex-ai

# Test streaming functionality
python examples/simple_streaming_test.py --provider google-ai
python examples/simple_streaming_test.py --provider vertex-ai

# Test embeddings (Vertex AI recommended for full token counting)
python examples/simple_embeddings_test.py --provider vertex-ai

# Get help for any test script
python examples/simple_test.py --help
```

### Environment Setup for Testing

#### For Google AI SDK Testing
```bash
export GOOGLE_API_KEY=your_google_api_key
export REVENIUM_METERING_API_KEY=your_revenium_key

# Run the test
python examples/simple_test.py --provider google-ai
```

#### For Vertex AI SDK Testing
```bash
export GOOGLE_CLOUD_PROJECT=your_project_id
export GOOGLE_CLOUD_LOCATION=us-central1  # optional, defaults to us-central1
export REVENIUM_METERING_API_KEY=your_revenium_key

# Ensure Google Cloud authentication
gcloud auth application-default login

# Run the test
python examples/simple_test.py --provider vertex-ai
```

### Expected Test Results

**Successful Test Output:**
```
Revenium Google AI Middleware - Test Suite
Testing: GOOGLE AI SDK
======================================================================
Google API Key: AIzaSyB8oD...
Revenium Key: hak_6PVMBR...

GOOGLE AI SDK EXAMPLES
======================================================================
Google AI SDK detected

Google AI SDK - Basic Example
==================================================
Response: According to the supercomputer Deep Thought...
Tokens: 12 input + 421 output = 433 total
Zero-config integration successful!

Google AI SDK - Enhanced Tracking Example
==================================================
Response: Okay, I'm ready to analyze the quarterly report...
Enhanced metadata tracking enabled!

======================================================================
TEST RESULTS SUMMARY
======================================================================
PASS: google_ai_basic
PASS: google_ai_enhanced

Overall: 2/2 tests passed
Success! Check your Revenium dashboard for usage data
```

**Failed Test Output:**
```
Missing required environment variable for Google AI SDK
   GOOGLE_API_KEY not found

Setup Instructions:
   1. Get your API key from: https://aistudio.google.com/app/apikey
   2. Set the environment variable:
      export GOOGLE_API_KEY=your_google_api_key
   3. Run the test again
```

### Test Script Features

- **Intelligent Provider Selection**: Automatically tests only the selected provider
- **Environment Validation**: Checks for required environment variables before testing
- **Clear Error Messages**: Provides specific setup instructions when configuration is missing
- **Comprehensive Coverage**: Tests basic functionality, enhanced metadata, streaming, and embeddings
- **User-Friendly Output**: Color-coded results with clear success/failure indicators

### Available Test Scripts

| Script | Purpose | Key Features |
|--------|---------|--------------|
| `simple_test.py` | Basic functionality testing | Chat completion, metadata tracking |
| `simple_streaming_test.py` | Streaming functionality | Real-time token counting, streaming responses |
| `simple_embeddings_test.py` | Embeddings testing | Text embeddings, token counting (Vertex AI) |

All test scripts support the `--provider` flag to specify which SDK to test.

## Troubleshooting

### Common Issues

| Issue | Solution |
|-------|----------|
| **"No module named 'google.genai'"** | Install with Google AI support: `pip install "revenium-middleware-google[genai]"` |
| **"No module named 'vertexai'"** | Install with Vertex AI support: `pip install "revenium-middleware-google[vertex]"` |
| **Vertex AI authentication errors** | Verify Google Cloud credentials: `gcloud auth application-default login` |
| **"Project not found" errors** | Ensure `GOOGLE_CLOUD_PROJECT` is set correctly |
| **Embeddings showing 0 tokens** | Expected with Google AI SDK; use Vertex AI for full token counting |
| **Requests not being tracked** | Ensure middleware is imported before Google AI/Vertex AI SDKs |

### Debug Mode

Enable debug logging to see provider detection and routing decisions:

```bash
export REVENIUM_LOG_LEVEL=DEBUG
python your_script.py
```

### Force Specific SDK

To ensure only one SDK is used:

```bash
# Use only Google AI SDK
pip install "revenium-middleware-google[genai]"

# Use only Vertex AI SDK
pip install "revenium-middleware-google[vertex]"
```

### Google AI SDK Troubleshooting

**Middleware not tracking requests:**
- Ensure middleware is imported before Google AI SDK
- Check that environment variables are loaded correctly
- Verify your `REVENIUM_METERING_API_KEY` is correct

**Embeddings showing 0 tokens:**
- This is expected due to Google AI SDK limitations
- Model name and metadata are still tracked correctly
- Chat and streaming operations provide full token data

### Vertex AI SDK Troubleshooting

**Authentication issues:**
- Verify Google Cloud credentials: `gcloud auth list`
- Check project access: `gcloud projects describe YOUR_PROJECT_ID`
- Ensure service account has required permissions

**Model not available errors:**
- Check if models are available in your region
- Verify Vertex AI API is enabled in your project
- Try a different model or region

## Logging

This module uses Python's standard logging system. You can control the log level by setting the `REVENIUM_LOG_LEVEL` environment variable:

```bash
# Enable debug logging
export REVENIUM_LOG_LEVEL=DEBUG

# Or when running your script
REVENIUM_LOG_LEVEL=DEBUG python your_script.py
```

Available log levels:
- `DEBUG`: Detailed debugging information
- `INFO`: General information (default)
- `WARNING`: Warning messages only
- `ERROR`: Error messages only
- `CRITICAL`: Critical error messages only

## Compatibility

- Python 3.8+
- Google AI SDK (`google-genai>=0.1.0`) or Vertex AI SDK (`google-cloud-aiplatform>=1.0.0`)
- Google Cloud Project (for Vertex AI SDK)

## Supported Models

The middleware works with all Google AI models available through both SDKs:

### Google AI SDK Models
- `gemini-2.0-flash-001`
- `gemini-2.0-flash-lite-001`
- `gemini-1.5-pro`
- `gemini-1.5-flash`
- `text-embedding-004`
- All other Gemini Developer API models

### Vertex AI SDK Models
- `gemini-2.0-flash-001`
- `gemini-2.0-flash-lite-001`
- `gemini-1.5-pro`
- `gemini-1.5-flash`
- `text-embedding-004`
- All other Vertex AI Gemini models

## Documentation

For detailed documentation, visit [docs.revenium.io](https://docs.revenium.io)

## Contributing

See [CONTRIBUTING.md](https://github.com/revenium/revenium-middleware-google-python/blob/main/CONTRIBUTING.md)

## Code of Conduct

See [CODE_OF_CONDUCT.md](https://github.com/revenium/revenium-middleware-google-python/blob/main/CODE_OF_CONDUCT.md)

## Security

See [SECURITY.md](https://github.com/revenium/revenium-middleware-google-python/blob/main/SECURITY.md)

## License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/revenium/revenium-middleware-google-python/blob/main/LICENSE) file for details.

## Support

For issues, feature requests, or contributions:

- **Website**: [www.revenium.ai](https://www.revenium.ai)
- **GitHub Repository**: [revenium/revenium-middleware-google-python](https://github.com/revenium/revenium-middleware-google-python)
- **Issues**: [Report bugs or request features](https://github.com/revenium/revenium-middleware-google-python/issues)
- **Documentation**: [docs.revenium.io](https://docs.revenium.io)
- **Email**: support@revenium.io

---

**Built by Revenium**
