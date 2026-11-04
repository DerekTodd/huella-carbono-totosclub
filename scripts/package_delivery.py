"""Empaqueta entregables sin originales pesados, secretos ni archivos temporales."""
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'output/TotosClub_Fase1_Entrega.zip'


def main():
    files = [ROOT / name for name in ['README.md', '.gitignore', 'requirements-report.txt', 'data/README.md']]
    for folder in ['scripts', 'docs', 'db', 'data/processed', 'output/pdf']:
        files += [path for path in (ROOT / folder).rglob('*') if path.is_file()
                  and '__pycache__' not in path.parts]
    with ZipFile(OUT, 'w', compression=ZIP_DEFLATED) as archive:
        for path in sorted(files):
            archive.write(path, 'TotosClub_Fase1/' + path.relative_to(ROOT).as_posix())
    with ZipFile(OUT) as archive:
        assert archive.testzip() is None, 'Archivo ZIP dañado'
        names = archive.namelist()
        assert all('/raw/' not in name and '/tmp/' not in name and '/.git/' not in name for name in names)
        assert 'TotosClub_Fase1/output/pdf/TotosClub_Fase1_Huella_de_Carbono.pdf' in names
        print(f'{OUT}\n{len(names)} archivos; {OUT.stat().st_size} bytes; integridad ZIP verificada.')


if __name__ == '__main__':
    main()
