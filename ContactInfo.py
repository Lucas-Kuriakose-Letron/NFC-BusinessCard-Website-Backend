class contactInfo:
    def __init__(self, name):
        self.name = name
        self.regionalContacts = {}

    def add_region(self, region):
        if region not in self.regionalContacts:
            self.regionalContacts[region] = []

    def addPhoneNum(self, region, phone):
        if region in self.regionalContacts:
            self.regionalContacts[region].append(phone)
            self.region_contacts[region].append(phone)

    def get_phone_numbers(self, region):
        if region in self.region_contacts:
            return self.region_contacts[region]
        return []



    def get_primary_number(self, region):
        numbers = self.get_phone_numbers(region)
        if numbers:
            return numbers[0]
        return None
    def get_all_contacts(self):
        return self.regionalContacts