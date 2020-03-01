use std::path::PathBuf;

enum Command<'a> {
    Math { cmd: &'a str, n_args: usize },
    Comparison { cmd: &'a str },
    Memory { cmd: &'a str, seg: String, idx: usize },
    NonCommand,
}

pub struct Parser<'a> {
    file: &'a PathBuf,
    comp_count: usize,
}

impl<'a> Parser<'a> {

    pub fn new(file: &'a PathBuf) -> Self {
        Parser { file, comp_count: 0 }
    }

    pub fn translate(&mut self, line: &mut String) -> String {
        let cmd = Self::get_command(line);
        
        match cmd {
            Command::Math { cmd, n_args } => Self::translate_math(cmd, n_args),
            Command::Comparison { cmd } => self.translate_comp(cmd),
            Command::Memory { cmd, seg, idx } => self.translate_mem(cmd, &seg, idx),
            Command::NonCommand => String::new(),
        }
    }

    fn translate_math(cmd: &str, n_args: usize) -> String {
        match n_args {
            1 => format!("@SP\nA=M-1\n{}", cmd),
            2 => format!("@SP\nAM=M-1\nD=M\nA=A-1\n{}", cmd),
            _ => panic!("Incorrect number of args"),
        }
    }

    fn translate_comp(&mut self, cmd: &str) -> String {
        let mut c = Vec::with_capacity(10);
        
        let count = self.comp_count;
        let fname = self.file.file_stem().unwrap().to_str().unwrap();
        let comp_jump = format!("@COMP_JUMP.{}.{}", fname, count);
        let cont_jump = format!("@CONT_JUMP.{}.{}", fname, count);
        let comp_label = format!("(COMP_JUMP.{}.{})", fname, count);
        let cont_label = format!("(CONT_JUMP.{}.{})", fname, count);
        c.extend(vec!["@SP", "AM=M-1", "D=M"]);
        c.extend(vec!["@SP", "A=M-1"]);
        c.push("D=M-D");
        c.push(&comp_jump.as_str());
        c.push(cmd);
        c.extend(vec!["@SP", "A=M-1", "M=0"]);
        c.push(&cont_jump.as_str());
        c.push("0;JMP");
        c.push(&comp_label.as_str());
        c.extend(vec!["@SP", "A=M-1", "M=-1"]);
        c.push(&cont_label);
        self.comp_count += 1;
        c.join("\n")
    }

    fn translate_mem(&self, cmd: &str, segment: &String, index: usize) -> String {
        let mut c = Vec::with_capacity(10);
        
        let seg_addr = self.get_seg_addr(segment, index);
        let seg_addr = seg_addr.split_whitespace().collect::<Vec<_>>();

        match cmd {
            "push" => {
                c.extend(seg_addr);
                match segment.as_str() {
                    "constant" => c.push("D=A"),
                    _ => c.push("D=M"),
                };
                c.extend(vec!["@SP", "M=M+1", "A=M-1", "M=D"]);
            },
            "pop" => {
                match seg_addr.len() {
                    1 => {
                        c.extend(vec!["@SP", "AM=M-1", "D=M"]);
                        c.extend(seg_addr);
                        c.push("M=D");
                    },
                    _ => {
                        c.extend(seg_addr);
                        c.push("D=A");
                        c.extend(vec!["@R13", "M=D"]);
                        c.extend(vec!["@SP", "AM=M-1", "D=M"]);
                        c.extend(vec!["@R13", "A=M", "M=D"]);
                    },
                };
            },
            _ => panic!("Incorrect mem command!"),
        }   
        c.join("\n")
    }

    fn get_command(line: &mut String) -> Command {
        *line = line.trim().split("//").next().unwrap().trim().to_string();
        if line.is_empty() {
            return Command::NonCommand
        }
        let mut iter = line.split_whitespace().map(|s| s.to_string());
        let (c, s, i) = (iter.next().unwrap(), iter.next(), iter.next());
        match c.as_str() {
            "add"  => Command::Math { cmd: "M=M+D", n_args: 2 },
            "sub"  => Command::Math { cmd: "M=M-D", n_args: 2 },
            "neg"  => Command::Math { cmd: "M=-M", n_args: 1 },
            "and"  => Command::Math { cmd: "M=M&D", n_args: 2 },
            "or"   => Command::Math { cmd: "M=M|D", n_args: 2 },
            "not"  => Command::Math { cmd: "M=!M", n_args: 1 },
            "eq"   => Command::Comparison { cmd: "D;JEQ" },
            "lt"   => Command::Comparison { cmd: "D;JLT" },
            "gt"   => Command::Comparison { cmd: "D;JGT" },
            "push" => {
                let cmd = "push";
                let seg = s.unwrap();
                let idx = i.unwrap().parse().unwrap();
                Command::Memory { cmd, seg, idx }
            },
            "pop"  => {
                let cmd = "pop";
                let seg = s.unwrap();
                let idx = i.unwrap().parse().unwrap();
                Command::Memory { cmd, seg, idx }
            }
            _ => panic!("Unknown command: {}", c),
        }
    }

    fn get_seg_addr(&self, segment: &String, index: usize) -> String {
        let fname = self.file.file_stem().unwrap().to_str().unwrap();
        match segment.as_str() {
            "local" => {
                match index {
                    0 => String::from("@LCL A=M"),
                    _ => format!("@LCL D=M @{} A=D+A", index),
                }
            },
            "argument" => {
                match index {
                    0 => String::from("@ARG A=M"),
                    _ => format!("@ARG D=M @{} A=D+A", index),
                }
            },
            "this" => {
                match index {
                    0 => String::from("@THIS A=M"),
                    _ => format!("@THIS D=M @{} A=D+A", index),
                }
            },
            "that" => {
                match index {
                    0 => String::from("@THAT A=M"),
                    _ => format!("@THAT D=M @{} A=D+A", index),
                }
            },
            "pointer" => {
                match index {
                    i if i < 2 => format!("@R{}", 3 + index),
                    _ => panic!("Index out of bounds for pointer: {}", index),
                }
            },
            "temp" => {
                match index {
                    i if i < 8 => format!("@R{}", 5 + index),
                    _ => panic!("Index out of bounds for temp: {}", index),
                }
            },
            "static" => format!("@{}.{}", fname, index),
            "constant" => format!("@{}", index),
            _ => panic!("Bad segment: {}", segment),
        }    
    }
}
