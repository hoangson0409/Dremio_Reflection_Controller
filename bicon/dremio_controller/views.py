# from django.shortcuts import render
# from .models import *
# from django.views.decorators.http import require_http_methods
# from .forms import *
# Create your views here.


# @require_http_methods(['POST', 'GET'])  # only get and post
# def refreshDremioView(request):
#     if request.method == 'POST':
#         form = ReflectionForm(request.POST)
#         form.save()
#     return render(request, 'bi_alerts.html', context={})

# def createReflection(dataset_id):
#     Reflection.objects.create(datasetId=dataset_id,
#                               type=)


# @csrf_exempt
# @require_http_methods(['POST', 'GET'])  # only get and post
# def createReflection(request):
#     if request.method == 'POST':
#         form = ReflectionForm(request.POST)
#         form.save()

    #     input_id = str(request.POST.get('input_id', None))
    #     input_id_new = input_id.replace('-', '')
    #     # header_settings = {
    #     #     'USER_AGENT': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    #     # }
    #     scrapyd_project = os.getenv('PW_SCRAPY_PROJECT', 'spiderman')
    #     scrapyd_spider = os.getenv('PW_SCRAPY_SPIDER', 'peter_parker')
    #     task = scrapyd.schedule(scrapyd_project,
    #                             scrapyd_spider,
    #                             # settings=header_settings,
    #                             input_id=input_id_new,
    #                             )
    #     InputPeter.objects.filter(input_id=input_id).update(task_id=task)
    #
    #     return HttpResponseRedirect('/main/crawl_result1/')
    #     # return JsonResponse({'task_id': task, 'domain': domain, 'domain_id': domain_id,
    #     #                      'status': 'started'})
    # elif request.method == 'GET':
    #     # We passed them back to here to check the status of crawling
    #     # And if crawling is completed, we respond back with a crawled data.
    #     task_id = request.GET.get('task_id', None)
    #     if not task_id:
    #         return JsonResponse({'error': 'Missing args'})
    #     # Here we check status of crawling that just started a few seconds ago.
    #     # If it is finished, we can query from database and get results
    #     # If it is not finished we can return active status
    #     # Possible results are -> pending, running, finished
    #     status = scrapyd.job_status('scrapy_app', task_id)
    #     if status == 'finished':
    #         try:
    #             item = OutputPeter.objects.get(task_id=task_id)
    #             return JsonResponse({'data': item.to_dict['data']})
    #         except Exception as e:
    #             return JsonResponse({'error': str(e)})
    #     else:
    #         return JsonResponse({'status': status})
    #
