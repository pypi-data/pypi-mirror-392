import click
import itertools
import seaborn as sns

from pathlib import Path

from . import formats


# A Click path that converts the received path to a pathlib.Path
path_arg = click.Path(path_type=Path)


@click.group()
def main():
    pass


@main.command()
@click.argument("files_or_directories", nargs=-1)
@click.option(
    "-m",
    "--curriculum-map",
    help="Curriculum map file",
    type=path_arg,
    required=True,
)
@click.option(
    "-o",
    "--output_dir",
    help="Output directory for FEAMS files",
    type=path_arg,
    required=True,
)
def feamsify(files_or_directories, curriculum_map, output_dir):
    """Convert assessment tool data file(s) into FEAMS files.

    This input to this command is a set of data files and/or directories (which will be
    searched recursively for data files). Those files may include data in any supported
    format, so gad can be used to combine data from differently-formatted repositories
    into a single FEAMS hierarchy, e.g.:

    gad feamsify core-data/ feams-input-1/ feams-input-2/ --output feams-output/
    """

    try:
        curriculum_map = formats.CurriculumMapFile.parse(curriculum_map)
        ga_data_files = formats.parse(files_or_directories, curriculum_map)

        output_dir.mkdir(parents=True, exist_ok=True)
        with open(output_dir / ".gitignore", "w") as gitignore:
            gitignore.write("*\n")

        for f in ga_data_files:
            try:
                formats.FEAMS.dump_files(output_dir, f, curriculum_map)
            except formats.CurriculumMap.MissingCourse as e:
                click.secho("Warning: ", fg="yellow", nl=False)
                click.secho(e.course, fg="blue", nl=False)
                click.echo(" not in curriculum map")

    except formats.DataError as err:
        click.secho("Error: ", fg="red", bold=True, nl=False)
        click.echo(err)


@main.group()
def indicator():
    """Commands related to GA indicators."""


@indicator.command("list")
@click.argument("curriculum-map", type=path_arg)
def list_indicators(curriculum_map):
    """List all GA indicators in a curriculum map."""

    try:
        cmap = formats.CurriculumMapFile.parse(curriculum_map)

        for ga in formats.GA:
            indicators = cmap.indicators_for_ga(ga)

            click.secho(f"GA {ga}", fg="cyan", bold=True, nl=False)
            click.secho(": ", fg="magenta", bold=True, nl=False)
            click.secho(ga.full_name(), fg="magenta", bold=True)

            if not indicators:
                click.secho(f"  No indicators mapped to GA {ga}", fg="red", bold=True)

            for indicator in sorted(indicators, key=lambda i: i.name):
                click.secho(ga.abbreviation(), fg="green", nl=False)
                click.secho(":", fg="magenta", nl=False)
                click.secho(f"{indicator.name}", fg="yellow", nl=False)
                click.echo("\t", nl=False)
                click.secho(indicator.description, fg="blue")

            click.echo()

    except formats.DataError as err:
        click.secho("Error: ", fg="red", bold=True, nl=False)
        click.echo(err)


@indicator.command("map")
@click.argument("curriculum-map", type=path_arg)
@click.option("-s", "--stat", is_flag=True, help="Only show tool stats, not details")
def map_indicators(curriculum_map: Path, stat: bool):
    """Show all assessment tools mapped to GA indicators.

    The detailed output of a curriculum map includes every GA, every indicator for that
    GA and every assessment tool mapped to every indicator. Assessment tools are shown
    with their mapped indicator levels (I, D or A). Each level has a human-meaningful
    colour (I: green, D: yellow, A: blue) missing indicator levels are indicated in red.
    """

    try:
        cmap = formats.CurriculumMapFile.parse(curriculum_map)

        # Iterate over every GA, not just the ones found in this curriculum map.
        for ga in formats.GA:
            indicators = cmap.indicators_for_ga(ga)

            # Summarize the GA (number and name)
            click.secho(f"GA {ga}", fg="cyan", nl=False)
            click.secho(": ", fg="magenta", nl=False)
            click.secho(ga.full_name(), fg="magenta")

            if not indicators:
                click.secho(f"No indicators mapped to GA {ga}", fg="red", bold=True)

            for indicator in sorted(indicators, key=lambda i: i.name):
                # Summarize the indicator
                click.secho(ga.abbreviation(), fg="green", nl=False)
                click.secho(":", fg="magenta", nl=False)
                click.secho(f"{indicator.name}", fg="yellow", nl=False)
                click.echo("\t", nl=False)

                if not stat:
                    click.secho(indicator.description, fg="blue")

                # Identify all assessment tools that have been mapped to this indicator,
                # storing them in a dictionary from level to list of tools
                mappings = {
                    level: list(group)
                    for level, group in itertools.groupby(
                        [cmap.mappings[idx] for idx in cmap.indicator_index[indicator]],
                        key=lambda m: m.level,
                    )
                }

                # Print out tools in ascending order of indicator level
                for level in formats.IndicatorLevel:
                    level_mappings = mappings.get(level, None)

                    if level_mappings:
                        colour = level.colour()

                        if stat:
                            n = len(level_mappings)
                            click.secho(f" {n:5}  ", fg=colour, nl=False)
                        else:
                            for m in level_mappings:
                                click.secho(f" {m.level}: {m.tool}", fg=colour)
                    else:
                        if stat:
                            click.secho(f" {0:5}  ", fg="red", nl=False, bold=True)
                        else:
                            click.secho(
                                f" {level}: No assessment tools", fg="red", bold=True
                            )

                click.echo()

            click.echo()

    except formats.DataError as err:
        click.secho("Error: ", fg="red", bold=True, nl=False)
        click.echo(err)


@main.group()
def plot():
    """Plot GA data graphically."""


@plot.command()
@click.argument("files_or_directories", nargs=-1)
@click.option("-f", "--format", default="pdf", help="Output format (pdf, svg, etc.)")
@click.option("-m", "--curriculum-map", help="Curriculum map file")
@click.option("-o", "--output_dir", required=True, help="Output directory for plots")
def tools(
    files_or_directories, curriculum_map: Path | None, format: str, output_dir: Path
):
    """Plot results from individual assessment tools in GA data files.

    This is the finest-grained form of data plotting: just the raw results of the
    assessment tools contained in a single GA data file. Each data file in the input
    set is converted into one plot file in the output directory.
    """

    sns.set_theme(style="whitegrid", palette="colorblind", font="Avenir")

    try:
        cmap = (
            formats.CurriculumMapFile.parse(curriculum_map) if curriculum_map else None
        )
        ga_data_files = formats.parse(files_or_directories, cmap)

        output_dir.mkdir(parents=True, exist_ok=True)

        with open(output_dir / ".gitignore", "w") as gitignore:
            gitignore.write("*")

        for f in ga_data_files:
            plot = f.plot()
            filename = f"{f.course_and_semester()}.{format}"
            plot.savefig(output_dir / filename)

    except formats.DataError as err:
        click.secho("Error: ", fg="red", bold=True, nl=False)
        click.echo(err)


@main.command()
@click.argument("files_or_directories", nargs=-1)
@click.option(
    "-m",
    "--curriculum-map",
    type=path_arg,
    help="Curriculum map file",
)
@click.option(
    "-u",
    "--unmapped-tools",
    is_flag=True,
    help="Warn about tools not in the curriculum map",
)
def validate(files_or_directories, curriculum_map: Path, unmapped_tools: bool):
    """Validate GA data files in either ATsheet or FEAMS format."""

    try:
        cmap = formats.CurriculumMapFile.parse(curriculum_map)
        ga_data_files = formats.parse(
            files_or_directories, cmap, validate=True, warn_unmapped=unmapped_tools
        )

        for f in ga_data_files:
            click.secho(f.course, fg="blue", nl=False)
            click.echo(" (", nl=False)
            click.secho(f.year_and_semester(long=True), fg="green", nl=False)
            click.echo(") contains ", nl=False)
            click.secho(len(f.results), fg="magenta", nl=False)
            click.echo(" results")

            if len(f.warnings) > 0:
                click.secho(f"{len(f.warnings)} warning(s)", fg="yellow", nl=False)
                click.secho(" for ", nl=False)
                click.secho(f.path, fg="blue", nl=False)
                click.secho(":")

                for _, message in enumerate(f.warnings):
                    click.secho(" - ", fg="yellow", nl=False)
                    click.secho(message, fg="magenta")

                click.echo()

    except formats.DataError as err:
        click.secho("Error: ", fg="red", bold=True, nl=False)
        click.echo(err)


if __name__ == "__main__":
    main()
