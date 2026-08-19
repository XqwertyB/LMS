from .serializers import HemisModelSerializer,HemisTokenSerializer,HemisBaseSerializer
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from .models import HemisModel,HemisToken,Hemis_Base


class HemisModellist(generics.ListCreateAPIView):
    queryset = HemisModel.objects.filter(status_action=True)
    serializer_class = HemisModelSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        return self.list(self, request, *args, **kwargs)
class HemisModelupdateAPIView(generics.UpdateAPIView):
    queryset = HemisModel.objects.filter(status_action=True)
    serializer_class = HemisModelSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class HemisModelDeactive(APIView):
    def get(self, request):
        # Handle GET request
        obj = HemisModel.objects.filter(status_action=False)
        serializer = HemisModelSerializer(obj,many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id=request.data.get('id')
            if not id :
                data ={'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = HemisModel.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data,status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data,status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

class HemisTokenlist(generics.ListCreateAPIView):
    queryset = HemisToken.objects.filter(status=True)
    serializer_class = HemisTokenSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        return self.list(self, request, *args, **kwargs)
class HemisTokenupdateAPIView(generics.UpdateAPIView):
    queryset = HemisToken.objects.filter(status=True)
    serializer_class = HemisTokenSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class HemisTokenDeactive(APIView):
    def get(self, request):
        # Handle GET request
        obj = HemisToken.objects.filter(status=False)
        serializer = HemisTokenSerializer(obj,many=True)
        data = {'Ochirlgan tokenlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id=request.data.get('id')
            if not id :
                data ={'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = HemisToken.objects.get(pk=id)
                obj.status = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data,status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data,status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class HemisBaselist(generics.ListCreateAPIView):
    queryset = Hemis_Base.objects.filter(status_action=True)
    serializer_class = HemisBaseSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        return self.list(self, request, *args, **kwargs)
class HemisBaseupdateAPIView(generics.UpdateAPIView):
    queryset = Hemis_Base.objects.filter(status_action=True)
    serializer_class = HemisBaseSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)


class HemisBaseDeactive(APIView):
    def get(self, request):
        # Handle GET request
        obj = Hemis_Base.objects.filter(status_action=False)
        serializer = HemisBaseSerializer(obj,many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id=request.data.get('id')
            if not id :
                data ={'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Hemis_Base.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data,status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data,status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_403_FORBIDDEN)



