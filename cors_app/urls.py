
from django.urls import path
from.import views

urlpatterns = [
    path('',views.login_views,name='login'),
    path('signup',views.signup,name='signup'),
    path('logout_view',views.logout_view,name='logout_view'),
    path('vender_dashboard',views.vender_dashboard,name='vender_dashboard'),
    # path('vendor_data',views.vendor_data,name='vendor_data'),
    path('control_centre_dashboard',views.control_centre_dashboard,name='control_centre_dashboard'),
    path('gdc_dashboard',views.gdc_dashboard,name='gdc_dashboard'),
    path('controlcentreform',views.controlcentreform,name='controlcentreform'),
    path('edit/<str:corsid>/', views.edit_controlcentre, name='edit_controlcentre'),
    path('edit_vendor/<str:corsid>/',views.edit_vendor_data, name='edit_vendor_data'),
    path('vendor_datalog',views.vendor_datalog, name='vendor_datalog'),
    path('edit_gdc/<str:corsid>/',views.edit_gdc_data, name='edit_gdc_data'),
    path('corsadmin_login',views.corsadmin_login, name='corsadmin_login'),
    path('corsadmin_dashboard',views.corsadmin_dashboard, name='corsadmin_dashboard'),
    path('vandor_admindashboard',views.vandor_admindashboard, name='vandor_admindashboard'),
    path('gdc_admindashboard',views.gdc_admindashboard, name='gdc_admindashboard'),
    path('gdc_admindashboard',views.gdc_admindashboard, name='gdc_admindashboard'),
    path('control_centerlog',views.control_centerlog, name='control_centerlog'),
    path('gdc_log',views.gdc_log, name='gdc_log'),
    path('gdc_logdownload_text_file', views.gdc_logdownload_text_file, name='download_text_file'),
    path('control_centerlogdownload', views.control_centerlogdownload, name='control_centerlogdownload'),
    path('vendor_datatext_file', views.vendor_datatext_file, name='vendor_datatext_file'),
    path('download_csv', views.vendardownload_csv, name='download_csv'),
    path('gdcdownload_csv', views.gdcdownload_csv, name='gdcdownload_csv'),
    path('control_centre_dashboard_csv', views.control_centre_dashboard_csv, name='control_centre_dashboard_csv'),
    path('approve_users', views.approve_users, name='approve_users'),
    path('forgot-password', views.forgot_password, name='forgot_password'),



    ####################################################kycurl#####################################################
    path('kyc',views.plot_data,name='plot_data'),
    # path('display_Images/',views.display_Images,name='display_Images'),
    path('generatepdf', views.generate_pdf, name='generate_pdf'),
    path('load-districts', views.load_districts, name='load_districts'),
    # path('delete-all-states/', views.delete_all_states, name='delete_all_states'),




    ################################################################ GRMDB #################################################

    path('grmdb',views.grmdblogin_view,name='grmdblogin_view'),
    path('signup',views.signup,name='signup'),
    path('gtstationdashboard',views.gtstationdashboard,name='gtstationdashboard'),
    path('gcpdashboard',views.gcpdashboard,name='gcpdashboard'),
    path('sbmdashboard',views.sbmdashboard,name='sbmdashboard'),
    path('logout_view',views.logout_view,name='logout_view'),
    path('edit_gcpdata/<str:id>/',views.edit_gcpdata, name='edit_gcpdata'),
    path('edit_gtstationdata/<str:id>/',views.edit_gtstationdata, name='edit_gtstationdata'),
    path('edit_sbmdata/<str:id>/',views.edit_sbmdata, name='edit_sbmdata'),
    path('addsbm',views.addsbm, name='addsbm'),
    path('admin_login',views.admin_login, name='admin_login'),
    path('admin_dashboard',views.admin_dashboard, name='admin_dashboard'),
    path('admin_dashboardgcpdata',views.admin_dashboardgcpdata, name='admin_dashboardgcpdata'),
    path('admin_dashboardSBMdata',views.admin_dashboardSBMdata, name='admin_dashboardSBMdata'),
    path('gcp_log',views.gcp_log, name='gcp_log'),
    path('gtstation_log',views.gtstation_log, name='gtstation_log'),
    path('sbm_log',views.sbm_log, name='sbm_log'),
    path('gtstationdownload_csv',views.gtstationdownload_csv, name='gtstationdownload_csv'),
    path('download_gcp_data_csv',views.download_gcp_data_csv, name='download_gcp_data_csv'),
    path('download_sbm_data_csv',views.download_sbm_data_csv, name='download_sbm_data_csv'),
    path('benchmark_sbmdata_download',views.benchmark_sbmdata_download, name='benchmark_sbmdata_download'),
    path('benchmark_gcpdata_download',views.benchmark_gcpdata_download, name='benchmark_gcpdata_download'),
    path('benchmark_gtstation_download',views.benchmark_gtstation_download, name='benchmark_gtstation_download'),
    path('addsbm',views.addsbm, name='addsbm'),
    path('addgtstation',views.addgtstation, name='addgtstation'),
    path('oc_hpcl_cw',views.oc_hpcl_cw, name='oc_hpcl_cw'),
    path('ic_datacenter',views.ic_datacenter, name='ic_datacenter'),
    path('update_status/', views.update_status, name='update_status'),
    path('oc_sgwupdate_status/', views.oc_sgwupdate_status, name='oc_sgwupdate_status'),
    path('ic_dataupdate_status/', views.ic_dataupdate_status, name='ic_dataupdate_status'),
    path('oc_sgw',views.oc_sgw, name='oc_sgw'),
    path('oc_hpcl_log',views.oc_hpcl_log, name='oc_hpcl_log'),
    path('oc_sgw_log',views.oc_sgw_log, name='oc_sgw_log'),
    path('ic_data_log',views.ic_data_log, name='ic_data_log'),
    path('grmdbforgot_password', views.grmdbforgot_password, name='grmdbforgot_password'),
    
]
