import re
import os
from django.conf import settings as django_settings
from rest_framework.views import APIView

from .utils import log_watch_request, get_request_ip
from .utils import get_streaming_response
from django.conf import settings
from rest_framework.permissions import AllowAny
from django.http import FileResponse, StreamingHttpResponse, HttpResponse

STREAM_DEFAULT_PERMISSION_CLASSES = getattr(settings, 'STREAM_DEFAULT_PERMISSION_CLASSES', (AllowAny,))
STREAM_DEFAULT_VIDEO_PATH_URL_VAR = getattr(settings, 'STREAM_DEFAULT_VIDEO_PATH_URL_VAR', 'path')
STREAM_MAX_LOAD_VOLUME = getattr(settings, 'STREAM_MAX_LOAD_VOLUME', 1 * 1024 * 1024)
STREAM_WATCH_LOG_ENABLED = getattr(settings, 'STREAM_WATCH_LOG_ENABLED', True)
STREAM_RANGE_HEADER_REGEX_PATTERN = getattr(settings, 'STREAM_RANGE_HEADER_REGEX_PATTER',
                                            r'bytes=(\d+)-(\d*)')


# ozim
# class VideoStreamAPIView(APIView):
#     """return StreamingHTTPResponse"""
#
#     permission_classes = STREAM_DEFAULT_PERMISSION_CLASSES
#
#     def get(self, request, *args, **kwargs):
#         """get range header & create streaming response"""
#         # initialize parameters
#         max_load_volume = STREAM_MAX_LOAD_VOLUME
#         path_key = STREAM_DEFAULT_VIDEO_PATH_URL_VAR
#         range_re_pattern = STREAM_RANGE_HEADER_REGEX_PATTERN
#         log_enabled = STREAM_WATCH_LOG_ENABLED
#         media_dir = django_settings.MEDIA_ROOT
#         media_url = django_settings.MEDIA_URL
#         # get video path & range header
#         video_path = request.GET.get(path_key)
#         range_header = request.META.get('HTTP_RANGE', '').strip()
#         video_path = video_path[1:]
#         range_re = re.compile(range_re_pattern, re.I)
#         video_path = video_path.replace(media_url, media_dir)
#         video_path = os.path.join(django_settings.BASE_DIR, video_path)
#         # log
#         if log_enabled:
#             ip = get_request_ip(request)
#             log_watch_request(video_path, request.user.is_authenticated, ip, request.user)
#
#         # create response
#         response = get_streaming_response(
#             path=video_path,
#             range_header=range_header,
#             range_re=range_re,
#             max_load_volume=max_load_volume,  # the maximum volume of the response body
#         )
#
#         return response
# chatgpt
# class VideoStreamAPIView(APIView):
#     permission_classes = STREAM_DEFAULT_PERMISSION_CLASSES
#
#     def get(self, request, *args, **kwargs):
#         max_load_volume = STREAM_MAX_LOAD_VOLUME
#         path_key = STREAM_DEFAULT_VIDEO_PATH_URL_VAR
#         range_re_pattern = STREAM_RANGE_HEADER_REGEX_PATTERN
#         log_enabled = STREAM_WATCH_LOG_ENABLED
#         media_dir = django_settings.MEDIA_ROOT
#         media_url = django_settings.MEDIA_URL
#
#         video_path = request.GET.get(path_key)
#         range_header = request.META.get("HTTP_RANGE", "").strip()
#         video_path = video_path[1:]
#         video_path = video_path.replace(media_url, media_dir)
#         video_path = os.path.join(django_settings.BASE_DIR, video_path)
#
#         if log_enabled:
#             ip = get_request_ip(request)
#             log_watch_request(video_path, request.user.is_authenticated, ip, request.user)
#
#         try:
#             response = get_streaming_response(
#                 path=video_path,
#                 range_header=range_header,
#                 range_re=re.compile(range_re_pattern, re.I),
#                 max_load_volume=max_load_volume,
#             )
#             response["Content-Type"] = "video/mp4"
#             response["Cache-Control"] = "no-cache, no-store, must-revalidate"
#             response["Pragma"] = "no-cache"
#             response["Expires"] = "0"
#             return response
#         except FileNotFoundError:
#             return Response({"error": "Video not found"}, status=404)
class VideoStreamAPIView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        # Path to the video file
        video_path = request.GET.get("path")
        if not video_path:
            return HttpResponse("Video path not provided", status=400)

        path_key = STREAM_DEFAULT_VIDEO_PATH_URL_VAR
        media_dir = django_settings.MEDIA_ROOT
        media_url = django_settings.MEDIA_URL
        video_path = request.GET.get(path_key)
        range_header = request.META.get("HTTP_RANGE", "").strip()
        video_path = video_path[1:]
        video_path = video_path.replace(media_url, media_dir)
        video_path = os.path.join(django_settings.BASE_DIR, video_path)
        # Resolve the full file path
        video_file = video_path
        if not os.path.exists(video_file):
            return HttpResponse("File not found", status=404)

        # Handle Range Header
        range_header = request.META.get('HTTP_RANGE', '').strip()
        range_match = re.match(r"bytes=(\d+)-(\d*)", range_header)

        file_size = os.path.getsize(video_file)
        content_type = "video/mp4"

        if range_match:
            start, end = range_match.groups()
            start = int(start)
            end = int(end) if end else file_size - 1
            length = end - start + 1

            with open(video_file, 'rb') as video:
                video.seek(start)
                data = video.read(length)

            response = HttpResponse(data, status=206, content_type=content_type)
            response['Content-Range'] = f"bytes {start}-{end}/{file_size}"
            response['Accept-Ranges'] = 'bytes'
            response['Content-Length'] = str(length)
        else:
            # Serve the full file if no Range header is present
            response = FileResponse(open(video_file, 'rb'), content_type=content_type)
            response['Content-Length'] = str(file_size)

        # Add CORS headers for Safari
        response['Access-Control-Allow-Origin'] = '*'
        response['Access-Control-Allow-Headers'] = 'Range'
        response['Accept-Ranges'] = 'bytes'

        return response

# import os
# import re
# import urllib.parse
# import mimetypes
#
# from django.conf import settings
# from django.core.exceptions import PermissionDenied
# from django.http import FileResponse, HttpResponse
# from rest_framework.views import APIView
#
#
# ALLOWED_EXT = {".mp4", ".webm", ".mov", ".mkv"}
#
#
# def secure_path(raw_path: str) -> str:
#     if not raw_path:
#         raise PermissionDenied("Empty path")
#
#     # --- decode (handle %2e%2e and double encoding) ---
#     p = urllib.parse.unquote(raw_path)
#     p = urllib.parse.unquote(p)
#
#     # --- normalize ---
#     p = p.replace("\\", "/").lstrip("/")
#
#     # --- remove MEDIA_URL prefix if present (/media/...) ---
#     media_url = settings.MEDIA_URL.lstrip("/")
#     if p.startswith(media_url):
#         p = p[len(media_url):]
#
#     # --- fast deny ---
#     if any(x in p for x in ("..", "\x00")):
#         raise PermissionDenied("Traversal detected")
#
#     base = os.path.realpath(settings.MEDIA_ROOT)
#     target = os.path.realpath(os.path.join(base, p))
#
#     # --- ensure inside MEDIA_ROOT (symlink-safe) ---
#     if not (target == base or target.startswith(base + os.sep)):
#         raise PermissionDenied("Out of media root")
#
#     # --- extension whitelist ---
#     ext = os.path.splitext(target)[1].lower()
#     if ext not in ALLOWED_EXT:
#         raise PermissionDenied("Invalid extension")
#
#     return target
#
#
# class VideoStreamAPIView(APIView):
#     permission_classes = []
#
#     def get(self, request, *args, **kwargs):
#         raw_path = request.GET.get("path")
#         if not raw_path:
#             return HttpResponse("Path required", status=400)
#
#         try:
#             video_file = secure_path(raw_path)
#         except PermissionDenied:
#             return HttpResponse("Forbidden", status=403)
#
#         if not os.path.exists(video_file):
#             return HttpResponse("Not found", status=404)
#
#         file_size = os.path.getsize(video_file)
#
#         # --- detect content-type dynamically ---
#         content_type, _ = mimetypes.guess_type(video_file)
#         content_type = content_type or "application/octet-stream"
#
#         # --- Range parsing ---
#         range_header = request.META.get("HTTP_RANGE", "").strip()
#         match = re.match(r"bytes=(\d+)-(\d*)", range_header)
#
#         if match:
#             start, end = match.groups()
#             start = int(start)
#             end = int(end) if end else file_size - 1
#
#             if start >= file_size:
#                 return HttpResponse(status=416)
#
#             end = min(end, file_size - 1)
#             length = end - start + 1
#
#             with open(video_file, "rb") as f:
#                 f.seek(start)
#                 data = f.read(length)
#
#             response = HttpResponse(data, status=206, content_type=content_type)
#             response["Content-Range"] = f"bytes {start}-{end}/{file_size}"
#             response["Content-Length"] = str(length)
#         else:
#             response = FileResponse(open(video_file, "rb"), content_type=content_type)
#             response["Content-Length"] = str(file_size)
#
#         response["Accept-Ranges"] = "bytes"
#
#         # optional (agar kerak bo‘lsa)
#         response["Access-Control-Allow-Origin"] = "*"
#         response["Access-Control-Allow-Headers"] = "Range"
#
#         return response