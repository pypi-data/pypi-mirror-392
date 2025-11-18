module RRTraceTop;

<%-toplevel%> top();

initial begin
    $dumpfile("waves.vcd");
    $dumpvars();
end


endmodule