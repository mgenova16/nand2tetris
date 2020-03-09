pub struct MathCommand<'a> {
    pub asm_op: &'a str,
    pub n_args: usize,
}

impl<'a> MathCommand<'a> {
    pub fn new(cmd: String) -> Self {
        match cmd.as_str() {
            "add" => Self { asm_op: "M=M+D", n_args: 2},
            "sub" => Self { asm_op: "M=M-D", n_args: 2},
            "neg" => Self { asm_op: "M=-M",  n_args: 1},
            "and" => Self { asm_op: "M=M&D", n_args: 2},
            "or"  => Self { asm_op: "M=M|D", n_args: 2},
            "not" => Self { asm_op: "M=!M",  n_args: 1},
            _ => panic!("Unknown math command: {}", cmd),
        }
    }

    pub fn asm_op(&self) -> String {
        self.asm_op.to_string()
    }

    pub fn n_args(&self) -> usize {
        self.n_args
    }
}

pub struct ComparisonCommand<'a> {
    asm_op: &'a str,
}

impl<'a> ComparisonCommand<'a> {
    pub fn new(cmd: String) -> Self {
        let asm_op = match cmd.as_str() {
            "eq" => "D;JEQ",
            "lt" => "D;JLT",
            "gt" => "D;JGT",
            _ => panic!("Unknown comparison command: {}", cmd),
        };
        Self { asm_op }
    }

    pub fn asm_op(&self) -> String {
        self.asm_op.to_string()
    }
}

pub struct PushCommand {
    segment: String,
    index: usize,
}

impl PushCommand {
    pub fn new(segment: String, index: usize) -> Self {
        Self { segment, index }
    }

    pub fn segment(&self) -> &String {
        &self.segment
    }

    pub fn index(&self) -> usize {
        self.index
    }
}

pub struct PopCommand {
    segment: String,
    index: usize,
}

impl PopCommand {
    pub fn new(segment: String, index: usize) -> Self {
        Self { segment, index }
    }

    pub fn segment(&self) -> &String {
        &self.segment
    }

    pub fn index(&self) -> usize {
        self.index
    }
}

pub struct ProgramFlowCommand {
    cmd: String,
    label: String,
}

impl ProgramFlowCommand {
    pub fn new(cmd: String, label: String) -> Self {
        Self { cmd, label }
    }

    pub fn command(&self) -> &String {
        &self.cmd
    }

    pub fn label(&self) -> &String {
        &self.label
    }
}

pub struct FunctionDefCommand {
    function_name: String,
    n_locals: usize,
}

impl FunctionDefCommand {
    pub fn new(function_name: String, n_locals: usize) -> Self {
        Self { function_name, n_locals }
    }

    pub fn function_name(&self) -> &String {
        &self.function_name
    }

    pub fn n_locals(&self) -> usize {
        self.n_locals
    }
}

pub struct CallCommand {
    function_name: String,
    n_args: usize,
}

impl CallCommand {
    pub fn new(function_name: String, n_args: usize) -> Self {
        Self { function_name, n_args }
    }

    pub fn function_name(&self) -> &String {
        &self.function_name
    }

    pub fn n_args(&self) -> usize {
        self.n_args
    }
}

pub struct ReturnCommand;

pub enum CommandType<'a> {
    Math { command: MathCommand<'a> },
    Comparison { command: ComparisonCommand<'a> },
    Push { command: PushCommand },
    Pop { command: PopCommand },
    ProgramFlow { command: ProgramFlowCommand },
    FunctionDef { command: FunctionDefCommand },
    Call { command: CallCommand },
    Return,
}

pub struct Command<'a> {
    pub command_type: CommandType<'a>,
}

impl<'a> Command<'a> {
    pub fn new(c: String, arg1: Option<String>, arg2: Option<String>) -> Self {
        match c.as_str() {
            "add" | "sub" | "neg" | "and" | "or" | "not" => {
                let cmd = MathCommand::new(c);
                Self { command_type: CommandType::Math { command: cmd } }
            },
            "eq" | "lt" | "gt" => {
                let cmd = ComparisonCommand::new(c);
                Self { command_type: CommandType::Comparison { command: cmd } }
            },
            "push" | "pop" => {
                let segment = match arg1 {
                    Some(s) => s,
                    None => panic!("No segment given for push command"),
                };
                let index = match arg2 {
                    Some(i) => match i.parse() {
                        Ok(idx) => idx,
                        Err(_) => panic!("Invalid index for push command"),
                    },
                    None => panic!("No index given for push command"),
                };
                match c.as_str() {
                    "push" => {
                        let cmd = PushCommand::new(segment, index);
                        Self { command_type: CommandType::Push { command: cmd } }
                    }
                    "pop" => {
                        let cmd = PopCommand::new(segment, index);
                        Self { command_type: CommandType::Pop { command: cmd } }
                    }
                    _ => panic!("Unknown push/pop command: {}", c),
                }
            },
            "label" | "goto" | "if-goto" => {
                let label = match arg1 {
                    Some(arg) => arg,
                    None => panic!("No label given for program flow command"),
                };
                let cmd = ProgramFlowCommand::new(c, label);
                Self { command_type: CommandType::ProgramFlow { command: cmd } }
            },
            "function" => {
                let function_name = match arg1 {
                    Some(name) => name,
                    None => panic!("No function name given for function def"),
                };
                let n_locals = match arg2 {
                    Some(n) => match n.parse() {
                        Ok(n) => n,
                        Err(_) => panic!("Invalid n_locals for function"),
                    },
                    None => panic!("No n locals given for function def"),
                };
                let cmd = FunctionDefCommand::new(function_name, n_locals);
                Self { command_type: CommandType::FunctionDef { command: cmd } }
            },
            "call" => {
                let function_name = match arg1 {
                    Some(name) => name,
                    None => panic!("No function name given for call"),
                };
                let n_args = match arg2 {
                    Some(n) => match n.parse() {
                        Ok(n) => n,
                        Err(_) => panic!("Invalid n_args for call"),
                    },
                    None => panic!("No n_args given for call"),
                };
                let cmd = CallCommand::new(function_name, n_args);
                Self { command_type: CommandType::Call { command: cmd } }
            },
            "return" => Self { command_type: CommandType::Return },
            _ => panic!("Unknown command: {}", c),
        }
    }
}
