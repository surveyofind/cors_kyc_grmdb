from django.shortcuts import render, redirect
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login,logout
from.models import *
from django.contrib import messages
# from django.contrib.auth.models import User
from cors_app.models import User
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from pytz import timezone as pytz_timezone
from django.urls import reverse
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.http import HttpResponse
import base64
import csv
import datetime
from django.db.models import Q
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import check_password, make_password

def login_views(request):
    gd_users = User.objects.filter(gdc=True)
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = None
        error_message = 'Invalid username, password, or user type'

        if user_type == 'control_centre':
            user = authenticate(request, username=username, password=password)
            if user and user.controlcentre:
                if user.is_approved:
                    login(request, user)
                    request.session['user_id'] = user.id  # Save user ID in session
                    return redirect(reverse('control_centre_dashboard'))
                else:
                    error_message = 'Your account is awaiting approval.'
            else:
                error_message = 'Invalid username, password, or user type'
        elif user_type == 'vendor':
            user = authenticate(request, username=username, password=password)
            if user and user.vendor:
                if user.is_approved:
                    login(request, user)
                    request.session['user_id'] = user.id  # Save user ID in session
                    return redirect(reverse('vender_dashboard'))
                else:
                    error_message = 'Your account is awaiting approval.'
            else:
                error_message = 'Invalid username, password, or user type'
        elif user_type == 'gdc':
            user = authenticate(request, username=username, password=password)
            if user and user.gdc:
                if user.is_approved:
                    login(request, user)
                    request.session['user_id'] = user.id  # Save user ID in session
                    return redirect(reverse('gdc_dashboard'))
                else:
                    error_message = 'Your account is awaiting approval.'
            else:
                error_message = 'Invalid username, password, or user type'
        return render(request, 'login.html', {'error': error_message,'gd_users': gd_users})

    
    return render(request, 'login.html', {'gd_users': gd_users})

def signup(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        mobile_no = request.POST.get('mobile_no')
        User = get_user_model()

        if User.objects.filter(username=username).exists():
            error_message = 'This username already exists'
            return render(request, 'signup.html', {'error': error_message})

        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
            mobileno=mobile_no,
            is_approved=False  # Set the user as unapproved
        )

        if user_type == 'control_centre':
            user.controlcentre = True
        elif user_type == 'vendor':
            user.vendor = True
        elif user_type == 'gdc':
            user.gdc = True

        user.save()
        return redirect('login')

    return render(request, 'signup.html')


@user_passes_test(lambda u: u.is_superuser)  # Ensure only superusers can access this view
def approve_users(request):
    User = get_user_model()
    users = User.objects.all()

    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        user = User.objects.get(id=user_id)
        user.is_approved = not user.is_approved  # Toggle the approved status
        user.save()
        return redirect('approve_users')

    return render(request, 'approve_users.html', {'users': users})


def logout_view(request):
    logout(request)
    return redirect('/')



def forgot_password(request):
    gd_users = User.objects.filter(Q(gdc=True) | Q(vendor=True))
    if request.method == 'POST':
        username = request.POST.get('username')
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')

        try:
            user = User.objects.get(username=username)
            if check_password(current_password, user.password):
                user.set_password(new_password)
                user.save()
                return render(request, 'forgot_password.html', {'success': 'Password has been changed successfully','gd_users':gd_users})
            else:
                return render(request, 'forgot_password.html', {'error': 'Incorrect current password' ,'gd_users':gd_users})
        except User.DoesNotExist:
            return render(request, 'forgot_password.html', {'error': 'Username not found','gd_users':gd_users})
    return render(request, 'forgot_password.html',{'gd_users':gd_users})

@login_required(login_url='/')
def vender_dashboard(request):
    query = request.POST.get('searchdata', '')
    request.session['query'] = query
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    username = user.username
    user_data = CorsAppCentreData.objects.filter(vendor_username=username).values_list('corsid', flat=True)
    vendor_data = CorsAppVendorData.objects.filter(corsid__in=user_data)
    if query:
        vendor_data = vendor_data.filter(Q(corsid__icontains=query)|Q(site_name__icontains=query)|Q(state_name__icontains=query))
        
    return render(request, 'vendor.html', {'vendor_data': vendor_data})


@login_required(login_url='/')
def vendardownload_csv(request):
    query = request.session.get('query')
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    username = user.username
    user_data = CorsAppCentreData.objects.filter(vendor_username=username).values_list('corsid', flat=True)
    vendor_data = CorsAppVendorData.objects.filter(corsid__in=user_data)
    if query:
        vendor_data = vendor_data.filter(Q(corsid__icontains=query)|Q(site_name__icontains=query)|Q(state_name__icontains=query))
        

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="vendor_data.csv"'

    writer = csv.writer(response)
 
    writer.writerow([
        'CORS ID', 'Site Name', 'State', 'Date of Monumentation', 'Date of Installation', 'Station Status', 
        'Antenna Type and Serial No.', 'Date of Installation of Antenna', 'Offset Parameter of Antenna', 
        'Height of Bottom of Antenna from Base of Pillar (cm)', 'Height of Bottom of Antenna from Top of Base Plate (cm)', 
        'Height of Bottom of Antenna from Solar Panel Lower Angle Bottom (cm)', 'Dimension of Pillar (H*W*B) in cm', 
        'Dimension of Pedestal (H*W*B) in cm', 'GNSS Data Logging Interval is 1 second', 'GNSS Data Frequencies', 
        'Electricity Provider Name & Connection No', 'Two No. of Solar Panels (60 W)', 'Serial No. of Solar Panel 1 and 2', 
        '2 No. of Batteries (12V) (DC)', 'Company Name and Serial No. of Batteries', 'Company Name of SIM1 & Mobile No.', 
        'Company Name of SIM2 & Mobile No.', 'Company Name and Serial No. of Broadband', 'Broadband Plan Validity', 
        'Receiver Model name and Serial No.', 'Date of Installation of Receiver and Firmware', 
        'Date of Installation of Radome and Serial No', 'Serial No. of Meteorological Sensor if any', 
        'Date of Installation of Meteorological Sensor', 'Meteorological Sensor Type and Firmware', 
        'Last Date of Site Visit', 'Operation & Maintenance Remark', 'Image East', 'Image West', 'Image North', 
        'Image South'
    ])


    for data in vendor_data:
        writer.writerow([
            data.corsid, data.site_name, data.state_name, data.date_of_monumentation, data.date_of_installation, 
            data.station_status, data.antenna_type_and_serial_no, data.date_of_installation_of_antenna, 
            data.offset_parameter_of_antenna.url if data.offset_parameter_of_antenna else 'No File Available', 
            data.height_of_bottom_of_antenna_from_base_of_pillar, data.height_of_bottom_of_antenna_from_top_of_base_plate, 
            data.height_of_bottom_of_antenna_from_solar_panel_lower_angle_bottom, data.dimension_of_pillar, 
            data.dimension_of_pedestal, data.logging_interval_of_gnss_data, data.gnss_data_frequencies, 
            data.electricity_provider, data.twonumber_of_solar_panels, data.serial_no_of_solar_panels1and2, 
            data.batteries_12v_2, data.company_name_and_no_of_batteries, data.company_name_of_sim1, 
            data.company_name_of_sim2, 
            data.company_name_and_no_of_broadband, data.broadband_plan_validity, data.receiver_model_name_and_serial_no, 
            data.date_of_installation_of_receiver_and_firmware, data.date_of_installation_of_radome_and_serial_no, 
            data.serial_no_of_meteorological_sensor, data.date_of_installation_of_meteorological_sensor, 
            data.meteorological_sensor_type_and_firmware, data.last_date_of_site_visit, 
            data.operationmaintainanceremark, data.image_east.url if data.image_east else 'No Image Available', 
            data.image_west.url if data.image_west else 'No Image Available', 
            data.image_north.url if data.image_north else 'No Image Available', 
            data.image_south.url if data.image_south else 'No Image Available'
        ])

    return response
  
   



@login_required(login_url='/')
def controlcentreform(request):
    # Retrieve the first Controlcentre object
    username_vendor = User.objects.filter(vendor=1)
    username_gdc = User.objects.filter(gdc=1)
    controlcentre_data = CorsAppCentreData.objects.order_by('id').first()  
    if request.method == 'POST':
        current_id = controlcentre_data.id 
        controlcentre_data.coordinates_of_sites_dms_lat = request.POST.get('coordinates_of_sites_dms_lat')
        controlcentre_data.coordinates_of_sites_dms_long = request.POST.get('coordinates_of_sites_dms_long')
        controlcentre_data.coordinates_of_sites_dms_elp_height = request.POST.get('coordinates_of_sites_dms_elp_height')
        controlcentre_data.digi_wr21_ip_dns_gateway_of_alloy_field = request.POST.get('digi_wr21_ip_dns_gateway_of_alloy_field')
        controlcentre_data.digi_username_password = request.POST.get('digi_username_password')
        controlcentre_data.alloy_cc_network_ip = request.POST.get('alloy_cc_network_ip')
        controlcentre_data.alloy_netmask = request.POST.get('alloy_netmask')
        controlcentre_data.alloy_local_wifi_ip = request.POST.get('alloy_local_wifi_ip')
        controlcentre_data.alloy_username_and_password = request.POST.get('alloy_username_and_password')
        controlcentre_data.vendor_username = request.POST.get('vendor_username')
        controlcentre_data.gdc_username = request.POST.get('gdc_username')
        controlcentre_data.save()
        next_controlcentre_data = CorsAppCentreData.objects.filter(id__gt=current_id).order_by('id').first() 
        if next_controlcentre_data:
            controlcentre_data = next_controlcentre_data
    return render(request, 'controlcentreform.html', {'username_vendor': username_vendor,
                                                      'username_gdc': username_gdc,
                                                      'controlcentre_data': controlcentre_data})






@login_required(login_url='/')
def control_centre_dashboard(request):
    query = request.POST.get('searchdata', '')
    request.session['query'] = query
    if query:
        data = CorsAppCentreData.objects.filter(
            Q(state__icontains=query)|
            Q(corsid__icontains=query) |
            Q(site_name__icontains=query) |
            Q(site_code__icontains=query) |
            Q(vendor_username__icontains=query) |
            Q(gdc_username__icontains=query) 
            
        )
        
    else:
        data = CorsAppCentreData.objects.all()
    context = {
        'data':data,
    }
    return render(request,'control_centre.html',context)


def control_centre_dashboard_csv(request):
    query = request.session.get('query')
    
    if query:
        data = CorsAppCentreData.objects.filter(
            Q(state__icontains=query) |
            Q(corsid__icontains=query) |
            Q(site_name__icontains=query) |
            Q(site_code__icontains=query) |
            Q(vendor_username__icontains=query) |
            Q(gdc_username__icontains=query)
        )
    else:
        data = CorsAppCentreData.objects.all()

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="cors_data.csv"'

    writer = csv.writer(response)
    writer.writerow(['CorsID', 'State', 'Site Name', 'Site Code', 'Latitude of Site (DMS)', 'Longitude of Site (DMS)', 'Ellipsoid Height (m)', 'Vendor Username', 'GDC Username'])

    for item in data:
        
        writer.writerow([item.corsid, item.state, item.site_name, item.site_code, item.coordinates_of_sites_dms_lat, item.coordinates_of_sites_dms_long, item.coordinates_of_sites_dms_elp_height, item.vendor_username, item.gdc_username])

    return response


@login_required(login_url='/')
def edit_controlcentre(request, corsid):
    date = datetime.datetime.now()
    username_vendor = User.objects.filter(vendor=1)
    username_gdc = User.objects.filter(gdc=1)
    controlcentre = CorsAppCentreData.objects.get(corsid=corsid)
    if request.method == 'POST':
        controlcentre.coordinates_of_sites_dms_lat = request.POST.get('coordinates_of_sites_dms_lat')
        controlcentre.coordinates_of_sites_dms_long = request.POST.get('coordinates_of_sites_dms_long')
        controlcentre.coordinates_of_sites_dms_elp_height = request.POST.get('coordinates_of_sites_dms_elp_height')
        controlcentre.vendor_username = request.POST.get('vendor_username')
        controlcentre.gdc_username = request.POST.get('gdc_username')
        controlcentre.updatetime=date
        controlcentre.save()
        messages.success(request, 'Successfully updated your data')
        return redirect('control_centre_dashboard')
    return render(request, 'edit_controlcentre.html', {'controlcentre': controlcentre, 'username_vendor': username_vendor, 'username_gdc': username_gdc})



@login_required(login_url='/')
def gdc_dashboard(request):
    query = request.POST.get('searchdata','')
    request.session['query'] = query
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    username = user.username
    user_data = CorsAppCentreData.objects.filter(gdc_username=username).values_list('corsid', flat=True)
    gdc_data = CorsAppGdcData.objects.filter(corsid__in=user_data)
    if query:
        gdc_data = gdc_data.filter(Q(corsid__icontains=query)|Q(site_name__icontains=query)|Q(state_name__icontains=query))
        
    return render(request, 'gdc.html', {'gdc_data': gdc_data})



def gdcdownload_csv(request):
    query = request.session.get('query')
    user_id = request.session.get('user_id')
    user = User.objects.get(id=user_id)
    username = user.username
    user_data = CorsAppCentreData.objects.filter(gdc_username=username).values_list('corsid', flat=True)
    gdc_data = CorsAppGdcData.objects.filter(corsid__in=user_data)
    
    if query:
        gdc_data = gdc_data.filter(Q(corsid__icontains=query)|Q(site_name__icontains=query)|Q(state_name__icontains=query))
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="gdc_data.csv"'
    writer = csv.writer(response)
    writer.writerow(['CORS ID', 'State Name', 'Site Name', 'District Name','Tahsil Name','PIN Code','Authorised Person name & Designation','Authorised Person Contact No.','Last Date of Visit','Inspection Remark','Image East Uploaded By The Field Team','Image West Uploaded By The Field Team','Image North Uploaded By The Field Team','Image South Uploaded By The Field Team'])
    for data in gdc_data:
        writer.writerow([data.corsid, data.state_name, data.site_name, data.dist_name,data.tahsil_name,data.pin_code,data.person_of_gdc,data.contact_no_of_gdc,data.last_date_of_gdc_visit,data.remark,
                        data.image_east.url if data.image_east else 'No Image Available', 
                        data.image_west.url if data.image_west else 'No Image Available', 
                        data.image_north.url if data.image_north else 'No Image Available', 
                        data.image_south.url if data.image_south else 'No Image Available'
                    ])
    return response    

@login_required(login_url='/')
def edit_gdc_data(request,corsid):
    date = datetime.datetime.now()
    gdc_data = get_object_or_404(CorsAppGdcData, corsid=corsid)
    if request.method =='POST':
        gdc_data.dist_name = request.POST.get('dist_name')
        gdc_data.tahsil_name = request.POST.get('tahsil_name')
        gdc_data.pin_code = request.POST.get('pin_code')
        gdc_data.gdc_name = request.POST.get('gdc_name')
        gdc_data.person_of_gdc = request.POST.get('person_of_gdc')
        gdc_data.contact_no_of_gdc = request.POST.get('contact_no_of_gdc')
        gdc_data.last_date_of_gdc_visit = request.POST.get('last_date_of_gdc_visit')
        gdc_data.remark = request.POST.get('remark')
        gdc_data.updatetime = date
        if request.FILES.get('image_east'):
            image_east = request.FILES['image_east']
            new_filename = rename_image(image_east.name, gdc_data.corsid, date, 'east')
            gdc_data.image_east.save(new_filename, image_east, save=False)
        if request.FILES.get('image_west'):
            image_west = request.FILES['image_west']
            new_filename = rename_image(image_west.name, gdc_data.corsid, date, 'west')
            gdc_data.image_west.save(new_filename, image_west, save=False)
        if request.FILES.get('image_north'):
            image_north = request.FILES['image_north']
            new_filename = rename_image(image_north.name, gdc_data.corsid, date, 'north')
            gdc_data.image_north.save(new_filename, image_north, save=False)
        if request.FILES.get('image_south'):
            image_south = request.FILES['image_south']
            new_filename = rename_image(image_south.name, gdc_data.corsid, date, 'south')
            gdc_data.image_south.save(new_filename, image_south, save=False)
        gdc_data.save()
        messages.success(request, 'Successfully updated your data')
        return redirect('gdc_dashboard')
    return render(request,'edit_gdc_data.html',{'gdc_data':gdc_data})


# def vendor_data(request):
#     all_data = Vendor.objects.all()
#     context = {
#         'all_data':all_data
#     }
#     return render(request,'vendor_data.html',context)



def rename_image(original_filename, corsid, date, direction):
    base_filename = f"{corsid}_{date.strftime('%Y-%m-%d')}_{direction}"
    extension = os.path.splitext(original_filename)[1]
    return f"{base_filename}{extension}"

def edit_vendor_data(request, corsid):
    date = datetime.datetime.now()
    vendor = get_object_or_404(CorsAppVendorData, corsid=corsid)
    original_corsid = vendor.corsid

    if request.method == 'POST':
        vendor.corsid = original_corsid
        vendor.last_date_of_site_visit = request.POST.get('last_date_of_site_visit')
        vendor.date_of_installation = request.POST.get('date_of_installation')
        vendor.date_of_monumentation = request.POST.get('date_of_monumentation')
        vendor.station_status = request.POST.get('status_of_station')
        vendor.dimension_of_pillar = request.POST.get('dimension_of_pillar')
        vendor.height_of_bottom_of_antenna_from_base_of_pillar = request.POST.get('height_of_bottom_of_antenna_from_base_of_pillar')
        vendor.height_of_bottom_of_antenna_from_top_of_base_plate = request.POST.get('height_of_bottom_of_antenna_from_top_of_base_plate')
        vendor.height_of_bottom_of_antenna_from_solar_panel_lower_angle_bottom = request.POST.get('height_of_bottom_of_antenna_from_solar_panel_lower_angle_bottom')
        vendor.dimension_of_pedestal = request.POST.get('dimension_of_pedestal')
        vendor.electricity_provider = request.POST.get('electricity_provider')
        vendor.electricity_meter_no = request.POST.get('electricity_meter_no')
        vendor.twonumber_of_solar_panels = request.POST.get('twonumber_of_solar_panels')
        vendor.capacity_of_solar_panel = request.POST.get('capacity_of_solar_panel')
        vendor.serial_no_of_solar_panels1and2 = request.POST.get('serial_no_of_solar_panels1and2')
        vendor.batteries_12v_2 = request.POST.get('batteries_12v_2')
        vendor.company_name_and_no_of_batteries = request.POST.get('company_name_and_no_of_batteries')
        vendor.company_name_of_sim1 = request.POST.get('company_name_of_sim1')
        vendor.sim1_plan_validity_and_sim1_no = request.POST.get('sim1_plan_validity_and_sim1_no')
        vendor.company_name_of_sim2 = request.POST.get('company_name_of_sim2')
        vendor.sim2_plan_validity_and_sim2_no = request.POST.get('sim2_plan_validity_and_sim2_no')
        vendor.company_name_and_no_of_broadband = request.POST.get('company_name_and_no_of_broadband')
        vendor.broadband_plan_validity = request.POST.get('broadband_plan_validity')
        vendor.antenna_type_and_serial_no = request.POST.get('antenna_type_and_serial_no')
        vendor.date_of_installation_of_antenna = request.POST.get('date_of_installation_of_antenna')
        vendor.receiver_model_name_and_serial_no = request.POST.get('receiver_model_name_and_serial_no')
        vendor.date_of_installation_of_receiver_and_firmware = request.POST.get('date_of_installation_of_receiver_and_firmware')
        vendor.date_of_installation_of_radome_and_serial_no = request.POST.get('date_of_installation_of_radome_and_serial_no')
        vendor.serial_no_of_meteorological_sensor = request.POST.get('serial_no_of_meteorological_sensor')
        vendor.date_of_installation_of_meteorological_sensor = request.POST.get('date_of_installation_of_meteorological_sensor')
        vendor.meteorological_sensor_type_and_firmware = request.POST.get('meteorological_sensor_type_and_firmware')
        gnss_data_frequencies = request.POST.getlist('gnss_data_frequencies')
        vendor.gnss_data_frequencies = ','.join(gnss_data_frequencies)
        vendor.vendor_time = date
        vendor.operationmaintainanceremark = request.POST.get('operationmaintainanceremark')

        # Handle image uploads and renaming
        if request.FILES.get('image_east'):
            image_east = request.FILES['image_east']
            new_filename = rename_image(image_east.name, vendor.corsid, date, 'east')
            vendor.image_east.save(new_filename, image_east, save=False)
        if request.FILES.get('image_west'):
            image_west = request.FILES['image_west']
            new_filename = rename_image(image_west.name, vendor.corsid, date, 'west')
            vendor.image_west.save(new_filename, image_west, save=False)
        if request.FILES.get('image_north'):
            image_north = request.FILES['image_north']
            new_filename = rename_image(image_north.name, vendor.corsid, date, 'north')
            vendor.image_north.save(new_filename, image_north, save=False)
        if request.FILES.get('image_south'):
            image_south = request.FILES['image_south']
            new_filename = rename_image(image_south.name, vendor.corsid, date, 'south')
            vendor.image_south.save(new_filename, image_south, save=False)

        # Handle additional form logic
        install_sensor = request.POST.get('serial_no_of_meteorological_sensor')
        additional_info = request.POST.get('additional_info')
        if 'serial_no_of_meteorological_sensor' in request.POST:
            if install_sensor == 'yes' and additional_info:
                vendor.serial_no_of_meteorological_sensor = additional_info
            elif install_sensor == 'None':
                vendor.serial_no_of_meteorological_sensor = 'Not Install'
        else:
            vendor.serial_no_of_meteorological_sensor = vendor.serial_no_of_meteorological_sensor

        install_logging = request.POST.get('logging_interval_of_gnss_data')
        additional_data = request.POST.get('additional_loginig')
        if 'logging_interval_of_gnss_data' in request.POST:
            if install_logging == 'logging' and additional_data:
                vendor.logging_interval_of_gnss_data = additional_data
            elif install_logging == 'YES':
                vendor.logging_interval_of_gnss_data = 'YES'
        else:
            vendor.logging_interval_of_gnss_data = vendor.logging_interval_of_gnss_data

        vendor.save()
        messages.success(request, 'Successfully updated your data')
        return redirect('/vender_dashboard')

    return render(request, 'edit_vendordata.html', {'vendor': vendor})



def corsadmin_login(request):
    username = request.POST.get('username')
    password = request.POST.get('password')
    user = authenticate(username=username,password=password)
    if user is not None:
        login(request,user)
        return redirect('corsadmin_dashboard')
    return render(request,'admin_login.html')



def corsadmin_dashboard(request):
    query = request.POST.get('searchdata','')
    request.session['query'] = query
    if query:
        data = CorsAppCentreData.objects.filter(Q(state__icontains=query)|Q(corsid__icontains=query) |Q(site_name__icontains=query) |Q(site_code__icontains=query) |Q(vendor_username__icontains=query) |Q(gdc_username__icontains=query))
    else:
        data = CorsAppCentreData.objects.all()    
    context = {
        'data':data
    }
    return render(request,'admin_dashboard.html',context)




def vandor_admindashboard(request):
    query = request.POST.get('searchdata','')
    data = CorsAppVendorData.objects.all()
    if query:
        data = data.filter(Q(corsid__icontains=query)|Q(site_name__icontains=query)|Q(state_name__icontains=query))
    context = {
        'data':data
    }
    return render(request,'vandor_admindashboard.html',context)


def gdc_admindashboard(request):
    query = request.POST.get('searchdata','')
    data = CorsAppGdcData.objects.all()
    if query:
        data = data.filter(Q(corsid__icontains=query)|Q(site_name__icontains=query)|Q(state_name__icontains=query))
        
    context = {
        'data':data
    }
    return render(request,'gdc_admindashboard.html',context)



def vendor_datalog(request):
    corsid = request.POST.get('corsid')
    request.session['corsid'] = corsid
    data  = CorsAppVendorDataBackup.objects.filter(corsid=corsid)
    
    context = {
        'datasss':data
    }
    return render(request,'vendordata_download.html',context)




def vendor_datatext_file(request):
    if request.method == 'GET':
        corsid = request.session.get('corsid')
        vendor_data = CorsAppVendorDataBackup.objects.filter(corsid=corsid)
        
        text_content = ""
        for i in vendor_data:
            text_content += f"CORS ID: {i.corsid}\n"
            text_content += f"Site Name: {i.site_name}\n"
            text_content += f"State: {i.state_name}\n"
            text_content += f"Date of Monumentation: {i.date_of_monumentation}\n"
            text_content += f"Date of Installation: {i.date_of_installation}\n"
            text_content += f"Station Status: {i.station_status}\n"
            text_content += f"Antenna Type and Serial No.: {i.antenna_type_and_serial_no}\n"
            text_content += f"Date of Installation of Antenna: {i.date_of_installation_of_antenna}\n"
            text_content += f"Offset Parameter of Antenna: {i.offset_parameter_of_antenna}\n"
            text_content += f"Height of Bottom of Antenna from Base of Pillar (cm): {i.height_of_bottom_of_antenna_from_base_of_pillar}\n"
            text_content += f"Height of Bottom of Antenna from Top of Base Plate (cm): {i.height_of_bottom_of_antenna_from_top_of_base_plate}\n"
            text_content += f"Height of Bottom of Antenna from Solar Panel Lower Angle Bottom (cm): {i.height_of_bottom_of_antenna_from_solar_panel_lower_angle_bottom}\n"
            text_content += f"Dimension of Pillar (H*W*B) in cm: {i.dimension_of_pillar}\n"
            text_content += f"Dimension of Pedestal (H*W*B) in cm: {i.dimension_of_pedestal}\n"
            text_content += f"GNSS Data Logging Interval is 1 second: {i.logging_interval_of_gnss_data}\n"
            text_content += f"GNSS Data Frequencies: {i.gnss_data_frequencies}\n"
            text_content += f"Electricity Provider Name & Connection No: {i.electricity_provider}\n"
            text_content += f"Two No. of solar Panels (60 W): {i.twonumber_of_solar_panels}\n"
            text_content += f"Serial No. of Solar Panel 1 and 2: {i.serial_no_of_solar_panels1and2}\n"
            text_content += f"2 No. of Batteries (12V) (DC): {i.batteries_12v_2}\n"
            text_content += f"Company Name and Serial No. of Batteries: {i.company_name_and_no_of_batteries}\n"
            text_content += f"Company Name of SIM1 & Mobile No.: {i.company_name_of_sim1}\n"
            text_content += f"Company Name of SIM2 & Mobile No.: {i.company_name_of_sim2}\n"
            text_content += f"Company Name and Serial No. of Broadband: {i.company_name_and_no_of_broadband}\n"
            text_content += f"Broadband Plan Validity: {i.broadband_plan_validity}\n"
            text_content += f"Receiver Model name and Serial No.: {i.receiver_model_name_and_serial_no}\n"
            text_content += f"Date of Installation of Receiver and Firmware: {i.date_of_installation_of_receiver_and_firmware}\n"
            text_content += f"Date of Installation of Radome and Serial No: {i.date_of_installation_of_radome_and_serial_no}\n"
            text_content += f"Serial No. of Meteorological Sensor if any: {i.serial_no_of_meteorological_sensor}\n"
            text_content += f"Date of Installation of Meteorological Sensor: {i.date_of_installation_of_meteorological_sensor}\n"
            text_content += f"Meteorological Sensor Type and Firmware: {i.meteorological_sensor_type_and_firmware}\n"
            text_content += f"Last Date of Site Visit: {i.last_date_of_site_visit}\n"
            text_content += f"Operation & Maintainance Remark: {i.operationmaintainanceremark}\n"
            text_content += f"Image East Uploaded By The Service Provider: {i.image_east}\n"
            text_content += f"Image West Uploaded By The Service Provider: {i.image_west}\n"
            text_content += f"Image North Uploaded By The Service Provider: {i.image_north}\n"
            text_content += f"Image South Uploaded By The Service Provider: {i.image_south}\n"
            text_content += f"Data Update Time: {i.vendor_time}\n"
            text_content += "\n"

        # Create the response
        response = HttpResponse(text_content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="Vendor_data.txt"'
        return response



def control_centerlog(request):
    corsid = request.POST.get('corsid')
    request.session['corsid'] = corsid
    data  = CorsAppCentreDataBackup.objects.filter(corsid=corsid)
    context = {
        'data':data
    }
    return render(request,'controlcentre_log.html',context)


def control_centerlogdownload(request):
    if request.method == 'GET':
        corsid = request.session.get('corsid')
        control_data = CorsAppCentreDataBackup.objects.filter(corsid=corsid)
        text_content = ""
        for gdc in control_data:
            text_content += f"CORS ID: {gdc.corsid}\n"
            text_content += f"State Name: {gdc.state}\n"
            text_content += f"Site Name: {gdc.site_name}\n"
            text_content += f"Site Code: {gdc.site_code}\n"
            text_content += f"Latitude of Site (DMS): {gdc.coordinates_of_sites_dms_lat}\n"
            text_content += f"Longitude of Site (DMS): {gdc.coordinates_of_sites_dms_long}\n"
            text_content += f"Ellipsoid Height (m): {gdc.coordinates_of_sites_dms_elp_height}\n"
            text_content += f"Vendor Username: {gdc.vendor_username}\n"
            text_content += f"GD Username: {gdc.gdc_username}\n"
            text_content += f"Data Update Time: {gdc.updatetime}\n"
            # Add other fields as needed
            text_content += "\n"  
        response = HttpResponse(text_content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="CORSProcessingandMonitoringCentre_data.txt"'
        return response



def gdc_log(request):
    if request.method =='POST':
        corsid = request.POST['corsid']
        request.session['corsid'] = corsid
        gdc_data  = CorsAppGdcDataBackup.objects.filter(corsid=corsid)

        context = {
            'gdc_data':gdc_data
        }
        return render(request,'gd_log.html',context)
    return render(request,'gd_log.html')



def gdc_logdownload_text_file(request):
    if request.method == 'GET':
        corsid = request.session.get('corsid')
        gdc_data = CorsAppGdcDataBackup.objects.filter(corsid=corsid)
        text_content = []
        for gdc in gdc_data:
            text_content += f"CORS ID: {gdc.corsid}\n"
            text_content += f"State Name: {gdc.state_name}\n"
            text_content += f"Site Name: {gdc.site_name}\n"
            text_content += f"Dist Name: {gdc.dist_name}\n"
            text_content += f"Tahsil Name: {gdc.tahsil_name}\n"
            text_content += f"Pin Code: {gdc.pin_code}\n"
            text_content += f"GDC Name: {gdc.gdc_name}\n"
            text_content += f"AUTHORISED PERSON NAME & DESIGNATION: {gdc.person_of_gdc}\n"
            text_content += f"Authorised Person Contact No: {gdc.contact_no_of_gdc}\n"
            text_content += f"LAST DATE OF VISIT: {gdc.last_date_of_gdc_visit}\n"
            text_content += f"Inspection Remark: {gdc.remark}\n"
            
            # Adding clickable links to the images
            text_content += f"Image East Uploaded By The Field Team: {gdc.image_east.url if gdc.image_east else 'No Image Available'}\n"
            text_content += f"Image West Uploaded By The Field Team: {gdc.image_west.url if gdc.image_west else 'No Image Available'}\n"
            text_content += f"Image North Uploaded By The Field Team: {gdc.image_north.url if gdc.image_north else 'No Image Available'}\n"
            text_content += f"Image South Uploaded By The Field Team: {gdc.image_south.url if gdc.image_south else 'No Image Available'}\n"
            text_content += f"Data Update Time: {gdc.updatetime}\n"
            
            text_content += "\n"

        response = HttpResponse(text_content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="gddata.txt"'
        return response


######################################################################## qu plot data code ###############################################################################


import os
from django.shortcuts import render
from .models import *

from django.conf import settings
from PIL import Image
from django.http import HttpResponse
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from django.http import JsonResponse




# def display_Images(request):
#     # Get the path to qc_plots and qc_Plots_UP directory within MEDIA_ROOT
#     qc_plots_path = os.path.join(settings.MEDIA_ROOT, 'qc_plots')
#     # qc_plots_up_path = os.path.join(settings.MEDIA_ROOT, 'qc_plots_up')
#     try:
#         # List site folders in qc_plots directory
#         site_folders = os.listdir(qc_plots_path)
#         # site_folders_1 = os.listdir(qc_plots_path, "MP")
#         # site_folders_2 = os.listdir( qc_plots_up_path, "UP")
#         # site_folders_1 = [(folder, "MP") for folder in os.listdir(qc_plots_path)]
#         # site_folders_2 = [(folder, "UP") for folder in os.listdir(qc_plots_up_path)]
#         # site_folders = site_folders_1 + site_folders_2
        
#         for site_code, state in site_folders:
            
#             # Construct full path to site folder
#             if state == "MP":
#                 site_folder_path = os.path.join(qc_plots_path, site_code)
#             elif state == "UP":
#                 site_folder_path = os.path.join(qc_plots_path, site_code)

#             if os.path.isdir(site_folder_path):
#                 # List PNG images in the site folder
#                 png_images = [image for image in os.listdir(site_folder_path) if image.lower().endswith('.png')]
                
#                 # Check if there are at least 4 PNG images
#                 if len(png_images) >= 4:
#                     # state = "MP" 
#                      # Fetch site_name from District model based on site_code
#                     district = District.objects.filter(name=site_code).first()
#                     site_name = district.site_name if district else ""
#                     coordinates = " "

#                     # Create Plot_data instance
#                     plot_data = Plot_data.objects.create(
#                         state=state,
#                         site_code=site_code,
#                         site_name =site_name,
#                         coordinates=coordinates,
#                         image_Cycle_Slip_PLOT=os.path.join('qc_plots', site_code, png_images[0]),
#                         image_MP_PLOT=os.path.join('qc_plots', site_code, png_images[1]),
#                         image_Percentage_Observation=os.path.join('qc_plots', site_code, png_images[2]),
#                         image_TS_PLOT=os.path.join('qc_plots', site_code, png_images[3])
#                     #     image_Cycle_Slip_PLOT=os.path.join('qc_plots' if state == "MP" else 'qc_plots_up', site_code, png_images[0]),
#                     #     image_MP_PLOT=os.path.join('qc_plots' if state == "MP" else 'qc_plots_up', site_code, png_images[1]),
#                     #     image_Percentage_Observation=os.path.join('qc_plots' if state == "MP" else 'qc_plots_up', site_code, png_images[2]),
#                     #     image_TS_PLOT=os.path.join('qc_plots' if state == "MP" else 'qc_plots_up', site_code, png_images[3])
#                     )
                    
#                     # Save the instance
                    
#                     plot_data.save()
                   
#     except FileNotFoundError:
#         # Handle the case where qc_plots directory does not exist
#         pass
    
#     return render(request, 'Display_Images.html')


 
    
def plot_data(request):
    states = PlotAppState.objects.using('database2').all()
    data = None
    selected_state = None
    if request.method == 'POST':
        state = request.POST.get('state')
        request.session['state'] = state 
        site_name = request.POST.get('site_name').strip()
        request.session['site_name'] = site_name 
        data = PlotAppPlotData.objects.using('database2').filter(site_name=site_name)
    else:
        selected_state = request.session.get('state')  # Get selected state from session
    return render(request, 'plot_data.html', {'states': states, 'selected_state': selected_state, 'data': data})
   


def load_districts(request):
    state_id = request.GET.get('state_id')
    districts = PlotAppDistrict.objects.using('database2').filter(state_id=state_id).order_by('site_name')
    return JsonResponse(list(districts.values('id', 'site_name')), safe=False)




def generate_pdf(request):
    state_id = request.session.get('state')
    site_name = request.session.get('site_name')

    if not site_name or not state_id:
        return HttpResponse("site_name or state not found in session.", status=400)

    state_data = PlotAppState.objects.using('database2').filter(id=state_id).values_list('name', flat=True).first()
    if not state_data:
        return HttpResponse("State not found.", status=400)
    
    # Fetch site code and coordinates from SiteData model based on site_name
    site_data = PlotAppSitedata.objects.using('database2').filter(site_name=site_name).first()
    if not site_data:
        return HttpResponse("Site data not found.", status=400)
    
    site_code = site_data.site_code
    coordinates = f"Lat: {site_data.coordinates_of_sites_dms_lat}, Long: {site_data.coordinates_of_sites_dms_long}, Height: {site_data.coordinates_of_sites_dms_elp_height}"
    
    
    data = PlotAppPlotData.objects.using('database2').filter(site_name=site_name)
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{site_name}_data.pdf"'
    
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Add site code, coordinates, state, and site name as text elements
    styles = getSampleStyleSheet()
    site_code_text = f"Site Code: {site_code}"
    state_text = f"State: {state_data}"
    site_text = f"Site Name: {site_name}"
    coordinates_text = f"Coordinates: {coordinates}"
    elements.append(Paragraph(site_code_text, styles['Normal']))
    elements.append(Paragraph(state_text, styles['Normal']))
    elements.append(Paragraph(site_text, styles['Normal']))
    elements.append(Paragraph(coordinates_text, styles['Normal']))
    elements.append(Paragraph("<br/> <br/>", styles['Normal'])) # Add some space after the texts
    
    # Add images 
    for item in data:
        image_path = item.image_Cycle_Slip_PLOT.path
        image = Image(image_path, width=360, height=260)
        elements.append(image)
        
        image_path = item.image_MP_PLOT.path
        image = Image(image_path, width=360, height=260)
        elements.append(image)
        
        image_path = item.image_Percentage_Observation.path
        image = Image(image_path, width=360, height=260)
        elements.append(image)
        
        image_path = item.image_TS_PLOT.path
        image = Image(image_path, width=360, height=260)
        elements.append(image)

    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    response.write(pdf_bytes)
    return response





################################################################################ GRMDB #################################################
from django.db import connections
from django.contrib.auth.hashers import check_password

# def grmdblogin_view(request):
#     gd_users = User.objects.filter(gdc=True)
#     if request.method == 'POST':
#         user_type = request.POST.get('user_type')
#         username = request.POST.get('username')
#         print(username)
#         password = request.POST.get('password')
#         print(password)
#         user = None
#         if user_type == 'gtstation':
#             user = authenticate(request, username=username, password=password)
            
#             if user and user.gdc:
#                 login(request, user)
#                 request.session['user_id'] = user.id  # Save user ID in session
#                 request.session['user_type'] = user_type
#                 return redirect(reverse('gtstationdashboard'))
#         elif user_type == 'gcp':
#             user = authenticate(request, username=username, password=password)
#             if user and user.gdc:
#                 login(request, user)
#                 request.session['user_id'] = user.id  # Save user ID in session
#                 request.session['user_type'] = user_type
#                 return redirect(reverse('gcpdashboard'))  
#         elif user_type == 'sbm':
#             user = authenticate(request, username=username, password=password)
#             if user and user.gdc:
#                 login(request, user)
#                 request.session['user_id'] = user.id  # Save user ID in session
#                 request.session['user_type'] = user_type
#                 return redirect(reverse('sbmdashboard'))      
#         return render(request, 'grmdb/login.html', {'error': 'Invalid username or password or user type'})
#     return render(request, 'grmdb/login.html',{'gd_users': gd_users})


def grmdblogin_view(request):
    gd_users = User.objects.filter(gdc=True)  # Query users from the second database
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        print(user_type)
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = None
        if user_type in ['gtstation', 'gcp', 'sbm']:
            try:
                cursor = connections['database3'].cursor()
                cursor.execute("SELECT * FROM auth_user WHERE username = %s", [username])
                user_data = cursor.fetchone()
                print('user_data',user_data)
                if user_data:
                    user_id, user_password = user_data[0], user_data[1]
                    if check_password(password, user_password):
                        user = AuthUser.objects.using('database3').get(id=user_id)
                        print("user2",user)
                    else:
                        error_message = 'Invalid username, or password'    
            except Exception as e:
                print(e)
        if user is not None:
            login(request, user)
            request.session['user_id'] = user.id  # Save user ID in session
            
            request.session['user_type'] = user_type
            if user_type == 'gtstation':
                print('gtstation')
                return redirect(reverse('gtstationdashboard'))
            elif user_type == 'gcp':
                return redirect(reverse('gcpdashboard'))
            elif user_type == 'sbm':
                return redirect(reverse('sbmdashboard'))

        return render(request, 'grmdb/login.html', {'error': error_message,'gd_users': gd_users})
    return render(request, 'grmdb/login.html', {'gd_users': gd_users})

def grmdbforgot_password(request):
    gdc_user = User.objects.filter(gdc=True)
    if request.method == 'POST':
        username = request.POST.get('username')
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')

        try:
            user = AuthUser.objects.using('database3').get(username=username)
            if check_password(current_password, user.password):
                user.password = make_password(new_password)
                user.save()
                return render(request, 'grmdb/forgot_password.html', {'success': 'Password has been changed successfully','gdc_user':gdc_user})
            else:
                return render(request, 'grmd/forgot_password.html', {'error': 'Incorrect current password','gdc_user':gdc_user})
        except AuthUser.DoesNotExist:
            return render(request, 'grmdb/forgot_password.html', {'error': 'Username not found','gdc_user':gdc_user})
    return render(request, 'grmdb/forgot_password.html',{'gdc_user':gdc_user})

def admin_login(request):
    if request.method == 'POST':
        username = request.POST.get('role')
        password = request.POST.get('password')
        user = authenticate(username=username, password=password)
        if user is None:
            try:
                cursor = connections['database3'].cursor()
                cursor.execute("SELECT id, password FROM auth_user WHERE username = %s", [username])
                user_data = cursor.fetchone()
                if user_data:
                    user_id, user_password = user_data
                    if check_password(password, user_password):
                        user = AuthUser.objects.using('database3').get(id=user_id)
                        print("user", user)
                    else:
                        error_message = 'Invalid username, or password'    
            except Exception as e:
                print(e)
        if user is not None:
            login(request, user)
            request.session['user_id'] = user.id
            request.session['username'] = username  # Ensure this is set correctly
            print(f"User logged in: {username}") 
            if username == 'admin':
                return redirect(reverse('admin_dashboard')) 
            if username == 'OC HPL & CW':
                return redirect(reverse('oc_hpcl_cw'))
            elif username == 'OC SGW':
                return redirect(reverse('oc_sgw'))
            elif username == 'I/C DATA CENTER':
                return redirect(reverse('ic_datacenter'))
        return render(request, 'grmdb/adminlogin.html',{'error': error_message})    
    
    return render(request, 'grmdb/adminlogin.html')

def signup(request):
    if request.method == 'POST':
        user_type = request.POST.get('user_type')
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')
        User = get_user_model()
        if User.objects.filter(username=username).exists():
            return render(request, 'grmdb/signup.html', {'error': 'Username already exists'})
        # Create the user
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email,
        )
        if user_type == 'gdc':
            user.gdc = True
        elif user_type == 'cors':
            user.cors = True
        user.save()
        return redirect('login')
    return render(request, 'grmdb/signup.html')

def logout_view(request):
    logout(request)
    return redirect('/')

def gtstationdashboard(request):
    print()
    query = request.POST.get('searchdata', '')
    request.session['query'] = query
    user_id = request.session.get('user_id')
    user = AuthUser.objects.using('database3').get(id=user_id)
    
    username = user.username
    user_data = BenchmarkGtstation.objects.using('database3').filter(gdc_username=username)
   
    
    if query:
        user_data = user_data.filter(Q(state__icontains=query) | Q(district__icontains=query) | Q(conduction_of_gtstation__icontains=query))
    context = {
        'user_data': user_data,
        'username':username
    }
    return render(request, 'grmdb/gtstationdashboard.html', context)



def gtstationdownload_csv(request):
    user_id = request.session.get('user_id')
    query = request.session.get('query')
    user = AuthUser.objects.using('database3').get(id=user_id)
    username = user.username
    user_data = BenchmarkGtstation.objects.using('database3').filter(gdc_username=username)
    
    if query:
        user_data = user_data.filter(Q(state__icontains=query) | Q(district__icontains=query) | Q(conduction_of_gtstation__icontains=query))
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="gt_station_data.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Key Id.', 'GT STATION NAME', 'PAMPHLET NO.', 'STATE', 'DISTRICT', 'TAHSIL', 'PIN CODE',
        'APPROX LATITUDE', 'APPROX LONGITUDE', 'TRIANGULATED HEIGHT (M)', 'ELLIPSOID HEIGHT (M)',
        'ORTHOMETRIC Height (m)', 'GRAVITY VALUE (MICROGAL)', 'GT STATION INSCRIPTION', 'OLD DESCRIPTION',
        'REVISED DESCRIPTION (IF NECESSARY)', 'CONDITION OF GT STATION', 'IMAGE EAST UPLOADED BY THE FIELD TEAM',
        'IMAGE WEST UPLOADED BY THE FIELD TEAM', 'IMAGE NORTH UPLOADED BY THE FIELD TEAM',
        'IMAGE SOUTH UPLOADED BY THE FIELD TEAM', 'INSPECTING PERSON NAME & DESIGNATION',
        'INSPECTING PERSON CONTACT NO.', 'LAST DATE OF VISIT', 'INSPECTION REMARK', 'GD USERNAME'
    ])

    for i in user_data:
        writer.writerow([
            i.keyid, i.gtstation_name, i.pamphlet_no, i.state, i.district, i.tahsil, i.pincode,
            i.latitude, i.longitude, i.triangulatedheight, i.ellipsoidheight, i.orthometrichight,
            i.gravityvalue, i.gt_station_inscription, i.old_description, i.revised_description,
            i.conduction_of_gtstation, i.image_east.url if i.image_east else 'No Image Available',
            i.image_west.url if i.image_west else 'No Image Available',
            i.image_north.url if i.image_north else 'No Image Available',
            i.image_south.url if i.image_south else 'No Image Available',
            i.authorised_person_name_and_designation, i.authorised_person_contactno,
            i.last_date_of_vist, i.inspection_remark, i.gdc_username
        ])

    return response



def gcpdashboard(request):
    query = request.POST.get('searchdata', '')
    request.session['query'] = query
    user_id = request.session.get('user_id')
    user = AuthUser.objects.using('database3').get(id=user_id)
    username = user.username
    user_data = BenchmarkGcpdata.objects.using('database3').filter(gdc_username=username)
    
    if query:
        user_data = user_data.filter(Q(state__icontains=query) | Q(gcp_name__icontains=query) | Q(district__icontains=query) | Q(conduction_of_gcp__icontains=query) | Q(tahsil__icontains=query))
    
    context = {
        'user_data': user_data,
        'username':username
    }
    return render(request, 'grmdb/gcpdashboard.html', context)


def download_gcp_data_csv(request):
    query = request.session.get('query')
    user_id = request.session.get('user_id')
    user = AuthUser.objects.using('database3').get(id=user_id)
    username = user.username
    user_data = BenchmarkGcpdata.objects.using('database3').filter(gdc_username=username)
    
    if query:
        user_data = user_data.filter(Q(state__icontains=query) | Q(gcp_name__icontains=query) | Q(district__icontains=query) | Q(conduction_of_gcp__icontains=query) | Q(tahsil__icontains=query))
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="gcp_data.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Key Id.', 'PID', 'GCP NAME', 'STATE', 'DISTRICT', 'TAHSIL', 'PIN CODE',
        'LATITUDE', 'LONGITUDE', 'Ellipsoid HEIGHT (m)', 'ORTHOMETRIC HEIGHT (m)', 'GRAVITY VALUE (MICROGAL)',
        'GCP ON PILLAR/ROCK', 'GCP OLD DESCRIPTION', 'GCP REVISED DESCRIPTION (IF NECESSARY)',
        'CONDITION OF GCP', 'IMAGE EAST UPLOADED BY THE FIELD TEAM', 'IMAGE WEST UPLOADED BY THE FIELD TEAM',
        'IMAGE NORTH UPLOADED BY THE FIELD TEAM', 'IMAGE SOUTH UPLOADED BY THE FIELD TEAM',
        'INSPECTING PERSON NAME & DESIGNATION', 'INSPECTING PERSON CONTACT NO.', 'LAST DATE OF VISIT',
        'INSPECTION REMARK', 'GD USERNAME'
    ])

    for i in user_data:
        writer.writerow([
            i.keyid, i.pid, i.gcp_name, i.state, i.district, i.tahsil, i.pincode,
            i.latitude, i.longitude, i.ellipsoidheight, i.orthometrichight, i.gravityvalue,
            i.gcp_on_pillar, i.old_description, i.revised_description,
            i.conduction_of_gcp, i.image_east.url if i.image_east else 'No Image Available',
            i.image_west.url if i.image_west else 'No Image Available',
            i.image_north.url if i.image_north else 'No Image Available',
            i.image_south.url if i.image_south else 'No Image Available',
            i.authorised_person_name_and_designation, i.authorised_person_contactno,
            i.last_date_of_vist, i.inspection_remark, i.gdc_username
        ])

    return response



def sbmdashboard(request):
    query = request.POST.get('searchdata', '')
    request.session['query'] = query
    user_id = request.session.get('user_id')
    user = AuthUser.objects.using('database3').get(id=user_id)
    username = user.username
    user_data = BenchmarkSbmdata.objects.using('database3').filter(gdc_username=username)
    
    if query:
        user_data = user_data.filter(Q(state__icontains=query) | Q(sbm_type__icontains=query) | Q(district__icontains=query)| Q(conduction_of_sbm__icontains=query) | Q(conduction_of_reference_pillar__icontains=query) | Q(tahsil__icontains=query))
    
    context = {
        'user_data': user_data,
        'username':username
    }
    return render(request, 'grmdb/sbmdasboard.html', context)



def download_sbm_data_csv(request):
    query = request.session.get('query')
    user_id = request.session.get('user_id')
    user = AuthUser.objects.using('database3').get(id=user_id)
    username = user.username
    user_data = BenchmarkSbmdata.objects.using('database3').filter(gdc_username=username)
    
    if query:
        user_data = user_data.filter(Q(state__icontains=query) | Q(sbm_type__icontains=query) | Q(district__icontains=query) | Q(conduction_of_reference_pillar__icontains=query) | Q(tahsil__icontains=query))
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="sbm_data.csv"'

    writer = csv.writer(response)
    header_row = [
        'Key Id.', 'SBM TYPE', 'PAMPHLET NO.', 'STATE', 'DISTRICT', 'TAHSIL', 'PIN CODE',
        'LATITUDE', 'LONGITUDE', 'SBM INSCRIPTION', 'SBM OLD DESCRIPTION', 'SBM REVISED DESCRIPTION (IF NECESSARY)',
        'CONDITION OF SBM', 'CONDITION OF REFERENCE PILLAR (IF NECESSARY)', 'IMAGE EAST UPLOADED BY THE FIELD TEAM',
        'IMAGE WEST UPLOADED BY THE FIELD TEAM', 'IMAGE NORTH UPLOADED BY THE FIELD TEAM', 'IMAGE SOUTH UPLOADED BY THE FIELD TEAM',
        'INSPECTING PERSON NAME & DESIGNATION', 'INSPECTING PERSON CONTACT NO.', 'LAST DATE OF VISIT',
        'INSPECTION REMARK', 'GDC NAME', 'LAST UPDATE TIME'
    ]
    # Add values for dynamically added columns
    # Assuming a custom method get_item to fetch dynamically added columns

    writer.writerow(header_row)

    for i in user_data:
        row = [
            i.keyid, i.sbm_type, i.pamphlet_no, i.state, i.district, i.tahsil, i.pincode,
            i.latitude, i.longitude, i.sbm_inscription, i.old_description, i.revised_description,
            i.conduction_of_sbm, i.conduction_of_reference_pillar,
            i.image_east.url if i.image_east else 'No Image Available',
            i.image_west.url if i.image_west else 'No Image Available',
            i.image_north.url if i.image_north else 'No Image Available',
            i.image_south.url if i.image_south else 'No Image Available',
            i.authorised_person_name_and_designation, i.authorised_person_contactno,
            i.last_date_of_vist, i.inspection_remark, i.gdc_username, i.updatetime
        ]
        # Add values for dynamically added columns
        # row += [i.get_item(column_name) for column_name in dynamically_added_columns]

        writer.writerow(row)

    return response

# def sbmdashboard(request):
#     user_id = request.session.get('user_id')
#     user = User.objects.get(id=user_id)
#     username = user.username
#     user_data = sbmdata.objects.filter(gdc_username=username)

#     # Retrieve dynamically added columns from session (if any)
#     dynamic_columns = request.session.get('columns', [])

#     # Prepare a list of dictionaries with attributes for each user_data instance
#     user_data_with_dynamic_columns = []

#     for i in user_data:
#         row = {
#             'id': i.id,
#             'sbm_type': i.sbm_type,
#             'pamphlet_no': i.pamphlet_no,
#             'state': i.state,
#             'district': i.district,
#             'tahsil': i.tahsil,
#             'pincode': i.pincode,
#             'longitude': i.longitude,
#             'latitude': i.latitude,
#             'sbm_inscription': i.sbm_inscription,
#             'old_description': i.old_description,
#             'revised_description': i.revised_description,
#             'conduction_of_sbm': i.conduction_of_sbm,
#             'conduction_of_reference_pillar': i.conduction_of_reference_pillar,
#             'photo_of_sbm': i.photo_of_sbm,
#             'authorised_person_name_and_designation': i.authorised_person_name_and_designation,
#             'authorised_person_contactno': i.authorised_person_contactno,
#             'last_date_of_vist': i.last_date_of_vist,
#             'inspection_remark': i.inspection_remark,
#             'gdc_username': i.gdc_username
#         }
#         for column in dynamic_columns:
#             row[column] = getattr(i, column, '')
#         user_data_with_dynamic_columns.append(row)
        
#     context = {
#         'user_data': user_data_with_dynamic_columns,
#         'dynamic_columns': dynamic_columns
#     }
#     print(context)
#     return render(request, 'sbmdasboard.html', context)



def edit_gcpdata(request, id):
    date = datetime.datetime.now()
    gcpalldata = BenchmarkGcpdata.objects.using('database3').get(id=id)
    
    # Backup existing image paths
    old_image_east = gcpalldata.image_east
    old_image_west = gcpalldata.image_west
    old_image_north = gcpalldata.image_north
    old_image_south = gcpalldata.image_south

    if request.method == 'POST':
        # Update the fields that are part of the form submission
        gcpalldata.district = request.POST.get('district')
        gcpalldata.tahsil = request.POST.get('tahsil')
        gcpalldata.pincode = request.POST.get('pincode')
        gcpalldata.orthometrichight = request.POST.get('orthometrichight')
        gcpalldata.gravityvalue = request.POST.get('gravityvalue')
        
        if request.POST.get('gcp_on_pillar'):
            gcpalldata.gcp_on_pillar = request.POST['gcp_on_pillar']

        gcpalldata.revised_description = request.POST.get('revised_description')
        if request.POST.get('conduction_of_gcp'):
            gcpalldata.conduction_of_gcp = request.POST['conduction_of_gcp']

        gcpalldata.authorised_person_name_and_designation = request.POST.get('authorised_person_name_and_designation')
        gcpalldata.authorised_person_contactno = request.POST.get('authorised_person_contactno')
        gcpalldata.last_date_of_vist = request.POST.get('last_date_of_vist')
        gcpalldata.inspection_remark = request.POST.get('inspection_remark')

        # Handle image uploads and preserve the existing path if not re-uploaded
        if 'image_east' in request.FILES:
            gcpalldata.image_east = request.FILES.get('image_east')
        else:
            gcpalldata.image_east = old_image_east.name  # Keep the original path

        if 'image_west' in request.FILES:
            gcpalldata.image_west = request.FILES.get('image_west')
        else:
            gcpalldata.image_west = old_image_west.name  # Keep the original path

        if 'image_north' in request.FILES:
            gcpalldata.image_north = request.FILES.get('image_north')
        else:
            gcpalldata.image_north = old_image_north.name  # Keep the original path

        if 'image_south' in request.FILES:
            gcpalldata.image_south = request.FILES.get('image_south')
        else:
            gcpalldata.image_south = old_image_south.name  # Keep the original path

        # Rename image files
        def rename_image(image_field, direction):
            if image_field and not image_field.name.startswith('image/'):
                ext = os.path.splitext(image_field.name)[-1]
                formatted_date = timezone.now().strftime("%Y-%m-%d")
                new_name = f"{gcpalldata.keyid}_{direction}_{formatted_date}{ext}"
                image_field.name = os.path.join('image', new_name)

        rename_image(gcpalldata.image_east, "east")
        rename_image(gcpalldata.image_west, "west")
        rename_image(gcpalldata.image_north, "north")
        rename_image(gcpalldata.image_south, "south")

        gcpalldata.updatetime = date
        gcpalldata.save()
        messages.success(request, 'Successfully updated your data')
        return redirect('gcpdashboard')

    return render(request, 'grmdb/gcpedit.html', {'gcpalldata': gcpalldata})




def edit_gtstationdata(request, id):
    date = datetime.datetime.now()
    gtalldata = BenchmarkGtstation.objects.using('database3').get(id=id)
    
    # Backup existing image paths
    old_image_east = gtalldata.image_east
    old_image_west = gtalldata.image_west
    old_image_north = gtalldata.image_north
    old_image_south = gtalldata.image_south

    if request.method == 'POST':
        # Update the fields that are part of the form submission
        gtalldata.district = request.POST.get('district')
        gtalldata.tahsil = request.POST.get('tahsil')
        gtalldata.pincode = request.POST.get('pincode')
        gtalldata.gt_station_inscription = request.POST.get('gt_station_inscription')
        gtalldata.old_description = request.POST.get('old_description')
        gtalldata.revised_description = request.POST.get('revised_description')
        
        if request.POST.get('conduction_of_gtstation'):
            gtalldata.conduction_of_gtstation = request.POST['conduction_of_gtstation']

        gtalldata.authorised_person_name_and_designation = request.POST.get('authorised_person_name_and_designation')
        gtalldata.authorised_person_contactno = request.POST.get('authorised_person_contactno')
        gtalldata.last_date_of_vist = request.POST.get('last_date_of_vist')
        gtalldata.inspection_remark = request.POST.get('inspection_remark')

        # Handle image uploads and preserve the existing path if not re-uploaded
        if 'image_east' in request.FILES:
            gtalldata.image_east = request.FILES.get('image_east')
        else:
            gtalldata.image_east = old_image_east.name  # Keep the original path

        if 'image_west' in request.FILES:
            gtalldata.image_west = request.FILES.get('image_west')
        else:
            gtalldata.image_west = old_image_west.name  # Keep the original path

        if 'image_north' in request.FILES:
            gtalldata.image_north = request.FILES.get('image_north')
        else:
            gtalldata.image_north = old_image_north.name  # Keep the original path

        if 'image_south' in request.FILES:
            gtalldata.image_south = request.FILES.get('image_south')
        else:
            gtalldata.image_south = old_image_south.name  # Keep the original path

        # Rename image files
        def rename_image(image_field, direction):
            if image_field and not image_field.name.startswith('image/'):
                ext = os.path.splitext(image_field.name)[-1]
                formatted_date = timezone.now().strftime("%Y-%m-%d")
                new_name = f"{gtalldata.keyid}_{direction}_{formatted_date}{ext}"
                image_field.name = os.path.join('image', new_name)

        rename_image(gtalldata.image_east, "east")
        rename_image(gtalldata.image_west, "west")
        rename_image(gtalldata.image_north, "north")
        rename_image(gtalldata.image_south, "south")

        gtalldata.updatetime = date    
        gtalldata.save()

        messages.success(request, 'Successfully updated your data')
        return redirect('gtstationdashboard')

    return render(request, 'grmdb/edit_gt_station.html', {'gtalldata': gtalldata})





def edit_sbmdata(request, id):
    date = datetime.datetime.now()
    sbmalldata = BenchmarkSbmdata.objects.using("database3").get(id=id)

    if request.method == 'POST':
        # Handle image uploads only if a new file is provided
        if 'image_east' in request.FILES:
            sbmalldata.image_east = request.FILES.get('image_east')
        else:
            # Retain the existing path if no new image is uploaded
            sbmalldata.image_east = sbmalldata.image_east.name

        if 'image_west' in request.FILES:
            sbmalldata.image_west = request.FILES.get('image_west')
        else:
            sbmalldata.image_west = sbmalldata.image_west.name

        if 'image_north' in request.FILES:
            sbmalldata.image_north = request.FILES.get('image_north')
        else:
            sbmalldata.image_north = sbmalldata.image_north.name

        if 'image_south' in request.FILES:
            sbmalldata.image_south = request.FILES.get('image_south')
        else:
            sbmalldata.image_south = sbmalldata.image_south.name

        # Update other fields
        if request.POST.get('sbm_type'):
            sbmalldata.sbm_type = request.POST['sbm_type']
        
        sbmalldata.district = request.POST.get('district', sbmalldata.district)
        sbmalldata.tahsil = request.POST.get('tahsil', sbmalldata.tahsil)
        sbmalldata.pincode = request.POST.get('pincode', sbmalldata.pincode)
        sbmalldata.latitude = request.POST.get('latitude', sbmalldata.latitude)
        sbmalldata.longitude = request.POST.get('longitude', sbmalldata.longitude)
        sbmalldata.sbm_inscription = request.POST.get('sbm_inscription', sbmalldata.sbm_inscription)
        sbmalldata.old_description = request.POST.get('old_description', sbmalldata.old_description)
        sbmalldata.revised_description = request.POST.get('revised_description', sbmalldata.revised_description)
        
        if request.POST.get('conduction_of_sbm'):
            sbmalldata.conduction_of_sbm = request.POST['conduction_of_sbm']
        
        if request.POST.get('conduction_of_reference_pillar'):
            sbmalldata.conduction_of_reference_pillar = request.POST['conduction_of_reference_pillar']
        
        sbmalldata.authorised_person_name_and_designation = request.POST.get('authorised_person_name_and_designation', sbmalldata.authorised_person_name_and_designation)
        sbmalldata.authorised_person_contactno = request.POST.get('authorised_person_contactno', sbmalldata.authorised_person_contactno)
        sbmalldata.last_date_of_vist = request.POST.get('last_date_of_vist', sbmalldata.last_date_of_vist)
        sbmalldata.inspection_remark = request.POST.get('inspection_remark', sbmalldata.inspection_remark)
        
        sbmalldata.updatetime = date
        sbmalldata.save()
        
        messages.success(request, 'Successfully updated your data')
        return redirect('sbmdashboard')

    return render(request, 'grmdb/editsbm.html', {'sbmalldata': sbmalldata})



def addsbm(request):
    user_id = request.session.get('user_id')
    user = AuthUser.objects.using('database3').get(id=user_id)
    username = user.username
    date = datetime.datetime.now()
    gd_username = User.objects.filter(gdc=True)

    if request.method == "POST":
        # Fetch form data
        sbm_type = request.POST.get('sbm_type')
        state = request.POST.get('state')
        district = request.POST.get('district')
        tahsil = request.POST.get('tahsil')
        pincode = request.POST.get('pincode')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        sbm_inscription = request.POST.get('sbm_inscription')
        old_description = request.POST.get('old_description')
        revised_description = request.POST.get('revised_description')
        conduction_of_sbm = request.POST.get('conduction_of_sbm')
        conduction_of_reference_pillar = request.POST.get('conduction_of_reference_pillar')
        image_east = request.FILES.get('image_east')
        image_west = request.FILES.get('image_west')
        image_north = request.FILES.get('image_north')
        image_south = request.FILES.get('image_south')
        authorised_person_name_and_designation = request.POST.get('authorised_person_name_and_designation')
        authorised_person_contactno = request.POST.get('authorised_person_contactno')
        last_date_of_vist = request.POST.get('last_date_of_vist')
        inspection_remark = request.POST.get('inspection_remark')

        # Create new entry
        new_entry = BenchmarkSbmdata(
            sbm_type=sbm_type,
            state=state,
            district=district,
            tahsil=tahsil,
            pincode=pincode,
            latitude=latitude,
            longitude=longitude,
            sbm_inscription=sbm_inscription,
            old_description=old_description,
            revised_description=revised_description,
            conduction_of_sbm=conduction_of_sbm,
            conduction_of_reference_pillar=conduction_of_reference_pillar,
            authorised_person_name_and_designation=authorised_person_name_and_designation,
            authorised_person_contactno=authorised_person_contactno,
            last_date_of_vist=last_date_of_vist,
            inspection_remark=inspection_remark,
            gdc_username=username,
            updatetime=date,
        )

        # Assign images after instance creation, triggering the save method renaming
        new_entry.image_east = image_east
        new_entry.image_west = image_west
        new_entry.image_north = image_north
        new_entry.image_south = image_south

        # Save the new entry, which will now trigger the renaming logic in save()
        new_entry.save(using='database3')

        return redirect('sbmdashboard')

    return render(request, 'grmdb/addsbm.html', {'gd_username': gd_username})



def addgtstation(request):
    user_id = request.session.get('user_id')
    user = AuthUser.objects.using('database3').get(id=user_id)
    username = user.username
    date = datetime.datetime.now()
    gd_username = User.objects.filter(gdc=True)
    
    if request.method == "POST":
        # Collect form data
        gtstation_name = request.POST.get('gtstation_name')
        state = request.POST.get('state')
        district = request.POST.get('district')
        tahsil = request.POST.get('tahsil')
        pincode = request.POST.get('pincode')
        latitude = request.POST.get('latitude')
        longitude = request.POST.get('longitude')
        triangulatedheight = request.POST.get('triangulatedheight')
        ellipsoidheight = request.POST.get('ellipsoidheight')
        orthometrichight = request.POST.get('orthometrichight')
        gravityvalue = request.POST.get('gravityvalue')
        gt_station_inscription = request.POST.get('gt_station_inscription')
        old_description = request.POST.get('old_description')
        revised_description = request.POST.get('revised_description')
        conduction_of_gtstation = request.POST.get('conduction_of_gtstation')
        image_east = request.FILES.get('image_east')
        image_west = request.FILES.get('image_west')
        image_north = request.FILES.get('image_north')
        image_south = request.FILES.get('image_south')
        authorised_person_name_and_designation = request.POST.get('authorised_person_name_and_designation')
        authorised_person_contactno = request.POST.get('authorised_person_contactno')
        last_date_of_vist = request.POST.get('last_date_of_vist')
        inspection_remark = request.POST.get('inspection_remark')
        
        # Generate the new keyid
        last_entry = BenchmarkGtstation.objects.using("database3").all().order_by('id').last()
        if last_entry:
            last_keyid = last_entry.keyid
            new_keyid = int(last_keyid[3:]) + 1
            keyid = 'GTS' + str(new_keyid).zfill(4)
        else:
            keyid = 'GTS0001'
        
        # Helper function to rename images
        def rename_image(image_field, direction):
            if image_field:
                ext = os.path.splitext(image_field.name)[-1]
                formatted_date =  timezone.now().strftime("%Y-%m-%d")
                new_name = f"{keyid}_{direction}_{formatted_date}{ext}"
                image_field.name = os.path.join('image', new_name)

        # Rename images
        rename_image(image_east, "east")
        rename_image(image_west, "west")
        rename_image(image_north, "north")
        rename_image(image_south, "south")

        # Create and save the new entry
        new_entry = BenchmarkGtstation(
            gtstation_name=gtstation_name,
            state=state,
            district=district,
            tahsil=tahsil,
            pincode=pincode,
            latitude=latitude,
            longitude=longitude,
            triangulatedheight=triangulatedheight,
            ellipsoidheight=ellipsoidheight,
            orthometrichight=orthometrichight,
            gravityvalue=gravityvalue,
            gt_station_inscription=gt_station_inscription,
            old_description=old_description,
            revised_description=revised_description,
            conduction_of_gtstation=conduction_of_gtstation,
            image_east=image_east,
            image_west=image_west,
            image_north=image_north,
            image_south=image_south,
            authorised_person_name_and_designation=authorised_person_name_and_designation,
            authorised_person_contactno=authorised_person_contactno,
            last_date_of_vist=last_date_of_vist,
            inspection_remark=inspection_remark,
            gdc_username=username,
            updatetime=date,
            keyid=keyid
        )
        
        new_entry.save(using='database3')
        
        return redirect('gtstationdashboard')

    return render(request, 'grmdb/addongt.html', {'gd_username': gd_username})

# def addsbm(request, id):
#     sbm_instance = get_object_or_404(sbmdata, id=id)
    
#     if request.method == 'POST':
#         form = AddFieldForm(request.POST)
#         if form.is_valid():
#             field_name = form.cleaned_data['field_name']
#             field_value = form.cleaned_data['field_value']
#             sbm_instance.dynamic_fields[field_name] = field_value
#             sbm_instance.save()
#     else:
#         form = AddFieldForm()
    
#     return render(request, 'addsbm.html', {'form': form, 'sbm_instance': sbm_instance})



# def admin_login(request):
#     if request.method == 'POST':
#         username = request.POST.get('role')
#         password = request.POST.get('password')
#         user = authenticate(username=username,password=password)
#         # if user is not None:
#         #     login(request,user)
#         #     return redirect('admin_dashboard')
#         if user is None:
#                     try:
#                         cursor = connections['database3'].cursor()
#                         cursor.execute("SELECT * FROM auth_user WHERE username = %s", [username])
#                         user_data = cursor.fetchone()
#                         if user_data:
#                             user_id, user_password = user_data[0], user_data[1]
#                             if check_password(password, user_password):
#                                 user = AuthUser.objects.using('database3').get(id=user_id)
#                                 print("user",user)
#                     except Exception as e:
#                         print(e)
#     return render(request,'grmdb/adminlogin.html')



def admin_dashboard(request):
    query = request.POST.get('searchdata', '')
    data = BenchmarkGtstation.objects.using("database3").all()
    if query:
        data = data.filter(Q(state__icontains=query) | Q(district__icontains=query) | Q(conduction_of_gtstation__icontains=query) |Q(keyid__icontains=query))
    context = {
        'data':data
    }
    return render(request,'grmdb/admin_dashboard.html',context)


def admin_dashboardgcpdata(request):
    query = request.POST.get('searchdata', '')
    data = BenchmarkGcpdata.objects.using("database3").all()
    if query:
        data = data.filter(Q(state__icontains=query) | Q(gcp_name__icontains=query) | Q(district__icontains=query) | Q(conduction_of_gcp__icontains=query) | Q(tahsil__icontains=query)|Q(keyid__icontains=query))
    context = {
        'data':data
    }
    return render(request,'grmdb/admingcpdata.html',context)


def admin_dashboardSBMdata(request):
    query = request.POST.get('searchdata', '')
    data = BenchmarkSbmdata.objects.using("database3").all()
    if query:
        data = data.filter(Q(state__icontains=query) | Q(sbm_type__icontains=query) | Q(district__icontains=query)| Q(conduction_of_sbm__icontains=query) | Q(conduction_of_reference_pillar__icontains=query) | Q(tahsil__icontains=query)|Q(keyid__icontains=query))
    
    context = {
        'data':data
    }
    return render(request,'grmdb/adminsbmdata.html',context)



def gcp_log(request):
    keyid = request.POST.get('keyid')
    request.session['keyid'] = keyid
    data  = BenchmarkGcpdataBackup.objects.using("database3").filter(keyid=keyid)
    context = {
        'data':data
    }
    return render(request,'grmdb/gcp_log.html',context)


def benchmark_gcpdata_download(request):
    if request.method == 'GET':
        keyid = request.session.get('keyid')
        benchmark_data = BenchmarkGcpdataBackup.objects.using("database3").filter(keyid=keyid)
        text_content = ""
        
        for gcp in benchmark_data:
            text_content += f"Key ID: {gcp.keyid}\n"
            text_content += f"GCP Name: {gcp.gcp_name}\n"
            text_content += f"Pamphlet No: {gcp.pamphlet_no}\n"
            text_content += f"State: {gcp.state}\n"
            text_content += f"District: {gcp.district}\n"
            text_content += f"Tahsil: {gcp.tahsil}\n"
            text_content += f"Pincode: {gcp.pincode}\n"
            text_content += f"Longitude: {gcp.longitude}\n"
            text_content += f"Latitude: {gcp.latitude}\n"
            text_content += f"Ellipsoid Height: {gcp.ellipsoidheight}\n"
            text_content += f"Orthometric Height: {gcp.orthometrichight}\n"
            text_content += f"Gravity Value: {gcp.gravityvalue}\n"
            text_content += f"GCP on Pillar: {gcp.gcp_on_pillar}\n"
            text_content += f"Old Description: {gcp.old_description}\n"
            text_content += f"Revised Description: {gcp.revised_description}\n"
            text_content += f"Conduction of GCP: {gcp.conduction_of_gcp}\n"
            text_content += f"Image East: {gcp.image_east}\n"
            text_content += f"Image West: {gcp.image_west}\n"
            text_content += f"Image North: {gcp.image_north}\n"
            text_content += f"Image South: {gcp.image_south}\n"
            text_content += f"Authorised Person Name and Designation: {gcp.authorised_person_name_and_designation}\n"
            text_content += f"Authorised Person Contact No: {gcp.authorised_person_contactno}\n"
            text_content += f"Last Date of Visit: {gcp.last_date_of_vist}\n"
            text_content += f"Inspection Remark: {gcp.inspection_remark}\n"
            text_content += f"Update Time: {gcp.updatetime}\n"
            text_content += f"GDC Username: {gcp.gdc_username}\n"
            text_content += f"VALIDATION : {gcp.status}\n"
            text_content += f"PID: {gcp.pid}\n"
            text_content += "\n"  # Add a newline for separation between records
        
        response = HttpResponse(text_content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="BenchmarkGcpdataBackup.txt"'
        return response

def gtstation_log(request):
    keyid = request.POST.get('keyid')
    request.session['keyid'] = keyid
    data  = BenchmarkGtstationBackup.objects.using("database3").filter(keyid=keyid)
    context = {
        'data':data
    }
    return render(request,'grmdb/gtstationlog.html',context)




def benchmark_gtstation_download(request):
    if request.method == 'GET':
        keyid = request.session.get('keyid')
        benchmark_data = BenchmarkGtstationBackup.objects.using("database3").filter(keyid=keyid)
        text_content = ""
        
        for gtstation in benchmark_data:
            text_content += f"Key ID: {gtstation.keyid}\n"
            text_content += f"GT Station Name: {gtstation.gtstation_name}\n"
            text_content += f"Pamphlet No: {gtstation.pamphlet_no}\n"
            text_content += f"State: {gtstation.state}\n"
            text_content += f"Ellipsoid Height: {gtstation.ellipsoidheight}\n"
            text_content += f"Triangulated Height: {gtstation.triangulatedheight}\n"
            text_content += f"Orthometric Height: {gtstation.orthometrichight}\n"
            text_content += f"Gravity Value: {gtstation.gravityvalue}\n"
            text_content += f"District: {gtstation.district}\n"
            text_content += f"Tahsil: {gtstation.tahsil}\n"
            text_content += f"Pincode: {gtstation.pincode}\n"
            text_content += f"Longitude: {gtstation.longitude}\n"
            text_content += f"Latitude: {gtstation.latitude}\n"
            text_content += f"GT Station Inscription: {gtstation.gt_station_inscription}\n"
            text_content += f"Old Description: {gtstation.old_description}\n"
            text_content += f"Revised Description: {gtstation.revised_description}\n"
            text_content += f"Conduction of GT Station: {gtstation.conduction_of_gtstation}\n"
            text_content += f"Image East: {gtstation.image_east}\n"
            text_content += f"Image West: {gtstation.image_west}\n"
            text_content += f"Image North: {gtstation.image_north}\n"
            text_content += f"Image South: {gtstation.image_south}\n"
            text_content += f"Authorised Person Name and Designation: {gtstation.authorised_person_name_and_designation}\n"
            text_content += f"Authorised Person Contact No: {gtstation.authorised_person_contactno}\n"
            text_content += f"Last Date of Visit: {gtstation.last_date_of_vist}\n"
            text_content += f"Inspection Remark: {gtstation.inspection_remark}\n"
            text_content += f"Update Time: {gtstation.updatetime}\n"
            text_content += f"VALIDATION :{gtstation.status}\n"
            text_content += f"GDC Username: {gtstation.gdc_username}\n"
            text_content += "\n"  # Add a newline for separation between records
        
        response = HttpResponse(text_content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="BenchmarkGtstationBackup.txt"'
        return response


def sbm_log(request):
    keyid = request.POST.get('keyid')
    request.session['keyid'] = keyid
    data  = BenchmarkSbmdataBackup.objects.using("database3").filter(keyid=keyid)
    context = {
        'data':data
    }
    return render(request,'grmdb/sbmlogs.html',context)


def benchmark_sbmdata_download(request):
    if request.method == 'GET':
        keyid = request.session.get('keyid')
        benchmark_data = BenchmarkSbmdataBackup.objects.using("database3").filter(keyid=keyid)
        text_content = ""
        
        for sbm in benchmark_data:
            text_content += f"Key ID: {sbm.keyid}\n"
            text_content += f"SBM Type: {sbm.sbm_type}\n"
            text_content += f"Pamphlet No: {sbm.pamphlet_no}\n"
            text_content += f"State: {sbm.state}\n"
            text_content += f"District: {sbm.district}\n"
            text_content += f"Tahsil: {sbm.tahsil}\n"
            text_content += f"Pincode: {sbm.pincode}\n"
            text_content += f"Longitude: {sbm.longitude}\n"
            text_content += f"Latitude: {sbm.latitude}\n"
            text_content += f"SBM Inscription: {sbm.sbm_inscription}\n"
            text_content += f"Old Description: {sbm.old_description}\n"
            text_content += f"Revised Description: {sbm.revised_description}\n"
            text_content += f"Conduction of SBM: {sbm.conduction_of_sbm}\n"
            text_content += f"Conduction of Reference Pillar: {sbm.conduction_of_reference_pillar}\n"
            text_content += f"Image East: {sbm.image_east}\n"
            text_content += f"Image West: {sbm.image_west}\n"
            text_content += f"Image North: {sbm.image_north}\n"
            text_content += f"Image South: {sbm.image_south}\n"
            text_content += f"Authorised Person Name and Designation: {sbm.authorised_person_name_and_designation}\n"
            text_content += f"Authorised Person Contact No: {sbm.authorised_person_contactno}\n"
            text_content += f"Last Date of Visit: {sbm.last_date_of_vist}\n"
            text_content += f"Inspection Remark: {sbm.inspection_remark}\n"
            text_content += f"Update Time: {sbm.updatetime}\n"
            text_content += f"VALIDATION : {sbm.status}\n"
            text_content += f"GDC Username: {sbm.gdc_username}\n"
            text_content += "\n"  # Add a newline for separation between records
        
        response = HttpResponse(text_content, content_type='text/plain')
        response['Content-Disposition'] = 'attachment; filename="BenchmarkSbmdataBackup.txt"'
        return response
    

def oc_hpcl_cw(request):
    query = request.POST.get('searchdata', '')
    data = BenchmarkSbmdata.objects.using("database3").all()
    if query:
        data = data.filter(Q(state__icontains=query) | Q(sbm_type__icontains=query) | Q(district__icontains=query)| Q(conduction_of_sbm__icontains=query) | Q(conduction_of_reference_pillar__icontains=query) | Q(tahsil__icontains=query)|Q(keyid__icontains=query))
    
    context = {
        'data': data,
        
    }
    return render(request, 'grmdb/oc_hpcl_cw.html', context)


@csrf_exempt
def update_status(request):
    if request.method == 'POST':
        try:
            id = request.POST.get('id')
            status = request.POST.get('status')
            obj = BenchmarkSbmdata.objects.using("database3").get(id=id)
            obj.status = status
            obj.save()
            return JsonResponse({'status': 'success'})
        except BenchmarkSbmdata.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Object does not exist'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)


@csrf_exempt
def oc_sgwupdate_status(request):
    if request.method == 'POST':
        try:
            id = request.POST.get('id')
            status = request.POST.get('status')
            obj = BenchmarkGcpdata.objects.using("database3").get(id=id)
            obj.status = status
            obj.save()
            return JsonResponse({'status': 'success'})
        except BenchmarkGcpdata.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Object does not exist'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)

@csrf_exempt
def ic_dataupdate_status(request):
    if request.method == 'POST':
        try:
            id = request.POST.get('id')
            status = request.POST.get('status')
            obj = BenchmarkGtstation.objects.using("database3").get(id=id)
            obj.status = status
            obj.save()
            return JsonResponse({'status': 'success'})
        except BenchmarkGtstation.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Object does not exist'}, status=400)
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=400)
    
    # If not the specific user, handle appropriately or redirect
   
def oc_sgw(request):
    query = request.POST.get('searchdata', '')
    data = BenchmarkGcpdata.objects.using("database3").all()
    if query:
        data = data.filter(Q(state__icontains=query) | Q(gcp_name__icontains=query) | Q(district__icontains=query) | Q(conduction_of_gcp__icontains=query) | Q(tahsil__icontains=query)|Q(keyid__icontains=query))
    context = {
        'data':data
    }
    return render(request,'grmdb/oc_sgw.html',context)



def ic_datacenter(request):
    query = request.POST.get('searchdata', '')
    data = BenchmarkGtstation.objects.using("database3").all()
    if query:
        data = data.filter(Q(state__icontains=query) | Q(district__icontains=query) | Q(conduction_of_gtstation__icontains=query) |Q(keyid__icontains=query))
    context = {
        'data':data
    }
    return render(request,'grmdb/ic_data.html',context)



def oc_hpcl_log(request):
    keyid = request.POST.get('keyid')
    request.session['keyid'] = keyid
    data  = BenchmarkSbmdataBackup.objects.using("database3").filter(keyid=keyid)
    context = {
        'data':data
    }
    return render(request,'grmdb/logs_for_oc_hpcl.html',context)



def oc_sgw_log(request):
    keyid = request.POST.get('keyid')
    request.session['keyid'] = keyid
    data  = BenchmarkGcpdataBackup.objects.using("database3").filter(keyid=keyid)
    context = {
        'data':data
    }
    return render(request,'grmdb/logs_for_oc_sgw.html',context)




def ic_data_log(request):
    keyid = request.POST.get('keyid')
    request.session['keyid'] = keyid
    data  = BenchmarkGtstationBackup.objects.using("database3").filter(keyid=keyid)
    context = {
        'data':data
    }
    return render(request,'grmdb/logs_for_ic_data.html',context)