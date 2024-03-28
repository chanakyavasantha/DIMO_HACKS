
from h2o_wave import main, app, Q, ui, on, run_on, data
from typing import Optional, List
import imaplib
import openai
import email

#openai.api_key = ''
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

    for i in range(3):
        add_card(q, f'info{i}', ui.tall_info_card(box='horizontal', name='', title='Speed',
                                                  caption='The models are performant thanks to...', icon='SpeedHigh'))
    add_card(q, 'article', ui.tall_article_preview_card(
        box=ui.box('vertical', height='600px'), title='How does magic work',
        image='https://images.pexels.com/photos/624015/pexels-photo-624015.jpeg?auto=compress&cs=tinysrgb&w=1260&h=750&dpr=1',
        content='''
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Vestibulum ac sodales felis. Duis orci enim, iaculis at augue vel, mattis imperdiet ligula. Sed a placerat lacus, vitae viverra ante. Duis laoreet purus sit amet orci lacinia, non facilisis ipsum venenatis. Duis bibendum malesuada urna. Praesent vehicula tempor volutpat. In sem augue, blandit a tempus sit amet, tristique vehicula nisl. Duis molestie vel nisl a blandit. Nunc mollis ullamcorper elementum.
Donec in erat augue. Nullam mollis ligula nec massa semper, laoreet pellentesque nulla ullamcorper. In ante ex, tristique et mollis id, facilisis non metus. Aliquam neque eros, semper id finibus eu, pellentesque ac magna. Aliquam convallis eros ut erat mollis, sit amet scelerisque ex pretium. Nulla sodales lacus a tellus molestie blandit. Praesent molestie elit viverra, congue purus vel, cursus sem. Donec malesuada libero ut nulla bibendum, in condimentum massa pretium. Aliquam erat volutpat. Interdum et malesuada fames ac ante ipsum primis in faucibus. Integer vel tincidunt purus, congue suscipit neque. Fusce eget lacus nibh. Sed vestibulum neque id erat accumsan, a faucibus leo malesuada. Curabitur varius ligula a velit aliquet tincidunt. Donec vehicula ligula sit amet nunc tempus, non fermentum odio rhoncus.
Vestibulum condimentum consectetur aliquet. Phasellus mollis at nulla vel blandit. Praesent at ligula nulla. Curabitur enim tellus, congue id tempor at, malesuada sed augue. Nulla in justo in libero condimentum euismod. Integer aliquet, velit id convallis maximus, nisl dui porta velit, et pellentesque ligula lorem non nunc. Sed tincidunt purus non elit ultrices egestas quis eu mauris. Sed molestie vulputate enim, a vehicula nibh pulvinar sit amet. Nullam auctor sapien est, et aliquet dui congue ornare. Donec pulvinar scelerisque justo, nec scelerisque velit maximus eget. Ut ac lectus velit. Pellentesque bibendum ex sit amet cursus commodo. Fusce congue metus at elementum ultricies. Suspendisse non rhoncus risus. In hac habitasse platea dictumst.
        '''
    ))





async def analyze_emails(q: Q):
    try:
        mail = imaplib.IMAP4_SSL('imap.gmail.com')
        mail.login(q.args.email_address, q.args.password)
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

                prompt = f"Conversation history: {conversation_history}. Sender's email: {sender_email}. Analyze whether the given email corresponds to phishing or contains any malicious content."
                response = openai.Completion.create(
                    model="gpt-3.5-turbo-instruct",
                    prompt=prompt,
                    max_tokens=250
                )
                reply_text = response.choices[0].text.strip()
                print(reply_text)

                # Display generated reply
                add_card(q, 'reply_card', ui.text(reply_text))

        mail.close()
        mail.logout()

    except Exception as e:
        print(f"An error occurred: {str(e)}")
        # Handle errors gracefully, such as displaying an error message to the user

    await q.page.save()

@on('#page3')
async def page3(q: Q):
    q.page['sidebar'].value = '#page3'
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
            ui.button(name='page3_step2', label='Submit', primary=True),
        ]))
    await q.page.save()

@on()
async def page3_step2(q: Q):
    await analyze_emails(q)
    await q.page.save()





async def init(q: Q) -> None:
    q.page['meta'] = ui.meta_card(box='', layouts=[ui.layout(breakpoint='xs', min_height='100vh', zones=[
        ui.zone('main', size='1', direction=ui.ZoneDirection.ROW, zones=[
            ui.zone('sidebar', size='250px'),
            ui.zone('body', zones=[
                ui.zone('header'),
                ui.zone('content', zones=[
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
        image='https://wave.h2o.ai/img/h2o-logo.svg', items=[
            ui.nav_group('Menu', items=[
                ui.nav_item(name='#page1', label='Home'),
                ui.nav_item(name='#page3', label='Grid'),
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

