# Rebrandly OpenTelemetry SDK for Python

A comprehensive OpenTelemetry instrumentation SDK designed specifically for Rebrandly services, with built-in support for AWS Lambda functions and message processing.

## Overview

The Rebrandly OpenTelemetry SDK provides a unified interface for distributed tracing, metrics collection, and structured logging across Python applications. It offers automatic instrumentation for AWS Lambda functions, simplified span management, and seamless integration with OTLP-compatible backends.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Getting Started](#getting-started)
  - [Step 1: Install the Package](#step-1-install-the-package)
  - [Step 2: Configure Environment Variables](#step-2-configure-environment-variables)
  - [Step 3: Choose Your Integration Pattern](#step-3-choose-your-integration-pattern)
  - [Step 4: Verify It's Working](#step-4-verify-its-working)
  - [Step 5: Add Custom Instrumentation](#step-5-add-custom-instrumentation-optional)
- [Configuration](#configuration)
- [Core Components](#core-components)
- [Built-in Metrics](#built-in-metrics)
- [Tracing Features](#tracing-features)
- [Automatic Span Attributes](#automatic-span-attributes)
- [Logging Integration](#logging-integration)
- [AWS Lambda Support](#aws-lambda-support)
- [Performance Considerations](#performance-considerations)
- [Export Formats](#export-formats)
- [Thread Safety](#thread-safety)
- [Resource Attributes](#resource-attributes)
- [Error Handling](#error-handling)
- [Compatibility](#compatibility)
- [Best Practices](#best-practices)
  - [Span Management](#span-management)
  - [Error Handling](#error-handling-1)
  - [Metric Cardinality](#metric-cardinality)
  - [Lambda Functions](#lambda-functions)
  - [Context Propagation](#context-propagation)
  - [Logging](#logging)
  - [Configuration](#configuration-1)
  - [Performance](#performance)
  - [Security](#security)
  - [Testing](#testing)
  - [Async/Await Support](#asyncawait-support)
  - [Database Instrumentation](#database-instrumentation)
- [Examples](#examples)
  - [Lambda - Send SNS / SQS](#lambda---send-sns--sqs-message)
  - [Lambda - Receive SQS](#lambda-receive-sqs-message)
  - [Lambda - Receive SNS](#lambda-receive-sns-message-record-specific-event)
  - [Flask](#flask)
  - [FastAPI](#fastapi)
  - [PyMySQL Database Instrumentation](#pymysql-database-instrumentation)
- [Troubleshooting](#troubleshooting)
- [Testing](#testing-1)
- [License](#license)
- [Build and Deploy](#build-and-deploy)

## Installation

```bash
pip install rebrandly-otel
```

> **Note**: The SDK automatically initializes when you import it. No manual setup or initialization calls are needed - just `from rebrandly_otel import otel` and start using it!

### Dependencies

- `opentelemetry-api`
- `opentelemetry-sdk`
- `opentelemetry-exporter-otlp-proto-grpc`
- `opentelemetry-semantic-conventions`
- `psutil` (for system metrics)

## Quick Start

Get started with the Rebrandly OpenTelemetry SDK in under 5 minutes:

```python
from rebrandly_otel import otel, logger
from opentelemetry.trace import SpanKind, Status, StatusCode

# 1. SDK auto-initializes when imported
# Optional: Configure via environment variables (see Configuration section)

# 2. Create a traced operation using context manager
def process_order(order_id):
    with otel.span("process-order", attributes={"order.id": order_id}) as span:
        logger.info(f"Processing order {order_id}")

        # Your business logic here
        save_to_database(order_id)

        # Exceptions are automatically recorded
        # No need to manually call span.end()

# 3. For AWS Lambda functions
from rebrandly_otel import lambda_handler

@lambda_handler(name="order-processor")
def handler(event, context):
    logger.info("Lambda invoked", extra={"event": event})
    order_id = event.get('orderId')
    process_order(order_id)
    return {'statusCode': 200, 'body': 'Success'}

# 4. For Flask applications
from flask import Flask
from rebrandly_otel import app_before_request, app_after_request, flask_error_handler

app = Flask(__name__)
app.before_request(app_before_request)
app.after_request(app_after_request)
app.register_error_handler(Exception, flask_error_handler)

@app.route('/orders/<order_id>')
def get_order(order_id):
    with otel.span("fetch-order"):
        logger.info(f"Fetching order {order_id}")
        # Your logic here
        return {"order_id": order_id, "status": "shipped"}
```

**Next Steps:**
- See [Getting Started](#getting-started) for detailed integration guide
- Check [Configuration](#configuration) to set up environment variables
- Explore [Examples](#examples) for framework-specific patterns (Flask, FastAPI, Lambda)

## Getting Started

### Step 1: Install the Package

```bash
pip install rebrandly-otel
```

### Step 2: Configure Environment Variables

Create a `.env` file or set environment variables:

```bash
# Required
export OTEL_SERVICE_NAME=my-service
export OTEL_SERVICE_VERSION=1.0.0

# Optional - for sending data to an OTLP collector
export OTEL_EXPORTER_OTLP_ENDPOINT=https://your-collector:4317

# Optional - for debugging locally
export OTEL_DEBUG=true
```

### Step 3: Choose Your Integration Pattern

#### For Flask Applications

```python
from flask import Flask
from rebrandly_otel import otel, logger, app_before_request, app_after_request, flask_error_handler

app = Flask(__name__)

# Register OTEL handlers - handles ALL telemetry automatically
app.before_request(app_before_request)
app.after_request(app_after_request)
app.register_error_handler(Exception, flask_error_handler)

# Your routes - no telemetry code needed!
@app.route('/api/users')
def get_users():
    logger.info("Fetching users")
    # Business logic only
    return {"users": []}

@app.route('/api/users/<user_id>')
def get_user(user_id):
    # Add custom spans when needed
    with otel.span("fetch-user-details"):
        logger.info(f"Fetching user {user_id}")
        # Your business logic
        return {"user_id": user_id, "name": "John Doe"}

if __name__ == '__main__':
    app.run(debug=True)
```

#### For FastAPI Applications

```python
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from rebrandly_otel import otel, logger, force_flush
from rebrandly_otel.fastapi_support import setup_fastapi, get_current_span

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application starting up")
    yield
    logger.info("Application shutting down")
    force_flush()

app = FastAPI(lifespan=lifespan)

# Setup OTEL integration - handles ALL telemetry automatically
setup_fastapi(otel, app)

# Your routes
@app.get("/api/users")
async def get_users():
    logger.info("Fetching users")
    return {"users": []}

@app.get("/api/users/{user_id}")
async def get_user(user_id: int, span=Depends(get_current_span)):
    # Add custom spans when needed
    with otel.span("fetch-user-details", attributes={"user.id": user_id}):
        logger.info(f"Fetching user {user_id}")
        # Your business logic
        return {"user_id": user_id, "name": "John Doe"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### For AWS Lambda Functions

```python
from rebrandly_otel import lambda_handler, logger, otel

@lambda_handler(name="user-processor")
def handler(event, context):
    logger.info("Processing event", extra={"event_type": event.get("eventType")})

    # Your business logic
    user_id = event.get('userId')

    # Add custom spans if needed
    with otel.span("process-user", attributes={"user.id": user_id}):
        result = process_user(user_id)

    return {
        'statusCode': 200,
        'body': result
    }

def process_user(user_id):
    logger.info(f"Processing user {user_id}")
    # Your business logic here
    return {"processed": True}
```

#### For Standalone Scripts

```python
from rebrandly_otel import otel, logger, force_flush, shutdown

def main():
    # Create traced operation
    with otel.span("main-operation"):
        logger.info("Starting operation")

        # Your business logic
        process_data()

        logger.info("Operation completed")

def process_data():
    with otel.span("process-data"):
        # Nested spans are automatically linked
        logger.info("Processing data")
        # Your logic here

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Operation failed: {e}", exc_info=True)
    finally:
        # Ensure telemetry is flushed before exit
        force_flush(timeout_millis=5000)
        shutdown()
```

### Step 4: Verify It's Working

#### Local Debugging

Set `OTEL_DEBUG=true` to see telemetry output in your console:

```bash
OTEL_DEBUG=true python app.py
```

You should see trace and metric data logged to the console.

#### Production Setup

Configure `OTEL_EXPORTER_OTLP_ENDPOINT` to point to your OpenTelemetry Collector or backend:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=https://your-collector.example.com:4317
export OTEL_EXPORTER_OTLP_HEADERS="x-api-key=your-api-key"
```

Common backends:
- **Honeycomb**: `https://api.honeycomb.io:443`
- **Lightstep**: `https://ingest.lightstep.com:443`
- **Jaeger**: `http://jaeger-collector:4317`
- **Self-hosted Collector**: `http://localhost:4317`

### Step 5: Add Custom Instrumentation (Optional)

Add custom spans, metrics, and logs as needed:

```python
from rebrandly_otel import otel, logger, meter
from opentelemetry.trace import Status, StatusCode

# Custom span with attributes
with otel.span("custom-operation", attributes={"user.id": user_id}) as span:
    # Add events to the span
    span.add_event("processing_started", {"timestamp": datetime.now().isoformat()})

    # Your code
    result = do_work()

    # Add more attributes dynamically
    span.set_attribute("result.count", len(result))

# Custom metric
order_counter = meter.meter.create_counter(
    name="orders.created",
    description="Number of orders created",
    unit="1"
)
order_counter.add(1, {"order.type": "standard", "region": "us-east-1"})

# Custom histogram for measuring durations
duration_histogram = meter.meter.create_histogram(
    name="order.processing.duration",
    description="Order processing duration",
    unit="ms"
)
duration_histogram.record(123.45, {"order.type": "standard"})

# Structured logging with trace correlation
logger.info("Order processed", extra={
    "order_id": 12345,
    "user_id": 67890,
    "amount": 99.99
})
```

## Configuration

The SDK is configured through environment variables:

| Variable                           | Description | Default                         |
|------------------------------------|-------------|---------------------------------|
| `OTEL_SERVICE_NAME`                | Service identifier | `default-service-python`        |
| `OTEL_SERVICE_VERSION`             | Service version | `1.0.0`                         |
| `OTEL_SERVICE_APPLICATION`         | Application namespace (groups multiple services under one application) | Fallback to `OTEL_SERVICE_NAME` |
| `OTEL_EXPORTER_OTLP_ENDPOINT`      | OTLP collector endpoint | `None`                          |
| `OTEL_DEBUG`                       | Enable console debugging | `false`                         |
| `OTEL_CAPTURE_REQUEST_BODY`        | Enable HTTP request body capture for Flask and FastAPI (default: true). Set to `false` to disable. Only captures JSON content with automatic sensitive data redaction. | `true`                          |
| `OTEL_SPAN_ATTRIBUTES`             | Attributes automatically added to all spans (format: `key1=value1,key2=value2`) | `None`                          |
| `BATCH_EXPORT_TIME_MILLIS`         | Batch export interval | `100`                           |
| `ENV` or `ENVIRONMENT` or `NODE_ENV`       | Deployment environment | `local`                         |

## Core Components

### RebrandlyOTEL Class

The main entry point for all telemetry operations. Implements a singleton pattern to ensure consistent instrumentation across your application.

#### Properties

- **`tracer`**: Returns the `RebrandlyTracer` instance for distributed tracing
- **`meter`**: Returns the `RebrandlyMeter` instance for metrics collection
- **`logger`**: Returns the configured Python logger with OpenTelemetry integration

#### Initialization

The SDK auto-initializes as soon as you embed it.

### Key Methods

#### `span(name, attributes=None, kind=SpanKind.INTERNAL, message=None)`

Context manager for creating traced spans with automatic error handling and status management.

#### `lambda_handler(name=None, attributes=None, kind=SpanKind.CONSUMER, auto_flush=True, skip_aws_link=True)`

Decorator for AWS Lambda functions with automatic instrumentation, metrics collection, and telemetry flushing.

#### `aws_message_handler(name=None, attributes=None, kind=SpanKind.CONSUMER, auto_flush=True)`

Decorator for processing individual AWS messages (SQS/SNS) with context propagation.

#### `aws_message_span(name, message=None, attributes=None, kind=SpanKind.CONSUMER)`

Context manager for creating spans from AWS messages with automatic context extraction.

#### `force_flush(start_datetime=None, timeout_millis=1000)`

Forces all pending telemetry data to be exported. Critical for serverless environments.

#### `shutdown()`

Gracefully shuts down all OpenTelemetry components.

## Built-in Metrics

The SDK automatically registers and tracks the following metrics:

### Standard Metrics

- **`cpu_usage_percentage`** (Gauge): CPU utilization percentage
- **`memory_usage_bytes`** (Gauge): Memory usage in bytes


### Custom Metrics

You can create the custom metrics you need using the default open telemetry metrics

```python
from src.rebrandly_otel import meter

sqs_counter = meter.meter.create_counter(
    name="sqs_sender_counter",
    description="Number of messages sent",
    unit="1"
)
sqs_counter.add(1)
```

## Tracing Features

### Automatic Context Propagation

The SDK automatically extracts and propagates trace context from:
- AWS SQS message attributes
- AWS SNS message attributes
- HTTP headers
- Custom carriers

### Span Attributes

Lambda spans automatically include:
- `faas.trigger`: Detected trigger type (sqs, sns, api_gateway, etc.)
- `faas.execution`: AWS request ID
- `faas.id`: Function ARN
- `cloud.provider`: Always "aws" for Lambda
- `cloud.platform`: Always "aws_lambda" for Lambda

## Automatic Span Attributes

The SDK supports automatically adding custom attributes to all spans via the `OTEL_SPAN_ATTRIBUTES` environment variable. This is useful for adding metadata that applies to all telemetry in a service, such as team ownership, deployment environment, or version information.

### Configuration

Set the `OTEL_SPAN_ATTRIBUTES` environment variable with a comma-separated list of key-value pairs:

```bash
export OTEL_SPAN_ATTRIBUTES="team=backend,environment=production,version=1.2.3"
```

### Behavior

- **Universal Application**: Attributes are added to ALL spans, including:
  - Manually created spans (`tracer.start_span()`, `tracer.start_as_current_span()`)
  - Lambda handler spans (`@lambda_handler`)
  - AWS message handler spans (`@aws_message_handler`)
  - Flask/FastAPI middleware spans
  - Auto-instrumented spans (database queries, HTTP requests, etc.)

- **Format**: Same as `OTEL_RESOURCE_ATTRIBUTES` - comma-separated `key=value` pairs
- **Value Handling**: Supports values containing `=` characters (e.g., URLs)
- **Whitespace**: Leading/trailing whitespace is automatically trimmed

### Example

```python
import os

# Set environment variable
os.environ['OTEL_SPAN_ATTRIBUTES'] = "team=backend,service.owner=platform-team,deployment.region=us-east-1"

# Initialize SDK
from rebrandly_otel import otel, logger

# Create any span - attributes are added automatically
with otel.span('my-operation'):
    logger.info('Processing request')
    # The span will include:
    # - team: "backend"
    # - service.owner: "platform-team"
    # - deployment.region: "us-east-1"
    # ... plus any other attributes you set manually
```

### Use Cases

- **Team/Ownership Tagging**: `team=backend,owner=john@example.com`
- **Environment Metadata**: `environment=production,region=us-east-1,availability_zone=us-east-1a`
- **Version Tracking**: `version=1.2.3,build=12345,commit=abc123def`
- **Cost Attribution**: `cost_center=engineering,project=customer-api`
- **Multi-Tenancy**: `tenant=acme-corp,customer_tier=enterprise`

### Difference from OTEL_RESOURCE_ATTRIBUTES

- **OTEL_RESOURCE_ATTRIBUTES**: Service-level metadata (set once, applies to the entire service instance)
- **OTEL_SPAN_ATTRIBUTES**: Span-level metadata (added to each individual span at creation time)

Both use the same format but serve different purposes in the OpenTelemetry data model.

### Exception Handling

Spans automatically capture exceptions with:
- Full exception details and stack traces
- Automatic status code setting
- Exception events in the span timeline

## Logging Integration

The SDK integrates with Python's standard logging module:

```python
from rebrandly_otel import logger

# Use as a standard Python logger
logger.info("Processing started", extra={"request_id": "123"})
logger.error("Processing failed", exc_info=True)
```

Features:
- Automatic trace context injection
- Structured logging support
- Console and OTLP export
- Log level configuration via environment

## AWS Lambda Support

### Trigger Detection

Automatically detects and labels Lambda triggers:
- API Gateway (v1 and v2)
- SQS
- SNS
- S3
- Kinesis
- DynamoDB
- EventBridge
- Batch

### Automatic Metrics

For Lambda functions, the SDK automatically captures:
- Memory usage
- CPU utilization

### Context Extraction

Automatically extracts trace context from:
- SQS MessageAttributes
- SNS MessageAttributes (including nested format)
- Custom message attributes

## Performance Considerations

### Batch Processing

The SDK uses batch processing to optimize network usage and reduce overhead:

```python
import os

# Configure batch export interval (milliseconds)
os.environ['BATCH_EXPORT_TIME_MILLIS'] = '100'  # Default: 100ms

# Faster flushing for Lambda (reduce cold start impact)
os.environ['BATCH_EXPORT_TIME_MILLIS'] = '50'   # Flush every 50ms

# Slower flushing for high-throughput apps (better batching)
os.environ['BATCH_EXPORT_TIME_MILLIS'] = '200'  # Flush every 200ms
```

**Trade-offs:**
- **Lower values (50ms)**: Faster data delivery, higher network overhead, better for serverless
- **Higher values (200ms)**: Better batching, lower overhead, risk of data loss on crashes

### Lambda Optimization

For AWS Lambda functions, the SDK is specifically optimized:

**Cold Start Impact**: < 50ms
- Lazy initialization of exporters
- Minimal import overhead
- Efficient resource allocation

**Memory Usage**: ~20-30 MB additional
- Efficient span buffering
- Automatic cleanup on function freeze
- No memory leaks in long-running containers

**Best Practices for Lambda**:
```python
from rebrandly_otel import lambda_handler, force_flush

@lambda_handler(name="my-function", auto_flush=True)
def handler(event, context):
    # auto_flush=True ensures telemetry is exported
    # Add 2-3 seconds to timeout for flush buffer
    return process_event(event)

# For manual control
@lambda_handler(name="my-function", auto_flush=False)
def handler(event, context):
    result = process_event(event)
    force_flush(timeout_millis=2000)  # Explicit flush with 2s timeout
    return result
```

### Sampling Strategies

For high-traffic applications, implement sampling to reduce overhead:

```python
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatioBased, ALWAYS_ON

# Sample 10% of traces
sampler = ParentBasedTraceIdRatioBased(0.1)

# Use ALWAYS_ON for low-traffic or critical services
sampler = ALWAYS_ON
```

### Metric Cardinality Management

Avoid high-cardinality attributes that create too many metric series:

```python
from rebrandly_otel import meter

# ❌ Bad: Creates millions of unique metric series
order_counter = meter.meter.create_counter("orders.processed")
order_counter.add(1, {"user_id": "12345", "order_id": "98765"})  # Too many combinations!

# ✅ Good: Limited cardinality
order_counter = meter.meter.create_counter("orders.processed")
order_counter.add(1, {
    "order.type": "standard",  # Only a few types
    "region": "us-east-1",     # Limited regions
    "tier": "premium"           # Few tier values
})
```

**Cardinality Guidelines:**
- Keep attribute combinations under 1000 per metric
- Use aggregations in your application layer for high-cardinality data
- Monitor metric series count in your backend

### Span Attributes Best Practices

Optimize span attributes for performance and cost:

```python
from rebrandly_otel import otel

# ✅ Good: Reasonable attribute size
with otel.span("process-order", attributes={
    "order.id": "12345",
    "user.id": "67890",
    "order.total": 99.99
}) as span:
    process_order()

# ❌ Bad: Large payloads in attributes
with otel.span("process-order", attributes={
    "order.full_details": json.dumps(order),  # Could be huge!
    "request.body": request_body               # Potentially large
}) as span:
    process_order()
```

**Guidelines:**
- Keep individual attributes under 1KB
- Avoid storing full payloads in attributes
- Use events for detailed debugging data
- Leverage `OTEL_CAPTURE_REQUEST_BODY=false` to disable body capture

### Database Query Optimization

Minimize overhead from database instrumentation:

```python
from rebrandly_otel import instrument_pymysql

# Configure slow query threshold to reduce span volume
connection = instrument_pymysql(otel, connection, options={
    'slow_query_threshold_ms': 1000,   # Only flag queries > 1s
    'capture_bindings': False          # Disable parameter capture (faster)
})
```

### Thread Pool and Async Considerations

The SDK is thread-safe and works with async code:

```python
import asyncio
from rebrandly_otel import otel, logger

async def async_operation():
    # Context is automatically propagated in async functions
    with otel.span("async-work"):
        await asyncio.sleep(0.1)
        logger.info("Async work completed")

# Multiple concurrent operations
async def main():
    await asyncio.gather(
        async_operation(),
        async_operation(),
        async_operation()
    )
```

### Memory Management

Monitor and optimize memory usage:

```python
import psutil
from rebrandly_otel import otel, meter, logger

# Create memory gauge for monitoring
memory_gauge = meter.meter.create_observable_gauge(
    name="process.memory.used",
    callbacks=[lambda: psutil.Process().memory_info().rss],
    description="Process memory usage",
    unit="bytes"
)

# Check span buffer size
def check_telemetry_overhead():
    process = psutil.Process()
    mem_before = process.memory_info().rss

    # Create 1000 spans
    for i in range(1000):
        with otel.span(f"test-{i}"):
            pass

    mem_after = process.memory_info().rss
    overhead = (mem_after - mem_before) / 1000
    logger.info(f"Per-span memory overhead: {overhead} bytes")
```

### Production Optimization Checklist

- [ ] Configure appropriate `BATCH_EXPORT_TIME_MILLIS` for your workload
- [ ] Implement sampling for high-traffic services (> 100 req/s)
- [ ] Keep metric cardinality under 1000 combinations per metric
- [ ] Monitor memory usage and adjust batch settings if needed
- [ ] Use `OTEL_DEBUG=false` in production (significant performance impact)
- [ ] Set appropriate timeout buffers for Lambda functions (add 2-3s)
- [ ] Review and limit span attribute sizes (< 1KB per attribute)
- [ ] Disable request body capture if not needed (`OTEL_CAPTURE_REQUEST_BODY=false`)
- [ ] Use connection pooling for database instrumentation
- [ ] Monitor OTLP exporter queue depth and adjust batch settings

## Export Formats

### Supported Exporters

- **OTLP/gRPC**: Primary export format for production
- **Console**: Available for local development and debugging

## Thread Safety

All components are thread-safe and can be used in multi-threaded applications:
- Singleton pattern ensures single initialization
- Thread-safe metric recording
- Concurrent span creation support

## Resource Attributes

Automatically includes:
- Service name and version
- Python runtime version
- Deployment environment
- Custom resource attributes via environment

## Error Handling

- Graceful degradation when OTLP endpoint unavailable
- Non-blocking telemetry operations
- Automatic retry with exponential backoff
- Comprehensive error logging

## Compatibility

- Python 3.7+
- AWS Lambda runtime support
- Compatible with OpenTelemetry Collector
- Works with any OTLP-compatible backend

## Best Practices

### Span Management

**1. Use Context Managers for Automatic Cleanup**
```python
from rebrandly_otel import otel, logger

# ✅ Good: Context manager automatically ends span
with otel.span("process-order", attributes={"order.id": order_id}):
    process_order(order_id)
    # Span automatically ended, even if exception occurs

# ⚠️ Manual span management (less preferred)
span = otel.tracer.start_span("process-order")
try:
    process_order(order_id)
finally:
    span.end()  # Must remember to end
```

**2. Use Meaningful Span Names**
```python
# ✅ Good: Descriptive, operation-focused names
with otel.span("fetch-user-profile"):
    pass
with otel.span("validate-payment"):
    pass
with otel.span("send-email-notification"):
    pass

# ❌ Bad: Vague or implementation-focused names
with otel.span("function1"):
    pass
with otel.span("handler"):
    pass
with otel.span("process"):
    pass
```

**3. Add Contextual Attributes**
```python
with otel.span("create-order", attributes={
    # Business context
    "order.id": order_id,
    "user.id": user_id,
    "order.total": total_amount,
    "payment.method": payment_method,
    # Technical context
    "db.system": "postgresql",
    "http.method": "POST"
}) as span:
    # Can add more attributes dynamically
    span.set_attribute("order.items_count", len(items))
```

**4. Record Exceptions Properly**
```python
from opentelemetry.trace import Status, StatusCode

with otel.span("risky-operation") as span:
    try:
        risky_operation()
    except Exception as e:
        span.record_exception(e)
        span.set_status(Status(StatusCode.ERROR, str(e)))
        raise  # Re-raise after recording
```

### Error Handling

**1. Distinguish Error Types**
```python
from rebrandly_otel import otel, logger
from opentelemetry.trace import Status, StatusCode

with otel.span("process-payment") as span:
    try:
        process_payment(amount)
        span.set_status(Status(StatusCode.OK))
    except ValidationError as e:
        # Client errors (4xx) - not span errors
        span.set_attribute("error.validation", str(e))
        span.set_status(Status(StatusCode.OK))  # Business logic, not system error
        raise
    except Exception as e:
        # Server errors (5xx) - mark span as error
        span.record_exception(e)
        span.set_status(Status(StatusCode.ERROR, str(e)))
        logger.error(f"Payment processing failed: {e}")
        raise
```

### Metric Cardinality

**1. Limit Attribute Values**
```python
from rebrandly_otel import meter

# ❌ Bad: Unbounded cardinality
request_counter.add(1, {
    "user.id": user_id,         # Millions of users!
    "request.id": request_id,   # Every request unique!
    "timestamp": time.time()    # Always unique!
})

# ✅ Good: Bounded cardinality
request_counter.add(1, {
    "http.method": "GET",       # ~10 values
    "http.route": "/api/users", # Hundreds of routes
    "http.status_code": 200     # ~50 status codes
})
```

**2. Aggregate High-Cardinality Data**
```python
# Store detailed data in spans, aggregate in metrics
with otel.span("process-order", attributes={
    "user.id": user_id,    # Detailed (high cardinality OK in spans)
    "order.id": order_id
}) as span:
    # Aggregated attributes in metrics (low cardinality)
    order_counter.add(1, {
        "user.tier": get_user_tier(user_id),    # bronze/silver/gold
        "order.category": get_category(order)    # electronics/clothing/food
    })
```

### Lambda Functions

**1. Always Flush Before Exit**
```python
from rebrandly_otel import lambda_handler, force_flush

# Using decorator (auto-flush enabled by default)
@lambda_handler(name="my-function")
def handler(event, context):
    # Your code
    return response

# Manual flush if needed
@lambda_handler(name="my-function", auto_flush=False)
def handler(event, context):
    result = process(event)
    force_flush(timeout_millis=5000)  # Flush with 5s timeout
    return result
```

**2. Add Buffer to Timeout**
```python
# If Lambda timeout is 30s, set function timeout to 27s
# Reserve 3s for telemetry flush

import time

LAMBDA_TIMEOUT_SEC = 30
FLUSH_BUFFER_SEC = 3
FUNCTION_TIMEOUT_SEC = LAMBDA_TIMEOUT_SEC - FLUSH_BUFFER_SEC

@lambda_handler(name="my-function")
def handler(event, context):
    deadline = time.time() + FUNCTION_TIMEOUT_SEC

    # Check timeout during processing
    if time.time() > deadline:
        raise TimeoutError("Function timeout approaching")

    return process_with_timeout(event, deadline)
```

### Context Propagation

**1. Propagate Context in HTTP Calls**
```python
import requests
from opentelemetry.propagate import inject

def call_downstream(url, data):
    # Extract current context and inject into headers
    headers = {}
    inject(headers)  # Automatically adds traceparent header

    # Make request with trace headers
    response = requests.post(url, json=data, headers=headers)
    return response.json()
```

**2. Propagate Context in AWS Messages**
```python
import boto3
import json
from rebrandly_otel import otel

sqs = boto3.client('sqs')

# Get trace context for message attributes
trace_attrs = otel.tracer.get_attributes_for_aws_from_context()

# Send message with trace context
sqs.send_message(
    QueueUrl=queue_url,
    MessageBody=json.dumps(data),
    MessageAttributes=trace_attrs  # Automatic context injection
)
```

### Logging

**1. Use Structured Logging**
```python
from rebrandly_otel import logger

# ✅ Good: Structured with context
logger.info("Order processed", extra={
    "order_id": order.id,
    "user_id": user.id,
    "amount": order.total,
    "duration": processing_time
})

# ❌ Bad: String formatting
logger.info(f"Order {order.id} processed for user {user.id} with amount {order.total}")
```

**2. Log at Appropriate Levels**
```python
logger.debug("Entering function", extra={"function": "process_order"})  # Development only
logger.info("Order created", extra={"order_id": 123})                   # Normal operations
logger.warning("Slow query detected", extra={"duration": 2.0})          # Performance issues
logger.error("Payment failed", extra={"error": str(e)}, exc_info=True) # Errors with traceback
```

### Configuration

**1. Use Environment-Specific Settings**
```bash
# .env.development
export OTEL_DEBUG=true
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
export BATCH_EXPORT_TIME_MILLIS=50
export LOG_LEVEL=DEBUG

# .env.production
export OTEL_DEBUG=false
export OTEL_EXPORTER_OTLP_ENDPOINT=https://collector.prod.example.com:4317
export BATCH_EXPORT_TIME_MILLIS=100
export LOG_LEVEL=INFO
export OTEL_SPAN_ATTRIBUTES=environment=production,team=backend
```

**2. Don't Hardcode Service Names**
```python
# ❌ Bad: Hardcoded in code
os.environ['OTEL_SERVICE_NAME'] = 'my-service'

# ✅ Good: Set via environment
# In Dockerfile or deployment config:
# ENV OTEL_SERVICE_NAME=my-service
# ENV OTEL_SERVICE_VERSION=1.2.3
```

### Performance

**1. Implement Sampling for High-Traffic Services**
```python
from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatioBased, ALWAYS_ON

# Sample 10% of traces for high-traffic services (> 1000 req/s)
sampler = ParentBasedTraceIdRatioBased(0.1)

# Use ALWAYS_ON for low-traffic or critical services
sampler = ALWAYS_ON
```

**2. Disable Debug Mode in Production**
```bash
# Significant performance impact!
export OTEL_DEBUG=false  # In production

# Only enable for troubleshooting specific issues
```

**3. Monitor Telemetry Overhead**
```python
from rebrandly_otel import meter
import time

# Track telemetry overhead
telemetry_duration = meter.meter.create_histogram(
    name="telemetry.overhead",
    description="Time spent on telemetry operations",
    unit="ms"
)

start = time.time()
# Your telemetry operation
overhead = (time.time() - start) * 1000
telemetry_duration.record(overhead)
```

### Security

**1. Sanitize Sensitive Data**
```python
from rebrandly_otel import logger

# ❌ Bad: Logging sensitive data
logger.info("User login", extra={"username": username, "password": password})

# ✅ Good: Exclude sensitive data
logger.info("User login", extra={
    "username": username,
    "password_provided": bool(password)
})

# SDK automatically redacts sensitive fields when OTEL_CAPTURE_REQUEST_BODY=true
```

**2. Use Secure Connections**
```bash
# ✅ Good: TLS endpoint
export OTEL_EXPORTER_OTLP_ENDPOINT=https://collector.example.com:4317

# ⚠️ Caution: Only use HTTP for local development
export OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
```

### Testing

**1. Disable Telemetry in Tests**
```python
# conftest.py or test setup
import os
import pytest

@pytest.fixture(autouse=True)
def disable_telemetry():
    os.environ['OTEL_EXPORTER_OTLP_ENDPOINT'] = ''
    os.environ['OTEL_DEBUG'] = 'false'

# Or mock the SDK
from unittest.mock import Mock, patch

@patch('rebrandly_otel.otel')
@patch('rebrandly_otel.logger')
def test_my_function(mock_logger, mock_otel):
    mock_otel.span.return_value.__enter__ = Mock()
    mock_otel.span.return_value.__exit__ = Mock()
    # Your test
```

**2. Test Telemetry Integration Separately**
```python
# test_telemetry_integration.py
from rebrandly_otel import otel
import os

def test_span_creation():
    os.environ['OTEL_DEBUG'] = 'true'
    with otel.span("test-span"):
        pass
    # Verify span was created
```

### Async/Await Support

**1. Use Spans with Async Functions**
```python
import asyncio
from rebrandly_otel import otel, logger

async def async_operation():
    # Context is automatically propagated in async functions
    with otel.span("async-work"):
        await asyncio.sleep(0.1)
        logger.info("Async work completed")

# Multiple concurrent operations
async def main():
    await asyncio.gather(
        async_operation(),
        async_operation(),
        async_operation()
    )

asyncio.run(main())
```

### Database Instrumentation

**1. Always Instrument Connections**
```python
import pymysql
from rebrandly_otel import otel, instrument_pymysql

# Create connection
connection = pymysql.connect(
    host='localhost',
    user='user',
    password='password',
    database='mydb'
)

# Instrument the connection
connection = instrument_pymysql(otel, connection, options={
    'slow_query_threshold_ms': 1000,  # Flag slow queries
    'capture_bindings': False         # Disable for performance/security
})

# All queries now automatically traced
with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
```

## Examples

### Lambda - Send SNS / SQS message
```python
import os
import json
import boto3
from rebrandly_otel import otel, lambda_handler, logger

sqs = boto3.client('sqs')
QUEUE_URL = os.environ.get('SQS_URL')

@lambda_handler("sqs_sender")
def handler(event, context):
    logger.info("Starting SQS message send")

    # Get trace context for propagation
    trace_attrs = otel.tracer.get_attributes_for_aws_from_context()

    # Send message with trace context
    response = sqs.send_message(
        QueueUrl=QUEUE_URL,
        MessageBody=json.dumps({"data": "test message"}),
        MessageAttributes=trace_attrs
    )

    logger.info(f"Sent SQS message: {response['MessageId']}")

    return {
        'statusCode': 200,
        'body': json.dumps({'messageId': response['MessageId']})
    }
```

### Lambda Receive SQS message
```python
import json
from rebrandly_otel import lambda_handler, logger, aws_message_span

@lambda_handler(name="sqs_receiver")
def handler(event, context):
    for record in event['Records']:
        # Process each message with trace context
        process_message(record)

def process_message(record):
    with aws_message_span("process_message_sqs_receiver", message=record) as s:
        logger.info(f"Processing message: {record['messageId']}")

        # Parse message body
        body = json.loads(record['body'])
        logger.info(f"Message data: {body}")
```

### Lambda Receive SNS message (record specific event)
```python
import json
from rebrandly_otel import lambda_handler, logger, aws_message_span

@lambda_handler(name="sns_receiver")
def handler(event, context):
    for record in event['Records']:
        # Process each message with trace context
        process_message(record)

def process_message(record):
    message = json.loads(record['Sns']['Message'])
    if message['event'] == 'whitelisted-event':
        with aws_message_span("process_message_sns_receiver", message=record) as s:
            logger.info(f"Processing message: {record['messageId']}")
    
            # Parse message body
            body = json.loads(record['body'])
            logger.info(f"Message data: {body}")
```

###
Flask

```python

from flask import Flask, jsonify
from src.rebrandly_otel import otel, logger, app_before_request, app_after_request, flask_error_handler
from datetime import datetime

app = Flask(__name__)

# Register the centralized OTEL handlers
app.before_request(app_before_request)
app.after_request(app_after_request)
app.register_error_handler(Exception, flask_error_handler)

@app.route('/health')
def health():
    logger.info("Health check requested")
    return jsonify({"status": "healthy"}), 200

@app.route('/process', methods=['POST', 'GET'])
def process():
    with otel.span("process_request"):
        logger.info("Processing POST request")

        # Simulate processing
        result = {"processed": True, "timestamp": datetime.now().isoformat()}

        logger.info(f"Returning result: {result}")
        return jsonify(result), 200

@app.route('/error')
def error():
    logger.error("Error endpoint called")
    raise Exception("Simulated error")

if __name__ == '__main__':
    app.run(debug=True)
```

###
FastAPI

```python

# main_fastapi.py
from fastapi import FastAPI, HTTPException, Depends
from contextlib import asynccontextmanager
from src.rebrandly_otel import otel, logger, force_flush
from src.fastapi_support import setup_fastapi, get_current_span
from datetime import datetime
from typing import Optional
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("FastAPI application starting up")
    yield
    # Shutdown
    logger.info("FastAPI application shutting down")
    force_flush()

app = FastAPI(title="FastAPI OTEL Example", lifespan=lifespan)

# Setup FastAPI with OTEL
setup_fastapi(otel, app)

@app.get("/health")
async def health():
    """Health check endpoint."""
    logger.info("Health check requested")
    return {"status": "healthy"}

@app.post("/process")
@app.get("/process")
async def process(span = Depends(get_current_span)):
    """Process endpoint with custom span."""
    with otel.span("process_request"):
        logger.info("Processing request")

        # You can also use the injected span directly
        if span:
            span.add_event("custom_processing_event", {
                "timestamp": datetime.now().isoformat()
            })

        # Simulate some processing
        result = {
            "processed": True,
            "timestamp": datetime.now().isoformat()
        }

        logger.info(f"Returning result: {result}")
        return result

@app.get("/error")
async def error():
    """Endpoint that raises an error."""
    logger.error("Error endpoint called")
    raise HTTPException(status_code=400, detail="Simulated error")

@app.get("/exception")
async def exception():
    """Endpoint that raises an unhandled exception."""
    logger.error("Exception endpoint called")
    raise ValueError("Simulated unhandled exception")

@app.get("/items/{item_id}")
async def get_item(item_id: int, q: Optional[str] = None):
    """Example endpoint with path and query parameters."""
    with otel.span("fetch_item", attributes={"item_id": item_id, "query": q}):
        logger.info(f"Fetching item {item_id} with query: {q}")

        if item_id == 999:
            raise HTTPException(status_code=404, detail="Item not found")

        return {
            "item_id": item_id,
            "name": f"Item {item_id}",
            "query": q
        }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### PyMySQL Database Instrumentation

The SDK provides connection-level instrumentation for PyMySQL that automatically traces all queries without requiring you to instrument each query individually.

```python
import pymysql
from rebrandly_otel import otel, logger, instrument_pymysql

# SDK auto-initializes on import

# Create and instrument your connection
connection = pymysql.connect(
    host='localhost',
    user='your_user',
    password='your_password',
    database='your_database'
)

# Instrument the connection - all queries are now automatically traced
connection = instrument_pymysql(otel, connection, options={
    'slow_query_threshold_ms': 1000,  # Queries over 1s flagged as slow
    'capture_bindings': False  # Set True to capture query parameters
})

# Use normally - all queries automatically traced
with connection.cursor() as cursor:
    cursor.execute("SELECT * FROM users WHERE id = %s", (123,))
    result = cursor.fetchone()
    logger.info(f"Found user: {result}")

connection.close()
otel.force_flush()
```

Features:
- Automatic span creation for all queries
- Query operation detection (SELECT, INSERT, UPDATE, etc.)
- Slow query detection and flagging
- Duration tracking
- Error recording with exception details
- Optional query parameter capture (disabled by default for security)

Environment configuration:
- `PYMYSQL_SLOW_QUERY_THRESHOLD_MS`: Threshold for slow query detection (default: 1500ms)

### More examples
You can find More examples [here](examples)

## Troubleshooting

### Common Issues

#### No Data Exported

**Symptoms**: Telemetry data not appearing in your observability backend.

**Solutions**:
1. Verify `OTEL_EXPORTER_OTLP_ENDPOINT` is correctly set:
   ```bash
   echo $OTEL_EXPORTER_OTLP_ENDPOINT
   ```
2. Check network connectivity to the collector:
   ```bash
   curl -v $OTEL_EXPORTER_OTLP_ENDPOINT
   ```
3. Enable debug mode to see console output:
   ```bash
   export OTEL_DEBUG=true
   python app.py
   ```
4. Verify the collector is running and accepting connections
5. Check for firewall rules blocking outbound gRPC traffic (port 4317)

#### Missing Traces in Lambda

**Symptoms**: Lambda function executes but no traces appear in backend.

**Solutions**:
1. Ensure `force_flush()` is called before handler returns:
   ```python
   from rebrandly_otel import lambda_handler, force_flush

   @lambda_handler(name="my-function")
   def handler(event, context):
       # Your code
       force_flush(timeout_millis=5000)  # Explicitly flush
       return response
   ```
2. Verify Lambda timeout allows enough time for flush (add 2-3 seconds buffer)
3. Check Lambda execution role has network access to OTLP endpoint
4. Verify environment variables are set in Lambda configuration
5. Check CloudWatch Logs for error messages

#### Trace Context Not Propagating

**Symptoms**: Distributed traces appear as disconnected spans instead of a unified trace.

**Solutions**:
1. Verify message attributes are being sent:
   ```python
   # For SQS
   trace_attrs = otel.tracer.get_attributes_for_aws_from_context()
   response = sqs.send_message(
       QueueUrl=queue_url,
       MessageBody=json.dumps(data),
       MessageAttributes=trace_attrs  # Don't forget this!
   )
   ```
2. Check that receiving end uses `aws_message_span()` or `@aws_message_handler`:
   ```python
   with aws_message_span("process-message", message=record):
       # Processing logic
       pass
   ```
3. For HTTP services, verify headers are being propagated:
   ```python
   import requests
   from opentelemetry.propagate import inject

   headers = {}
   inject(headers)  # Injects traceparent header
   response = requests.get(url, headers=headers)
   ```

#### High Memory Usage

**Symptoms**: Application memory usage grows over time.

**Solutions**:
1. Reduce batch export interval:
   ```bash
   export BATCH_EXPORT_TIME_MILLIS=50  # Flush more frequently (default: 100)
   ```
2. Implement sampling for high-traffic applications:
   ```python
   from opentelemetry.sdk.trace.sampling import ParentBasedTraceIdRatioBased

   # Sample 10% of traces
   sampler = ParentBasedTraceIdRatioBased(0.1)
   ```
3. Monitor metric cardinality - avoid high-cardinality attributes:
   ```python
   # Bad: user_id has millions of possible values
   counter.add(1, {"user_id": user_id})

   # Good: user_tier has limited values
   counter.add(1, {"user_tier": "premium"})
   ```
4. Check for span leaks - ensure all spans are properly closed

#### Import Errors

**Symptoms**: `ModuleNotFoundError` or `ImportError` when importing rebrandly_otel.

**Solutions**:
1. Verify installation:
   ```bash
   pip show rebrandly-otel
   ```
2. Reinstall if necessary:
   ```bash
   pip uninstall rebrandly-otel
   pip install rebrandly-otel
   ```
3. Check Python version compatibility (requires Python 3.7+):
   ```bash
   python --version
   ```
4. For Lambda, ensure package is included in deployment package or layer

#### Database Instrumentation Not Working

**Symptoms**: Database queries not appearing as spans.

**Solutions**:
1. Verify connection is instrumented:
   ```python
   from rebrandly_otel import instrument_pymysql

   connection = pymysql.connect(...)
   connection = instrument_pymysql(otel, connection)  # Don't forget this!
   ```
2. Check that you're using the instrumented connection object
3. Verify slow query threshold settings:
   ```bash
   export PYMYSQL_SLOW_QUERY_THRESHOLD_MS=1000
   ```

#### Flask/FastAPI Routes Not Traced

**Symptoms**: HTTP requests not creating spans.

**Solutions**:
1. Verify middleware is registered **before** route definitions:
   ```python
   # Flask
   app.before_request(app_before_request)
   app.after_request(app_after_request)
   app.register_error_handler(Exception, flask_error_handler)

   # Then define routes
   @app.route('/api/users')
   def get_users():
       ...
   ```
2. For FastAPI, ensure `setup_fastapi()` is called:
   ```python
   from rebrandly_otel.fastapi_support import setup_fastapi
   setup_fastapi(otel, app)
   ```
3. Check for middleware conflicts with other libraries

### Debugging Tips

#### Enable Debug Mode

See all telemetry data in console:
```bash
export OTEL_DEBUG=true
python app.py
```

#### Check Span Attributes

Print span attributes during development:
```python
with otel.span("test-span") as span:
    print(f"Trace ID: {span.get_span_context().trace_id}")
    print(f"Span ID: {span.get_span_context().span_id}")
    # Your code
```

#### Verify Environment Variables

Check all OTEL configuration:
```python
import os
print("OTEL_SERVICE_NAME:", os.getenv("OTEL_SERVICE_NAME"))
print("OTEL_EXPORTER_OTLP_ENDPOINT:", os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT"))
print("OTEL_DEBUG:", os.getenv("OTEL_DEBUG"))
```

#### Test Trace Context Propagation

Manually test context extraction:
```python
from rebrandly_otel import otel

# Simulate SQS message
test_message = {
    'messageAttributes': {
        'traceparent': {'stringValue': '00-trace-id-span-id-01'}
    }
}

context = otel.tracer.extract_context_from_aws_message(test_message)
print(f"Extracted context: {context}")
```

## Testing

### Running Tests

The test suite uses [pytest](https://docs.pytest.org/).

Run all tests:
```bash
pytest
```

Run specific test file:
```bash
pytest tests/test_flask_support.py -v
pytest tests/test_fastapi_support.py -v
pytest tests/test_usage.py -v
pytest tests/test_pymysql_instrumentation.py -v
pytest tests/test_metrics_and_logs.py -v
pytest tests/test_decorators.py -v
pytest tests/test_span_attributes_processor.py -v
```

Run with coverage:
```bash
pytest --cov=src --cov-report=html
```

### Test Coverage

The test suite includes:
- **Integration tests** (`test_usage.py`): Core OTEL functionality, Lambda handlers, message processing
- **Flask integration tests** (`test_flask_support.py`): Flask setup and hooks
- **FastAPI integration tests** (`test_fastapi_support.py`): FastAPI setup and middleware
- **PyMySQL instrumentation tests** (`test_pymysql_instrumentation.py`): Database connection instrumentation, query tracing, helper functions
- **Metrics and logs tests** (`test_metrics_and_logs.py`): Custom metrics creation (counter, histogram, gauge), logging levels (info, warning, debug, error)
- **Decorators tests** (`test_decorators.py`): Lambda handler decorator, AWS message handler decorator, traces decorator, aws_message_span context manager
- **Span attributes processor tests** (`test_span_attributes_processor.py`): Automatic span attributes from OTEL_SPAN_ATTRIBUTES (31 tests)

## License

Rebrandly Python SDK is released under the MIT License.

## Build and Deploy

```bash
brew install pipx
pipx ensurepath
pipx install build
pipx install twine
```

> build
> 
> twine upload dist/*

If `build` gives you an error, try:

> pyproject-build
>
> twine upload dist/*