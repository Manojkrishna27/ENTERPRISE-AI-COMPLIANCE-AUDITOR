import time

# Prometheus metric collectors
HTTP_REQUESTS_TOTAL = {"count": 0, "by_endpoint": {}, "by_status": {}}

AI_INFERENCE_LATENCY = []
QDRANT_QUERY_LATENCY = []


def record_http_request(endpoint: str, status_code: int, duration: float):
    HTTP_REQUESTS_TOTAL["count"] += 1
    HTTP_REQUESTS_TOTAL["by_endpoint"][endpoint] = (
        HTTP_REQUESTS_TOTAL["by_endpoint"].get(endpoint, 0) + 1
    )
    HTTP_REQUESTS_TOTAL["by_status"][str(status_code)] = (
        HTTP_REQUESTS_TOTAL["by_status"].get(str(status_code), 0) + 1
    )


def record_ai_inference(provider: str, duration: float):
    AI_INFERENCE_LATENCY.append(
        {"provider": provider, "duration": duration, "time": time.time()}
    )


def record_qdrant_query(collection: str, duration: float):
    QDRANT_QUERY_LATENCY.append(
        {"collection": collection, "duration": duration, "time": time.time()}
    )


def generate_prometheus_metrics() -> str:
    lines = [
        "# HELP http_requests_total Total number of HTTP requests processed.",
        "# TYPE http_requests_total counter",
        f"http_requests_total {HTTP_REQUESTS_TOTAL['count']}",
    ]

    for status_code, count in HTTP_REQUESTS_TOTAL["by_status"].items():
        lines.append(f'http_requests_by_status{{code="{status_code}"}} {count}')

    for endpoint, count in HTTP_REQUESTS_TOTAL["by_endpoint"].items():
        lines.append(f'http_requests_by_endpoint{{path="{endpoint}"}} {count}')

    lines.extend(
        [
            "# HELP ai_inference_requests_total Total AI inference calls.",
            "# TYPE ai_inference_requests_total counter",
            f"ai_inference_requests_total {len(AI_INFERENCE_LATENCY)}",
        ]
    )

    lines.extend(
        [
            "# HELP qdrant_queries_total Total Qdrant vector queries.",
            "# TYPE qdrant_queries_total counter",
            f"qdrant_queries_total {len(QDRANT_QUERY_LATENCY)}",
        ]
    )

    return "\n".join(lines) + "\n"
