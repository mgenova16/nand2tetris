use std::{env, io};

use vm_translator::config::Config;
use vm_translator::parser::Parser;
use vm_translator::code_writer::CodeWriter;

fn main() -> io::Result<()> {
    let args = env::args();
    let config = Config::new(args)?;

    let mut code_writer = CodeWriter::new(config.asm_file())?;

    let needs_sys_init = config.vm_files()
        .iter()
        .map(|f| f.file_name().unwrap() == "Sys.vm")
        .any(|res| res);

    if needs_sys_init {
        code_writer.write_bootstrap()?;
    }

    for f in config.vm_files() {
        let mut parser = Parser::new(&f)?;
        code_writer.set_filename(&f);

        while parser.has_more_commands() {
            parser.advance()?;
            let command = match parser.command_type() {
                Some(c_type) => c_type,
                None => panic!("Malformed command"),
            };
            code_writer.write(&command)?;
        }
    }

    Ok(())
}
