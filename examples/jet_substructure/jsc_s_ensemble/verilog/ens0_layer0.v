module ens0_layer0 (input [31:0] M0, output [127:0] M1);

wire [5:0] ens0_layer0_N0_wire = {M0[3], M0[2], M0[17], M0[16], M0[27], M0[26]};
ens0_layer0_N0 ens0_layer0_N0_inst (.M0(ens0_layer0_N0_wire), .M1(M1[1:0]));

wire [5:0] ens0_layer0_N1_wire = {M0[3], M0[2], M0[11], M0[10], M0[31], M0[30]};
ens0_layer0_N1 ens0_layer0_N1_inst (.M0(ens0_layer0_N1_wire), .M1(M1[3:2]));

wire [5:0] ens0_layer0_N2_wire = {M0[3], M0[2], M0[15], M0[14], M0[25], M0[24]};
ens0_layer0_N2 ens0_layer0_N2_inst (.M0(ens0_layer0_N2_wire), .M1(M1[5:4]));

wire [5:0] ens0_layer0_N3_wire = {M0[5], M0[4], M0[17], M0[16], M0[19], M0[18]};
ens0_layer0_N3 ens0_layer0_N3_inst (.M0(ens0_layer0_N3_wire), .M1(M1[7:6]));

wire [5:0] ens0_layer0_N4_wire = {M0[25], M0[24], M0[27], M0[26], M0[29], M0[28]};
ens0_layer0_N4 ens0_layer0_N4_inst (.M0(ens0_layer0_N4_wire), .M1(M1[9:8]));

wire [5:0] ens0_layer0_N5_wire = {M0[9], M0[8], M0[11], M0[10], M0[19], M0[18]};
ens0_layer0_N5 ens0_layer0_N5_inst (.M0(ens0_layer0_N5_wire), .M1(M1[11:10]));

wire [5:0] ens0_layer0_N6_wire = {M0[15], M0[14], M0[21], M0[20], M0[29], M0[28]};
ens0_layer0_N6 ens0_layer0_N6_inst (.M0(ens0_layer0_N6_wire), .M1(M1[13:12]));

wire [5:0] ens0_layer0_N7_wire = {M0[7], M0[6], M0[9], M0[8], M0[13], M0[12]};
ens0_layer0_N7 ens0_layer0_N7_inst (.M0(ens0_layer0_N7_wire), .M1(M1[15:14]));

wire [5:0] ens0_layer0_N8_wire = {M0[9], M0[8], M0[25], M0[24], M0[31], M0[30]};
ens0_layer0_N8 ens0_layer0_N8_inst (.M0(ens0_layer0_N8_wire), .M1(M1[17:16]));

wire [5:0] ens0_layer0_N9_wire = {M0[1], M0[0], M0[23], M0[22], M0[29], M0[28]};
ens0_layer0_N9 ens0_layer0_N9_inst (.M0(ens0_layer0_N9_wire), .M1(M1[19:18]));

wire [5:0] ens0_layer0_N10_wire = {M0[9], M0[8], M0[17], M0[16], M0[25], M0[24]};
ens0_layer0_N10 ens0_layer0_N10_inst (.M0(ens0_layer0_N10_wire), .M1(M1[21:20]));

wire [5:0] ens0_layer0_N11_wire = {M0[3], M0[2], M0[9], M0[8], M0[27], M0[26]};
ens0_layer0_N11 ens0_layer0_N11_inst (.M0(ens0_layer0_N11_wire), .M1(M1[23:22]));

wire [5:0] ens0_layer0_N12_wire = {M0[5], M0[4], M0[15], M0[14], M0[25], M0[24]};
ens0_layer0_N12 ens0_layer0_N12_inst (.M0(ens0_layer0_N12_wire), .M1(M1[25:24]));

wire [5:0] ens0_layer0_N13_wire = {M0[11], M0[10], M0[13], M0[12], M0[27], M0[26]};
ens0_layer0_N13 ens0_layer0_N13_inst (.M0(ens0_layer0_N13_wire), .M1(M1[27:26]));

wire [5:0] ens0_layer0_N14_wire = {M0[11], M0[10], M0[13], M0[12], M0[15], M0[14]};
ens0_layer0_N14 ens0_layer0_N14_inst (.M0(ens0_layer0_N14_wire), .M1(M1[29:28]));

wire [5:0] ens0_layer0_N15_wire = {M0[3], M0[2], M0[27], M0[26], M0[31], M0[30]};
ens0_layer0_N15 ens0_layer0_N15_inst (.M0(ens0_layer0_N15_wire), .M1(M1[31:30]));

wire [5:0] ens0_layer0_N16_wire = {M0[11], M0[10], M0[23], M0[22], M0[27], M0[26]};
ens0_layer0_N16 ens0_layer0_N16_inst (.M0(ens0_layer0_N16_wire), .M1(M1[33:32]));

wire [5:0] ens0_layer0_N17_wire = {M0[1], M0[0], M0[17], M0[16], M0[23], M0[22]};
ens0_layer0_N17 ens0_layer0_N17_inst (.M0(ens0_layer0_N17_wire), .M1(M1[35:34]));

wire [5:0] ens0_layer0_N18_wire = {M0[5], M0[4], M0[7], M0[6], M0[13], M0[12]};
ens0_layer0_N18 ens0_layer0_N18_inst (.M0(ens0_layer0_N18_wire), .M1(M1[37:36]));

wire [5:0] ens0_layer0_N19_wire = {M0[7], M0[6], M0[13], M0[12], M0[15], M0[14]};
ens0_layer0_N19 ens0_layer0_N19_inst (.M0(ens0_layer0_N19_wire), .M1(M1[39:38]));

wire [5:0] ens0_layer0_N20_wire = {M0[3], M0[2], M0[15], M0[14], M0[27], M0[26]};
ens0_layer0_N20 ens0_layer0_N20_inst (.M0(ens0_layer0_N20_wire), .M1(M1[41:40]));

wire [5:0] ens0_layer0_N21_wire = {M0[9], M0[8], M0[17], M0[16], M0[27], M0[26]};
ens0_layer0_N21 ens0_layer0_N21_inst (.M0(ens0_layer0_N21_wire), .M1(M1[43:42]));

wire [5:0] ens0_layer0_N22_wire = {M0[13], M0[12], M0[19], M0[18], M0[21], M0[20]};
ens0_layer0_N22 ens0_layer0_N22_inst (.M0(ens0_layer0_N22_wire), .M1(M1[45:44]));

wire [5:0] ens0_layer0_N23_wire = {M0[3], M0[2], M0[11], M0[10], M0[27], M0[26]};
ens0_layer0_N23 ens0_layer0_N23_inst (.M0(ens0_layer0_N23_wire), .M1(M1[47:46]));

wire [5:0] ens0_layer0_N24_wire = {M0[1], M0[0], M0[9], M0[8], M0[27], M0[26]};
ens0_layer0_N24 ens0_layer0_N24_inst (.M0(ens0_layer0_N24_wire), .M1(M1[49:48]));

wire [5:0] ens0_layer0_N25_wire = {M0[5], M0[4], M0[17], M0[16], M0[31], M0[30]};
ens0_layer0_N25 ens0_layer0_N25_inst (.M0(ens0_layer0_N25_wire), .M1(M1[51:50]));

wire [5:0] ens0_layer0_N26_wire = {M0[5], M0[4], M0[23], M0[22], M0[31], M0[30]};
ens0_layer0_N26 ens0_layer0_N26_inst (.M0(ens0_layer0_N26_wire), .M1(M1[53:52]));

wire [5:0] ens0_layer0_N27_wire = {M0[11], M0[10], M0[17], M0[16], M0[27], M0[26]};
ens0_layer0_N27 ens0_layer0_N27_inst (.M0(ens0_layer0_N27_wire), .M1(M1[55:54]));

wire [5:0] ens0_layer0_N28_wire = {M0[1], M0[0], M0[23], M0[22], M0[31], M0[30]};
ens0_layer0_N28 ens0_layer0_N28_inst (.M0(ens0_layer0_N28_wire), .M1(M1[57:56]));

wire [5:0] ens0_layer0_N29_wire = {M0[13], M0[12], M0[21], M0[20], M0[25], M0[24]};
ens0_layer0_N29 ens0_layer0_N29_inst (.M0(ens0_layer0_N29_wire), .M1(M1[59:58]));

wire [5:0] ens0_layer0_N30_wire = {M0[15], M0[14], M0[21], M0[20], M0[27], M0[26]};
ens0_layer0_N30 ens0_layer0_N30_inst (.M0(ens0_layer0_N30_wire), .M1(M1[61:60]));

wire [5:0] ens0_layer0_N31_wire = {M0[1], M0[0], M0[5], M0[4], M0[23], M0[22]};
ens0_layer0_N31 ens0_layer0_N31_inst (.M0(ens0_layer0_N31_wire), .M1(M1[63:62]));

wire [5:0] ens0_layer0_N32_wire = {M0[5], M0[4], M0[23], M0[22], M0[27], M0[26]};
ens0_layer0_N32 ens0_layer0_N32_inst (.M0(ens0_layer0_N32_wire), .M1(M1[65:64]));

wire [5:0] ens0_layer0_N33_wire = {M0[3], M0[2], M0[9], M0[8], M0[23], M0[22]};
ens0_layer0_N33 ens0_layer0_N33_inst (.M0(ens0_layer0_N33_wire), .M1(M1[67:66]));

wire [5:0] ens0_layer0_N34_wire = {M0[3], M0[2], M0[19], M0[18], M0[29], M0[28]};
ens0_layer0_N34 ens0_layer0_N34_inst (.M0(ens0_layer0_N34_wire), .M1(M1[69:68]));

wire [5:0] ens0_layer0_N35_wire = {M0[11], M0[10], M0[15], M0[14], M0[27], M0[26]};
ens0_layer0_N35 ens0_layer0_N35_inst (.M0(ens0_layer0_N35_wire), .M1(M1[71:70]));

wire [5:0] ens0_layer0_N36_wire = {M0[1], M0[0], M0[17], M0[16], M0[21], M0[20]};
ens0_layer0_N36 ens0_layer0_N36_inst (.M0(ens0_layer0_N36_wire), .M1(M1[73:72]));

wire [5:0] ens0_layer0_N37_wire = {M0[11], M0[10], M0[29], M0[28], M0[31], M0[30]};
ens0_layer0_N37 ens0_layer0_N37_inst (.M0(ens0_layer0_N37_wire), .M1(M1[75:74]));

wire [5:0] ens0_layer0_N38_wire = {M0[5], M0[4], M0[27], M0[26], M0[29], M0[28]};
ens0_layer0_N38 ens0_layer0_N38_inst (.M0(ens0_layer0_N38_wire), .M1(M1[77:76]));

wire [5:0] ens0_layer0_N39_wire = {M0[15], M0[14], M0[21], M0[20], M0[23], M0[22]};
ens0_layer0_N39 ens0_layer0_N39_inst (.M0(ens0_layer0_N39_wire), .M1(M1[79:78]));

wire [5:0] ens0_layer0_N40_wire = {M0[5], M0[4], M0[19], M0[18], M0[25], M0[24]};
ens0_layer0_N40 ens0_layer0_N40_inst (.M0(ens0_layer0_N40_wire), .M1(M1[81:80]));

wire [5:0] ens0_layer0_N41_wire = {M0[3], M0[2], M0[5], M0[4], M0[25], M0[24]};
ens0_layer0_N41 ens0_layer0_N41_inst (.M0(ens0_layer0_N41_wire), .M1(M1[83:82]));

wire [5:0] ens0_layer0_N42_wire = {M0[19], M0[18], M0[27], M0[26], M0[29], M0[28]};
ens0_layer0_N42 ens0_layer0_N42_inst (.M0(ens0_layer0_N42_wire), .M1(M1[85:84]));

wire [5:0] ens0_layer0_N43_wire = {M0[3], M0[2], M0[19], M0[18], M0[29], M0[28]};
ens0_layer0_N43 ens0_layer0_N43_inst (.M0(ens0_layer0_N43_wire), .M1(M1[87:86]));

wire [5:0] ens0_layer0_N44_wire = {M0[1], M0[0], M0[3], M0[2], M0[23], M0[22]};
ens0_layer0_N44 ens0_layer0_N44_inst (.M0(ens0_layer0_N44_wire), .M1(M1[89:88]));

wire [5:0] ens0_layer0_N45_wire = {M0[1], M0[0], M0[3], M0[2], M0[23], M0[22]};
ens0_layer0_N45 ens0_layer0_N45_inst (.M0(ens0_layer0_N45_wire), .M1(M1[91:90]));

wire [5:0] ens0_layer0_N46_wire = {M0[7], M0[6], M0[9], M0[8], M0[19], M0[18]};
ens0_layer0_N46 ens0_layer0_N46_inst (.M0(ens0_layer0_N46_wire), .M1(M1[93:92]));

wire [5:0] ens0_layer0_N47_wire = {M0[7], M0[6], M0[17], M0[16], M0[21], M0[20]};
ens0_layer0_N47 ens0_layer0_N47_inst (.M0(ens0_layer0_N47_wire), .M1(M1[95:94]));

wire [5:0] ens0_layer0_N48_wire = {M0[5], M0[4], M0[25], M0[24], M0[31], M0[30]};
ens0_layer0_N48 ens0_layer0_N48_inst (.M0(ens0_layer0_N48_wire), .M1(M1[97:96]));

wire [5:0] ens0_layer0_N49_wire = {M0[1], M0[0], M0[15], M0[14], M0[25], M0[24]};
ens0_layer0_N49 ens0_layer0_N49_inst (.M0(ens0_layer0_N49_wire), .M1(M1[99:98]));

wire [5:0] ens0_layer0_N50_wire = {M0[1], M0[0], M0[5], M0[4], M0[13], M0[12]};
ens0_layer0_N50 ens0_layer0_N50_inst (.M0(ens0_layer0_N50_wire), .M1(M1[101:100]));

wire [5:0] ens0_layer0_N51_wire = {M0[1], M0[0], M0[3], M0[2], M0[27], M0[26]};
ens0_layer0_N51 ens0_layer0_N51_inst (.M0(ens0_layer0_N51_wire), .M1(M1[103:102]));

wire [5:0] ens0_layer0_N52_wire = {M0[11], M0[10], M0[19], M0[18], M0[27], M0[26]};
ens0_layer0_N52 ens0_layer0_N52_inst (.M0(ens0_layer0_N52_wire), .M1(M1[105:104]));

wire [5:0] ens0_layer0_N53_wire = {M0[13], M0[12], M0[15], M0[14], M0[29], M0[28]};
ens0_layer0_N53 ens0_layer0_N53_inst (.M0(ens0_layer0_N53_wire), .M1(M1[107:106]));

wire [5:0] ens0_layer0_N54_wire = {M0[7], M0[6], M0[13], M0[12], M0[27], M0[26]};
ens0_layer0_N54 ens0_layer0_N54_inst (.M0(ens0_layer0_N54_wire), .M1(M1[109:108]));

wire [5:0] ens0_layer0_N55_wire = {M0[1], M0[0], M0[5], M0[4], M0[25], M0[24]};
ens0_layer0_N55 ens0_layer0_N55_inst (.M0(ens0_layer0_N55_wire), .M1(M1[111:110]));

wire [5:0] ens0_layer0_N56_wire = {M0[1], M0[0], M0[7], M0[6], M0[19], M0[18]};
ens0_layer0_N56 ens0_layer0_N56_inst (.M0(ens0_layer0_N56_wire), .M1(M1[113:112]));

wire [5:0] ens0_layer0_N57_wire = {M0[9], M0[8], M0[19], M0[18], M0[27], M0[26]};
ens0_layer0_N57 ens0_layer0_N57_inst (.M0(ens0_layer0_N57_wire), .M1(M1[115:114]));

wire [5:0] ens0_layer0_N58_wire = {M0[1], M0[0], M0[21], M0[20], M0[29], M0[28]};
ens0_layer0_N58 ens0_layer0_N58_inst (.M0(ens0_layer0_N58_wire), .M1(M1[117:116]));

wire [5:0] ens0_layer0_N59_wire = {M0[5], M0[4], M0[7], M0[6], M0[17], M0[16]};
ens0_layer0_N59 ens0_layer0_N59_inst (.M0(ens0_layer0_N59_wire), .M1(M1[119:118]));

wire [5:0] ens0_layer0_N60_wire = {M0[5], M0[4], M0[17], M0[16], M0[19], M0[18]};
ens0_layer0_N60 ens0_layer0_N60_inst (.M0(ens0_layer0_N60_wire), .M1(M1[121:120]));

wire [5:0] ens0_layer0_N61_wire = {M0[5], M0[4], M0[23], M0[22], M0[25], M0[24]};
ens0_layer0_N61 ens0_layer0_N61_inst (.M0(ens0_layer0_N61_wire), .M1(M1[123:122]));

wire [5:0] ens0_layer0_N62_wire = {M0[9], M0[8], M0[11], M0[10], M0[15], M0[14]};
ens0_layer0_N62 ens0_layer0_N62_inst (.M0(ens0_layer0_N62_wire), .M1(M1[125:124]));

wire [5:0] ens0_layer0_N63_wire = {M0[3], M0[2], M0[17], M0[16], M0[27], M0[26]};
ens0_layer0_N63 ens0_layer0_N63_inst (.M0(ens0_layer0_N63_wire), .M1(M1[127:126]));

endmodule