import ryu_ofctl
flow = ryu_ofctl.FlowEntry()
act1 = ryu_ofctl.OutputAction(1)
act2 = ryu_ofctl.OutputAction(2)
act3 = ryu_ofctl.OutputAction(3)

flow.in_port = 1
flow.addAction(act2)
flow.addAction(act3)

dpid = 0x1
ryu_ofctl.insertFlow(dpid,flow)

flow.in_port = 3
flow.addAction(act1)

ryu_ofctl.insertFlow(dpid,flow)