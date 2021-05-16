from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response

# Create your views here.

class CreateUpdateDeleteView(APIView):
    model=None
    serializer=None
    def post(self, request, *args, **kwargs):
        user=request.user
        output_status=False
        output_detail="Falied"
        res_status=status.HTTP_400_BAD_REQUEST
        data={}
        extra_data={
            "user":user.id
        }
        serializer=self.serializer(data=request.data,extra_data=extra_data)
        if serializer.is_valid():
            serializer.save()
            output_status=True
            output_detail="Success"
            res_status=status.HTTP_200_OK
            data=serializer.data
        else:
            output_detail=serializer.errors
        context={
            "status":output_status,
            "detail":output_detail,
            "data":data
        }
        return Response(context, status=res_status)


    def delete(self, request, *args, **kwargs):
        user=request.user
        delete_data_id=request.GET.get("id")
        output_status=False
        output_detail="Falied"
        res_status=status.HTTP_400_BAD_REQUEST
        model=self.model.objects.filter(user=user,id=delete_data_id)
        if model:
            model.delete()
            output_status=True
            output_detail="Success"
            res_status=status.HTTP_400_BAD_REQUEST
        else:
            output_detail="you don't have access"
        context={
            "status":output_status,
            "detail":output_detail,
        }
        return Response(context, status=res_status)

    def put(self, request, *args, **kwargs):
        user=request.user
        update_data_id=request.data.get("id")
        output_status=False
        output_detail="Falied"
        res_status=status.HTTP_400_BAD_REQUEST
        data={}
        model=self.model.objects.filter(user=user,id=update_data_id).first()
        if model:
            serializer = self.serializer(model,data = request.data, partial = True)
            if serializer.is_valid():
                serializer.save()
                output_status=True
                output_detail="Data Updated"
                res_status=status.HTTP_400_BAD_REQUEST
                data=serializer.data
            else:
                output_detail=serializer.errors
        else:
            output_detail="you don't have access"
        context={
            "status":output_status,
            "detail":output_detail,
            "data":data
        }
        return Response(context, status=res_status)

