from dataclasses import dataclass
from datetime import datetime, timedelta
import random
import string


@dataclass
class OrderEstimate:
    order_id: str
    tracking_id: str
    estimated_delivery: datetime
    priority: str


class OrderUtils:
    """
    Utility class to help with order IDs, tracking IDs, and delivery estimates.
    Designed to be used inside your Django app and AWS Lambda.
    """

    def __init__(self, base_days: int = 3):
        self.base_days = base_days

    def generate_order_id(self, prefix: str = "ORD") -> str:
        ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        rand = ''.join(random.choices(string.digits, k=4))
        return f"{prefix}-{ts}{rand}"

    def generate_tracking_id(self, prefix: str = "TRK") -> str:
        rand = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        return f"{prefix}-{rand}"

    def estimate_delivery(
        self,
        distance_km: int,
        priority: str = "STANDARD"
    ) -> datetime:
        """
        Simple estimation:
        - STANDARD: base_days + distance_km / 300
        - EXPRESS: base_days - 1 (minimum 1 day)
        """
        if priority.upper() == "EXPRESS":
            days = max(1, self.base_days - 1)
        else:
            days = self.base_days + max(0, distance_km // 300)

        return datetime.utcnow() + timedelta(days=days)

    def create_order_estimate(
        self, distance_km: int, priority: str = "STANDARD"
    ) -> OrderEstimate:
        order_id = self.generate_order_id()
        tracking_id = self.generate_tracking_id()
        eta = self.estimate_delivery(distance_km, priority)
        return OrderEstimate(
            order_id=order_id,
            tracking_id=tracking_id,
            estimated_delivery=eta,
            priority=priority.upper(),
        )
