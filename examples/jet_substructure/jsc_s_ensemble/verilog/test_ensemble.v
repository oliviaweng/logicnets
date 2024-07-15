module top (input [64*4-1:0] M0, input clk, input rst, output[19:0] M2);

wire [63:0] M0w_0;
wire [19:0] M2_0;
assign M0w_0 = M0[63:0];
polylut0 polylut0_inst (.M0(M0w_0), .clk(clk), .rst(rst), .M2_0(M2_0));

wire [63:0] M0w_1;
wire [19:0] M2_1;
assign M0w_0 = M0[64*2-1:64];
polylut1 polylut1_inst (.M0(M0w_0), .clk(clk), .rst(rst), .M2_0(M2_1));

wire [63:0] M0w_2;
wire [19:0] M2_2;
assign M0w_0 = M0[64*3-1:128];
polylut2 polylut2_inst (.M0(M0w_0), .clk(clk), .rst(rst), .M2_0(M2_2));

wire [63:0] M0w_3;
wire [19:0] M2_3;
assign M0w_0 = M0[64*4-1:64*3];
polylut3 polylut3_inst (.M0(M0w_0), .clk(clk), .rst(rst), .M2_0(M2_3));

assign M2 = M2_0 + M2_1 + M2_2 + M2_3;

endmodule