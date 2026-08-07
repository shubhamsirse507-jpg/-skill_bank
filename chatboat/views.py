import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from chatboat.ai_service import generate_ai_response


def chat(request):
    """
    Main AI Chat Boat page.
    No login required — accessible for frontend preview.
    """
    return render(request, 'chatboat/chat.html', {
        'user': request.user,
    })


@csrf_exempt
def chat_api(request):
    """
    API Endpoint for sending messages to AI with automatic multi-provider failover.
    POST /chat/api/send/
    Body: {"message": "...", "provider": "gemini|groq|openrouter"}
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        prompt = data.get('message', '').strip()
        provider = data.get('provider', 'gemini')

        if not prompt:
            return JsonResponse({'error': 'Message cannot be empty'}, status=400)

        result = generate_ai_response(prompt, requested_provider=provider)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
