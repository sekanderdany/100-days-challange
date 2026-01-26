


# Creating and Configuring Linux Network Namespaces for Isolated Networking

![Logo](./Linux_network_namespaces.png)

## Introduction

In the world of Linux networking, creating isolated network environments can be crucial for testing, security, and network management. Network namespaces in Linux allow us to compartmentalize network interfaces, IP addresses, and routing tables, making it possible to have multiple isolated network environments on a single host. In this post, we'll explore how to create and configure two such namespaces, which we'll name `red` and `blue`, and set them up to communicate with each other.

## Creating the Network Namespaces

First, we need to create our namespaces. We'll call these namespaces `red` and `blue`. This is done using the ip netns command.

```bash
ip netns add red
ip netns add blue
```

## Verifying the Namespace Creation

To ensure our namespaces are created, we can list them:

```bash
ip netns list
```

## Creating a Virtual Ethernet (veth) Pair

A veth pair is like a virtual Ethernet cable. One end will be in the `red` namespace, and the other in the `blue` namespace.

```bash
ip link add veth-red type veth peer name veth-blue
```

## Assigning veth Ends to Each Namespace

Now, we move each end of the veth pair into its respective namespace:

```bash
ip link set veth-red netns red
ip link set veth-blue netns blue
```
## Configuring Network Interfaces and IP Addresses

For the `red` and `blue` namespaces to communicate, we need to configure their network interfaces and assign IP addresses.

### Inside the `Red` Namespace:
```bash
ip netns exec red ip link set lo up
ip netns exec red ip link set veth-red up
ip netns exec red ip addr add 192.168.15.1/32 dev veth-red
```

### Inside the `Blue` Namespace:
```bash
ip netns exec blue ip link set lo up
ip netns exec blue ip link set veth-blue up
ip netns exec blue ip addr add 192.168.15.2/32 dev veth-blue
```

## Setting Up Routing Between Namespaces

Finally, to allow the namespaces to communicate via ping or other network protocols, we set up routing:

```bash
ip netns exec red ip route add default via 192.168.15.1
ip netns exec blue ip route add default via 192.168.15.2
```

# Conclusion

Network namespaces in Linux offer a powerful tool for creating isolated network environments. By following these steps, you can simulate network scenarios, test applications, and experiment with network configurations without affecting your main network. Enjoy exploring the possibilities! Thanks for your time!!
