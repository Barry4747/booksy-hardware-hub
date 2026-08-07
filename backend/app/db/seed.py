import json
import logging
from datetime import datetime
import os
import difflib
from app.db.base import SessionLocal, engine
from app.models import Base
from app.models.hardware import Hardware, HardwareStatus
Base.metadata.create_all(bind=engine)

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger(__name__)

KNOWN_BRANDS = {"apple", "samsung", "dell", "razer", "logitech", "sony", "lenovo"}


def detect_brand_typo(brand: str) -> bool:
    brand_lower = brand.lower()
    if brand_lower in KNOWN_BRANDS:
        return False
    matches = difflib.get_close_matches(brand_lower, KNOWN_BRANDS, n=1, cutoff=0.7)
    return len(matches) > 0


def parse_date(date_str: str | None, item_id: int) -> tuple[datetime | None, bool]:
    if not date_str:
        return None, False

    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date(), False
    except ValueError:
        pass

    try:
        parsed = datetime.strptime(date_str, "%d-%m-%Y").date()
        logger.info(
            f"ANOMALY DETECTED ID {item_id}: "
            f"Parsed incorrectly formatted date '{date_str}' to {parsed}"
        )
        return parsed, True
    except ValueError:
        pass

    logger.info(f"ANOMALY DETECTED ID {item_id}: Unrecognized date format '{date_str}', skipping date.")
    return None, True


def run_seed():
    seed_file_path = os.path.join(os.path.dirname(__file__), "seed_data.json")

    if not os.path.exists(seed_file_path):
        logger.error(f"Seed file not found at {seed_file_path}")
        return

    with open(seed_file_path, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except json.JSONDecodeError:
            logger.error("Failed to parse seed_data.json")
            return

    inserted = 0
    skipped = 0
    anomalies = 0

    seen_ids = set()
    db = SessionLocal()
    try:
        for item in data:
            item_id = item.get("id")

            # 1. Duplicate IDs
            if item_id:
                if item_id in seen_ids:
                    logger.info(f"SKIPPED ID {item_id}: Duplicate ID found within seed data.")
                    skipped += 1
                    continue
                
                seen_ids.add(item_id)
                
                existing = db.query(Hardware).filter(Hardware.id == item_id).first()
                if existing:
                    logger.info(f"SKIPPED ID {item_id}: Duplicate ID already exists in database.")
                    skipped += 1
                    continue

            # 2. Handle assignedTo and history fields
            item.pop("assignedTo", None)

            notes = item.get("notes") or ""
            if "history" in item:
                history_info = item.pop("history")
                notes = f"{notes}\nHistory: {history_info}".strip() if notes else f"History: {history_info}"

            # 3. Unknown or invalid status
            raw_status = item.get("status")
            try:
                status = HardwareStatus(raw_status) if raw_status else HardwareStatus.AVAILABLE
            except ValueError:
                logger.info(
                    f"SKIPPED ID {item_id}: Unknown status '{raw_status}'. "
                    f"Decision: skipped — status is strictly typed and non-nullable in DB."
                )
                skipped += 1
                anomalies += 1
                continue

            # 4. Missing or empty brand
            brand = (item.get("brand") or "").strip()
            if not brand:
                logger.info(f"ANOMALY DETECTED ID {item_id}: Missing or empty brand.")
                anomalies += 1

            # 5. Brand typo detection
            elif detect_brand_typo(brand):
                logger.info(f"ANOMALY DETECTED ID {item_id}: Possible typo in brand name '{brand}'.")
                anomalies += 1

            # 6. Purchase date parsing and future date check
            raw_date = item.get("purchaseDate") or item.get("purchase_date")
            purchase_date, date_anomaly = parse_date(raw_date, item_id)
            if date_anomaly:
                anomalies += 1

            if purchase_date and purchase_date > datetime.now().date():
                logger.info(f"ANOMALY DETECTED ID {item_id}: Purchase date {purchase_date} is in the future.")
                anomalies += 1

            # 7. Damage notes with Available status
            if status == HardwareStatus.AVAILABLE and notes and "damage" in notes.lower():
                logger.info(
                    f"ANOMALY DETECTED ID {item_id}: Status is 'Available' but damage "
                    f"mentioned in notes. Potential audit issue."
                )
                anomalies += 1

            hardware = Hardware(
                id=item_id,
                name=item.get("name") or "Unknown Device",
                brand=brand,
                purchase_date=purchase_date,
                status=status,
                notes=notes or None,
            )

            db.add(hardware)
            inserted += 1

        db.commit()

    except Exception as e:
        logger.error(f"Failed to commit to database: {e}")
        db.rollback()
    finally:
        db.close()

    logger.info("-" * 50)
    logger.info("Seed Summary:")
    logger.info(f"  Items inserted:  {inserted}")
    logger.info(f"  Items skipped:   {skipped}")
    logger.info(f"  Anomalies found: {anomalies}")
    logger.info("-" * 50)


if __name__ == "__main__":
    run_seed()