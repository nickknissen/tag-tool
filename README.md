# `Tag tool`

Git tagging tool to generate annotated tag with specified format.
For now now the format is hard coded and retrive part of the version number from rally (sprint number)

## INSTALLATION

`$ git clone git@github.com:nickknissen/tag_tool.git`
`$ pip install -r requirements.txt`

## USAGE

```
$ python tag_tool.py --help

# ...
# Usage: tag_tool.py [OPTIONS]
# 
# Options:
#   --rally-user TEXT  Username to rally1.rallydev.com  [required]
#   --rally-pass TEXT  Password to rally1.rallydev.com  [required]
#   --help             Show this message and exit.
```

## IDEAS

- [ ] Clean up and reuse code
- [ ] Use a file to instead of template to easier customization.
- [ ] Use Request instead of CURL to make it platform platform agnostic.
- [ ] Make it work from current branch instead of master
- [ ] Config file for input and output format for tagname.
- [ ] Tests!!!

## LICENSE
[MIT](LICENSE)


