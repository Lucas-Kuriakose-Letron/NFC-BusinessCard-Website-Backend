class ContactCardGenerator:
    def generate_vcard(self, name, phone, company):
        return f"""BEGIN:VCARD
        VERSION:3.0
        FN:{name}
        ORG:{company}
        TEL;TYPE=CELL:{phone}
        END:VCARD
        """
    