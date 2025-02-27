
from openai import OpenAI
from fastapi import FastAPI, Form, Request, WebSocket
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse

chat_responses = []
app = FastAPI()
templates = Jinja2Templates(directory="templates")

@app.get('/', response_class=HTMLResponse)
async def chat_page(request: Request): 
    return templates.TemplateResponse("home.html", {"request": request, 'chat_responses': chat_responses})

chat_log = [{'role': 'system',
             'content': 'You tell jokes.'
             }]

openai = OpenAI(
    api_key="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"
)

@app.websocket("/ws")
async def chat(websocket: WebSocket):

    await websocket.accept()

    while True:
        user_input = await websocket.receive_text()
        chat_log.append({'role': 'user', 'content': user_input})
        chat_responses.append(user_input)

        try:
            response = openai.chat.completions.create(
                model='gpt-4',
                messages=chat_log,
                temperature=0.6,
                stream=True
            )

            ai_response = ''

            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    ai_response += chunk.choices[0].delta.content
                    await websocket.send_text(chunk.choices[0].delta.content)
            chat_responses.append(ai_response)

        except Exception as e:
            await websocket.send_text(f'Error: {str(e)}')
            break
            
@app.post('/', response_class=HTMLResponse)
async def chat(request: Request, user_input: Annotated[str, Form()]):
    
    chat_log.append({'role': 'user', 'content': user_input})
    chat_responses.append(user_input)

    response = openai.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=chat_log,
        temperature=0.6   
    )
    
    bot_resopnce = response.choices[0].message.content
    chat_log.append({'role': 'assistant', 'content': bot_resopnce})
    chat_responses.append(bot_resopnce)
    return templates.TemplateResponse("home.html", {"request": request, "chat_responses": chat_responses})


@app.get('/image', response_class=HTMLResponse)
async def get_image(request: Request):
    return templates.TemplateResponse("image.html", {"request": request})

@app.post('/image', response_class=HTMLResponse)
async def create_image(request: Request, user_input: Annotated[str, Form()]):
    
    response = openai.images.generate(
        prompt=user_input,
        n=1,
        size='256x256'
    )
    
    image_url = response.data[0].url
    return templates.TemplateResponse("image.html", {"request": request, "image_url": image_url})