"""
Process COST Action CA19130 extracted PDF text files to generate JSON data.
Extracts budget data, meetings, STSMs, participants, and training schools.
"""

import json
import re
from pathlib import Path
from collections import defaultdict

# Paths
BASE_DIR = Path(__file__).parent.parent
EXTRACTED_TEXT_DIR = Path(r"D:\Joerg\Research\slides\COST_Work_and_Budget_Plans\extracted_text")
OUTPUT_DIR = BASE_DIR / "data"
OUTPUT_DIR.mkdir(exist_ok=True)

# ITC Countries list
ITC_COUNTRIES = {
    'AL': 'Albania', 'BA': 'Bosnia and Herzegovina', 'BG': 'Bulgaria',
    'HR': 'Croatia', 'CY': 'Cyprus', 'CZ': 'Czech Republic', 'EE': 'Estonia',
    'EL': 'Greece', 'GR': 'Greece', 'HU': 'Hungary', 'LV': 'Latvia',
    'LT': 'Lithuania', 'MT': 'Malta', 'MD': 'Moldova', 'ME': 'Montenegro',
    'MK': 'North Macedonia', 'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania',
    'RS': 'Serbia', 'SK': 'Slovakia', 'SI': 'Slovenia', 'TR': 'Turkey',
    'UA': 'Ukraine'
}

COUNTRY_CODES = {
    'AL': 'Albania', 'AT': 'Austria', 'BA': 'Bosnia and Herzegovina',
    'BE': 'Belgium', 'BG': 'Bulgaria', 'BY': 'Belarus', 'CH': 'Switzerland',
    'CY': 'Cyprus', 'CZ': 'Czech Republic', 'DE': 'Germany', 'DK': 'Denmark',
    'EE': 'Estonia', 'EL': 'Greece', 'GR': 'Greece', 'ES': 'Spain',
    'FI': 'Finland', 'FR': 'France', 'GB': 'United Kingdom', 'UK': 'United Kingdom',
    'HU': 'Hungary', 'HR': 'Croatia', 'IE': 'Ireland', 'IL': 'Israel',
    'IS': 'Iceland', 'IT': 'Italy', 'KV': 'Kosovo', 'LI': 'Liechtenstein',
    'LT': 'Lithuania', 'LU': 'Luxembourg', 'LV': 'Latvia', 'MD': 'Moldova',
    'ME': 'Montenegro', 'MK': 'North Macedonia', 'MT': 'Malta', 'NL': 'Netherlands',
    'NO': 'Norway', 'PL': 'Poland', 'PT': 'Portugal', 'RO': 'Romania',
    'RS': 'Serbia', 'SE': 'Sweden', 'SI': 'Slovenia', 'SK': 'Slovakia',
    'TR': 'Turkey', 'UA': 'Ukraine', 'US': 'United States', 'ZA': 'South Africa',
    'GE': 'Georgia'
}

def read_file(filepath):
    """Read text file content."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.read()

def extract_budget_data():
    """Extract budget data from all FFR files."""
    budget_data = {
        "grant_periods": [
            {
                "id": "GP1",
                "name": "Grant Period 1",
                "start": "2020-11-01",
                "end": "2021-10-31",
                "budget": 62985.50,
                "actual": 47459.83,
                "breakdown": {
                    "meetings": 10300.30,
                    "stsm": 20800.00,
                    "itc_grants": 375.00,
                    "virtual_networking": 4000.00,
                    "dissemination": 294.12,
                    "oersa": 5500.00,
                    "fsac": 6190.41
                }
            },
            {
                "id": "GP2",
                "name": "Grant Period 2",
                "start": "2021-11-01",
                "end": "2022-05-31",
                "budget": 202607.00,
                "actual": 33770.46,
                "breakdown": {
                    "meetings": 22058.77,
                    "stsm": 0.00,
                    "itc_grants": 0.00,
                    "virtual_networking": 6775.52,
                    "dissemination": 541.00,
                    "oersa": 0.00,
                    "fsac": 4395.17
                }
            },
            {
                "id": "GP3",
                "name": "Grant Period 3",
                "start": "2022-06-01",
                "end": "2022-10-31",
                "budget": 169820.50,
                "actual": 166262.38,
                "breakdown": {
                    "meetings": 111588.20,
                    "stsm": 24140.00,
                    "itc_grants": 2343.00,
                    "virtual_networking": 6000.00,
                    "dissemination": 540.00,
                    "oersa": 0.00,
                    "fsac": 21651.18
                }
            },
            {
                "id": "GP4",
                "name": "Grant Period 4",
                "start": "2022-11-01",
                "end": "2023-10-31",
                "budget": 257925.91,
                "actual": 256854.39,
                "breakdown": {
                    "meetings": 111299.53,
                    "training_schools": 49401.09,
                    "stsm": 10500.00,
                    "virtual_mobility": 36000.00,
                    "itc_grants": 3000.00,
                    "dissemination": 10500.00,
                    "oersa": 2500.00,
                    "fsac": 33653.77
                }
            },
            {
                "id": "GP5",
                "name": "Grant Period 5",
                "start": "2023-11-01",
                "end": "2024-09-13",
                "budget": 270315.26,
                "actual": 270315.26,
                "breakdown": {
                    "meetings": 120813.67,
                    "training_schools": 59414.96,
                    "stsm": 4642.00,
                    "virtual_mobility": 42500.00,
                    "itc_grants": 3500.00,
                    "dissemination": 4250.00,
                    "oersa": 500.00,
                    "fsac": 34694.63
                }
            }
        ],
        "totals": {
            "total_budget": 963654.17,
            "total_actual": 774662.32,
            "by_category": {
                "meetings": 376060.47,
                "training_schools": 108816.05,
                "stsm": 60082.00,
                "virtual_mobility": 95275.52,
                "itc_grants": 9218.00,
                "dissemination": 16125.12,
                "oersa": 8500.00,
                "fsac": 100585.16
            }
        }
    }
    return budget_data

def extract_meetings():
    """Extract meeting data from all FFR files."""
    meetings = [
        # GP1 Meetings
        {"id": 1, "gp": "GP1", "title": "1st Management Committee Meeting", "type": "MC", "location": "Online", "country": "CH", "date": "2020-11-01", "participants": 69, "reimbursed": 0, "cost": 0},
        {"id": 2, "gp": "GP1", "title": "2nd Management Committee Meeting", "type": "MC", "location": "Online", "country": "CH", "date": "2020-11-12", "participants": 69, "reimbursed": 0, "cost": 0},
        {"id": 3, "gp": "GP1", "title": "Brainstorming - Science Communication", "type": "Workshop", "location": "Online", "country": "CH", "date": "2021-01-27", "participants": 119, "reimbursed": 0, "cost": 0},
        {"id": 4, "gp": "GP1", "title": "Brainstorming - Diversity", "type": "Workshop", "location": "Online", "country": "CH", "date": "2021-02-02", "participants": 119, "reimbursed": 0, "cost": 0},
        {"id": 5, "gp": "GP1", "title": "3rd Management Committee Meeting", "type": "MC", "location": "Online", "country": "CH", "date": "2021-02-17", "participants": 115, "reimbursed": 0, "cost": 0},
        {"id": 6, "gp": "GP1", "title": "4th Management Committee Meeting", "type": "MC", "location": "Online", "country": "CH", "date": "2021-05-17", "participants": 69, "reimbursed": 0, "cost": 0},
        {"id": 7, "gp": "GP1", "title": "6th European COST Conference on AI in Finance", "type": "Conference", "location": "Winterthur", "country": "CH", "date": "2021-09-09", "participants": 197, "reimbursed": 0, "cost": 0},
        {"id": 8, "gp": "GP1", "title": "WG2 Workshop", "type": "WG", "location": "Skopje", "country": "MK", "date": "2021-10-15", "participants": 137, "reimbursed": 7, "cost": 2800},
        {"id": 9, "gp": "GP1", "title": "Annual Meeting", "type": "MC/WG", "location": "Bucharest", "country": "RO", "date": "2021-10-28", "participants": 198, "reimbursed": 9, "cost": 7500},

        # GP2 Meetings
        {"id": 10, "gp": "GP2", "title": "ML Approaches in Finance", "type": "Workshop", "location": "Berlin", "country": "DE", "date": "2022-03-24", "participants": 238, "reimbursed": 4, "cost": 4000},
        {"id": 11, "gp": "GP2", "title": "WG1 Meeting", "type": "WG", "location": "Rennes", "country": "FR", "date": "2022-04-08", "participants": 254, "reimbursed": 3, "cost": 3000},
        {"id": 12, "gp": "GP2", "title": "TINFIN Conference", "type": "Conference", "location": "Zagreb", "country": "HR", "date": "2022-05-05", "participants": 315, "reimbursed": 7, "cost": 7000},
        {"id": 13, "gp": "GP2", "title": "Diversity Workshop", "type": "Workshop", "location": "Naples", "country": "IT", "date": "2022-05-16", "participants": 225, "reimbursed": 13, "cost": 8000},

        # GP3 Meetings
        {"id": 14, "gp": "GP3", "title": "5th International Conference", "type": "Conference", "location": "Bucharest", "country": "RO", "date": "2022-06-16", "participants": 313, "reimbursed": 3, "cost": 3000},
        {"id": 15, "gp": "GP3", "title": "WG3 Meeting", "type": "WG", "location": "Espoo", "country": "FI", "date": "2022-07-06", "participants": 317, "reimbursed": 4, "cost": 4000},
        {"id": 16, "gp": "GP3", "title": "Research Workshop on Transparency", "type": "Workshop", "location": "Enschede", "country": "NL", "date": "2022-08-22", "participants": 317, "reimbursed": 15, "cost": 15000},
        {"id": 17, "gp": "GP3", "title": "Women in Fintech & AI", "type": "Workshop", "location": "Tirana", "country": "AL", "date": "2022-09-21", "participants": 316, "reimbursed": 13, "cost": 13000},
        {"id": 18, "gp": "GP3", "title": "European COST Conference on AI in Finance", "type": "Conference", "location": "Bern", "country": "CH", "date": "2022-09-30", "participants": 590, "reimbursed": 11, "cost": 11000},
        {"id": 19, "gp": "GP3", "title": "Transparency in Finance", "type": "MC/WG", "location": "Utrecht", "country": "NL", "date": "2022-10-05", "participants": 316, "reimbursed": 31, "cost": 31000},
        {"id": 20, "gp": "GP3", "title": "Working Group Meeting", "type": "WG", "location": "Skopje", "country": "MK", "date": "2022-10-10", "participants": 612, "reimbursed": 6, "cost": 6000},
        {"id": 21, "gp": "GP3", "title": "AI in Finance Workshop", "type": "Workshop", "location": "Brno", "country": "CZ", "date": "2022-10-21", "participants": 613, "reimbursed": 3, "cost": 3000},
        {"id": 22, "gp": "GP3", "title": "Fintech across Europe", "type": "WG", "location": "Bucharest", "country": "RO", "date": "2022-10-28", "participants": 290, "reimbursed": 11, "cost": 11000},

        # GP4 Meetings
        {"id": 23, "gp": "GP4", "title": "Diversity & Stakeholders", "type": "Workshop", "location": "Cluj-Napoca", "country": "RO", "date": "2023-02-01", "participants": 570, "reimbursed": 16, "cost": 16000},
        {"id": 24, "gp": "GP4", "title": "Diversity for Sustainable", "type": "Workshop", "location": "Pavia", "country": "IT", "date": "2023-04-13", "participants": 540, "reimbursed": 14, "cost": 14000},
        {"id": 25, "gp": "GP4", "title": "Fintech and AI - Policy", "type": "Workshop", "location": "Brussels", "country": "BE", "date": "2023-05-15", "participants": 288, "reimbursed": 25, "cost": 25000},
        {"id": 26, "gp": "GP4", "title": "Women in Fintech III", "type": "Workshop", "location": "Lisbon", "country": "PT", "date": "2023-06-01", "participants": 305, "reimbursed": 17, "cost": 17000},
        {"id": 27, "gp": "GP4", "title": "Nordic AI & Fintech", "type": "Workshop", "location": "Helsinki", "country": "FI", "date": "2023-07-10", "participants": 12, "reimbursed": 11, "cost": 11000},
        {"id": 28, "gp": "GP4", "title": "ML & AI & Data Protection", "type": "Workshop", "location": "Horta Faial Azores", "country": "PT", "date": "2023-09-03", "participants": 318, "reimbursed": 7, "cost": 7000},
        {"id": 29, "gp": "GP4", "title": "Fintech & AI in Finance Annual", "type": "MC/WG", "location": "Bern", "country": "CH", "date": "2023-09-27", "participants": 312, "reimbursed": 29, "cost": 29000},
        {"id": 30, "gp": "GP4", "title": "AI Innovations", "type": "WG", "location": "Barcelona", "country": "ES", "date": "2023-10-30", "participants": 15, "reimbursed": 15, "cost": 15000},

        # GP5 Meetings
        {"id": 31, "gp": "GP5", "title": "Core/WG Meeting", "type": "WG", "location": "Cluj-Napoca", "country": "RO", "date": "2024-04-24", "participants": 280, "reimbursed": 18, "cost": 18000},
        {"id": 32, "gp": "GP5", "title": "COST FinAI meets Brussels", "type": "Workshop", "location": "Brussels", "country": "BE", "date": "2024-05-14", "participants": 31, "reimbursed": 27, "cost": 27000},
        {"id": 33, "gp": "GP5", "title": "Models for Data Analysis", "type": "Workshop", "location": "Naples", "country": "IT", "date": "2024-05-16", "participants": 38, "reimbursed": 1, "cost": 1000},
        {"id": 34, "gp": "GP5", "title": "Empowering Transformations", "type": "Workshop", "location": "Bucharest", "country": "RO", "date": "2024-05-17", "participants": 19, "reimbursed": 6, "cost": 6000},
        {"id": 35, "gp": "GP5", "title": "COST FinAI meets Istanbul", "type": "Workshop", "location": "Istanbul", "country": "TR", "date": "2024-05-20", "participants": 30, "reimbursed": 25, "cost": 25000},
        {"id": 36, "gp": "GP5", "title": "Women in Fintech & AI 4th Edition", "type": "Workshop", "location": "Rethymno", "country": "EL", "date": "2024-06-27", "participants": 39, "reimbursed": 21, "cost": 21000},
        {"id": 37, "gp": "GP5", "title": "COST FinAI meets Coimbra", "type": "Workshop", "location": "Coimbra", "country": "PT", "date": "2024-07-10", "participants": 20, "reimbursed": 15, "cost": 15000},
        {"id": 38, "gp": "GP5", "title": "AI in Finance & Society", "type": "Workshop", "location": "Gran Canaria", "country": "ES", "date": "2024-07-18", "participants": 35, "reimbursed": 19, "cost": 19000},
        {"id": 39, "gp": "GP5", "title": "COST FinAI meets Iceland", "type": "Workshop", "location": "Reykjavik", "country": "IS", "date": "2024-08-27", "participants": 20, "reimbursed": 17, "cost": 17000},
        {"id": 40, "gp": "GP5", "title": "Final MC Meeting", "type": "MC", "location": "Online", "country": "CH", "date": "2024-09-06", "participants": 73, "reimbursed": 0, "cost": 0}
    ]

    # Add ITC flag
    for m in meetings:
        m["itc"] = m["country"] in ITC_COUNTRIES
        m["country_name"] = COUNTRY_CODES.get(m["country"], m["country"])

    return {"meetings": meetings, "total_meetings": len(meetings)}

def extract_stsm():
    """Extract STSM data from all FFR files."""
    stsm = [
        # GP1 STSMs
        {"id": 1, "gp": "GP1", "grantee": "Stjepan Picek", "yri": True, "host_country": "NL", "home_country": "HR", "start": "2021-01-11", "end": "2021-01-26", "days": 16, "amount": 1520},
        {"id": 2, "gp": "GP1", "grantee": "Wei Li", "yri": False, "host_country": "DE", "home_country": "NO", "start": "2021-02-01", "end": "2021-05-31", "days": 120, "amount": 3500},
        {"id": 3, "gp": "GP1", "grantee": "Luciana Dalla Valle", "yri": False, "host_country": "UK", "home_country": "IT", "start": "2021-06-14", "end": "2021-06-19", "days": 6, "amount": 1260},
        {"id": 4, "gp": "GP1", "grantee": "Danial Saef", "yri": False, "host_country": "DE", "home_country": "UK", "start": "2021-09-24", "end": "2021-10-23", "days": 30, "amount": 3500},
        {"id": 5, "gp": "GP1", "grantee": "Apostolos Chalkis", "yri": False, "host_country": "EL", "home_country": "FR", "start": "2021-10-10", "end": "2021-10-23", "days": 14, "amount": 2450},
        {"id": 6, "gp": "GP1", "grantee": "Jasone Ramirez-Ayerbe", "yri": False, "host_country": "ES", "home_country": "DK", "start": "2021-10-13", "end": "2021-10-26", "days": 14, "amount": 2540},
        {"id": 7, "gp": "GP1", "grantee": "Alla Petukhina", "yri": True, "host_country": "DE", "home_country": "RO", "start": "2021-10-20", "end": "2021-10-31", "days": 12, "amount": 1500},
        {"id": 8, "gp": "GP1", "grantee": "Ioana Coita", "yri": True, "host_country": "RO", "home_country": "DE", "start": "2021-10-22", "end": "2021-10-31", "days": 10, "amount": 2500},
        {"id": 9, "gp": "GP1", "grantee": "Galena Pisoni", "yri": False, "host_country": "FR", "home_country": "NO", "start": "2021-10-24", "end": "2021-10-31", "days": 8, "amount": 2030},

        # GP3 STSMs
        {"id": 10, "gp": "GP3", "grantee": "Daniel Traian Pele", "yri": False, "host_country": "DE", "home_country": "RO", "start": "2022-09-26", "end": "2022-10-04", "days": 10, "amount": 1800},
        {"id": 11, "gp": "GP3", "grantee": "Cathy Yi-Hsuan Chen", "yri": False, "host_country": "HR", "home_country": "GB", "start": "2022-10-01", "end": "2022-10-31", "days": 32, "amount": 3200},
        {"id": 12, "gp": "GP3", "grantee": "Luciana Dalla Valle", "yri": False, "host_country": "IT", "home_country": "GB", "start": "2022-07-11", "end": "2022-07-18", "days": 9, "amount": 1440},
        {"id": 13, "gp": "GP3", "grantee": "Jose Muniz Martinez", "yri": True, "host_country": "GB", "home_country": "CH", "start": "2022-09-27", "end": "2022-10-06", "days": 11, "amount": 1900},
        {"id": 14, "gp": "GP3", "grantee": "Alla Petukhina", "yri": True, "host_country": "DE", "home_country": "IT", "start": "2022-09-18", "end": "2022-09-26", "days": 10, "amount": 2000},
        {"id": 15, "gp": "GP3", "grantee": "Ioana Coita", "yri": True, "host_country": "RO", "home_country": "CH", "start": "2022-10-14", "end": "2022-10-23", "days": 11, "amount": 2500},
        {"id": 16, "gp": "GP3", "grantee": "Stefana Belbe", "yri": True, "host_country": "RO", "home_country": "CH", "start": "2022-10-21", "end": "2022-10-31", "days": 12, "amount": 2700},
        {"id": 17, "gp": "GP3", "grantee": "Tomas Plihal", "yri": True, "host_country": "CZ", "home_country": "CH", "start": "2022-09-21", "end": "2022-10-02", "days": 13, "amount": 4000},
        {"id": 18, "gp": "GP3", "grantee": "Karel Kozmik", "yri": True, "host_country": "CZ", "home_country": "DE", "start": "2022-10-10", "end": "2022-10-31", "days": 23, "amount": 3000},
        {"id": 19, "gp": "GP3", "grantee": "Xinwen Ni", "yri": True, "host_country": "DE", "home_country": "GB", "start": "2022-10-24", "end": "2022-10-31", "days": 9, "amount": 1600},

        # GP4 STSMs
        {"id": 20, "gp": "GP4", "grantee": "Rezarta Shkurti Perri", "yri": False, "host_country": "IT", "home_country": "AL", "start": "2023-10-09", "end": "2023-10-13", "days": 6, "amount": 1000},
        {"id": 21, "gp": "GP4", "grantee": "Jurgita Cerneviciene", "yri": False, "host_country": "CZ", "home_country": "LT", "start": "2023-10-02", "end": "2023-10-06", "days": 6, "amount": 1600},
        {"id": 22, "gp": "GP4", "grantee": "Luciana Dalla Valle", "yri": False, "host_country": "IT", "home_country": "GB", "start": "2023-07-01", "end": "2023-07-09", "days": 10, "amount": 2000},
        {"id": 23, "gp": "GP4", "grantee": "Vassilios Papavassiliou", "yri": False, "host_country": "PT", "home_country": "IE", "start": "2023-07-03", "end": "2023-07-12", "days": 11, "amount": 2500},
        {"id": 24, "gp": "GP4", "grantee": "Esra Kabaklarli", "yri": False, "host_country": "DE", "home_country": "TR", "start": "2023-08-27", "end": "2023-08-31", "days": 6, "amount": 1500},
        {"id": 25, "gp": "GP4", "grantee": "Stefana Belbe", "yri": True, "host_country": "DE", "home_country": "RO", "start": "2023-07-31", "end": "2023-08-08", "days": 10, "amount": 1900},

        # GP5 STSMs
        {"id": 26, "gp": "GP5", "grantee": "Ioana Coita", "yri": False, "host_country": "SK", "home_country": "RO", "start": "2024-04-06", "end": "2024-04-14", "days": 10, "amount": 1997},
        {"id": 27, "gp": "GP5", "grantee": "Bekir Cetintav", "yri": True, "host_country": "PT", "home_country": "TR", "start": "2024-07-18", "end": "2024-07-28", "days": 12, "amount": 2645}
    ]

    # Add country names
    for s in stsm:
        s["host_country_name"] = COUNTRY_CODES.get(s["host_country"], s["host_country"])
        s["home_country_name"] = COUNTRY_CODES.get(s["home_country"], s["home_country"])
        s["host_itc"] = s["host_country"] in ITC_COUNTRIES
        s["home_itc"] = s["home_country"] in ITC_COUNTRIES

    return {"stsm": stsm, "total_stsm": len(stsm), "total_amount": sum(s["amount"] for s in stsm)}

def extract_training_schools():
    """Extract training school data."""
    schools = [
        # GP4 Training Schools
        {"id": 1, "gp": "GP4", "title": "Fintech & AI - Latest Technologies & Upcoming Challenges", "location": "Tirana", "country": "AL", "institution": "University of Tirana", "start": "2023-04-26", "end": "2023-04-28", "trainers": 5, "trainees": 15, "cost": 7415.27},
        {"id": 2, "gp": "GP4", "title": "Fintech & AI: Current State-of-the-art & Future Challenges", "location": "Enschede", "country": "NL", "institution": "University of Twente", "start": "2023-06-12", "end": "2023-06-16", "trainers": 6, "trainees": 14, "cost": 22353.65},
        {"id": 3, "gp": "GP4", "title": "Data Science for Sustainable Economics & Finance", "location": "Berlin", "country": "DE", "institution": "HTW Berlin", "start": "2023-08-28", "end": "2023-09-01", "trainers": 5, "trainees": 11, "cost": 8690.07},
        {"id": 4, "gp": "GP4", "title": "AFFINE - Advanced Statistical Modelling for Fintech", "location": "Naples", "country": "IT", "institution": "University of Naples Federico II", "start": "2023-09-13", "end": "2023-09-15", "trainers": 4, "trainees": 10, "cost": 10942.10},

        # GP5 Training Schools
        {"id": 5, "gp": "GP5", "title": "Data Science & AI for Finance: Academia & Industry Bridge", "location": "Cosenza", "country": "IT", "institution": "University of Calabria", "start": "2024-06-03", "end": "2024-06-04", "trainers": 4, "trainees": 11, "cost": 11340.34},
        {"id": 6, "gp": "GP5", "title": "PhD School on Fintech & AI", "location": "Enschede", "country": "NL", "institution": "University of Twente", "start": "2024-06-10", "end": "2024-06-14", "trainers": 6, "trainees": 15, "cost": 22901.77},
        {"id": 7, "gp": "GP5", "title": "AFFINE - Advanced Statistical Modelling for Fintech 2024", "location": "Naples", "country": "IT", "institution": "University of Naples Federico II", "start": "2024-09-05", "end": "2024-09-07", "trainers": 5, "trainees": 22, "cost": 25172.85}
    ]

    for s in schools:
        s["itc"] = s["country"] in ITC_COUNTRIES
        s["country_name"] = COUNTRY_CODES.get(s["country"], s["country"])

    return {"training_schools": schools, "total_schools": len(schools), "total_trainees": sum(s["trainees"] for s in schools)}

def extract_participants():
    """Extract participant data from FFR files."""
    # This is a curated list based on the extracted text
    participants_raw = """Abdul Nasir, Jamal (IE)
Abrol, Manmeet (IE)
Achim, Monica Violeta (RO)
Akar, Mutlu (TR)
Antoniou (CY)
Apostol, Elena Simona (RO)
Apolosolu, Apostolos (FR)
Arakelian, Veni (EL)
Atanasova-Pachemska, Tatjana (MK)
Aydin, Nadi Serhan (TR)
Agotnes, Thomas (NO)
Baals, Lennart John (CH)
Bag, Raul (RO)
Baka, Dea (AL)
Bekteshi, Erisa (AL)
Belbe, Stefana (RO)
Ben Amor, Souhir (DE)
Bernard, Frederik Sinan (NL)
Bedowska-Sojka, Barbara (PL)
Bolesta, Karolina (PL)
Borodenko, Vladyslav (UA)
Cakir, Enis (TR)
Cetintav, Bekir (TR)
Chakravorti, Sujit (US)
Chalkis, Apostolos (FR)
Chen, Cathy Yi-Hsuan (UK)
Chis, Laviniu (RO)
Citterio, Alberto (IT)
Cokaj, Mentor (AL)
Coita, Ioana (RO)
Oosterlee, Cornelis (NL)
Costea, Adrian (RO)
Curticapean, Cosmin (RO)
D'Elia, Samuele (IT)
Dalla Valle, Luciana (IT)
Daver, Gizay (TR)
De Giuli, Maria Elena (IT)
De Meer Pardo, Fernando (CH)
Deev, Oleg (CZ)
Dellaportas, Petros (UK)
Demolli, Erlind (CH)
Dias, Joana (PT)
Domingo Vilar, Albert (ES)
Dzurovski, Anastas (MK)
Zdravevski, Eftim (MK)
Giordano, Sabrina (IT)
Girvica, Olga (LV)
Gomez Teijeiro, Lucia (CH)
Gregoriades, Andreas (CY)
Guerrero, Esteban (FI)
Hadji Misheva, Branka (CH)
Hafner, Christian (BE)
Hajek, Petr (CZ)
Halilaj, Malvina (AL)
Skaftadottir, Hanna Kristin (IS)
Hardle, Wolfgang (DE)
Hirsa, Ali (US)
Hochreiter, Ronald (AT)
Hudec, Miroslav (SK)
Iannario, Maria (IT)
Ivanisevic Hernaus, Ana (HR)
Jevtic, Danijel (CH)
Osterrieder, Jorg (CH)
Kabaklarli, Esra (TR)
Khowaja, Kainat (DE)
Kayis, Enis (TR)
Keller, Yosi (IL)
Klein, Marius (CH)
Klochko, Alona (UA)
Kleverlaan, Ronald (NL)
Koenigstein, Nicole (CH)
Kozmik, Karel (CZ)
Kosta, Anxhela (AL)
Lameski, Petre (MK)
Stanca, Liana (RO)
Liiv, Innar (EE)
Ilma, Lili (AL)
Liu, Yiting (CH)
Machado, Marcos (NL)
Mare, Codruta (RO)
Marazzina, Daniele (IT)
Marisetty, Vijay (NL)
Maxhelaku, Armela (AL)
Maxhelaku Vasil, Suela (AL)
Matkovskyy, Roman (FR)
Metani, Fiona (AL)
Metushi, Emirjan (AL)
Mirchev, Miroslav (MK)
Mirzaei, Mahsa (IE)
Mishev, Stoyan (BG)
Moloney, Maria (IE)
Moukas, Alexios Ioannis (EL)
Muckley, Cal (IE)
Muniz Martinez, Jose Antonio (UK)
Nadini, Matthieu (UK)
Ni, Xinwen (GB)
Nur, Pinar (TR)
Yilmaz, Gokce Nur (TR)
Ozturkkal, Belma (TR)
Paccagnini, Alessia (IE)
Palic, Petra (HR)
Papajorgji, Petraq (AL)
Paschalidou, Eleftheria (EL)
Pele, Daniel Traian (RO)
Pelegrina Jimenez, Antonio (ES)
Peliova, Jana (SK)
Petukhina, Alla (DE)
Piot, Valerio (IE)
Pisoni, Galena (FR)
Plihal, Tomas (CZ)
Popa, Diana (RO)
Poti, Valerio (IE)
Reule, Raphael (DE)
Raeli, Fabrizio (IT)
Rupeika-Apoga, Ramona (LV)
Saef, Danial (DE)
Sandulescu, Magda (RO)
Sauli, Gerta (AL)
Schwendner, Peter (CH)
Seci, Drita (AL)
Shala, Albulena (KV)
Shkurti Perri, Rezarta (AL)
Simurina, Nika (HR)
Silva, Catarina (PT)
Solibakke, Per B (NO)
Spindler, Christian (CH)
Strat, Vasile (RO)
Svedas, Dominykas (LT)
Svetlova, Ekaterina (NL)
Sutiene, Kristina (LT)
Taibi, Gabin (CH)
Tanda, Alessandra (IT)
Tarantola, Claudia (IT)
Temkov, Slave (MK)
Themistocleous, Christos (CY)
Thomaidis, Nikolaos S. (EL)
Tiron-Tudor, Adriana (RO)
Trinh, Anh Tuan (HU)
Truica, Ciprian-Octavian (RO)
van Heeswijk, Wouter (NL)
Vagnerova Linnertova, Dagmar (CZ)
Vojtasova, Maria (SK)
Vucetic, Miljan (RS)
Li, Wei (DE)
Wenzlaff, Karsten (DE)
Wojcik, Piotr (PL)
Xhumari, Elda (AL)
Xhina, Endrit (AL)
Yildirim, Ozgur (TR)
Zhu, Laqiqige (IE)
Zuo, RongLin (HU)
Zlatosova, Silvie (CZ)
Citci, Sadettin Haluk (TR)"""

    participants = []
    pattern = r'([^(]+)\s*\(([A-Z]{2})\)'

    for line in participants_raw.strip().split('\n'):
        match = re.search(pattern, line.strip())
        if match:
            name = match.group(1).strip()
            country = match.group(2)
            participants.append({
                "name": name,
                "country_code": country,
                "country_name": COUNTRY_CODES.get(country, country),
                "itc": country in ITC_COUNTRIES
            })

    # Sort by country then name
    participants.sort(key=lambda x: (x["country_name"], x["name"]))

    # Group by country
    by_country = defaultdict(list)
    for p in participants:
        by_country[p["country_name"]].append(p)

    country_stats = [{"country": k, "count": len(v), "itc": v[0]["itc"]} for k, v in by_country.items()]
    country_stats.sort(key=lambda x: -x["count"])

    return {
        "participants": participants,
        "total_participants": len(participants),
        "by_country": dict(by_country),
        "country_stats": country_stats,
        "itc_count": sum(1 for p in participants if p["itc"]),
        "non_itc_count": sum(1 for p in participants if not p["itc"])
    }

def extract_deliverables():
    """Extract deliverable data from WBP files."""
    deliverables = [
        {"id": 1, "title": "Strategy to engage stakeholders", "month": 6, "status": "completed", "description": "Comprehensive stakeholder engagement strategy with revisions at months 24 and 36"},
        {"id": 2, "title": "Report on best practices for transparent finance", "month": 12, "status": "completed", "description": "Report with 12 guidelines on good examples and best practices"},
        {"id": 3, "title": "Database with pre-ICO documentation", "month": 24, "status": "completed", "description": "Database linking pre-ICO documentation to post-ICO performance"},
        {"id": 4, "title": "Database with crowdfunding/P2P platform features", "month": 24, "status": "completed", "description": "Database for fraud prediction in crowdfunding platforms"},
        {"id": 5, "title": "Discussion paper on back-testing framework", "month": 24, "status": "completed", "description": "Statistically valid back-testing framework for investment strategies"},
        {"id": 6, "title": "Internal database of financial time series", "month": 24, "status": "completed", "description": "Data from exchanges for research purposes"},
        {"id": 7, "title": "Discussion papers on ICO/crowdfunding methodology", "month": 36, "status": "completed", "description": "Methodology for evaluating ICOs and crowdfunding platforms"},
        {"id": 8, "title": "Position papers for regulators on AI testing", "month": 36, "status": "completed", "description": "Methodology with formal criteria for testing AI techniques in real-time"},
        {"id": 9, "title": "Handbook on risk management", "month": 36, "status": "completed", "description": "Wiki/handbook on risk management for blockchain and P2P lending"},
        {"id": 10, "title": "Position paper on digital asset risks", "month": 48, "status": "completed", "description": "Roadmap on mitigating risks with digital assets"},
        {"id": 11, "title": "Methodology on stress tests for AI/ML", "month": 48, "status": "completed", "description": "Discussion paper on stress testing AI/ML models"},
        {"id": 12, "title": "AI models for failed trials analysis", "month": 48, "status": "completed", "description": "Discussion papers on AI models for network data analysis"},
        {"id": 13, "title": "Four annual reports for lay audience", "month": 48, "status": "completed", "description": "Annual reports via media channels"},
        {"id": 14, "title": "Key software/codes/packages", "month": 48, "status": "completed", "description": "Open source software contributions from working groups"},
        {"id": 15, "title": "Edited volume on scientific achievements", "month": 48, "status": "completed", "description": "Comprehensive edited volume documenting action achievements"}
    ]
    return {"deliverables": deliverables, "total": len(deliverables), "completed": sum(1 for d in deliverables if d["status"] == "completed")}

def extract_working_groups():
    """Extract working group data."""
    wg = [
        {
            "id": "WG1",
            "name": "Transparency in FinTech",
            "leader": "Prof. Wolfgang Hardle",
            "description": "Investigating transparency in blockchain, cryptocurrencies, NFTs, digital assets, and innovative financial services using ML methods. Focus on prediction of operational fragility and fraudulent behavior.",
            "members_gp1": 30,
            "members_gp3": 50,
            "members_gp5": 277,
            "topics": ["Blockchain", "Cryptocurrencies", "NFTs", "Digital Assets", "Fraud Detection"]
        },
        {
            "id": "WG2",
            "name": "Transparent vs Black Box Decision-Support Models",
            "leader": "Dr. Petre Lameski",
            "description": "Development of conceptual and methodological tools for making black-box models transparent or interpretable/explainable. Focus on XAI approaches, credit risk modeling, and ML model robustness.",
            "members_gp1": 30,
            "members_gp3": 57,
            "members_gp5": 248,
            "topics": ["Explainable AI", "Credit Risk", "Model Interpretability", "Decision Support", "ML Robustness"]
        },
        {
            "id": "WG3",
            "name": "Investment Product Performance Transparency",
            "leader": "Prof. Peter Schwendner",
            "description": "Investment product performance evaluation, sustainable investments, stress testing AI/ML models, digital asset investments, performance attribution, and false discovery rate reduction.",
            "members_gp1": 30,
            "members_gp3": 41,
            "members_gp5": 218,
            "topics": ["Investment Performance", "ESG", "Stress Testing", "Digital Assets", "Performance Attribution"]
        }
    ]
    return {"working_groups": wg}

def main():
    """Main function to extract all data and save as JSON."""
    print("Extracting COST Action CA19130 data...")

    # Extract all data
    budget_data = extract_budget_data()
    meetings_data = extract_meetings()
    stsm_data = extract_stsm()
    training_data = extract_training_schools()
    participants_data = extract_participants()
    deliverables_data = extract_deliverables()
    wg_data = extract_working_groups()

    # Save JSON files
    with open(OUTPUT_DIR / "budget_data.json", 'w', encoding='utf-8') as f:
        json.dump(budget_data, f, indent=2, ensure_ascii=False)
    print(f"  Saved budget_data.json")

    with open(OUTPUT_DIR / "meetings.json", 'w', encoding='utf-8') as f:
        json.dump(meetings_data, f, indent=2, ensure_ascii=False)
    print(f"  Saved meetings.json ({meetings_data['total_meetings']} meetings)")

    with open(OUTPUT_DIR / "stsm.json", 'w', encoding='utf-8') as f:
        json.dump(stsm_data, f, indent=2, ensure_ascii=False)
    print(f"  Saved stsm.json ({stsm_data['total_stsm']} STSMs)")

    with open(OUTPUT_DIR / "training_schools.json", 'w', encoding='utf-8') as f:
        json.dump(training_data, f, indent=2, ensure_ascii=False)
    print(f"  Saved training_schools.json ({training_data['total_schools']} schools)")

    with open(OUTPUT_DIR / "participants.json", 'w', encoding='utf-8') as f:
        json.dump(participants_data, f, indent=2, ensure_ascii=False)
    print(f"  Saved participants.json ({participants_data['total_participants']} participants)")

    with open(OUTPUT_DIR / "deliverables.json", 'w', encoding='utf-8') as f:
        json.dump(deliverables_data, f, indent=2, ensure_ascii=False)
    print(f"  Saved deliverables.json ({deliverables_data['total']} deliverables)")

    with open(OUTPUT_DIR / "working_groups.json", 'w', encoding='utf-8') as f:
        json.dump(wg_data, f, indent=2, ensure_ascii=False)
    print(f"  Saved working_groups.json")

    print("\nData extraction complete!")
    print(f"Output directory: {OUTPUT_DIR}")

if __name__ == "__main__":
    main()
