import sys
sys.path.insert(0, '/home/dshvetsov/mininet')


from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.node import RemoteController

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

def simpleTest():
    "Simple test"
    topo = BinTreeTopo(n = 4)
    net = Mininet(topo, controller=lambda name: RemoteController(name, ip='127.0.0.1', port=6653))
    net.start()
    switches = [net.get(i) for i in topo.sws]
    for j in switches :
        filename = "snoop" + str( j.dpid ) + '.dmp'
        j.dpctl('snoop', '2>' + filename + '&')
    dumpNodeConnections(net.hosts)
    net.pingAll()
    net.stop()

if __name__ == '__main__':
    simpleTest()
#topos = {'mytopo' : ( lambda n: BinTreeTopo(n) ) }
