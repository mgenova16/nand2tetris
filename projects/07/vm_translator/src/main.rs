use std::env;
use std::fs::OpenOptions;
use std::io::{self, BufRead, BufReader, Write};

extern crate vm_translator;
use vm_translator::config::TranslatorFiles;
use vm_translator::parser::Parser;

fn main() -> Result<(), io::Error> {
    let files = TranslatorFiles::new(env::args())?;

    let in_files = files.vm_files();
    let out_file = files.asm_file();

    let mut f_out = OpenOptions::new().write(true).create(true).open(out_file)?;

    for f in in_files {
        let f_in = OpenOptions::new().read(true).open(f)?;
        
        let reader = BufReader::new(f_in);

        let mut parser = Parser::new(f);

        for line in reader.lines() {
            let mut u_line = line.unwrap();
            let translated_line = parser.translate(&mut u_line);
            if let Some(l) = translated_line {
                writeln!(f_out, "{}", l)?;
            }
        }
    }
    Ok(())
}
