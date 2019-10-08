import ryu_ofctl
flow = ryu_ofctl.FlowEntry()
act1 = ryu_ofctl.OutputAction(1)
act2 = ryu_ofctl.OutputAction(2)
act3 = ryu_ofctl.OutputAction(3)

dpid = 0x1
ryu_ofctl.deleteAllFlows(dpid)

flow.in_port = 1
flow.addAction(act2)
ryu_ofctl.insertFlow(dpid,flow)
flow.in_port = 3
ryu_ofctl.insertFlow(dpid,flow)

flow.in_port = 2
flow.addAction(act1)
flow.addAction(act3)
ryu_ofctl.insertFlow(dpid,flow)
