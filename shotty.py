import boto3
import botocore
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

def has_pending_snapshots(volume):#returns true is there are pending snapshots
    snapshots=list(volume.snapshots.all())
    return snapshots and snapshots[0].state=='pending'

@click.group()
def cli():
    """Shotty manages volumes and instances"""

@cli.group('snapshots')
def snapshots():
    """Commands for volumes"""

@snapshots.command('list')
@click.option('--project',default=None,
    help="Only snapshots for Project (tag Project:<name>)")
@click.option('--all','--list_all',default=False,is_flag=True,
    help="List all volumes for each snapshot not just the latest")#only works is --all is present

def list_snapshots(project, list_all):
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
#the above loops returns in reverse chronological order
                    if j.state == 'completed' and not list_all:
                        break
#this break helps print only the latest snapshot of an instance, otherwise
#if '--all' is present it shows all the instances

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
@click.option('--project',default=None,
    help="Only instances for Project (tag Project:<name>)")

def create_snapshots(project):
    "Create snapshot for EC2 instances"

    instances=filter_instances(project)

    for i in instances:
        print("Stopping {0}... ".format(i.id))
        i.stop()
        i.wait_until_stopped()

        for v in i.volumes.all():
            if (has_pending_snapshots):
                print("snapshot already in progress {0} ".format(v.id))
                continue
            print("Creating Snapshot of {0}",format(v.id))
            v.create_snapshot(Description="Created by Shotty program")
        print("Starting {0}...".format(i.id))
        i.start()
        i.wait_until_running()

        print("Job's Done")
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
        try:
            i.stop()
        except botocore.exceptions.ClientError as e:
            print("Could not stop {0}.".format(i.id)+str(e))
            continue

    return

@instances.command('start')
@click.option('--project', default=None, help='Only instances for Project')

def stop_instances(project):
    "Start Ec2 instances"

    instances=filter_instances(project)

    for i in instances:
        print ('starting {0}...' .format(i.id))
        try:
            i.start()
        except botocore.exceptions.ClientError as e:
            print("Could not start {0}.".format(i.id)+str(e))
            continue
    return


if __name__=='__main__':
    cli()
