from config.permissions import AllowOnlyTrustedOrigins
from shared.permissions import IsAdminTeacherOrStudent, IsAdmin
from .serializers import OtmSerializer,OtmtypeSerializer,OtmshapeSerializer,OtmUpdateSerializer,CitySerializer,OtmSectionSerializer
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAdminUser
from .models import Otm,Otmtype,Otmshape,City,OtmSection
from django_filters.rest_framework import DjangoFilterBackend
#OTM korish va yartish
class OtmList(APIView):
    # Uncomment the following line if you want to restrict access
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent]

    def post(self, request, *args, **kwargs):
        if Otm.objects.exists():
            return Response({"error": "Uji OTM qoshilgan faqat bita qo`shiladi."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = OtmSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, *args, **kwargs):
        obj = Otm.objects.last()
        if obj is None:
            return Response({"error": "No OTM found."}, status=status.HTTP_404_NOT_FOUND)
        serializer = OtmSerializer(obj)
        return Response(serializer.data)
#http://127.0.0.1:8000/api/otm/update/61505f0d-c276-44c1-b9de-453e3916d835
class OtmupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    #permission_classes = [AllowAny, ]
    queryset = Otm.objects.all()
    serializer_class = OtmUpdateSerializer
    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

class OtmGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent]
    def get(self,request,pk):
        try:
            obj = Otm.objects.get(id=pk)
            serializer = OtmSerializer(obj,many=False)
            return Response(serializer.data)
        except:
            return Response({'error':'Bu ko`rinshdagi obekt yo`q'})


#Otmi type ko`rish va yartish
class Otmtypelist(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent]
    queryset = Otmtype.objects.filter(status_action=True)
    serializer_class = OtmtypeSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        return self.list(self, request, *args, **kwargs)
class OtmtypeupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    queryset = Otmtype.objects.filter(status_action=True)
    serializer_class = OtmtypeSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

class OtmtypeGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent]
    def get(self,request,pk):
        try:
            obj = Otmtype.objects.get(id=pk)
            serializer = OtmtypeSerializer(obj,many=False)
            return Response(serializer.data)
        except:
            return Response({'error':'Bu ko`rinshdagi obekt yo`q'})



class Otmtypedelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    def get(self, request):
        # Handle GET request
        obj = Otmtype.objects.filter(status_action=False)
        serializer = OtmtypeSerializer(obj,many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id=request.data.get('id')
            if not id :
                data ={'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Otmtype.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data,status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data,status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_403_FORBIDDEN)


class Otmshapelist(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent]
    queryset = Otmshape.objects.filter(status_action=True)
    serializer_class = OtmshapeSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        return self.list(self, request, *args, **kwargs)


class OtmshapeupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    queryset = Otmshape.objects.filter(status_action=True)
    serializer_class = OtmshapeSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

class OtmshapeGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent]
    def get(self,request,pk):
        try:
            obj = Otmshape.objects.get(id=pk)
            serializer = OtmshapeSerializer(obj,many=False)
            return Response(serializer.data)
        except:
            return Response({'error':'Bu ko`rinshdagi obekt yo`q'})



class Otmshapedelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    def get(self, request):
        # Handle GET request
        obj = Otmshape.objects.filter(status_action=False)
        serializer = OtmshapeSerializer(obj,many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id=request.data.get('id')
            if not id :
                data ={'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = Otmshape.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data,status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data,status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

class Citylist(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent]
    queryset = City.objects.filter(status_action=True)
    serializer_class = CitySerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        return self.list(self, request, *args, **kwargs)


class CityupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    queryset = City.objects.filter(status_action=True)
    serializer_class = CitySerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

class OtmCityGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent]
    def get(self,request,pk):
        try:
            obj = City.objects.get(id=pk)
            serializer = CitySerializer(obj,many=False)
            return Response(serializer.data)
        except:
            return Response({'error':'Bu ko`rinshdagi obekt yo`q'})



class Citydelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    def get(self, request):
        # Handle GET request
        obj = City.objects.filter(status_action=False)
        serializer = CitySerializer(obj,many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id=request.data.get('id')
            if not id :
                data ={'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = City.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data,status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data,status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_403_FORBIDDEN)

class OtmSectionlist(generics.ListCreateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent]
    queryset = OtmSection.objects.filter(status_action=True)
    serializer_class = OtmSectionSerializer

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):

        return self.list(self, request, *args, **kwargs)


class OtmSectionupdateAPIView(generics.UpdateAPIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    queryset = OtmSection.objects.filter(status_action=True)
    serializer_class = OtmSectionSerializer

    def patch(self, request, *args, **kwargs):
        return self.partial_update(request, *args, **kwargs)

    def put(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

class OtmSectionGetAPIView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdminTeacherOrStudent]
    def get(self,request,pk):
        try:
            obj = OtmSection.objects.get(id=pk)
            serializer = OtmSectionSerializer(obj,many=False)
            return Response(serializer.data)
        except:
            return Response({'error':'Bu ko`rinshdagi obekt yo`q'})


class OtmSectiondelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    def get(self, request):
        # Handle GET request
        obj = OtmSection.objects.filter(status_action=False)
        serializer = OtmSectionSerializer(obj,many=True)
        data = {'Ochirlgan malumotlar': serializer.data}
        return Response(data, status=status.HTTP_200_OK)

    def post(self, request):
        if 'id' in request.data:
            id=request.data.get('id')
            if not id :
                data ={'id': 'id bosh qiymat kirtilgan'}
                return Response(data, status=status.HTTP_400_BAD_REQUEST)
            try:
                obj = OtmSection.objects.get(pk=id)
                obj.status_action = False
                obj.save()
                data = {'xabar': 'malumot ochirildi!'}
                return Response(data,status=status.HTTP_200_OK)
            except:
                data = {'id': 'id malumotlar omboridan topilmadi'}
                return Response(data,status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(status=status.HTTP_403_FORBIDDEN)
