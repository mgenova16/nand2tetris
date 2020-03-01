use std::{env, fs, io, path::PathBuf};

pub struct TranslatorFiles {
    vm_files: Vec<PathBuf>,
    asm_file: PathBuf,
}

impl TranslatorFiles {

    pub fn new(mut args: env::Args) -> Result<TranslatorFiles, io::Error> {
        let script = args.next().unwrap();
        let in_file = match args.next() {
            Some(arg) => arg,
            None => panic!("Usage: {} <in_file>", script),
        };
        let metadata = fs::metadata(&in_file)?;

        match metadata.is_dir() {
            true => Self::from_directory(&in_file),
            false => Self::from_file(&in_file),
        }
    }

    fn from_directory(s: &String) -> Result<TranslatorFiles, io::Error> {
        let vm_files: Vec<PathBuf> = fs::read_dir(s)?
            .filter_map(|res| res.ok())
            .map(|f| f.path())
            .filter(|f| Self::is_vm_file(&f))
            .collect::<Vec<_>>();

        let in_path = PathBuf::from(s);
        let asm_file_name = PathBuf::from(in_path.file_name().unwrap());
        let mut asm_file = in_path.join(asm_file_name);
        asm_file.set_extension("asm");

        Ok(TranslatorFiles { vm_files, asm_file })
    }

    fn from_file(s: &String) -> Result<TranslatorFiles, io::Error> {
        let in_file = PathBuf::from(s);
        assert!(Self::is_vm_file(&in_file));
        let vm_files = vec![in_file];
        let mut asm_file = PathBuf::from(s);
        asm_file.set_extension("asm");

        Ok(TranslatorFiles { vm_files, asm_file })
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
