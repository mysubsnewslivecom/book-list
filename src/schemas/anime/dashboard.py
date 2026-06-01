from pydantic import BaseModel


class DashboardStatsResponse(BaseModel):
    watching: int
    completed: int
    on_hold: int
    dropped: int
    plan_to_watch: int
