import json

from fastapi import APIRouter
from opentelemetry import trace

from schemas.anime.dashboard import DashboardStatsResponse

from .deps import WatchEntryServiceDep

tracer = trace.get_tracer(__name__)

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
def get_stats(service: WatchEntryServiceDep):
    with tracer.start_as_current_span("api.anime.dashboard.stats") as span:
        stats = service.dashboard_stats()
        span.set_attribute("stats", json.dumps(stats))
        return DashboardStatsResponse(**stats)
