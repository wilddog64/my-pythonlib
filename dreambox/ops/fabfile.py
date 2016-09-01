from fabric.api import run
from fabric.api import settings
import time
import logging
import sys

## setup logging
logger = logging.getLogger(__name__)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
logger.setLevel(logging.INFO)

RVM_ENV = '/usr/local/rvm/environments/ree-1.8.7-2012.02'

class FabricTestException(Exception):
    pass


def thread_status_check_with_session():
    run('curl http://localhost:8081/thread_status_check_with_session')


def verify_chef_status():
    run('if ! sudo service chef-client status; then sudo service chef-client start ; fi')


def wake_chef_client():
    run('sudo service chef-client wake')


def verify_node_running_product_revision(product_revision):
    link_path = '/home/mongrel/Product/current'
    result = run('if sudo file %s | grep -q releases/%s ; then echo passed; else echo failed; fi' % (link_path, product_revision))
    return result


def verify_node_running_api_revision(api_revision):
    link_path = '/home/mongrel/Api/current'
    result = run('if sudo file %s | grep -q releases/%s ; then echo passed; else echo failed; fi' % (link_path, api_revision))
    return result


def verify_node_running_dataagg_url(dataagg_url):
    dataagg_url = dataagg_url.rstrip('/')
    link_path = '/home/mongrel/DataAgg/current'
    result = run('if sudo svn info `sudo readlink %s` | grep -E ^URL: | grep -q %s ; then echo passed; else echo failed; fi' % (link_path, dataagg_url))
    return result

def verify_node_running_api_url(api_url):
    api_url = api_url.rstrip('/')
    link_path = '/home/mongrel/Api/current'
    result = run('if sudo svn info `sudo readlink %s` | grep -E ^URL: | grep -q %s ; then echo passed; else echo failed; fi' % (link_path, api_url))
    return result


def verify_node_running_lessons_revision(lessons_revision):
    link_path = '/home/mongrel/assets/lessons/current'
    # we may need to convert other verification functions to use this method as its more robust
    result = run('if $(sudo file %s | grep %s -q) && [ $(sudo ls %s | wc -l) -ne 0 ] ; then echo passed; else echo failed; fi' % (link_path, lessons_revision, link_path))
    return result


def verify_node_running_dreamboxcom_revision(dreamboxcom_revision):
    link_path = '/home/mongrel/DreamBoxCom/current'
    result = run('if sudo file %s | grep -q releases/%s ; then echo passed; else echo failed; fi' % (link_path, dreamboxcom_revision))
    return result


def is_product_maintenance_mode_enabled():
    result = run('if sudo test -e /home/mongrel/Product/current/public/sitedown/maintenance.html ; then echo true ; else echo false ; fi')
    return_val = True
    if 'false' in result:
        return_val = False
    return return_val


def product_enable_maintenance_mode():
    maintenance_mode_file = '/home/mongrel/Product/current/public/sitedown/maintenance.html'
    maintenance_mode_file_json = '/home/mongrel/Product/current/public/sitedown/maintenance.json'
    run('sudo cp %(maintenance_mode_file)s.disabled %(maintenance_mode_file)s' % {'maintenance_mode_file' : maintenance_mode_file} )
    run('sudo cp %(maintenance_mode_file)s.disabled %(maintenance_mode_file)s' % {'maintenance_mode_file' : maintenance_mode_file_json} )


def product_disable_maintenance_mode():
    maintenance_mode_file = '/home/mongrel/Product/current/public/sitedown/maintenance.html'
    maintenance_mode_file_json = '/home/mongrel/Product/current/public/sitedown/maintenance.json'
    run('sudo rm -f %s' % maintenance_mode_file)
    run('sudo rm -f %s' % maintenance_mode_file_json)


def product_get_config_value(config_key):
    result = run('''sudo bash -l -c "cd /home/mongrel/Product/current ; source %s ; export RAILS_ENV=production ; bundle exec rails runner 'puts Setup.get_config(\\\\\"%s\\\\\") ' " ''' % (RVM_ENV, config_key ) )
    return result


def product_set_config_value(config_key, config_value):
    run('''sudo bash -l -c "cd /home/mongrel/Product/current ; source %s ; export RAILS_ENV=production ; bundle exec rails runner 'Setup.set_config(\\\\\"%s\\\\\", \\\\\"%s\\\\\") ' " ''' % (RVM_ENV, config_key, str(config_value)) )
    if product_get_config_value(config_key) == str(config_value):
        logger.info("New value for config key %s is %s" % (config_key, config_value))
        return True
    else:
        return False


def product_increment_config_value(config_key):
    logger.info("Old value for config key %s is %s" % (config_key, product_get_config_value(config_key)))
    new_val = str(int(time.time()))
    product_set_config_value(config_key, new_val)
    return True


def product_migrate():
    run('sudo bash -l -c "cd /home/mongrel/Product/current ; source %s ; env RAILS_ENV=production bundle exec rake db:migrate"' % RVM_ENV)


def api_migrate():
    run('sudo bash -l -c "cd /home/mongrel/Api/current ; source %s ; env RAILS_ENV=production bundle exec rake db:migrate"' % RVM_ENV)


def setup_sequencing():
    run('sudo bash -l -c "cd /home/mongrel/Product/current ; source %s ; env RAILS_ENV=production bundle exec rails runner SetupSequences.setup_sequencing"' % RVM_ENV)


def import_email_templates():
    run('sudo bash -l -c "cd /home/mongrel/Product/current ; source %s ; env RAILS_ENV=production bundle exec rails runner Templates.import"' % RVM_ENV)


def import_all_intermediate_items():
    run('sudo bash -l -c "cd /home/mongrel/Product/current ; source %s ; env RAILS_ENV=production bundle exec rake import:all_intermediate_items"' % RVM_ENV)


def import_lesson_exclusion():
    run('sudo bash -l -c "cd /home/mongrel/Product/current ; source %s ; env RAILS_ENV=production bundle exec rake import:import_lesson_exclusion"' % RVM_ENV)


def import_client_bundles():
    run('sudo bash -l -c "cd /home/mongrel/Product/current ; source %s ; env RAILS_ENV=production bundle exec rake import:client_bundles"' % RVM_ENV)


def calc_initial_placement():
    run('sudo bash -l -c "cd /home/mongrel/Product/current ; source %s ; env RAILS_ENV=production bundle exec rake initial_placement:calc"' % RVM_ENV)


def set_approval_status(bundle_id, status):
    run('sudo bash -l -c "cd /home/mongrel/Product/current ; source %s ; env RAILS_ENV=production bundle exec rake client_bundle_admin:set_approval_status bundle_id=%s status=%s"' % (RVM_ENV, bundle_id, status))


def create_dynamo_tables():
    run('sudo bash -l -c "cd /home/mongrel/Product/current ; source %s ; env RAILS_ENV=production bundle exec rake aws:dynamo:create_key_value_storage"' % RVM_ENV)


def product_reload():
    run('sudo service product reload')


def product_admin_reload():
    run('sudo service product_admin reload')


def dataagg_reload():
    run('sudo service dataagg reload')


def api_reload():
    run('sudo service api reload')


def dreamboxcom_reload():
    run('sudo service dreamboxcom reload')


def restart_tomcat():
    run('sudo service tomcat7 restart')


def stop_tomcat():
    run('sudo service tomcat7 stop')


def umount_vol(mount_point):
    result = run('if mount | grep %s -q; then sudo umount %s; else echo "no_mount"; fi' % (mount_point, mount_point))
    return result


def mount_vol(attach_point, mount_point):
    result = run('sudo mount -t xfs %s %s' % (attach_point, mount_point))
    return result


def dump_db_and_put_in_s3(user, passwd, host, database, s3_path):
    run('mysqldump -u%s -p%s -h%s --databases %s > %s.sql' % (user, passwd, host, database, database))
    result = run('aws s3 cp %s.sql s3://%s/%s_%s.sql' % (database, s3_path, database, str(int(time.time())) ) )
    return result
