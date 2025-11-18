# Revenium Google AI Middleware - Examples

This directory contains working examples demonstrating how to use the Revenium middleware with Google AI services.

## Getting Started - Step by Step

### 1. Install Dependencies

```bash
# For Google AI SDK (Gemini Developer API)
pip install "revenium-middleware-google[genai]"

# For Vertex AI SDK (Google Cloud)
pip install "revenium-middleware-google[vertex]"

# For both SDKs
pip install "revenium-middleware-google[all]"
```

### 2. Environment Setup

Create a `.env` file or export environment variables:

**For Google AI SDK:**
```bash
export REVENIUM_METERING_API_KEY="your-revenium-api-key"
export GOOGLE_API_KEY="your-google-api-key"
```

**For Vertex AI SDK:**
```bash
export REVENIUM_METERING_API_KEY="your-revenium-api-key"
export GOOGLE_CLOUD_PROJECT="your-gcp-project-id"
export GOOGLE_CLOUD_LOCATION="us-central1"  # optional

# Authenticate with Google Cloud
gcloud auth application-default login
```

### 3. Run Examples

```bash
# Simple getting started examples
python examples/getting_started_google_ai.py
python examples/getting_started_vertex_ai.py

# Comprehensive test suite
python examples/simple_test.py --provider google-ai
python examples/simple_test.py --provider vertex-ai
```

---

## Available Examples

### `getting_started_google_ai.py` - Simple Google AI SDK Entry Point

The simplest possible example for Google AI SDK (Gemini Developer API).

**What it demonstrates:**
- Zero-config integration (just import the middleware)
- Single chat completion
- Automatic usage tracking

**Run it:**
```bash
python examples/getting_started_google_ai.py
```

---

### `getting_started_vertex_ai.py` - Simple Vertex AI SDK Entry Point

The simplest possible example for Vertex AI SDK (Google Cloud).

**What it demonstrates:**
- Zero-config integration
- Vertex AI initialization
- Single chat completion
- Automatic usage tracking

**Run it:**
```bash
python examples/getting_started_vertex_ai.py
```

---

### `simple_test.py` - Comprehensive Test Suite

Full-featured test suite with multiple scenarios and provider selection.

**What it demonstrates:**
- Provider selection (Google AI vs Vertex AI)
- Zero-config and enhanced tracking examples
- Environment validation
- Error handling and debugging
- Command-line arguments

**Run it:**
```bash
# Test Google AI SDK
python examples/simple_test.py --provider google-ai

# Test Vertex AI SDK
python examples/simple_test.py --provider vertex-ai

# Show help
python examples/simple_test.py --help
```

---

### `simple_streaming_test.py` - Streaming Responses

Demonstrates streaming responses with real-time token counting.

**What it demonstrates:**
- Streaming chat completions
- Time-to-first-token tracking
- Streaming with both SDKs
- Metadata tracking with streaming

**Run it:**
```bash
python examples/simple_streaming_test.py --provider google-ai
python examples/simple_streaming_test.py --provider vertex-ai
```

---

### `simple_embeddings_test.py` - Text Embeddings

Demonstrates text embeddings with token counting.

**What it demonstrates:**
- Text embeddings generation
- Token counting for embeddings (Vertex AI)
- Batch embeddings processing
- SDK differences

**Run it:**
```bash
python examples/simple_embeddings_test.py --provider google-ai
python examples/simple_embeddings_test.py --provider vertex-ai
```

**Note:** Google AI SDK embeddings don't return token counts due to API limitations. Use Vertex AI SDK for full token tracking.

---

## Requirements

- Python 3.9+
- Revenium API key (sign up at [revenium.io](https://revenium.io))
- Google AI API key (for Google AI SDK) or Google Cloud project (for Vertex AI SDK)

---

## Troubleshooting

### Import Errors

```bash
# Ensure correct dependencies are installed
pip install "revenium-middleware-google[all]"
```

### Environment Variables Not Set

```bash
# Verify environment variables
echo $REVENIUM_METERING_API_KEY
echo $GOOGLE_API_KEY
echo $GOOGLE_CLOUD_PROJECT
```

### Vertex AI Authentication Errors

```bash
# Authenticate with Google Cloud
gcloud auth application-default login

# Verify authentication
gcloud auth application-default print-access-token
```

### Debug Mode

Enable debug logging to see detailed middleware activity:

```bash
export REVENIUM_LOG_LEVEL=DEBUG
python examples/getting_started_google_ai.py
```

---

## Additional Resources

- **Main Documentation:** [README.md](../README.md)
- **Revenium API:** [API Documentation](https://revenium.readme.io/reference/meter_ai_completion)
- **Google AI SDK:** [Google AI Python SDK](https://ai.google.dev/gemini-api/docs/quickstart?lang=python)
- **Vertex AI SDK:** [Vertex AI Python SDK](https://cloud.google.com/vertex-ai/docs/python-sdk/use-vertex-ai-python-sdk)
