module ens0_layer6 (input [127:0] M0, output [39:0] M1);

wire [7:0] ens0_layer6_N0_wire = {M0[19], M0[63], M0[102], M0[104], M0[119], M0[122], M0[124], M0[125]};
ens0_layer6_N0 ens0_layer6_N0_inst (.M0(ens0_layer6_N0_wire), .M1(M1[3:0]));

wire [7:0] ens0_layer6_N1_wire = {M0[27], M0[38], M0[47], M0[69], M0[71], M0[82], M0[85], M0[116]};
ens0_layer6_N1 ens0_layer6_N1_inst (.M0(ens0_layer6_N1_wire), .M1(M1[7:4]));

wire [7:0] ens0_layer6_N2_wire = {M0[20], M0[35], M0[42], M0[50], M0[52], M0[81], M0[92], M0[103]};
ens0_layer6_N2 ens0_layer6_N2_inst (.M0(ens0_layer6_N2_wire), .M1(M1[11:8]));

wire [7:0] ens0_layer6_N3_wire = {M0[0], M0[6], M0[34], M0[68], M0[88], M0[97], M0[103], M0[110]};
ens0_layer6_N3 ens0_layer6_N3_inst (.M0(ens0_layer6_N3_wire), .M1(M1[15:12]));

wire [7:0] ens0_layer6_N4_wire = {M0[4], M0[47], M0[53], M0[57], M0[63], M0[64], M0[95], M0[114]};
ens0_layer6_N4 ens0_layer6_N4_inst (.M0(ens0_layer6_N4_wire), .M1(M1[19:16]));

wire [7:0] ens0_layer6_N5_wire = {M0[46], M0[48], M0[57], M0[79], M0[83], M0[100], M0[109], M0[118]};
ens0_layer6_N5 ens0_layer6_N5_inst (.M0(ens0_layer6_N5_wire), .M1(M1[23:20]));

wire [7:0] ens0_layer6_N6_wire = {M0[35], M0[46], M0[64], M0[73], M0[83], M0[89], M0[96], M0[114]};
ens0_layer6_N6 ens0_layer6_N6_inst (.M0(ens0_layer6_N6_wire), .M1(M1[27:24]));

wire [7:0] ens0_layer6_N7_wire = {M0[10], M0[26], M0[41], M0[44], M0[50], M0[71], M0[74], M0[86]};
ens0_layer6_N7 ens0_layer6_N7_inst (.M0(ens0_layer6_N7_wire), .M1(M1[31:28]));

wire [7:0] ens0_layer6_N8_wire = {M0[4], M0[17], M0[22], M0[44], M0[86], M0[106], M0[118], M0[123]};
ens0_layer6_N8 ens0_layer6_N8_inst (.M0(ens0_layer6_N8_wire), .M1(M1[35:32]));

wire [7:0] ens0_layer6_N9_wire = {M0[17], M0[27], M0[57], M0[62], M0[89], M0[94], M0[100], M0[117]};
ens0_layer6_N9 ens0_layer6_N9_inst (.M0(ens0_layer6_N9_wire), .M1(M1[39:36]));

endmodule