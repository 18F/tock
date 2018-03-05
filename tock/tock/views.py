from django.shortcuts import render_to_response


def csrf_failure(request, reason=""):
    return render_to_response('403.html')
