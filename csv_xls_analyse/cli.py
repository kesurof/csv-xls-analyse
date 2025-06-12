import click
from .core import merge_csv_files, create_export_excel, analyse_consumption


@click.group()
def cli():
    """CSV/XLS analyse utilities."""
    pass


@cli.command()
@click.argument('paths', nargs=-1, type=click.Path(exists=True))
@click.option('--output', '-o', default='Analyse de Parc.xlsx', help='Output Excel file.')
def merge(paths, output):
    """Merge provided CSV or ZIP files into an Excel workbook."""
    if not paths:
        click.echo('No input files provided')
        return

    df = merge_csv_files(paths)
    create_export_excel(df, output)
    click.echo(f'Created {output}')


@cli.command()
@click.argument('folder', type=click.Path(exists=True, file_okay=False))
@click.option('--output', '-o', default='Analyse de consommation.xlsx', help='Output Excel file.')
def moyenne_conso(folder, output):
    """Generate \"Moyenne conso DATA\" sheet from CSV files in FOLDER."""
    analyse_consumption(folder, output)
    click.echo(f'Created {output}')


if __name__ == '__main__':
    cli()
