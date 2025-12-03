import json
import os
import shutil
from gi.repository import GLib
from models import FinanceData, Asset, Stream, Milestone

class DataManager:
    def __init__(self):
        self.data_dir = os.path.join(GLib.get_user_data_dir(), "firefinance")
        self.file_path = os.path.join(self.data_dir, "data.json")
        self.model = FinanceData()

        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def load_data(self):
        if not os.path.exists(self.file_path):
            self._create_default_data()
            return self.model

        try:
            with open(self.file_path, 'r') as f:
                raw_data = json.load(f)

            # Load Config
            self.model.currency_preference = raw_data.get("currency_preference", "USD")
            self.model.tax_rate_income = raw_data.get("tax_rate_income", 0.25)
            self.model.tax_rate_property = raw_data.get("tax_rate_property", 0.015)
            self.model.tax_rate_cap_gains = raw_data.get("tax_rate_cap_gains", 0.15)

            # Load Lists
            self.model.assets = [Asset(**a) for a in raw_data.get("assets", [])]
            self.model.streams = [Stream(**s) for s in raw_data.get("streams", [])]
            self.model.milestones = [Milestone(**m) for m in raw_data.get("milestones", [])]

        except Exception as e:
            print(f"Error loading data: {e}")
            self._create_default_data()

        return self.model

    def save_data(self):
        data = {
            "currency_preference": self.model.currency_preference,
            "tax_rate_income": self.model.tax_rate_income,
            "tax_rate_property": self.model.tax_rate_property,
            "tax_rate_cap_gains": self.model.tax_rate_cap_gains,
            "assets": [vars(a) for a in self.model.assets],
            "streams": [vars(s) for s in self.model.streams],
            "milestones": [vars(m) for m in self.model.milestones]
        }

        temp_path = self.file_path + ".tmp"
        with open(temp_path, 'w') as f:
            json.dump(data, f, indent=4)
        shutil.move(temp_path, self.file_path)

    def _create_default_data(self):
        """Creates GENERIC example data."""
        self.model.assets = [
            Asset(name="Bitcoin Cold Storage", balance=0.5, currency="BTC"),
            Asset(name="Savings Account", balance=15000.0, currency="USD", apy=0.04),
            Asset(name="Primary Home", balance=450000.0, currency="USD", apy=0.03, is_real_estate=True)
        ]
        self.model.streams = [
            Stream(name="Salary", amount=85000.00, currency="USD", frequency="Yearly", is_income=True),
            Stream(name="Groceries", amount=6000.00, currency="USD", frequency="Yearly", is_income=False),
        ]
        self.model.milestones = [
            Milestone(name="New Car", amount=35000.0, year_offset=3, duration=1),
            Milestone(name="Kids College", amount=45000.0, year_offset=10, duration=4)
        ]
        self.save_data()
