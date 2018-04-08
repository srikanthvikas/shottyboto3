import boto3

if __name__=='__main__':
    sess = boto3.session

    ec2_sess = sess.boto3.resource('ec2')

    for k in ec2_sess.instances.all():
        print k
