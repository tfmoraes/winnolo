extern crate subprocess;

use std::io::{Read};
use std::str;
use subprocess::{Popen, PopenConfig, Redirection, PopenError};


fn main() -> Result<(), PopenError>{
    let mut p = Popen::create(&["dmesg"], PopenConfig{
    stdout: Redirection::Pipe, ..Default::default()
    })?;
    let mut buffer = [0; 1024];


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
