
from revoregex import RevoRegex


def print_result(desc, valid, msg=None):
	if valid:
		print(f"{desc}: True")
	else:
		print(f"{desc}: False | Hata: {msg}")


# Turkish validations
revo_tr = RevoRegex(lang="tr")
for desc, key, value in [
	("TR email valid", "email", "test@example.com"),
	("TR email invalid", "email", "test.com"),
	("TR telefon valid", "telefon", "+905551234567"),
	("TR telefon invalid", "telefon", "12345"),
	("TR tc valid", "tc", "12345678901"),
	("TR tc invalid", "tc", "02345678901"),
	("TR iban valid", "iban", "TR330006100519786457841326"),
	("TR iban invalid", "iban", "TR006100519786457841326"),
	("TR url valid", "url", "https://www.example.com"),
	("TR url invalid", "url", "not_a_url"),
	("TR ip valid", "ip", "192.168.1.1"),
	("TR ip invalid", "ip", "999.999.999.999"),
	("TR kredi_kartı valid", "kredi_kartı", "4000000000000000"),
	("TR kredi_kartı invalid", "kredi_kartı", "4000000000000001"),
	("TR hex_color valid", "hex_color", "#FFAABB"),
	("TR hex_color invalid", "hex_color", "#GGHHII"),
	("TR domain valid", "domain", "example.com"),
	("TR domain invalid", "domain", "example"),
]:
	valid, msg = revo_tr.validate_with_message(key, value)
	print_result(desc, valid, msg)



# English validations
revo_en = RevoRegex(lang="en")
for desc, key, value in [
	("EN email valid", "email", "test@example.com"),
	("EN email invalid", "email", "test.com"),
	("EN phone valid", "phone", "+11234567890"),
	("EN phone invalid", "phone", "555-1234"),
	("EN ssn valid", "ssn", "123-45-6789"),
	("EN ssn invalid", "ssn", "000-00-0000"),
	("EN iban valid", "iban", "GB29 NWBK 6016 1331 9268 19"),
	("EN iban invalid", "iban", "1234567890"),
	("EN url valid", "url", "https://www.example.com"),
	("EN url invalid", "url", "not_a_url"),
	("EN ip valid", "ip", "192.168.1.1"),
	("EN ip invalid", "ip", "999.999.999.999"),
	("EN credit_card valid", "credit_card", "4000000000000000"),
	("EN credit_card invalid", "credit_card", "4000000000000001"),
	("EN hex_color valid", "hex_color", "#FFAABB"),
	("EN hex_color invalid", "hex_color", "#GGHHII"),
	("EN domain valid", "domain", "example.com"),
	("EN domain invalid", "domain", "example"),
]:
	valid, msg = revo_en.validate_with_message(key, value)
	print_result(desc, valid, msg)

# German validations
revo_de = RevoRegex(lang="de")
for desc, key, value in [
	("DE email valid", "email", "test@example.com"),
	("DE email invalid", "email", "test.com"),
	("DE telefon valid", "telefon", "+4915123456789"),
	("DE telefon invalid", "telefon", "12345"),
	("DE iban valid", "iban", "DE89370400440532013000"),
	("DE iban invalid", "iban", "DE00440532013000"),
	("DE url valid", "url", "https://www.beispiel.de"),
	("DE url invalid", "url", "not_a_url"),
	("DE ip valid", "ip", "192.168.1.1"),
	("DE ip invalid", "ip", "999.999.999.999"),
	("DE kreditkarte valid", "kreditkarte", "4000000000000000"),
	("DE kreditkarte invalid", "kreditkarte", "4000000000000001"),
	("DE hex_farbe valid", "hex_farbe", "#FFAABB"),
	("DE hex_farbe invalid", "hex_farbe", "#GGHHII"),
	("DE domain valid", "domain", "beispiel.de"),
	("DE domain invalid", "domain", "beispiel"),
]:
	valid, msg = revo_de.validate_with_message(key, value)
	print_result(desc, valid, msg)

# French validations
revo_fr = RevoRegex(lang="fr")
for desc, key, value in [
	("FR email valid", "email", "test@example.com"),
	("FR email invalid", "email", "test.com"),
	("FR téléphone valid", "téléphone", "+33612345678"),
	("FR téléphone invalid", "téléphone", "12345"),
	("FR iban valid", "iban", "FR1420041010050500013M02606"),
	("FR iban invalid", "iban", "FR0010050500013M02606"),
	("FR url valid", "url", "https://www.exemple.fr"),
	("FR url invalid", "url", "not_a_url"),
	("FR ip valid", "ip", "192.168.1.1"),
	("FR ip invalid", "ip", "999.999.999.999"),
	("FR carte_bancaire valid", "carte_bancaire", "4000000000000000"),
	("FR carte_bancaire invalid", "carte_bancaire", "4000000000000001"),
	("FR couleur_hex valid", "couleur_hex", "#FFAABB"),
	("FR couleur_hex invalid", "couleur_hex", "#GGHHII"),
	("FR domaine valid", "domaine", "exemple.fr"),
	("FR domaine invalid", "domaine", "exemple"),
]:
	valid, msg = revo_fr.validate_with_message(key, value)
	print_result(desc, valid, msg)