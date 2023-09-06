#!/usr/bin/env python

from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
from mininet.clean import cleanup


def networkTestbed():
    info( '######################################################################\n' )    
    info( '# This script was developed by Ruijun Jiang for\n' )    
    info( '# his final project (MSc) at the University of Glasgow\n' )    
    info( '######################################################################\n\n' )    
    
    # (0) Erase any remaining configurations, and reset the Mininet environment
    info( '######################################################################\n' )    
    info( '# (0) Erase any remaining configurations, and\n' )    
    info( '#     reset the Mininet environment\n' )    
    info( '######################################################################\n' )
    cleanup()
    
    # (1) Create and run the testing environment
    info( '######################################################################\n' )    
    info( '# (1) Create and run the testing environment\n' )    
    info( '#\n' )    
    info( '# h1-----|                                              |-----h2\n' )    
    info( '#        |----------s1----------s2----------s3----------|\n' )    
    info( '# h3-----|                                              |-----h4\n' )    
    info( '#\n' )    
    info( '######################################################################\n' ) 
    net = Mininet( topo=None,
                   build=False,
                   ipBase='10.0.0.0/8')

    info( '*** Adding controller\n' )
    info( '*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch, failMode='standalone')
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch, failMode='standalone')
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch, failMode='standalone')

    info( '*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='10.0.0.1', defaultRoute=None)
    h2 = net.addHost('h2', cls=Host, ip='10.0.0.2', defaultRoute=None)
    h3 = net.addHost('h3', cls=Host, ip='10.0.0.3', defaultRoute=None)
    h4 = net.addHost('h4', cls=Host, ip='10.0.0.4', defaultRoute=None)

    info( '*** Add links\n')
    net.addLink(s1, s2)
    net.addLink(s2, s3)
    net.addLink(h1, s1)
    net.addLink(h3, s1)
    net.addLink(h2, s3)
    net.addLink(s3, h4)

    info( '*** Starting network\n')
    net.build()
    info( '*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info( '*** Starting switches\n')
    net.get('s1').start([])
    net.get('s2').start([])
    net.get('s3').start([])

    info( '*** Post configure switches and hosts\n')

    # (2) Configure the testing environment
    # (2.1) Modify receive & send buffer size limits on all the hosts [20*BDP]
    info( '######################################################################\n' )    
    info( '# (2) Configure the testing environment\n' )    
    info( '#\n' )    
    info( '#     (2.1) Modify receive & send buffer size limits on all the hosts\n' )    
    info( '#           [20 * BDP]\n' )    
    info( '######################################################################\n' )
    modifyHostBuffers(net)
    
    # (2.2) Emulate a WAN with delay and packet loss
    # (2.2.1) Add delay & packet loss on the link between s1-s2 [30 ms]
    # (2.2.2) Limit the link speed between s2-s3 to 1 Gbps, and 
    #         modify the buffer size on the network node s2 [10 * BDP]
    # (2.2.3) Deploy FQ-CoDel on the network node s2 egress port
    info( '######################################################################\n' )    
    info( '#     (2.2) Emulate a WAN with delay\n' )    
    info( '#\n' )    
    info( '#           (2.2.1) Add delay on the link between s1-s2\n' )    
    info( '#                   [30 ms]\n' )
    info( '#           (2.2.2) Limit the link speed between s2-s3 to 1 Gbps, and\n' )    
    info( '#                   modify the buffer size on the network node s2\n' )    
    info( '#                   [10 * BDP]\n' )    
    info( '#           (2.2.3) Deploy FQ-CoDel on the network node s2 egress port\n' )    
    info( '######################################################################\n' )
    emulateWAN(net)
    
    # (3) Conduct scenario 1 experiment 1: single flow [CUBIC]
    # (3.1) Deploy CUBIC on the sender host h1
    # (3.2) Run iPerf3 test (h1-h2)
    info( '######################################################################\n' )    
    info( '# (3) Conduct scenario 1 experiment 1: single flow [CUBIC]\n' )    
    info( '#\n' )    
    info( '#     (3.1) Deploy CUBIC on the sender host h1\n' )    
    info( '#     (3.2) Run iPerf3 test (h1-h2)\n' )    
    info( '######################################################################\n' )   
    scenario1Experiment1(net)
    
    # (4) Conduct scenario 1 experiment 2: single flow [BBR]
    # (4.1) Deploy BBR on the sender host h1
    # (4.2) Run iPerf3 test (h1-h2)
    info( '######################################################################\n' )    
    info( '# (4) Conduct scenario 1 experiment 2: single flow [BBR]\n' )    
    info( '#\n' )    
    info( '#     (4.1) Deploy BBR on the sender host h1\n' )    
    info( '#     (4.2) Run iPerf3 test (h1-h2)\n' )    
    info( '######################################################################\n' )   
    scenario1Experiment2(net)

    # (5) Conduct scenario 2 experiment 1: parallel flows [CUBIC]
    # (5.1) Deploy CUBIC on the sender host h1
    # (5.2) Run iPerf3 test (h1-h2)
    info( '######################################################################\n' )    
    info( '# (5) Conduct scenario 2 experiment 1: 2 parallel flows from 1 host\n' )    
    info( '#                                      [CUBIC]\n' )    
    info( '#\n' )    
    info( '#     (5.1) Deploy CUBIC on the sender host h1\n' )    
    info( '#     (5.2) Run iPerf3 test (h1-h2)\n' )    
    info( '######################################################################\n' )   
    scenario2Experiment1(net)
    
    # (6) Conduct scenario 2 experiment 2: parallel flows [BBR]
    # (6.1) Deploy BBR on the sender host h1
    # (6.2) Run iPerf3 test (h1-h2)
    info( '######################################################################\n' )    
    info( '# (6) Conduct scenario 2 experiment 2: 2 parallel flows from 1 host\n' )    
    info( '#                                      [BBR]\n' )    
    info( '#\n' )    
    info( '#     (6.1) Deploy BBR on the sender host h1\n' )    
    info( '#     (6.2) Run iPerf3 test (h1-h2)\n' )    
    info( '######################################################################\n' )   
    scenario2Experiment2(net)
    
    # (7) Conduct scenario 3 experiment 1: competing flows [2 CUBIC flows]
    # (7.1) Deploy CUBIC on the sender host h1
    # (7.2) Deploy CUBIC on the sender host h3
    # (7.3) Run iPerf3 test (h1-h2 & h3-h4)
    info( '######################################################################\n' )    
    info( '# (7) Conduct scenario 3 experiment 1: 2 competing flows from 2 hosts\n' )    
    info( '#                                      [2 CUBIC flows]\n' )    
    info( '#\n' )    
    info( '#     (7.1) Deploy CUBIC on the sender host h1\n' )    
    info( '#     (7.2) Deploy CUBIC on the sender host h3\n' )    
    info( '#     (7.3) Run iPerf3 test (h1-h2 & h3-h4)\n' )    
    info( '######################################################################\n' )   
    scenario3Experiment1(net)

    # (8) Conduct scenario 3 experiment 2: competing flows [2 BBR flows]
    # (8.1) Deploy BBR on the sender host h1
    # (8.2) Deploy BBR on the sender host h3
    # (8.3) Run iPerf3 test (h1-h2 & h3-h4)
    info( '######################################################################\n' )    
    info( '# (8) Conduct scenario 3 experiment 2: 2 competing flows from 2 hosts\n' )    
    info( '#                                      [2 BBR flows]\n' )    
    info( '#\n' )    
    info( '#     (8.1) Deploy BBR on the sender host h1\n' )    
    info( '#     (8.2) Deploy BBR on the sender host h3\n' )    
    info( '#     (8.3) Run iPerf3 test (h1-h2 & h3-h4)\n' )    
    info( '######################################################################\n' )   
    scenario3Experiment2(net)
    
    # (9) Conduct scenario 3 experiment 3: competing flows [1 CUBIC flow, 1 BBR flow]
    # (9.1) Deploy CUBIC on the sender host h1
    # (9.2) Deploy BBR on the sender host h3
    # (9.3) Run iPerf3 test (h1-h2 & h3-h4)
    info( '######################################################################\n' )    
    info( '# (9) Conduct scenario 3 experiment 3: 2 competing flows from 2 hosts\n' )    
    info( '#                                      [1 CUBIC flow, 1 BBR flow]\n' )    
    info( '#\n' )    
    info( '#     (9.1) Deploy CUBIC on the sender host h1\n' )    
    info( '#     (9.2) Deploy BBR on the sender host h3\n' )    
    info( '#     (9.3) Run iPerf3 test (h1-h2 & h3-h4)\n' )    
    info( '######################################################################\n' )   
    scenario3Experiment3(net)
    
    # Note that: All experiments are completed! 
    info( '######################################################################\n' )
    info( '# Note that: All experiments are completed!\n' )
    info( '#\n' )
    info( '# To proceed with further testing, enter the desired commands manually\n' )
    info( '# To exit, type "quit"\n' )
    info( '######################################################################\n\n' )    
    CLI(net)
    
    net.stop()


# (2.1)
#     BW = 1 Gbps = 1000000000 bps
#     RTT = 30 ms = 0.03 s
# =>
#     BDP = 1000000000 * 0.03 = 30000000 bits = 3750000 bytes
# =>
#     20 * BDP = 20 * 3750000 = 75000000 bytes

def modifyHostBuffers(net):    
    # Define the sysctl commands
    commands = [
        "sysctl -w net.ipv4.tcp_wmem='10240 87380 75000000'",
        "sysctl -w net.ipv4.tcp_rmem='10240 87380 75000000'"
    ]

    # Execute the commands on each host
    info( '*** Modifying buffers on all the hosts\n')
    for host in net.hosts:
        for cmd in commands:
            host.cmd(cmd)


# (2.2)
# egrep '^CONFIG_HZ_[0-9]+' /boot/config-$(uname -r)				
# The HZ on sender hosts is 250
# tbf burst = rate/HZ = 1 Gbps / 250 = 1000000000 bps / 250 = 4000000 bits =  500000 bytes

#     BW = 1 Gbps = 1000000000 bps
#     RTT = 30 ms = 0.03 s
# =>
#     BDP = 1000000000 * 0.03 = 30000000 bits = 3750000 bytes
# =>
#     10 * BDP = 10 * 3750000 = 37500000 bytes

#     fq_codel limit = buffer size on the network node / maximum size of a data packet 
#                    = 10 * BDP / MTU = 37500000 / 1500 = 25000

def emulateWAN(net):
    # Add delay on the link between s1-s2 [30 ms]
    # info( '*** Adding delay and packet loss in the WAN\n')
    info( '*** Adding delay in the WAN\n')
    s1 = net.get('s1')
    # s1.cmd('sudo tc qdisc add dev s1-eth1 root netem loss 0.01% delay 30ms')
    s1.cmd('sudo tc qdisc add dev s1-eth1 root netem delay 30ms')
    
    # Limit the link speed between s2-s3 to 1 Gbps, and 
    # modify the buffer size on the network node s2 [10 * BDP]
    info( '*** Limiting the speed of the bottleneck link\n')
    s2 = net.get('s2')
    s2.cmd('sudo tc qdisc add dev s2-eth2 root handle 1: tbf rate 1gbit burst 500000 limit 37500000')
    
    # Deploy FQ-CoDel on the network node s2 egress port
    info( '*** Deploying FQ-CoDel Active Queue Management\n')
    s2.cmd('sudo tc qdisc add dev s2-eth2 parent 1: handle 2: fq_codel limit 25000 target 5ms interval 100ms')


# (3)
def scenario1Experiment1(net):    
    # Deploy CUBIC on the sender host h1
    info( '*** Deploying CUBIC TCP congestion control\n')
    h1 = net.get('h1')
    h1.cmd('sysctl -w net.ipv4.tcp_congestion_control=cubic')
    
    # Execute pingall to avoid bias due to ARP caching
    info( '*** Executing ping to avoid ARP bias...\n')    
    while True:
        result = net.pingAll()
        # 0 indicates success
        if result == 0:
            break
        info('*** Ping was unsuccessful. Retrying...\n')
    
    # Start iPerf3 server on the receiver host h2
    info( '*** Starting iPerf3 server on h2...\n')    
    h2 = net.get('h2')
    h2.cmd('iperf3 -s &')

    # Give the server a moment to start
    info('*** Waiting for iPerf3 server to start...\n')
    h1.waitOutput()    
    
    # Run iPerf3 client on the sender host h1 and 
    # save the results to a JSON file
    info('*** Running iPerf3 client on h1...\n')
    h1.cmd('iperf3 -c 10.0.0.2 -t 60 -J > s1e1_single_flow_cubic.json')
    
    # Kill the iPerf3 server on h2 after the test
    info('*** Results saved!\n')    
    info('*** Stoping iPerf3 server on h2...\n')    
    h2.cmd('pkill iperf3')


# (4)
def scenario1Experiment2(net):    
    # Deploy BBR on the sender host h1
    info( '*** Deploying BBR TCP congestion control\n')
    h1 = net.get('h1')
    h1.cmd('sysctl -w net.ipv4.tcp_congestion_control=bbr')
    
    # Execute pingall to avoid bias due to ARP caching
    info( '*** Executing ping to avoid ARP bias...\n')    
    while True:
        result = net.pingAll()
        # 0 indicates success
        if result == 0:
            break
        info('*** Ping was unsuccessful. Retrying...\n')
    
    # Start iPerf3 server on the receiver host h2
    info( '*** Starting iPerf3 server on h2...\n')    
    h2 = net.get('h2')
    h2.cmd('iperf3 -s &')

    # Give the server a moment to start
    info('*** Waiting for iPerf3 server to start...\n')
    h1.waitOutput()    
    
    # Run iPerf3 client on the sender host h1 and 
    # save the results to a JSON file
    info('*** Running iPerf3 client on h1...\n')
    h1.cmd('iperf3 -c 10.0.0.2 -t 60 -J > s1e2_single_flow_bbr.json')
    
    # Kill the iPerf3 server on h2 after the test
    info('*** Results saved!\n')    
    info('*** Stoping iPerf3 server on h2...\n')    
    h2.cmd('pkill iperf3')


# (5)
def scenario2Experiment1(net):    
    # Deploy CUBIC on the sender host h1
    info( '*** Deploying CUBIC TCP congestion control\n')
    h1 = net.get('h1')
    h1.cmd('sysctl -w net.ipv4.tcp_congestion_control=cubic')
    
    # Execute pingall to avoid bias due to ARP caching
    info( '*** Executing ping to avoid ARP bias...\n')    
    while True:
        result = net.pingAll()
        # 0 indicates success
        if result == 0:
            break
        info('*** Ping was unsuccessful. Retrying...\n')
    
    # Start iPerf3 server on the receiver host h2
    info( '*** Starting iPerf3 server on h2...\n')    
    h2 = net.get('h2')
    h2.cmd('iperf3 -s &')

    # Give the server a moment to start
    info('*** Waiting for iPerf3 server to start...\n')
    h1.waitOutput()    
    
    # Run iPerf3 client on the sender host h1 and 
    # save the results to a JSON file
    info('*** Running iPerf3 client on h1...\n')
    h1.cmd('iperf3 -c 10.0.0.2 -P 2 -t 60 -J > s2e1_parallel_flows_cubic.json')
    
    # Kill the iPerf3 server on h2 after the test
    info('*** Results saved!\n')    
    info('*** Stoping iPerf3 server on h2...\n')    
    h2.cmd('pkill iperf3')


# (6)
def scenario2Experiment2(net):    
    # Deploy BBR on the sender host h1
    info( '*** Deploying BBR TCP congestion control\n')
    h1 = net.get('h1')
    h1.cmd('sysctl -w net.ipv4.tcp_congestion_control=bbr')
    
    # Execute pingall to avoid bias due to ARP caching
    info( '*** Executing ping to avoid ARP bias...\n')    
    while True:
        result = net.pingAll()
        # 0 indicates success
        if result == 0:
            break
        info('*** Ping was unsuccessful. Retrying...\n')
    
    # Start iPerf3 server on the receiver host h2
    info( '*** Starting iPerf3 server on h2...\n')    
    h2 = net.get('h2')
    h2.cmd('iperf3 -s &')

    # Give the server a moment to start
    info('*** Waiting for iPerf3 server to start...\n')
    h1.waitOutput()    
    
    # Run iPerf3 client on the sender host h1 and 
    # save the results to a JSON file
    info('*** Running iPerf3 client on h1...\n')
    h1.cmd('iperf3 -c 10.0.0.2 -P 2 -t 60 -J > s2e2_parallel_flows_bbr.json')
    
    # Kill the iPerf3 server on h2 after the test
    info('*** Results saved!\n')    
    info('*** Stoping iPerf3 server on h2...\n')    
    h2.cmd('pkill iperf3')


# (7)
def scenario3Experiment1(net):
    # Deploy CUBIC on the sender host h1
    info( '*** Deploying CUBIC TCP congestion control\n')
    h1 = net.get('h1')
    h1.cmd('sysctl -w net.ipv4.tcp_congestion_control=cubic')
    
    # Deploy CUBIC on the sender host h3
    info( '*** Deploying CUBIC TCP congestion control\n')
    h3 = net.get('h3')
    h3.cmd('sysctl -w net.ipv4.tcp_congestion_control=cubic')
    
    # Execute pingall to avoid bias due to ARP caching
    info( '*** Executing ping to avoid ARP bias...\n')    
    while True:
        result = net.pingAll()
        # 0 indicates success
        if result == 0:
            break
        info('*** Ping was unsuccessful. Retrying...\n')
    
    # Start iPerf3 server on the receiver host h2
    info( '*** Starting iPerf3 server on h2...\n')    
    h2 = net.get('h2')
    h2.cmd('iperf3 -s &')

    # Start iPerf3 server on the receiver host h4
    info( '*** Starting iPerf3 server on h4...\n')    
    h4 = net.get('h4')
    h4.cmd('iperf3 -s &')

    # Give the server a moment to start
    info('*** Waiting for iPerf3 server to start...\n')
    h1.waitOutput()
    h3.waitOutput()      
    
    # Run iPerf3 client on the sender host h1 and 
    # save the results to a JSON file
    info('*** Running iPerf3 client on h1 and h3 simultaneously...\n')
    h1.cmd('iperf3 -c 10.0.0.2 -t 60 -J > s3e1_h1_competing_flow_cubic.json')
    h3.cmd('iperf3 -c 10.0.0.4 -t 60 -J > s3e1_h3_competing_flow_cubic.json')
    
    # Kill the iPerf3 server on h2 after the test
    # Kill the iPerf3 server on h4 after the test
    info('*** Results saved!\n')
    info('*** Stoping iPerf3 server on h2...\n')
    info('*** Stoping iPerf3 server on h4...\n')    
    h2.cmd('pkill iperf3')    
    h4.cmd('pkill iperf3')    


# (8)
def scenario3Experiment2(net):
    # Deploy BBR on the sender host h1
    info( '*** Deploying BBR TCP congestion control\n')
    h1 = net.get('h1')
    h1.cmd('sysctl -w net.ipv4.tcp_congestion_control=bbr')
    
    # Deploy BBR on the sender host h3
    info( '*** Deploying BBR TCP congestion control\n')
    h3 = net.get('h3')
    h3.cmd('sysctl -w net.ipv4.tcp_congestion_control=bbr')
    
    # Execute pingall to avoid bias due to ARP caching
    info( '*** Executing ping to avoid ARP bias...\n')    
    while True:
        result = net.pingAll()
        # 0 indicates success
        if result == 0:
            break
        info('*** Ping was unsuccessful. Retrying...\n')
    
    # Start iPerf3 server on the receiver host h2
    info( '*** Starting iPerf3 server on h2...\n')    
    h2 = net.get('h2')
    h2.cmd('iperf3 -s &')

    # Start iPerf3 server on the receiver host h4
    info( '*** Starting iPerf3 server on h4...\n')    
    h4 = net.get('h4')
    h4.cmd('iperf3 -s &')

    # Give the server a moment to start
    info('*** Waiting for iPerf3 server to start...\n')
    h1.waitOutput()
    h3.waitOutput()      
    
    # Run iPerf3 client on the sender host h1 and 
    # save the results to a JSON file
    info('*** Running iPerf3 client on h1 and h3 simultaneously...\n')
    h1.cmd('iperf3 -c 10.0.0.2 -t 60 -J > s3e2_h1_competing_flow_bbr.json')
    h3.cmd('iperf3 -c 10.0.0.4 -t 60 -J > s3e2_h3_competing_flow_bbr.json')
    
    # Kill the iPerf3 server on h2 after the test
    # Kill the iPerf3 server on h4 after the test
    info('*** Results saved!\n')
    info('*** Stoping iPerf3 server on h2...\n')
    info('*** Stoping iPerf3 server on h4...\n')    
    h2.cmd('pkill iperf3')    
    h4.cmd('pkill iperf3')    


# (9)
def scenario3Experiment3(net):
    # Deploy CUBIC on the sender host h1
    info( '*** Deploying CUBIC TCP congestion control\n')
    h1 = net.get('h1')
    h1.cmd('sysctl -w net.ipv4.tcp_congestion_control=cubic')
    
    # Deploy BBR on the sender host h3
    info( '*** Deploying BBR TCP congestion control\n')
    h3 = net.get('h3')
    h3.cmd('sysctl -w net.ipv4.tcp_congestion_control=bbr')
    
    # Execute pingall to avoid bias due to ARP caching
    info( '*** Executing ping to avoid ARP bias...\n')    
    while True:
        result = net.pingAll()
        # 0 indicates success
        if result == 0:
            break
        info('*** Ping was unsuccessful. Retrying...\n')
    
    # Start iPerf3 server on the receiver host h2
    info( '*** Starting iPerf3 server on h2...\n')    
    h2 = net.get('h2')
    h2.cmd('iperf3 -s &')

    # Start iPerf3 server on the receiver host h4
    info( '*** Starting iPerf3 server on h4...\n')    
    h4 = net.get('h4')
    h4.cmd('iperf3 -s &')

    # Give the server a moment to start
    info('*** Waiting for iPerf3 server to start...\n')
    h1.waitOutput()
    h3.waitOutput()      
    
    # Run iPerf3 client on the sender host h1 and 
    # save the results to a JSON file
    info('*** Running iPerf3 client on h1 and h3 simultaneously...\n')
    h1.cmd('iperf3 -c 10.0.0.2 -t 60 -J > s3e3_h1_competing_flow_cubic.json')
    h3.cmd('iperf3 -c 10.0.0.4 -t 60 -J > s3e3_h3_competing_flow_bbr.json')
    
    # Kill the iPerf3 server on h2 after the test
    # Kill the iPerf3 server on h4 after the test
    info('*** Results saved!\n')
    info('*** Stoping iPerf3 server on h2...\n')
    info('*** Stoping iPerf3 server on h4...\n')    
    h2.cmd('pkill iperf3')    
    h4.cmd('pkill iperf3')  


if __name__ == '__main__':
    setLogLevel( 'info' )
    networkTestbed()

