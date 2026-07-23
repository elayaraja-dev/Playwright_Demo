from playwright.sync_api import sync_playwright
import pandas as pd
import json
import random
from datetime import datetime

# Read Excel
contacts = pd.read_excel("contacts.xlsx")

report = []

with sync_playwright() as p:

    context = p.chromium.launch_persistent_context(
        user_data_dir="whatsapp_profile",
        headless=False
    )

    page = context.pages[0] if context.pages else context.new_page()

    page.goto("https://web.whatsapp.com")

    print("Scan QR Code if required...")

    page.wait_for_selector("#pane-side", timeout=300000)

    print("WhatsApp Ready!")

    for index, row in contacts.iterrows():

        name = str(row["Name"]).strip()
        phone = str(row["Phone"]).replace("+", "").replace(".0", "")
        message = str(row["Message"]).replace("{name}", name)

        status = "Failed"

        try:

            # -------------------------
            # Search by Phone Number
            # -------------------------
            search = page.get_by_role(
                "textbox",
                name="Search or start a new chat"
            )

            search.click()
            search.press("Control+A")
            search.press("Backspace")

            search.fill(phone)

            page.wait_for_timeout(3000)

            # Click first search result
            page.locator('[data-testid="cell-frame-container"]').first.click()

            page.wait_for_timeout(2000)

            # -------------------------
            # Message Box
            # -------------------------
            box = page.get_by_role(
                "textbox",
                name="Type a message"
            )

            box.click()

            page.keyboard.type(message)

            page.keyboard.press("Enter")

            page.wait_for_timeout(3000)

            page.screenshot(path=f"{name}.png")

            status = "Sent"

            print(f"Message sent to {name}")

        except Exception as e:

            print(f"Failed for {name}")
            print(e)

        report.append({
            "Name": name,
            "Phone": phone,
            "Status": status
        })

        page.wait_for_timeout(random.randint(2000,5000))

    context.close()

# -----------------------
# Save Reports
# -----------------------
today = datetime.now().strftime("%Y-%m-%d")

with open(f"whatsapp_report_{today}.json", "w") as f:
    json.dump(report, f, indent=4)

pd.DataFrame(report).to_excel(
    f"whatsapp_report_{today}.xlsx",
    index=False
)

print("Completed Successfully!")