#!/usr/bin/python

import sys
import boto
import boto.ec2
import boto.cloudformation
import boto.s3
from boto.s3.key import Key
import os
import re
import time
import logging
import json
from boto.exception import S3ResponseError
import distutils.util


def parse_args(args):
    logger = set_up_logging()
    arg_dict = {}
    for k, v in args.__dict__.items():
        arg_dict[k] = v
    return (arg_dict, logger)


def get_cloudformation_stack(stack_name, region):
    cfn_conn = boto.cloudformation.connect_to_region(region)
    all_stacks = cfn_conn.describe_stacks()
    try:
        return [s for s in all_stacks if stack_name.lower() == s.stack_name.lower()][0]
    except:
        return None


def check_timeout(timeout):
    if int(time.time()) > timeout:
        raise Exception('This operation timed out.')
    else:
        return True


def monitor_stack_status_to_completion(stack, desired_status, logger, max_wait=300):
    timeout = 10800 + int(time.time())
    wait_time = 2
    tries = 0
    time.sleep(wait_time)
    stack.update()
    while stack.stack_status != desired_status and check_timeout(timeout):
        if any(x in stack.stack_status for x in ['ROLLBACK', 'FAILED']):
            logger.info('Stack failed the update. Rolling back.')
            logger.error("\n".join(
                [str((str(e.timestamp), e, e.resource_status_reason)) for e in stack.describe_events()[0:10]]))
            if desired_status == 'UPDATE_COMPLETE':
                raise Exception(
                    'Stack update failed! Leaving the stack as is.')
            if desired_status == 'CREATE_COMPLETE':
                # we want to delete the stack after it finishes rollback
                stack.update()
                logger.info(
                    'Creation failed so the stack will be deleted when rollback finishes')
                while stack.stack_status != 'ROLLBACK_COMPLETE' and check_timeout(timeout):
                    if stack.stack_status == 'DELETE_COMPLETE':
                        raise Exception(
                            'Stack was deleted by some other action.')
                    logger.info("Stack status is currently %s. Waiting %s seconds and checking again..." % (
                        stack.stack_status, '60'))
                    time.sleep(60)
                    stack.update()
                stack.delete()
                raise Exception(
                    'Stack creation failed! Final deletion has started.')
        if (tries * wait_time + wait_time) < max_wait:
            wait_time = tries * wait_time + wait_time
        else:
            wait_time = max_wait
        logger.info("Stack status is currently %s. Waiting %s seconds and checking again..." % (
            stack.stack_status, str(wait_time)))
        time.sleep(wait_time)
        stack.update()
        tries += 1
    logger.info('Update was successful!')
    return True


def set_all_s3_bucket_tags(region, stack_param_dict, logger):
    s3_conn = boto.s3.connect_to_region(region)
    s3_bucket_name = s3_conn.get_bucket(stack_param_dict['KeyValueBucket'])
    set_s3_bucket_tags(s3_bucket_name, {'OWNER': stack_param_dict[
                       'ChefEnvironment'], 'UPDATED': get_s3_bucket_tags(s3_bucket_name, logger).get('UPDATED')})


def bool_filter(value):
    if value == 'false':
        return False
    elif value == 'true':
        return True
    else:
        return value


def y_n_filter(value):
    if value:
        return 'Yes'
    else:
        return 'No'


def set_up_logging():
    logger = logging.getLogger(__name__)
    ch = logging.StreamHandler(sys.stdout)
    ch.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(logging.INFO)
    return logger


def get_s3_bucket_tags(bucket, logger):
    s3_tag_dict = dict()
    try:
        tag_set_list = bucket.get_tags()
        tag_set = tag_set_list[0]
        for tag in tag_set:
            s3_tag_dict[tag.key] = tag.value

    except S3ResponseError as e:
        logger.warning(e)
        pass
    return s3_tag_dict


def set_s3_bucket_tags(bucket, tag_dict):
    tagset = boto.s3.tagging.TagSet()
    for k, v in tag_dict.items():
        tagset.add_tag(k, v)
    tag = boto.s3.tagging.Tags()
    tag.add_tag_set(tagset)
    return bucket.set_tags(tag)


def get_all_unowned_buckets(region, logger):
    s3_conn = boto.s3.connect_to_region(region)
    all_kv_buckets = [b for b in s3_conn.get_all_buckets() if re.match(
        "[0-9]{2,12}%s-backup-databag" % region.split('-')[1], b.name)]
    return [b for b in all_kv_buckets if re.match('BACKUP-[0-9a-zA-Z]{6}', get_s3_bucket_tags(b, logger).get('OWNER'))]


# if spinning up an environment for DR, second arg should be set to 0
def get_last_updated_bucket(bucket_list, newness, logger):
    return sorted(bucket_list, key=lambda b: get_s3_bucket_tags(b, logger).get('UPDATED'), reverse=True)[newness]


def get_chef_environment_document(chef_environment):
    document = json.load(open(chef_environment_path(chef_environment)))
    return document


def chef_environment_path(environment_name):
    return '%s/environments/%s.json' % (os.getenv('WORKSPACE'), environment_name)


def del_leftover_route53_entries(prefix, zone_name='dreambox.com'):
    r53_conn = boto.connect_route53()
    zone = r53_conn.get_zone(zone_name)
    r53sets = r53_conn.get_all_rrsets(zone.id)

    if 'stage' in prefix.lower():
        for r53set in r53sets:
            if r53set.name.lower().startswith(prefix.lower()) and r53set.type == 'CNAME':
                print(
                    'Found matching record for CNAME %s. Will delete that now.' % r53set.name)
                result = zone.delete_cname(r53set.name)
                print(result)
    else:
        print(
            'Environment is not a stage environment, skipping route53 cleanup')
    return True


def get_latest_dataset_dict(region, newness, logger):
    latest_bucket = get_last_updated_bucket(
        get_all_unowned_buckets(region, logger), newness)
    base_name = latest_bucket.name.split('-')[0]
    param_dict = get_dataset_dict(base_name)
    return param_dict


def get_dataset_dict(base_name):
    param_dict = {}
    param_dict['KeyValueBucket'] = '%s-backup-databag' % base_name
    for x in ['Api', 'Extract', 'Galactus', 'Magneto', 'Play']:
        param_dict['%sSnapshot' % x] = '%sbackup-%s' % (x.lower(), base_name)
    return param_dict


def upload_template_to_s3(stack_name, current_template, bucket_name='dreambox-ops'):
    s3_conn = boto.s3.connect_to_region('us-east-1')
    bucket = s3_conn.get_bucket(bucket_name)
    path = 'cfn_temp/%s/%s.json' % (stack_name, str(int(time.time())))
    template_key = Key(bucket)
    template_key.key = path
    template_key.set_contents_from_string(current_template)
    template_url = 'https://s3.amazonaws.com/%s/%s' % (bucket.name, path)
    return template_url


def update_stack_params(stack, stack_param_dict, current_template, bucket_name='dreambox-ops'):
    if current_template.startswith('https://s3'):
        template_url = current_template
    else:
        template_url = upload_template_to_s3(
            stack.stack_name, current_template, bucket_name)
    return stack.connection.update_stack(stack.stack_name, template_url=template_url, parameters=stack_param_dict.items(), capabilities=['CAPABILITY_IAM'])


def yes_or_no_question(question, logger):
    try:
        response = input('%s [y/n]: ' % question)
        return distutils.util.strtobool(response)
    except Exception as e:
        logger.critical("Value was not y or n! Exiting. ")
        logger.critical(e)
        exit(1)


def get_all_apps_metadata():
    app_dict = {
        'account': {
            'version_locations': {
                '/opt/account': ('account', 'version', 'number'), },  # ideally we could check ['magneto']['version']['type'] also
            'service': 'tomcat7',
            'roles': ['account'],
            },
        'api': {
            'version_locations': {
                '/home/mongrel/Api/': ('api', 'subversion', 'revision'), },  # also here it would be nice to test branch (if not move to s3)
            'service': 'api',
            'roles': ['PRODUCTION_api_cron_server', 'api_app', 'PRODUCTION_api_server', 'PRODUCTION_product_admin_server'],
        },
        'dreamboxcom': {
            'version_locations': {
                '/home/mongrel/DreamBoxCom/current': ('api', 'subversion', 'revision'), },
            'service': 'dreamboxcom',
            'roles': ['dreamboxcom_app', 'PRODUCTION_dreamboxcom_server'],
        },
        'galactus': {
            'version_locations': {
                '/opt/galactus': ('galactus', 'version', 'number'), },
            'service': 'tomcat7',
            'roles': ['galactus'],
        },
        'magneto': {
            'version_locations': {
                '/opt/provision': ('magneto', 'version', 'number'), },
            'service': 'tomcat7',
            'roles': ['magneto'],
        },
        'product': {
            'version_locations': {
                '/home/mongrel/Product/current': ('product', 'build_key'),
                '/home/mongrel/assets/lessons/current': ('lessons', 'key'),
            },
            'service': 'product',
            'roles': ['PRODUCTION_product_app_server', 'PRODUCTION_product_rpc_server', 'PRODUCTION_product_reports_server', 'play-admin', 'cron_worker', 'play_app', 'cron_standalone'],
        },
        'product_admin': {
            'version_locations': {
                '/home/mongrel/Product/current': ('product', 'build_key'), },  # lessons are unimportant on admin nodes
            'service': 'product_admin',
            'roles': ['PRODUCTION_product_app_server', 'PRODUCTION_product_rpc_server', 'PRODUCTION_product_reports_server', 'play-admin', 'cron_worker', 'play_app', 'cron_standalone'],
        },
    }
    return app_dict
