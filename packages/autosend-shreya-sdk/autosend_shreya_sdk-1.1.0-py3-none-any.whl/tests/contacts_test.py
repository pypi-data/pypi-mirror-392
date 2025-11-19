# test_sdk.py
from autosend import AutosendClient

client = AutosendClient(api_key="YOUR_API_KEY_HERE")

def test_get_contact():
    contact_id = input("Enter Contact ID: ")
    print(client.contacts.get_contact(contact_id))

def test_search_by_emails():
    raw = input("Enter comma-separated emails: ")
    emails = [e.strip() for e in raw.split(",")]
    print(client.contacts.search_by_emails(emails))

def test_remove_contacts():
    raw = input("Emails to remove (comma-separated): ")
    emails = [e.strip() for e in raw.split(",")]
    print(client.contacts.remove_contacts(emails))

def test_bulk_update():
    print("Enter contacts in simple format.")
    print("Example: email=john@example.com firstName=John lastName=Doe userId=123")
    
    num = int(input("How many contacts? "))
    contacts = []
    
    for _ in range(num):
        print("\nEnter contact fields:")
        contact = {}
        while True:
            field = input("key=value (or press Enter to finish this contact): ")
            if not field:
                break
            key, value = field.split("=")
            contact[key] = value
        contacts.append(contact)

    run_wf = input("Run workflow? (y/n): ").lower() == "y"
    print(client.contacts.bulk_update(contacts, run_workflow=run_wf))

def test_delete_by_user_id():
    user_id = input("Enter User ID: ")
    print(client.contacts.delete_by_user_id(user_id))

def test_delete_by_id():
    cid = input("Enter Contact ID: ")
    print(client.contacts.delete_by_id(cid))


def main():
    print("\n=== AUTOSEND SDK TEST MENU ===")
    print("1. Get Contact by ID")
    print("2. Search Contacts by Emails")
    print("3. Remove Contacts")
    print("4. Bulk Update Contacts")
    print("5. Delete Contact by User ID")
    print("6. Delete Contact by Contact ID")
    print("0. Exit")

    choice = input("Choose an option: ")

    match choice:
        case "1":
            test_get_contact()
        case "2":
            test_search_by_emails()
        case "3":
            test_remove_contacts()
        case "4":
            test_bulk_update()
        case "5":
            test_delete_by_user_id()
        case "6":
            test_delete_by_id()
        case "0":
            print("Exiting...")
            return
        case _:
            print("Invalid choice.")

if __name__ == "__main__":
    while True:
        main()
        print("\n--------------------------------\n")
