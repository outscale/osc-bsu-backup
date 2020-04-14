instances = {
    "Reservations": [
        {
            "Groups": [
                {
                    "GroupName": "priv",
                    "GroupId": "sg-0fea0dac"
                }
            ],
            "Instances": [
                {
                    "AmiLaunchIndex": 0,
                    "ImageId": "ami-b0d57010",
                    "InstanceId": "i-e6b7ab04",
                    "InstanceType": "t2.nano",
                    "KernelId": "",
                    "KeyName": "work",
                    "LaunchTime": "2020-04-09T13:28:58.721Z",
                    "Monitoring": {
                        "State": "disabled"
                    },
                    "Placement": {
                        "AvailabilityZone": "eu-west-2a",
                        "GroupName": "",
                        "Tenancy": "default"
                    },
                    "PrivateDnsName": "ip-10-0-2-10.eu-west-2.compute.internal",
                    "PrivateIpAddress": "10.0.2.10",
                    "ProductCodes": [],
                    "PublicDnsName": "",
                    "State": {
                        "Code": 16,
                        "Name": "running"
                    },
                    "SubnetId": "subnet-4c66da82",
                    "VpcId": "vpc-ad730e33",
                    "Architecture": "x86_64",
                    "BlockDeviceMappings": [
                        {
                            "DeviceName": "/dev/sda1",
                            "Ebs": {
                                "AttachTime": "2020-04-09T13:28:58.721Z",
                                "DeleteOnTermination": True,
                                "Status": "attached",
                                "VolumeId": "vol-a87f91c1"
                            }
                        }
                    ],
                    "ClientToken": "",
                    "EbsOptimized": False,
                    "Hypervisor": "xen",
                    "NetworkInterfaces": [
                        {
                            "Attachment": {
                                "AttachTime": "2020-04-09T13:28:58.721Z",
                                "AttachmentId": "eni-attach-1fb7811e",
                                "DeleteOnTermination": True,
                                "DeviceIndex": 0,
                                "Status": "attached"
                            },
                            "Description": "Primary network interface",
                            "Groups": [
                                {
                                    "GroupName": "priv",
                                    "GroupId": "sg-0fea0dac"
                                }
                            ],
                            "MacAddress": "aa:d6:af:71:91:f6",
                            "NetworkInterfaceId": "eni-a8213f11",
                            "OwnerId": "763630846467",
                            "PrivateDnsName": "ip-10-0-2-10.eu-west-2.compute.internal",
                            "PrivateIpAddress": "10.0.2.10",
                            "PrivateIpAddresses": [
                                {
                                    "Primary": True,
                                    "PrivateDnsName": "ip-10-0-2-10.eu-west-2.compute.internal",
                                    "PrivateIpAddress": "10.0.2.10"
                                }
                            ],
                            "SourceDestCheck": True,
                            "Status": "in-use",
                            "SubnetId": "subnet-4c66da82",
                            "VpcId": "vpc-ad730e33"
                        }
                    ],
                    "RootDeviceName": "/dev/sda1",
                    "RootDeviceType": "ebs",
                    "SecurityGroups": [
                        {
                            "GroupName": "priv",
                            "GroupId": "sg-0fea0dac"
                        }
                    ],
                    "SourceDestCheck": True,
                    "Tags": [
                        {
                            "Key": "Name",
                            "Value": "test1"
                        }
                    ],
                    "VirtualizationType": "hvm"
                }
            ],
            "OwnerId": "763630846467",
            "ReservationId": "r-390600af"
        }
    ]
}

volumes = {
    "Volumes": [
        {
            "Attachments": [
                {
                    "AttachTime": "2019-10-08T17:14:52.314Z",
                    "Device": "/dev/sda1",
                    "InstanceId": "i-8c1d8798",
                    "State": "attached",
                    "VolumeId": "vol-a24fffdc",
                    "DeleteOnTermination": False
                }
            ],
            "AvailabilityZone": "eu-west-2a",
            "CreateTime": "2017-08-10T17:34:59.644Z",
            "Size": 10,
            "SnapshotId": "snap-d1c97efa",
            "State": "in-use",
            "VolumeId": "vol-a24fffdc",
            "Tags": [
                {
                    "Key": "Name",
                    "Value": "test1"
                },
                {
                    "Key": "project",
                    "Value": "test2"
                }
            ],

            "VolumeType": "standard"
        }
    ]
}
