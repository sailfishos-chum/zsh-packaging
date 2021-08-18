Zsh packaging for Sailfish OS

# Build

- clone into `zsh-packaging`
- `cd zsh-packaging/zsh`
- in build engine: `sb2 -t SailfishOS-4.1.0.24-aarch64 rpmbuild --build-in-place -bb ../rpm/zsh.spec`

or simply

- `sfdk build`


