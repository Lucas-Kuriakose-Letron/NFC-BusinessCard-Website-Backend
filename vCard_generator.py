class ContactCardGenerator:
    def generate_vcard(self, name, phone, company):
        parts = name.strip().split(" ", 1)
        first = parts[0]
        last = parts[1] if len(parts) >1 else ""
        return (
            "BEGIN:VCARD\r\n"
            "VERSION:3.0\r\n"
            "N:" + last + ";" + first + ";;;\r\n"
            "FN:" + name + "\r\n"
            "ORG:" + company + "\r\n"
            "TEL;TYPE=CELL:" + phone + "\r\n"
            "END:VCARD\r\n"
        )

    
