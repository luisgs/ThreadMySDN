#!/usr/bin/python

"""
- Software Defined Networking (SDN) course
-- Network Virtualization: Network Topology
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
        hconfig = {'inNamespace':True}
        http_link_config = {'bw': 1}
        video_link_config = {'bw': 10}
	# Therefore, maximum badnwith speed should be 10mbps
        host_link_config = {'bw':10}

        # Create switch nodes
        for i in range(4):
            sconfig = {'dpid': "%016x" % (i+1)}
            self.addSwitch('s%d' % (i+1), **sconfig)

        # Create host nodes
        # I have control about the MAC addresses so they are not assigned as default.
        for i in range(4):
            self.addHost('h%d' % (i+1), mac='0:0:0:0:0:%d'%(i+1),ip='10.0.0.%d'%(i+1), **hconfig)

        # I add a particular host with a particular MAC and IP addresses
        self.addHost('h5', mac='0:0:0:0:0:B', ip='10.0.0.25', **hconfig)
        # Add switch links
        # Specified to the port numbers to avoid any port number consistency issue
        
        self.addLink('s2', 's1', port1=1, port2=1, **http_link_config)
        self.addLink('s3', 's1', port1=1, port2=2, **video_link_config)
        self.addLink('h1', 's1', port1=1, port2=3, **host_link_config)
        self.addLink('h2', 's1', port1=1, port2=4, **host_link_config)
        
        self.addLink('s2', 's4', port1=2, port2=1, **http_link_config)
        self.addLink('s3', 's4', port1=2, port2=2, **video_link_config)
        self.addLink('h3', 's4', port1=1, port2=3, **host_link_config)
        self.addLink('h4', 's4', port1=1, port2=4, **host_link_config)

        # Add link to my malicious host
        self.addLink('s2', 'h5', port1=3, port2=1, **http_link_config)
        
        info( '\n*** printing and validating the ports running on each interface\n' )
        


def startNetwork():
    info('** Creating Overlay network topology\n')
    topo = FVTopo()
    global net
    net = Mininet(topo=topo, link = TCLink,
                  controller=lambda name: RemoteController(name, ip='127.0.0.1'),
                  listenPort=6633, autoSetMacs=True)

    info('** Starting the network\n')
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
