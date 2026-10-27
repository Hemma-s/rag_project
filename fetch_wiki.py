import wikipediaapi
from pathlib import Path

wiki = wikipediaapi.Wikipedia(
    user_agent="securedocs-project (hemxx04@gmail.com)",
    language="en",
)

topics = {
    "acme": ["Manufacturing", "Supply chain", "Lean manufacturing", "Six Sigma",
             "Quality control", "Industrial robot", "3D printing",
             "Just-in-time manufacturing", "Automotive industry", "Steel",
             "Warehouse", "Logistics"],
    "globex": ["Diabetes", "Hypertension", "Clinical trial", "Pharmacology",
               "Hospital", "Vaccine", "Antibiotic", "Cardiology",
               "Public health", "Nursing", "Medical imaging", "Surgery"],
    "initech": ["Bank", "Insurance", "Stock market", "Mutual fund",
                "Credit score", "Inflation", "Mortgage loan", "Bond (finance)",
                "Audit", "Taxation", "Venture capital", "Accounting"],
}

for tenant, pages in topics.items():
    for i, title in enumerate(pages):
        level = "public" if i < 6 else "internal"
        page = wiki.page(title)
        if not page.exists():
            print("MISSING", tenant, title)
            continue
        name = title.replace(" ", "_").replace("(", "").replace(")", "")
        out = Path(f"data/{tenant}/{level}/{name}.txt")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(page.text, encoding="utf-8")
        print("saved", tenant, level, title)