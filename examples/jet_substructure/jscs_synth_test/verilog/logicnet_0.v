module logicnet_0 (input [31:0] M0, input clk, input rst, output[9:0] M5);
wire [31:0] M0w;
myreg #(.DataWidth(32)) ens0_layer0_reg (.data_in(M0), .clk(clk), .rst(rst), .data_out(M0w));
wire [127:0] M1;
ens0_layer0 ens0_layer0_inst (.M0(M0w), .M1(M1));
wire [127:0] M1w;
myreg #(.DataWidth(128)) ens0_layer1_reg (.data_in(M1), .clk(clk), .rst(rst), .data_out(M1w));
wire [63:0] M2;
ens0_layer1 ens0_layer1_inst (.M0(M1w), .M1(M2));
wire [63:0] M2w;
myreg #(.DataWidth(64)) ens0_layer2_reg (.data_in(M2), .clk(clk), .rst(rst), .data_out(M2w));
wire [63:0] M3;
ens0_layer2 ens0_layer2_inst (.M0(M2w), .M1(M3));
wire [63:0] M3w;
myreg #(.DataWidth(64)) ens0_layer3_reg (.data_in(M3), .clk(clk), .rst(rst), .data_out(M3w));
wire [63:0] M4;
ens0_layer3 ens0_layer3_inst (.M0(M3w), .M1(M4));
wire [63:0] M4w;
myreg #(.DataWidth(64)) ens0_layer4_reg (.data_in(M4), .clk(clk), .rst(rst), .data_out(M4w));
ens0_layer4 ens0_layer4_inst (.M0(M4w), .M1(M5));

endmodule
