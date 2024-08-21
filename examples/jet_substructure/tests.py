from logicnets.nn import averaging_module_verilog

def main():
    print(averaging_module_verilog(2, 3, output_dir="test_verilog"))

if __name__ == "__main__":
    main()
