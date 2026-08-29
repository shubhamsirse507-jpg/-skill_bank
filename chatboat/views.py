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
    Body: {"message": "...", "provider": "gemini|groq|openrouter", "image": "data:image/..."}
    """
    if request.method != 'POST':
        return JsonResponse({'error': 'POST method required'}, status=405)

    try:
        data = json.loads(request.body.decode('utf-8'))
        prompt = data.get('message', '').strip()
        provider = data.get('provider', 'gemini')
        image_data = data.get('image', None)

        if not prompt and not image_data:
            return JsonResponse({'error': 'Message or image cannot be empty'}, status=400)

        if not prompt and image_data:
            prompt = "What is shown in this image, and how does it relate to learning or skills?"

        result = generate_ai_response(prompt, requested_provider=provider, image_data=image_data)
        return JsonResponse(result)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
