import torch
import tensorrt as trt
from tensorrt import ICudaEngine, IExecutionContext
from torch.onnx import export as onnx_export
import numpy as np
import pycuda.driver as cuda
import pycuda.autoinit


class SemanticGrainModel(torch.nn.Module):
    def forward(self, data):
        return data  # Placeholder


def build_trt_engine(onnx_path: str, engine_path: str):
    logger = trt.Logger(trt.Logger.WARNING)
    builder = trt.Builder(logger)
    network = builder.create_network(
        1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH)
    )
    parser = trt.OnnxParser(network, logger)

    with open(onnx_path, "rb") as f:
        if not parser.parse(f.read()):
            raise RuntimeError("Failed to parse ONNX")

    config = builder.create_builder_config()
    config.max_workspace_size = 1 << 32  # 4GB for RTX
    config.set_flag(trt.BuilderFlag.FP16)
    config.set_flag(trt.BuilderFlag.TF32)  # TensorFloat-32 for perf
    engine = builder.build_serialized_network(network, config)

    with open(engine_path, "wb") as f:
        f.write(engine)


def infer_trt(engine_path: str, input_data: torch.Tensor) -> np.ndarray:
    with open(engine_path, "rb") as f:
        engine_ser = f.read()

    runtime = trt.Runtime(trt.Logger(trt.Logger.WARNING))
    engine: ICudaEngine = runtime.deserialize_cuda_engine(engine_ser)
    context: IExecutionContext = engine.create_execution_context()

    input_shape = input_data.shape
    context.set_binding_shape(0, input_shape)

    input_size = trt.volume(input_shape) * trt.int32.itemsize
    d_input = cuda.mem_alloc(input_size)
    output_shape = input_shape
    output_size = trt.volume(output_shape) * trt.int32.itemsize
    d_output = cuda.mem_alloc(output_size)
    h_output = np.empty(output_shape, dtype=np.int32)

    cuda.memcpy_htod(d_input, input_data.cpu().numpy())

    bindings = [int(d_input), int(d_output)]
    context.execute_v2(bindings)

    cuda.memcpy_dtoh(h_output, d_output)

    return h_output


if __name__ == "__main__":
    model = SemanticGrainModel()
    dummy_input = torch.randint(0, 256, (1, 1024), dtype=torch.uint8).cuda()
    onnx_export(model, dummy_input, "semantic_grain.onnx")
    build_trt_engine("semantic_grain.onnx", "semantic_grain.trt")
    result = infer_trt("semantic_grain.trt", dummy_input)
    print("Inference result shape:", result.shape)
