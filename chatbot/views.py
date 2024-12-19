import threading
from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views import View
from core.models import Userprofile
from .models import *
from huggingface_hub import InferenceClient
from .parse_markdown import parse_markdown

class create_chat(View):
    def get(self, request):
        return render(request, 'chatbot/core/start_chat.html')
    def post(self, request):
        title = request.POST.get('title')
        user = Userprofile.objects.get(user=request.user)

        chat = Chat.objects.create(
            title = title,
            user = user
        )
        print(chat.id)
        prompt = "You are Futura, a chatbot on Fashion Futuist with the aim of providing outfit recommendations to the user based on their fashion choices and physical attributes. Lets start with collection information abouut the user about like style, ocassion and clothing size."

        Message.objects.create(
            chat = chat,
            sender = "system",
            content = prompt
        )

        Message.objects.create(
            chat = chat,
            sender = "assistant",
            content = f"Hey {user.name}! Welcome to Fashion Futurist. I'm Futura, your personalised assistant ready to help you with outfit recommendations! Lets start off with a few questions first. Could you tell describe your preferred style and occassion?",
            content_html = f"Hey {user.name}! Welcome to Fashion Futurist. I'm Futura, your personalised assistant ready to help you with outfit recommendations! Lets start off with a few questions first. Could you tell describe your preferred style and occassion?"
        )

        return redirect('chat', chat.id)

class chat(View):
    def get(self, request, chatid):
        context = {}
        chat = get_object_or_404(Chat, id = chatid)
        if chat.user != Userprofile.objects.get(user=request.user):
            return HttpResponse('Not Found', status=404)
        context['chat'] = chat

        message = chat.messages.last()
        if message and message.content == "Thinking...":
            messages = chat.messages.all()
            thread = threading.Thread(target=self.llm_response, args=(message.id,messages))
            thread.start()
            return render(request, 'chatbot/chat/chat.html', context)
        elif message and message.content == "This chat has ended." and message.sender == "system":
            return render(request, 'chatbot/chat/chat_ended.html', context)
        return render(request, 'chatbot/chat/chat.html', context)
    
    def post(self, request, chatid):
        chat = Chat.objects.get(id = chatid)
        content = request.POST.get('content')
        response = chat.messages.last()
        if response and response.content == "Thinking...":
            agent_message_html = render_to_string('chatbot/chat/partials/error.html', {'error_message': "Please wait till previous request is processed", 'note':'Please refresh the page if it is taking too long'})
            return HttpResponse(agent_message_html)
        if content and content.strip():
            if len(content) > 500 and chat.title != "boss_mode":
                agent_message_html = render_to_string(
                    'chatbot/chat/partials/error.html',
                    {
                        'error_message': "Message exceeds character limit",
                        'note':'Maximum prompt length is 500 characters'
                    }
                )
                return HttpResponse(agent_message_html)

            user_message = Message.objects.create(sender="user", content=content, chat=chat)
            user_message_html = render_to_string('chatbot/chat/partials/message.html', {'message': user_message})
            agent_message = Message.objects.create(
                sender="assistant", 
                content="Thinking...", 
                chat=chat
            )
            agent_message_html = render_to_string('chatbot/chat/partials/hot_response.html', {'message': agent_message})
            messages = user_message_html + agent_message_html
            message_history = chat.messages.all()
            thread = threading.Thread(target=self.llm_response, args=(agent_message.id,message_history))
            thread.start()
            return HttpResponse(messages)
        else:
            return HttpResponse('Invalid request', status=400)

    def llm_response(self, messageid, messages):
        message_history = []
        for m in messages:
            message = {}
            message["role"] = m.sender
            message["content"] = m.content
            message_history.append(message)
        try:
            client = InferenceClient(
                "microsoft/Phi-3-mini-4k-instruct",
                token="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",
            )
            print(message_history)
            response = client.chat_completion(
                    messages=message_history,
                    max_tokens=500,
                    stream=False,
                )
            agent_message = Message.objects.get(id=messageid)
            response_message = parse_markdown(response.choices[0].message.content)
            agent_message.content = response.choices[0].message.content
            agent_message.content_html = response_message
            agent_message.save()
        except:
            agent_message = Message.objects.get(id=messageid)
            agent_message.sender = "system"
            agent_message.content = "Something went wrong while generating response"
            agent_message.save()

def get_response(request, chat_id):
    user_profile = Userprofile.objects.filter(user=request.user).first()
    chat = get_object_or_404(Chat, id=chat_id)
    if chat.user != user_profile:
        return HttpResponse('Not Found', status=404)
    response = chat.messages.last()
    if response.content == "Thinking...":
        response_html = render_to_string('chatbot/chat/partials/hot_response.html',  {'message': response})
    else:
        context = {}
        context["message"] = response
        response_html = render_to_string('chatbot/chat/partials/response.html', context)
    return HttpResponse(response_html)

def index(request):
    context = {}
    user = Userprofile.objects.get(user=request.user)
    chats = user.chats
    context["chats"] = chats
    return render(request, 'chatbot/core/index.html', context)