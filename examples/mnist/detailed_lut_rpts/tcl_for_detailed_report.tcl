# 
# File to get utilization results per module
# TODO: Parametrize this file with tcl's $argc or $argv approach
#        Once this is done, you can call vivado with this tcl script like this:
#           vivado -mode tcl -source <this_file.tcl> -tclargs $1 $2 $3
#

#Set variable to point to vivado project (.xpr)
set vivado_xpr "/workspace/logicnets/examples/mnist/mnist_xs_synth/verilog/results_logicnet_0/vivadocompile/vivadocompile.xpr"

#Set variable to point to synthesis run
set synth_run_name "synth_1"

#Set the output file for the detailed report
set output_rpt "/workspace/logicnets/mnist_xs_util_test2.txt"

# Open the project
open_project -read_only $vivado_xpr

# Open/load the desired synthesis run
open_run $synth_run_name

report_utilization -hierarchical -file $output_rpt

exit 