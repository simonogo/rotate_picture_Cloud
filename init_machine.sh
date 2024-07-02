#!/bin/bash

# Configuration variables
export VM_NAME="project-machine-$RANDOM"
ZONE="northamerica-northeast1-b"
MACHINE_TYPE="e2-small"
IMAGE_FAMILY="debian-11"
IMAGE_PROJECT="debian-cloud"
SSH_KEY_PATH="$HOME/.ssh/google_compute_engine.pub"


# Create VM
gcloud compute instances create "$VM_NAME" \
    --zone="$ZONE" \
    --machine-type="$MACHINE_TYPE" \
    --image-family="$IMAGE_FAMILY" \
    --image-project="$IMAGE_PROJECT"

gcloud compute instances add-metadata $VM_NAME \
  --metadata-from-file ssh-keys=$SSH_KEY_PATH \
  --zone=$ZONE 


# Copy SSH key configure SSH for root
gcloud compute ssh "$VM_NAME" --zone="$ZONE" --command="sudo mkdir -p /root/.ssh && sudo cp ~/.ssh/authorized_keys /root/.ssh/authorized_keys" 
gcloud compute ssh "$VM_NAME" --zone="$ZONE" --command="sudo sed -i '/\bPermitRootLogin\b/d' /etc/ssh/sshd_config  && echo 'PermitRootLogin prohibit-password' | sudo tee -a /etc/ssh/sshd_config && sudo systemctl restart sshd && sudo mkdir /root/user_creation" 


# Install Ansible
gcloud compute ssh root@"$VM_NAME" --zone="$ZONE" --command="sudo apt update && sudo apt install -y ansible" 


# Copy Ansible script
gcloud compute scp ansible_script/* root@"$VM_NAME":/root/user_creation --zone="$ZONE" 


# Exec Ansible script to create new_user and personalize his directory structure
gcloud compute ssh root@"$VM_NAME" --zone="$ZONE" --command="ansible-playbook /root/user_creation/create_user.yml" 

echo "User created and configured. Python venv was created and all need modules were installed."

# Code/Scripts transfering
gcloud compute scp env_scripts/* my_user@"$VM_NAME":/home/my_user/workspace/env_scripts --zone="$ZONE"
gcloud compute scp event_broker/* my_user@"$VM_NAME":/home/my_user/workspace/sending_picture/event_broker  --zone="$ZONE"
gcloud compute scp rotate_script/* my_user@"$VM_NAME":/home/my_user/workspace/rotate_script  --zone="$ZONE"
gcloud compute scp sending_picture_script/* my_user@"$VM_NAME":/home/my_user/workspace/sending_picture  --zone="$ZONE"


# Machine description
echo "Virtual machine $VM_NAME was created"
gcloud compute instances list --filter=$VM_NAME --format="table(name, status, networkInterfaces[0].accessConfigs[0].natIP:label=EXTERNAL_IP, zone:label=LOCATION)"

