import boto3
import click

sess = boto3.session
ec2_sess = sess.boto3.resource('ec2')

def filter_instances(project):
        instances=[]

        if project:
            filters = [{'Name':'tag:Project','Values':[project]}]
            instances = ec2_sess.instances.filter(Filters=filters)
        else:
            instances = ec2_sess.instances.all()

        return instances

@click.group()
def instances():
    """Commands for instances"""

@instances.command('list')
@click.option('--project',default=None,
    help="Only instances for Project (tag Project:<name>)")

def list_instances(project):
        "List EC2 instances"
        instances=filter_instances(project)

        for k in instances:
            tags = { t['Key']:t['Value'] for t in k.tags or [] }

            print (','.join((
                k.id,
                k.instance_type,
                k.placement['AvailabilityZone'],
                k.state['Name'],
                k.public_dns_name,
                tags.get('Project', '<no project>')
                )))
        return
@instances.command('stop')
@click.option('--project', default=None, help='Only instances for Project')

def stop_instances(project):
    "Stop Ec2 instances"

    instances=filter_instances(project)

    for i in instances:
        print ('stopping {0}...' .format(i.id))
        i.stop()
    return

@instances.command('start')
@click.option('--project', default=None, help='Only instances for Project')

def stop_instances(project):
    "Start Ec2 instances"

    instances=filter_instances(project)

    for i in instances:
        print ('starting {0}...' .format(i.id))
        i.start()
    return


if __name__=='__main__':
    instances()
