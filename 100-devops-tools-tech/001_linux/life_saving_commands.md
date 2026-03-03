# get rid of hours of lag in yum update

yum update --disableplugin=subscription-manager

# If passwd root not working
```
authselect select minimal --force
```
# Resque bad k8s node- 

```
kubectl cordon <worker-node-name>

kubectl delete node <worker-node-name>

systemctl stop kubelet
systemctl stop containerd   # or cri-o / docker

kubeadm reset -f

rm -rf /etc/cni/net.d
rm -rf /var/lib/cni
rm -rf /var/lib/kubelet/*
rm -rf /etc/kubernetes

swapoff -a
sysctl net.ipv4.ip_forward

systemctl start containerd
systemctl enable containerd

kubeadm token create --print-join-command

kubeadm join <MASTER_IP>:6443 \
  --token <token> \
  --discovery-token-ca-cert-hash sha256:<hash>
```