import boto3
import click

sess = boto3.session
ec2_sess = sess.boto3.resource('ec2')

@click.command()
def list_instances():
        "List EC2 instances"
        for k in ec2_sess.instances.all():
            print (','.join((
                k.id,
                k.instance_type,
                k.placement['AvailabilityZone'],
                k.state['Name'],
                k.public_dns_name
                )))

        return

if __name__=='__main__':
    list_instances()
