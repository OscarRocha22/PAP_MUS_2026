from playwright.sync_api import sync_playwright

with sync_playwright() as p:

    browser = p.chromium.launch(
        headless=False
    )

    page = browser.new_page()

    page.goto("https://www.facebook.com/")

    print("Facebook abierto.")
    print("Inicia sesión manualmente si es necesario.")

    input("Presiona ENTER cuando quieras cerrar el navegador...")

    browser.close()