# -*- coding: utf-8 -*-

from subprocess import check_output

duplicate_contributors = ["ahub",
                          "monsieurh",
                          "Arsenijs",
                          "samkaufman01",
                          "crimier",
                          "none",
                          "kylemoran138",
                          "Ser2808",
                          "CrunchBang LiveUser"]

replace_contributors = {"CRImier": "CRImier (Arsenijs)",
                        "Zero Phone": "Unnamed contributor",
                        "Louis Pi": "Louis Parkerson"}


add_contributors = [[10, "Serge Spraiter"]]

output = check_output(["git", "shortlog", "--numbered", "--summary", "--all"])
lines = filter(None, [line.strip() for line in output.split('\n')])
contributors = [line.split("\t", 1) for line in lines]
contributors = [[int(n), name.strip()] for n, name in contributors]
for c in add_contributors:
    contributors.append(c)
contributors = list(reversed(sorted(contributors)))
contributor_names = [name for _, name in contributors if name not in duplicate_contributors]

with open("CONTRIBUTORS.md", 'w') as f:
    f.write("#ZPUI project contributors\n\n")
    for name in contributor_names:
        f.write(" - {}\n".format(replace_contributors.get(name, name)))
