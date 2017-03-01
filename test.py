import sys
import time
sys.path.insert(0, '/home/dshvetsov/mininet')


from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.node import Controller

class RUNOS ( Controller ) :
    def __init__( self, name, cdir='/home/dshvetsov/runos',
            command='execute', port=6653,  cargs='./build/runos %d',**kwargs ):
        Controller.__init__(self, name, cdir=cdir, port=port, command=command,
                cargs=cargs, **kwargs )

class Node :
    def __init__(self):
        self.left = None
        self.right = None

    def addChild(self, child):
        if self.left is None:
            self.left = child
            return
        elif self.right is None:
            self.right = child
            return

    def isHost(self):
        return self.left is None and self.right is None

def createTopo(n):
    node = Node()
    if n > 1:
        node.addChild(createTopo(n/2))
        node.addChild(createTopo(n - n/2))
    return node


class BinTreeTopo(Topo):

    def build_tree(self, node):
        if node.isHost():
            self.hostName += 1
            return self.addHost("h%s" % self.hostName)
        else:
            self.switchName += 1
            sw = self.addSwitch("s%s" % self.switchName)
            self.sws.append(sw)
            left_subtree = self.build_tree(node.left)
            right_subtree = self.build_tree(node.right)
            self.addLink(sw, left_subtree)
            self.addLink(sw, right_subtree)
            return sw

    def __init__(self, n=2):
        self.sws = []
        self.switchName = 0
        self.hostName= 0
        Topo.__init__( self )
        root = createTopo( n )
        self.build_tree( root )

trigged = False
def smartSum(text, first, second):

    def helper(line):
        global trigged
        if trigged and line.count(second) > 0:
            trigged = False
            return 1
        if line.count(first) > 0 :
            trigged = True
        else :
            trigged = False
        return 0

    ret =  reduce(lambda x,y : x + helper(y), text.split('\n'), 0)
    trigged = False
    return ret

def simpleTest(n = 4):
    "Simple test"
    topo = BinTreeTopo(n)
    net = Mininet(topo,controller=lambda name : RUNOS(name=name))
    net.start()
    switches = [net.get(i) for i in topo.sws]
    files = []
    for j in switches :
        filename = "snoop" + str( j.dpid ) + '.dmp'
        j.dpctl('snoop', '2>&1 >/dev/null | grep -E "OFPT_FLOW_MOD|OFPT_PACKET_IN|dl_type=0x88cc|OFPT_PACKET_OUT|OFPT_FLOW_REMOVED > ' + filename + '&')
        files.append(filename)
    time.sleep(0.5)
#dumpNodeConnections(net.hosts)
    loss = net.pingAll()
    if loss > 10 :
        print "WARNING: in %d hosts too many loss" %n
    net.stop()
    flowmods = 0
    packet_ins = 0
    lldp_packet_ins = 0
    packet_outs = 0
    lldp_packet_outs = 0
    flow_removeds = 0

    for j in files:
        f = open(j)
        text = f.readlines()
        text = ''.join(text)
        flowmods += text.count('OFPT_FLOW_MOD')
        packet_ins += text.count('OFPT_PACKET_IN')
        lldp_packet_ins += smartSum(text, "OFPT_PACKET_IN", "dl_type=0x88cc")
        packet_outs += text.count('OFPT_PACKET_OUT')
        lldp_packet_outs +=smartSum(text, "OFPT_PACKET_OUT", "dl_type=0x88cc")
        flow_removeds += text.count('OFPT_FLOW_REMOVED')

    f.close()
    f = open('ans.csv', 'a')
    f.write("%d, %d, %d, %d, %d, %d, %d, %f\n" % (n , flowmods , packet_ins , lldp_packet_ins , packet_outs , lldp_packet_outs , flow_removeds , loss))
    f.close()

    print flowmods, packet_ins, lldp_packet_ins, packet_outs, lldp_packet_outs, flow_removeds

if __name__ == '__main__':
    for i in range(2, 4):
        simpleTest(i)
#topos = {'mytopo' : ( lambda n: BinTreeTopo(n) ) }
