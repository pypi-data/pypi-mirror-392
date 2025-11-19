from arua.compression.semantic import semantic_compress
from arua.compression.semantic_integrator import IntegratorConfig, SemanticIntegrator


def test_integrator_routes_to_cpu_and_decompresses() -> None:
    data = b"hello integrator"
    payload = semantic_compress(data, codec="Sa", domain_id=20)

    integrator = SemanticIntegrator()
    result = integrator.route_and_decompress(payload)

    assert result.backend_name == "cpu"
    assert result.value == data
    assert result.plan.codec_label == "Sa"
    assert result.header.domain_id == 20


def test_integrator_can_select_gpu_backend_stub() -> None:
    data = b"numeric Sq payload"
    payload = semantic_compress(data, codec="Sb", domain_id=21)

    integrator = SemanticIntegrator()
    result = integrator.route_and_decompress(payload, priority="high")

    assert result.backend_name in {"cpu", "gpu"}
    assert result.value == data
    assert result.duration_ms >= 0.0


def test_integrator_on_decision_callback_invoked() -> None:
    data = b"callback test"
    payload = semantic_compress(data, codec="Sa", domain_id=22)

    called = []

    def _cb(res):
        called.append((res.backend_name, res.header.domain_id))

    cfg = IntegratorConfig(on_decision=_cb)
    integrator = SemanticIntegrator(config=cfg)
    result = integrator.route_and_decompress(payload)

    assert result.value == data
    assert called == [("cpu", 22)]
