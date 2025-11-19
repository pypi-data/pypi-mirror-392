import random
import string
from datafakegenerator.providers.base_provider import BaseProvider


class BankSwiftBicProvider(BaseProvider):
    def __init__(self, blank_percentage: float = 0.0, **kwargs):
        super().__init__(blank_percentage=blank_percentage,
                         datasets=['bank'], **kwargs)

        self.bank_codes = [
            "ANZB", "AUBK", "BKCH", "BKKB", "BNOR", "BNPA", "BOFA", "BOPI",
            "BOTK", "BPDI", "BPFS", "BPGO", "CHAS", "CHBK", "CHSV", "CITI",
            "CPHI", "CTCB", "DBPH", "DEUT", "EQSN", "EWBC", "FCBK", "HBPH",
            "HNBK", "HSBC", "IBKO", "ICBC", "INGB", "KOEX", "MBBE", "MBTC",
            "MHCB", "PABI", "PHSB", "PHTB", "PHVB", "PNBM", "PPBU", "RCBC",
            "ROBP", "SCBL", "SETC", "SHBK", "SMBC", "STLA", "TACB", "TLBP",
            "TYBK", "UBPH", "UCPB", "UOVB", "UWCB"
        ]
        self.country_codes = ["PH", "US", "GB", "DE",
                              "FR", "JP", "CN", "SG", "AU", "NL", "HK"]

    def generate_non_blank(self, row_data=None):
        bank_code = self.get_random_data_by_list(self.bank_codes)
        country_code = self.get_random_data_by_list(self.country_codes)
        location_code = ''.join(random.choices(
            string.ascii_uppercase + string.digits, k=2))

        branch_code = ''.join(random.choices(
            string.ascii_uppercase, k=3)) if random.random() < 0.5 else ""

        return f"{bank_code}{country_code}{location_code}{branch_code}"
