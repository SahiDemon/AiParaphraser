import time, re, sys, random, string, pyperclip
from colorama import Fore, init
from tempmail import EMail
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select

init()

def generate_password(length=10):
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for i in range(length))

def extract_verify_link(text):
    pattern = r'<a\s+href="([^"]+)"[^>]*>https://undetectable\.ai/verify/\?a=[^<]+</a>'
    matches = re.findall(pattern, text)
    if matches:
        return matches[0]
    else:
        return None

def main(purpose_choice, readability_choice, article_file_path):
    try:
        with open(article_file_path, 'r', encoding="utf8") as article_file:
            article_text = article_file.read()

        # Split the article into chunks of 250 words
        words = article_text.split()
        chunk_size = 250
        article_chunks = [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]

        if not article_chunks:
            print(f"{Fore.RED}Your file is empty.")
            return

        # Initialize the WebDriver
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--log-level=3")
        options.add_argument('--no-proxy-server')
        options.add_argument("--incognito")
        options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])

        prefs = {"profile.default_content_setting_values.notifications": 2}
        options.add_experimental_option("prefs", prefs)

        while article_chunks:
            # Generate temp email
            email = EMail()
            password = generate_password()

            with open('accounts.txt', 'a') as file:
                file.write(f'{email}:{password}\n')

            # Create a new WebDriver instance for each account
            driver = webdriver.Chrome(options=options)

            try:
                driver.get("https://undetectable.ai/login")

                # Click registration button
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="vplpzd"]/div[7]/div[2]'))).click()
                
                # Enter email and password
                try:
                    WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, '/html/body/div[5]/div[2]/div/div/div/div/div/div[2]/div[3]/div/input'))).send_keys(str(email))
                except:
                    try:
                        WebDriverWait(driver, 2).until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div[2]/div/div/div/div/div/div[2]/div[3]/div/input"))).send_keys(str(email))
                    except:
                        print("Both XPaths failed to locate the email input.")

                driver.find_element(By.XPATH, '//*[@id="pws"]').send_keys(password)


                # Check terms and conditions and click register
                try:
                    terms_checkbox_button_xpath = "//div[contains(@class, 'cmaUraC')]//button[contains(@class, 'cmhdaC2')]"
                    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, terms_checkbox_button_xpath))).click()
                    print("Clicked on the Terms and Conditions checkbox.")
                except Exception as e:
                        print(f"Failed to click on the Terms and Conditions checkbox: {e}")

                driver.find_element(By.XPATH, '//*[@id="bSignup"]').click()

              

                # Wait for the confirmation email to arrive
                msg = email.wait_for_message()

                verify_link = extract_verify_link(msg.body)
                if verify_link:
                    driver.get(verify_link)
                    time.sleep(1)
                    driver.get("https://undetectable.ai")
                    time.sleep(1.5)
                else:
                    print(f"{Fore.RED}Verify link not found.")

                wait = WebDriverWait(driver, 10)
                purpose = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="dPurpose"]')))
                readability = wait.until(EC.presence_of_element_located((By.XPATH, '//*[@id="dReadability"]')))
                
                select1 = Select(purpose)
                select2 = Select(readability)

                options1 = select1.options
                options2 = select2.options

                if 1 <= purpose_choice <= len(options1) - 1:
                    select1.select_by_index(purpose_choice)

                if 1 <= readability_choice <= len(options2) - 1:
                    select2.select_by_index(readability_choice)

                driver.find_element(By.XPATH, '//*[@id="bBalanced"]').click()
                driver.find_element(By.XPATH, '//*[@id="checkBoxTerms"]').click()

                # Get the next chunk to submit
                chunk = article_chunks.pop(0)

                textarea = driver.find_element(By.XPATH, '//*[@id="paste"]')
                textarea.clear()
                textarea.send_keys(chunk)

                humanize = driver.find_element(By.XPATH, '//*[@id="bHumanize"]').click()

                paraphrased = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="gCopyOutput"]')))
                paraphrased.click()

                time.sleep(1)

                copied_content = pyperclip.paste()

       
                with open('paraphrased.txt', 'a') as new:
                    new.write(f'{copied_content}\n')

                # Pause the script and wait for user input
                input("Press Enter to close the browser and exit the script.")

            except Exception as e:
                print(f"{Fore.RED}Error during registration: {e}")
            finally:
                # Close the browser
                driver.quit()

        print(f"{Fore.GREEN}\nArticle has been paraphrased successfully.")

    except Exception as e:
        print(f"{Fore.RED}Error during article submission: {e}")
        raise

# ... rest of your code

if __name__ == "__main__":
    try:
        use_defaults = input(f"{Fore.CYAN}Do you want to use default values? (y/n): {Fore.GREEN}")
        if use_defaults.lower() == "y":
            purpose_choice = 7
            readability_choice = 2
            article_file_path = 'input.txt'
        else:
            print(f'{Fore.GREEN}1. General Writing\n2. Essay\n3. Article\n4. Marketing Material\n5. Story\n6. Cover letter\n7. Report\n8. Business Material\n9. Legal Material\n')
            purpose_choice = input(f'{Fore.CYAN}Select the purpose of your writing: {Fore.GREEN}')
            purpose_choice = int(purpose_choice) if purpose_choice else 7
            print(f'{Fore.GREEN}\n1. High School\n2. University\n3. Doctorate\n4. Journalist\n5. Marketing')
            readability_choice = input(f'\n{Fore.CYAN}Select the readability of your writing: {Fore.GREEN}')
            readability_choice = int(readability_choice) if readability_choice else 2
            article_file_path = input(f"\n{Fore.CYAN}Enter the path to the text file containing your article: {Fore.GREEN}")
            article_file_path = article_file_path if article_file_path else 'input.txt'
        
        main(purpose_choice, readability_choice, article_file_path)
    except:
        print(f"{Fore.RED}Aborting ...")
        sys.exit()