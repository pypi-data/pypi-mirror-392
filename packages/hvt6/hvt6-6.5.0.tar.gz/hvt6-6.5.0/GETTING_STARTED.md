# Getting Started with HVT6 (3 Minutes)

**Hardening Verification Tool (HVT6)** - Automated Cisco IOS/IOS-XE security auditing

---

## Prerequisites

- **Python 3.8+** (tested on 3.9, 3.10, 3.11)
- **pip** package manager
- **Git** (for installation)

---

## Quick Install (1 minute)

```bash
# 1. Clone the repository
git clone https://github.com/yourusername/ios-xe_hardening.git
cd ios-xe_hardening

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt
```

**Verify installation:**
```bash
python hvt6.py --help
```

You should see the HVT6 help message with all available options.

---

## Your First Audit (2 minutes)

### Option 1: Try with Sample Data

```bash
# Test with the provided example configurations
python hvt6.py --repo-dir examples/configs --customer "Test Company" --dry-run

# Generate all report formats
python hvt6.py --repo-dir examples/configs --customer "Test Company" \
    --generate-pdf --generate-excel

# View results
open index.html  # macOS
xdg-open index.html  # Linux
start index.html  # Windows
```

### Option 2: Audit Your Own Devices

**Step 1: Prepare Configuration Files**

For each device, place these 3 files in the `./repo/` directory:
- `{hostname}_sh_ver.txt` - Output of `show version`
- `{hostname}_sh_inv.txt` - Output of `show inventory`
- `{hostname}_sh_run.cfg` - Output of `show running-config`

Example:
```
repo/
├── router1_sh_ver.txt
├── router1_sh_inv.txt
├── router1_sh_run.cfg
├── switch1_sh_ver.txt
├── switch1_sh_inv.txt
└── switch1_sh_run.cfg
```

**Step 2: Run the Audit**

```bash
# Basic audit (HTML + CSV)
python hvt6.py --customer "Your Company"

# Full audit (HTML + CSV + PDF + Excel)
python hvt6.py --customer "Your Company" --generate-pdf --generate-excel
```

**Step 3: View Reports**

```bash
# Open master dashboard
open index.html

# Individual device reports
open reports/router1_20251114.html

# Comprehensive PDF report
open results/Security_Audit_Your_Company_20251114.pdf

# Excel with pivot tables
open results/Security_Audit_Your_Company_20251114.xlsx
```

---

## Understanding the Output

### Generated Files

| File | Description | Best For |
|------|-------------|----------|
| `index.html` | Master dashboard with all devices | Quick overview |
| `reports/{device}_{date}.html` | Individual device report with check details | Deep dive per device |
| `results/Security_Audit_{customer}_{date}.pdf` | Professional client-ready PDF (130 pages for 12 devices) | Executive review, client delivery |
| `results/Security_Audit_{customer}_{date}.xlsx` | Excel with 3 sheets (Summary, Devices, Check Results) | Data analysis, pivot tables |
| `results/hostnames.csv` | Simple CSV with device scores | Import to other tools |

### Report Sections

1. **Executive Summary** - Overall security grade (A-F), total devices, average score
2. **Device Summary Table** - All devices with scores and grades
3. **Category Performance** - Scores by security category (General, Access, Control, etc.)
4. **Individual Device Reports** - Detailed check results per device
5. **Top 5 Critical Findings** - Highest priority issues across all devices (PDF only)
6. **Prioritized Recommendations** - Remediation steps sorted by impact (PDF only)

### Security Grading Scale

| Grade | Percentage | Status |
|-------|-----------|--------|
| A | 90-100% | Excellent |
| B | 80-89% | Good |
| C | 70-79% | Acceptable |
| D | 60-69% | Needs Improvement |
| F | <60% | Critical Issues |

---

## Next Steps

### Learn More

- **Full Documentation**: [README.md](README.md) - Complete feature guide (1,200 lines)
- **Security Configuration**: [SECURITY.md](SECURITY.md) - Credential management best practices
- **Collection Guide**: [collector/README.md](collector/README.md) - Automated configuration collection
- **Architecture**: [CLAUDE.md](CLAUDE.md) - Developer guide and system architecture

### Advanced Features

**Automated Collection:**
```bash
# Collect configs from all devices in inventory
python collect.py --all

# Then run audit
python hvt6.py --customer "Your Company" --generate-pdf --generate-excel
```

**Environment Variables (Secure Credentials):**
```bash
# Create .env file (see .env.example)
cp .env.example .env
nano .env

# Use encrypted credentials
python hvt6.py --customer "Your Company"
```

**Dry Run (Validation Only):**
```bash
# Test without generating reports
python hvt6.py --dry-run
```

**Verbose Logging:**
```bash
# See detailed check execution
python hvt6.py --verbose --customer "Your Company"
```

---

## Troubleshooting

### Common Issues

**1. No devices found**
```
ERROR: No device file groups found in repo/
```
**Solution:** Ensure files follow naming convention `{hostname}_sh_run.cfg`, `{hostname}_sh_ver.txt`, `{hostname}_sh_inv.txt`

**2. Version warning**
```
WARNING: La versión 15.2(4)M10 está por debajo de la línea base...
```
**Solution:** This is informational only. Audit continues but checks may not fully apply to old versions.

**3. Template rendering errors**
```
ERROR: jinja2.exceptions.TemplateNotFound: device_report.j2
```
**Solution:** Ensure `templates/` directory exists with all required templates.

**4. Module not found**
```
ModuleNotFoundError: No module named 'openpyxl'
```
**Solution:** Reinstall dependencies: `pip install -r requirements.txt`

### Get Help

- **GitHub Issues**: https://github.com/yourusername/ios-xe_hardening/issues
- **Documentation**: Full troubleshooting guide in [README.md](README.md) lines 1064-1141
- **Examples**: Sample configurations in `examples/` directory

---

## What HVT6 Checks

**65+ security checks across 5 categories:**

- **General (21 checks)** - Infrastructure basics, IOS version compliance
- **Access Control (15 checks)** - AAA, SSH, VTY, login banners
- **Control Plane (12 checks)** - Routing protocol security, infrastructure ACLs
- **Management (10 checks)** - SNMP, NTP, logging, service hardening
- **Data Plane (7 checks)** - Interface security, unused ports, DHCP snooping

**Based on:**
- Cisco IOS-XE Hardening Guide
- CIS Benchmarks
- DISA STIG V-215846+
- NIST SP 800-53

---

## Quick Reference Commands

```bash
# Standard audit
python hvt6.py --customer "Company"

# Full report package (HTML + PDF + Excel)
python hvt6.py --customer "Company" --generate-pdf --generate-excel

# Validation only (no reports)
python hvt6.py --dry-run

# Verbose mode
python hvt6.py --verbose

# Custom directories
python hvt6.py --repo-dir /path/to/configs --output-dir /path/to/reports

# Collect then audit
python collect.py --all && python hvt6.py --customer "Company"
```

---

**Ready to dive deeper?** → Read the full [README.md](README.md) for all features and advanced usage.
