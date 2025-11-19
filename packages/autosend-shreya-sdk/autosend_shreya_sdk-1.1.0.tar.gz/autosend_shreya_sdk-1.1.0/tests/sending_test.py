# test_sending.py
from autosend import AutosendClient

client = AutosendClient(api_key="YOUR_API_KEY_HERE")


# -----------------------------
# 1. Test send_email
# -----------------------------
def test_send_email():
    print("\n--- Send Single Email ---")

    to_email = input("Recipient email: ")
    to_name = input("Recipient name: ")

    from_email = input("Sender email: ")
    from_name = input("Sender name: ")

    subject = input("Subject: ")
    html = input("HTML body: ")

    print("Enter dynamic data (template variables). Format: key=value")
    dynamic_data = {}
    while True:
        field = input("key=value (or press ENTER to skip): ")
        if not field:
            break
        key, value = field.split("=")
        dynamic_data[key] = value

    reply_to = input("Reply-to email (optional): ") or None

    add_attachments = input("Add attachments? (y/n): ").lower()
    attachments = None

    if add_attachments == "y":
        attachments = []
        print("Enter attachments as: filename=..., base64=...")
        print("Add as many as you want. Press ENTER to finish.")
        while True:
            print("\nAttachment:")
            filename = input("filename (press ENTER to stop): ")
            if not filename:
                break
            base64_data = input("base64 content: ")

            attachments.append({
                "filename": filename,
                "base64": base64_data
            })

    response = client.sending.send_email(
        to_email=to_email,
        to_name=to_name,
        from_email=from_email,
        from_name=from_name,
        subject=subject,
        html=html,
        dynamic_data=dynamic_data,
        reply_to_email=reply_to,
        attachments=attachments,
    )

    print("\nResponse:")
    print(response)


# -----------------------------
# 2. Test send_bulk
# -----------------------------
def test_send_bulk():
    print("\n--- Send Bulk Email ---")

    num = int(input("Number of recipients: "))
    recipients = []

    for i in range(num):
        print(f"\nRecipient {i+1}:")
        email = input("email: ")
        name = input("name: ")

        recipients.append({
            "email": email,
            "name": name
        })

    from_email = input("\nSender email: ")
    from_name = input("Sender name: ")

    subject = input("\nSubject: ")
    html = input("HTML body: ")

    print("\nEnter dynamicData fields (key=value)")
    dynamic_data = {}
    while True:
        field = input("key=value (or press ENTER to finish): ")
        if not field:
            break
        key, value = field.split("=")
        dynamic_data[key] = value

    reply_to = input("Reply-to email (optional): ") or None

    add_attachments = input("Add attachments? (y/n): ").lower()
    attachments = None

    if add_attachments == "y":
        attachments = []
        print("Enter attachments as filename/base64 pairs. Press ENTER to stop.")
        while True:
            print("\nAttachment:")
            filename = input("filename (press ENTER to stop): ")
            if not filename:
                break
            base64_data = input("base64 content: ")

            attachments.append({
                "filename": filename,
                "base64": base64_data
            })

    response = client.sending.send_bulk(
        recipients=recipients,
        from_email=from_email,
        from_name=from_name,
        subject=subject,
        html=html,
        dynamic_data=dynamic_data,
        reply_to_email=reply_to,
        attachments=attachments,
    )

    print("\nResponse:")
    print(response)


# -----------------------------
# Main Menu
# -----------------------------
def main():
    print("\n=== AUTOSEND SENDING TEST MENU ===")
    print("1. Send Single Email")
    print("2. Send Bulk Email")
    print("0. Exit")

    choice = input("Choose an option: ")

    match choice:
        case "1":
            test_send_email()
        case "2":
            test_send_bulk()
        case "0":
            print("Exiting...")
            return
        case _:
            print("Invalid choice.")

if __name__ == "__main__":
    while True:
        main()
        print("\n--------------------------------\n")
