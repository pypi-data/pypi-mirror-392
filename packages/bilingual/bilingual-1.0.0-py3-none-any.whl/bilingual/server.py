#!/usr/bin/env python3
"""
Production-ready FastAPI server for the Bilingual NLP Toolkit.

Provides REST API endpoints for all bilingual functionality including:
- Text processing and analysis
- Model inference and generation
- Data collection and evaluation
- Model training and deployment
- Health monitoring and telemetry
"""

from contextlib import asynccontextmanager
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel, Field

sys.path.insert(0, str(Path(__file__).parent))

try:
    import bilingual as bb
    from bilingual.config import get_settings

    BILINGUAL_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Bilingual package not available: {e}")
    BILINGUAL_AVAILABLE = False

# Prometheus metrics (optional)
try:
    from fastapi.responses import Response
    from prometheus_client import CONTENT_TYPE_LATEST, Counter, Histogram, generate_latest

    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False


# Request/Response Models
class LanguageDetectionRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=10000)
    method: str = Field("combined", description="Detection method")


class LanguageDetectionResponse(BaseModel):
    language: str
    confidence: float
    method: str
    processing_time_ms: float


class TranslationRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000)
    source_lang: str = Field("auto", description="Source language")
    target_lang: str = Field("en", description="Target language")
    model: str = Field("t5-small", description="Translation model")


class TranslationResponse(BaseModel):
    original_text: str
    translated_text: str
    source_lang: str
    target_lang: str
    model_used: str
    processing_time_ms: float


class GenerationRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=1000)
    model: str = Field("t5-small", description="Generation model")
    max_length: int = Field(150, ge=10, le=500)
    temperature: float = Field(1.0, ge=0.1, le=2.0)
    num_beams: int = Field(4, ge=1, le=10)


class GenerationResponse(BaseModel):
    prompt: str
    generated_text: str
    model_used: str
    processing_time_ms: float


class EvaluationRequest(BaseModel):
    task: str = Field(..., description="Evaluation task (translation, generation)")
    references: List[str] = Field(..., min_items=1)
    candidates: List[str] = Field(..., min_items=1)


class EvaluationResponse(BaseModel):
    task: str
    results: Dict[str, Any]
    processing_time_ms: float


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str
    uptime_seconds: float
    models_loaded: List[str]
    memory_usage_mb: Optional[float] = None


# Global variables for monitoring
START_TIME = time.time()
REQUEST_COUNT = 0
ERROR_COUNT = 0

# Metrics (if Prometheus available)
if PROMETHEUS_AVAILABLE:
    REQUEST_COUNTER = Counter("bilingual_requests_total", "Total requests", ["endpoint", "method"])
    REQUEST_DURATION = Histogram(
        "bilingual_request_duration_seconds", "Request duration", ["endpoint"]
    )
    ERROR_COUNTER = Counter("bilingual_errors_total", "Total errors", ["endpoint", "error_type"])


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    print("🚀 Starting Bilingual API Server...")
    print(f"📍 Server will be available at: http://localhost:8000")
    print(f"📚 API Documentation: http://localhost:8000/docs")

    if BILINGUAL_AVAILABLE:
        try:
            # Pre-load common models for faster inference
            settings = get_settings()
            print(f"🔧 Configuration loaded: {settings.model.default_model}")

            # Try to load tokenizer
            try:
                bb.load_tokenizer("models/tokenizer/bilingual_sp.model")
                print("✅ Tokenizer loaded successfully")
            except Exception as e:
                print(f"⚠️  Could not load tokenizer: {e}")

        except Exception as e:
            print(f"⚠️  Could not initialize bilingual components: {e}")

    yield

    # Shutdown
    print("👋 Shutting down Bilingual API Server...")


# Create FastAPI app
app = FastAPI(
    title="Bilingual NLP API",
    description="Production-ready API for the Bilingual NLP Toolkit",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing middleware
@app.middleware("http")
async def add_process_time_header(request, call_next):
    global REQUEST_COUNT
    REQUEST_COUNT += 1

    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time

    # Add custom headers
    response.headers["X-Process-Time"] = str(process_time)
    response.headers["X-Request-ID"] = str(REQUEST_COUNT)

    # Update metrics
    if PROMETHEUS_AVAILABLE:
        REQUEST_DURATION.labels(endpoint=str(request.url.path)).observe(process_time)

    return response


# Error handling middleware
@app.middleware("http")
async def error_handling_middleware(request, call_next):
    global ERROR_COUNT

    try:
        response = await call_next(request)

        # Count 4xx and 5xx errors
        if response.status_code >= 400:
            ERROR_COUNT += 1
            if PROMETHEUS_AVAILABLE:
                ERROR_COUNTER.labels(
                    endpoint=str(request.url.path), error_type=str(response.status_code)
                ).inc()

        return response

    except Exception as e:
        ERROR_COUNT += 1
        if PROMETHEUS_AVAILABLE:
            ERROR_COUNTER.labels(endpoint=str(request.url.path), error_type=type(e).__name__).inc()

        # Return error response
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal server error",
                "message": str(e),
                "timestamp": datetime.now().isoformat(),
            },
        )


# Routes


@app.get("/", response_class=HTMLResponse)
async def root():
    """Root endpoint with API information."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Bilingual NLP API</title>
        <style>
            body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
            .hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 40px; border-radius: 10px; text-align: center; margin-bottom: 30px; }
            .endpoint { background: #f8f9fa; padding: 15px; margin: 10px 0; border-radius: 5px; border-left: 4px solid #007bff; }
            .method { font-weight: bold; color: #007bff; }
            code { background: #e9ecef; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }
        </style>
    </head>
    <body>
        <div class="hero">
            <h1>🌏 Bilingual NLP API</h1>
            <p>Production-ready API for advanced Bangla-English text processing</p>
        </div>

        <h2>🚀 Quick Start</h2>

        <div class="endpoint">
            <div class="method">GET /health</div>
            <p>Check server health and status</p>
            <code>curl http://localhost:8000/health</code>
        </div>

        <div class="endpoint">
            <div class="method">POST /detect-language</div>
            <p>Detect language of text</p>
            <code>curl -X POST "http://localhost:8000/lang" -d '{"text": "Hello world"}'</code>
        </div>

        <div class="endpoint">
            <div class="method">POST /translate</div>
            <p>Translate text between languages</p>
            <code>curl -X POST "http://localhost:8000/translate" -H "Content-Type: application/json" -d '{"text": "Hello world", "target_lang": "bn"}'</code>
        </div>

        <div class="endpoint">
            <div class="method">POST /generate</div>
            <p>Generate text using AI models</p>
            <code>curl -X POST "http://localhost:8000/generate" -H "Content-Type: application/json" -d '{"prompt": "Write a story about friendship"}'</code>
        </div>

        <div class="endpoint">
            <div class="method">POST /evaluate</div>
            <p>Evaluate model outputs</p>
            <code>curl -X POST "http://localhost:8000/evaluate" -H "Content-Type: application/json" -d '{"task": "translation", "references": ["Hello"], "candidates": ["Hello"]}'</code>
        </div>

        <h2>📚 Documentation</h2>
        <p><a href="/docs">Interactive API Documentation (Swagger/ReDoc)</a></p>
        <p><a href="/redoc">Alternative API Documentation</a></p>

        <h2>🔧 Features</h2>
        <ul>
            <li>🚀 High-performance async API</li>
            <li>🌍 Bilingual Bangla-English support</li>
            <li>🤖 State-of-the-art transformer models</li>
            <li>📊 Comprehensive evaluation metrics</li>
            <li>🛡️ Production-ready with monitoring</li>
            <li>🔒 Type-safe with Pydantic validation</li>
        </ul>
    </body>
    </html>
    """


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint with system information."""
    uptime = time.time() - START_TIME

    # Get loaded models (if available)
    loaded_models = []
    if BILINGUAL_AVAILABLE:
        try:
            # This would need to be implemented in the transformer_models module
            loaded_models = ["t5-small"]  # Placeholder
        except Exception:
            pass

    # Memory usage (optional)
    memory_usage = None
    try:
        import psutil

        process = psutil.Process()
        memory_usage = process.memory_info().rss / 1024 / 1024  # MB
    except ImportError:
        pass

    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0",
        uptime_seconds=uptime,
        models_loaded=loaded_models,
        memory_usage_mb=memory_usage,
    )


@app.post("/detect-language", response_model=LanguageDetectionResponse)
async def detect_language_endpoint(request: LanguageDetectionRequest):
    """Detect the language of input text."""
    if not BILINGUAL_AVAILABLE:
        raise HTTPException(status_code=503, detail="Bilingual package not available")

    start_time = time.time()

    try:
        result = bb.detect_language(request.text, method=request.method)

        processing_time = (time.time() - start_time) * 1000

        return LanguageDetectionResponse(
            language=result["language"],
            confidence=result["confidence"],
            method=result["method"],
            processing_time_ms=processing_time,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Language detection failed: {str(e)}")


@app.post("/translate", response_model=TranslationResponse)
async def translate_endpoint(request: TranslationRequest):
    """Translate text between languages."""
    if not BILINGUAL_AVAILABLE:
        raise HTTPException(status_code=503, detail="Bilingual package not available")

    start_time = time.time()

    try:
        # Auto-detect source language if not specified
        source_lang = request.source_lang
        if source_lang == "auto":
            detected = bb.detect_language(request.text)
            source_lang = detected["language"]

        # Load model and translate
        bb.load_model(request.model, "t5")
        translated_text = bb.translate_text(
            request.model, request.text, source_lang, request.target_lang
        )

        processing_time = (time.time() - start_time) * 1000

        return TranslationResponse(
            original_text=request.text,
            translated_text=translated_text,
            source_lang=source_lang,
            target_lang=request.target_lang,
            model_used=request.model,
            processing_time_ms=processing_time,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation failed: {str(e)}")


@app.post("/generate", response_model=GenerationResponse)
async def generate_endpoint(request: GenerationRequest):
    """Generate text using AI models."""
    if not BILINGUAL_AVAILABLE:
        raise HTTPException(status_code=503, detail="Bilingual package not available")

    start_time = time.time()

    try:
        bb.load_model(request.model, "t5")
        generated_text = bb.generate_text(
            request.model,
            request.prompt,
            max_length=request.max_length,
            temperature=request.temperature,
            num_beams=request.num_beams,
        )

        processing_time = (time.time() - start_time) * 1000

        return GenerationResponse(
            prompt=request.prompt,
            generated_text=generated_text,
            model_used=request.model,
            processing_time_ms=processing_time,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


@app.post("/evaluate", response_model=EvaluationResponse)
async def evaluate_endpoint(request: EvaluationRequest):
    """Evaluate model outputs against references."""
    if not BILINGUAL_AVAILABLE:
        raise HTTPException(status_code=503, detail="Bilingual package not available")

    start_time = time.time()

    try:
        if request.task == "translation":
            results = bb.evaluate_translation(request.references, request.candidates)
        elif request.task == "generation":
            results = bb.evaluate_generation(request.references, request.candidates)
        else:
            raise HTTPException(status_code=400, detail=f"Unknown task: {request.task}")

        processing_time = (time.time() - start_time) * 1000

        return EvaluationResponse(
            task=request.task, results=results, processing_time_ms=processing_time
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {str(e)}")


@app.get("/metrics")
async def metrics_endpoint():
    """Prometheus metrics endpoint (if available)."""
    if not PROMETHEUS_AVAILABLE:
        raise HTTPException(status_code=503, detail="Prometheus metrics not available")

    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/status")
async def status_endpoint():
    """Get server status and statistics."""
    uptime = time.time() - START_TIME

    return {
        "status": "running",
        "uptime_seconds": uptime,
        "total_requests": REQUEST_COUNT,
        "total_errors": ERROR_COUNT,
        "error_rate": ERROR_COUNT / max(REQUEST_COUNT, 1),
        "timestamp": datetime.now().isoformat(),
    }


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    return app


def run_server(host: str = "localhost", port: int = 8000, workers: int = 1, reload: bool = False):
    """Run the FastAPI server."""
    print(f"🚀 Starting server on {host}:{port}")
    print(f"📚 API docs available at: http://{host}:{port}/docs")
    print(f"🔍 Health check: http://{host}:{port}/health")

    uvicorn.run(
        "bilingual.server:app",
        host=host,
        port=port,
        workers=workers,
        reload=reload,
        log_level="info",
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Bilingual NLP API Server")
    parser.add_argument("--host", default="localhost", help="Server host")
    parser.add_argument("--port", type=int, default=8000, help="Server port")
    parser.add_argument("--workers", type=int, default=1, help="Number of workers")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")

    args = parser.parse_args()
    run_server(args.host, args.port, args.workers, args.reload)
