module ens0_layer4 (input [63:0] M0, output [9:0] M1);

wire [5:0] ens0_layer4_N0_wire = {M0[19], M0[18], M0[23], M0[22], M0[33], M0[32]};
ens0_layer4_N0 ens0_layer4_N0_inst (.M0(ens0_layer4_N0_wire), .M1(M1[1:0]));

wire [5:0] ens0_layer4_N1_wire = {M0[11], M0[10], M0[25], M0[24], M0[45], M0[44]};
ens0_layer4_N1 ens0_layer4_N1_inst (.M0(ens0_layer4_N1_wire), .M1(M1[3:2]));

wire [5:0] ens0_layer4_N2_wire = {M0[41], M0[40], M0[47], M0[46], M0[49], M0[48]};
ens0_layer4_N2 ens0_layer4_N2_inst (.M0(ens0_layer4_N2_wire), .M1(M1[5:4]));

wire [5:0] ens0_layer4_N3_wire = {M0[9], M0[8], M0[15], M0[14], M0[37], M0[36]};
ens0_layer4_N3 ens0_layer4_N3_inst (.M0(ens0_layer4_N3_wire), .M1(M1[7:6]));

wire [5:0] ens0_layer4_N4_wire = {M0[5], M0[4], M0[11], M0[10], M0[47], M0[46]};
ens0_layer4_N4 ens0_layer4_N4_inst (.M0(ens0_layer4_N4_wire), .M1(M1[9:8]));

endmodule