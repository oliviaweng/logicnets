module layer4 (input [63:0] M0, output [9:0] M1);

wire [5:0] layer4_N0_wire = {M0[25], M0[24], M0[37], M0[36], M0[49], M0[48]};
layer4_N0 layer4_N0_inst (.M0(layer4_N0_wire), .M1(M1[1:0]));

wire [5:0] layer4_N1_wire = {M0[31], M0[30], M0[33], M0[32], M0[51], M0[50]};
layer4_N1 layer4_N1_inst (.M0(layer4_N1_wire), .M1(M1[3:2]));

wire [5:0] layer4_N2_wire = {M0[23], M0[22], M0[37], M0[36], M0[55], M0[54]};
layer4_N2 layer4_N2_inst (.M0(layer4_N2_wire), .M1(M1[5:4]));

wire [5:0] layer4_N3_wire = {M0[17], M0[16], M0[47], M0[46], M0[51], M0[50]};
layer4_N3 layer4_N3_inst (.M0(layer4_N3_wire), .M1(M1[7:6]));

wire [5:0] layer4_N4_wire = {M0[5], M0[4], M0[13], M0[12], M0[47], M0[46]};
layer4_N4 layer4_N4_inst (.M0(layer4_N4_wire), .M1(M1[9:8]));

endmodule