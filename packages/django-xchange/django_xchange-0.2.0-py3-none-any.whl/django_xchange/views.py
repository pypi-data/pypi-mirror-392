from django.db import IntegrityError
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
import json


from .models import Rate


@csrf_exempt  ## To exempt from default requirement for CSRF tokens to use postman
def ratelist_view(request: HttpRequest) -> JsonResponse:
    try:
        if request.method == 'GET':
            rates = Rate.objects.values_list('day', 'base', 'rates')
            return JsonResponse({k[0].strftime('%Y-%m-%d'): {'base': k[1], 'rates': k[2]} for k in rates}, safe=False)

        if request.method == 'POST':
            body = json.loads(request.body.decode('utf-8'))
            Rate.objects.create(**body)
            return JsonResponse(body, safe=False, status=201)
    except IntegrityError as e:
        return JsonResponse({'error': str(e)}, safe=False, status=400)
    except Exception as e:  # noqa: BLE001
        return JsonResponse({'error': str(e)}, safe=False, status=500)


@csrf_exempt  ## To exempt from default requirement for CSRF tokens to use postman
def rate_view(request: HttpRequest, day: str) -> JsonResponse:
    try:
        if request.method == 'GET':
            try:
                record = Rate.objects.get(day=day)
            except Rate.DoesNotExist:
                if request.GET.get('force') and request.GET.get('force')[:1].upper() in ('1', 'T', 'Y'):
                    record = Rate.for_date(day=day)
                else:
                    return JsonResponse({'error': f'No record found for {day}'}, safe=False, status=404)
            return JsonResponse(record.as_dict(), safe=False)

        if request.method == 'PUT':
            # Turn the body into a dict
            body = json.loads(request.body.decode('utf-8'))
            # update the item
            Rate.objects.filter(day=day).update(**body)
            newrecord = Rate.objects.get(day=day)
            # send json response with updated object
            return JsonResponse(newrecord.as_dict(), safe=False)

        if request.method == 'DELETE':
            # delete the item, get all remaining records for response
            Rate.objects.filter(day=day).delete()
            return JsonResponse('None', safe=False, status=204)
    except Exception as e:  # noqa: BLE001
        return JsonResponse({'error': str(e)}, safe=False, status=500)
