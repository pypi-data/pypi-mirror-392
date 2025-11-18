from __future__ import annotations

from typing import ClassVar

from opentelemetry import metrics
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import Resource


class DaftInferenceMetrics:
    """Helper for configuring and updating OpenTelemetry metrics."""

    _provider_initialized: ClassVar[bool] = False

    def __init__(self, service_name: str, export_interval_millis: int = 1000) -> None:
        if not DaftInferenceMetrics._provider_initialized:
            resource = Resource.create(attributes={"service.name": service_name})
            exporter = OTLPMetricExporter()
            reader = PeriodicExportingMetricReader(exporter, export_interval_millis=export_interval_millis)
            provider = MeterProvider(resource=resource, metric_readers=[reader])
            try:
                metrics.set_meter_provider(provider)
            except RuntimeError:
                # A provider has already been registered elsewhere; reuse it.
                pass
            DaftInferenceMetrics._provider_initialized = True

        meter = metrics.get_meter(__name__)
        self._tokens_in = meter.create_counter(
            "daft.inference.tokens_in", description="The number of tokens input in to the model"
        )
        self._tokens_out = meter.create_counter(
            "daft.inference.tokens_out", description="The number of tokens output from the model"
        )
        self._tokens_total = meter.create_counter(
            "daft.inference.tokens_total", description="The number of tokens total from the model"
        )
        self._requests = meter.create_counter(
            "daft.inference.requests", description="The number of requests to the model"
        )

    def record(
        self,
        *,
        model: str,
        protocol: str,
        input_tokens: int | None = None,
        output_tokens: int | None = None,
        total_tokens: int | None = None,
    ) -> None:
        attributes = {"model": model, "protocol": protocol, "provider": "daft"}
        if input_tokens is not None:
            self._tokens_in.add(input_tokens, attributes=attributes)
        if output_tokens is not None:
            self._tokens_out.add(output_tokens, attributes=attributes)
        if total_tokens is not None:
            self._tokens_total.add(total_tokens, attributes=attributes)
        self._requests.add(1, attributes=attributes)


DAFT_INFERENCE_METRICS = DaftInferenceMetrics(service_name="daft")

__all__ = ["DAFT_INFERENCE_METRICS", "DaftInferenceMetrics"]
