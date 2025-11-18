"""Goal statistic data class for tracking navigation statistics"""

from dataclasses import dataclass

from ara_api._utils.data.nav.goal_status import GoalStatus


@dataclass
class GoalStatistic:
    total_checks: int = 0
    goals_reached: int = 0
    success_rate: float = 0.0
    position_success_rate: float = 0.0
    position_reached_count: int = 0
    yaw_reached_count: int = 0
    z_ignored_count: int = 0
    yaw_ignored_count: int = 0
    yaw_success_rate: float = 0.0

    def reset(self):
        self.total_checks = 0
        self.goals_reached = 0
        self.success_rate = 0.0
        self.position_success_rate = 0.0
        self.position_reached_count = 0
        self.yaw_reached_count = 0
        self.z_ignored_count = 0
        self.yaw_ignored_count = 0
        self.yaw_success_rate = 0.0

    def update(self, status: GoalStatus):
        self.total_checks += 1
        if status.is_reached:
            self.goals_reached += 1
        if status.position_reached:
            self.position_reached_count += 1
        if status.yaw_reached:
            self.yaw_reached_count += 1
        # Check if z or yaw were ignored (value equals infinity)
        if status.distance_z == float("inf"):
            self.z_ignored_count += 1
        if status.yaw_diff == float("inf"):
            self.yaw_ignored_count += 1

        # Calculate success rates
        if self.total_checks > 0:
            self.success_rate = self.goals_reached / self.total_checks
            self.position_success_rate = (
                self.position_reached_count / self.total_checks
            )
            self.yaw_success_rate = self.yaw_reached_count / self.total_checks
