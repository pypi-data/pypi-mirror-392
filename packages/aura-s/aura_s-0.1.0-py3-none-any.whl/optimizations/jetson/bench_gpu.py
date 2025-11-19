import time
import torch
import numpy as np
import grok_gpu


def bench_semantic_grain_gpu(
    data_bytes=1024, batch_size=32, use_trt=False
):  # Jetson-optimized benchmarking
    # Batched small tensors
    batch_data = torch.randint(
        0, 256, (batch_size, data_bytes), dtype=torch.uint8, device="cuda"
    )
    batch_matches = torch.zeros(
        (batch_size, data_bytes, 2), dtype=torch.int32, device="cuda"
    )

    if use_trt:
        from trt_integration import infer_trt

        # Warmup
        infer_trt("semantic_grain.trt", batch_data)

        start = time.time()
        for _ in range(10):
            infer_trt("semantic_grain.trt", batch_data)
        end = time.time()
    else:
        # Warmup
        grok_gpu.semantic_grain_match_batch(
            batch_data, batch_matches, window_size=4096, batch_size=batch_size
        )

        start = time.time()
        for _ in range(10):  # Average over runs
            grok_gpu.semantic_grain_match_batch(
                batch_data, batch_matches, window_size=4096, batch_size=batch_size
            )
        end = time.time()

    total_bytes = batch_size * data_bytes * 10
    mode = "TensorRT" if use_trt else "CUDA"
    print(
        f"GPU Semantic Grain ({mode}) time: {(end - start)/10:.4f}s avg per batch, throughput: {total_bytes / (end - start):.2f} bytes/s"
    )


def bench_prng_gpu(num_elements=1024, batch_size=32):
    total_elements = num_elements * batch_size
    output = torch.zeros((total_elements,), dtype=torch.uint64, device="cuda")

    # Warmup
    grok_gpu.prng_generate(output, seed=42, num_elements=total_elements)

    start = time.time()
    for _ in range(10):
        grok_gpu.prng_generate(output, seed=42, num_elements=total_elements)
    end = time.time()

    print(
        f"GPU PRNG time: {(end - start)/10:.4f}s avg, throughput: {total_elements * 10 / (end - start):.2f} rand64/s"
    )


def cpu_baseline_semantic_grain(data_bytes=1024):
    data = np.random.randint(0, 256, data_bytes, dtype=np.uint8)
    start = time.time()
    # Simple CPU match (placeholder)
    for i in range(data_bytes):
        pass  # Simulate work
    end = time.time()
    print(f"CPU Semantic Grain sim time: {end - start:.4f}s for {data_bytes} bytes")


if __name__ == "__main__":
    if not torch.cuda.is_available():
        print("CUDA not available; running CPU baseline.")
        cpu_baseline_semantic_grain()
    else:
        bench_semantic_grain_gpu()
        bench_prng_gpu()
