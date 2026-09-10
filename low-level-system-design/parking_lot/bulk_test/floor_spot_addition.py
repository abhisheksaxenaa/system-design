import argparse
import enum
import json
import random
import sys
import urllib.request
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

class SpotType(str, enum.Enum):
    COMPACT = "compact"
    LARGE = "large"
    # HANDICAPPED = "handicapped"
    MOTORCYCLE = "motorcycle"
    EV = "ev"



def create_random_spots(
    base_url: str,
    count: int,
    min_floor: int = 1,
    max_floor: int = 5,
    api_key: str = "admin-token",
) -> List[Dict[str, Any]]:
    """Create a batch of random parking spots via the admin API."""
    spot_types = [spot_type.value for spot_type in SpotType]
    created_spots: List[Dict[str, Any]] = []

    for _ in range(count):
        floor = random.randint(min_floor, max_floor)
        spot_type = random.choice(spot_types)
        request = urllib.request.Request(
            f"{base_url.rstrip('/')}/admin/spots",
            data=json.dumps({"floor": floor, "spot_type": spot_type}).encode("utf-8"),
            headers={"Content-Type": "application/json", "X-API-KEY": api_key},
            method="POST",
        )
        with urllib.request.urlopen(request, timeout=10) as response:
            created_spots.append(json.load(response))

    return created_spots


def main() -> None:
    parser = argparse.ArgumentParser(description="Create random parking spots in bulk")
    parser.add_argument("--count", type=int, default=10, help="Number of spots to create")
    parser.add_argument("--base-url", default="http://127.0.0.1:8000", help="Parking lot API base URL")
    parser.add_argument("--min-floor", type=int, default=1, help="Minimum floor number")
    parser.add_argument("--max-floor", type=int, default=2, help="Maximum floor number")
    parser.add_argument("--api-key", default="admin-token", help="Admin API key")
    args = parser.parse_args()

    created_spots = create_random_spots(
        base_url=args.base_url,
        count=args.count,
        min_floor=args.min_floor,
        max_floor=args.max_floor,
        api_key=args.api_key,
    )

    print(f"Created {len(created_spots)} spots successfully.")
    for spot in created_spots:
        print(f"- spot_id={spot['spot_id']} floor={spot['floor']} type={spot['spot_type']}")


if __name__ == "__main__":
    main()
