"""Shared settings for lac-subnational."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw"            # downloads, not committed
PROCESSED = ROOT / "data" / "processed"  # committed
OUTPUT = ROOT / "output"

# The 33 Latin American and Caribbean member states of ECLAC.
COUNTRIES = {
    "ARG": "Argentina", "ATG": "Antigua and Barbuda", "BHS": "Bahamas", "BRB": "Barbados",
    "BLZ": "Belize", "BOL": "Bolivia", "BRA": "Brazil", "CHL": "Chile", "COL": "Colombia",
    "CRI": "Costa Rica", "CUB": "Cuba", "DMA": "Dominica", "DOM": "Dominican Republic",
    "ECU": "Ecuador", "SLV": "El Salvador", "GRD": "Grenada", "GTM": "Guatemala",
    "GUY": "Guyana", "HTI": "Haiti", "HND": "Honduras", "JAM": "Jamaica", "MEX": "Mexico",
    "NIC": "Nicaragua", "PAN": "Panama", "PRY": "Paraguay", "PER": "Peru",
    "KNA": "Saint Kitts and Nevis", "LCA": "Saint Lucia", "VCT": "Saint Vincent and the Grenadines",
    "SUR": "Suriname", "TTO": "Trinidad and Tobago", "URY": "Uruguay", "VEN": "Venezuela",
}

# Classes as in OECD Regions and Cities at a Glance: regional GDP per capita, national = 100.
BANDS = [(-1e9, 75, "≤ 75"), (75, 90, "> 75 to 90"), (90, 110, "> 90 to 110"), (110, 1e9, "> 110")]
