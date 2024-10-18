from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash, logout, get_user_model
from django.contrib import messages
from .models import Notification, Dentist, Clinic_Info, Event, Patient, Appointment, Treatment, Payment, MedicalHistory, Invoice_items, Invoice
from .forms import ClinicForm, DentistForm, CustomUserChangeForm, SignupForm, PatientForm, AppointmentForm, TreatmentForm, PaymentForm, MedicalHistoryForm, InvoiceForm, Invoice_itemsForm
from django.forms import modelformset_factory
from django.http import JsonResponse, Http404, HttpResponse
from django.db.models import F, Sum
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone
from datetime import datetime
from django.core.mail import send_mail
from django.conf import settings
import random
from django.contrib.auth.decorators import login_required, user_passes_test
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.decorators import api_view
from .serializers import Invoice_ItemSerializer, DentistSerializer, ClinicInfoSerializer, AppointmentSerializer, MedicalHistorySerializer, InvoiceSerializer, PatientSerializer, TreatmentSerializer, UserAccountSerializer
from django.core.signing import Signer, BadSignature
from datetime import timedelta, datetime
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

User = get_user_model()

# class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
#     def validate(self, attrs):
#         # This part handles authentication
#         data = super().validate(attrs)

#         # Check if the user has verified their email
#         user = self.user
#         if not user.is_email_verified:
#             raise serializers.ValidationError({"detail": "Please verify your email before logging in."})

#         return data

# class CustomTokenObtainPairView(TokenObtainPairView):
#     serializer_class = CustomTokenObtainPairSerializer

@api_view(['GET'])
def confirm_email(request, token):
    signer = Signer()
    try:
        email = signer.unsign(token)
        user = User.objects.get(email=email)
        user.is_email_verified = True
        user.save()
        return HttpResponse("Email confirmed successfully!")
    except (BadSignature, User.DoesNotExist):
        return HttpResponse("Invalid confirmation link.", status=400)

class DentistAPIView(APIView):
    permission_classes = []

    def get(self, request):
        dentist = Dentist.objects.all()
        serializer = DentistSerializer(dentist, many=True, context={'request': request})
        return Response(serializer.data)

class PatientListAPIView(APIView):
    permission_classes = [IsAuthenticated]  # Require the user to be authenticated

    def get(self, request):
        # Get the patient associated with the authenticated user
        try:
            patient = Patient.objects.get(user_account=request.user)
        except Patient.DoesNotExist:
            return Response({"detail": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PatientSerializer(patient, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request):
        try:
            patient = Patient.objects.get(user_account=request.user)
        except Patient.DoesNotExist:
            return Response({"detail": "Patient not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = PatientSerializer(patient, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save()  # This will update the existing patient
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SignupAPIView(APIView):
    permission_classes = [] 

    def post(self, request):
        serializer = PatientSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TreatmentAPIView(APIView):
    permission_classes = []

    def get(self, request):
        treatments = Treatment.objects.all()
        serializer = TreatmentSerializer(treatments, many=True, context={'request': request})
        return Response(serializer.data)
    
class ClinicInfoAPIView(APIView):
    permission_classes = []

    def get(self, request):
        clinic_info = Clinic_Info.objects.first()
        serializer = ClinicInfoSerializer(clinic_info, context={'request': request})
        return Response(serializer.data)
    
class InvoiceAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        patient = Patient.objects.get(user_account=request.user)
        
        # Check if an 'invoiceId' is passed as a query parameter
        invoice_id = request.query_params.get('invoiceId', None)
        
        if invoice_id:
            try:
                # Fetch a specific invoice for the patient using the ID
                invoice = Invoice.objects.get(id=invoice_id, patient=patient)
                serializer = InvoiceSerializer(invoice, context={'request': request})
                return Response(serializer.data, status=status.HTTP_200_OK)
            except Invoice.DoesNotExist:
                return Response({'detail': 'Invoice not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # If no 'invoiceId' is provided, return all invoices for the patient
        invoices = Invoice.objects.filter(patient=patient)
        serializer = InvoiceSerializer(invoices, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class Invoice_ItemAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Check if an 'invoiceId' is passed as a query parameter
        invoice_id = request.query_params.get('invoiceId', None)
        if invoice_id:
            try:
                # Fetch the specific invoice using the ID
                invoice = Invoice.objects.get(id=invoice_id)
                # Fetch all items for the specified invoice
                invoice_items = Invoice_items.objects.filter(invoice=invoice_id)
                
                # Serialize both the invoice and its items
                invoice_serializer = InvoiceSerializer(invoice, context={'request': request})
                invoice_items_serializer = Invoice_ItemSerializer(invoice_items, many=True, context={'request': request})

                # Combine the data into a single response
                return Response({
                    'invoice': invoice_serializer.data,
                    'invoice_items': invoice_items_serializer.data
                }, status=status.HTTP_200_OK)
            except Invoice_items.DoesNotExist:
                return Response({'detail': 'Invoice items not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        # If no 'invoiceId' is provided, return a bad request response
        return Response({'detail': 'invoiceId query parameter is required.'}, status=status.HTTP_400_BAD_REQUEST)
    
class MedicalHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        patient = Patient.objects.get(user_account=request.user)
        medHis = MedicalHistory.objects.filter(patient=patient)
        serializer = MedicalHistorySerializer(medHis, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        patient = Patient.objects.get(user_account=request.user)
        serializer = MedicalHistorySerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(patient=patient)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    		
    def put(self, request):
        patient = Patient.objects.get(user_account=request.user)
        try:
            medhis = MedicalHistory.objects.get(id=request.POST.get('id'))
        except MedicalHistory.DoesNotExist:
            return Response({"detail": "Medical History not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = MedicalHistorySerializer(medhis, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save(patient=patient)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
    def delete(self, request):
        patient = Patient.objects.get(user_account=request.user)
        medhis_id = request.data.get('id')
        
        try:
            medhis = MedicalHistory.objects.get(id=medhis_id, patient=patient)
        except MedicalHistory.DoesNotExist:
            return Response({"detail": "Medical History not found."}, status=status.HTTP_404_NOT_FOUND)

        medhis.delete()
        return Response({"detail": "Medical History deleted successfully."}, status=status.HTTP_204_NO_CONTENT)    

class AppointmentAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        patient = Patient.objects.get(user_account=request.user)
        appointment = Appointment.objects.filter(patient=patient)
        serializer = AppointmentSerializer(appointment, many=True, context={'request': request})
        return Response(serializer.data)
    
    def post(self, request):
        patient = Patient.objects.get(user_account=request.user)
        serializer = AppointmentSerializer(data=request.data, context={'request': request})
        
        start_time_str = request.data.get('start_time')
        start_time = datetime.strptime(start_time_str, '%H:%M')
        treatment_id = request.data.get('treatment')
        treatment = Treatment.objects.get(id=treatment_id)

        # Calculate the end time using the treatment duration.
        duration_minutes = treatment.duration  # Assuming `duration` is an integer field in minutes.
        end_time = start_time + timedelta(minutes=duration_minutes)

        if serializer.is_valid():
            appointment = serializer.save(patient=patient, end_time=end_time.time())
            
            admin_user = User.objects.filter(is_staff=True)

            for user in admin_user:
                Notification.objects.create(
                    appointment=appointment,
                    user=user,
                    patient=patient,
                    message=f"New appointment request from {request.user.username}"
                )
                
                # Send a real-time notification via channels
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f"user_{user.id}",  # Adjust according to your admin's ID
                    {
                        "type": "send_notification",
                        "message": f"{patient.first_name} {patient.last_name}",
                        "patient_image_url": patient.image.url,
                        "timestamp": timezone.now().isoformat(),
                    }
                )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request):
        try:
            appointment = Appointment.objects.get(user_account=request.data.id)
        except Appointment.DoesNotExist:
            return Response({"detail": "Appointment not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = AppointmentSerializer(appointment, data=request.data, context={'request': request}, partial=True)
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@login_required
def unread_notif(request):
    if request.method == 'GET':
        notifs = Notification.objects.filter(appointment__status='Pending')
        notif_data = []
        for notif in notifs:
            notif_data.append({
                'id': notif.pk,
                'appointment_id': notif.appointment.id,
                'patient': f'{notif.patient.first_name} {notif.patient.last_name}',
                'patient_image_url': notif.patient.image.url,
                'timestamp': notif.timestamp.isoformat(),
                'appointment_date': notif.appointment.appointment_date.isoformat(),
                'start_time': notif.appointment.start_time.isoformat(),
                'end_time': notif.appointment.end_time.isoformat(),
                'status': notif.appointment.status,
            })
        return JsonResponse(notif_data, safe=False)

# Create your views here.
@login_required
def index(request):
    # resident = Resident.objects.exclude(house_no__isnull=True)
    patient= Patient.objects.all().order_by("first_name")
    # user_patient = Patient.objects.get(user_account=request.user)
    # members = resident.values('house_no').annotate(total_count=Count('id')).order_by('house_no')
    context = {
        'patient': patient,
        # 'user_patient': user_patient,
    }
    return render(request, 'index.html', context)

def logout_view(request):
    logout(request)
    return redirect('login')

def signIn(request):

    return render(request, 'sign-in.html')

def signUp(request):
    if request.method == 'POST':
        signup_form = SignupForm(request.POST)
        patient_form = PatientForm(request.POST, request.FILES)
        if signup_form.is_valid() and patient_form.is_valid():

            # Proceed with sending the confirmation code and saving the data in the session
            request.session['signup_data'] = request.POST  # Store the signup form data
            request.session['patient_data'] = request.POST  # Store the patient form data

            # Generate confirmation code
            confirmation_code = random.randint(100000, 999999) 
            request.session['confirmation_code'] = confirmation_code

            user_email = patient_form.cleaned_data['email']
            send_mail(
                'Your Confirmation Code',
                f'Your confirmation code is: {confirmation_code}',
                settings.DEFAULT_FROM_EMAIL,
                [user_email],
                fail_silently=False,
            )

            # return JsonResponse({'success': 'success'})
            return redirect('confirm_signup')
    else:
        signup_form = SignupForm()
        patient_form = PatientForm()
        # return JsonResponse({'success': 'fail'})
    
    context = {
        'signup_form': signup_form,
        'patient_form': patient_form,
    }
    return render(request, 'sign-up.html', context)

def user_Signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST, instance=None)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = True
            user.save()
            return redirect('confirm_signup')
    else:
        form = SignupForm()

    context = {'form': form}
    
    return render(request, 'User.html', context)

def confirm_signup(request):
    if request.method == 'POST':
        entered_code = request.POST.get('confirmation_code')
        stored_code = request.session.get('confirmation_code')
        
        if entered_code == str(stored_code):
            signup_form = SignupForm(request.session['signup_data'])
            patient_form = PatientForm(request.session['patient_data'])
            
            user = signup_form.save()
            saveForm = patient_form.save(commit=False)
            saveForm.user_account = user
            saveForm.save()

            # Clear session data after saving
            request.session.pop('confirmation_code', None)
            request.session.pop('signup_data', None)
            request.session.pop('patient_data', None)

            return redirect('login')
        else:
            # Handle invalid confirmation code
            return render(request, 'confirm_signup.html', {'error': 'Invalid confirmation code.'})
    
    return render(request, 'Confirmation.html')

@login_required
def dashboard(request):
    now = timezone.now()

    #treatment
    top_treatments = (
        Invoice_items.objects
        .select_related('treatment')  # Fetch related treatment details
        .values('treatment__name')  # Group by treatment name
        .annotate(total_price=Sum('price'))  # Sum the qty for each treatment
        .order_by('-total_price')[:3]  # Get the top 3 treatments
    )

    #Appointments
    upcoming_appointments = Appointment.objects.filter(
        appointment_date__gt=now.date()
    ).order_by('appointment_date', 'start_time')

    #patients
    patients = Patient.objects.all()
    top6_patient = patients[:6]
    additional_patients = patients.count() - 6

    #payments
    payments = Payment.objects.all().aggregate(total_payments=Sum('payment'))

    context = {
        'top_treatments': top_treatments,
        'top6_patient': top6_patient,
        'patients': patients,
        'additional_patients': additional_patients,
        'upcoming_appointments': upcoming_appointments,
        'payments': payments,
    }
    return render(request, 'ecommerce.html', context)

@login_required
def getchartData(request):
    payments = Payment.objects.all()
    labels = []
    data = []
    for payment in payments:
        labels.append(payment.payment_date.strftime('%Y-%m-%d'))
        data.append(payment.payment)

    context = {
        'labels': labels,
        'data': data,
    }

    return JsonResponse(context)

@login_required
def Add(request, instance=None, form_class=None, template=None, redirect_to=None, additional_context=None):
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            return redirect(redirect_to)
    else:
        form = form_class(instance=instance)

    context = {'form': form}
    
    # Add additional context if provided
    if additional_context:
        context.update(additional_context)

    return render(request, template, context)

def Save(request, instance=None, form_class=None, additional_context=None):
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=instance)
        if form.is_valid():
            form.save()
            # return redirect(redirect_to)
    else:
        form = form_class(instance=instance)

    context = {'form': form}
        
        # Add additional context if provided
    if additional_context:
        context.update(additional_context)

@login_required
def getForm(request, form_class=None, instance=None):
    if request.method == 'POST':
        form = form_class(request.POST, request.FILES, instance=instance)
    else:
        form = form_class(instance=instance)
    return form

@login_required
def delete(request, pk, obj):
    if request.method == 'POST':
        try:
            # Ensure obj_class is a model class, not an instance or string
            instance = get_object_or_404(obj, pk=pk)
            instance.delete()
            return JsonResponse({'success': True})
        except obj.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Record not found'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    else:
        return JsonResponse({'success': False, 'error': 'Invalid request'})

@login_required
def dentists(request):  
    dentist = Dentist.objects.all()
    id = request.POST.get('id')
    if id:
        inst = get_object_or_404(Dentist, pk=id)
    else:
        inst = None
    additional_context = {'dentist': dentist}
    return Add(
        request,
        instance=inst,
        form_class=DentistForm, 
        template='dentist.html',
        redirect_to=request.path_info,
        additional_context=additional_context
    )

@login_required
def patients(request): 
    patient= Patient.objects.all() 
    additional_context = {'patient': patient}
    return Add(
        request,
        instance=None,
        form_class=PatientForm, 
        template='Patientlist.html',
        redirect_to='patients_list',
        additional_context=additional_context
    )

@login_required
def Patient_info(request, pk):
    formid = request.POST.get('formid')
    formid1 = request.POST.get('formid1')
    medHis_id = request.POST.get('id')

    patient_inst = get_object_or_404(Patient, pk=pk)
    patient_form = getForm(request, form_class=PatientForm, instance=patient_inst)
    
    medhis_inst = get_object_or_404(MedicalHistory, pk=medHis_id) if medHis_id else None
    medHis_form = getForm(request, form_class=MedicalHistoryForm, instance=medhis_inst)
    medHis_list = MedicalHistory.objects.filter(patient=patient_inst)

    invoices = Invoice.objects.filter(patient=patient_inst)

    appointments = Appointment.objects.filter(patient=patient_inst).order_by("-appointment_date")
    
    if request.method == 'POST':
        if formid == "PatientForm":
            if patient_form.is_valid():
                patient_form.save()
                return redirect(request.path_info)
            else:
                print(patient_form.errors) 

        if formid1 == "MedicalHistoryForm":
            if medHis_form.is_valid():
                medHis_form.save()
                return redirect(request.path_info)
            else:
                print(medHis_form.errors) 

    context = {'patient_form': patient_form, 
               'patient_inst': patient_inst, 
               'medHis_form': medHis_form, 
               'medHis_list': medHis_list,
               'invoices': invoices,
               'appointments': appointments,
               }
    
    return render(request, 'Patientdetails.html', context)

@login_required
def ClinicInfo(request):
    info = Clinic_Info.objects.all()

    if info.count() > 0:
        current_Info = info.first()
    else:
        current_Info = None

    form = ClinicForm(request.POST, request.FILES, instance=current_Info)
    if request.method == 'POST':
        if form.is_valid:
            form.save()
            return redirect(request.path_info)
    else:
        form = ClinicForm(instance=current_Info)

    context = {
        'form': form,
        'current_Info': current_Info
    }
    
    return render(request, 'ClinicInfo.html', context)

@login_required
def Delete_patient(request, pk):
    return delete(request, pk, Patient)

@login_required
def Delete_treatment(request, pk):
    return delete(request, pk, Treatment)

@login_required
def Delete_dentist(request, pk):
    return delete(request, pk, Dentist)

@login_required
def Delete_medHis(request, pk):
    return delete(request, pk, MedicalHistory)

@login_required
def Delete_invoice(request, pk):
    return delete(request, pk, Invoice)

@login_required
def Delete_payment(request, pk):
    return delete(request, pk, Payment)

@login_required
def calendar(request):
    appointment = Appointment.objects.all()
    id = request.POST.get('id')
    if id:
        inst = get_object_or_404(Appointment, pk=id)
    else:
        inst = None

    if request.method == 'POST':
        form = AppointmentForm(request.POST, request.FILES, instance=inst)
        if form.is_valid():
            a = form.save(commit=False)
            # a.status = 'Approved'
            a.save()
            form.save_m2m()
            
            # Calculate the end time after treatments are saved
            total_duration = sum([treatment.duration for treatment in a.treatment.all()])
            start_datetime = datetime.combine(a.appointment_date, a.start_time)
            end_datetime = start_datetime + timedelta(minutes=total_duration)
            a.end_time = end_datetime.time()
            a.save()

            return redirect(request.path_info)
    else:
        form = AppointmentForm(instance=inst)

    context = {
        'form': form,
        'appointment': appointment
    }

    return render(request, 'Calendar.html', context)

@login_required
def appointments(request):  
    appointment = Appointment.objects.all()
    id = request.POST.get('id')
    if id:
        inst = get_object_or_404(Appointment, pk=id)
    else:
        inst = None

    if request.method == 'POST':
        form = AppointmentForm(request.POST, request.FILES, instance=inst)
        if form.is_valid():
            a = form.save(commit=False)
            # a.status = 'Approved'
            a.save()
            form.save_m2m()
            
            # Calculate the end time after treatments are saved
            total_duration = sum([treatment.duration for treatment in a.treatment.all()])
            start_datetime = datetime.combine(a.appointment_date, a.start_time)
            end_datetime = start_datetime + timedelta(minutes=total_duration)
            a.end_time = end_datetime.time()
            a.save()

            notification_id = 1
            Notification.objects.filter(id=notification_id).update(is_read=True)

            return redirect(request.path_info)
    else:
        form = AppointmentForm(instance=inst)

    context = {
        'form': form,
        'appointment': appointment
    }

    return render(request, 'Appointments.html', context)

@login_required
def treatments(request):  
    treatment = Treatment.objects.all()
    id = request.POST.get('id')
    if id:
        inst = get_object_or_404(Treatment, pk=id)
    else:
        inst = None
    additional_context = {'treatment': treatment}
    return Add(
        request,
        instance=inst,
        form_class=TreatmentForm, 
        template='Treatmentlist.html',
        redirect_to=request.path_info,
        additional_context=additional_context
    )

@login_required
def invoices(request):  
    invoices = Invoice.objects.prefetch_related('items').all().order_by("-invoice_date")

    context = {
        'invoices': invoices,
    }
    return render(request, 'InvoiceList.html', context)

@login_required
def getpayForm(request):
    id = request.GET.get('id', None)  # Get the payment ID from the AJAX request
    if id:
        payment = get_object_or_404(Payment, pk=id)  # Fetch the payment if ID exists
        form_html = PaymentForm(instance=payment)
    else:
        form_html = PaymentForm()  # If no ID, provide an empty form for new entry

    # Render the form as HTML
    form = form_html.as_p()  # Or form.as_table() depending on your form rendering

    return JsonResponse({'form': form})

@login_required
def getDentistForm(request):
    id = request.GET.get('id', None)  # Get the payment ID from the AJAX request
    if id:
        dentist = get_object_or_404(Dentist, pk=id)  # Fetch the payment if ID exists
        form_html = DentistForm(instance=dentist)
    else:
        form_html = DentistForm()  # If no ID, provide an empty form for new entry

    # Render the form as HTML
    form = form_html.as_p()  # Or form.as_table() depending on your form rendering

    return JsonResponse({'form': form})

@login_required
def getmedhisForm(request):
    id = request.GET.get('id', None)  # Get the payment ID from the AJAX request
    if id:
        medHis = get_object_or_404(MedicalHistory, pk=id)  # Fetch the payment if ID exists
        form_html = MedicalHistoryForm(instance=medHis)
    else:
        form_html = MedicalHistoryForm()  # If no ID, provide an empty form for new entry

    # Render the form as HTML
    form = form_html.as_p()  # Or form.as_table() depending on your form rendering

    return JsonResponse({'form': form})

@login_required
def getAppointmentForm(request):
    id = request.GET.get('id', None)  # Get the payment ID from the AJAX request
    if id:
        appointment = get_object_or_404(Appointment, pk=id)  # Fetch the payment if ID exists
        form_html = AppointmentForm(instance=appointment)
    else:
        form_html = AppointmentForm()  # If no ID, provide an empty form for new entry

    # Render the form as HTML
    form = form_html.as_p()  # Or form.as_table() depending on your form rendering

    return JsonResponse({'form': form})

@login_required
def getTreatmentForm(request):
    id = request.GET.get('id', None)  # Get the payment ID from the AJAX request
    if id:
        treatment = get_object_or_404(Treatment, pk=id)  # Fetch the payment if ID exists
        form_html = TreatmentForm(instance=treatment)
    else:
        form_html = TreatmentForm()  # If no ID, provide an empty form for new entry

    # Render the form as HTML
    form = form_html.as_p()  # Or form.as_table() depending on your form rendering

    return JsonResponse({'form': form})

@login_required
def payments(request):
    payment_list = Payment.objects.all()
    id = request.POST.get('id', None)
    if id:
        inst = get_object_or_404(Payment, pk=id)
    else:
        inst = None
    additional_context = {'payment_list': payment_list}
    return Add(
        request,
        instance=inst,
        form_class=PaymentForm, 
        template='PaymentList.html',
        redirect_to=request.path_info,
        additional_context=additional_context
    )

@login_required
def printInvoice(request, pk):  
    invoices = Invoice.objects.get(pk=pk)
    items = invoices.items.all()
    totals = [{'item': item, 'total': item.qty * item.price} for item in items]
    context = {
        'invoices': invoices,
        'items': totals,
    }
    return render(request, 'PrintInvoice.html', context)

@login_required
def create_invoice(request, invoice_id=None):
    if invoice_id:
        # Editing an existing invoice
        invoice = get_object_or_404(Invoice, pk=invoice_id)
        InvoiceItemFormSet = modelformset_factory(Invoice_items, form=Invoice_itemsForm, extra=0, can_delete=True)

        if request.method == 'POST':
            invoice_form = InvoiceForm(request.POST, instance=invoice)
            invoice_items_formset = InvoiceItemFormSet(request.POST, queryset=Invoice_items.objects.filter(invoice=invoice))

            if invoice_form.is_valid() and invoice_items_formset.is_valid():
                # Save the invoice
                invoice = invoice_form.save()
                for index, form in enumerate(invoice_items_formset.forms):
                    if 'DELETE' in form.cleaned_data:
                        print(f"Marked for Deletion: {form.cleaned_data['DELETE']}")

                # Handle deletions
                for form in invoice_items_formset.deleted_forms:
                    if form.instance.pk:  # Ensure the instance has a primary key
                        form.instance.delete()

                # Handle new and modified items
                for form in invoice_items_formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        item = form.save(commit=False)
                        item.invoice = invoice
                        item.save()

                return redirect('Invoice_list')
            else:
                print("Invoice Form Errors:", invoice_form.errors)
                print("Invoice Items Formset Errors:", invoice_items_formset.errors)
        else:
            invoice_form = InvoiceForm(instance=invoice)
            invoice_items_formset = InvoiceItemFormSet(queryset=Invoice_items.objects.filter(invoice=invoice))
    else:
        InvoiceItemFormSet = modelformset_factory(Invoice_items, form=Invoice_itemsForm, extra=1, can_delete=True)

        if request.method == 'POST':
            invoice_form = InvoiceForm(request.POST)
            invoice_items_formset = InvoiceItemFormSet(request.POST)

            if invoice_form.is_valid() and invoice_items_formset.is_valid():
                # Save the invoice first
                invoice = invoice_form.save()

                # Handle new items
                for form in invoice_items_formset:
                    if form.cleaned_data and not form.cleaned_data.get('DELETE', False):
                        item = form.save(commit=False)
                        item.invoice = invoice
                        item.save()

                return redirect('Invoice_list')
            else:
                print("Invoice Form Errors:", invoice_form.errors)
                print("Invoice Items Formset Errors:", invoice_items_formset.errors)
        else:
            invoice_form = InvoiceForm()
            invoice_items_formset = InvoiceItemFormSet(queryset=Invoice_items.objects.none())

    context = {
        'invoice_form': invoice_form,
        'invoice_items_formset': invoice_items_formset,
    }
    return render(request, 'create_invoice.html', context)

@login_required
def getPrice(request, treatment_id):
    if request.method == 'GET':
        treatment = get_object_or_404(Treatment, pk=treatment_id)
        price = treatment.cost
        # print(price)
        return JsonResponse({'price': price}, safe=False)

@login_required
def events_list(request):
    if request.method == 'GET':
        events = Event.objects.all().values('id', 'title', 'start', 'end', 'description', 'location', 'all_day')
        return JsonResponse(list(events), safe=False)

# Create event
@csrf_exempt
def create_event(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        event = Event.objects.create(**data)
        return JsonResponse({'id': event.id}, status=201)

# Update event
@csrf_exempt
def update_event(request, event_id):
    if request.method == 'PUT':
        data = json.loads(request.body)
        Event.objects.filter(id=event_id).update(**data)
        return HttpResponse(status=204)

# Delete event
@csrf_exempt
def delete_event(request, event_id):
    if request.method == 'DELETE':
        Event.objects.filter(id=event_id).delete()
        return HttpResponse(status=204)
    
@login_required
def appointment_list(request):
    if request.method == 'GET':
        appointments = Appointment.objects.all()
        events = []
        for appointment in appointments:
            treatments = [treatment.name for treatment in appointment.treatment.all()]
            events.append({
                'id': f'{appointment.pk}',
                'patientid': f'{appointment.patient.id}',
                'title': f'Appointment with {appointment.patient.first_name} {appointment.patient.last_name} (status: {appointment.status})',
                "description": f'{appointment.notes}',
                'start': f'{appointment.appointment_date}T{appointment.start_time}', 
                'end': f'{appointment.appointment_date}T{appointment.end_time}', 
                'treatments': treatments  # Add the treatments as a list
            })
        print(events)
        return JsonResponse(events, safe=False)

@login_required
@csrf_exempt
def create_appointment(request):
    if request.method == 'POST':
        try:
            
            # Attempt to load JSON data
            data = json.loads(request.body)

            # Fetch the patient based on the provided ID
            patient = Patient.objects.get(id=data['patient'])

            appointment_id = data['id']

            if appointment_id:
                # Update existing appointment
                appointment = get_object_or_404(Appointment, id=appointment_id)
                appointment.patient = patient
                appointment.appointment_date = data['appointment_date']
                appointment.start_time = data['start_time']
                appointment.notes = data['notes']
                appointment.save()
            else:
                # # Create a new appointment
                appointment = Appointment.objects.create(
                    patient=patient,
                    appointment_date=data['appointment_date'],
                    start_time=data['start_time'],
                    notes=data['notes']
                )

            # Prepare the response data
            patient_name = f"Appointment with {patient.first_name} {patient.last_name}"
            response_data = {
                'id': appointment.id,
                'patient_name': patient_name,
            }

            # Return a success response
            return JsonResponse(response_data, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)
        
        except Patient.DoesNotExist:
            return JsonResponse({'error': 'Patient not found'}, status=404)
        
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    
    # If the request method is not POST
    return JsonResponse({'error': 'Invalid request method'}, status=400)

@login_required
@csrf_exempt
def delete_appointment(request, appointment_id):
    if request.method == 'POST':
        Appointment.objects.filter(id=appointment_id).delete()
        return HttpResponse(status=204)
