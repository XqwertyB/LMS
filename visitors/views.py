import urllib

import requests
import xmltodict
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from bigbluebutton.checksum_genrate import checksum_genration
from bigbluebutton.models import Bigbluebutton_Model, Bigbluebutton_sub, BigbluebuttonMain
from rest_framework import status
from bigbluebutton.views import Bigbluebutton_join_mentor
from config.permissions import AllowOnlyTrustedOrigins
from content.serializers import ContentViewSerializer
from employee.models import Employee
from shared.utils import CustomPageNumberPagination
from students.models import Student
from user.models import User
from user.permission import IsAdmin
from .serializers import BigBlubuttonSerializer, CTecherListAll_Serializer, Content_teacherlistSerailer, \
    Topic_list_Seralizer
from content.models import Content_teacher, Topic
from django.db.models import F, Q
from rest_framework.pagination import PageNumberPagination
from django.db import transaction


class Room_BigbluebuttonListView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    serializer_class = BigBlubuttonSerializer
    pagination_class = CustomPageNumberPagination

    def get(self, request):
        try:
            patok = request.query_params.get('patok', None)
            obj = Bigbluebutton_Model.objects.filter(status=True)
            if patok == '1':
                obj = obj.exclude(topic_id__isnull=True)  # topic bor
            elif patok == '2':  # Mavzuv boyicha
                obj = obj.exclude(team_id__isnull=True)  # patok bor
            else:
                obj = obj.exclude(topic_id__isnull=True, team_id__isnull=True)

            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(obj, request)

            serializer = self.serializer_class(paginated_queryset, many=True)

        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return paginator.get_paginated_response(serializer.data)
        # return Response(seralizer.data, status=status.HTTP_200_OK)


class TeacherList_View(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]
    pagination_class = CustomPageNumberPagination
    serializer_class = CTecherListAll_Serializer

    def get(self, request):
        try:
            # Get the full name filter from query parameters
            teacher_fullname = request.query_params.get('teacher_fullname', None)
            if teacher_fullname:
                filtered_employees = Employee.objects.filter(full_name__icontains=teacher_fullname)
                # Query to get distinct teachers with the relevant data

                distinct_teachers_with_data = Content_teacher.objects.filter(
                    teacher_id__in=filtered_employees).distinct(
                    'teacher_id')
            else:
                distinct_teachers_with_data = Content_teacher.objects.distinct('teacher_id')

            # Initialize custom paginator

            paginator = self.pagination_class()
            paginated_queryset = paginator.paginate_queryset(distinct_teachers_with_data, request)

            serializer = self.serializer_class(paginated_queryset, many=True)
            return paginator.get_paginated_response(serializer.data)
        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class Content_teacher_List_View(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    def get(self, request, pk):
        try:
            content = Content_teacher.objects.filter(teacher_id=pk)
            seralizer = Content_teacherlistSerailer(content, many=True)
            return Response({
                'results': seralizer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class Topic_teacher_list_View(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    def get(self, request, pk):
        try:
            content = Topic.objects.filter(content_teacher_connect=pk).order_by('number')
            seralizer = Topic_list_Seralizer(content, many=True)
            return Response({
                'results': seralizer.data
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class EnterRoom(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin, ]

    def get(self, request, pk):

        try:
            bigbluebutton = Bigbluebutton_Model.objects.get(id=pk)
            try:
                username = 'Nazoratchi'
                try:
                    base_url = BigbluebuttonMain.objects.last()
                    "URl qaytarish qo`shiladigan hona uchun mentor uchun "

                except:
                    data = {'base_url': 'base_url malumotlar omboridan topilmadi'}
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                try:
                    send_url = Bigbluebutton_sub.objects.get(uniq_id=5)
                    "URl qaytarish qo`shiladigan hona uchun mentor uchun "

                except:
                    data = {'send_url': 'send_url metod malumotlar omboridan topilmadi'}
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)

                if bigbluebutton.status:
                    query = ""
                    meetingID = str(bigbluebutton.meetingID)
                    moderatorPW = urllib.parse.quote(str(bigbluebutton.moderatorPW).encode("utf-8"))
                    redirect = bigbluebutton.redirect
                    # Print field names and their values
                    query += 'meetingID=' + meetingID + '&password=' + moderatorPW + '&redirect=' + str(
                        redirect).lower()

                    # print(query)

                    xquery = send_url.url_method + query
                    # print(xquery)

                    checksum = checksum_genration(xquery, base_url.sicret_key)
                    # print(checksum)
                    url = f'{base_url.main_url}{send_url.url}?{query}&checksum={checksum}'
                    response = requests.get(url)
                    if response.status_code == 200:

                        parsed_dict = xmltodict.parse(response.text)

                        if 'response' in parsed_dict:
                            response_data = parsed_dict['response']
                            if response_data.get('returncode') == 'FAILED':
                                # Check if the specific messageKey is 'notFound'
                                if response_data.get('messageKey') == 'notFound':
                                    return Response(
                                        {'success': False,
                                         'message': 'Video dars hali boshlanmagan!, O`qituvchiga murojaat qiling!'},
                                        status=status.HTTP_404_NOT_FOUND)
                                else:
                                    return Response({'success': False,
                                                     'message': response_data.get('message', 'Unknown error occurred')},
                                                    status=status.HTTP_400_BAD_REQUEST)
                            if response_data.get('running') == 'false':
                                return Response({'success': False,
                                                 'message': 'Video dars hali boshlanmagan!, O`qituvchiga murojaat qiling!'},
                                                status=status.HTTP_400_BAD_REQUEST)
                try:
                    send_url = Bigbluebutton_sub.objects.get(uniq_id=2)
                    "URl qaytarish qo`shiladigan hona uchun mentor uchun "

                except:
                    data = {'send_url': 'send_url metod malumotlar omboridan topilmadi'}
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                if bigbluebutton.status:
                    query = ""
                    meetingID = str(bigbluebutton.meetingID)
                    fullName = urllib.parse.quote(str(username).encode("utf-8"))
                    moderatorPW = urllib.parse.quote(str(bigbluebutton.moderatorPW).encode("utf-8"))
                    redirect = bigbluebutton.redirect
                    # Print field names and their values
                    query += 'fullName=' + fullName + '&meetingID=' + meetingID + '&password=' + moderatorPW + '&redirect=' + str(
                        redirect).lower()

                    # print(query)

                    xquery = send_url.url_method + query
                    # print(xquery)

                    checksum = checksum_genration(xquery, base_url.sicret_key)
                    # print(checksum)
                    url = f'{base_url.main_url}{send_url.url}?{query}&checksum={checksum}'
                    urls = 'http://test-install.blindsidenetworks.com/bigbluebutton/api/join?fullName=User+6886500&meetingID=random-4728086&password=mp&redirect=true&checksum=ff8515a2e1388807c1452acd94580dca5f87bdff'
                    # response = requests.get(urls)
                    return Response({'succes': 'true', 'url': url}, status=status.HTTP_200_OK)
                else:
                    return Response({'error': 'Xona ochilmagan!'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class GetInfoRoom(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    def get_student_group(self, user_id):
        try:
            student = Student.objects.get(id=user_id)
            return {
                'id': student.group.id,
                'name': student.group.name,
            }
        except Student.DoesNotExist:
            return "Talaba guruhi topilmadi!"

    def get(self, request, pk):
        try:
            bigbluebutton = Bigbluebutton_Model.objects.get(id=pk)
            try:
                username = 'Nazoratchi'
                try:
                    base_url = BigbluebuttonMain.objects.last()
                    "URl qaytarish qo`shiladigan hona uchun mentor uchun "

                except:
                    data = {'base_url': 'base_url malumotlar omboridan topilmadi'}
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)
                try:
                    send_url = Bigbluebutton_sub.objects.get(uniq_id=5)
                    "URl qaytarish qo`shiladigan hona uchun mentor uchun "

                except:
                    data = {'send_url': 'send_url metod malumotlar omboridan topilmadi'}
                    return Response(data, status=status.HTTP_400_BAD_REQUEST)

                if bigbluebutton.status:
                    query = ""
                    meetingID = str(bigbluebutton.meetingID)
                    moderatorPW = urllib.parse.quote(str(bigbluebutton.moderatorPW).encode("utf-8"))
                    redirect = bigbluebutton.redirect
                    # Print field names and their values
                    query += 'meetingID=' + meetingID + '&password=' + moderatorPW + '&redirect=' + str(
                        redirect).lower()

                    # print(query)

                    xquery = send_url.url_method + query
                    # print(xquery)

                    checksum = checksum_genration(xquery, base_url.sicret_key)
                    # print(checksum)
                    url = f'{base_url.main_url}{send_url.url}?{query}&checksum={checksum}'
                    response = requests.get(url)
                    if response.status_code == 200:
                        parsed_dict = xmltodict.parse(response.text)
                        # print(parsed_dict)
                        if 'response' in parsed_dict:
                            response_data = parsed_dict['response']
                            if response_data.get('returncode') == 'FAILED':
                                # Check if the specific messageKey is 'notFound'
                                if response_data.get('messageKey') == 'notFound':
                                    return Response(
                                        {'success': False, 'message': 'Video dars hali boshlanmagan!'},
                                        status=status.HTTP_404_NOT_FOUND)
                                else:
                                    return Response({'success': False,
                                                     'message': response_data.get('message', 'Unknown error occurred')},
                                                    status=status.HTTP_400_BAD_REQUEST)
                            if response_data.get('running') == 'false':
                                return Response({'success': False,
                                                 'message': 'Video dars hali boshlanmagan!, O`qituvchiga murojaat qiling!'},
                                                status=status.HTTP_400_BAD_REQUEST)
                            # Remove or mask attendeePW and moderatorPW
                            if 'attendeePW' in response_data:
                                del response_data['attendeePW']  # You can also set it to a masked value if needed
                            if 'moderatorPW' in response_data:
                                del response_data['moderatorPW']
                        if 'attendees' in response_data and response_data['attendees'] is not None:
                            attendees = response_data['attendees']['attendee']

                            # Ensure that 'attendees' is a list before filtering
                            if isinstance(attendees, list):
                                viewers = [
                                    {
                                        **attendee,
                                        "group": self.get_student_group(attendee["userID"])
                                    }
                                    for attendee in attendees if attendee["role"] == "VIEWER"
                                ]
                                # viewers = [attendee for attendee in attendees if attendee['role'] == 'VIEWER']
                                viewer_count = len(viewers)
                                if 'attendees' in response_data:
                                    del response_data['attendees']
                            elif isinstance(attendees, dict):  # Single attendee case
                                viewers = [attendees] if attendees['role'] == 'VIEWER' else []
                                viewer_count = len(viewers)
                                if 'attendees' in response_data:
                                    del response_data['attendees']
                            else:
                                viewers = []
                                viewer_count = 0
                        else:
                            # Handle case where attendees is None
                            viewers = []
                            viewer_count = 0

                        return Response({'succes': 'True', 'results': parsed_dict['response'], 'viewers': viewers,
                                         'viewer_count': viewer_count}, status=status.HTTP_200_OK)
                    else:
                        return Response({'succes': 'False', 'message': 'BBB muamo mavjud!'},
                                        status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({'error': 'Xona ochilmagan!'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({'errors': True, 'message': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class RealRoomListView(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    def get(self, request):
        try:
            base_url = BigbluebuttonMain.objects.last()
            "URl qaytarish qo`shiladigan hona uchun mentor uchun "

        except:
            data = {'base_url': 'base_url malumotlar omboridan topilmadi'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        try:
            send_url = Bigbluebutton_sub.objects.get(uniq_id=6)
            "URl qaytarish qo`shiladigan hona uchun mentor uchun "

        except:
            data = {'send_url': 'send_url metod malumotlar omboridan topilmadi'}
            return Response(data, status=status.HTTP_400_BAD_REQUEST)
        xquery = send_url.url_method
        checksum = checksum_genration(xquery, base_url.sicret_key)
        url = f'{base_url.main_url}{send_url.url}?checksum={checksum}'
        response = requests.get(url)
        if response.status_code == 200:
            parsed_dict = xmltodict.parse(response.text)
            if 'response' in parsed_dict:
                response_data = parsed_dict['response']
                if response_data.get('returncode') == 'FAILED':
                    # Check if the specific messageKey is 'notFound'
                    if response_data.get('messageKey') == 'notFound':
                        return Response(
                            {'success': False, 'message': 'Video dars hali boshlanmagan!'},
                            status=status.HTTP_404_NOT_FOUND)
                if 'messageKey' in response_data:
                    if response_data.get('messageKey') == 'noMeetings':
                        return Response(
                            {'success': False, 'message': 'Darsxonalar mavjud emas!'},
                            status=status.HTTP_404_NOT_FOUND)
                if 'meetings' in response_data:
                    meetings = response_data['meetings']
                    if 'meeting' in meetings:
                        meeting = meetings['meeting']
                        list_meetings = []
                        for item in meeting:
                            dict_meeting = {}
                            dict_meeting['meetingID'] = item['meetingID']
                            dict_meeting['running'] = item['running']

                    pass

            return Response({'succes': 'True', 'results': parsed_dict['response']}, status=status.HTTP_200_OK)
        else:
            return Response({'succes': 'False', 'message': 'Bigbluebutton bilan aloqa mavjud emas!'},
                            status=status.HTTP_400_BAD_REQUEST)


import time


class ListMettingRoomDelete(APIView):
    permission_classes = [AllowOnlyTrustedOrigins,IsAdmin,]
    def bbb_baseurl(self):
        base_url = BigbluebuttonMain.objects.last()
        if not base_url:
            raise ValueError("Asosiy manzil malumotlar omboridan topilmadi, Adminga murojaat qiling!")
        return base_url

    def bbb_sendingurl(self, number):
        try:
            return Bigbluebutton_sub.objects.get(uniq_id=number)
        except Bigbluebutton_sub.DoesNotExist:
            raise ValueError("send_url metod malumotlar omboridan topilmadi")

    def bbb_delete(self, base_url, obj):
        seconf_url = self.bbb_sendingurl(7)
        meetingID = urllib.parse.quote(str(obj.meetingID).encode("utf-8"))
        moderatorPW = urllib.parse.quote(str(obj.moderatorPW).encode("utf-8"))
        query = 'meetingID=' + meetingID + 'moderatorPW=' + moderatorPW
        xquery = seconf_url.url_method + 'meetingID=' + meetingID + 'moderatorPW=' + moderatorPW
        checksum = checksum_genration(xquery, base_url.sicret_key)
        url = f'{base_url.main_url}{seconf_url.url}?{query}&checksum={checksum}'
        response = requests.get(url)
        if response.status_code == 200:
            parsed_dict = xmltodict.parse(response.text)
        else:
            parsed_dict = xmltodict.parse(response.text)
        return parsed_dict

    def bbb_over_delete(self, base_url, meetingID, moderatorPW):
        seconf_url = self.bbb_sendingurl(7)
        meetingID = urllib.parse.quote(str(meetingID).encode("utf-8"))
        moderatorPW = urllib.parse.quote(str(moderatorPW).encode("utf-8"))
        query = f"meetingID={meetingID}&password={moderatorPW}"
        print(query)
        xquery = seconf_url.url_method + query
        checksum = checksum_genration(xquery, base_url.sicret_key)
        url = f'{base_url.main_url}{seconf_url.url}?{query}&checksum={checksum}'
        response = requests.get(url)
        if response.status_code == 200:
            parsed_dict = xmltodict.parse(response.text)
            print(parsed_dict)
        else:
            parsed_dict = xmltodict.parse(response.text)

        return parsed_dict

    def get(self, request):
        try:
            base_url = self.bbb_baseurl()
            seconf_url = self.bbb_sendingurl(6)
            xquery = seconf_url.url_method
            checksum = checksum_genration(xquery, base_url.sicret_key)
            url = f'{base_url.main_url}{seconf_url.url}?checksum={checksum}'
            response = requests.get(url)
            if response.status_code == 200:
                parsed_dict = xmltodict.parse(response.text)
                if 'response' in parsed_dict:
                    response_data = parsed_dict['response']
                if response_data.get('returncode') == 'FAILED':
                    if response_data.get('messageKey') == 'notFound':
                        return Response(
                            {'success': False, 'message': 'Video dars hali boshlanmagan!'},
                            status=status.HTTP_404_NOT_FOUND)
                if 'messageKey' in response_data:
                    if response_data.get('messageKey') == 'noMeetings':
                        return Response(
                            {'success': False, 'message': 'Darsxonalar mavjud emas!'},
                            status=status.HTTP_404_NOT_FOUND)
                if 'meetings' in response_data:
                    meetings = response_data['meetings']
                    if 'meeting' in meetings:
                        meeting = meetings['meeting']
                    data_meeting = []
                    number = 1
                    for item in meeting:
                        dict_meeting = {}
                        dict_meeting['number'] = number
                        dict_meeting['meetingID'] = item['meetingID']
                        dict_meeting['running'] = item['running']
                        dict_meeting['moderatorPW'] = item['moderatorPW']
                        self.bbb_over_delete(base_url, item['meetingID'], item['moderatorPW'])
                        time.sleep(1)
                        data_meeting.append(dict_meeting)
                        number = number + 1
                error_list = []
                acchot = []
                # with transaction.atomic():
                #     for jitem in data_meeting:
                #         try:
                #             info = Bigbluebutton_Model.objects.get(meetingID=jitem['meetingID'])
                #             bbb_delete = self.bbb_delete(base_url,info)
                #             if info.team_id is not None:
                #                 info.team_id.delete()
                #             info.delete()
                #             zer_dict = {
                #                 'meetingID': jitem['meetingID'],
                #                 'info': bbb_delete
                #             }
                #             acchot.append(zer_dict)
                #
                #         except Exception as ex:
                #             zer_dict = {
                #                 'meetingID': jitem['meetingID'],
                #                 'error': str(ex)
                #             }
                #             error_list.append(zer_dict)

                return Response({'success': True, 'error': error_list, 'info': acchot, 'result': data_meeting},
                                status=status.HTTP_200_OK)
            else:
                return Response(
                    {'error': True, 'message': 'Bigbluebutton bilan aloqa mavjud emas,Adminga murojaat qiling!'},
                    status=status.HTTP_400_BAD_REQUEST)
        except Exception as ex:
            return Response({'error': True, 'message': 'Texnik muamo!:' + str(ex)}, status=status.HTTP_400_BAD_REQUEST)
