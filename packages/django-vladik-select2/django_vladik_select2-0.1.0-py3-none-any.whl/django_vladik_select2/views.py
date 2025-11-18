from django.apps import apps
from django.http import JsonResponse
import json
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def vladik_select2_api(request):
    if request.method != "POST":
        return JsonResponse({"error": "POST only"}, status=405)

    try:
        data = json.loads(request.body)
    except:
        return JsonResponse({"error": "Invalid JSON"}, status=400)

    model_name = data.get("model")
    term = data.get("term", "")

    # reconstruye dependencias estilo depend_campo
    filters = {
        key.replace("depend_", "") + "_id": value
        for key, value in data.items()
        if key.startswith("depend_")
    }

    if not model_name:
        return JsonResponse({"results": []})

    app_name = name_app(model_name)
    Model = apps.get_model(app_name, model_name)

    qs = Model.objects.all()

    if filters:
        qs = qs.filter(**filters)

    if term:
        qs = qs.filter(nombre__icontains=term)

    results = [{"id": o.id, "text": str(o)} for o in qs[:50]]
    return JsonResponse({"results": results})

def name_app(model_name):
    for app in apps.get_app_configs():
        for model in app.get_models():
            if model_name in model._meta.model_name.lower():
                return app.label