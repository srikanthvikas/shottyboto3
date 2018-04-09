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
def cli():
    """Shotty manages volumes and instances"""

@cli.group('snapshots')
def snapshots():
    """Commands for volumes"""

@snapshots.command('list')
@click.option('--project',default=None,
    help="Only snapshots for Project (tag Project:<name>)")

def list_snapshots(project):
    "List Ec2 Snapshots"
    instances = filter_instances(project)

    for k in instances:
        for v in k.volumes.all():
            for j in v.snapshots.all():
                print(", ". join((
                j.id,
                j.state,
                j.progress,
                j.start_time.strftime("%c"),
                v.id,
                k.id,
                v.state
                )))
    return

@cli.group('volumes')
def volumes():
    """Commands for volumes"""

@volumes.command('list')
@click.option('--project',default=None,
    help="Only instances for Project (tag Project:<name>)")

def list_volumes(project):
    "List Ec2 Volumes"
    instances = filter_instances(project)

    for k in instances:
        for v in k.volumes.all():
            print(", ". join((
            v.id,
            k.id,
            v.state,
            str(v.size)+" GiB",
            v.encrypted and "Encrypted" or "Not Encrypted"
            )))
    return


@cli.group('instances')
def instances():
    """Commands for instances"""

@instances.command('snapshot',
    help="Only instances for Project (tag Project: <name>)")

def create_snapshots(project):
    "Create cnapshot for EC2 instances"

    instances=filter_instances(project)

    for i in instances:
        for v in volumes.all():
            print("Creating Snapshot of {0}",format(v.id))
            v.create_snapshot(Description="Created by Shotty program")
    return

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
    cli()
