from pathlib import Path

docs = {
 # ---------------- ACME (manufacturing) ----------------
 "acme/public/company_overview.txt":
  "Acme Manufacturing is a precision-parts maker founded in 1987 and headquartered in Pune. "
  "It has 2,400 employees and plants in Pune and Chennai. Products include gearboxes and hydraulic valves.",
 "acme/internal/leave_policy.txt":
  "Acme Leave Policy: employees get 18 days of paid leave per year plus 10 public holidays. "
  "Up to 9 unused days carry over. Requests go to the line manager through the AcmeHR portal "
  "at least 5 working days ahead. Maternity leave is 26 weeks and paternity leave is 10 days.",
 "acme/internal/onboarding_guide.txt":
  "Acme Onboarding: week 1 is safety training at Pune Plant 1, with badges issued at Security Desk B. "
  "Laptops are provisioned with the PROJECT-ANVIL VPN profile. Each new hire gets a mentor for 90 days. "
  "Probation lasts 6 months.",
 "acme/confidential/salary_sheet_fy2026.txt":
  "CONFIDENTIAL - Acme salary sheet FY2026. CEO Ramesh Iyer: 4.2 crore. CFO Sunita Rao: 2.8 crore. "
  "VP Engineering Priya Menon: 48 lakh. Plant manager Karthik Nair: 36 lakh. Annual bonus pool: 6.5 crore.",
 "acme/confidential/restructuring_plan.txt":
  "CONFIDENTIAL - Acme restructuring plan. Chennai Plant 3 will close by March 2027, affecting 310 employees, "
  "with 4 months severance. Acquisition target: Delta Gears Pvt Ltd for 85 crore, code name Operation Falcon.",

 # ---------------- GLOBEX (healthcare) ----------------
 "globex/public/company_overview.txt":
  "Globex Healthcare operates 14 hospitals across Karnataka and Tamil Nadu. Founded in 1999, it has "
  "6,100 staff. Its flagship is the Globex Heart Institute in Bengaluru.",
 "globex/internal/leave_policy.txt":
  "Globex Leave Policy: staff get 24 days of paid leave. Nurses on rotating shifts get 2 extra rest days "
  "per month. Night shift allowance is 1,200 rupees per night. Apply through the GlobexConnect portal.",
 "globex/internal/onboarding_guide.txt":
  "Globex Onboarding: infection control training on day 1, ward orientation on days 2 to 5, badges from the "
  "HR desk in Block C. New hires must submit hepatitis B vaccination proof.",
 "globex/confidential/salary_sheet_fy2026.txt":
  "CONFIDENTIAL - Globex salaries. CEO Farida Khan: 5.1 crore. Chief Medical Officer Dr. Anand Verma: 3.6 crore. "
  "Head of Cardiology Dr. Meera Pillai: 2.1 crore. Average senior nurse: 9.5 lakh.",
 "globex/confidential/strategy_and_incidents.txt":
  "CONFIDENTIAL - Globex plans to acquire Sunrise Clinics for 120 crore, code name Operation Lotus. "
  "A data breach in August 2026 exposed 8,400 patient records and has not yet been disclosed to regulators.",

 # ---------------- INITECH (finance) ----------------
 "initech/public/company_overview.txt":
  "Initech Finance is a mid-size NBFC founded in 2005 in Mumbai. It has 1,800 employees and 220 branches, "
  "offering personal loans, gold loans and insurance distribution.",
 "initech/internal/leave_policy.txt":
  "Initech Leave Policy: 20 days of paid leave and 12 sick days. Non-branch staff may work from home up to "
  "2 days per week. Approvals go through the InitechHub portal.",
 "initech/internal/onboarding_guide.txt":
  "Initech Onboarding: KYC and compliance training in week 1. Access to the LoanDesk Pro loan origination "
  "system is granted after an exam with an 80 percent pass mark.",
 "initech/confidential/salary_sheet_fy2026.txt":
  "CONFIDENTIAL - Initech salaries. MD Vikram Shah: 5.8 crore. Chief Risk Officer Neha Kapoor: 2.9 crore. "
  "Average branch manager: 18 lakh. Top sales bonus: 12 lakh to Arjun Desai.",
 "initech/confidential/strategy_and_risks.txt":
  "CONFIDENTIAL - Initech plans to lay off 260 back-office staff in Q2 2027. Undisclosed non-performing assets "
  "stand at 410 crore. Merger talks with Capstone Credit are code named Operation Harbor.",
}

for path, text in docs.items():
    out = Path("data") / path
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    print("wrote", out)