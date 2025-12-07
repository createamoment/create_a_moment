def before_insert(doc, event):
	if not doc.address_title:
		if doc.links:
			doc.address_title = doc.links[0].link_name
		else:
			doc.address_title = f"{doc.address_line1}, {doc.pincode} {doc.city}"
