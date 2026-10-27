import shutil
from pathlib import Path

FAKE = {"company_overview", "leave_policy", "onboarding_guide", "salary_sheet_fy2026",
        "restructuring_plan", "strategy_and_incidents", "strategy_and_risks"}

for f in Path("data").glob("*/*/*.txt"):
    if f.stem in FAKE:
        dest = Path("tests/fixture_data") / f.relative_to("data")
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(f, dest)
        print("copied", dest)