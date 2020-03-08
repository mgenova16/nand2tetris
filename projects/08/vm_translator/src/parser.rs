use std::io::{self, Read, BufRead, BufReader};
use std::fs::{File, OpenOptions};
use std::path::PathBuf;

use crate::command::{Command, CommandType};

pub struct Parser<'a, R: Read> {
    reader: BufReader<R>,
    command: Option<Command<'a>>,
}

impl<'a> Parser<'a, File> {
    
    pub fn new(p: &PathBuf) -> io::Result<Self> {
        let file = OpenOptions::new().read(true).open(p)?;
        let reader = BufReader::new(file);
        Ok(Self { reader, command: None })
    }

    pub fn has_more_commands(&mut self) -> bool {
        let buffer = match self.reader.fill_buf() {
            Ok(b) => b,
            Err(_) => panic!("Error reading file"),
        };

        buffer.len() > 0
    }

    pub fn advance(&mut self) -> io::Result<()> {
        let mut line = String::new();
        loop {
            if let Ok(0) = self.reader.read_line(&mut line) {
                self.command = None;  // we've reached EOF
                break;
            }
            line = line.trim().split("//").next().unwrap().trim().to_string();
            if line.is_empty() {
                continue;
            }
            let iter = &mut line.split_whitespace().map(|s| s.to_string());
            let (c, a1, a2) = (iter.next().unwrap(), iter.next(), iter.next());
            self.command = Some(Command::new(c, a1, a2));
            break;
        }
        Ok(())
    }

    pub fn command_type(&self) -> Option<&CommandType> {
        match &self.command {
            Some(command) => Some(&command.command_type),
            None => None
        }
    }
}