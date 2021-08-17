#!/usr/bin/python

"""
- Software Defined Networking (SDN) course
-- Network Virtualization: Network Topology
-- Creator: Luis Gomez
"""

import inspect
import os
import atexit
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.topo import Topo
from mininet.link import TCLink
from mininet.topo import SingleSwitchTopo
from mininet.node import RemoteController


net = None

class FVTopo(Topo):
    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        # Create template host, switch, and link
        hconfig = {'inNamespace':False}
        switch_link_config = {'bw': 50}
	    # Therefore, maximum badnwith speed should be 10mbps
        host_link_config = {'bw':10}

        # Create switch nodes
        for i in range(2):
            sconfig = {'dpid': '%016x' % (i+1)}
            self.addSwitch('s%d' % (i+1), **sconfig)

        # Create host nodes
        # I have control about the MAC addresses so they are not assigned as default.

        #for i in range(3):
        #    self.addHost('h%d' % (i+1), mac='00:00:00:00:00:0%d'%(i+1),ip='10.0.0.%d'%(i+1), **hconfig)

        self.addHost('h1', mac='00:00:00:00:00:01',ip='10.0.0.1/24')
        self.addHost('h2', mac='00:00:00:00:00:02',ip='10.0.0.2/24')
        self.addHost('h3', mac='00:00:00:00:00:03',ip='10.0.0.3/24')

        # Attacker host will have a very clear MAC and IP.
        #self.addHost('h4', mac='00:00:00:00:00:0B', ip='10.0.0.25', **hconfig)
        self.addHost('h4', mac='00:00:00:00:00:0B', ip='10.0.0.25/24')

        # Add switch links
        # Specified to the port numbers to avoid any port number consistency issue

        # Switch interconnection
        self.addLink('s2', 's1', port1=1, port2=1, **switch_link_config)

        # hosts to switch connections
        self.addLink('h1', 's1', port1=1, port2=2, **host_link_config)
        self.addLink('h2', 's1', port1=1, port2=3, **host_link_config)
        self.addLink('h3', 's2', port1=2, port2=2, **host_link_config)
            # h1 will be our victim
            # h3 will try to contact h1

        # Add link to my malicious host
        self.addLink('h4', 's2', port1=1, port2=3, **host_link_config)

        info( '\n*** printing and validating the ports running on each interface\n' )



def startNetwork():
    info('** Creating Overlay network topology\n')
    topo = FVTopo()
    global net
    net = Mininet(topo=topo, link = TCLink,
                  controller=lambda name: RemoteController(name, ip='127.0.0.1'),
                  listenPort=6633) #, autoSetMacs=True)

    info('** Starting the network\n')

    # DISABLING IPv6
    for h in net.hosts:
        print "disable ipv6"
        h.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        h.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        h.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")

    for sw in net.switches:
        print "disable ipv6"
        sw.cmd("sysctl -w net.ipv6.conf.all.disable_ipv6=1")
        sw.cmd("sysctl -w net.ipv6.conf.default.disable_ipv6=1")
        sw.cmd("sysctl -w net.ipv6.conf.lo.disable_ipv6=1")
    net.start()

    info('** Running CLI\n')
    CLI(net)


def stopNetwork():
    if net is not None:
        info('** Tearing down Overlay network\n')
        net.stop()

if __name__ == '__main__':
    # Force cleanup on exit by registering a cleanup function
    atexit.register(stopNetwork)

    # Tell mininet to print useful information
    setLogLevel('info')
    startNetwork()
