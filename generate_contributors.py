# -*- coding: utf-8 -*-

from subprocess import check_output

duplicate_contributors = ["ahub",
                          "monsieurh",
                          "Arsenijs",
                          "samkaufman01",
                          "crimier",
                          "none",
                          "kylemoran138",
                          "CrunchBang LiveUser"]

replace_contributors = {"CRImier": "CRImier (Arsenijs)",
                        "Zero Phone": "Unnamed contributor"}

output = check_output(["git", "shortlog", "--numbered", "--summary", "--all"])
lines = filter(None, [line.strip() for line in output.split('\n')])
contributor_names = [line.split("\t", 1)[-1].strip() for line in lines]
contributors = [name for name in contributor_names if name not in duplicate_contributors]

with open("CONTRIBUTORS.md", 'w') as f:
    f.write("#ZPUI project contributors\n\n")
    for name in contributors:
        f.write(" - {}\n".format(replace_contributors.get(name, name)))
