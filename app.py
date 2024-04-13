from h2o_wave import main, app, Q, ui, on, run_on, data
from typing import Optional, List
import imaplib
import openai
import email
import json
import pandas as pd
from web3 import Web3
from hashlib import sha256
import requests

#w3 = Web3(Web3.HTTPProvider('https://erpc.xinfin.network'))

# Verify connection
"""if w3.is_connected():
    print("Successfully connected to XinFin Mainnet.")
else:
    print("Failed to connect.")"""



"""def store_email_hash_on_chain(email_body, sender_email):
    email_hash = sha256((email_body + sender_email).encode()).hexdigest()
    tx_hash = w3.eth.contract(
        address='0xFc515EA2899bC4Ce74A69b59Ef49935C069f0dF0',  # Replace with your contract address
        abi=contract_abi  # Contract ABI to interact with
    ).functions.storeHash(email_hash).transact({'from': w3.eth.accounts[0]})

    return tx_hash"""

class EmailCredentials:
    def __init__(self, email_address: str, password: str):
        self.email_address = email_address
        self.password = password
        # Initialize an empty DataFrame to store email analysis results
        self.analysis_results = pd.DataFrame(columns=['UID', 'Sender', 'ConversationHistory', 'PhishingScore', 'Explanation'])

    def add_analysis_result(self, uid, sender_email, conversation_history, phishing_score, explanation):
        new_row = pd.DataFrame({
            'UID': [uid],
            'Sender': [sender_email],
            'ConversationHistory': [conversation_history],
            'PhishingScore': [phishing_score],
            'Explanation': [explanation]
        })
        # Use pd.concat to add the new row
        self.analysis_results = pd.concat([self.analysis_results, new_row], ignore_index=True)



openai.api_key = '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'

# Use for page cards that should be removed when navigating away.
# For pages that should be always present on screen use q.page[key] = ...
def add_card(q, name, card) -> None:
    q.client.cards.add(name)
    q.page[name] = card


# Remove all the cards related to navigation.
def clear_cards(q, ignore: Optional[List[str]] = []) -> None:
    if not q.client.cards:
        return

    for name in q.client.cards.copy():
        if name not in ignore:
            del q.page[name]
            q.client.cards.remove(name)


@on('#page1')
async def page1(q: Q):
    q.page['sidebar'].value = '#page1'
    clear_cards(q)  # When routing, drop all the cards except of the main ones (header, sidebar, meta).
    add_card(q, 'article', ui.tall_article_preview_card(
        box=ui.box('vertical', height='1800px'), title='Project Description',
        image='https://images.unsplash.com/photo-1485230405346-71acb9518d9c?w=800&auto=format&fit=crop&q=60&ixlib=rb-4.0.3&ixid=M3wxMjA3fDB8MHxzZWFyY2h8NHx8c2VjdXJpdHl8ZW58MHx8MHx8fDA%3D',
        content='''

#### **Overview of the Phishing Email Detection Application**

The Phishing Email Detection application is designed to assist users in identifying potential phishing threats within their emails using advanced text analysis powered by OpenAI's GPT models. The application integrates various technologies including `h2o_wave` for the user interface, Python’s `imaplib` for email access, and the Ethereum blockchain for data integrity verification.

### Purpose

The main purpose of this application is to:
- Provide a secure way for users to login and fetch their emails.
- Analyze the content of each email to assess the risk of phishing.
- Store hashes of emails on the Ethereum blockchain to ensure data integrity and provide a non-repudiable proof of the email's original content.
- Use AI to generate detailed explanations of the analysis to help users understand why an email was flagged as a phishing attempt.

### Tech Stack

#### 1. **H2O Wave**

- **Purpose**: Used for building the user interface.
- **Details**: H2O Wave is a lightweight Python development framework that allows for the rapid creation of interactive web applications with sophisticated user interfaces. It supports real-time updates and interactive user feedback without requiring extensive frontend development expertise.

#### 2. **Python Standard Libraries**

- **`imaplib`**: This library is used to connect to and interact with IMAP servers. `imaplib` allows the application to fetch emails from a user's mailbox securely.
- **`email`**: Used to parse emails fetched from IMAP servers. It can handle different parts of an email, such as attachments and body content.

#### 3. **LLM Models**

- **Purpose**: To analyze email texts and predict phishing attempts.
- **Details**: The application uses LLM's like llama2 and gpt to assess and score emails based on their likelihood of being phishing attempts. This AI model provides not just a score but also a detailed explanation, enhancing user understanding and trust in the system.

#### 4. **Ethereum Blockchain (XinFin Network)**

- **Purpose**: To store email content hashes for data verification.
- **Details**: The application utilizes the Ethereum-compatible XinFin Network to store the SHA-256 hashes of email contents. This ensures that once an email is analyzed, its content can be verified in the future to prevent disputes about its originality or content changes over time.

#### 5. **Web3.py**

- **Purpose**: To interact with the Ethereum blockchain.
- **Details**: Web3.py is a Python library for interacting with Ethereum. It is used to connect to the XinFin Network, create transactions, and interact with smart contracts.

#### 6. **Pandas**

- **Purpose**: Data manipulation and analysis.
- **Details**: Used for organizing the analysis results into a structured format, which allows for easier reporting and visualization within the H2O Wave app.

#### 7. **Requests**

- **Purpose**: To make HTTP requests to external APIs.
- **Details**: In this application, the `requests` library is used for sending data to third-party services, such as initiating phone calls via an API that integrates AI-driven voice analysis.

### Security Features

- **Secure Email Fetching**: By using `imaplib` over SSL, the application ensures that all email transmissions are encrypted.
- **Data Integrity via Blockchain**: By storing hashes on the blockchain, the application provides a tamper-proof ledger of email analyses.
- **AI-based Analysis**: Leveraging AI for phishing detection reduces the risk of human error and biases in identifying threats.

### Conclusion

The Phishing Email Detection application is a robust tool that combines advanced AI analysis, secure email handling, and blockchain technology to provide a comprehensive solution for detecting phishing attempts in emails. This application is particularly useful for organizations and individuals looking to enhance their cybersecurity measures against increasingly sophisticated email-based threats. The use of H2O Wave for the frontend allows for rapid developments and real-time data interaction, making it a user-friendly option for users with varying levels of technical expertise.
        '''
    ))

@on('#page2')
async def page2(q: Q):
    q.page['sidebar'].value = '#page2'
    clear_cards(q)
    if q.args.show_inputs:
        print(f'email_address={q.args.email_address}')
        add_card(q, 'example', ui.form_card(box='horizontal', items=[
            ui.text(f'email_address={q.args.email_address}'),
            ui.text(f'password={q.args.password}'),
            ui.button(name='show_form', label='Back', primary=True),
        ]))
    else:
        add_card(q, 'example', ui.form_card(box='horizontal', items=[
            ui.textbox(name='email_address', label='Email Address', required=True),
            ui.textbox(name='password', label='Password', password=True),
            ui.button(name='page2_step2', label='Submit', primary=True),
        ]))
    await q.page.save()
        
@on()
async def page2_step2(q: Q):
    # Store credentials in q.client
    q.client.email_credentials = EmailCredentials(q.args.email_address, q.args.password)
    await analyze_emails(q)




async def analyze_emails(q: Q):
    try:
        print("Analyzing emails...")
        print(q.client.email_credentials.email_address)
        credentials = q.client.email_credentials
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(credentials.email_address, credentials.password)
        mail.select('inbox')

        result, data = mail.uid('search', None, 'ALL')
        uids = data[0].split()

        for uid in uids:
            result, data = mail.uid('fetch', uid, '(RFC822)')
            if result == 'OK':
                raw_email = data[0][1]
                email_message = email.message_from_bytes(raw_email)

                conversation_history = ''
                for part in email_message.walk():
                    if part.get_content_type() == 'text/plain':
                        conversation_history = f"{part.get_payload(decode=True).decode()}"

                sender_email = email_message['From']

                """tx_hash = store_email_hash_on_chain(conversation_history, sender_email)
                print(f"Stored email hash in transaction: {tx_hash.hex()}")"""


                prompt = (f"Based on the following conversation history, provide a JSON response with a 'score' field from 0 to 100 "
                    f"indicating the likelihood of the email being phishing (where 0 is definitely not phishing and 100 is definitely phishing), "
                    f"and an 'explanation' field explaining the reasoning.\n\n"
                    f"Conversation history: {conversation_history}\n"
                    f"Sender's email: {sender_email}\n\n"
                    f"Response:")


                response = openai.Completion.create(
                    model="gpt-3.5-turbo-instruct",
                    prompt=prompt,
                    max_tokens=250
                )
                try:
                    gpt_response = json.loads(response.choices[0].text.strip())
                    phishing_score = gpt_response.get("score")
                    explanation = gpt_response.get("explanation")
                except json.JSONDecodeError:
                    phishing_score = 0  # Default or error value
                    explanation = "Failed to parse response."

                # Display generated reply
                
                credentials.add_analysis_result(uid.decode("utf-8"), sender_email, conversation_history, phishing_score/100, explanation)
                """add_card(q,f'conversation_history{uid}', ui.form_card( title = 'conversation',box = 'vertical',items = [ui.text(conversation_history)]))
                add_card(q, f'reply_card{uid}', ui.form_card( title = 'reply' , box = 'vertical',items = [ui.text(explanation)]))
                add_card(q,f'PhishingScore{uid}',ui.wide_gauge_stat_card(
                    box='vertical',
                    title='Phishing Score',
                    value='=${{intl foo minimum_fraction_digits=2 maximum_fraction_digits=2}}',
                    aux_value='={{intl bar style="percent" minimum_fraction_digits=2 maximum_fraction_digits=2}}',
                    plot_color='$red',
                    progress=int(phishing_score)/100,
                    data=dict(foo=int(phishing_score), bar=int(phishing_score)/100)
                ))"""
                print(credentials.analysis_results)
                # At the end of analyze_emails function
                csv_file_path = 'email_analysis_results.csv'  # Specify a path in the writable directory
                credentials.analysis_results.to_csv(csv_file_path, index=False)
        mail.close()
        mail.logout()

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Handle errors gracefully, such as displaying an error message to the user

    await q.page.save()

csv_file_path = 'email_analysis_results.csv'
df = pd.read_csv(csv_file_path)
@on('#page3')
async def page3(q: Q):
    q.page['sidebar'].value = '#page3'
    clear_cards(q)
    if q.args.show_inputs:
        print('_________________')
        q.page['table'].items = [
            ui.text(f'selected={q.args.table}'),
            ui.button(name='show_form', label='Back', primary=True),
        ]
    else: 
        table_rows = []
        for index, row in df.iterrows():
            phishing_score = row['PhishingScore']
            phishing_score_display = f"{phishing_score:.2f}"  # This is a placeholder
            table_rows.append(ui.table_row(
                name=str(row['UID']),  # Assuming UID is the unique identifier for rows
                cells=[
                    phishing_score_display,  # This will need proper client-side handling to render correctly
                    row['ConversationHistory'],
                    row['Explanation'],
                ]
            ))
            if index == 10000:  # Limit rows for performance reasons
                break
        add_card(q, 'table', ui.form_card(box='vertical', items=[
            ui.table(
                name='table',
                downloadable=True,
                resettable=True,
                groupable=True,
                columns=[
                    ui.table_column(name='PhishingScore', label='PhishingScore', searchable=True, min_width='200', sortable=True),
                    ui.table_column(name='ConversationHistory', label='ConversationHistory', searchable=True, min_width='800'),
                    ui.table_column(name='Explanation', label='Explanation', searchable=True, min_width='200'),
                ],
                rows=table_rows,
                values = [str(item) for item in df['UID']],
            ),
            ui.button(name='show_inputs', label='Submit', primary=True),
        ]))
        await q.page.save()

selected = 1
@on()
async def show_inputs(q: Q):
    print('HI')
    selected_row = int(q.args.table[0])
    selected = selected_row
    row = df.loc[df['UID'] == selected_row]  # Assuming 'UID' is the unique identifier in your DataFrame
    print(row)
    uid = selected_row
    phishing_score = row['PhishingScore'].iloc[0]
    conversation_history = row['ConversationHistory'].iloc[0]
    explanation = row['Explanation'].iloc[0]
    print(phishing_score, conversation_history, explanation)
    add_card(q,f'conversation_history{uid}', ui.form_card( title = 'conversation',box = 'vertical',items = [ui.text(conversation_history)]))
    add_card(q, f'reply_card{uid}', ui.form_card( title = 'reply' , box = 'vertical',items = [ui.text(explanation)]))
    add_card(q,f'PhishingScore{uid}',ui.wide_bar_stat_card(
        box='vertical',
        title='Phishing Score',
        value='=${{intl foo minimum_fraction_digits=2 maximum_fraction_digits=2}}',
        aux_value='={{intl bar style="percent" minimum_fraction_digits=2 maximum_fraction_digits=2}}',
        plot_color='$red',
        progress=phishing_score,
        data=dict(foo=float(phishing_score), bar=float(phishing_score))))
    
    add_card(q, 'table_phishing', ui.form_card(box='vertical', items= [
            ui.text(f'selected={q.args.table}'),
            ui.button(name='show_form', label='Back', primary=True),
            ui.button(name='run_script', label='Call the User', primary=True),
        ]))
    await q.page.save()

@on()
async def run_script(q: Q):
    clear_cards(q)
    selected_row = selected
    row = df.loc[df['UID'] == selected_row]  # Assuming 'UID' is the unique identifier in your DataFrame
    print(row)
    uid = selected_row
    phishing_score = row['PhishingScore'].iloc[0]
    conversation_history = row['ConversationHistory'].iloc[0]
    explanation = row['Explanation'].iloc[0]
    print(conversation_history, phishing_score, explanation)
    auth_token = '1a9a3b2f-af0e-4160-8fb8-5e92275275a8'
    phone_number_id = '17914db4-b20c-4911-b9d4-9918aa581b30'
    customer_number = "+919515472473"
    headers = {
        'Authorization': f'Bearer {auth_token}',
        'Content-Type': 'application/json',
    }
    data = {
        'assistant': {
            "firstMessage": "Hello! You have some phishing threats in your email.I will help you understand them and stay secured.",
            "model": {
                "provider": "openai",
                "model": "gpt-3.5-turbo",
                "messages": [
                    {
                        "role": "system",
                        "content": f"You are an AI trained to analyze phishing threats. Here's what you need to consider:\n, don't talk continously, let the user speak."
                                   f"Conversation history: {conversation_history}\n"
                                   f"Phishing score: {phishing_score:.2f}\n"
                                   f"Explanation: {explanation}"
                    }
                ]
            },
            "voice": "jennifer-playht"
        },
        'phoneNumberId': phone_number_id,
        'customer': {
            'number': customer_number,
        },
    }
    response = requests.post('https://api.vapi.ai/call/phone', headers=headers, json=data)
    if response.status_code == 201:
        print('Call created successfully')
        print(response.json())
    else:
        print('Failed to create call')
        print(response.text)

    await q.page.save()


async def init(q: Q) -> None:
    q.page['meta'] = ui.meta_card(box='', layouts=[ui.layout(breakpoint='xs', min_height='100vh', zones=[
        ui.zone('main', size='1', direction=ui.ZoneDirection.ROW, zones=[
            ui.zone('sidebar', size='250px'),
            ui.zone('body', zones=[
                ui.zone('header'),
                ui.zone('content', size = '1800px',zones=[
                    # Specify various zones and use the one that is currently needed. Empty zones are ignored.
                    ui.zone('horizontal', direction=ui.ZoneDirection.ROW),
                    ui.zone('vertical'),
                    ui.zone('grid', direction=ui.ZoneDirection.ROW, wrap='stretch', justify='center')
                ]),
            ]),
        ])
    ])])
    q.page['sidebar'] = ui.nav_card(
        box='sidebar', color='primary', title='Phishing Email Detection', subtitle="Let's detect phishing emails",
        value=f'#{q.args["#"]}' if q.args['#'] else '#page1',
        image='', items=[
            ui.nav_group('Menu', items=[
                ui.nav_item(name='#page1', label='Home'),
                ui.nav_item(name='#page2', label='Login'),
                ui.nav_item(name='#page3', label='Analysis'),
            ]),
        ])
    # If no active hash present, render page1.
    if q.args['#'] is None:
        await page1(q)


@app('/')
async def serve(q: Q):
    # Run only once per client connection.
    if not q.client.initialized:
        q.client.cards = set()
        await init(q)
        q.client.initialized = True

    # Handle routing.
    await run_on(q)
    await q.page.save()

