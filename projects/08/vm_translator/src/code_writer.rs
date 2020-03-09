use std::fmt::Display;
use std::fs::{File, OpenOptions};
use std::io::{self, BufWriter, Write};
use std::path::PathBuf;

use crate::command::{
    CommandType, MathCommand, ComparisonCommand,
    PushCommand, PopCommand, CallCommand,
    ProgramFlowCommand, FunctionDefCommand,
};

pub struct CodeWriter<W: Write> {
    writer: BufWriter<W>,
    filename: String,
    comp_count: usize,
    call_count: usize,
}

impl CodeWriter<File> {
    pub fn new(out_file: &PathBuf) -> io::Result<Self> {
        let filename = String::new();

        let file = OpenOptions::new()
            .write(true)
            .create(true)
            .open(out_file)?;

        let writer = BufWriter::new(file);
        let comp_count = 0;
        let call_count = 0;
        Ok(Self { writer, filename, comp_count, call_count })
    }

    pub fn set_filename(&mut self, p: &PathBuf) {
        self.filename = Self::path_buf_to_string(p);
    }

    fn path_buf_to_string(p: &PathBuf) -> String {
        match p.file_stem() {
            Some(stem) => match stem.to_os_string().into_string() {
                Ok(filename) => filename,
                Err(_) => panic!("Must use UTF-8 encoded file names"),
            },
            None => panic!("Unable to determine asm file name"),
        }
    }
}

impl<W: Write> CodeWriter<W> {
    
    pub fn write(&mut self, command_type: &CommandType) -> io::Result<()> {
        Ok(
            match command_type {
                CommandType::Math { command } => self.write_math(&command)?,
                CommandType::Comparison { command } => self.write_comparison(&command)?,
                CommandType::Push { command } => self.write_push(&command)?,
                CommandType::Pop { command } => self.write_pop(&command)?,
                CommandType::ProgramFlow { command } => self.write_program_flow(&command)?,
                CommandType::FunctionDef { command } => self.write_function_def(&command)?,
                CommandType::Call { command } => self.write_call(&command)?,
                CommandType::Return => self.write_return()?,
            }
        )
    }

    fn write_math(&mut self, command: &MathCommand) -> io::Result<()> {
        let n_args = command.n_args();
        self.write_line("@SP")?;

        if n_args == 1 {
            self.write_line("A=M-1")?;
        } else if n_args == 2 {
            self.write_line("AM=M-1")?;
            self.write_line("D=M")?;
            self.write_line("A=A-1")?;
        } else {
            panic!("Invalid number of args for math command");
        }

        self.write_line(command.asm_op())?;
        Ok(())
    }

    fn write_comparison(&mut self, command: &ComparisonCommand) -> io::Result<()> {
        
        let true_jump_addr = format!("@JUMP_IF_TRUE.{}", self.comp_count);
        let true_jump_label = format!("(JUMP_IF_TRUE.{})", self.comp_count);
        let false_jump_addr = format!("@JUMP_IF_FALSE.{}", self.comp_count);
        let false_jump_label = format!("(JUMP_IF_FALSE.{})", self.comp_count);

        self.write_line("@SP")?;
        self.write_line("AM=M-1")?;
        self.write_line("D=M")?;
        self.write_line("@SP")?;
        self.write_line("A=M-1")?;
        self.write_line("D=M-D")?;
        self.write_line(true_jump_addr)?;
        self.write_line(command.asm_op())?;
        self.write_line("@SP")?;
        self.write_line("A=M-1")?;
        self.write_line("M=0")?;
        self.write_line(false_jump_addr)?;
        self.write_line("0;JMP")?;
        self.write_line(true_jump_label)?;
        self.write_line("@SP")?;
        self.write_line("A=M-1")?;
        self.write_line("M=-1")?;
        self.write_line(false_jump_label)?;

        self.comp_count += 1;

        Ok(())
    }

    fn write_push(&mut self, command: &PushCommand) -> io::Result<()> {
        let seg = command.segment();
        let idx = command.index();
        let segment_address = self.get_segment_address(seg, idx);

        self.write_line(segment_address)?;
        if seg == "constant" {
            self.write_line("D=A")?;
        } else {
            self.write_line("D=M")?;
        }
        self.write_line("@SP")?;
        self.write_line("M=M+1")?;
        self.write_line("A=M-1")?;
        self.write_line("M=D")?;


        Ok(())
    }

    fn write_pop(&mut self, command: &PopCommand) -> io::Result<()> {
        let seg = command.segment();
        let idx = command.index();

        let segment_address = self.get_segment_address(seg, idx);
        
        match seg.as_str() {
            "local" | "argument" | "this" | "that" => {
                self.write_line(segment_address)?;
                self.write_line("D=A")?;
                self.write_line("@R13")?;
                self.write_line("M=D")?;
                self.write_line("@SP")?;
                self.write_line("AM=M-1")?;
                self.write_line("D=M")?;
                self.write_line("@R13")?;
                self.write_line("A=M")?;
                self.write_line("M=D")?;
            },
            "pointer" | "temp" | "static" | "constant" => {
                self.write_line("@SP")?;
                self.write_line("AM=M-1")?;
                self.write_line("D=M")?;
                self.write_line(segment_address)?;
                self.write_line("M=D")?;
            },
            _ => panic!("Invalid segment"),
        };

        Ok(())
    }

    fn write_program_flow(&mut self, command: &ProgramFlowCommand) -> io::Result<()> {
        let c_type = command.command();
        let label = command.label();
        let out_label = match c_type.as_str() {
            "label" => format!("({}${})", self.filename, label),
            "goto" => format!("@{}${}", self.filename, label),
            "if-goto" => format!("@{}${}", self.filename, label),
            _ => panic!("Invalid program flow command: {}", c_type),
        };

        if c_type == "if-goto" {
            self.write_line("@SP")?;
            self.write_line("AM=M-1")?;
            self.write_line("D=M")?;
        }

        self.write_line(out_label)?;

        if c_type == "if-goto" {
            self.write_line("D;JNE")?;
        } else if c_type == "goto" {
            self.write_line("0;JMP")?;
        }

        Ok(())
    }

    fn write_function_def(&mut self, command: &FunctionDefCommand) -> io::Result<()>  {
        let n = command.n_locals();
        let f_label = format!("({})", command.function_name());
        self.write_line(f_label)?;

        // push 0 for each local arg
        for _ in 0..n {
            self.write_line("@SP")?;
            self.write_line("M=M+1")?;
            self.write_line("A=M-1")?;
            self.write_line("M=0")?;
        }

        Ok(())
    }

    fn write_call(&mut self, command: &CallCommand) -> io::Result<()>  {
        let frame_addrs = ["@LCL", "@ARG", "@THIS", "@THAT"];
        let count = self.call_count;
        let func_name = command.function_name();
        let n_args = command.n_args();
        let return_label = format!("{}_RETURN.{}", func_name, count);
        let function_label = format!("@{}", func_name);

        // push return address
        self.write_line(format!("@{}", return_label))?;
        self.write_line("D=A")?;
        self.write_line("@SP")?;
        self.write_line("M=M+1")?;
        self.write_line("A=M-1")?;
        self.write_line("M=D")?;

        // push LCL, ARG, THIS, THAT
        for addr in frame_addrs.iter() {
            self.write_line(addr)?;
            self.write_line("D=M")?;
            self.write_line("@SP")?;
            self.write_line("M=M+1")?;
            self.write_line("A=M-1")?;
            self.write_line("M=D")?;
        }

        // LCL = SP
        self.write_line("@SP")?;
        self.write_line("D=M")?;
        self.write_line("@LCL")?;
        self.write_line("M=D")?;
        
        // ARG = SP - 5 - n_args
        self.write_line(format!("@{}", n_args + 5))?;
        self.write_line("D=D-A")?;
        self.write_line("@ARG")?;
        self.write_line("M=D")?;

        // go to function
        self.write_line(function_label)?;
        self.write_line("0;JMP")?;

        // return
        self.write_line(format!("({})", return_label))?;

        self.call_count += 1;

        Ok(())
    }

    fn write_return(&mut self) -> io::Result<()> {
        
        let frame_addrs = ["@THAT", "@THIS", "@ARG", "@LCL"];
        let tmp_frame = "@R13";
        let tmp_ret = "@R14";

        // FRAME = LCL
        self.write_line("@LCL")?;
        self.write_line("D=M")?;
        self.write_line(tmp_frame)?;
        self.write_line("M=D")?;

        // RET = *(FRAME - 5)
        self.write_line(tmp_frame)?;
        self.write_line("D=M")?;
        self.write_line("@5")?;
        self.write_line("A=D-A")?;
        self.write_line("D=M")?;
        self.write_line(tmp_ret)?;
        self.write_line("M=D")?;

        // *ARG = pop()
        self.write_line("@SP")?;
        self.write_line("AM=M-1")?;
        self.write_line("D=M")?;
        self.write_line("@ARG")?;
        self.write_line("A=M")?;
        self.write_line("M=D")?;

        // SP = ARG + 1
        self.write_line("@ARG")?;
        self.write_line("D=M")?;
        self.write_line("@SP")?;
        self.write_line("M=D+1")?;

        // Restore THAT, THIS, ARG, LCL of caller
        for (i, addr) in frame_addrs.iter().enumerate() {
            self.write_line(tmp_frame)?;
            self.write_line("D=M")?;
            self.write_line(format!("@{}", i + 1))?;
            self.write_line("A=D-A")?;
            self.write_line("D=M")?;
            self.write_line(addr)?;
            self.write_line("M=D")?;
        }

        // go to return address
        self.write_line(tmp_ret)?;
        self.write_line("A=M")?;
        self.write_line("0;JMP")?;

        Ok(())
    }
   
    pub fn write_bootstrap(&mut self) -> io::Result<()> {
        self.write_line("@256")?;
        self.write_line("D=A")?;
        self.write_line("@SP")?;
        self.write_line("M=D")?;
        
        let function_name = String::from("Sys.init");
        let n_args = 0;
        let command = CallCommand::new(function_name, n_args);

        self.write_call( &command )?;

        Ok(())
    }

    fn write_line<T: Display>(&mut self, line: T) -> io::Result<()> {
        writeln!(&mut self.writer, "{}", line)?;
        Ok(())
    }

    fn get_segment_address(&self, seg: &String, idx: usize) -> String {
        match seg.as_str() {
            "local" | "argument" | "this" | "that" => {
                let addr = Self::seg_to_addr(seg);
                match idx {
                    0 => format!("{}\nA=M", addr),
                    _ => format!("{}\nD=M\n@{}\nA=D+A", addr, idx),
                }
            },
            "pointer" => {
                match idx {
                    _ if idx < 2 => format!("@{}", 3 + idx),
                    _ => panic!("Invalid index for pointer: {}", idx),
                }
            },
            "temp" => {
                match idx {
                    _ if idx < 8 => format!("@{}", 5 + idx),
                    _ => panic!("Invalid index for temp: {}", idx),
                }
            },
            "static" => format!("@{}.{}", self.filename, idx),
            "constant" => format!("@{}", idx),
            _ => panic!("Invalid segment: {}", seg),
        }
    }
    
    fn seg_to_addr(seg: &String) -> &str {
        match seg.as_str() {
            "local" => "@LCL",
            "argument" => "@ARG",
            "this" => "@THIS",
            "that" => "@THAT",
            _ => panic!("That segment has no constant segment"),
        }
    }
}
