
class VMWriter:
    def __init__(self, f_out):
        self.f_out = f_out

    def __del__(self):
        self.f_out.close()

    def write_arithmetic(self, command):
        self.write_line(command)

    def write_call(self, function_name, n_args):
        self.write_line(f'call {function_name} {n_args}')

    def write_goto(self, label):
        self.write_line(f'goto {label}')

    def write_function(self, function_name, n_locals):
        self.write_line(f'function {function_name} {n_locals}')

    def write_if(self, label):
        self.write_line(f'if-goto {label}')

    def write_label(self, label):
        self.write_line(f'label {label}')

    def write_return(self):
        self.write_line('return')

    def write_pop(self, segment, idx):
        self.write_line(f'pop {segment} {idx}')

    def write_push(self, segment, idx):
        self.write_line(f'push {segment} {idx}')

    def write_line(self, line):
        self.f_out.write(line + '\n')
