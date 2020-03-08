use std::{env, fs, io};
use std::path::PathBuf;

pub struct Config {
    vm_files: Vec<PathBuf>,
    asm_file: PathBuf,
}

impl Config {

    pub fn new(mut args: env::Args) -> io::Result<Self> {
        let script = args.next().unwrap();
        let in_file = match args.next() {
            Some(arg) => arg,
            None => panic!("Usage: {} <vm file or directory>", script),
        };

        let p = PathBuf::from(&in_file);
        let metadata = fs::metadata(&p)?;

        match metadata.is_dir() {
            true => Self::from_directory(&p),
            false => Self::from_file(&p),
        }
    }

    fn from_directory(p: &PathBuf) -> io::Result<Self> {
        let vm_files = fs::read_dir(p)?
            .filter_map(|res| res.ok())
            .map(|f| f.path())
            .filter(|f| Self::is_vm_file(&f))
            .collect();

        let asm_file_name = match p.file_name() {
            Some(n) => n,
            None => panic!("Unable to determine filename from {:?}", p),
        };

        let mut asm_file = p.join(asm_file_name);
        asm_file.set_extension("asm");

        Ok(Self { vm_files, asm_file })
    }

    fn from_file(p: &PathBuf) -> io::Result<Self> {
        if !Self::is_vm_file(p) {
            panic!("Must provide .vm file");
        }
        let vm_files = vec![p.clone()];
        let asm_file = p.with_extension("asm");

        Ok(Self { vm_files, asm_file })
    }

    fn is_vm_file(p: &PathBuf) -> bool {
        p.is_file() && p.extension().map(|e| e == "vm").unwrap_or(false)
    }

    pub fn vm_files(&self) -> &Vec<PathBuf> {
        &self.vm_files
    }

    pub fn asm_file(&self) -> &PathBuf {
        &self.asm_file
    }
}
