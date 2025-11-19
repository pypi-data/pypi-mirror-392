#!/usr/bin/env python3
"""Test realistic AI data types through the 4 new semantic codecs.

This script generates various AI data types and verifies they compress/decompress
cleanly through Sr, Sv, Sw, and St codecs.
"""

import json
import struct
import sys
import os
from pathlib import Path

# Add src to path - avoid loading app.py
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Prevent app.py from being loaded by importing compression modules directly
os.environ.setdefault("SKIP_APP_IMPORT", "1")

from arua.compression.semantic_resolver import compress as sr_compress, decompress as sr_decompress
from arua.compression.semantic_vector import compress as sv_compress, decompress as sv_decompress
from arua.compression.semantic_stream import compress as sw_compress, decompress as sw_decompress
from arua.compression.semantic_table import (
    compress as st_compress,
    decompress as st_decompress,
    TableColumn,
    TableSchema,
    encode_table,
    decode_table,
)


def test_vector_embeddings():
    """Test realistic text embedding vectors (Sv codec)."""
    print("\n=== Testing Vector Embeddings (Sv) ===")

    # Simulate a 768-dim text embedding (BERT-like)
    embedding_dim = 768
    embedding_data = struct.pack(f"{embedding_dim}f", *[0.1 * i % 1.0 for i in range(embedding_dim)])

    metadata = {
        "dimension": embedding_dim,
        "model": "text-embedding-ada-002",
        "dtype": "float32",
        "normalized": True,
        "source": {
            "document_id": "doc-12345",
            "chunk_index": 5,
            "text": "Machine learning models process data through neural networks"
        },
        "pooling": "mean",
        "timestamp": 1705315800000
    }

    # Compress
    compressed = sv_compress(embedding_data, metadata=metadata)
    print(f"Original size: {len(embedding_data)} bytes")
    print(f"Compressed size: {len(compressed)} bytes")
    print(f"Compression ratio: {len(embedding_data) / len(compressed):.2f}x")

    # Decompress
    decompressed_data, decoded_metadata = sv_decompress(compressed)

    # Verify
    assert decompressed_data == embedding_data, "Vector data mismatch!"
    assert decoded_metadata == metadata, "Vector metadata mismatch!"
    assert decoded_metadata["dimension"] == 768
    assert decoded_metadata["source"]["document_id"] == "doc-12345"

    print("✓ Vector embedding roundtrip successful")
    print(f"✓ Metadata preserved: dimension={decoded_metadata['dimension']}, model={decoded_metadata['model']}")
    return True


def test_multimodal_embeddings():
    """Test multimodal embeddings (image + text)."""
    print("\n=== Testing Multimodal Embeddings (Sv) ===")

    # Simulate CLIP-style multimodal embedding
    dim = 512
    embedding_data = struct.pack(f"{dim}f", *[0.01 * (i ** 2) % 1.0 for i in range(dim)])

    metadata = {
        "dimension": dim,
        "dtype": "float32",
        "modality": "image+text",
        "image_model": "clip-vit-b-32",
        "text_model": "clip-text-b-32",
        "fusion": "concatenate",
        "image_weight": 0.6,
        "text_weight": 0.4,
        "source": {
            "image_path": "images/cat.jpg",
            "caption": "A fluffy orange cat sitting on a windowsill"
        }
    }

    compressed = sv_compress(embedding_data, metadata=metadata)
    decompressed_data, decoded_metadata = sv_decompress(compressed)

    assert decompressed_data == embedding_data
    assert decoded_metadata["modality"] == "image+text"
    assert decoded_metadata["image_weight"] == 0.6

    print(f"✓ Multimodal embedding roundtrip successful")
    print(f"✓ Modality: {decoded_metadata['modality']}, fusion: {decoded_metadata['fusion']}")
    return True


def test_audio_stream():
    """Test audio stream data (Sw codec)."""
    print("\n=== Testing Audio Stream (Sw) ===")

    # Simulate 1 second of 16kHz mono audio (PCM)
    sample_rate = 16000
    duration_seconds = 1.0
    num_samples = int(sample_rate * duration_seconds)

    # Generate sine wave at 440Hz (A note)
    import math
    frequency = 440.0
    audio_samples = [
        int(32767 * 0.5 * math.sin(2 * math.pi * frequency * i / sample_rate))
        for i in range(num_samples)
    ]
    audio_data = struct.pack(f"{num_samples}h", *audio_samples)

    metadata = {
        "sample_rate": sample_rate,
        "channels": 1,
        "bit_depth": 16,
        "format": "pcm_s16le",
        "duration_ms": int(duration_seconds * 1000),
        "codec": "raw",
        "source": {
            "recording": "speech_sample_001",
            "speaker": "speaker_A",
            "language": "en-US"
        },
        "processing": {
            "noise_reduction": True,
            "normalization": "peak"
        }
    }

    compressed = sw_compress(audio_data, metadata=metadata)
    print(f"Original size: {len(audio_data)} bytes ({len(audio_data)/1024:.1f} KB)")
    print(f"Compressed size: {len(compressed)} bytes ({len(compressed)/1024:.1f} KB)")
    print(f"Compression ratio: {len(audio_data) / len(compressed):.2f}x")

    decompressed_data, decoded_metadata = sw_decompress(compressed)

    assert decompressed_data == audio_data
    assert decoded_metadata["sample_rate"] == sample_rate
    assert decoded_metadata["source"]["language"] == "en-US"

    print("✓ Audio stream roundtrip successful")
    print(f"✓ Format: {decoded_metadata['format']}, {decoded_metadata['sample_rate']}Hz, {decoded_metadata['channels']} channel(s)")
    return True


def test_video_stream():
    """Test video frame stream data (Sw codec)."""
    print("\n=== Testing Video Stream (Sw) ===")

    # Simulate a 1920x1080 YUV420p video frame
    width, height = 1920, 1080
    y_plane_size = width * height
    uv_plane_size = (width // 2) * (height // 2)

    # Generate dummy YUV data
    frame_data = bytes([128] * y_plane_size + [128] * uv_plane_size + [128] * uv_plane_size)

    metadata = {
        "width": width,
        "height": height,
        "fps": 30,
        "codec": "h264",
        "bitrate": 5000000,
        "format": "yuv420p",
        "color_space": "bt709",
        "frame_index": 42,
        "timestamp_ms": 1400,
        "keyframe": False,
        "source": {
            "video_id": "video-789",
            "camera": "front-facing",
            "resolution": "1080p"
        }
    }

    compressed = sw_compress(frame_data, metadata=metadata)
    print(f"Original size: {len(frame_data)} bytes ({len(frame_data)/1024/1024:.2f} MB)")
    print(f"Compressed size: {len(compressed)} bytes ({len(compressed)/1024:.1f} KB)")
    print(f"Compression ratio: {len(frame_data) / len(compressed):.2f}x")

    decompressed_data, decoded_metadata = sw_decompress(compressed)

    assert decompressed_data == frame_data
    assert decoded_metadata["width"] == width
    assert decoded_metadata["height"] == height

    print("✓ Video stream roundtrip successful")
    print(f"✓ Resolution: {decoded_metadata['width']}x{decoded_metadata['height']}, {decoded_metadata['fps']}fps")
    return True


def test_training_data_table():
    """Test ML training data table (St codec)."""
    print("\n=== Testing Training Data Table (St) ===")

    # Simulate a dataset of training examples
    rows = [
        {
            "example_id": 1,
            "input_text": "The weather is sunny today",
            "label": "positive",
            "confidence": 0.95,
            "tokens": 5,
            "embedding_norm": 1.0
        },
        {
            "example_id": 2,
            "input_text": "I am feeling sad",
            "label": "negative",
            "confidence": 0.87,
            "tokens": 4,
            "embedding_norm": 0.98
        },
        {
            "example_id": 3,
            "input_text": "The product works well",
            "label": "positive",
            "confidence": 0.92,
            "tokens": 4,
            "embedding_norm": 1.02
        },
    ]

    # Encode table
    encoded = encode_table(rows, domain_id=10, template_id=100)
    print(f"Table size: {len(rows)} rows")
    print(f"Encoded size: {len(encoded)} bytes")

    # Decode table
    decoded_rows, schema, header, plan = decode_table(encoded)

    # Verify
    assert len(decoded_rows) == len(rows)
    assert decoded_rows[0]["input_text"] == "The weather is sunny today"
    assert decoded_rows[1]["label"] == "negative"
    assert decoded_rows[2]["confidence"] == 0.92

    print("✓ Training data table roundtrip successful")
    print(f"✓ Schema: {len(schema.columns)} columns")
    for col in schema.columns:
        print(f"  - {col.name}: {col.type}")
    return True


def test_model_metrics_table():
    """Test model performance metrics table (St codec)."""
    print("\n=== Testing Model Metrics Table (St) ===")

    # Simulate model evaluation metrics
    rows = [
        {
            "epoch": 1,
            "train_loss": 2.456,
            "val_loss": 2.389,
            "train_acc": 0.456,
            "val_acc": 0.478,
            "learning_rate": 0.001,
            "batch_size": 32
        },
        {
            "epoch": 2,
            "train_loss": 1.234,
            "val_loss": 1.298,
            "train_acc": 0.678,
            "val_acc": 0.654,
            "learning_rate": 0.001,
            "batch_size": 32
        },
        {
            "epoch": 3,
            "train_loss": 0.867,
            "val_loss": 0.923,
            "train_acc": 0.789,
            "val_acc": 0.765,
            "learning_rate": 0.0005,
            "batch_size": 32
        },
    ]

    schema = TableSchema(
        columns=(
            TableColumn(name="epoch", type="int"),
            TableColumn(name="train_loss", type="float"),
            TableColumn(name="val_loss", type="float"),
            TableColumn(name="train_acc", type="float"),
            TableColumn(name="val_acc", type="float"),
            TableColumn(name="learning_rate", type="float"),
            TableColumn(name="batch_size", type="int"),
        )
    )

    # Convert to columnar JSON
    table_json = {
        "schema": [{"name": col.name, "type": col.type} for col in schema.columns],
        "columns": {
            "epoch": [r["epoch"] for r in rows],
            "train_loss": [r["train_loss"] for r in rows],
            "val_loss": [r["val_loss"] for r in rows],
            "train_acc": [r["train_acc"] for r in rows],
            "val_acc": [r["val_acc"] for r in rows],
            "learning_rate": [r["learning_rate"] for r in rows],
            "batch_size": [r["batch_size"] for r in rows],
        }
    }

    table_data = json.dumps(table_json, separators=(",", ":")).encode("utf-8")

    compressed = st_compress(table_data, schema=schema)
    decompressed_data, decoded_schema = st_decompress(compressed)

    # Parse back
    decoded_json = json.loads(decompressed_data.decode("utf-8"))

    assert decoded_json["columns"]["epoch"] == [1, 2, 3]
    assert len(decoded_schema.columns) == 7
    assert decoded_schema.columns[0].name == "epoch"

    print("✓ Model metrics table roundtrip successful")
    print(f"✓ Metrics tracked: {', '.join([col.name for col in decoded_schema.columns[:4]])}")
    return True


def test_routing_hints():
    """Test model routing/inference hints (Sr codec)."""
    print("\n=== Testing Routing Hints (Sr) ===")

    # Simulate inference request with routing hints
    request_data = json.dumps({
        "prompt": "Translate the following text to French: Hello, how are you?",
        "max_tokens": 100,
        "temperature": 0.7
    }).encode("utf-8")

    hints = {
        "model": {
            "name": "gpt-4",
            "version": "2024-01",
            "deployment": "production"
        },
        "routing": {
            "region": "us-west-2",
            "tier": "premium",
            "priority": "high",
            "deadline_ms": 5000
        },
        "optimization": {
            "use_cache": True,
            "batch_compatible": False,
            "quantization": "int8"
        },
        "resources": {
            "min_gpus": 1,
            "preferred_gpu": "A100",
            "max_memory_gb": 40
        },
        "metadata": {
            "request_id": "req-abc-123",
            "user_id": "user-456",
            "session_id": "sess-789"
        }
    }

    compressed = sr_compress(request_data, hints=hints)
    print(f"Request size: {len(request_data)} bytes")
    print(f"Compressed size: {len(compressed)} bytes")

    decompressed_data, decoded_hints = sr_decompress(compressed)

    assert decompressed_data == request_data
    assert decoded_hints["model"]["name"] == "gpt-4"
    assert decoded_hints["routing"]["region"] == "us-west-2"
    assert decoded_hints["resources"]["preferred_gpu"] == "A100"

    print("✓ Routing hints roundtrip successful")
    print(f"✓ Model: {decoded_hints['model']['name']}, Region: {decoded_hints['routing']['region']}")
    print(f"✓ Resources: {decoded_hints['resources']['min_gpus']} GPU(s), {decoded_hints['resources']['max_memory_gb']}GB RAM")
    return True


def test_distributed_inference_routing():
    """Test distributed inference routing (Sr codec)."""
    print("\n=== Testing Distributed Inference Routing (Sr) ===")

    # Simulate a batch inference request
    batch_data = json.dumps([
        {"text": "Example 1"},
        {"text": "Example 2"},
        {"text": "Example 3"},
    ]).encode("utf-8")

    hints = {
        "distribution": {
            "strategy": "round-robin",
            "replicas": 3,
            "shard_key": "batch_id_123",
            "nodes": ["node-1", "node-2", "node-3"]
        },
        "load_balancing": {
            "algorithm": "least-connections",
            "health_check": True,
            "failover": True
        },
        "performance": {
            "target_latency_ms": 100,
            "target_throughput_qps": 1000,
            "batch_size": 32
        },
        "monitoring": {
            "trace_id": "trace-xyz-789",
            "span_id": "span-abc-456",
            "log_level": "info"
        }
    }

    compressed = sr_compress(batch_data, hints=hints)
    decompressed_data, decoded_hints = sr_decompress(compressed)

    assert decompressed_data == batch_data
    assert decoded_hints["distribution"]["strategy"] == "round-robin"
    assert len(decoded_hints["distribution"]["nodes"]) == 3

    print("✓ Distributed routing roundtrip successful")
    print(f"✓ Strategy: {decoded_hints['distribution']['strategy']}, Replicas: {decoded_hints['distribution']['replicas']}")
    print(f"✓ Target latency: {decoded_hints['performance']['target_latency_ms']}ms")
    return True


def test_sensor_data_stream():
    """Test IoT/sensor data stream (Sw codec)."""
    print("\n=== Testing Sensor Data Stream (Sw) ===")

    # Simulate accelerometer readings (100Hz, 3-axis)
    sample_rate = 100  # Hz
    duration = 1.0  # seconds
    num_samples = int(sample_rate * duration)

    # Each sample: (timestamp_ms, x, y, z)
    readings = []
    for i in range(num_samples):
        timestamp_ms = i * 10  # 10ms intervals
        x = 0.1 * i % 1.0
        y = 0.2 * i % 1.0
        z = 9.8 + (0.05 * i % 0.2)  # ~1g gravity
        readings.append((timestamp_ms, x, y, z))

    # Pack as binary
    sensor_data = struct.pack(f"{num_samples * 4}f", *[v for reading in readings for v in reading])

    metadata = {
        "sensor_type": "accelerometer",
        "sample_rate": sample_rate,
        "units": "m/s^2",
        "axes": ["x", "y", "z"],
        "calibration": {
            "offset": [0.01, -0.02, 0.03],
            "scale": [1.0, 1.0, 1.0]
        },
        "device": {
            "id": "sensor-001",
            "location": "wrist",
            "battery_percent": 85
        },
        "session": {
            "activity": "walking",
            "user_id": "user-123",
            "start_time": 1705315800000
        }
    }

    compressed = sw_compress(sensor_data, metadata=metadata)
    print(f"Original size: {len(sensor_data)} bytes ({num_samples} samples)")
    print(f"Compressed size: {len(compressed)} bytes")
    print(f"Compression ratio: {len(sensor_data) / len(compressed):.2f}x")

    decompressed_data, decoded_metadata = sw_decompress(compressed)

    assert decompressed_data == sensor_data
    assert decoded_metadata["sensor_type"] == "accelerometer"
    assert decoded_metadata["sample_rate"] == 100

    print("✓ Sensor data stream roundtrip successful")
    print(f"✓ Sensor: {decoded_metadata['sensor_type']}, Rate: {decoded_metadata['sample_rate']}Hz")
    print(f"✓ Axes: {', '.join(decoded_metadata['axes'])}")
    return True


def main():
    """Run all AI data roundtrip tests."""
    print("=" * 60)
    print("Testing AI Data Types Through Semantic Codecs")
    print("=" * 60)

    tests = [
        ("Vector Embeddings", test_vector_embeddings),
        ("Multimodal Embeddings", test_multimodal_embeddings),
        ("Audio Stream", test_audio_stream),
        ("Video Stream", test_video_stream),
        ("Training Data Table", test_training_data_table),
        ("Model Metrics Table", test_model_metrics_table),
        ("Routing Hints", test_routing_hints),
        ("Distributed Routing", test_distributed_inference_routing),
        ("Sensor Data Stream", test_sensor_data_stream),
    ]

    passed = 0
    failed = 0

    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            failed += 1
            print(f"✗ {name} FAILED: {e}")
            import traceback
            traceback.print_exc()

    print("\n" + "=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} tests")
    print("=" * 60)

    if failed == 0:
        print("\n🎉 All AI data types compress/decompress cleanly!")
        return 0
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
