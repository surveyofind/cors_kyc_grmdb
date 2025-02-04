# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models


class AuthGroup(models.Model):
    name = models.CharField(unique=True, max_length=150)

    class Meta:
        managed = False
        db_table = 'auth_group'


class AuthGroupPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)
    permission = models.ForeignKey('AuthPermission', models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_group_permissions'
        unique_together = (('group', 'permission'),)


class AuthPermission(models.Model):
    name = models.CharField(max_length=255)
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING)
    codename = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'auth_permission'
        unique_together = (('content_type', 'codename'),)


class AuthUser(models.Model):
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'auth_user'


class AuthUserGroups(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    group = models.ForeignKey(AuthGroup, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_groups'
        unique_together = (('user', 'group'),)


class AuthUserUserPermissions(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)
    permission = models.ForeignKey(AuthPermission, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'auth_user_user_permissions'
        unique_together = (('user', 'permission'),)


class BenchmarkGcpdata(models.Model):
    id = models.BigAutoField(primary_key=True)
    gcp_name = models.CharField(max_length=200, blank=True, null=True)
    pamphlet_no = models.CharField(max_length=200, blank=True, null=True)
    state = models.CharField(max_length=200, blank=True, null=True)
    district = models.CharField(max_length=200, blank=True, null=True)
    tahsil = models.CharField(max_length=200, blank=True, null=True)
    pincode = models.CharField(max_length=200, blank=True, null=True)
    longitude = models.CharField(max_length=200, blank=True, null=True)
    latitude = models.CharField(max_length=200, blank=True, null=True)
    gcp_on_pillar = models.CharField(max_length=500, blank=True, null=True)
    old_description = models.TextField(blank=True, null=True)
    revised_description = models.TextField(blank=True, null=True)
    conduction_of_gcp = models.CharField(max_length=500, blank=True, null=True)
    authorised_person_name_and_designation = models.CharField(max_length=500, blank=True, null=True)
    authorised_person_contactno = models.CharField(max_length=500, blank=True, null=True)
    last_date_of_vist = models.CharField(max_length=500, blank=True, null=True)
    inspection_remark = models.CharField(max_length=500, blank=True, null=True)
    gdc_username = models.TextField(blank=True, null=True)
    ellipsoidheight = models.CharField(max_length=200, blank=True, null=True)
    pid = models.CharField(max_length=500, blank=True, null=True)
    image_east = models.CharField(max_length=100, blank=True, null=True)
    image_north = models.CharField(max_length=100, blank=True, null=True)
    image_south = models.CharField(max_length=100, blank=True, null=True)
    image_west = models.CharField(max_length=100, blank=True, null=True)
    keyid = models.CharField(max_length=200, blank=True, null=True)
    updatetime = models.CharField(max_length=500, blank=True, null=True)
    gravityvalue = models.CharField(max_length=200, blank=True, null=True)
    orthometrichight = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'benchmark_gcpdata'


class BenchmarkGcpdataBackup(models.Model):
    keyid = models.CharField(max_length=200, blank=True, null=True)
    gcp_name = models.CharField(max_length=200, blank=True, null=True)
    pamphlet_no = models.CharField(max_length=200, blank=True, null=True)
    state = models.CharField(max_length=200, blank=True, null=True)
    district = models.CharField(max_length=200, blank=True, null=True)
    tahsil = models.CharField(max_length=200, blank=True, null=True)
    pincode = models.CharField(max_length=200, blank=True, null=True)
    longitude = models.CharField(max_length=200, blank=True, null=True)
    latitude = models.CharField(max_length=200, blank=True, null=True)
    ellipsoidheight = models.CharField(max_length=200, blank=True, null=True)
    orthometrichight = models.CharField(max_length=200, blank=True, null=True)
    gravityvalue = models.CharField(max_length=200, blank=True, null=True)
    gcp_on_pillar = models.CharField(max_length=500, blank=True, null=True)
    old_description = models.TextField(blank=True, null=True)
    revised_description = models.TextField(blank=True, null=True)
    conduction_of_gcp = models.CharField(max_length=500, blank=True, null=True)
    image_east = models.CharField(max_length=500, blank=True, null=True)
    image_west = models.CharField(max_length=500, blank=True, null=True)
    image_north = models.CharField(max_length=500, blank=True, null=True)
    image_south = models.CharField(max_length=500, blank=True, null=True)
    authorised_person_name_and_designation = models.CharField(max_length=500, blank=True, null=True)
    authorised_person_contactno = models.CharField(max_length=500, blank=True, null=True)
    last_date_of_vist = models.CharField(max_length=500, blank=True, null=True)
    inspection_remark = models.CharField(max_length=500, blank=True, null=True)
    updatetime = models.CharField(max_length=500, blank=True, null=True)
    gdc_username = models.TextField(blank=True, null=True)
    pid = models.CharField(max_length=500, blank=True, null=True)
    id = models.CharField(max_length=45, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'benchmark_gcpdata_backup'


class BenchmarkGtstation(models.Model):
    id = models.BigAutoField(primary_key=True)
    gtstation_name = models.CharField(max_length=200, blank=True, null=True)
    pamphlet_no = models.CharField(max_length=200, blank=True, null=True)
    state = models.CharField(max_length=200, blank=True, null=True)
    district = models.CharField(max_length=200, blank=True, null=True)
    tahsil = models.CharField(max_length=200, blank=True, null=True)
    pincode = models.CharField(max_length=200, blank=True, null=True)
    longitude = models.CharField(max_length=200, blank=True, null=True)
    latitude = models.CharField(max_length=200, blank=True, null=True)
    gt_station_inscription = models.CharField(max_length=200, blank=True, null=True)
    ellipsoidheight = models.CharField(max_length=200, blank=True, null=True)
    old_description = models.TextField(blank=True, null=True)
    revised_description = models.TextField(blank=True, null=True)
    conduction_of_gtstation = models.CharField(max_length=500, blank=True, null=True)
    image_east = models.CharField(max_length=100, blank=True, null=True)
    authorised_person_name_and_designation = models.CharField(max_length=500, blank=True, null=True)
    authorised_person_contactno = models.CharField(max_length=500, blank=True, null=True)
    last_date_of_vist = models.CharField(max_length=500, blank=True, null=True)
    inspection_remark = models.CharField(max_length=500, blank=True, null=True)
    gdc_username = models.TextField(blank=True, null=True)
    image_north = models.CharField(max_length=100, blank=True, null=True)
    image_south = models.CharField(max_length=100, blank=True, null=True)
    image_west = models.CharField(max_length=100, blank=True, null=True)
    keyid = models.CharField(max_length=200, blank=True, null=True)
    updatetime = models.CharField(max_length=500, blank=True, null=True)
    gravityvalue = models.CharField(max_length=200, blank=True, null=True)
    orthometrichight = models.CharField(max_length=200, blank=True, null=True)
    triangulatedheight = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'benchmark_gtstation'


class BenchmarkGtstationBackup(models.Model):
    keyid = models.CharField(max_length=200, blank=True, null=True)
    gtstation_name = models.CharField(max_length=200, blank=True, null=True)
    pamphlet_no = models.CharField(max_length=200, blank=True, null=True)
    state = models.CharField(max_length=200, blank=True, null=True)
    ellipsoidheight = models.CharField(max_length=200, blank=True, null=True)
    triangulatedheight = models.CharField(max_length=200, blank=True, null=True)
    orthometrichight = models.CharField(max_length=200, blank=True, null=True)
    gravityvalue = models.CharField(max_length=200, blank=True, null=True)
    district = models.CharField(max_length=200, blank=True, null=True)
    tahsil = models.CharField(max_length=200, blank=True, null=True)
    pincode = models.CharField(max_length=200, blank=True, null=True)
    longitude = models.CharField(max_length=200, blank=True, null=True)
    latitude = models.CharField(max_length=200, blank=True, null=True)
    gt_station_inscription = models.CharField(max_length=200, blank=True, null=True)
    old_description = models.TextField(blank=True, null=True)
    revised_description = models.TextField(blank=True, null=True)
    conduction_of_gtstation = models.CharField(max_length=500, blank=True, null=True)
    image_east = models.CharField(max_length=500, blank=True, null=True)
    image_west = models.CharField(max_length=500, blank=True, null=True)
    image_north = models.CharField(max_length=500, blank=True, null=True)
    image_south = models.CharField(max_length=500, blank=True, null=True)
    authorised_person_name_and_designation = models.CharField(max_length=500, blank=True, null=True)
    authorised_person_contactno = models.CharField(max_length=500, blank=True, null=True)
    last_date_of_vist = models.CharField(max_length=500, blank=True, null=True)
    inspection_remark = models.CharField(max_length=500, blank=True, null=True)
    updatetime = models.CharField(max_length=500, blank=True, null=True)
    gdc_username = models.TextField(blank=True, null=True)
    id = models.CharField(max_length=45, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'benchmark_gtstation_backup'


class BenchmarkSbmdata(models.Model):
    id = models.BigAutoField(primary_key=True)
    sbm_type = models.CharField(max_length=200, blank=True, null=True)
    pamphlet_no = models.CharField(max_length=200, blank=True, null=True)
    state = models.CharField(max_length=200, blank=True, null=True)
    district = models.CharField(max_length=200, blank=True, null=True)
    tahsil = models.CharField(max_length=200, blank=True, null=True)
    pincode = models.CharField(max_length=200, blank=True, null=True)
    longitude = models.CharField(max_length=200, blank=True, null=True)
    latitude = models.CharField(max_length=200, blank=True, null=True)
    sbm_inscription = models.CharField(max_length=500, blank=True, null=True)
    old_description = models.CharField(max_length=500, blank=True, null=True)
    revised_description = models.CharField(max_length=500, blank=True, null=True)
    conduction_of_sbm = models.CharField(max_length=500, blank=True, null=True)
    conduction_of_reference_pillar = models.CharField(max_length=500, blank=True, null=True)
    image_east = models.CharField(max_length=100, blank=True, null=True)
    authorised_person_name_and_designation = models.CharField(max_length=500, blank=True, null=True)
    authorised_person_contactno = models.CharField(max_length=500, blank=True, null=True)
    last_date_of_vist = models.CharField(max_length=500, blank=True, null=True)
    inspection_remark = models.CharField(max_length=500, blank=True, null=True)
    gdc_username = models.TextField(blank=True, null=True)
    image_north = models.CharField(max_length=100, blank=True, null=True)
    image_south = models.CharField(max_length=100, blank=True, null=True)
    image_west = models.CharField(max_length=100, blank=True, null=True)
    keyid = models.CharField(max_length=200, blank=True, null=True)
    updatetime = models.CharField(max_length=500, blank=True, null=True)
    status = models.CharField(max_length=20)

    class Meta:
        managed = False
        db_table = 'benchmark_sbmdata'


class BenchmarkSbmdataBackup(models.Model):
    keyid = models.CharField(max_length=200, blank=True, null=True)
    sbm_type = models.CharField(max_length=200, blank=True, null=True)
    pamphlet_no = models.CharField(max_length=200, blank=True, null=True)
    state = models.CharField(max_length=200, blank=True, null=True)
    district = models.CharField(max_length=200, blank=True, null=True)
    tahsil = models.CharField(max_length=200, blank=True, null=True)
    pincode = models.CharField(max_length=200, blank=True, null=True)
    longitude = models.CharField(max_length=200, blank=True, null=True)
    latitude = models.CharField(max_length=200, blank=True, null=True)
    sbm_inscription = models.CharField(max_length=500, blank=True, null=True)
    old_description = models.CharField(max_length=500, blank=True, null=True)
    revised_description = models.CharField(max_length=500, blank=True, null=True)
    conduction_of_sbm = models.CharField(max_length=500, blank=True, null=True)
    conduction_of_reference_pillar = models.CharField(max_length=500, blank=True, null=True)
    image_east = models.CharField(max_length=500, blank=True, null=True)
    image_west = models.CharField(max_length=500, blank=True, null=True)
    image_north = models.CharField(max_length=500, blank=True, null=True)
    image_south = models.CharField(max_length=500, blank=True, null=True)
    authorised_person_name_and_designation = models.CharField(max_length=500, blank=True, null=True)
    authorised_person_contactno = models.CharField(max_length=500, blank=True, null=True)
    last_date_of_vist = models.CharField(max_length=500, blank=True, null=True)
    inspection_remark = models.CharField(max_length=500, blank=True, null=True)
    updatetime = models.CharField(max_length=500, blank=True, null=True)
    gdc_username = models.TextField(blank=True, null=True)
    id = models.CharField(max_length=45, blank=True, null=True)
    status = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'benchmark_sbmdata_backup'


class BenchmarkUser(models.Model):
    id = models.BigAutoField(primary_key=True)
    password = models.CharField(max_length=128)
    last_login = models.DateTimeField(blank=True, null=True)
    is_superuser = models.IntegerField()
    username = models.CharField(unique=True, max_length=150)
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.CharField(max_length=254)
    is_staff = models.IntegerField()
    is_active = models.IntegerField()
    date_joined = models.DateTimeField()
    gdc = models.IntegerField()
    cors = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'benchmark_user'


class DjangoAdminLog(models.Model):
    action_time = models.DateTimeField()
    object_id = models.TextField(blank=True, null=True)
    object_repr = models.CharField(max_length=200)
    action_flag = models.PositiveSmallIntegerField()
    change_message = models.TextField()
    content_type = models.ForeignKey('DjangoContentType', models.DO_NOTHING, blank=True, null=True)
    user = models.ForeignKey(AuthUser, models.DO_NOTHING)

    class Meta:
        managed = False
        db_table = 'django_admin_log'


class DjangoContentType(models.Model):
    app_label = models.CharField(max_length=100)
    model = models.CharField(max_length=100)

    class Meta:
        managed = False
        db_table = 'django_content_type'
        unique_together = (('app_label', 'model'),)


class DjangoMigrations(models.Model):
    id = models.BigAutoField(primary_key=True)
    app = models.CharField(max_length=255)
    name = models.CharField(max_length=255)
    applied = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_migrations'


class DjangoSession(models.Model):
    session_key = models.CharField(primary_key=True, max_length=40)
    session_data = models.TextField()
    expire_date = models.DateTimeField()

    class Meta:
        managed = False
        db_table = 'django_session'
