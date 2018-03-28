# eboekhouden-cli

Use [eboekhouden.nl](https://eboekhouden.nl) from the command line.

# Install

```
git clone <repo>
cd <repo>
python setup.py install
```

# Usage

### Show all options
```
$ ebh --help
Usage: ebh [OPTIONS] COMMAND [ARGS]...

  eboekhouden.nl from the command line

Options:
  --help  Show this message and exit.

Commands:
  add       Add hours for a given date.
  list      Show hours for this month.
  projects  List available projects.
  remove    Remove hours for a given id.
  setup     Store credentials in system keyring.
```

### Add 4 hours to your default project
```
$ ebh add 4
Adding 4.0 hours for 2018-03-28 to "Your Default Project"...
```

### Add 8 hours for tomorrow for project id 1
```
$ ebh add 8 tomorrow --project_id 1
Adding 8.0 hours for 2018-03-28 to "Your Awesome Project"...
```

### Show hours for this month
```
$ ebh list
+---------+------------+-----------+-----------------------------+--------------------------+----------------------------+---------------+
|      id | Datum      | Weekdag   | Project                     | Activiteit               | Opmerkingen                |   Aantal uren |
|---------+------------+-----------+-----------------------------+--------------------------+----------------------------+---------------|
| 1393023 | 2018-03-01 | Thursday  | The Best Project            | Training                 | Top training!              |             8 |
+---------+------------+-----------+-----------------------------+--------------------------+----------------------------+---------------+
```

### Remove hours
Remove hours using the id shown when using the `list` command.
```
$ ebh remove 1393023
```

### List your projects
```
$ ebh projects
+------------+-------+--------------------------------------------+
| selected   |    id | name                                       |
|------------+-------+--------------------------------------------|
| False      | 14013 | Intern                                     |
| False      | 24202 | Vakantie uren/dagen                        |
| False      | 40910 | Ziektedagen                                |
+------------+-------+--------------------------------------------+
```
