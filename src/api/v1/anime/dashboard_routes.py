from fastapi import APIRouter

from schemas.anime.dashboard import DashboardStatsResponse

from .deps import WatchEntryServiceDep

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStatsResponse)
def get_stats(service: WatchEntryServiceDep):
    stats = service.dashboard_stats()
    return DashboardStatsResponse(**stats)
