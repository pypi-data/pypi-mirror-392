import time
import torch
import numpy as np
import grok_gpu


def bench_semantic_grain_gpu(data_bytes=1024, batch_size=32, use_trt=False):
    batch_data = torch.randint(
        0, 256, (batch_size, data_bytes), dtype=torch.uint8, device="cuda"
    )
    batch_matches = torch.zeros(
        (batch_size, data_bytes, 2), dtype=torch.int32, device="cuda"
    )

    if use_trt:
        from trt_integration import infer_trt

        infer_trt("semantic_grain.trt", batch_data)  # Warmup

        start = time.time()
        for _ in range(10):
            infer_trt("semantic_grain.trt", batch_data)
        end = time.time()
    else:
        grok_gpu.semantic_grain_match_batch(
            batch_data, batch_matches, window_size=4096, batch_size=batch_size
        )  # Warmup

        start = time.time()
        for _ in range(10):
            grok_gpu.semantic_grain_match_batch(
                batch_data, batch_matches, window_size=4096, batch_size=batch_size
            )
        end = time.time()

    total_bytes = batch_size * data_bytes * 10
    mode = "TensorRT" if use_trt else "CUDA"
    print(
        f"RTX GPU Semantic Grain ({mode}) time: {(end - start)/10:.4f}s avg, throughput: {total_bytes / (end - start):.2f} bytes/s"
    )


# Similar for prng
