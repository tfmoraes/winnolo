extern crate subprocess;

use std::io::{Read};
use std::str;
use subprocess::{Popen, PopenConfig, Redirection, PopenError};
use std::vec::Vec;
use std::env;
use std::path::Path;


fn main() -> Result<(), PopenError>{
    let app_folder = Path::new("app");
    env::set_current_dir(&app_folder);
    let mut cmd : Vec<String> = Vec::new();
    cmd.push("..\\python\\python.exe".to_string());
    cmd.push("app.py".to_string());
    for arg in std::env::args().skip(1) {
        cmd.push(arg);
    }
    let mut p = Popen::create(&cmd, PopenConfig{
    stdout: Redirection::Pipe, ..Default::default()
    })?;
    let mut buffer = [0; 1024];

    println!("{:?}", std::env::args().skip(1));


    while p.poll() == None {
        match p.stdout.as_mut() {
            Some(stdout) => {
                stdout.read(&mut buffer);
                let s = str::from_utf8(&buffer).unwrap();
                print!("{}", s)
            }
            _ => panic!("could not read stdout"),
        }
    }

    Ok(())
}
